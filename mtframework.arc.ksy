meta:
  id: mtframework_arc
  endian: le
  title:  Resident Evil 5 (MTFramework) archive format
  application: Resident Evil 5/Biohazard 5
  file-extension: arc
  license: CC0-1.0
  ks-version: 0.8

seq:
  - id: ident
    contents: [0x41, 0x52, 0x43, 0x00]
  - id: version
    type: s2
  - id: files_count
    type: s2
  - id: file_entries
    type: file_entry
    repeat: expr
    repeat-expr: files_count
  # TODO: padding

types:
  file_entry:
    seq:
      - id: file_path
        type: str
        encoding: ascii
        size: 64
      - id: file_id
        type: s4
      - id: zsize
        type: u4
      - id: size
        type: b24
      - id: flags
        type: b8
      - id: offset
        type: u4
    instances:
      body:
        io: _root._io
        pos: offset
        size: zsize
