"""Pure-Python encoder for XMemCompress streams, the counterpart of
albam.lib.xcompress.

Written against that decoder rather than against any general description of
LZX: it is what the game's own data round-trips through, so it is the
specification here. Everything below mirrors it in reverse - the same
16-bit-word bit packing, the same canonical Huffman construction, the same
delta-coded code lengths, the same position slots.

What lives here is one stream: its frames and its blocks, and nothing about
where the stream sits. Two containers hold these streams and frame them
differently - albam/engines/cie/lfs_compress.py cuts a .lfs payload into
64KB chunks and gives each one a stream of its own, while an MT Framework
archive entry (albam/engines/mtfw/arc_fs.py) is a single bare stream however
large it is.

The shape a stream has to take, measured by decoding every entry of 400
Devil May Cry 4 archives - 3960 streams, 23826 frames, 5821 blocks (the .lfs
side has its own numbers in lfs_compress, and agrees on all of this):

* No match may run past the end of its own frame. This decoder stops a match
  dead when the frame's output is full and simply loses the rest of it, and
  not one match in the sample crosses a frame boundary, so a match that
  would is split at the boundary (see _operations).
* Matches do reach back into earlier frames, up to 131067 bytes - all but
  five bytes of the 0x20000 window - so the window is not reset per frame.
  Only writing is bounded by the frame, not reading.
* Every frame but a stream's last carries the two byte header, and the last
  carries the five byte one even when the short one would fit it, without
  exception in the sample, and nothing at all follows it (see _frame).
* Blocks are independent of frames: one block covers the whole stream in
  3463 of the 3960, and where a stream has more, their boundaries fall
  anywhere inside a frame.
* The x86 call transform is never on - 3960 streams, not one sets it.

Match finding is delegated to zlib: its deflate output is parsed back into
the literal/match token stream that produced it (_lz77_tokens), which is
then re-encoded as LZX. Deflate's window is 32KB against the 0x20000 the
format allows, so this leaves some ratio on the table, but it puts the O(n)
search work in C instead of in Python.
"""
import heapq
import struct
import zlib
from bisect import bisect_right

from .xcompress import EXTRA_BITS, POSITION_BASE

# One frame's uncompressed size. The frame header's size fields are 16 bit,
# so a frame cannot say it holds more than this.
FRAME_SIZE = 32768
# Introduces the long frame header; a frame not starting with it carries the
# short one (see _frame).
SHORT_FRAME_HEADER_MARKER = 0xFF

LZX_NUM_CHARS = 256
LZX_MIN_MATCH = 2
LZX_MAX_MATCH = 257
LZX_NUM_POSITION_SLOTS = 34
LZX_NUM_SECONDARY_LENGTHS = 249
LZX_BLOCKTYPE_VERBATIM = 1
LZX_MAIN_SYMBOLS = LZX_NUM_CHARS + LZX_NUM_POSITION_SLOTS * 8
LZX_PRETREE_SYMBOLS = 20
# Code lengths are read as 4-bit fields for the pretree and are capped at 16
# by the tree builder for everything else.
LZX_MAX_CODE_LENGTH = 16
LZX_MAX_PRETREE_LENGTH = 15
# A block header states its length in 24 bits, so a stream longer than this
# needs more than one block.
MAX_BLOCK_SIZE = 0xFFFFFF

# The lowest distance each position slot can express. The decoder computes
# `POSITION_BASE[slot] - 2` and adds the slot's extra bits to it, so the slots
# tile the distances from 1 upwards without a gap.
_SLOT_BASE = [POSITION_BASE[i] - 2 for i in range(LZX_NUM_POSITION_SLOTS)]


