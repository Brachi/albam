"""
Pure-Python LZX encoder for RE4 UHD .lfs archives.

The counterpart of lfs_decompress.py, and written against it rather than
against any general description of LZX: that decoder is what the game's own
data round-trips through, so it is the specification here. Everything below
mirrors it in reverse - the same 16-bit-word bit packing, the same canonical
Huffman construction, the same delta-coded code lengths, the same position
slots.

Two things about the container shape the encoder more than the bit format
does (see lfs.ksy and xcompress_decompress_re4hd):

* No match reaches out of its own chunk. This decoder would allow it - it
  carries one window across the whole file, so a chunk can refer to what the
  chunks before it decoded - and an earlier version of this encoder did
  exactly that, producing archives this decoder read back perfectly and the
  game rejected outright. The game's own data says why: over a 150 archive
  sample, of 72146673 matches not one reaches back past the start of the
  chunk it lives in, and the longest distance seen anywhere is 65469, under
  one chunk. So a chunk here is encoded as if the window were empty, and
  decodes on its own wherever it sits in the file.
* Per chunk the decoder resets the code lengths and the three repeated
  offsets, but not the window, not the current block and not the trees. So
  every chunk here starts a fresh block and ends exactly on its last byte,
  leaving no partial block for the next chunk to fall into.
* A chunk says where its frames stop, rather than leaving that to whoever
  counts the bytes coming out: its last frame takes the long header and five
  zero bytes follow it (see _frame and FRAME_TERMINATOR). This decoder needs
  neither, which is how an encoder written against it came to omit both.

Match finding is delegated to zlib: its deflate output is parsed back into the
literal/match token stream that produced it (_lz77_tokens), which is then
re-encoded as LZX. Deflate's window is 32KB against the chunk's 64KB, so this
leaves some ratio on the table, but it puts the O(n) search work in C instead
of in Python.
"""
import heapq
import struct
import zlib
from bisect import bisect_right

from .lfs_decompress import (
    CHUNK_ALIGNMENT,
    EXTRA_BITS,
    LFS_CHUNK_SIZE,
    LFS_DEFAULT_FILE_ID,
    LFS_MAGIC1,
    POSITION_BASE,
)

# One frame's uncompressed size. The frame header's size fields are 16 bit,
# and a whole chunk does not fit one, so a chunk is two frames.
FRAME_SIZE = 32768
# Introduces the long frame header; a frame not starting with it carries the
# short one (see _frame).
SHORT_FRAME_HEADER_MARKER = 0xFF
# Closes a chunk, after its last frame. Reads as a frame header declaring no
# compressed bytes, which is what stops a reader that walks frames until they
# run out rather than until the output is full. Every compressed chunk in the
# game's own data ends with exactly these five bytes, and they count towards
# the chunk's size in the chunk table.
FRAME_TERMINATOR = b"\x00" * 5

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

# The lowest distance each position slot can express. The decoder computes
# `POSITION_BASE[slot] - 2` and adds the slot's extra bits to it, so the slots
# tile the distances from 1 upwards without a gap.
_SLOT_BASE = [POSITION_BASE[i] - 2 for i in range(LZX_NUM_POSITION_SLOTS)]


class _BitWriter:
    """Bits in the order lfs_decompress._BitReader consumes them.

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
    """The codes lfs_decompress._build_tree assigns to `lengths`.

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

    Mirrors lfs_decompress._read_lengths: a plain symbol is the difference
    from the length the same slot had in the previous block, modulo 17, and
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


def _lz77_tokens(chunk, level=9):
    """`chunk` as literals and back-references, all within the chunk itself."""
    compressor = zlib.compressobj(level, zlib.DEFLATED, -15, 9)
    return _parse_deflate(compressor.compress(chunk) + compressor.flush())


# ---------------------------------------------------------------------------
# LZX blocks
# ---------------------------------------------------------------------------

class _FrameTooLarge(Exception):
    """Raised when a frame will not fit its own header's size field."""


def _operations(chunk, tokens):
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
                append((chunk[position], -1, 0, 0, 1))
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


