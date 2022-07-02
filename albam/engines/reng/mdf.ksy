meta:
    id: reengine_mdf
    endian: le
    title: RE Engine material info format
    license: CCO-1.0
    ks-version: 0.8

seq:
    - {id: id_magic, contents: [0x4d, 0x44, 0x46, 0x00]}
    - {id: unk_01, type: u2}
    - {id: num_materials, type: u2}
    - {id: unk_02, type: u4}
    - {id: unk_03, type: u4}
    - {id: materials, type: material, repeat: expr, repeat-expr: num_materials}

types:
  material:
    seq:
      - {id: ofs_material_name, type: u8}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}  # size of floatStr (?)
      - {id: num_textures, type: u4}
      - {id: unk_05, type: u4} # flags, first isAlpha (?)
      - {id: unk_06, type: u4} # ofs_float_hdr
      - {id: unk_07, type: u8}
      - {id: ofs_textures, type: u8}
      - {id: unk_09, type: u8}
      - {id: unk_10, type: u8}
    instances:
      name_raw:  # Hack to overcome https://github.com/kaitai-io/kaitai_struct/issues/187
        {pos: ofs_material_name, type: u2, repeat: until, repeat-until: _ == 0}

      textures:
        {pos: ofs_textures, type: texture_info, repeat: expr, repeat-expr: num_textures}

  texture_info:
    seq:
      - {id: ofs_texture_type, type: u8}
      - {id: unk_01, type: u8}
      - {id: ofs_texture_name, type: u8}

    instances:
      texture_type_raw: # Hack to overcome https://github.com/kaitai-io/kaitai_struct/issues/187
        {pos: ofs_texture_type, type: u2, repeat: until, repeat-until: _ == 0}

      texture_name_raw:  # Hack to overcome https://github.com/kaitai-io/kaitai_struct/issues/187
        {pos: ofs_texture_name, type: u2, repeat: until, repeat-until: _ == 0}
