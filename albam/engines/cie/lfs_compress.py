"""The .lfs side of the LZX encoder: how RE4UHD chunks a payload up.

The LZX itself - the bit packing, the Huffman trees, the blocks and the
frames - lives in albam/lib/xcompress_encode.py, which this shared out when
MT Framework archives needed the same streams without .lfs chunking around
them. What stays here is the container.

Two things about that container shape a chunk more than the bit format does
(see lfs.ksy and xcompress_decompress_re4hd):

* No match reaches out of its own chunk. The decoder would allow it - it
  carries one window across the whole file, so a chunk can refer to what the
  chunks before it decoded - and an earlier version of this encoder did
  exactly that, producing archives that decoder read back perfectly and the
  game rejected outright. The game's own data says why: over a 150 archive
  sample, of 72146673 matches not one reaches back past the start of the
  chunk it lives in, and the longest distance seen anywhere is 65469, under
  one chunk. So a chunk here is compressed on its own, as a stream of its
  own, and decodes wherever it sits in the file.
* Per chunk the decoder resets the code lengths and the three repeated
  offsets, but not the window, not the current block and not the trees. So
  every chunk here starts a fresh block and ends exactly on its last byte,
  leaving no partial block for the next chunk to fall into.
* A chunk says where its frames stop, rather than leaving that to whoever
  counts the bytes coming out: its last frame takes the long header and five
  zero bytes follow it (see FRAME_TERMINATOR). The decoder needs neither,
  which is how an encoder written against it came to omit both. An .arc
  entry, framing the same streams, has no terminator at all - which is why
  it belongs here and not in the shared encoder.
"""
import struct

from ...lib.xcompress_encode import FrameTooLarge, compress_frames, frame_stream
from .lfs_decompress import (
    CHUNK_ALIGNMENT,
    LFS_CHUNK_SIZE,
    LFS_DEFAULT_FILE_ID,
    LFS_MAGIC1,
)

# Closes a chunk, after its last frame. Reads as a frame header declaring no
# compressed bytes, which is what stops a reader that walks frames until they
# run out rather than until the output is full. Every compressed chunk in the
# game's own data ends with exactly these five bytes, and they count towards
# the chunk's size in the chunk table.
FRAME_TERMINATOR = b"\x00" * 5


def _compress_chunk(chunk):
    """One chunk as LZX frames, or None if that is no smaller than storing it.

    A single verbatim block covers the whole chunk and ends on its last byte,
    so the decoder's block state is clean again for the next chunk.
    """
    out = bytearray(frame_stream(compress_frames(chunk)))
    out += FRAME_TERMINATOR
    if len(out) >= len(chunk):
        return None
    return bytes(out)


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
        except FrameTooLarge:
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
