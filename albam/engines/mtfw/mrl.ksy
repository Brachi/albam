meta:
  id: mrl
  file-extension: mrl
  endian: le
seq:
  - id: id_magic
    contents: [0x4d, 0x52, 0x4c, 0x00]
  - id: version
    type: u4
  - id: mat_lib_count
    type: u4
  - id: tex_lib_count
    type: u4
  - id: unk_01
    type: u4
  - id: tex_lib_offset
    type: u4
  - id: mat_lib_offset
    type: u4
instances:
  mat_lib:
    pos: mat_lib_offset
    type: mat_lib
    repeat: expr
    repeat-expr: mat_lib_count
  tex_lib:
    pos: tex_lib_offset
    type: tex_lib
    repeat: expr
    repeat-expr: tex_lib_count

types:
  tex_lib:
    seq:
      - id: unk_01
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_02
        type: u4
      - id: unk_03
        type: u4
      - id: texture_path
        type: str
        size: 64
        encoding: ascii
  mat_lib:
    seq:
      - id: unk_01
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_02
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_03
        type: u4
      - id: unk_04
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_05
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_06
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_07
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_08
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_09
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: unk_10
        type: u4
      - id: unk_11
        type: u4
      - id: unk_12
        type: u4
      - id: unk_13
        type: u4
      - id: unk_14
        type: u4
      - id: unk_15
        type: u4

