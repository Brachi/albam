"""
The LZX encoder (albam/engines/cie/lfs_compress.py) against the decoder that
is its specification.

Round-tripping through albam's own decoder is the whole test: the encoder is
correct exactly when what it writes decodes back to what it was given, as
part of the chunk sequence it belongs to rather than on its own. Half of this
file needs no game data at all; the other half compresses real payloads,
which is what proves the sequencing right - a synthetic payload does not
exercise a chunk matching back into the one before it nearly as hard.
"""
import pytest

from tests.cie.lfs_paths import resolve_archive_hashes
from tests.cie.test_lfs_fs import LFS_PARSING_DATASET

CHUNK_SIZE = 0x10000

# Payloads that between them cover what the encoder has to decide: nothing to
# emit, too little to compress, a stream that is all matches, one that cannot
# be compressed at all and falls back to stored chunks, and several chunks,
# both aligned to the chunk size and not.
SYNTHETIC_PAYLOADS = {
    "empty": b"",
    "single_byte": b"A",
    "short": b"albam" * 3,
    "one_full_chunk": bytes(CHUNK_SIZE),
    "repetitive": b"abcabcabc" * 30000,
    "several_chunks": (b"the same line, over and over\n" * 20000)[:5 * CHUNK_SIZE + 1234],
    "chunk_boundary": bytes(range(256)) * (CHUNK_SIZE // 256) * 2,
}


def _random_bytes(size):
    import random

    generator = random.Random(20240501)
    return bytes(generator.getrandbits(8) for _ in range(size))


def _round_trip(payload):
    """`payload` compressed and read back, with the rebuilt file's size.

    compress=True is explicit because it is no longer the default: writing an
    archive stores its chunks, since an archive written with this encoder is
    read back correctly here and rejected by the game. These tests are what
    covers the encoder itself, so they ask for it by name.
    """
    from albam.engines.cie.lfs_decompress import (xcompress_compress_re4hd,
                                                  xcompress_decompress_re4hd)
    from albam.engines.cie.structs.lfs import Lfs

    rebuilt = xcompress_compress_re4hd(payload, compress=True)
    reparsed = Lfs.from_bytes(rebuilt)
    reparsed._read()
    assert reparsed.header.size_decompressed == len(payload)
    return bytes(xcompress_decompress_re4hd(reparsed.chunks)), rebuilt


@pytest.mark.parametrize("name", sorted(SYNTHETIC_PAYLOADS))
def test_synthetic_payload_round_trips(name):
    """CI-safe: no game data, only the encoder against the decoder."""
    payload = SYNTHETIC_PAYLOADS[name]
    assert _round_trip(payload)[0] == payload


def test_incompressible_payload_round_trips():
    """Random bytes compress to nothing, so every chunk falls back to stored
    - and a stored chunk is copied out without ever reaching the LZX window,
    which the chunks after it must not then try to match against."""
    payload = _random_bytes(2 * CHUNK_SIZE + 7)
    decompressed, rebuilt = _round_trip(payload)
    assert decompressed == payload
    assert len(rebuilt) < len(payload) + 4 * CHUNK_SIZE


def test_compressible_payload_shrinks():
    payload = SYNTHETIC_PAYLOADS["several_chunks"]
    assert len(_round_trip(payload)[1]) < len(payload) // 10


def test_a_stored_chunk_between_compressed_ones_round_trips():
    """The awkward mixture: an incompressible chunk in the middle leaves the
    window where it was, so the chunk after it is matching against the chunk
    before it rather than against what immediately precedes it."""
    filler = b"a line that repeats itself\n" * 4000
    payload = b"".join([filler[:CHUNK_SIZE], _random_bytes(CHUNK_SIZE),
                        filler[:CHUNK_SIZE], filler[:1000]])
    assert _round_trip(payload)[0] == payload


def _pseudo_payload(seed, size):
    """Data with matches everywhere and no structure to it, so matches land
    across chunk and frame boundaries at every alignment."""
    import random

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


@pytest.mark.parametrize("seed", range(12))
def test_pseudo_random_payloads_round_trip(seed):
    """A match may not run over the end of a frame: the decoder stops it dead
    there and the rest of it is simply lost, so the encoder splits one that
    would. Which alignments that has to handle is not something a handwritten
    payload finds, hence a spread of generated ones.
    """
    payload = _pseudo_payload(seed, 70000 + seed * 7919)
    assert _round_trip(payload)[0] == payload


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in LFS_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['payload_extension'].lstrip('.')}-{d['archive_path_hash']}"
               for d in LFS_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_real_payload_round_trips_compressed(game_root, local_archive_path_hash):
    """A real archive, decompressed and compressed again, comes back byte for
    byte - and comes out smaller than the payload, which is the point of the
    encoder existing.

    Real payloads are what test the sequencing: chunks share one window, so a
    chunk decodes only in its place in the sequence, matching back into the
    chunks before it. Synthetic data barely exercises that.

    The size is not compared to the original archive's: this encoder searches
    a 32KB window where the format allows 128KB, so it is expected to land
    somewhat behind whatever produced the shipped archives.
    """
    from albam.engines.cie.lfs_decompress import xcompress_decompress_re4hd
    from albam.engines.cie.structs.lfs import Lfs

    path = resolve_archive_hashes(game_root, {local_archive_path_hash})[local_archive_path_hash]
    original = Lfs.from_file(path)
    original._read()
    payload = bytes(xcompress_decompress_re4hd(original.chunks))

    decompressed, rebuilt = _round_trip(payload)
    assert decompressed == payload

    reparsed = Lfs.from_bytes(rebuilt)
    reparsed._read()
    assert any(chunk.is_compressed for chunk in reparsed.chunks)
    assert len(rebuilt) < len(payload), "the rebuilt archive should be compressed"
