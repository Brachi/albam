meta:
  endian: le
  file-extension: mrl
  id: mrl
  ks-version: 0.10
  title: MTFramework material format
seq:
  - {id: id_magic, contents: [0x4d, 0x52, 0x4c, 0x00]}
  - {id: version, type: u4}
  - {id: num_materials, type: u4}
  - {id: num_textures, type: u4}
  - {id: unk_01, type: u4}
  - {id: ofs_textures, type: u4}
  - {id: ofs_materials, type: u4}
  - {id: textures, type: texture_slot, repeat: expr, repeat-expr: num_textures}
  - {id: materials, type: material, repeat: expr, repeat-expr: num_materials}

types:
  resource_binding:
    seq:
      - {id: resource_type, type: u4}
      - {id: resource_index, type: u4}
      - {id: unk_01, type: u4}

  texture_slot:
    seq:
      - {id: unk_01, type: u1, repeat: expr, repeat-expr: 4}
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}
      - {id: texture_path, type: str, size: 64, encoding: ascii, terminator: 0}

  material:
    seq:
      - {id: unk_01, type: u4}
      - {id: name_hash_crcjam32, type: u4}
      - {id: size_data, type: u4}
      - {id: unk_04, type: u4}
      - {id: unk_05, type: u1, repeat: expr, repeat-expr: 4}
      - {id: unk_06, type: u1, repeat: expr, repeat-expr: 4}
      - {id: num_resources, type: u1}
      - {id: unk_07, type: u1, repeat: expr, repeat-expr: 3}
      - {id: unk_08, type: u1, repeat: expr, repeat-expr: 4}
      - {id: unk_09, type: u1, repeat: expr, repeat-expr: 4}
      - {id: unk_10, type: u4}
      - {id: unk_11, type: u4}
      - {id: unk_12, type: u4}
      - {id: unk_13, type: u4}
      - {id: ofs_data, type: u4}
      - {id: unk_15, type: u4}

    instances:
      resources:
        {pos: ofs_data, type: resource_binding, repeat: expr, repeat-expr: num_resources}