class _BitWriter:
    """Bits in the order xcompress._BitReader consumes them.

    That reader takes 16 bits at a time out of a little-endian u2 and hands
    them out most-significant first, so bits accumulate into a word here and
    each finished word is written low byte first.
    """

    __slots__ = ("out", "buf", "bl")

    def __init__(self):
        self.out = bytearray()
        self.buf = 0
        self.bl = 0

    def write(self, value, num_bits):
        while num_bits > 16:
            num_bits -= 16
            self.write((value >> num_bits) & 0xFFFF, 16)
            value &= (1 << num_bits) - 1
        if not num_bits:
            return
        self.buf = (self.buf << num_bits) | value
        self.bl += num_bits
        while self.bl >= 16:
            self.bl -= 16
            word = (self.buf >> self.bl) & 0xFFFF
            self.out.append(word & 0xFF)
            self.out.append(word >> 8)
        self.buf &= (1 << self.bl) - 1

    def finish(self):
        """The bytes written, padded with zero bits to a whole word."""
        if self.bl:
            self.write(0, 16 - self.bl)
        return bytes(self.out)


def _huffman_lengths(freqs, max_length):
    """Canonical code lengths for `freqs`, none longer than `max_length`.

    Over-long codes are dealt with by halving the frequencies and rebuilding,
    which converges because equal weights bound the depth at log2(n).

    A tree of one symbol gets a second, unused one alongside it, so that the
    lengths always describe a complete code. This decoder does not care - it
    walks a tree and only ever meets the code that was written - but a
    decoder building a lookup table has half of it undefined, and the game's
    own data never leaves a code incomplete: across a 40 archive sample all
    9909 pre-trees and all 3303 main trees are complete, and of the 3303
    length trees 3219 are complete and 84 empty, with none in between.
    """
    freqs = list(freqs)
    while True:
        used = [i for i, f in enumerate(freqs) if f]
        lengths = [0] * len(freqs)
        if not used:
            return lengths
        if len(used) == 1:
            lengths[used[0]] = 1
            lengths[1 if used[0] == 0 else 0] = 1
            return lengths

        heap = [(freqs[i], i) for i in used]
        heapq.heapify(heap)
        children = {}
        next_node = len(freqs)
        while len(heap) > 1:
            weight_a, node_a = heapq.heappop(heap)
            weight_b, node_b = heapq.heappop(heap)
            children[next_node] = (node_a, node_b)
            heapq.heappush(heap, (weight_a + weight_b, next_node))
            next_node += 1

        too_long = False
        stack = [(heap[0][1], 0)]
        while stack:
            node, depth = stack.pop()
            child = children.get(node)
            if child is None:
                lengths[node] = depth
                if depth > max_length:
                    too_long = True
            else:
                stack.append((child[0], depth + 1))
                stack.append((child[1], depth + 1))
        if not too_long:
            return lengths
        freqs = [(f + 1) >> 1 if f else 0 for f in freqs]


def _canonical_codes(lengths):
    """The codes xcompress._build_tree assigns to `lengths`.

    Same walk: count the lengths, start each length's codes where the
    previous length's left off shifted up one, hand them out in symbol order.
    """
    counts = [0] * (LZX_MAX_CODE_LENGTH + 1)
    for length in lengths:
        if 0 < length <= LZX_MAX_CODE_LENGTH:
            counts[length] += 1
    starts = [0] * (LZX_MAX_CODE_LENGTH + 1)
    for i in range(1, LZX_MAX_CODE_LENGTH):
        starts[i + 1] = (starts[i] + counts[i]) << 1
    codes = [0] * len(lengths)
    for symbol, length in enumerate(lengths):
        if 0 < length <= LZX_MAX_CODE_LENGTH:
            codes[symbol] = starts[length]
            starts[length] += 1
    return codes


