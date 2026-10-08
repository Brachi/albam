"""The .lfs container: its chunk table, and the payload behind it.

The LZX streams each chunk holds are decoded by albam.lib.xcompress, which
this shared out - MT Framework archives carry the same streams (see
albam/engines/mtfw/arc_fs.py). What stays here is the container: how chunks
are sized, stored and written back.
"""

import struct

from ...lib.xcompress import (  # noqa: F401 - re-exported for lfs_compress
    EXTRA_BITS,
    POSITION_BASE,
    _LzxState,
    _lzx_inflate,
)

LFS_MAGIC1 = 0x584C4452
LFS_CHUNK_SIZE = 0x10000
# The value real archives carry in the header's second word - the same in
# every one of a 400-archive sample, so a constant rather than an id.
LFS_DEFAULT_FILE_ID = 0xFEEEBAAA
# Chunk data is padded to this; the last chunk is not padded.
CHUNK_ALIGNMENT = 16
# Bytes before the chunk table, which chunk offsets are measured from.
LFS_HEADER_SIZE = 20


# ============================================================================
# LFS public API
# ============================================================================

def is_lfs(data):
    """Check if data starts with the LFS magic."""
    if len(data) < 20:
        return False
    magic = struct.unpack_from("<I", data, 0)[0]
    return magic == LFS_MAGIC1


def lfs_decompress(data):
    """
    Decompress an LFS file (RE4UHD format).
    Accepts bytes or bytearray. Returns bytearray.
    """
    if isinstance(data, (bytes, memoryview)):
        data = bytearray(data)

    if len(data) < 20:
        raise RuntimeError("Data too small for LFS header")

    magic, _, size_decompressed, _, num_chunks = struct.unpack_from("<5I", data, 0)
    if magic != LFS_MAGIC1:
        raise RuntimeError(f"Invalid LFS magic: 0x{magic:08X}")
    if num_chunks == 0 or num_chunks > 0x10000:
        raise RuntimeError(f"Invalid chunk count: {num_chunks}")

    header_size = 20
    chunk_table_offset = header_size
    # Each chunk entry: u16 size_compressed, u16 size_decompressed, u32 offset
    chunk_entry_size = 8
    chunks_base = chunk_table_offset

    out = bytearray(size_decompressed)
    out_pos = 0
    st = _LzxState(131072)

    for i in range(num_chunks):
        entry_offset = chunks_base + i * chunk_entry_size
        c_sz, d_sz, offset = struct.unpack_from("<HHI", data, entry_offset)

        comp_data_offset = chunks_base + (offset & ~1)
        comp_size = c_sz if c_sz != 0 else LFS_CHUNK_SIZE
        decomp_size = d_sz if d_sz != 0 else LFS_CHUNK_SIZE

        if out_pos + decomp_size > size_decompressed:
            decomp_size = size_decompressed - out_pos

        if not (offset & 1):
            # Uncompressed chunk
            out[out_pos:out_pos + comp_size] = data[comp_data_offset:comp_data_offset + comp_size]
            out_pos += comp_size
        else:
            # LZX compressed chunk
            written = _lzx_inflate(st, data, comp_data_offset, comp_size,
                                   out, out_pos, decomp_size)
            out_pos += written

    return out[:out_pos]


def chunk_sizes(chunks, stream_size):
    """The real compressed length of every chunk.

    `size_compressed` is a u2 holding a length that can reach 0x10000 and
    beyond - a chunk that barely compresses ends up larger than the chunk
    size - so it is stored modulo 0x10000 and cannot be read at face value.
    What pins it down is the distance to the next chunk: chunks are laid out
    in order, padded to 16 bytes (the last one not padded), so the real
    length is the only value congruent to `size_compressed` that lands in
    that distance.

    This also covers the ordinary full-size chunk, which stores 0 and means
    0x10000, without needing a special case for it.
    """
    positions = [chunk.data_offset for chunk in chunks]
    sizes = []
    for i, chunk in enumerate(chunks):
        end = positions[i + 1] if i + 1 < len(positions) else stream_size
        gap = end - positions[i]
        size = chunk.size_compressed
        while size <= gap - CHUNK_ALIGNMENT:
            size += LFS_CHUNK_SIZE
        sizes.append(min(size, gap))
    return sizes


