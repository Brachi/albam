meta:
    id: reengine_mdf
    endian: le
    title: RE Engine material info format
    license: CCO-1.0
    ks-version: 0.8

params:
  - {id: mdf_version, type: u4}

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
      - {id: hash, type: u4}
      - {id: size_properties, type: u4}
      - {id: num_properties_headers, type: u4}
      - {id: num_textures, type: u4}
      - {id: unk_01, type: u8, if: _root.mdf_version >= 19}
      - {id: material_shading_type, type: u4}
      - {id: alpha_flags, type: alpha_flags}
      - {id: ofs_properties_headers, type: u8}
      - {id: ofs_texture_headers, type: u8}
      - {id: ofs_first_material_name, type: u8, if: _root.mdf_version >= 19}
      - {id: ofs_properties, type: u8}
      - {id: ofs_master_material_path, type: u8}
    instances:
      name_raw:  # Hack to overcome https://github.com/kaitai-io/kaitai_struct/issues/187
        {pos: ofs_material_name, type: u2, repeat: until, repeat-until: _ == 0}
      name:
        {pos: ofs_material_name, type: str, encoding: utf-16, size: (name_raw.size * 2) - 2}
      textures:
        {pos: ofs_texture_headers, type: texture_header, repeat: expr, repeat-expr: num_textures}
      properties_headers:
          pos: ofs_properties_headers
          repeat: expr
          repeat-expr: num_properties_headers
          type:
            switch-on: _root.mdf_version
            cases:
              10: properties_header_10
              13: properties_header_13
              21: properties_header_13
      master_material_path_raw:
        {pos: ofs_master_material_path, type: u2, repeat: until, repeat-until: _ == 0}
      master_material_path:
        {pos: ofs_master_material_path, type: str, encoding: utf-16, size: (master_material_path_raw.size * 2) - 2}

  properties_header_10:
    seq:
      - {id: ofs_name, type: u8}
      - {id: name_hash_utf16, type: u4}
      - {id: name_hash_ascii, type: u4}
      - {id: num_params, type: u4}
      - {id: ofs_prop, type: u4}
    instances:
      name_raw:
        {pos: ofs_name, type: u2, repeat: until, repeat-until: _ == 0}
      params:
        {pos: _parent.ofs_properties + ofs_prop, type: f4, repeat: expr, repeat-expr: num_params}
      name:
        {pos: ofs_name, type: str, encoding: utf-16, size: (name_raw.size * 2) - 2}


  properties_header_13:
    seq:
      - {id: ofs_name, type: u8}
      - {id: name_hash_utf16, type: u4}
      - {id: name_hash_ascii, type: u4}
      - {id: ofs_prop, type: u4}
      - {id: num_params, type: u4}
    instances:
      name_raw:
        {pos: ofs_name, type: u2, repeat: until, repeat-until: _ == 0}
      params:
        {pos: _parent.ofs_properties + ofs_prop, type: f4, repeat: expr, repeat-expr: num_params}
      name:
        {pos: ofs_name, type: str, encoding: utf-16, size: (name_raw.size * 2) - 2}

  texture_header:
    seq:
      - {id: ofs_texture_type, type: u8}
      - {id: hash_utf16, type: u4}
      - {id: hash_ascii, type: u4}
      - {id: ofs_texture_path, type: u8}
      - {id: unk_01, type: u8, if: _root.mdf_version >= 13}

    instances:
      texture_type_raw:
        {pos: ofs_texture_type, type: u2, repeat: until, repeat-until: _ == 0}
      texture_path_raw:
        {pos: ofs_texture_path, type: u2, repeat: until, repeat-until: _ == 0}
      texture_type:
        {pos: ofs_texture_type, type: str, encoding: utf-16, size: (texture_type_raw.size * 2) - 2}
      texture_path:
        # Thanks to https://github.com/kaitai-io/kaitai_struct/issues/187#issuecomment-1585245651
        {pos: ofs_texture_path, type: str, encoding: utf-16, size: (texture_path_raw.size * 2) - 2}

  alpha_flags:
    seq:
      - {id: base_two_side_enable, type: b1}
      - {id: base_alpha_test_enable, type: b1}
      - {id: shadow_cast_disable, type: b1}
      - {id: vertex_shader_used, type: b1}
      - {id: emissive_used, type: b1}
      - {id: tessellation_enable, type: b1}
      - {id: enable_ignore_depth, type: b1}
      - {id: alpha_mask_used, type: b1}
      - {id: forced_two_side_enable, type: b1}
      - {id: two_side_enable, type: b1}
      - {id: tess_factor, type: b6}
      - {id: phong_factor, type: b1} ## empty?
      - {id: rough_transparent_enable, type: b1}
      - {id: forced_alpha_test_enable, type: b1}
      - {id: alpha_test_enable, type: b1}
      - {id: sss_profile_used, type: b1}
      - {id: enable_stencil_priority, type: b1}
      - {id: require_dual_quaternion, type: b1}
      - {id: pixel_depth_offset_used, type: b1}
      - {id: no_ray_tracing, type: b1}
      - {id: unk_01, type: b7}