def _length_tokens(new_lengths, previous_lengths, first, last):
    """The pre-tree token stream for new_lengths[first:last].

    Mirrors xcompress._read_lengths: a plain symbol is the difference from
    the length the same slot had in the previous block, modulo 17, and
    17/18/19 are runs. Each token is (symbol, extra_value, extra_bits) with an
    optional trailing delta symbol for 19.
    """
    tokens = []
    x = first
    while x < last:
        length = new_lengths[x]
        run = 1
        while x + run < last and new_lengths[x + run] == length:
            run += 1
        if length == 0:
            while run >= 4:
                if run >= 20:
                    take = min(run, 51)
                    tokens.append((18, take - 20, 5, None))
                else:
                    take = min(run, 19)
                    tokens.append((17, take - 4, 4, None))
                x += take
                run -= take
        else:
            while run >= 4:
                take = min(run, 5)
                delta = (previous_lengths[x] - length) % 17
                tokens.append((19, take - 4, 1, delta))
                x += take
                run -= take
        for _ in range(run):
            tokens.append(((previous_lengths[x] - new_lengths[x]) % 17, 0, 0, None))
            x += 1
    return tokens


def _write_lengths(writer, new_lengths, previous_lengths, first, last):
    """Write new_lengths[first:last] the way _read_lengths reads them."""
    tokens = _length_tokens(new_lengths, previous_lengths, first, last)
    freqs = [0] * LZX_PRETREE_SYMBOLS
    for symbol, _value, _bits, delta in tokens:
        freqs[symbol] += 1
        if delta is not None:
            freqs[delta] += 1

    pretree_lengths = _huffman_lengths(freqs, LZX_MAX_PRETREE_LENGTH)
    pretree_codes = _canonical_codes(pretree_lengths)
    for length in pretree_lengths:
        writer.write(length, 4)
    for symbol, value, bits, delta in tokens:
        writer.write(pretree_codes[symbol], pretree_lengths[symbol])
        if bits:
            writer.write(value, bits)
        if delta is not None:
            writer.write(pretree_codes[delta], pretree_lengths[delta])


# ---------------------------------------------------------------------------
# Match finding, by way of zlib
# ---------------------------------------------------------------------------

_DEFLATE_LENGTH_BASE = [
    3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59,
    67, 83, 99, 115, 131, 163, 195, 227, 258,
]
_DEFLATE_LENGTH_EXTRA = [
    0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4,
    5, 5, 5, 5, 0,
]
_DEFLATE_DIST_BASE = [
    1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513,
    769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577,
]
_DEFLATE_DIST_EXTRA = [
    0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10,
    11, 11, 12, 12, 13, 13,
]
_DEFLATE_CODE_LENGTH_ORDER = [
    16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15,
]
_FIXED_LITERAL_LENGTHS = [8] * 144 + [9] * 112 + [7] * 24 + [8] * 8
_FIXED_DISTANCE_LENGTHS = [5] * 32


class _DeflateBits:
    """Least-significant-bit-first reader, the order deflate is packed in."""

    __slots__ = ("data", "size", "pos", "buf", "bl")

    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.pos = 0
        self.buf = 0
        self.bl = 0

    def fill(self, num_bits):
        while self.bl < num_bits:
            if self.pos < self.size:
                byte = self.data[self.pos]
                self.pos += 1
            else:
                byte = 0
            self.buf |= byte << self.bl
            self.bl += 8

    def get(self, num_bits):
        if not num_bits:
            return 0
        self.fill(num_bits)
        value = self.buf & ((1 << num_bits) - 1)
        self.buf >>= num_bits
        self.bl -= num_bits
        return value

    def align(self):
        drop = self.bl & 7
        self.buf >>= drop
        self.bl -= drop


def _deflate_table(lengths):
    """A (peeked bits -> symbol, code length) lookup table for `lengths`."""
    max_length = max(lengths)
    if not max_length:
        return None, 0
    counts = [0] * (max_length + 1)
    for length in lengths:
        if length:
            counts[length] += 1
    next_code = [0] * (max_length + 1)
    code = 0
    for length in range(1, max_length + 1):
        code = (code + counts[length - 1]) << 1
        next_code[length] = code

    table = [0] * (1 << max_length)
    for symbol, length in enumerate(lengths):
        if not length:
            continue
        code = next_code[length]
        next_code[length] += 1
        reversed_code = 0
        for i in range(length):
            reversed_code = (reversed_code << 1) | ((code >> i) & 1)
        entry = (symbol << 4) | length
        for index in range(reversed_code, 1 << max_length, 1 << length):
            table[index] = entry
    return table, max_length


