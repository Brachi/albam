"""The bare XMemCompress stream encoder (albam/lib/xcompress_encode.py)
against the decoder that is its specification (albam/lib/xcompress.py).

Everything here is CI-safe: no game data, only the encoder against the
decoder. What real archives have to say is in tests/mtfw/test_arc_compression.py
(MT Framework entries) and tests/cie/test_lfs_compress.py (.lfs chunks),
which is also where the .lfs framing this shared the encoder out from is
covered.

Round-tripping through albam's own decoder is not on its own evidence that
the game would accept a stream - that decoder is more forgiving than the
game's, which is how the .lfs encoder came to ship three separate bugs
against it - so the tests that matter here are the ones that pin the shape
shipped streams have rather than only what reads back.
"""
import random

import pytest

from albam.lib.xcompress import xmem_decompress
from tests.xcompress_cab import independent_decompress, sevenzip
from tests.xcompress_frames import frames_of
from albam.lib.xcompress_encode import (
    FRAME_SIZE,
    LZX_MIN_MATCH,
    _huffman_lengths,
    _lz77_tokens,
    _operations,
    _split_blocks,
    _stored_frames,
    compress_frames,
    frame_stream,
    xmem_compress,
)

# Payloads that between them cover what the encoder has to decide: nothing to
# emit, too little to compress, a stream that is all matches, one that is
# exactly one frame, and several frames both aligned to the frame size and
# not.
SYNTHETIC_PAYLOADS = {
    "empty": b"",
    "single_byte": b"A",
    "short": b"albam" * 3,
    "one_full_frame": bytes(FRAME_SIZE),
    "repetitive": b"abcabcabc" * 30000,
    "several_frames": (b"the same line, over and over\n" * 20000)[:5 * FRAME_SIZE + 1234],
    "frame_boundary": bytes(range(256)) * (FRAME_SIZE // 256) * 2,
}


def _random_bytes(size):
    generator = random.Random(20240501)
    return bytes(generator.getrandbits(8) for _ in range(size))


def _pseudo_payload(seed, size):
    """Data with matches everywhere and no structure to it, so matches land
    across frame boundaries at every alignment."""
    generator = random.Random(seed)
    alphabet = bytes(generator.randrange(256)
                     for _ in range(generator.choice([2, 3, 5, 17])))
    payload = bytearray()
    while len(payload) < size:
        if payload and generator.random() < 0.6:
            start = generator.randrange(len(payload))
            payload += payload[start:start + generator.choice([2, 3, 3, 4, 8, 40, 300])]
        else:
            payload += bytes(generator.choice(alphabet)
                             for _ in range(generator.randrange(1, 6)))
    return bytes(payload[:size])


@pytest.mark.parametrize("used", [0, 1, 5, 300])
def test_a_one_symbol_tree_is_still_complete(used):
    """No code the encoder writes leaves half a decode table undefined.

    A tree of a single symbol is the one case where a Huffman build gives an
    incomplete code, and the game's own data has none: a second, unused
    symbol goes in beside it (see _huffman_lengths).
    """
    freqs = [0] * 512
    freqs[used] = 7
    lengths = _huffman_lengths(freqs, 16)
    assert sum(2.0 ** -length for length in lengths if length) == 1.0
    assert lengths[used] == 1


@pytest.mark.parametrize("name", sorted(SYNTHETIC_PAYLOADS))
def test_synthetic_payload_round_trips(name):
    payload = SYNTHETIC_PAYLOADS[name]
    assert xmem_decompress(xmem_compress(payload), len(payload)) == payload


@pytest.mark.parametrize("seed", range(8))
def test_pseudo_random_payloads_round_trip(seed):
    """A match may not run over the end of a frame: the decoder stops it dead
    there and the rest of it is simply lost, so the encoder splits one that
    would. Which alignments that has to handle is not something a handwritten
    payload finds, hence a spread of generated ones.
    """
    payload = _pseudo_payload(seed, 70000 + seed * 7919)
    assert xmem_decompress(xmem_compress(payload), len(payload)) == payload


def test_incompressible_payload_round_trips():
    """Random bytes have nothing to match, so every symbol is a literal and
    the stream comes out slightly larger than the payload. An .arc entry has
    no stored flag to fall back on, so that is the right answer rather than
    a failure."""
    payload = _random_bytes(3 * FRAME_SIZE + 7)
    stream = xmem_compress(payload)
    assert xmem_decompress(stream, len(payload)) == payload
    assert len(stream) < len(payload) * 1.1


def test_compressible_payload_shrinks():
    payload = SYNTHETIC_PAYLOADS["several_frames"]
    assert len(xmem_compress(payload)) < len(payload) // 10


def test_an_empty_payload_is_an_empty_stream():
    assert xmem_compress(b"") == b""


@pytest.mark.parametrize("size", [1000, FRAME_SIZE, FRAME_SIZE + 4321, 3 * FRAME_SIZE])
def test_frames_take_the_shape_the_game_s_own_streams_do(size):
    """The frame shape every entry stream in the game's data has.

    Measured over the entries of 400 Devil May Cry 4 archives, without a
    single exception in 3960 streams: every frame but the last carries the
    two byte header, the last carries the five byte one even when the short
    one would fit it, and nothing at all follows it - unlike an .lfs chunk,
    which closes with five zero bytes.
    """
    payload = (b"a line that repeats itself, mostly\n" * 4000)[:size]
    frames, trailing = frames_of(xmem_compress(payload))
    assert frames
    assert [f[0] for f in frames] == [2] * (len(frames) - 1) + [5]
    assert sum(f[1] for f in frames) == size
    assert all(f[1] == FRAME_SIZE for f in frames[:-1])
    assert trailing == b""


@pytest.mark.parametrize("seed", range(4))
def test_no_match_runs_past_the_end_of_its_frame(seed):
    """The invariant behind the split in _operations, checked at the source
    rather than through what happens to decode.

    The decoder truncates a match at the frame's end and loses the rest, and
    no match in the game's own streams needs it to do otherwise - over 3960
    entry streams decoded whole, not one match crosses a frame boundary.
    """
    payload = _pseudo_payload(seed, 5 * FRAME_SIZE + 999)
    position = 0
    for _symbol, _secondary, _value, _bits, emitted in _operations(
            payload, _lz77_tokens(payload)):
        assert position % FRAME_SIZE + emitted <= FRAME_SIZE
        assert emitted == 1 or emitted >= LZX_MIN_MATCH
        position += emitted
    assert position == len(payload)


def test_a_stream_of_several_blocks_round_trips():
    """A block header states its length in 24 bits, so a long enough stream
    has to be split into several - and then a block header lands somewhere in
    the middle of a frame, at whatever bit offset the symbols before it
    happen to end on.

    That is the case a 16MB payload would reach and nothing smaller does,
    which is why compress_frames takes the cap as an argument: this walks the
    same path in a second rather than a minute.
    """
    payload = _pseudo_payload(99, 4 * FRAME_SIZE + 4321)
    operations = _operations(payload, _lz77_tokens(payload))
    assert len(_split_blocks(operations, 5000)) > 20

    stream = frame_stream(compress_frames(payload, max_block_size=5000))
    assert xmem_decompress(stream, len(payload)) == payload


def test_a_block_ends_where_its_header_says_it_does():
    """Every block's declared length is exactly what its operations emit -
    a block that overruns puts every block after it in the wrong place."""
    payload = _pseudo_payload(7, 3 * FRAME_SIZE)
    blocks = _split_blocks(_operations(payload, _lz77_tokens(payload)), 7000)
    assert sum(emitted for _block, emitted in blocks) == len(payload)
    for operations, emitted in blocks:
        assert sum(operation[4] for operation in operations) == emitted


@pytest.mark.parametrize("size", [1, 100, FRAME_SIZE, FRAME_SIZE + 1, 3 * FRAME_SIZE - 3])
def test_stored_frames_round_trip(size):
    """The fallback for a frame that would not fit its own header's size
    field. Nothing measurable reaches it, so it is tested directly rather
    than through an input that provokes it."""
    payload = _random_bytes(size)
    stream = _stored_frames(payload)
    assert xmem_decompress(stream, size) == payload
    frames, trailing = frames_of(stream)
    assert [f[0] for f in frames] == [2] * (len(frames) - 1) + [5]
    assert sum(f[1] for f in frames) == size
    assert trailing == b""


needs_p7zip = pytest.mark.skipif(sevenzip() is None,
                                 reason="p7zip is not installed (see tests/xcompress_cab.py)")


@needs_p7zip
@pytest.mark.parametrize("seed", range(4))
def test_an_independent_decoder_reads_the_same_bytes_back(seed):
    """The encoder's output through a decoder that is not albam's.

    albam's decoder and this encoder were written against each other, so
    agreeing tells us less than it looks like: whatever the decoder is
    lenient about, the encoder is free to get wrong. p7zip's LZX decoder was
    written from the format, shares nothing with either, and is stricter -
    see tests/xcompress_cab.py for what it is being handed and why that is
    the same bitstream.
    """
    payload = _pseudo_payload(seed, 3 * FRAME_SIZE + 5000)
    assert independent_decompress(xmem_compress(payload), len(payload)) == payload


@needs_p7zip
def test_an_independent_decoder_reads_a_multi_block_stream():
    payload = _pseudo_payload(42, 4 * FRAME_SIZE + 4321)
    stream = frame_stream(compress_frames(payload, max_block_size=5000))
    assert independent_decompress(stream, len(payload)) == payload
