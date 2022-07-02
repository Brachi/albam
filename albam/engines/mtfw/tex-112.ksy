meta:
  id: mtframework_tex
  endian: le
  title:  Resident Evil 5 (MTFramework) texture format
  application: Resident Evil 5/Biohazard 5
  file-extension: tex
  license: CC0-1.0
  ks-version: 0.8

seq:
  - id: ident
    contents: [0x54, 0x45, 0x58, 0x00]
  - id: version
    type: u2
  - id: revision
    type: u2
  - id: num_mipmaps
    type: u1
  - id: unk_01
    type: u1
  - id: unk_02
    type: u1
  - id: unk_03
    type: u1
  - id: width
    type: u2
  - id: height
    type: u2
  - id: reserved
    type: u4
  - id: compression_format
    type: str
    encoding: ascii
    size: 4
  - id: unk_04
    type: f4
  - id: unk_05
    type: f4
  - id: unk_06
    type: f4
  - id: unk_07
    type: f4
  - id: offsets_mipmaps
    type: u4
    repeat: expr
    repeat-expr: num_mipmaps
  - id: dds_data
    size-eos: true
