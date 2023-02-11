meta:
  endian: le
  file-extension: arc
  id: arc
  ks-version: 0.10
  title: MTFramework archive format


seq:
  - {id: ident, contents: [0x41, 0x52, 0x43, 0x00]}
  - {id: version, type: s2}
  - {id: num_files, type: s2}
  - {id: file_entries, type: file_entry, repeat: expr, repeat-expr: num_files}
  # TODO: padding

types:
  file_entry:
    seq:
      - {id: file_path, type: str, encoding: ascii, size: 64, terminator: 0}
      - {id: file_type, type: s4}
      - {id: zsize, type: u4}
      - {id: size, type: b24}
      - {id: flags, type: b8}
      - {id: offset, type: u4}
    instances:
      raw_data:
        {io: _root._io, pos: offset, size: zsize}
