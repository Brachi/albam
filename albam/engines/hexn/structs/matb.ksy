meta:
  id: hexane_matb
  endian: le
  title: Hexane Engine Material Format
  file-extension: matb
  license: CC0-1.0
  ks-version: 0.8


seq:
  - {id: id_magic, contents: [0x4d, 0x41, 0x54, 0x7]}
  - {id: ofs_names, type: u4}
  - {id: num_textures, type: u4}
  - {id: unk_01, type: u4}
  - {id: unk_02, type: u4}
  - {id: unk_03, type: u4}
  - {id: unk_04, type: u4}
  - {id: unk_05, type: u4}
  - {id: unk_06, type: u4}
  - {id: unk_07, type: u4}
instances:
  shader:
      {pos: ofs_names, type: tmp}
types:
  tmp:
    seq:
      - {id: shader, type: strz, encoding: ASCII}
      - {id: textures, type: strz, encoding: ASCII, repeat: expr, repeat-expr: _parent.num_textures}
