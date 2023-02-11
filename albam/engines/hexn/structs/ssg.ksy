meta:
  id: hexane_ssg
  endian: le
  title: Hexane Engine Archive format
  file-extension: ssg
  license: CC0-1.0
  ks-version: 0.8

seq:
  - {id: id_magic, contents: [0x06, 0x00, 0x00, 0x00]}
  - {id: reserved_01, type: u4}
  - {id: size_files_info, type: u4}
  - {id: size_file_names, type: u4}
  - {id: size_chunks_buffer, type: u4}
  - {id: reserverd_01, type: u4}
  - {id: size_chunks_info, type: u4}
  - {id: size_padding, type: u4}
  - {id: files_info, type: file_info, repeat: expr, repeat-expr: size_files_info / 32}
  - {id: chunk_sizes, type: u4, repeat: expr, repeat-expr: size_chunks_info / 4}
  - {id: file_names, size: size_file_names}
  - {id: buffer_chunks, size: size_chunks_buffer}

types:
  file_info:
    seq:
      - {id: ident, type: u4}
      - {id: name_offset_rel, type: u4}
      - {id: size, type: u4}
      - {id: reserved_01, type: u4}
      - {id: reserved_02, type: u4}
      - {id: file_type, type: s4}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u4}
    instances: # convenience, although it's already read
      name:
        {type: str, terminator: 0, encoding: ASCII, pos: 32 + _parent.size_files_info + _parent.size_chunks_info + name_offset_rel}