def _deflate_symbol(bits, table, max_length):
    bits.fill(max_length)
    entry = table[bits.buf & ((1 << max_length) - 1)]
    length = entry & 15
    if not length:
        raise ValueError("invalid deflate code")
    bits.buf >>= length
    bits.bl -= length
    return entry >> 4


def _parse_deflate(data):
    """The literal/match tokens a raw deflate stream encodes.

    A literal is an int, a match is a (length, distance) pair. Only what zlib
    itself emits has to be handled, but all three block types are, since a
    stored block is what it falls back to for data it cannot compress.
    """
    bits = _DeflateBits(data)
    tokens = []
    append = tokens.append
    while True:
        final = bits.get(1)
        block_type = bits.get(2)
        if block_type == 0:
            bits.align()
            size = bits.get(16)
            bits.get(16)
            for _ in range(size):
                append(bits.get(8))
        elif block_type in (1, 2):
            if block_type == 1:
                literal_lengths = _FIXED_LITERAL_LENGTHS
                distance_lengths = _FIXED_DISTANCE_LENGTHS
            else:
                num_literals = bits.get(5) + 257
                num_distances = bits.get(5) + 1
                num_code_lengths = bits.get(4) + 4
                code_lengths = [0] * 19
                for i in range(num_code_lengths):
                    code_lengths[_DEFLATE_CODE_LENGTH_ORDER[i]] = bits.get(3)
                code_table, code_max = _deflate_table(code_lengths)
                all_lengths = []
                while len(all_lengths) < num_literals + num_distances:
                    symbol = _deflate_symbol(bits, code_table, code_max)
                    if symbol < 16:
                        all_lengths.append(symbol)
                    elif symbol == 16:
                        all_lengths += [all_lengths[-1]] * (bits.get(2) + 3)
                    elif symbol == 17:
                        all_lengths += [0] * (bits.get(3) + 3)
                    else:
                        all_lengths += [0] * (bits.get(7) + 11)
                literal_lengths = all_lengths[:num_literals]
                distance_lengths = all_lengths[num_literals:num_literals + num_distances]
            literal_table, literal_max = _deflate_table(literal_lengths)
            distance_table, distance_max = _deflate_table(distance_lengths)
            while True:
                symbol = _deflate_symbol(bits, literal_table, literal_max)
                if symbol < 256:
                    append(symbol)
                elif symbol == 256:
                    break
                else:
                    index = symbol - 257
                    length = _DEFLATE_LENGTH_BASE[index] + bits.get(_DEFLATE_LENGTH_EXTRA[index])
                    index = _deflate_symbol(bits, distance_table, distance_max)
                    distance = _DEFLATE_DIST_BASE[index] + bits.get(_DEFLATE_DIST_EXTRA[index])
                    append((length, distance))
        else:
            raise ValueError(f"invalid deflate block type {block_type}")
        if final:
            return tokens


def _lz77_tokens(payload, level=9):
    """`payload` as literals and back-references, all within itself."""
    compressor = zlib.compressobj(level, zlib.DEFLATED, -15, 9)
    return _parse_deflate(compressor.compress(payload) + compressor.flush())


# ---------------------------------------------------------------------------
# LZX blocks and frames
# ---------------------------------------------------------------------------

class FrameTooLarge(Exception):
    """Raised when a frame will not fit its own header's size field."""


