meta:
  id: lfs
  file-extension: lfs
  endian: le
  bit-endian: le
  ks-version: "0.11"
  title: RE4 UHD LZX ("xcompress") compressed container

doc: |
  An .lfs is a compression wrapper, not a file archive: it holds exactly one
  payload, split into fixed-size chunks that are each compressed on their own.
  What the payload *is* comes from the extension the file name carries before
  ".lfs" - "r20d.udas.lfs" is a UDAS container, "icon_u.tpl.lfs" is a single
  TPL (see albam/engines/cie/fs.py).

  Every chunk decompresses to 0x10000 bytes except the last, and both size
  fields are u2, so a full-size chunk is stored as 0 in them. Across a real
  install (350907 chunks) `size_decompressed` is 0 for 346438 of them and
  `size_compressed` is never 0, compressed chunks always coming out smaller
  than the chunk size.

  Chunks are not necessarily compressed. The low bit of `offset` is the
  compressed flag and the rest is the chunk's own position, measured from the
  start of the chunk table (that is, from byte 20, past this header). A chunk
  with the bit clear is stored: its bytes are the payload's, verbatim. Real
  game data almost never uses this - exactly one chunk in the whole install is
  stored - but the game's own loader accepts it, which is what lets albam
  write an .lfs without implementing an LZX encoder.

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
      # 0 means a full 0x10000 chunk - see this format's own doc.
      len_raw_data:
        value: 'size_compressed == 0 ? 0x10000 : size_compressed'
      raw_data:
        {pos: (offset & ~1) + 20, size: len_raw_data}
