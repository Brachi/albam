meta:
  id: reengine_pak
  endian: le
  title:  Resident Evil 2 Remake pak format
  application: Resident Evil 2 Remake
  file-extension: pak
  license: CC0-1.0
  ks-version: 0.8


seq:
  - id: ident
    contents: [0x4b, 0x50, 0x4b, 0x41]
  - id: version
    type: u4
  - id: num_files
    type: s4
  - id: reserved
    type: s4
  - id: files
    type: file_entry
    repeat: expr
    repeat-expr: num_files


types:
  file_entry:
    seq:
      - id: name_crc_l
        type: u4
      - id: name_crc_u
        type: u4
      - id: offset
        type: s8
      - id: zsize
        type: s8
      - id: size
        type: s8
      - id: flags
        type: s8
      - id: unk_01
        type: s8
