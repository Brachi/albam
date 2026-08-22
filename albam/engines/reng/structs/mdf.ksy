meta:
    id: reengine_mdf
    endian: le
    title: RE Engine material info format
    license: CCO-1.0
    ks-version: '0.11'

params:
  - {id: mdf_version, type: u4}

seq:
    - {id: id_magic, contents: [0x4d, 0x44, 0x46, 0x00]}
    # In-file format version counter, distinct from mdf_version (the param
    # passed in from the file's own extension, e.g. ".mdf2.21") - always
    # written as 1 regardless of game/mdf_version.
    - {id: format_version, type: u2}
    - {id: num_materials, type: u2}
    - {id: material_flags, type: u8} # almost always 0 (only ever seen set, to 1, for MHWILDS)
    - {id: materials, type: material, repeat: expr, repeat-expr: num_materials}

types:
  material:
    seq:
      - {id: ofs_material_name, type: u8}
      - {id: hash, type: u4}
      - {id: size_properties, type: u4}
      - {id: num_properties_headers, type: u4}
      - {id: num_textures, type: u4}
      # Counts for the "GPBF" buffer name/path table (see ofs_gpbf_buffer
      # below). That table is dead code in albam today - nothing reads it,
      # same as its offset.
      - {id: num_gpbf_buffer_names, type: u4, if: _root.mdf_version >= 19}
      - {id: num_gpbf_buffer_paths, type: u4, if: _root.mdf_version >= 19}
      - {id: material_shading_type, type: u4} # real enum exists upstream, but flagged there as game-version-fragile - not modeled here
      - {id: alpha_flags, type: alpha_flags}
      - {id: ofs_properties_headers, type: u8}
      - {id: ofs_texture_headers, type: u8}
      # Offset to the GPBF buffer name/path table (counts above); "GPBF"
      # is unexplained upstream too, and this offset is dead code in
      # albam (never read).
      - {id: ofs_gpbf_buffer, type: u8, if: _root.mdf_version >= 19}
      - {id: ofs_properties, type: u8}
      - {id: ofs_master_material_path, type: u8}
    instances:
      name_raw:  # Hack to overcome https://github.com/kaitai-io/kaitai_struct/issues/187
        {pos: ofs_material_name, type: u2, repeat: until, repeat-until: _ == 0}
      name:
        {pos: ofs_material_name, type: str, encoding: utf-16, size: (name_raw.size * 2) - 2}
      textures:
        {pos: ofs_texture_headers, type: texture_header, repeat: expr, repeat-expr: num_textures}
      # There are only ever two real property-header layouts: >=13 or <13
      # - not a per-version list (mdf_version 19 is RE8's own .mdf2
      # version, per apps.py).
      properties_headers:
          pos: ofs_properties_headers
          repeat: expr
          repeat-expr: num_properties_headers
          type:
            switch-on: _root.mdf_version >= 13
            cases:
              true: properties_header_13
              false: properties_header_10
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
      - {id: num_params, type: u2} # unk_flag (next field) is unexplained upstream too
      - {id: unk_flag, type: u2}
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
    # Kaitai defaults to MSB-first bit consumption within a byte; the real
    # struct this mirrors (RE-Mesh-Editor's ctypes MDFFlags_bits) is
    # LSB-first.
    meta:
      bit-endian: le
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
      - {id: phong_factor, type: b8} # 0-255 factor, not a flag - 10+6+8+8 = 32 bits exactly
      - {id: rough_transparent_enable, type: b1}
      - {id: forced_alpha_test_enable, type: b1}
      - {id: alpha_test_enable, type: b1}
      - {id: sss_profile_used, type: b1}
      - {id: enable_stencil_priority, type: b1}
      - {id: require_dual_quaternion, type: b1}
      - {id: pixel_depth_offset_used, type: b1}
      - {id: no_ray_tracing, type: b1}
