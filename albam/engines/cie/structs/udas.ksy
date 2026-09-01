meta:
  id: udas
  file-extension: udas
  ks-version: "0.11"
  title: Capcom Internal Engine block container
  endian: le

doc: |
  A UDAS wraps one or more blocks, described by a table of 32-byte
  descriptors starting at 0x20 and ending at one whose `block_type` is
  0xFFFFFFFF. `block_type` 0 is the DAT block - the file table every model,
  texture and animation in a character archive lives in - and a non-zero
  type is a trailing sound block, whose descriptor carries a `size` of 0
  because it simply runs to the end of the file.

  The 8 words before the table are the same value repeated. It is a signature
  no reader validates and it says nothing about the container - see id_magic.

  This models the little-endian variant, the one all but a couple of archives
  of an install use. albam/engines/cie/fs.py tells the other one apart and
  says why it cannot be listed.

  The DAT block's own layout is the same one dat.ksy models standalone, so
  the two agree field for field; it is repeated here rather than shared
  because a .dat entry's offsets are relative to the file while a UDAS's are
  relative to the block.

seq:
 - {id: header, type: udas_header}

types:
  udas_header:
    seq:
    # The same word repeated 8 times, either 0xCAB6BE20 or its byte-reverse
    # 0x20BEB6CA. Both values occur in archives whose fields are
    # little-endian, so the word is not a byte-order mark and no reader
    # validates it. What varies between archives is the byte order of the
    # block table below, which albam/engines/cie/fs.py reads for itself.
    - {id: id_magic, type: u4, repeat: expr, repeat-expr: 8}
    - {id: blocks, type: block_descriptor, repeat: until,
       repeat-until: _.block_type == 0xffffffff}
    instances:
     # Block 0 is the DAT block in every archive seen. The table is walked in
     # order by every reader of this format, JADERLINK's included, rather
     # than searched by type.
     data_block:
      value: blocks[0]
     data_offset:
      value: data_block.offset
     file_size:
      value: data_block.size
     data_blocks:
      {pos: data_offset, type: udas_data}

  block_descriptor:
    seq:
    - {id: block_type, type: u4}
    # 0 for a sound block: it runs from `offset` to the end of the file.
    - {id: size, type: u4}
    - {id: unused, type: u4}
    - {id: offset, type: u4}
    - {id: padding, size: 16}

  udas_data:
    seq:
    - {id: num_files, type: u4}
    - {id: padding, type: u4, repeat: expr, repeat-expr: 3}
    # Relative to the start of this block, not to the file.
    - {id: offsets, type: u4, repeat: expr, repeat-expr: num_files}
    - {id: file_extension, type: extension, repeat: expr, repeat-expr: num_files}
    instances:
     file_entries:
      type: file_entry(_index) # <= pass `_index` into file_body
      repeat: expr
      repeat-expr: num_files

  file_entry:
    params:
      - id: i               # => receive `_index` as `i` here
        type: s4
    instances:
      raw_data:
        pos: _parent.offsets[i] + _root.header.data_offset
        size: "i == _parent.num_files - 1 ?
              (_root.header.file_size - _parent.offsets[i]) :
              (_parent.offsets[i + 1] - _parent.offsets[i])"

  extension:
    seq:
      # A blank extension is a real, empty slot in the table, not a missing
      # one - see albam/engines/cie/fs.py, which keeps it listed.
      - {id: ext, type: str , size: 4, encoding: UTF-8, terminator: 0}