def xcompress_decompress_re4hd(chunks):
    """The payload of an .lfs, from its parsed chunk list (see lfs.ksy).

    Chunks are decoded through one shared LZX state, which is what this
    decoder's original does. Real data never needs it - across a 150 archive
    sample none of 72146673 matches reaches back past the start of its own
    chunk - and the game's own decoder gives a chunk no history at all, so a
    chunk anything but albam wrote does decode on its own. The state is
    carried anyway because it costs nothing and reads strictly more.

    An .lfs is still only ever read whole, though: the chunk table has no
    index of its own, so there is nothing to seek to a single file by.
    """
    dec_data = bytearray()
    if not chunks:
        return dec_data

    stream = chunks[0]._io
    sizes = chunk_sizes(chunks, stream.size())
    st = _LzxState(131072)

    for i, chunk in enumerate(chunks):
        stream.seek(chunk.data_offset)
        raw = stream.read_bytes(sizes[i])
        expected_size = LFS_CHUNK_SIZE if chunk.size_decompressed == 0 else chunk.size_decompressed

        if not chunk.is_compressed:
            dec_data.extend(raw)
            continue

        chunk_out = bytearray(expected_size)
        written = _lzx_inflate(st, bytearray(raw), 0, len(raw), chunk_out, 0, expected_size)
        if written != expected_size:
            raise RuntimeError(
                f"Chunk {i} output size mismatch (got {written}, expected {expected_size})")
        dec_data.extend(chunk_out[:expected_size])

    return dec_data


def xcompress_compress_re4hd(payload, file_id=LFS_DEFAULT_FILE_ID, compress=True):
    """`payload` wrapped as a complete .lfs file, chunks LZX compressed.

    Pass compress=False to store them instead. A stored archive is valid -
    the format flags each chunk either way and the game reads both - but it
    is around 2.8x the size of a compressed one.

    Getting compression accepted took three fixes, each the same shape: this
    module's decoder accepts more than the game's does, so an encoder written
    against it was free to emit what the game rejects. Matches reached back
    into earlier chunks, which the game gives an empty window; one-symbol
    Huffman trees were left incomplete; and a chunk did not end the way every
    shipped one does (see lfs_compress). An archive written this way now
    loads in the game.
    """
    if not compress:
        return store_lfs(payload, file_id)
    from .lfs_compress import compress_lfs
    return compress_lfs(payload, file_id)


def store_lfs(payload, file_id=LFS_DEFAULT_FILE_ID):
    """`payload` wrapped as an .lfs whose chunks are all stored.

    No LZX involved: the chunk table's flag says each chunk is verbatim, and
    the game's own data contains such a chunk, so its loader accepts them.
    """
    payload = bytes(payload)
    chunks = [payload[i:i + LFS_CHUNK_SIZE]
              for i in range(0, len(payload), LFS_CHUNK_SIZE)]
    if not chunks:
        # A zero-length payload still needs a chunk: num_chunks == 0 is
        # rejected as a malformed header on the way back in.
        chunks = [b""]

    table = bytearray()
    body = bytearray()
    table_size = len(chunks) * 8
    total = 0
    for i, chunk in enumerate(chunks):
        # 0x10000 doesn't fit a u2; the format spells a full chunk as 0.
        size = len(chunk) % LFS_CHUNK_SIZE
        # Low bit clear: stored. Offsets are measured from the chunk table.
        table += struct.pack("<HHI", size, size, table_size + len(body))
        body += chunk
        total += len(chunk)
        if i + 1 < len(chunks):
            body += b"\x00" * (-len(body) % CHUNK_ALIGNMENT)

    header = struct.pack("<5I", LFS_MAGIC1, file_id, len(payload), total, len(chunks))
    return header + bytes(table) + bytes(body)
