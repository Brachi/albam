meta:
  bit-endian: le
  endian: le
  file-extension: arc
  id: arc
  ks-version: 0.10
  title: MTFramework archive format


seq:
  - {id: header, type: arc_header}
  - {id: file_entries, type: file_entry, repeat: expr, repeat-expr: _root.header.num_files}
  - {id: padding, size: 32760 - (_root.header.num_files * 80) % 32760}

types:
  arc_header:
    seq:
    - {id: ident, contents: [0x41, 0x52, 0x43, 0x00]}
    - {id: version, type: s2}
    - {id: num_files, type: s2}
    instances:
      size_:
        value: 8 
  file_entry:
    seq:
      - {id: file_path, type: str, encoding: ascii, size: 64, terminator: 0}
      - {id: file_type, type: s4}
      - {id: zsize, type: u4}
      - {id: size, type: b29}
      - {id: flags, type: b3}
      - {id: offset, type: u4}
    instances:
      raw_data:
        {io: _root._io, pos: offset, size: zsize}