def _operations(payload, tokens):
    """`tokens` as the symbols one verbatim block encodes them with.

    Each operation is (main symbol, secondary length symbol or -1, extra bits
    value, extra bit count, bytes emitted). Two things are settled here rather
    than at write time: the three repeated offsets, which have to be tracked
    exactly as the decoder updates them, and frame boundaries, which no match
    may cross - the decoder stops a match dead when the frame's output is full
    and would lose the rest of it.
    """
    operations = []
    append = operations.append
    r0 = r1 = r2 = 1
    position = 0
    for token in tokens:
        if type(token) is int:
            append((token, -1, 0, 0, 1))
            position += 1
            continue

        length, distance = token
        while length:
            take = min(length, LZX_MAX_MATCH, FRAME_SIZE - (position % FRAME_SIZE))
            if length - take == 1 and take > LZX_MIN_MATCH:
                # A one byte tail cannot be a match of its own, so leave it
                # two bytes to be one.
                take -= 1
            if take < LZX_MIN_MATCH:
                append((payload[position], -1, 0, 0, 1))
                position += 1
                length -= 1
                continue

            if distance == r0:
                slot, extra_value, extra_bits = 0, 0, 0
            elif distance == r1:
                slot, extra_value, extra_bits = 1, 0, 0
                r1 = r0
                r0 = distance
            elif distance == r2:
                slot, extra_value, extra_bits = 2, 0, 0
                r2 = r0
                r0 = distance
            else:
                slot = bisect_right(_SLOT_BASE, distance) - 1
                extra_bits = EXTRA_BITS[slot]
                extra_value = distance - _SLOT_BASE[slot]
                r2 = r1
                r1 = r0
                r0 = distance

            footer = take - LZX_MIN_MATCH
            if footer >= 7:
                secondary = footer - 7
                footer = 7
            else:
                secondary = -1
            append((LZX_NUM_CHARS + slot * 8 + footer, secondary, extra_value, extra_bits, take))
            position += take
            length -= take
    return operations


def _split_blocks(operations, max_block_size):
    """`operations` cut into blocks of at most `max_block_size` bytes each.

    A block header states its length in 24 bits, so a stream longer than
    that cannot be one block however well it compresses. The cut lands
    between two operations, never inside a match, because a block's length
    has to be exactly the bytes it emits - so a block holding a single
    operation can still overrun a cap smaller than one match, which the real
    one (16MB against 257 bytes) is in no danger of being.
    """
    blocks = []
    current = []
    emitted = 0
    for operation in operations:
        size = operation[4]
        if emitted + size > max_block_size and current:
            blocks.append((current, emitted))
            current = []
            emitted = 0
        current.append(operation)
        emitted += size
    if current:
        blocks.append((current, emitted))
    return blocks


def _write_block_header(writer, operations, emitted, previous_main, previous_secondary):
    """One verbatim block's header and its two trees.

    Every code length is delta coded against the length the same slot had in
    the previous block, which is why the caller passes those in; at the start
    of a stream the decoder zeroes them (see xcompress._lzx_inflate). Returns
    each tree as (lengths, codes), the lengths being what the block after
    this one is coded against.
    """
    main_freqs = [0] * LZX_MAIN_SYMBOLS
    secondary_freqs = [0] * LZX_NUM_SECONDARY_LENGTHS
    for symbol, secondary, _value, _bits, _size in operations:
        main_freqs[symbol] += 1
        if secondary >= 0:
            secondary_freqs[secondary] += 1

    main_lengths = _huffman_lengths(main_freqs, LZX_MAX_CODE_LENGTH)
    secondary_lengths = _huffman_lengths(secondary_freqs, LZX_MAX_CODE_LENGTH)

    writer.write(LZX_BLOCKTYPE_VERBATIM, 3)
    writer.write(emitted, 24)
    _write_lengths(writer, main_lengths, previous_main, 0, LZX_NUM_CHARS)
    _write_lengths(writer, main_lengths, previous_main, LZX_NUM_CHARS, LZX_MAIN_SYMBOLS)
    _write_lengths(writer, secondary_lengths, previous_secondary,
                   0, LZX_NUM_SECONDARY_LENGTHS)
    return ((main_lengths, _canonical_codes(main_lengths)),
            (secondary_lengths, _canonical_codes(secondary_lengths)))