def _compress_chunk(chunk):
    """One chunk as LZX frames, or None if that is no smaller than storing it.

    A single verbatim block covers the whole chunk and ends on its last byte,
    so the decoder's block state is clean again for the next chunk.
    """
    tokens = _lz77_tokens(chunk)
    operations = _operations(chunk, tokens)

    main_freqs = [0] * LZX_MAIN_SYMBOLS
    secondary_freqs = [0] * LZX_NUM_SECONDARY_LENGTHS
    for symbol, secondary, _value, _bits, _emitted in operations:
        main_freqs[symbol] += 1
        if secondary >= 0:
            secondary_freqs[secondary] += 1

    main_lengths = _huffman_lengths(main_freqs, LZX_MAX_CODE_LENGTH)
    main_codes = _canonical_codes(main_lengths)
    secondary_lengths = _huffman_lengths(secondary_freqs, LZX_MAX_CODE_LENGTH)
    secondary_codes = _canonical_codes(secondary_lengths)

    writer = _BitWriter()
    # No E8 (x86 call) translation. The decoder reads this bit once per chunk,
    # before the first block.
    writer.write(0, 1)
    writer.write(LZX_BLOCKTYPE_VERBATIM, 3)
    writer.write(len(chunk), 24)
    # Every length is delta coded against the previous block's, and the
    # decoder zeroes those at the start of each chunk (see _lzx_inflate).
    zeros = [0] * LZX_MAIN_SYMBOLS
    _write_lengths(writer, main_lengths, zeros, 0, LZX_NUM_CHARS)
    _write_lengths(writer, main_lengths, zeros, LZX_NUM_CHARS, LZX_MAIN_SYMBOLS)
    _write_lengths(writer, secondary_lengths, [0] * LZX_NUM_SECONDARY_LENGTHS,
                   0, LZX_NUM_SECONDARY_LENGTHS)

    frames = []
    emitted = 0
    for symbol, secondary, value, bits, size in operations:
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
    if sum(size for _data, size in frames) != len(chunk):
        raise RuntimeError("LZX encoder lost track of a chunk's output size")

    out = bytearray()
    for i, (data, size) in enumerate(frames):
        out += _frame(data, size, last=i + 1 == len(frames))
    out += FRAME_TERMINATOR

    if len(out) >= len(chunk):
        return None
    return bytes(out)


def _frame(data, uncompressed_size, last):
    """One frame, with the header lfs_decompress._lzx_inflate expects.

    Both of its sizes are big-endian u2. The two byte header says only how
    many compressed bytes follow and leaves the uncompressed size implied, so
    it can only carry a frame of the standard size; the five byte one the
    0xFF marker introduces spells both out.

    A chunk's last frame always takes the long header, even when its
    uncompressed size is the standard one and the short header would do. That
    is what the game's own data does without exception: over a 700 archive
    sample every one of 65594 compressed chunks ends on a long header, and
    every frame before it uses the short one.
    """
    size = len(data)
    if size > 0xFFFF:
        # Both header forms hold the compressed size in a u2. A frame this
        # large means the data did not compress at all, and the chunk it
        # belongs to is about to be stored instead.
        raise _FrameTooLarge()
    if not last and uncompressed_size == FRAME_SIZE and (size >> 8) != SHORT_FRAME_HEADER_MARKER:
        return struct.pack(">H", size) + data
    return struct.pack(">BHH", SHORT_FRAME_HEADER_MARKER, uncompressed_size, size) + data


def compress_chunks(payload):
    """`payload` split into .lfs chunks, each as (bytes, is_compressed).

    Each chunk is compressed on its own, referring to nothing outside itself,
    so it does not matter what the chunks around it are or whether they are
    compressed at all. A chunk that does not come out smaller compressed is
    stored instead.
    """
    chunks = []
    for start in range(0, len(payload), LFS_CHUNK_SIZE):
        chunk = payload[start:start + LFS_CHUNK_SIZE]
        try:
            compressed = _compress_chunk(chunk)
        except _FrameTooLarge:
            compressed = None
        chunks.append((chunk, False) if compressed is None else (compressed, True))
    if not chunks:
        # A zero-length payload still needs a chunk: num_chunks == 0 is
        # rejected as a malformed header on the way back in.
        chunks.append((b"", False))
    return chunks


def compress_lfs(payload, file_id=LFS_DEFAULT_FILE_ID):
    """`payload` wrapped as a complete .lfs file."""
    payload = bytes(payload)
    chunks = compress_chunks(payload)

    table = bytearray()
    body = bytearray()
    # Offsets are measured from the start of the chunk table, so the first
    # chunk's data begins right after the table itself.
    table_size = len(chunks) * 8
    chunk_total = 0
    for i, (data, is_compressed) in enumerate(chunks):
        decompressed_size = min(len(payload) - i * LFS_CHUNK_SIZE, LFS_CHUNK_SIZE)
        # 0x10000 doesn't fit a u2; the format spells a full chunk as 0, and
        # a compressed chunk that grew past 0x10000 wraps the same way.
        offset = table_size + len(body)
        table += struct.pack("<HHI", len(data) % LFS_CHUNK_SIZE,
                             decompressed_size % LFS_CHUNK_SIZE,
                             offset | (1 if is_compressed else 0))
        body += data
        chunk_total += len(data)
        if i + 1 < len(chunks):
            # Chunks are padded to 16 bytes, the last one not at all, which
            # is also what keeps the offsets even and the flag bit free.
            body += b"\x00" * (-len(body) % CHUNK_ALIGNMENT)

    # size_compressed is the sum of the chunks' own bytes: not the file size,
    # and neither the chunk table nor the padding between chunks counts
    # towards it. Checked against a sample of real archives.
    header = struct.pack("<5I", LFS_MAGIC1, file_id, len(payload),
                         chunk_total, len(chunks))
    return header + bytes(table) + bytes(body)
