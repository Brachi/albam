meta:
  id: lfs
  file-extension: lfs
  endian: le
  bit-endian: le
  ks-version: "0.11"
  title: RE4UHD LZX ("xcompress") compressed container

doc: |
  An .lfs is a compression wrapper, not a file archive: it holds exactly one
  payload, split into fixed-size chunks that are each compressed on their own.
  What the payload *is* comes from the extension the file name carries before
  ".lfs" - "r20d.udas.lfs" is a UDAS container, "icon_u.tpl.lfs" is a single
  TPL (see albam/engines/cie/fs.py).

  Every chunk decompresses to 0x10000 bytes except the last, and both size
  fields are u2. That is one byte too narrow for a full chunk, so both are
  stored **modulo 0x10000**: `size_decompressed` reads 0 for a full chunk
  (346438 of 350907 across a real install), and `size_compressed` wraps for a
  chunk that barely compresses - one whose real compressed size is 65564
  reads as 28. A chunk's real size can only be recovered from the distance to
  the next chunk, which is why albam/engines/cie/lfs_decompress.py slices the
  chunk data rather than this declaring a size for it. Chunks are padded to
  16 bytes, the last one not being padded at all.

  Chunks are not necessarily compressed. The low bit of `offset` is the
  compressed flag and the rest is the chunk's own position, measured from the
  start of the chunk table (that is, from byte 20, past this header). A chunk
  with the bit clear is stored: its bytes are the payload's, verbatim. Real
  game data almost never uses this - exactly one chunk in the whole install is
  stored - but the game's own loader accepts it either way, so an .lfs can be
  written without compressing anything.

seq:
  - {id: header, type: lfs_header}
  - {id: chunks, type: chunk, repeat: expr, repeat-expr: header.num_chunks}

types:
  lfs_header:
    seq:
    - {id: id_magic, contents: [0x52, 0x44, 0x4c, 0x58]}
    - {id: file_id, type: u4} # 0xaabaeefe
    - {id: size_decompressed, type: u4}
    - {id: size_compressed, type: u4}
    - {id: num_chunks, type: u4}
  chunk:
    seq:
    - {id: size_compressed, type: u2}
    - {id: size_decompressed, type: u2}
    # Low bit: 1 = LZX compressed, 0 = stored. Rest: position from byte 20.
    - {id: offset, type: u4}
    instances:
      is_compressed:
        value: (offset & 1) != 0
      # Where this chunk's bytes start. How many there are cannot be said
      # here: the count is modulo 0x10000 (see this format's own doc) and is
      # recovered from the next chunk's position.
      data_offset:
        value: (offset & ~1) + 20