def compress_frames(payload, max_block_size=MAX_BLOCK_SIZE):
    """`payload` as a list of (frame bytes, uncompressed size).

    Every frame but the last holds FRAME_SIZE bytes. Blocks are laid over
    the frames rather than inside them: one block covers the whole payload
    unless it is too long for a block header's 24-bit length, and a block
    header can land anywhere in a frame. Only the bits are cut at each frame
    boundary, since each frame is read by a bit reader of its own and so has
    to start on a whole word.

    `max_block_size` is a parameter so a test can force the multi-block path
    without a 16MB payload.
    """
    operations = _operations(payload, _lz77_tokens(payload))
    blocks = _split_blocks(operations, max_block_size)

    writer = _BitWriter()
    # No E8 (x86 call) translation. The decoder reads this bit once per
    # stream, before the first block.
    writer.write(0, 1)

    frames = []
    emitted = 0
    main_lengths = [0] * LZX_MAIN_SYMBOLS
    secondary_lengths = [0] * LZX_NUM_SECONDARY_LENGTHS
    for block_operations, block_size in blocks:
        (main_lengths, main_codes), (secondary_lengths, secondary_codes) = (
            _write_block_header(writer, block_operations, block_size,
                                main_lengths, secondary_lengths))
        for symbol, secondary, value, bits, size in block_operations:
            writer.write(main_codes[symbol], main_lengths[symbol])
            if secondary >= 0:
                writer.write(secondary_codes[secondary], secondary_lengths[secondary])
            if bits:
                writer.write(value, bits)
            emitted += size
            if emitted == FRAME_SIZE:
                frames.append((writer.finish(), emitted))
                emitted = 0
                writer = _BitWriter()
    if emitted:
        frames.append((writer.finish(), emitted))
    if sum(size for _data, size in frames) != len(payload):
        raise RuntimeError("LZX encoder lost track of a stream's output size")
    return frames


def _frame(data, uncompressed_size, last):
    """One frame, with the header xcompress._lzx_inflate expects.

    Both of its sizes are big-endian u2. The two byte header says only how
    many compressed bytes follow and leaves the uncompressed size implied, so
    it can only carry a frame of the standard size; the five byte one the
    0xFF marker introduces spells both out.

    A stream's last frame always takes the long header, even when its
    uncompressed size is the standard one and the short header would do. That
    is what the game's own data does without exception, in both containers:
    over a 700 archive .lfs sample every one of 65594 compressed chunks ends
    on a long header, and over 400 Devil May Cry 4 archives so does every one
    of 3960 entry streams, with every frame before it using the short one.
    """
    size = len(data)
    if size > 0xFFFF:
        # Both header forms hold the compressed size in a u2.
        raise FrameTooLarge(
            f"a frame holding {uncompressed_size} bytes came to {size} compressed, "
            f"more than the {0xFFFF} a frame header can count"
        )
    if not last and uncompressed_size == FRAME_SIZE and (size >> 8) != SHORT_FRAME_HEADER_MARKER:
        return struct.pack(">H", size) + data
    return struct.pack(">BHH", SHORT_FRAME_HEADER_MARKER, uncompressed_size, size) + data


def frame_stream(frames):
    """`frames` (as compress_frames returns them) with their headers on."""
    out = bytearray()
    for i, (data, size) in enumerate(frames):
        out += _frame(data, size, last=i + 1 == len(frames))
    return bytes(out)


def xmem_compress(payload):
    """`payload` as one bare XMemCompress stream - what an .arc entry holds.

    The size is not in the stream; whatever points at it stores that (an
    .arc file entry's `size`), and xcompress.xmem_decompress takes it back.

    Raises FrameTooLarge if a frame will not fit its own header's size
    field, the way compress_frames raises on a size mismatch: a stream that
    cannot be encoded correctly is refused rather than written.
    """
    payload = bytes(payload)
    if not payload:
        return b""
    return frame_stream(compress_frames(payload))
