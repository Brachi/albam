meta:
  endian: le
  bit-endian: le
  file-extension: mrl
  id: mrl
  ks-version: 0.10
  title: MTFramework material format

params:
  - {id: app_id, type: str}  # TODO: enum

seq:
  - {id: id_magic, contents: [0x4d, 0x52, 0x4c, 0x00]}
  - {id: version, type: u4}
  - {id: num_materials, type: u4}
  - {id: num_textures, type: u4}
  - {id: shader_version, type: u4}
  - {id: ofs_textures, type: u4}
  - {id: ofs_materials, type: u4}
  - {id: textures, type: texture_slot, repeat: expr, repeat-expr: num_textures}
  - {id: materials, type: material, repeat: expr, repeat-expr: num_materials}

instances:
  size_textures_:
    value: "textures[0].size_ * num_textures"
  size_materials_:
    value: "materials[0].size_ * num_materials"
  ofs_textures_calculated:
    value: 28
  ofs_materials_calculated:
    value: "ofs_textures_calculated + size_textures_"
  ofs_resources_calculated_no_padding:  # TODO: # padding(16)
    value: size_top_level_ + size_textures_ + size_materials_
  ofs_resources_calculated:
    value: "ofs_resources_calculated_no_padding + (-ofs_resources_calculated_no_padding % 16)"
  size_top_level_:
    value: 28
  size_todo_:  # TODO: # padding(16) + sum(m.cmd_buffer_size + m.anim_data_size for m in materials)
    value: size_top_level_ + size_textures_ + size_materials_

types:
  texture_slot:  # TODO: rename-me
    seq:
      - {id: type_hash, type: u4, enum: texture_type} # rTexture not in mfx
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}
      - {id: texture_path, type: str, encoding: ASCII, terminator: 0}
      - {id: filler, type: u1, repeat: expr, repeat-expr:  64 - texture_path.length - 1}

    instances:
      size_:
        value: 76

  material: # MATERIAL_INFO
    seq:
      #- {id: type_hash, type: u4, enum: material_type} # TYPE_nDraw_MaterialStd not in mfx
      - {id: type_hash, type: u4}
      - {id: name_hash_crcjam32, type: u4}
      - {id: cmd_buffer_size, type: u4}
      - {id: blend_state_hash, type: u4}
      - {id: depth_stencil_state_hash, type: u4}
      - {id: rasterizer_state_hash, type: u4}
      - {id: num_resources, type: b12} # state_num
      - {id: reserverd1, type: b9}
      - {id: id, type: b8}
      - {id: fog, type: b1}
      - {id: tangent, type: b1}
      - {id: half_lambert, type: b1}
      - {id: stencil_ref, type: b8}
      - {id: alphatest_ref, type: b8}
      - {id: polygon_offset, type: b4}
      - {id: alphatest, type: b1}
      - {id: alphatest_func, type: b3}
      - {id: draw_pass, type: b5}
      - {id: layer_id, type: b2}
      - {id: deffered_lighting, type: b1}
      - {id: blend_factor, type: f4, repeat: expr, repeat-expr: 4}
      - {id: anim_data_size, type: u4}
      - {id: ofs_cmd, type: u4}
      - {id: ofs_anim_data, type: u4}
    instances:
      resources:
        {pos: ofs_cmd, type: resource_binding, repeat: expr, repeat-expr: num_resources}
      anims:
        {pos: ofs_anim_data, type: anim_data, if: anim_data_size != 0}
      size_:
        value: 60

  resource_binding:
    seq:
      - {id: cmd_type, type: b4, enum: cmd_type}
      - {id: unused, type: b16}  # Always 0xDCDC
      - {id: shader_obj_idx, type: b12}
      - id: value_cmd
        type:
          switch-on: cmd_type
          cases:
            "cmd_type::set_flag": shader_object
            "cmd_type::set_constant_buffer": cmd_ofs_buffer
            "cmd_type::set_sampler_state": shader_object
            "cmd_type::set_texture": cmd_tex_idx
            "cmd_type::set_unk": shader_object
      - {id: shader_object_id, type: u4}
    instances:
      size_:
        value: 12
      shader_object_hash:
        value: shader_object_id >> 12
        enum: shader_object_hash
      float_buffer:
        pos: _parent.ofs_cmd + value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
        type:
          switch-on: shader_object_hash
          cases:
            "shader_object_hash::globals": cb_globals
            "shader_object_hash::cbdistortion" : cb_distortion
            "shader_object_hash::cbmaterial" : cb_material
            "shader_object_hash::cbcolormask" : cb_color_mask
            "shader_object_hash::cbvertexdisplacement": cb_vertex_displacement
            "shader_object_hash::cbvertexdisplacement2": cb_vertex_displacement2
            "shader_object_hash::cbappclipplane": cb_app_clip_plane
            "shader_object_hash::cboutlineex": cb_outline_ex
            "shader_object_hash::cbddmaterialparam": cb_dd_material_param
            "shader_object_hash::cbappreflect": cb_app_reflect
            "shader_object_hash::cbappreflectshadowlight": cb_app_reflect_shadow_light
            "shader_object_hash::cbddmaterialparaminnercorrect": cb_dd_material_param_inner_correct
            "shader_object_hash::cbburncommon": cb_burn_common
            "shader_object_hash::cbburnemission": cb_burn_emission
            "shader_object_hash::cbspecularblend": cb_specular_blend
            "shader_object_hash::cbuvrotationoffset": cb_uv_rotation_offset
        if: cmd_type == cmd_type::set_constant_buffer

  anim_data:
    seq:
      - {id: entry_count, type: u4}
      - {id: ofs_to_info, type: anim_ofs, repeat: expr, repeat-expr: entry_count}
    instances:
      ofs_base:
        value: _parent.ofs_anim_data 

  anim_ofs:
    seq:
      - {id: ofs_block, type: u4}
    instances:
      anim_entries:
        pos: _parent._parent.ofs_anim_data + ofs_block
        type: anim_entry

  anim_entry:
    seq:
      - {id: unk_00, type: u4}
      - {id: info, type: anim_info}
      - {id: ofs_list_entry1, type: u4}
      - {id: unk_hash, type: u4} # not in mfx
      - {id: ofs_entry2, type: block_offset, repeat: expr, repeat-expr: info.num_entry2}
      - {id: set_buff_hash, type: u4, repeat: expr, repeat-expr: info.num_entry1}

  block_offset:
    seq:
      - {id: ofc_block, type: u4}
    instances:
      body:
        pos: _parent._parent._parent.ofs_base + ofc_block
        type: anim_sub_entry
      #test_ofs:
      #  value: _parent._parent._parent.ofs_base + ofc_block

  anim_info:
    seq:
      - {id: unk, type: b2}
      - {id: num_entry2, type: b16}
      - {id: num_entry1, type: b14}

  anim_data_info:
    seq:
      - {id: type, type: b4}
      - {id: unk_00, type: b4}
      - {id: num_entry, type: b24}

  shader_object:
    seq:
      - {id: index, type: b12}
      - {id: name_hash, type: b20, enum: shader_object_hash}

  cmd_ofs_buffer:
    seq:
      - {id: ofs_float_buff, type: u4}

  cmd_tex_idx:
    seq:
      - {id: tex_idx, type: u4}
  anim_sub_entry:
    seq:
      - {id: shader_hash, type: u4}
      - {id: info, type: anim_data_info}
      - id: entry
        type: 
          switch-on: info.type
          cases:
            0: anim_sub_entry0
            1: anim_sub_entry1
            2: anim_sub_entry2
            3: anim_sub_entry3
            4: anim_sub_entry4
            5: anim_sub_entry5
            6: anim_sub_entry6
            7: anim_sub_entry7

  anim_sub_entry0:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 4}
     - {id: values, type: anim_type0, repeat: expr, repeat-expr: _parent.info.num_entry}

  anim_type0:
    seq:
      - {id: unk_00, type: u4}
      - {id: unk_01, type: f4}

  anim_sub_entry1:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 4}
     - {id: values, type: anim_type1, repeat: expr, repeat-expr: _parent.info.num_entry}

  anim_type1:
    seq:
      - {id: unk_00, type: u4}
      - {id: unk_01, type: f4, repeat: expr, repeat-expr: 4}

  anim_sub_entry2: # unused
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 12}
     - {id: values, type: u1, repeat: expr, repeat-expr: 8 * _parent.info.num_entry}

  anim_sub_entry3: # unused
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 24}
     - {id: values, type: u1, repeat: expr, repeat-expr: 16 * (_parent.info.num_entry -1)}

  anim_sub_entry4:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 4}
     - {id: values, type: anim_type4, repeat: expr, repeat-expr: _parent.info.num_entry}
     - {id: hash, type: u4, repeat: expr, repeat-expr: _parent.info.num_entry}

  anim_type4:
    seq:
      - {id: unk_00, type: u4}
      - {id: unk_01, type: f4, repeat: expr, repeat-expr: 19}

  anim_sub_entry5: # unused
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 12}
     - {id: values, type: u1, repeat: expr, repeat-expr: 8 * _parent.info.num_entry}

  anim_sub_entry6:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 4}
     - {id: values, type: anim_type6, repeat: expr, repeat-expr: _parent.info.num_entry }

  anim_type6:
    seq:
      - {id: unk_00, type: u4, repeat: expr, repeat-expr: 2}
      - {id: unk_01, type: f4, repeat: expr, repeat-expr: 4}

  anim_sub_entry7: # unused
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 36}
     - {id: values, type: u1, repeat: expr, repeat-expr: 24 * (_parent.info.num_entry -1)}


  tex_offset:
    seq:
      - {id: texture_id, type: u4}

  shd_hash:
    seq:
      - {id: shader_hash, type: u4}

  ofs_buff:
    seq:
      - {id: ofs_const_buff, type: u4}

  cb_material:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"re0"': cb_material_1
              '"re1"': cb_material_1
              '"rev1"': cb_material_1
              '"rev2"': cb_material_1
              '"dd"': cb_material_1
              _ : cb_material_1

  cb_globals:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"re0"': cb_globals_1
              '"re1"': cb_globals_1
              '"re6"': cb_globals_3
              '"rev1"': cb_globals_1
              '"rev2"': cb_globals_2
              '"dd"': cb_globals_4
              _ : cb_globals_1

  cb_color_mask:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"re6"': cb_color_mask_1
              '"rev2"': cb_color_mask_1
              _ : cb_color_mask_1

  cb_vertex_displacement:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"re0"': cb_vertex_displacement_1
              '"re1"': cb_vertex_displacement_1
              '"re6"': cb_vertex_displacement_1
              '"rev1"': cb_vertex_displacement_1
              '"rev2"': cb_vertex_displacement_1
              '"dd"': cb_vertex_displacement_1
              _ : cb_vertex_displacement_1


  cb_vertex_displacement2:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"re0"': cb_vertex_displacement2_1
              '"re1"': cb_vertex_displacement2_1
              '"re6"': cb_vertex_displacement2_1
              '"rev1"': cb_vertex_displacement2_1
              '"rev2"': cb_vertex_displacement2_1
              '"dd"': cb_vertex_displacement2_1
              _ : cb_vertex_displacement2_1
  
  cb_burn_common:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_burn_common_1
              _ :  cb_burn_common_1

  cb_burn_emission:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_burn_emission_1
              _ : cb_burn_emission_1
  
  cb_app_clip_plane:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_app_clip_plane_1
              _ : cb_app_clip_plane_1
 
  cb_specular_blend:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_specular_blend_1
              _ : cb_specular_blend_1
 
  cb_app_reflect:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_app_reflect_1
              _ : cb_app_reflect_1
  
  cb_app_reflect_shadow_light:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_app_reflect_shadow_light_1
              _ : cb_app_reflect_shadow_light_1
 
  cb_outline_ex:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_outline_ex_1
              _ : cb_outline_ex_1
  
  cb_dd_material_param:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_dd_material_param_1
              _ : cb_dd_material_param_1
  
  cb_uv_rotation_offset:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_uv_rotation_offset_1
              _ : cb_uv_rotation_offset_1

  cb_dd_material_param_inner_correct:
      instances:
        app_specific:
          pos: _parent._parent.ofs_cmd + _parent.value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
          type:
            switch-on: "_root.app_id"
            cases:
              '"dd"': cb_dd_material_param_inner_correct_1
              _ : cb_dd_material_param_inner_correct_1
  
  cb_globals_1:
    instances:
      size_:
        value: 288
    seq:
      - {id: f_alpha_clip_threshold, type: f4} # 0
      - {id: f_albedo_color, type: f4, repeat: expr, repeat-expr: 3} #1
      - {id: f_albedo_blend_color, type: f4, repeat: expr, repeat-expr: 4} #4
      - {id: f_detail_normal_power, type: f4} #8
      - {id: f_detail_normal_uv_scale, type: f4} #9
      - {id: f_detail_normal2_power, type: f4} #10
      - {id: f_detail_normal2_uv_scale, type: f4} #11
      - {id: f_primary_shift, type: f4} #12
      - {id: f_secondary_shift, type: f4} #13
      - {id: f_parallax_factor, type: f4} #14
      - {id: f_parallax_self_occlusion, type: f4} #15
      - {id: f_parallax_min_sample, type: f4} #16
      - {id: f_parallax_max_sample, type: f4, repeat: expr, repeat-expr: 3} #17
      - {id: f_light_map_color, type: f4, repeat: expr, repeat-expr: 4} #20
      - {id: f_thin_map_color, type: f4, repeat: expr, repeat-expr: 3} #24
      - {id: f_thin_scattering, type: f4} #27
      - {id: f_screen_uv_scale, type: f4, repeat: expr, repeat-expr: 2} #28
      - {id: f_screen_uv_offset, type: f4, repeat: expr, repeat-expr: 2} #30
      - {id: f_indirect_offset, type: f4, repeat: expr, repeat-expr: 2} #32
      - {id: f_indirect_scale, type: f4, repeat: expr, repeat-expr: 2} #34
      - {id: f_fresnel_schlick, type: f4} #36
      - {id: f_fresnel_schlick_rgb, type: f4, repeat: expr, repeat-expr: 3} #37
      - {id: f_specular_color, type: f4, repeat: expr, repeat-expr: 3} #40
      - {id: f_shininess, type: f4} #43
      - {id: f_emission_color, type: f4, repeat: expr, repeat-expr: 3} #44
      - {id: f_emission_threshold, type: f4} #47
      - {id: f_constant_color, type: f4, repeat: expr, repeat-expr: 4} #48
      - {id: f_roughness, type: f4} #52
      - {id: f_roughness_rgb, type: f4, repeat: expr, repeat-expr: 3} #53
      - {id: f_anisotoropic_direction, type: f4, repeat: expr, repeat-expr: 3} #56
      - {id: f_smoothness, type: f4} #59
      - {id: f_anistropic_uv, type: f4,repeat: expr, repeat-expr: 2} #60
      - {id: f_primary_expo, type: f4} #62
      - {id: f_secondary_expo, type: f4} #63
      - {id: f_primary_color, type: f4, repeat: expr, repeat-expr: 4} #64
      - {id: f_secondary_color, type: f4, repeat: expr, repeat-expr: 4} #68

  cb_globals_2:
    instances:
      size_:
        value: 480
    seq:
      - {id: f_alpha_clip_threshold, type: f4} # 0
      - {id: f_albedo_color, type: f4, repeat: expr, repeat-expr: 3} #1
      - {id: f_albedo_blend_color, type: f4, repeat: expr, repeat-expr: 4} #4
      - {id: f_detail_normal_power, type: f4} #8
      - {id: f_detail_normal_uv_scale, type: f4} #9
      - {id: f_detail_normal2_power, type: f4} #10
      - {id: f_detail_normal2_uv_scale, type: f4} #11
      - {id: f_primary_shift, type: f4} #12
      - {id: f_secondary_shift, type: f4} #13
      - {id: f_parallax_factor, type: f4} #14
      - {id: f_parallax_self_occlusion, type: f4} #15
      - {id: f_parallax_min_sample, type: f4} #16
      - {id: f_parallax_max_sample, type: f4, repeat: expr, repeat-expr: 3} #17
      - {id: f_light_map_color, type: f4, repeat: expr, repeat-expr: 4} #20
      - {id: f_thin_map_color, type: f4, repeat: expr, repeat-expr: 3} #24
      - {id: f_thin_scattering, type: f4} #27
      - {id: f_screen_uv_scale, type: f4, repeat: expr, repeat-expr: 2} #28
      - {id: f_screen_uv_offset, type: f4, repeat: expr, repeat-expr: 2} #30
      - {id: f_indirect_offset, type: f4, repeat: expr, repeat-expr: 2} #32
      - {id: f_indirect_scale, type: f4, repeat: expr, repeat-expr: 2} #34
      - {id: f_fresnel_schlick, type: f4} #36
      - {id: f_fresnel_schlick_rgb, type: f4, repeat: expr, repeat-expr: 3} #37
      - {id: f_specular_color, type: f4, repeat: expr, repeat-expr: 3} #40
      - {id: f_shininess, type: f4} #43
      - {id: f_emission_color, type: f4, repeat: expr, repeat-expr: 3} #44
      - {id: f_emission_threshold, type: f4} #47
      - {id: f_constant_color, type: f4, repeat: expr, repeat-expr: 4} #48
      - {id: f_roughness, type: f4} #52
      - {id: f_roughness_rgb, type: f4, repeat: expr, repeat-expr: 3} #53
      - {id: f_anisotoropic_direction, type: f4, repeat: expr, repeat-expr: 3} #56
      - {id: f_smoothness, type: f4} #59
      - {id: f_anistropic_uv, type: f4,repeat: expr, repeat-expr: 2} #60
      - {id: f_primary_expo, type: f4} #62
      - {id: f_secondary_expo, type: f4} #63
      - {id: f_primary_color, type: f4, repeat: expr, repeat-expr: 4} #64
      - {id: f_secondary_color, type: f4, repeat: expr, repeat-expr: 4} #68
      - {id: f_albedo_color2, type: f4, repeat: expr, repeat-expr: 4} #72
      - {id: f_specular_color2, type: f4, repeat: expr, repeat-expr: 3} #76
      - {id: f_fresnel_schlick2, type: f4} #79
      - {id: f_shininess2, type: f4, repeat: expr, repeat-expr: 4} #80
      - {id: f_transparency_clip_threshold, type: f4, repeat: expr, repeat-expr: 4} #84
      - {id: f_blend_uv, type: f4} #88
      - {id: f_normal_power, type: f4, repeat: expr, repeat-expr: 3} #89
      - {id: f_albedo_blend2_color, type: f4, repeat: expr, repeat-expr: 4} #92
      - {id: f_detail_normal_u_v_scale, type: f4, repeat: expr, repeat-expr: 2} #96
      - {id: f_fresnel_legacy, type: f4, repeat: expr, repeat-expr: 2} #98
      - {id: f_normal_mask_pow0, type: f4, repeat: expr, repeat-expr: 4} #100
      - {id: f_normal_mask_pow1, type: f4, repeat: expr, repeat-expr: 4} #104
      - {id: f_normal_mask_pow2, type: f4, repeat: expr, repeat-expr: 4} #108
      - {id: f_texture_blend_rate, type: f4, repeat: expr, repeat-expr: 4} #112
      - {id: f_texture_blend_color, type: f4, repeat: expr, repeat-expr: 4} #116

  cb_globals_3:
    instances:
      size_:
        value: 336
        # value: 328
    seq:
      - {id: f_albedo_color, type: f4, repeat: expr, repeat-expr: 3} # 0
      - {id: padding_1, type: f4}
      - {id: f_albedo_blend_color, type: f4, repeat: expr, repeat-expr: 4} # 4
      - {id: f_detail_normal_power, type: f4} #8
      - {id: f_detail_normal_uv_scale, type: f4} #9
      - {id: f_detail_normal2_power, type: f4} #10
      - {id: f_detail_normal2_uv_scale, type: f4} #11
      - {id: f_primary_shift, type: f4} #12
      - {id: f_secondary_shift, type: f4} #13
      - {id: f_parallax_factor, type: f4} #14
      - {id: f_parallax_self_occlusion, type: f4} #15
      - {id: f_parallax_min_sample, type: f4} #16
      - {id: f_parallax_max_sample, type: f4} #17
      - {id: padding_2, type: f4, repeat: expr, repeat-expr: 2} # 18
      - {id: f_light_map_color, type: f4, repeat: expr, repeat-expr: 3} #20
      - {id: padding_3, type: f4}  # 23
      - {id: f_thin_map_color, type: f4, repeat: expr, repeat-expr: 3} #24
      - {id: f_thin_scattering, type: f4} #27
      - {id: f_indirect_offset, type: f4, repeat: expr, repeat-expr: 2} #28
      - {id: f_indirect_scale, type: f4, repeat: expr, repeat-expr: 2} # 30
      - {id: f_fresnel_schlick, type: f4} # 32
      - {id: f_fresnel_schlick_rgb, type: f4, repeat: expr, repeat-expr: 3} # 33
      - {id: f_specular_color, type: f4, repeat: expr, repeat-expr: 3} # 36
      - {id: f_shininess, type: f4} # 39
      - {id: f_emission_color, type: f4, repeat: expr, repeat-expr: 3} # 40
      - {id: f_alpha_clip_threshold, type: f4}  # 43
      - {id: f_primary_expo, type: f4} # 44
      - {id: f_secondary_expo, type: f4} # 45
      - {id: padding_4, type: f4, repeat: expr, repeat-expr: 2}  # 46
      - {id: f_primary_color, type: f4, repeat: expr, repeat-expr: 3} #  48
      - {id: padding_5, type: f4}  # 51
      - {id: f_secondary_color, type: f4, repeat: expr, repeat-expr: 3} # 52
      - {id: padding_6, type: f4}  # 55
      - {id: f_albedo_color_2, type: f4, repeat: expr, repeat-expr: 3} # 56
      - {id: padding_7, type: f4}  # 59
      - {id: f_specular_color_2, type: f4, repeat: expr, repeat-expr: 3}  # 60
      - {id: f_fresnel_schlick_2, type: f4}  # 63
      - {id: f_shininess_2, type: f4} # 64
      - {id: padding_8, type: f4, repeat: expr, repeat-expr: 3}  # 65
      - {id: f_transparency_clip_threshold, type: f4, repeat: expr, repeat-expr: 4} # 68
      - {id: f_blend_uv, type: f4} # 72
      - {id: padding_9, type: f4, repeat: expr, repeat-expr: 3}  # 73
      - {id: f_albedo_blend2_color, type: f4, repeat: expr, repeat-expr: 4}  # 76
      - {id: f_detail_normalu_vscale, type: f4, repeat: expr, repeat-expr: 2}  # 80
      - {id: padding_10, type: f4, repeat: expr, repeat-expr: 2}  # 82

  cb_globals_4:
    instances:
      size_:
        value: 320
    seq:
      - {id: f_albedo_color, type: f4, repeat: expr, repeat-expr: 3} #0 3
      - {id: padding_1, type: f4}
      - {id: f_albedo_blend_color, type: f4, repeat: expr, repeat-expr: 4} #4
      - {id: f_detail_normal_power, type: f4} #8
      - {id: f_detail_normal_uv_scale, type: f4} #9
      - {id: f_detail_normal2_power, type: f4} #10
      - {id: f_detail_normal2_uv_scale, type: f4} #11
      - {id: f_primary_shift, type: f4} #12
      - {id: f_secondary_shift, type: f4} #13
      - {id: f_parallax_factor, type: f4} #14
      - {id: f_parallax_self_occlusion, type: f4} #15
      - {id: f_parallax_min_sample, type: f4} #16
      - {id: f_parallax_max_sample, type: f4} #17
      - {id: padding_2, type: f4, repeat: expr, repeat-expr: 2}
      - {id: f_light_map_color, type: f4, repeat: expr, repeat-expr: 3} #20
      - {id: padding_3, type: f4}
      - {id: f_thin_map_color, type: f4, repeat: expr, repeat-expr: 3} #24
      - {id: f_thin_scattering, type: f4} #27
      - {id: f_indirect_offset, type: f4, repeat: expr, repeat-expr: 2} #28
      - {id: f_indirect_scale, type: f4, repeat: expr, repeat-expr: 2} #30
      - {id: f_fresnel_schlick, type: f4} #32
      - {id: f_fresnel_schlick_rgb, type: f4, repeat: expr, repeat-expr: 3} #33
      - {id: f_specular_color, type: f4, repeat: expr, repeat-expr: 3} #36
      - {id: f_shininess, type: f4} #39
      - {id: f_emission_color, type: f4, repeat: expr, repeat-expr: 3} #40
      - {id: f_alpha_clip_threshold, type: f4} # 43
      - {id: f_roughness, type: f4} #44
      - {id: f_roughness_rgb, type: f4, repeat: expr, repeat-expr: 3} #45
      - {id: f_anisotoropic_direction, type: f4, repeat: expr, repeat-expr: 3} #48
      - {id: f_smoothness, type: f4} #51
      - {id: f_anistropic_uv, type: f4,repeat: expr, repeat-expr: 2} #52
      - {id: f_primary_expo, type: f4} #54
      - {id: f_secondary_expo, type: f4} #55
      - {id: f_primary_color, type: f4, repeat: expr, repeat-expr: 3} #56
      - {id: padding_4, type: f4}
      - {id: f_secondary_color, type: f4, repeat: expr, repeat-expr: 3} #60
      - {id: padding_5, type: f4}
      - {id: xyzw_sepalate, type: f4, repeat: expr, repeat-expr: 16} # 64
  
  cb_material_1: #all games 32 floats
    instances:
      size_:
        value: 128
    seq:
      - {id: f_diffuse_color, type: f4, repeat: expr, repeat-expr: 3}
      - {id: f_transparency, type: f4}
      - {id: f_reflective_color, type: f4, repeat: expr, repeat-expr: 3}
      - {id: f_transparency_volume, type: f4}
      - {id: f_uv_transform, type: f4, repeat: expr, repeat-expr: 8}
      - {id: f_uv_transform2, type: f4, repeat: expr, repeat-expr: 8}
      - {id: f_uv_transform3, type: f4, repeat: expr, repeat-expr: 8}

  cb_color_mask_1: # 24 floats
    instances:
      size_:
        value: 96
    seq:
      - {id: f_color_mask_threshold, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask_offset, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_clip_threshold, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask_color, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask2_threshold, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask2_color, type: f4, repeat: expr, repeat-expr: 4}

  cb_vertex_displacement_1: # CBVertexDisplacement 0x15419236 rev2 8 floats
    instances:
      size_:
        value: 32
    seq:
      - {id: f_vtx_disp_start, type: f4}
      - {id: f_vtx_disp_scale, type: f4}
      - {id: f_vtx_disp_inv_area, type: f4}
      - {id: f_vtx_disp_rcn, type: f4}
      - {id: f_vtx_disp_tilt_u, type: f4}
      - {id: f_vtx_disp_tilt_v, type: f4}
      - {id: filler, type: f4, repeat: expr, repeat-expr: 2}

  cb_vertex_displacement2_1: # CBVertexDisplacement2 0x51814237 rev2 4 floats
    instances:
      size_:
        value: 16
    seq:
      - {id: f_vtx_disp_start2, type: f4}
      - {id: f_vtx_disp_scale2, type: f4}
      - {id: f_vtx_disp_inv_area2, type: f4}
      - {id: f_vtx_disp_rcn2, type: f4}

  cb_burn_common_1:  # 768
    instances:
      size_:
        value: 48
    seq:
    - {id: f_b_blend_map_color, type: f4, repeat: expr, repeat-expr: 3}  # 0
    - {id: f_b_alpha_clip_threshold, type: f4}  # 3
    - {id: f_b_blend_alpha_threshold, type: f4}  # 4
    - {id: f_b_blend_alpha_band, type: f4}  # 5
    - {id: f_b_specular_blend_rate, type: f4}  # 6
    - {id: f_b_albedo_blend_rate, type: f4}  # 7
    - {id: f_b_albedo_blend_rate2, type: f4}  # 8
    - {id: padding, type: f4, repeat: expr, repeat-expr: 3}

  cb_burn_emission_1:  # 769
    instances:
      size_:
        value: 32
    seq:
    - {id: f_b_emission_factor, type: f4}  # 0
    - {id: f_b_emission_alpha_band, type: f4}  # 1
    - {id: padding_1, type: f4, repeat: expr, repeat-expr: 2}
    - {id: f_burn_emission_color, type: f4, repeat: expr, repeat-expr: 3}  # 4
    - {id: padding_2, type: f4}
  
  cb_app_clip_plane_1: # 770
    instances:
      size_:
        value: 48
    seq:
      - {id: f_plane_normal, type: f4, repeat: expr, repeat-expr: 3}  # 0
      - {id: padding_1, type: f4}
      - {id: f_plane_point, type: f4, repeat: expr, repeat-expr: 3}  # 4
      - {id: padding_2, type: f4}
      - {id: f_app_clip_mask, type: f4}  # 8
      - {id: padding_3, type: f4}
      
  cb_specular_blend_1:  # 772
    instances:
      size_:
        value: 16
    seq:
    - {id: f_specular_blend_color, type: f4, repeat: expr, repeat-expr: 4}

  cb_app_reflect_1:  # 773
    instances:
      size_:
        value: 16
    seq:
    - {id: f_app_water_reflect_scale, type: f4}  # 0
    - {id: f_app_shadow_light_scale, type: f4}  # 1
    - {id: padding, type: f4, repeat: expr, repeat-expr: 2}

  cb_app_reflect_shadow_light_1:  # 774
    instances:
      size_:
        value: 16
    seq:
    - {id: f_app_reflect_shadow_dir, type: f4, repeat: expr, repeat-expr: 3}  # 0
    - {id: padding, type: f4}

  cb_outline_ex_1:  # 775
    instances:
      size_:
        value: 64
    seq:
      - {id: f_outline_outer_color, type: f4, repeat: expr, repeat-expr: 4}  # 0
      - {id: f_outline_inner_color, type: f4, repeat: expr, repeat-expr: 4}  # 4
      - {id: f_outline_balance_offset, type: f4}  # 8
      - {id: f_outline_balance_scale, type: f4}  # 9
      - {id: f_outline_balance, type: f4}  # 10
      - {id: padding, type: f4}
      - {id: f_outline_blend_mask, type: f4, repeat: expr, repeat-expr: 4}  # 12

  cb_dd_material_param_1:  # 779
    instances:
      size_:
        value: 160
    seq:
      - {id: f_dd_material_blend_color, type: f4, repeat: expr, repeat-expr: 4}  # 0
      - {id: f_dd_material_color_blend_rate, type: f4, repeat: expr, repeat-expr: 2}  # 4
      - {id: f_dd_material_area_mask, type: f4, repeat: expr, repeat-expr: 2}  # 6
      - {id: f_dd_material_border_blend_mask, type: f4, repeat: expr, repeat-expr: 4}  # 8
      - {id: f_dd_material_border_shade_band, type: f4}  # 12
      - {id: f_dd_material_base_power, type: f4}  # 13
      - {id: f_dd_material_normal_blend_rate, type: f4}  # 14
      - {id: f_dd_material_reflect_blend_color, type: f4}  #15
      - {id: f_dd_material_specular_factor, type: f4}  #16
      - {id: f_dd_material_specular_map_factor, type: f4}  #17
      - {id: f_dd_material_env_map_blend_color, type: f4}  # 18
      - {id: f_dd_material_area_alpha, type: f4}  # 19
      - {id: f_dd_material_area_pos, type: f4, repeat: expr, repeat-expr: 4}  # 20
      - {id: f_dd_material_albedo_uv_scale, type: f4}  # 24
      - {id: f_dd_material_normal_uv_scale, type: f4}  #25
      - {id: f_dd_material_normal_power, type: f4}  # 26
      - {id: f_dd_material_base_env_map_power, type: f4}  # 27
      - {id: f_dd_material_lantern_color, type: f4, repeat: expr, repeat-expr: 3}  # 28
      - {id: padding_1, type: f4}
      - {id: f_dd_material_lantern_pos, type: f4, repeat: expr, repeat-expr: 3}  # 32
      - {id: padding_2, type: f4}
      - {id: f_dd_material_lantern_param, type: f4, repeat: expr, repeat-expr: 3}  # 36
      - {id: padding_3, type: f4}

  cb_uv_rotation_offset_1:  # 777
    instances:
      size_:
        value: 32
    seq:
    - {id: f_uv_rotation_center, type: f4, repeat: expr, repeat-expr: 2}  # 0
    - {id: f_uv_rotation_angle, type: f4}  # 2
    - {id: padding, type: f4}
    - {id: f_uv_rotation_offset, type: f4, repeat: expr, repeat-expr: 2}  # 4
    - {id: f_uv_rotation_scale, type: f4, repeat: expr, repeat-expr: 2}  # 6

  cb_dd_material_param_inner_correct_1:  #782
    instances:
      size_:
        value: 16
    seq:
    - {id: f_dd_material_inner_correct_offset, type: f4}  # 0
    - {id: padding, type: f4, repeat: expr, repeat-expr: 3}

  cb_distortion: #CBDistortion 0xefca3227 4 floats
    seq:
      - {id: f_distortion_factor, type: f4}
      - {id: f_distortion_blend, type: f4}
      - {id: filler, type: f4, repeat: expr, repeat-expr: 2}
enums:
  material_type:
    0x854d484: type_n_draw__material_null
    0x5fb0ebe4: type_n_draw__material_std
    0x7d2b31b3: type_n_draw__material_std_est
    0x1cab245e: type_n_draw__dd_material_std
    0x26d9ba5c: type_n_draw__dd_material_inner
    0x30dba54f: type_n_draw__dd_material_water

  texture_type:
    0x241f5deb: type_r_texture
    0x7808ea10: type_r_render_target_texture

  cmd_type:
    0: set_flag
    1: set_constant_buffer
    2: set_sampler_state # guess
    3: set_texture
    4: set_unk
  shader_object_hash:
    0xabee5: iasystemcopy
    0x7fa75: iasystemclear
    0x7abfa: iadevelopprim2d
    0xc9abb: iadevelopprim3d
    0xfc7fe: iacollisioninput
    0x97c15: iafilter
    0x30d3b: iafilter0
    0x43dad: iafilter1
    0xd6c17: iafilter2
    0x1a6a1: iaswing
    0x73358: iaswing2
    0xf367f: iaswinghighprecision
    0x2001e: iaswing2highprecision
    0x7698a: iainstancing
    0x8771a: iainstancingcolor
    0x7ebd8: ialatticedeform
    0x6942: iatetradeform
    0x3a155: iatetradeform2
    0xb0983: iaskinbridge1wt
    0xdb7da: iaskinbridge2wt
    0xcb68: iaskinbridge4wt
    0xa320c: iaskinbridge8wt
    0x5d5ad: iaskinbridge4wt4m
    0xa8fab: iaskintb1wt
    0x667b1: iaskintbn1wt
    0xcbf6c: iaskintbc1wt
    0xd8778: iaskintbnla1wt
    0xc31f2: iaskintb2wt
    0xd9e8: iaskintbn2wt
    0xa0135: iaskintbc2wt
    0xb3921: iaskintbnla2wt
    0x14d40: iaskintb4wt
    0xda55a: iaskintbn4wt
    0x77d87: iaskintbc4wt
    0x64593: iaskintbnla4wt
    0xbb424: iaskintb8wt
    0x75c3e: iaskintbn8wt
    0xd84e3: iaskintbc8wt
    0xcbcf7: iaskintbnla8wt
    0xd8297: ianonskintb
    0x49b4f: ianonskintbc
    0xb86de: ianonskintbl
    0xd4504: ianonskintbl_la
    0x5e7f2: ianonskintbn
    0xafa63: ianonskintba
    0x926fd: ianonskintbnc
    0x63b6c: ianonskintbnl
    0x5402f: ianonskintbnl_la
    0x747d1: ianonskintbna
    0x12553: ianonskintbla
    0x9399c: ianonskintbca
    0xb6681: ianonskintbnca
    0x37a4e: ianonskintbnla
    0xa7d7d: ianonskinb
    0x207d6: ianonskinbc
    0xd1a47: ianonskinbl
    0x8a618: ianonskinbl_la
    0xc66fa: ianonskinba
    0x2082f: ianonskinbla
    0xa14e0: ianonskinbca
    0x2f55c: iaskinotb_4wt_4m
    0x4325a: ianonskintbn_4m
    0xefc14: iaskinvelocytyedge
    0xb4229: iadualparaboloid
    0xa0978: ia_deferredlighting_lightvolume
    0x64435: iaprimitivecloudbillboard
    0xed029: iaprimitivecloud
    0xccc74: iaprimitivesprite
    0x28185: iaprimitivent
    0x55ce2: iaprimitivepolyline
    0x814ba: iaprimitivepolygon
    0x50217: iacubemapfilter
    0x7d107: iagsdoffilter
    0x377d7: iabokeh
    0x40521: iawater
    0xc463c: iawaterripple
    0xfc6e2: iagui
    0xfa335: iatextureblend
    0x77562: iagpuparticle
    0x833a2: iagpulineparticle
    0x14093: iagpupolylineparticle
    0x1af65: ialightshaftinput
    0xa8e08: iagrass
    0xa6451: iagrasshicomp
    0xe8a86: iagrasshicomp2
    0x4bb95: iagrasspoint
    0xb6d3f: iagrasslowest
    0xc8705: iagrassspu
    0x11035: iagrassoutsourcing
    0x1533b: iagrassoutsourcingf32
    0x2aa4: iamirage
    0xabe96: iasimwaterforviewinput
    0xcc1fe: iasoftbodyquad
    0x79a5e: iasoftbodyvertex
    0xcff47: iasoftbodydecouple
    0x4d186: iasoftbodyvertexnovtf
    0xd4e3: iasoftbodyvertexps3
    0x81fcf: iasoftbodydecouplenovtf
    0x96284: iatattooblend2d
    0x6d5d5: iabuilder
    0xce69f: iasky
    0x9821b: iaastralbody
    0x13845: iaskystar
    0x507e4: iaambientshadow
    0x78320: iavertexindexf32
    0xc25bb: iavertexindexf16
    0x6e59d: iatrianglef32
    0xd4306: iatrianglef16
    0x710f8: iainfparticle
    0xc07ae: ia_system_copy
    0xc841c: ia_system_clear
    0xe65d9: system_output
    0xdbabe: system_depthout
    0x670a3: system_mrt2
    0x14035: system_mrt3
    0x5d596: system_mrt4
    0x706b8: procedural_texture_out
    0xdb25c: ia_develop_prim2d
    0x6831d: ia_develop_prim3d
    0x8a5f0: develop_output
    0xa1598: ia_collision_vs_input
    0xbc628: collision_out
    0xcfca6: material_context
    0x33c18: ia_filter
    0x3bc6: ia_filter0
    0x70b50: ia_filter1
    0xe5aea: ia_filter2
    0xca1b5: filter_out
    0x872f1: filter_input
    0x2d292: filter_output_16
    0x7b5d7: fog_out
    0x15dc1: skinning_input
    0x6065: light_param
    0xf4f94: light_output
    0x5c34f: deferred_lighting_result
    0x41e6d: material_input
    0x55aa6: morph_input
    0x25636: softbody_input
    0x8f876: lattice_deform_input
    0xfb2b: swing_input
    0x97ade: instancing_input
    0x6d2ba: projection_input
    0x31d65: material_output
    0x580d5: material_hs_input
    0xae745: material_hs_output
    0xb7ef8: material_output_ex
    0xbbf48: ia_swing
    0x3539d: ia_swing2
    0xcb731: ia_swing_high_precision
    0xba420: ia_swing2_high_precision
    0x530ae: swing_info
    0xf5f8: ia_instancing
    0x5faf2: ia_instancing_color
    0x95853: ia_lattice_deform
    0x9f45c: ia_tetra_deform
    0x9b5ab: ia_tetra_deform2
    0xe9811: world_coordinate_input
    0x8d8cf: ia_skin_bridge_1wt
    0xe6696: ia_skin_bridge_2wt
    0x31a24: ia_skin_bridge_4wt
    0x9e340: ia_skin_bridge_8wt
    0x8717a: ia_skin_bridge_4wt_4m
    0x53790: ia_skin_tb_1wt
    0xe29cd: ia_skin_tbn_1wt
    0xeed7c: ia_skin_tbc_1wt
    0x2a3a1: ia_skin_tbnla_1wt
    0x389c9: ia_skin_tb_2wt
    0x89794: ia_skin_tbn_2wt
    0x85325: ia_skin_tbc_2wt
    0x41df8: ia_skin_tbnla_2wt
    0xef57b: ia_skin_tb_4wt
    0x5eb26: ia_skin_tbn_4wt
    0x52f97: ia_skin_tbc_4wt
    0x9614a: ia_skin_tbnla_4wt
    0x40c1f: ia_skin_tb_8wt
    0xf1242: ia_skin_tbn_8wt
    0xfd6f3: ia_skin_tbc_8wt
    0x3982e: ia_skin_tbnla_8wt
    0x3168b: ia_nonskin_tb
    0x7994: ia_nonskin_tbc
    0xf6405: ia_nonskin_tbl
    0xe28ce: ia_nonskin_tbl_la
    0x10529: ia_nonskin_tbn
    0xe18b8: ia_nonskin_tba
    0x3d4d2: ia_nonskin_tbnl
    0xe98ec: ia_nonskin_tbnl_la
    0xcc943: ia_nonskin_tbnc
    0x2a86f: ia_nonskin_tbna
    0x4caed: ia_nonskin_tbla
    0xcd622: ia_nonskin_tbca
    0x3ede5: ia_nonskin_tbnca
    0xbf12a: ia_nonskin_tbnla
    0x6cb0: ia_nonskin_b
    0xc93ca: ia_nonskin_bc
    0x38e5b: ia_nonskin_bl
    0x2d7c: ia_nonskin_bl_la
    0x2f2e6: ia_nonskin_ba
    0x6eaf4: ia_nonskin_bla
    0xef63b: ia_nonskin_bca
    0xab495: ia_skin_otb_4wt_4m
    0x75f90: ia_nonskin_tbn_4m
    0x44a51: material_velocity_output
    0x7760: ia_skin_velocity_edge
    0xaf772: outline_detector
    0xa4d9b: material_outline_output
    0x74524: shadowreceiveparam
    0x82e10: shadowreceivecontext
    0xfe3ab: shadowreceive_output
    0x9f0e6: shadowreceive_deferred_output
    0xd5abd: ia_dual_paraboloid
    0x258e3: dual_paraboloid_output
    0xdaa39: deferred_lighting_geometry_parameter
    0xcff23: diferred_lighting_mrt
    0xe90ec: deferred_lighting_gbuffer_pass_vs_output
    0x1adf9: ia_deferred_lighting_light_volume
    0x6a816: deferred_lighting_light_volume_vs_output
    0xc99bf: deferred_lighting_light_volume_mrt_ps_output
    0x3913b: rsm_param
    0xa8096: rsm_output
    0xbf40b: adhesion_input
    0x1c6e2: adhesion_output
    0x64692: adhesion_output_pv
    0x60350: hs_pn_constant
    0x87317: hs_ph_constant
    0x32a51: material_ph_output
    0xe0f1a: hs_dm_constant
    0x65d64: shadowcast_input
    0x39782: shadowcast_output
    0xbc7fb: ia_primitive_cloud_billboard
    0x21249: ia_primitive_cloud
    0x3a126: ia_primitive_sprite
    0x8d153: ia_primitive_nt
    0x10c04: ia_primitive_polyline
    0x5bbc7: ia_primitive_polygon
    0x6b8f1: primitive_vs_input
    0xbf0ac: primitive_vs_output
    0x79be8: primitive_hs_input
    0x796b4: primitive_hs_const_data
    0x8a335: primitive_hs_control_point
    0xd9a5b: primitive_ds_output
    0x6ab70: primitive_dc_output
    0xba85c: radial_blur_output
    0xfc9bb: tvnoise_filter_output
    0x62b51: variance_filter_output
    0x2a944: cubemap_variance_filter_output
    0x553c3: bloom_filter_output
    0xd800d: image_plane_filter_out
    0x5add1: ia_cubemap_filter
    0x3d8db: cubemap_filter_output
    0x9c9cc: ia_gsdoffilter
    0x1dfcd: vs_dof_input
    0xc7e5e: gs_dof_input
    0xc7a2d: ps_dof_input
    0x7c413: gs_dof_output
    0xae49d: ssao_output
    0xa4beb: ssao_normal_out
    0x96e3e: ia_bokeh
    0x76b67: tangent_filter_out
    0x3bb7f: prim_fog_out
    0x41304: prim_eye_out
    0xd8830: prim_ntb_out
    0xe1cc8: ia_water
    0xf8a54: ia_water_vcolor
    0x61b3a: ia_water_ripple
    0xf3318: water_output
    0xf552: water_ripple_output
    0x874fd: water_position_output
    0xea095: ia_gui
    0x2dc14: vs_out_gui
    0x940df: ia_texture_blend
    0x31675: texture_blend_output
    0xff8fd: ia_gpu_particle
    0x730a6: ia_gpu_line_particle
    0x78491: ia_gpu_polyline_particle
    0x621ba: gpu_particle_vs_input
    0x9283d: gpu_particle_ps_input
    0x229bf: ia_lightshaft_input
    0x94b18: lightshaft_output
    0x97e1: ia_grass
    0xcdae: ia_grass_hicomp
    0x5bfa2: ia_grass_hicomp2
    0x1c4c0: ia_grass_lowest
    0xb3523: ia_grass_point
    0x1b919: grass_input
    0x40de7: grass_output
    0x66dfd: grass_shadowreceive_output
    0xcbc3: dynamicedit_input
    0x875f: dynamicedit_output
    0x34009: grass_infomation
    0x36f5b: grass_reflection
    0xed79e: deferred_material_ps_output
    0x9718e: ia_grass_spu_input
    0xc5a78: ia_grass_outsourcing
    0xbf6f7: ia_grass_outsourcing_f32
    0xcd440: grass_spu_input
    0x9a582: grass_outsourcing_input
    0xd1c9e: ia_miragefilter
    0xa01bd: mirage_filter_vs_input
    0x5083a: mirage_filter_ps_input
    0x8b6cd: mirage_heat_vs_input
    0x7bf4a: mirage_heat_ps_input
    0x6a81: ia_simwater_for_view_vs_input
    0xf4adc: simwater_for_view_vs_output
    0x71052: simwater_for_view_ps_input
    0x1c10e: ia_softbody_quad
    0x17b34: ia_softbody_vertex
    0x910b8: ia_softbody_decouple
    0x4f4a8: ia_softbody_vertex_novtf
    0x9ba18: ia_softbody_vertex_ps3
    0xde9fc: ia_softbody_decouple_novtf
    0xe5730: sb_ic_output
    0x60dbb: sb_input
    0x8b897: sb_output
    0xdbfdf: sb_output2
    0xd470d: sb_psmrtout
    0x6c07a: sb_psmrtout2
    0x1f0ec: sb_psmrtout3
    0x960e3: tattoo_output
    0x9bfd7: ia_tattoo_blend2d
    0xbba0b: tattoo_blend2d_output
    0xbc3e0: ia_builder
    0xe48a8: builder_vs_input
    0x1412f: builder_ps_input
    0x78482: ia_sky
    0xbc9a5: ia_astral_body
    0xe49c1: sky_map_vs_out
    0x6d4b: sky_out
    0x6136b: astral_body_vs_out
    0x3377f: ia_sky_star
    0xa99f4: sky_star_out
    0xb7070: sky_starry_sky_out
    0x3d2e3: ia_ambient_shadow
    0xb8e92: ambient_shadow_out
    0x28c98: occlusion_query_vs_output
    0x28615: mrtoutput
    0x3bcde: mrtoutput3t
    0x7a857: ia_vertex_index_f32
    0xc0ecc: ia_vertex_index_f16
    0xe6233: triangle_input
    0x8ebea: triangle_output
    0x4bec1: ia_triangle_index_f32
    0xf185a: ia_triangle_index_f16
    0x224d1: mirror_output
    0x86f52: mirror_filter
    0x7fec5: ia_inf_particle
    0x370eb: inf_particle_vs_input
    0xc796c: inf_particle_ps_input
    0x54df7: material_output_lite
    0xab3c1: material_context_lite
    0x7b2c2: globals
    0xb933b: cbviewprojection
    0x9446d: cbscreen
    0xff2c: cbviewprojectionpf
    0x6d556: cbviewfrustum
    0x42d58: cbworld
    0xb2399: cbtest
    0x76fdd: cbpicker
    0x1c76a: cbmiplevel
    0xc3b63: cbhdrfactor
    0xf90c1: cbroptest
    0x17fa6: cbblendfactor
    0x282cf: sspoint
    0x93bbf: sslinear
    0xa82cc: ssanisotoropic
    0x41382: sswrappoint
    0x71003: sswraplinear
    0x99e5f: sswrapanisotoropic
    0x344a: ssborderpoint
    0x58ea6: ssborderlinear
    0x9099a: sslinearmippoint
    0xd6fa6: ssclamppoint
    0x11dae: ssclamplinear
    0x4d2c8: bsdefault
    0x62b2d: bssolid
    0x67927: bssolidex
    0x23baf: bsblendalpha
    0xd4823: bscomposite
    0xeb00e: bsinvcomposite
    0x3e21b: bsblendinvalpha
    0x4f92: bsadd
    0x81dd4: bsmul
    0xd3b1d: bsaddalpha
    0x9463d: bsaddinvalpha
    0xa07b0: bsblendfactor
    0x13c43: bsblendfactoralpha
    0xc1efc: bsmax
    0x52518: bsnowrite
    0x6cec1: bsazero
    0x936d: bsaadd
    0x86256: bsasub
    0xb806a: bsainvert
    0x28bca: bsrgbwrite
    0x61d96: bsrwrite
    0xd8ebe: bsgwrite
    0x1f0d: bsbwrite
    0x46da3: bsawrite
    0xb4a9e: bsaddcolor
    0x44a2c: bsblendcolor
    0xc4064: bsrevsubalpha
    0xa161b: bsrevsubinvalpha
    0x7017: bsrevsubblendalpha
    0xa31e7: bsrevsubcolor
    0x60194: bsrevsubblendcolor
    0x6a583: bsrevsub
    0x3e185: bsaddalphargb
    0x945a3: bsblendalphargb
    0x61ae4: bsaddcolorrgb
    0xcbec2: bsblendcolorrgb
    0x87d9c: bsaddrgb
    0xb1a3: bsrevsubalphargb
    0xdff3a: bsrevsubblendalphargb
    0x54ac2: bsrevsubcolorrgb
    0x8045b: bsrevsubblendcolorrgb
    0xdd886: bsrevsubrgb
    0xe6cf4: bsminalpha
    0xec315: bsmaxalpha
    0x9726c: bsminalphargb
    0x40963: bsmaxalphargb
    0x4959e: bsblendalphaex
    0x7d43b: bsaddalphaex
    0x8a90a: bsblendcolorex
    0xbe8af: bsaddcolorex
    0x7c9ee: bsaccumulatecoloralpha
    0xeab42: dsdefault
    0xb8139: dsztestwrite
    0x50a08: dsztestwritegt
    0x7d2f6: dsztest
    0xa967c: dszwrite
    0xd79e0: dszwritestencilwrite
    0xc80a6: dsztestwritestencilwrite
    0x30511: dszteststencilwrite
    0x45aeb: dsstencilwrite
    0x490b9: rsdefault
    0x108cf: rsmesh
    0xc220b: rsmeshbias1
    0x573b1: rsmeshbias2
    0x24327: rsmeshbias3
    0x6d684: rsmeshbias4
    0x1e612: rsmeshbias5
    0x8b7a8: rsmeshbias6
    0xf873e: rsmeshbias7
    0x9aaf: rsmeshbias8
    0x7aa39: rsmeshbias9
    0xb5506: rsmeshbias10
    0xc6590: rsmeshbias11
    0x5342a: rsmeshbias12
    0x2ab01: rsmeshcf
    0x92333: rsmeshcn
    0xc3c2c: rsprim
    0x29883: rsscissormesh
    0xfac60: rsscissorprim
    0xb3bad: rswireframe
    0x46fd4: cbsystemgamma
    0x73a1c: cbsystemmiptarget
    0x2f3d9: cbsystemnormalslope
    0x7aa9a: cbsystemdepthcopy
    0x83d11: cbhdremphasis
    0xc0dfc: cbsystemstencilrouting
    0xfc672: sssystemcopy
    0x33564: bsmrtwrite0001
    0xf34b3: bsmrtwrite0010
    0x80425: bsmrtwrite0011
    0x66fc5: bsmrtwrite0100
    0x15f53: bsmrtwrite0101
    0xd5e84: bsmrtwrite0110
    0xa6e12: bsmrtwrite0111
    0x86297: bsmrtwrite1000
    0xf5201: bsmrtwrite1001
    0x353d6: bsmrtwrite1010
    0x46340: bsmrtwrite1011
    0xa08a0: bsmrtwrite1100
    0xd3836: bsmrtwrite1101
    0x139e1: bsmrtwrite1110
    0xa575c: ssprocedural
    0x6eaa9: cbdevelopflags
    0xa8b0a: ssdevelop
    0x80570: bsblendaddalpha
    0xf09b: bsblendblendalpha
    0xe74f3: bsblendaddcolor
    0x68118: bsblendblendcolor
    0x20522: bsblendadd
    0x9861a: bsblendrevsubalpha
    0x8150b: bsblendrevsubblendalpha
    0xff799: bsblendrevsubcolor
    0xe6488: bsblendrevsubblendcolor
    0x2fc8a: bsblendrevsub
    0xb5299: bsblendminalpha
    0xbfd78: bsblendmaxalpha
    0x3e292: bsblendnoblend
    0x627fb: bsblendaddalphargb
    0x257fb: bsblendblendalphargb
    0x3dc9a: bsblendaddcolorrgb
    0x7ac9a: bsblendblendcolorrgb
    0xc2495: bsblendaddrgb
    0x3d377: bsblendrevsubalphargb
    0xa50c0: bsblendrevsubblendalphargb
    0x62816: bsblendrevsubcolorrgb
    0xfaba1: bsblendrevsubblendcolorrgb
    0xdb05d: bsblendrevsubrgb
    0xcb412: bsblendminalphargb
    0x1cf1d: bsblendmaxalphargb
    0xb444c: bsblendadddestcolor
    0xcf066: bsblendblendadddestcolor
    0xa81e5: bsblendblendadddestalpha
    0x5598: bsblendadddestcolorrgb
    0xb2935: bsblendblendadddestcolorrgb
    0xed254: bsblendblendadddestalphargb
    0x6ceb8: bsblendnoblendrgb
    0x99073: cblocalwind
    0x6c801: cbmaterial
    0x138a5: dsfilterstencilequal
    0x17a40: cbfilter
    0x3dc11: ssfilter
    0x1ec3f: cbhermitecurve
    0x7c82c: cbfog
    0x9a6da: cbblendfog
    0x65c12: bsfogblend
    0xab962: cbskinning
    0x4e7f5: cbjointmatrix
    0x18096: cbjointmatrixpf
    0x57b29: cbjointmatrixex
    0x11529: cbambient
    0x25444: cblightgroup
    0x7554f: cbdeferredlightingdiscontinuitysensitivefiltering
    0xea691: cbdynamiclighting
    0x6c72: cbdynamiclightingdl
    0xef767: sstransparencymap
    0xcaa79: ssalbedomap
    0x92388: ssalbedomapclamp
    0x9788f: ssocclusionmap
    0x25c76: ssnormalmap
    0x80088: ssnormalmapclamp
    0x8c4be: ssdetailnormalmap
    0xba5e: ssparallaxheightmap
    0x2a7a2: cblightmask
    0xa0809: sslightmap
    0x78211: ssthinmap
    0x4e02c: cbchannelblend
    0x41971: ssfresnelmap
    0xbbf63: ssenvmap
    0xf7792: ssenvmaplodbias1
    0x62628: ssenvmaplodbias2
    0x116be: ssenvmaplodbias3
    0x5831d: ssenvmaplodbias4
    0x2b38b: ssenvmaplodbias5
    0x339e2: ssspheremap
    0x8043e: ssspecularmap
    0x7d302: ssspecularmapclamp
    0x20b29: ssshininessmap
    0x6301e: ssemissionmap
    0xefca3: cbdistortion
    0xc48f7: cbdistortionrefract
    0x60776: ssdistortionmap
    0x4be4c: cbdissolve
    0xed825: ssdisolvemap
    0xb3c62: cbswing1weight
    0x326ff: cbswing2weight
    0x34794: cbquantcompress
    0x4f981: cbswingbillboard
    0x9845c: cbinstancematrix
    0xadd99: cbinstanceid
    0xf9284: cbinstanceshadowcastercache
    0x9b315: cblatticedeform
    0x5b30d: cbmorph
    0xd7f0c: sswraponelinear
    0x15419: cbvertexdisplacement
    0x51814: cbvertexdisplacement2
    0x22882: cbvertexdisplacement3
    0xceb0f: cbvertexdisplacementwave
    0x61e43: cbvertexdisplacementexplosion
    0x65ba7: cbvertexdisplacementranduv
    0xb1999: cbvertexdisplacementexplosionquant
    0x61c6e: cbvertexdispmaskuv
    0x3253f: cbvertexdispuv
    0xd6e60: cbvertexdisplacementdirexplosion
    0x7abfb: cbdebugview
    0xae375: cbmotionblur
    0xdd686: cbmaterialvelocity
    0xd846b: bsoutlinemodulate
    0xed449: bsoutlineblend
    0xcb409: cboutlinefilter
    0x4c59c: cboutlinemask
    0xedb6c: dsoutlinezteststenciltest
    0x462bd: dsoutlineztestwritestenciltest
    0x12ceb: cbshadowlight
    0xb8cc1: cbshadowtype
    0x3b517: cbmultishadow
    0x33657: cbshadowreceivermode
    0xa1d64: cbshadowcasterrasterizerstate
    0xd621e: cbshadowcast
    0x118c5: cbshadowcastoption
    0x7899: cbshadowfrustum
    0x873d4: cbshadowreceive
    0x26b3c: ssshadowdepth
    0x42282: ssshadowdepthcomp
    0x44a27: ssshadowvariance
    0x8618d: ssshadowvariance0
    0xf511b: ssshadowvariance1
    0x600a1: ssshadowvariance2
    0x13037: ssshadowvariance3
    0x47a52: ssshadowvariancemip0
    0xead2: bsshadowrecvsolidgroup0
    0x7da44: bsshadowrecvsolidgroup1
    0x7e510: bsshadowrecvtransparentgroup0
    0xd586: bsshadowrecvtransparentgroup1
    0x44f6e: bsshadowrecvmultisolidgroup0
    0x37ff8: bsshadowrecvmultisolidgroup1
    0xd9b33: bsshadowrecvmultitransparentgroup0
    0xaaba5: bsshadowrecvmultitransparentgroup1
    0xc3ce7: bsshadowrecvzpass
    0x5927c: cbdualparaboloid
    0x32881: dsdeferredlightingzwritestenciltestrouted
    0x253fe: dsdeferredlightingzteststencilwritedepthfail
    0x5ac93: dsdeferredlightingzteststencilwritedepthpass
    0x1c51f: dsdeferredlightingzteststenciltest
    0xcedca: dsdeferredlightingstenciltest
    0xb1f17: bsaccumulatecoloralphamrt2
    0x3e812: bsmultiplycoloralpha
    0xe9f8f: bsmultiplycoloralphamrt2
    0xb03f5: cblightvolume
    0x1ce5f: cbambientmask
    0xb255f: bsambientmaskgroup0
    0xc15c9: bsambientmaskgroup1
    0x54473: bsambientmaskgroup2
    0x274e5: bsambientmaskgroup3
    0x6536e: bsambientmaskalphagroup0
    0x163f8: bsambientmaskalphagroup1
    0x83242: bsambientmaskalphagroup2
    0x21012: cbrsmindirectlighting
    0x41bce: cbadhesion
    0x97d31: cbmaterialsss
    0x16977: cbmaterialsssblend
    0xe0fb1: cbtessellation
    0xc2a7d: ssdisplacementmap
    0xd0bfb: cbdisplacement
    0xffe12: cbshadowreceive0
    0x8ce84: cbshadowreceive1
    0x19f3e: cbshadowreceive2
    0x6afa8: cbshadowreceive3
    0x762c6: cbbilateralfilter
    0x9510f: cbprimitivedebug
    0xbdc9: cbprimitiveview
    0x43955: cbprimitivecoord
    0xf807b: cbprimitiveex
    0x86183: cbprimitivetessellationcmn
    0x4801: cbprimitivemetadatafresnel
    0x88053: cbprimitivemetadatauvclamp
    0xa7282: cbprimitivemetadatashade
    0x8e5f5: cbprimitivemetadataocclusion
    0x8f8dc: cbprimitivemetadatalvcorrection
    0xb608a: cbprimitivemetadatalensflare
    0x3d833: cbcloudmetadata
    0x96471: cbprimitivemodel
    0x1737f: cbprimitivemodeldistortion
    0x2f33e: cbprimitivetessellation
    0x120d2: cbprimitiveparallaxtess
    0x198c: cbprimitiveparticletess
    0x144fb: ssprimocclusionmap
    0x589a0: dsprimstenciltesteq
    0x55fb7: dsprimstenciltestneq
    0x874e6: dsprimzteststenciltesteq
    0x566ef: dsprimzteststenciltestneq
    0xb4db: dsprimzwritestenciltesteq
    0x523e: dsprimzwritestenciltestneq
    0x948b0: dsprimztestwritestenciltesteq
    0x58312: dsprimztestwritestenciltestneq
    0x2efc0: cbradialblurfilter
    0xf144a: ssradialfilterclamplinear
    0x12819: cbtvnoisefilter
    0xe2e0: cbfisheyefilter
    0x6c72d: cbcolorcorrectmatrix
    0x38b38: cbcolorcorrectgamma
    0x613a0: cbcolorcorrectcolor
    0xf8ec6: cbvolumecolorcorrectblend
    0x20868: ssvariance
    0x10368: cbbloomfilter
    0x799b6: cbbloomgaussblur
    0xef6d: cblightscattering
    0x90f19: cbimageplane
    0x23b9f: cbhazefilter
    0xa6d02: cbtonemapfilter
    0xb5ada: cbcubemapfilter
    0xfdfe1: cbdoffilter
    0xe97d7: cbssaoffilter
    0xf10ba: cbssaoffilterlineardepth
    0xd350: cbssaoffilterintensity
    0xd52c0: bsssao
    0xa2dd4: cbbokehcomposite
    0x1bca: cbfilteredgeantialiasing
    0x1f7d8: cbgodraysiterator
    0x42767: cbgodraysfilter
    0x93b75: ssp2o
    0x79707: bsgodrays
    0x67f65: cbblurmask
    0x8b744: cbblurmaskintermediate
    0xad62f: cbchromaticaberration
    0x87825: cbtangentfilter
    0xe8494: cbbruteforcelightingparam
    0x16e2f: cbwaterwave
    0xcfbeb: cbwaternormal
    0xfec9c: cbwaterdetail
    0xd1039: cbwaterfog
    0xa91ac: cbwatercaustics
    0x962f8: cbwaterbubble
    0xf1122: cbwatershadow
    0xdf2ea: cbwaterripple
    0x28c1: cbwater
    0x6ab0: cbguiglobal
    0x6a0fc: cbguimatrix
    0x31804: cbguistaticcolor
    0xbc61b: cbguicolor
    0xc9548: cbguicolorattribute
    0x5a10f: cbguicoord
    0x961c2: cbguialphamask
    0xcc76e: cbguifontfilter
    0xfd6d5: ssgui
    0x21f00: rsguiscissorenable
    0xcb2cf: bsguiaddcolorrgb
    0x59f95: bsguiaddinvcolor
    0x5a070: bsguicolorblendalphaadd
    0xe7275: bsguialphamaskwrite
    0xee62b: bsguialphamaskupdate
    0xdfa1c: bsguialphamaskadd
    0x85bd: dsguistencilwrite
    0x473fd: dsguistencilapply
    0xa321e: dsguistencilapplyreverse
    0xc325e: dsguistencilupdate
    0x8c2a7: dsguizteststencilapply
    0x786cb: dsguizteststencilapplyreverse
    0x97605: dsguizteststencilupdate
    0xb37b8: dsguizwritestencilapply
    0xf50c2: dsguizwritestencilapplyreverse
    0x94805: dsguizwritestencilupdate
    0x944e: dsguiztestwritestencilapply
    0xfbde2: dsguiztestwritestencilapplyreverse
    0x7948f: dsguiztestwritestencilupdate
    0x830df: cbprojectiontexture
    0x21560: cbtextureblend
    0xa4392: cbgpuparticleex
    0x8b47e: cbgpuparticletex
    0x2ae35: cbgpuparticlelvcorrection
    0xa7a7c: cblightshaft
    0xafe4: cbmark
    0xaee18: ssgrass
    0xe2958: cbgrasscommon
    0x21601: cbgrassmaterial
    0x6de1b: cbgrasschain
    0xe2745: cbgrassbillboard
    0xc351b: cbgrassroot
    0xc67d4: cbgrassglobalwind
    0x3c013: cbgrassunit
    0xcf50f: cbgrasspointshadow
    0x93f: bsaddrwrite
    0xb9a17: bsaddgwrite
    0x60ba4: bsaddbwrite
    0x2790a: bsaddawrite
    0x76747: bssubrwrite
    0xcf46f: bssubgwrite
    0x165dc: bssubbwrite
    0x51772: bssubawrite
    0x430ef: bsalphatocoverage
    0xeb037: cbmiragecommon
    0xcffe1: cbmiragenoise
    0xf1f19: cbmiragerefract
    0xb67fd: cbmiragedepthblend
    0x454f9: bsrgwrite
    0x32b2a: bsbawrite
    0x273ee: dsztestwriteback
    0x2544d: cbsoftbodysim
    0x70110: cbsoftbodyrtparam2
    0xd64a9: cbsoftbodydirectgrasswind
    0xd5f2e: cbsoftbodyrtparam
    0x177ab: cbsoftbodyquad
    0x28ecf: cbsoftbodycollision
    0x43407: cbsoftbodyworldoffset
    0x53f32: cbsoftbodylwmatrix
    0x84f12: cbsbviewprojection
    0xd2f6: cbsbextrapolation
    0xb6932: cbtattoo
    0x951d0: cbsky
    0x203a: cbskyfog
    0xdd14a: cbskyastralbody
    0xb538: cbskystar
    0xbb8ef: cbskystarryskycolor
    0xb5f29: cbambientshadow
    0x78d29: dsambientshadow
    0x3ca94: bsaddmrt
    0x23e17: cbmirror
    0xe1115: cbinfparticlecontext
    0x59919: cbinfparticletexture
    0xca367: ssinfparticle
    0xaddac: ssinfparticlepoint
    0xaee37: cbbalphaclip
    0x4a2bf: cbsacan
    0x6f016: cbcolormask
    0x1d9ff: cbcolorcorrectfilter
    0x84115: cbratemap
    0x8c162: dsnvstenciltest
    0x36738: bsnvmodelblendalpha
    0x85b3b: cbnvmodel
    0x9cbf1: cbpsdiscardmaterialparamcommon
    0x11a88: cbcolormodifieropticalcamouflage
    0x16a5b: cbmaterialstd
    0xc0772: cbmaterialstdmodeleffect
    0xfd5f7: cbmaterialconstant
    0x798aa: cbmaterialtoon
    0xaf34: tbasemap
    0x5a3f: tcubemap
    0x377b6: tdepthmap
    0x603e7: tvolumemap
    0x6b95d: tvolumeblendmap
    0xa742c: ttestmap
    0x99851: tblendmap
    0x8f23f: treductionblendmap
    0x904d: tocclusiondepth
    0x3c580: ttablemap
    0x298de: tvertexpositionmap
    0xa227d: tvertexpositionsubmap
    0x282e9: tvertexnormalmap
    0x15232: tvertextangentmap
    0x85551: tprocedural1d0
    0xf65c7: tprocedural1d1
    0x6347d: tprocedural1d2
    0x104eb: tprocedural1d3
    0xeeb08: tprocedural2d0
    0x9db9e: tprocedural2d1
    0x8a24: tprocedural2d2
    0x7bab2: tprocedural2d3
    0x931b7: tfiltertempmap1
    0x600d: tfiltertempmap2
    0xee653: tfogtable
    0x74491: tfogtablevtf
    0xe7104: tfogvolumemap
    0x6166e: tfogfrontdepth
    0x726bd: tfogbackdepth
    0x7b747: tfogfrontdepthsmall
    0xa27e3: tfogbackdepthsmall
    0xe06ea: tmatrixmap
    0x7c770: tmatrixpfmap
    0xe2e4: tspotlighttexture0
    0x7d272: tspotlighttexture1
    0xe83c8: tspotlighttexture2
    0x9b35e: tspotlighttexture3
    0xd26fd: tspotlighttexture4
    0xa166b: tspotlighttexture5
    0x347d1: tspotlighttexture6
    0x47747: tspotlighttexture7
    0x60f5a: tpointlighttexture0
    0x13fcc: tpointlighttexture1
    0x86e76: tpointlighttexture2
    0xf5ee0: tpointlighttexture3
    0xbcb43: tpointlighttexture4
    0xcfbd5: tpointlighttexture5
    0x5aa6f: tpointlighttexture6
    0x29af9: tpointlighttexture7
    0x225b6: tlightaccumulationtexture0
    0x51520: tlightaccumulationtexture1
    0xd0e52: tspheremapluttexture
    0xf0061: tdsfbuffer
    0x1698a: ttransparencymap
    0xcd06f: talbedomap
    0xff5be: talbedoblendmap
    0x1e421: tocclusionmap
    0x22660: tnormalmap
    0xed6be: tnormalblendmap
    0x75a53: tdetailnormalmap
    0xd4694: tdetailnormalmap2
    0x88165: tdetailmaskmap
    0x7b571: theightmap
    0x1cb2a: thairshiftmap
    0xc496e: tlightmaskmap
    0xaa6f0: tlightmap
    0x5f2a: tthinmap
    0x6ab7e: tindirectmap
    0x90ac1: tindirectmaskmap
    0x47c5a: tfresnelmap
    0x64c43: tenvmap
    0x343f4: tspheremap
    0xf1d7e: tglobalenvmap
    0x7a8ee: tmaskmap
    0xed1b: tspecularmap
    0x181cf: tspecularblendmap
    0xa9787: tshininessmap
    0xed93b: temissionmap
    0x32105: tdistortionmap
    0x45fbb: tnoise
    0x57e05: tdepthtestmap
    0x9a94b: twcvtfpos
    0xe818b: twcvtfpos1
    0xe1a61: twcvtfprevpos
    0x2efee: twcvtfprevpos1
    0x1c967: tshaderattributes
    0x4934a: tvtxdisplacement
    0x39c0: tvtxdispmask
    0xd8dbb: tshadowmapcombine
    0x4f725: tshadowmapcombine0
    0x3c7b3: tshadowmapcombine1
    0xa9609: tshadowmapcombine2
    0xda69f: tshadowmapcombine3
    0x811a3: tvirtualcubeshadowfaceselection
    0xc1f66: tvirtualcubeshadowfaceoffset
    0xbb0eb: tvirtualcubeshadowindirection
    0x6d000: tfrontparaboloidmap
    0xa52e7: tbackparaboloidmap
    0xfa06c: tgbuffer
    0x3be61: tcomparisontexture
    0xa820: tambientmaskmap
    0x4d7ed: treflectiveshadowmap0
    0x3e77b: treflectiveshadowmap1
    0x2323f: tindirectlighting
    0x47a64: tsssdiffusemap0
    0x34af2: tsssdiffusemap1
    0xa1b48: tsssdiffusemap2
    0xd2bde: tsssdiffusemap3
    0x9be7d: tsssdiffusemap4
    0xe8eeb: tsssdiffusemap5
    0x3b490: tdisplacementmap
    0xeebd1: tdepthbiasmap
    0x1356f: tdispersionmap
    0x75926: tprimdepthmap
    0x9210a: tprimnormalmap
    0xa9e1d: tprimmaskmap
    0x890f8: tprimscenemap
    0x72798: tprimalphamap
    0xd6b8a: ttvnoisemap
    0xd808a: ttvnoisemaskmap
    0xeb178: tcolorcorrecttablemap
    0x8c5a1: tcubeblendmap
    0x61f3: tdofmap
    0x2abaf: tssaonarrowmap
    0xfa82e: tssaowidemap
    0x672c: tssaonormalmap
    0xb6053: tssaoreductionnormalmap
    0x86f0b: tssaobackfacedepthmap
    0x34912: ttangentmap
    0x3ffea: twaterrefraction
    0x35a6f: twaterreflection
    0xae385: twaterenvironment
    0xd02f0: twaterdetail
    0xbe9e: twaterdetail2
    0xf58a: twatercaustics
    0xb8c94: twaterbubble
    0xa3d51: twaterbubble2
    0xa0778: twaterbubblemask
    0xdff4e: twatershadow
    0xf1c86: twaterripple
    0x3a000: twaterdepthmap
    0xc9f82: twatersurfacemap
    0xa7f13: twatersurfacemap2
    0x5be8c: tguibasemap
    0x996fe: tguiblendmap
    0x307a7: tguialphamap
    0xdbccc: tyuvdecodery
    0xbf0e7: tyuvdecoderu
    0x2a15d: tyuvdecoderv
    0x2267c: ttextureblendsource0
    0x516ea: ttextureblendsource1
    0x8a204: ttextureblendsourcecube0
    0xf9292: ttextureblendsourcecube1
    0x29f23: tgrassalbedomap
    0x4a4f4: tdynamiceditmap
    0x9aa66: twindmap
    0x79784: tmiragedepthmap
    0x85e5a: tmiragescenemap
    0xeccaa: tmiragerefractionmap
    0x4839c: tmiragenoisemap
    0x91766: tsimwaterforview
    0x2d4ef: tsoftbodysrctex1
    0xb8555: tsoftbodysrctex2
    0xcb5c3: tsoftbodysrctex3
    0x82060: tsoftbodysrctex4
    0xf10f6: tsoftbodysrctex5
    0x6414c: tsoftbodysrctex6
    0x171da: tsoftbodysrctex7
    0x6ed89: tsoftbodytexsphere
    0x7dc41: tsoftbodytextriangle
    0x60555: tsoftbodytexbox
    0x7b304: tsoftbodytexellipsoid
    0x67c82: tsoftbodytexcapsule
    0x88eb0: tsoftbodytexterrain
    0x30c86: tsoftbodytexdepthnorm1
    0xa5d3c: tsoftbodytexdepthnorm2
    0xd6daa: tsoftbodytexdepthnorm3
    0x9f809: tsoftbodytexdepthnorm4
    0xec89f: tsoftbodytexdepthnorm5
    0x79925: tsoftbodytexdepthnorm6
    0xa9b3: tsoftbodytexdepthnorm7
    0xfb422: tsoftbodytexdepthnorm8
    0xf0bbe: tbuilderbasemap
    0x23a7c: trayleighdepthmap
    0x6329c: tmiedepthmap
    0x6edb9: trayleighscattermap
    0x319d3: tmiescattermap
    0x76682: tcloudscattermap
    0x367b0: tstarryskymap
    0x2edc: tambientshadowmap
    0x7e9aa: tblendratemap
    0xb97e6: tenvmap2
    0x73b94: tshininessblendmap
    0xc3df7: tdetailnormalblendmap
    0x52e1: tdistortionblendmap
    0x62fde: tdistortionblend2map
    0x57c1c: talbedoblend2map
    0x75d3f: tnormalblend2map
    0x187f7: tnormalmaskmap
    0xeb065: ttextureblendmap
    0x64b96: tcolormodifieropticalcamouflagemap
    0xe88e6: textendmap
    0xc5512: tproceduralmap
    0x5dec1: tlutfresnel
    0xb998: tlutshininess
    0xa5553: tluttoon
    0xa961: max4
    0x32a4: makedirectionfromuv
    0x120e2: easein
    0xe8d21: calcviewdepth
    0x90: flinearcolor
    0x45e67: flinearcolorsrgb
    0xd88b4: ffrontfacenormal
    0x2cb25: ffrontfacenormaltwosidedlh
    0x88c2f: fviewproj
    0x28f5f: fuvproj
    0x1a2ad: fdithering
    0x7e772: fditheringbayer10bit
    0x49610: fditheringbayer8bit
    0x90bc8: vs_system
    0x2898c: vs_systemdownsample16
    0xc6083: ftonemap
    0x4eeed: fluminance
    0xfe847: fluminanceenable
    0x95184: fsystemcopy
    0xfff1e: fsystemcopygamma
    0x76269: fsystemconverthightmaptonormalmap
    0x2af95: fsystemconverthightmaptoparallaxmap
    0x6e9ab: fsystemconvertreversehightmaptonormalmap
    0x41b10: fsystemconvertreversehightmaptoparallaxmap
    0x8554a: fsystemconvertbasemaptonormalmap
    0xe8a14: fsystemmakemiplevel
    0x3b944: fsystemcachecopyy
    0xe6c9f: fsystemcachecopycb
    0x97cfb: fsystemcachecopycr
    0x2314: fsystemcachedecodecopy
    0xee329: ps_systemcopy
    0x15da8: ps_systemdepthcopy
    0xec68f: ps_systemdepthdownsample
    0x75ba1: ps_systemdepthhmax
    0x17b0d: ps_systemdepthvmax
    0xf93e4: ps_systemminidepthcopy
    0xfbc8a: ps_systemaacopy
    0xe86da: ps_systemtonemap
    0x990f1: ps_systemtonemapdepth
    0x2f0b3: ps_systemclear
    0x8fc66: ps_systemclearmrt2
    0xfccf0: ps_systemclearmrt3
    0xb5953: ps_systemclearmrt4
    0xcb16a: ps_systemdepthtoalpha
    0xd9a99: ps_systemdepthtoalphaaa
    0xf6893: ps_systemdownsample4
    0x790f3: ps_systemdownsample4emphansis
    0x9bcaa: ps_systemdownsample4hdr
    0xf8c4a: ps_systemdownsample16
    0x9ecd2: ps_systemocclusionconvertz
    0xaa0a0: ps_systemps3aacopy
    0x4a7ab: ps_systemps3aadepthcopy
    0xbdcf2: ps_systemps3zcullreload
    0xd812b: ps_systemclearstencilrouting
    0x22a87: ps_systemfillstencilrouting
    0x84f11: falphatest
    0xaa2b3: falphatestalways
    0xafebf: falphatestnever
    0xd0c33: falphatestgreater
    0xe273: falphatestgreaterequal
    0x93ab: falphatestless
    0x10d43: falphatestlessequal
    0x44958: falphatestequal
    0x6dd66: falphatestnotequal
    0x4af2b: falphatocoveragerop
    0x49cbc: falphatocoverage
    0xd8f42: encodesrgb
    0x111b7: foutputencode
    0x1760c: foutputencodenone
    0xf8751: foutputencodezero
    0xbbae2: foutputencodedepth24
    0x2ad30: foutputencodercrgb
    0x79dca: foutputencoderrrgb
    0x98e3e: foutputencodergbi
    0xd3507: foutputencoderrrgbi
    0xd44fe: foutputencodenormal
    0x3fe89: foutputencodevariance
    0xea25: foutputencodesrgbrcrgb
    0x883ab: foutputencodesrgbrrrgbi
    0x5dadf: foutputencodesrgbrrrgb
    0xda50d: foutputencodesrgb
    0xb9409: foutputencodesrgbrgbi
    0xa7aa1: decodesrgb
    0xc559d: fprocedural1d1e0
    0xb650b: fprocedural1d1e1
    0x234b1: fprocedural1d1e2
    0x50427: fprocedural1d1e3
    0xaebc4: fprocedural1d2e0
    0xddb52: fprocedural1d2e1
    0x48ae8: fprocedural1d2e2
    0x3ba7e: fprocedural1d2e3
    0x881f3: fprocedural1d3e0
    0xfb165: fprocedural1d3e1
    0x6e0df: fprocedural1d3e2
    0x1d049: fprocedural1d3e3
    0x79776: fprocedural1d4e0
    0xa7e0: fprocedural1d4e1
    0x9f65a: fprocedural1d4e2
    0xec6cc: fprocedural1d4e3
    0xc2f4d: fprocedural2d1e0
    0xb1fdb: fprocedural2d1e1
    0x24e61: fprocedural2d1e2
    0x57ef7: fprocedural2d1e3
    0xa9114: fprocedural2d2e0
    0xda182: fprocedural2d2e1
    0x4f038: fprocedural2d2e2
    0x3c0ae: fprocedural2d2e3
    0x8fb23: fprocedural2d3e0
    0xfcbb5: fprocedural2d3e1
    0x69a0f: fprocedural2d3e2
    0x1aa99: fprocedural2d3e3
    0x7eda6: fprocedural2d4e0
    0xdd30: fprocedural2d4e1
    0x98c8a: fprocedural2d4e2
    0xebc1c: fprocedural2d4e3
    0xb33dd: vs_proceduraltexture
    0x75dd2: fprocedural1e
    0xa0e11: fprocedural2e
    0x13f50: fprocedural3e
    0xa997: fprocedural4e
    0x2fc3e: ps_proceduraltextureunorm
    0x2099e: ps_proceduraltexturesnorm
    0x9d5f: fxaafilter
    0x6b79f: fxaa3
    0xde53: fxaa3hq
    0x6a9e4: vs_fxaa
    0x69cde: ps_fxaa
    0x1e1de: vs_fxaa3
    0xee859: ps_fxaa3
    0x4f6c6: ps_fxaa3hq
    0xce301: vs_develop2d
    0x7d240: vs_develop3d
    0xbee36: getdeveloptexedgefont
    0x92cd: getdeveloptexcubeface
    0xeb150: getdeveloptexcuberefrect
    0x68cd5: fdeveloptexture
    0xe1bb5: fdeveloptexcubeface
    0xcb6c5: fdeveloptexcuberefrect
    0x5674e: fdeveloptexedgefont
    0x4151b: getdeveloptexture
    0xdc291: fdevelopdecode
    0x6de99: fdevelopdecode_r
    0xb3a72: fdevelopdecode_g
    0x1cefd: fdevelopdecode_b
    0x89f47: fdevelopdecode_a
    0x29288: fdevelopdecode_rgb
    0x5f0b4: fdevelopdecode_rgbi
    0x2e0d0: fdevelopdecode_rgby
    0x16517: fdevelopdecode_rgbn
    0x9009b: fdevelopdecode_font
    0x264d5: ps_develop
    0xbb354: ps_developsimple
    0x9d005: ps_developedgefont
    0x74ee9: fcollisionsimplevs
    0xde96f: fcollisionsimpleps
    0x2e955: fwindtrianglecurve
    0x6fc06: fwindsincoscurve
    0x10345: fwinddirection
    0xc2688: fwindpoint
    0xd1946: fwindline
    0xbf216: flocalwindloopdirection
    0xf2310: flocalwindlooppoint
    0xdb440: flocalwindloopline
    0xbf5ce: flocalwindloopslot0
    0xcc558: flocalwindloopslot1
    0x594e2: flocalwindloopslot2
    0x3a4fa: flocalwindreference
    0x5967d: flocalwind
    0xa4f8b: flocalwinddisable
    0x879e6: fdynamiclocalwind0
    0xf4970: fdynamiclocalwind1
    0x618ca: fdynamiclocalwind2
    0x1285c: fdynamiclocalwind3
    0x5bdff: fdynamiclocalwind4
    0x28d69: fdynamiclocalwind5
    0xbdcd3: fdynamiclocalwind6
    0xcec45: fdynamiclocalwind7
    0xa3c5a: flocalwinddirection
    0x2ef38: flocalwindpoint
    0x9840b: flocalwindline
    0xc9df1: flocalwindunroll
    0xd2ac6: initmaterialcontext
    0x42c8b: fsamplecount
    0x73ebe: fsamplecount1
    0xe6f04: fsamplecount2
    0x95f92: fsamplecount3
    0xdca31: fsamplecount4
    0xafaa7: fsamplecount5
    0x3ab1d: fsamplecount6
    0x49b8b: fsamplecount7
    0xb861a: fsamplecount8
    0xcb68c: fsamplecount9
    0xb0919: fsamplecount10
    0xc398f: fsamplecount11
    0x56835: fsamplecount12
    0x258a3: fsamplecount13
    0x6cd00: fsamplecount14
    0x1fd96: fsamplecount15
    0x8ac2c: fsamplecount16
    0xf9cba: fsamplecount17
    0x812b: fsamplecount18
    0x7b1bd: fsamplecount19
    0x65ada: fsamplecount20
    0x16a4c: fsamplecount21
    0x83bf6: fsamplecount22
    0xf0b60: fsamplecount23
    0xb9ec3: fsamplecount24
    0xcae55: fsamplecount25
    0x5ffef: fsamplecount26
    0x2cf79: fsamplecount27
    0xdd2e8: fsamplecount28
    0xae27e: fsamplecount29
    0xd6b9b: fsamplecount30
    0xa5b0d: fsamplecount31
    0x30ab7: fsamplecount32
    0x1d2cb: ffiltertexcoord
    0x80adc: ffilterscreentexcoord
    0x57a8d: ffiltercopy
    0xfd3a4: ffiltercopycolor
    0x455e: vs_filter
    0xa3cd4: ps_filter
    0x6c953: ps_filterdepth
    0x9d9f6: ffiltercomposite
    0xb37ad: fblendfog
    0xc6c1e: fblendfogdiffuse
    0x4ea8b: fblendfogmodulate
    0x4a0dc: fheightfog
    0xd683e: fheightfogvtf
    0x80526: fheightfogworldy
    0xe05f3: fheightfogdistance
    0x8a91e: fheightfogvolume
    0xab951: fheightfogmodelsimple
    0x9d797: fheightfogmodelsimplevtf
    0x1b226: fheightfogmodel
    0x1a40: fheightfogmodelvtf
    0x25f1b: fdistancefog
    0xf94a9: fdistancefoglinear
    0xf7362: fdistancefogexp
    0xf6e87: fdistancefogexp2
    0xb85e7: fdistancefogreverseexp
    0xb3dde: fdistancefogreverseexp2
    0x4cdd9: fdistancefogtable
    0xa2c0f: fdistancefogtablevtf
    0x55e3: ffog
    0x16c02: ffogdistance
    0x6b37d: ffogdistanceest
    0x19e3d: ffogdistancecolortable
    0x31154: ffogdistancecolortableest
    0x2e423: ffogdistancetable
    0x72e31: ffogdistancetableest
    0x38862: ffogvtf
    0xa46e7: ffogvtfnone
    0x5095a: ffogvtfdistance
    0xe9772: ffogvtfdistanceest
    0x2c23d: ffogvtfdistancecolortable
    0x2f1c5: ffogvtfdistancecolortableest
    0x96175: ffogvtfdistancetable
    0xf5a4a: ffogvtfdistancetableest
    0xafd8e: ffiltercolorfogblend
    0x40614: ffiltercolorfogcomposite
    0xf8422: ffilterfogtable
    0x4a102: fjointmatrix
    0x364a9: fjointmatrixpf
    0x6ade2: fjointmatrixfromcbuf
    0xfe371: fjointmatrixpffromcbuf
    0xbb29d: fjointmatrixexfromcbuf
    0x82815: fskinning
    0x51522: fskinningnone
    0x740b9: fskinning1weight
    0xf5a24: fskinning2weight
    0xf6f1e: fskinning4weight
    0xa356e: fskinning4weightbranch
    0xf056a: fskinning8weight
    0x8c95: fskinning8weightbranch
    0x4acd7: fskinningpf
    0x125a6: fskinningpfnone
    0x8822b: fskinningpf1weight
    0x98b6: fskinningpf2weight
    0xad8c: fskinningpf4weight
    0x6bba7: fskinningpf4weightbranch
    0xc7f8: fskinningpf8weight
    0xc025c: fskinningpf8weightbranch
    0xb0e6b: getshdiffuse
    0x67416: fshdiffuse
    0xd9ebd: fshdiffusedisable
    0xb3d2a: fdistanceattenuation
    0x82106: fdistanceattenuationsquarelaw
    0xcf404: getangularattenuation
    0x4d5c4: calclightmask
    0xc60c2: fisoutofrange
    0xed5e1: fdeferredlightinggetclearcolorlightbuffer
    0xeb3c5: fdeferredlightinggetclearcolorlightbufferlog
    0x22898: fdeferredlightingencodeoutput
    0xe1969: fdeferredlightingdecodeinput
    0x80eb6: fdeferredlightingdecodeinputexponent
    0xb20a4: fdeferredlightingdecodeinputlog
    0x954e2: fdeferredlightingencodenormal
    0xd9fc9: fdeferredlightingdecodenormal
    0xde099: fdeferredlightingdecodenormalspheremaplut
    0x69828: fdeferredlightingencodelineardepth
    0xb78d6: fdeferredlightingdecodelineardepth
    0xe8430: setuplight
    0x1dd48: setuplightbalance
    0x55eaf: setuplightspecular
    0x414c7: setuplightdiffuse
    0xe251b: fdynamiclight0
    0x9158d: fdynamiclight1
    0x4437: fdynamiclight2
    0x774a1: fdynamiclight3
    0x3e102: fdynamiclight4
    0x4d194: fdynamiclight5
    0xd802e: fdynamiclight6
    0xab0b8: fdynamiclight7
    0xf394a: fdynamiclightdl0
    0x809dc: fdynamiclightdl1
    0x15866: fdynamiclightdl2
    0x668f0: fdynamiclightdl3
    0x2fd53: fdynamiclightdl4
    0x5cdc5: fdynamiclightdl5
    0xc9c7f: fdynamiclightdl6
    0xbace9: fdynamiclightdl7
    0x56272: finfinitelight
    0x705ce: finfinitelightb
    0x7253c: finfinitelights
    0x4a0fb: finfinitelightd
    0xc1293: fpointlight
    0xcce50: fpointlightb
    0xf6b65: fpointlightd
    0xceea2: fpointlights
    0xbde34: fpointlightr
    0xfcde2: fpointlightbr
    0x56a64: fpointlightdr
    0x6eef2: fpointlightsr
    0xafb78: fspotlight
    0x53349: fspotlightb
    0x6967c: fspotlightd
    0x513bb: fspotlights
    0x2232d: fspotlightr
    0x32cdf: fspotlightbr
    0x98b59: fspotlightdr
    0xa0fcf: fspotlightsr
    0x50219: fcapsulelight
    0x2c113: fcuboidlight
    0x233a3: fcuboidlightb
    0x19696: fcuboidlightd
    0x21351: fcuboidlights
    0x1a1c7: fbrdf
    0x5B3E9: fbrdffur
    0x7a331: fbrdfhalflambert
    0x23990: flighting
    0x71bac: flightingvs
    0x5cc90: fdeferredlightingsamplinglight
    0x42fb0: fdeferredlightingsamplinglightdiscontinuityfiltering
    0x7e5b0: fdeferredlightingsamplinglightdiscontinuityfilteringlayer1
    0xc337d: fdeferredlightingsamplinglightcomformancefiltering
    0x1e568: flightingdeferredlighting
    0xd919b: flightingdeferredlightingapproximatespecular
    0x4bb9d: flightingdeferredlightingseparatespecular
    0x171dd: ftransparency
    0x8e54a: ftransparencyalpha
    0x66f6c: fuvtransparencymap
    0xc0572: fchanneltransparencymap
    0x9090a: ftransparencymap
    0xad6b9: ftransparencydodgemap
    0x5da47: ftransparencyvolume
    0xe03de: ftransparencyalphaclip
    0x6159a: ftransparencymapalphaclip
    0xcceed: fuvalbedomap
    0x24f65: fuvalbedoblendmap
    0x1c76e: falbedo
    0xa826a: falbedomap
    0xb30ba: falbedomapblend
    0xb1ba8: falbedomapblendalpha
    0xad982: falbedomapblendtransparencymap
    0x9ab11: falbedomapmodulate
    0xf8146: falbedomapadd
    0x76cf5: falbedomapblendcoloronly
    0xd5585: fuvocclusionmap
    0x82634: fchannelocclusionmap
    0x7b9ec: focclusion
    0x4bc45: focclusionmap
    0xbec9: focclusionambient
    0x3f932: focclusionambientmap
    0x238e2: fuvnormalmap
    0x36c65: fuvnormalblendmap
    0x5cb5: fuvdetailnormalmap
    0x576df: fuvdetailnormalmap2
    0xffbd0: fbump
    0xb22d7: fbumpnormalmap
    0xb2612: fbumpnormalmapblendtransparencymap
    0x610a5: fbumpdetailnormalmap
    0x6722c: fchanneldetailmap
    0x299b7: fbumpdetailmasknormalmap
    0xe0f7: fbumpdetailnormalmap2
    0xf46b0: fbumphair
    0xef377: fbumpparallax
    0xe1c7f: fbumpparallaxocclusion
    0xea1ac: flightmask
    0xf4580: flightmasksolid0
    0x87516: flightmasksolid1
    0xd7c5f: flightmasksolid01
    0xbd6a5: flightmasktransparent0
    0xce633: flightmasktransparent1
    0x2bc8b: flightmasktransparent01
    0x795f9: flightmaskenable
    0xfefd6: fambient
    0x63eaa: fambientsh
    0x33737: fuvlightmap
    0xafec0: fuvthinmap
    0x9b0dd: fchannelthinmap
    0xfdb6f: fdiffuse
    0xfe58e: fdiffuseconstant
    0xd6888: fdiffuseconstantsrgb
    0xa8610: fdiffuseconstantsrgbvertexcolor
    0x5325e: fdiffusesh
    0x623c7: fdiffusethinsh
    0xd947: fdiffusethin
    0x25211: fdiffuselightmap
    0x73d0f: fdiffuselightmapocclusion
    0x2d662: fdiffusevertexcolor
    0xf90fb: fdiffusevertexcolorocclusion
    0xa3273: fdiffusevertexcolorsh
    0x91272: fuvprimary
    0xc4ef1: fuvsecondary
    0x14211: fuvunique
    0xa5d4a: fuvextend
    0x5808b: fuvviewnormal
    0xf7556: fuvscreen
    0xc6994: fuvindirectmap
    0x9c151: fuvindirectsource
    0xeb2dc: fuvindirect
    0xec027: fuvindirectmask
    0x7de0b: fchannelr
    0xa3ae0: fchannelg
    0xce6f: fchannelb
    0x99fd5: fchannela
    0xa67d5: fchannelblend
    0x7de48: fuvfresnelmap
    0x54e7c: fchannelfresnelmap
    0x1a481: ffresnel
    0x8c6db: ffresnelschlick
    0x52136: ffresnelschlickrgb
    0x617df: ffresnelschlickmap
    0xac357: freflect
    0x8f001: freflectcubemap
    0x552b7: freflectspheremap
    0xd5bc: freflectglobalcubemap
    0xa2ff1: fuvspecularmap
    0x9b184: fuvspecularblendmap
    0xdd9d4: fchannelspecularmap
    0x50eba: fspecular
    0x24580: fspecularmap
    0x8fd41: fspecularmapblendtransparencymap
    0x773f9: fspeculardisable
    0x62623: fuvshininessmap
    0x35592: fchannelshininessmap
    0x9d7bb: fshininess
    0xfcfe3: fshininessmap
    0x41bd1: fuvemissionmap
    0x3edf4: fchannelemissionmap
    0x87017: femission
    0xe360b: femissionconstant
    0xc71a0: femissionmap
    0xadae3: fthresholdreactionemissionmapclipping
    0x5dc9b: fuvtransformoffset
    0xd0e90: fuvtransformoffset2
    0xa3e06: fuvtransformoffset3
    0x78205: fuvtransformprimary
    0xd779a: fuvtransformsecondary
    0xd403c: fuvtransformunique
    0x65f67: fuvtransformextend
    0x89da2: fdistortion
    0x9f352: fdistortionrefract
    0x180fa: fdistortionrefractmask
    0xd1f1c: fuvdisolvemap
    0xcd11c: fdissolvepatterndither
    0x18faa: fdissolvepatterntexture
    0x62f3b: fdissolve
    0x335c2: fdissolvedither
    0xf7f9d: fdissolvetexture
    0x4b1e4: fdepthtest
    0xe3822: fdepthtestlt
    0xae1e9: fdepthtestgt
    0x2e0f0: fcolormodifier
    0xe92aa: ffinalcombiner
    0xb0db2: ffinalcombinernofog
    0x4073b: fdefaulttransparency
    0x63eac: fuseglobaltransparency
    0xcc033: creatematerialcontext
    0xf55c2: creatematerialcontextex
    0xf4fd: creatematerialcontextexest
    0x3aa5e: fquaternionaxis
    0xcc405: fquaternionmultiplay
    0x6862f: fquaternionrotationarc
    0x3509b: fquaternioninverse
    0xd0071: fpositionrotatequaternion
    0xf062f: frotationnormalfromquaternion
    0x2d495: fquaterniontomatrix
    0x9e3dc: fmatrixtoquaternion
    0x15d0f: fswingadjustposition
    0x17927: fswingadjustpositiondisable
    0x48ad8: fswingadjustnormaltangentdisable
    0x73e6a: fswingadjustnormaltangent
    0x64f1a: fswingdisable
    0x668b4: fswingupdate
    0xe35e: fswingupdateyaxis
    0x8bd12: fswingupdateall
    0xc26fd: fswingupdatebillboard
    0xae6a5: fswingorigindefault
    0x517e5: fswingoriginfromworld
    0x78ae: fswingdefaultviewi
    0x7200e: fswingviewi
    0x1ee3: fswingjointsupportdisable
    0x99edb: fswingjointsupport
    0x90c42: fswingbillboarddisable
    0xff0da: fswingbillboardtransform
    0xc18e4: fswingbillboardtransformfixedy
    0x69658: fswingbillboard
    0x32ae3: fswingbillboardrotation
    0x5bb9b: fswing1weight
    0xda106: fswing2weight
    0x4f7e0: finstancingstreamsourcematrix
    0xd5c02: finstancingconstantmatrix
    0xe44b4: finstancingmultiply
    0x4f148: finstancingmultiplyenable
    0x486eb: finstancing
    0x24010: finstancingenable
    0x68925: ldnormalpackf32
    0x19126: ldnormalunpackf32
    0x3df40: ldidxtotexcoord
    0x5037f: fldtexturesampler3wprev
    0x20de1: fldtexturesampler3wprevxbox
    0x2ba17: flddeformerwithprev
    0x35e57: fldtexturesampler3
    0xeda72: fldtexturesampler3xbox
    0x2b621: flddeformer
    0x5ef90: fldlatticedeformer
    0x742cb: fldtetradeformer
    0xa6ed0: fldtestdeformer
    0x86fd1: fworldmatrix
    0x9e022: fmorph
    0xc2c0f: fmorphposition
    0xc270e: fworldcoordinate
    0x6dddf: fworldcoordinateswing
    0x2a5b6: fworldcoordinatetransformed
    0xb0952: fworldcoordinatelatticedeform
    0x610d0: fworldcoordinatelatticedeformedge
    0xe46f2: fworldcoordinatesymmetry
    0x123f7: fworldcoordinatefromtexture
    0xac7c9: fworldcoordinatefromtexturecalctangnet
    0xff227: fshaderattributes
    0xc000: fshaderattributesvtf
    0x38b30: vs_materialnull
    0x95fc2: ps_materialnull
    0x52968: vs_materialdummy
    0x4408c: ps_materialdummy
    0x6b9f9: vs_dummy
    0x9b07e: ps_dummy
    0x4080: vs_materialdummyedge
    0x8ed37: ps_dummypicker0
    0xfdda1: ps_dummypicker1
    0x68c1b: ps_dummypicker2
    0x1bc8d: ps_dummypicker3
    0xba4f7: ps_dummydynamicpicker
    0x93903: hsv2rgb
    0x66e25: vdunpacku8u8n
    0x5746f: fvdmaskuvtransformoffset
    0x92200: fvdmaskuvtransform
    0x2022a: fvduvtransformoffset
    0xcce95: fvduvtransform
    0x66921: fvduvprimary
    0xd3b2d: fvduvsecondary
    0xeea76: fvduvunique
    0x5f52d: fvduvextend
    0x34230: fuvvertexdisplacement
    0x3486: fvdgetmask
    0xe1293: fvdgetmaskfromtexture
    0x39e22: fvdgetmaskfromao
    0xb3e3f: fvdgetmaskdisable
    0x5e6c5: fvertexdisplacement
    0xd3336: fvertexdisplacementcurveu
    0x4628c: fvertexdisplacementcurvev
    0x69c6b: fvertexdisplacementcurveuv
    0x9ab04: fvertexdisplacementdiru
    0xfabe: fvertexdisplacementdirv
    0x17973: fvertexdisplacementdiruv
    0xbc178: fvertexdisplacementmap
    0xe6016: fvertexdisplacementmapdir
    0x2e6f4: fvtxdispgenwave
    0x3f765: fvertexdisplacementwave
    0xe1ee1: fvertexdisplacementwaverandom
    0x6076f: fvertexdisplacementwaveplus
    0xb8722: fvertexdisplacementdirexplosion
    0xea988: fvertexdisplacementdirexplosionplus
    0xa928e: fdebugviewvertex
    0xbae7: fdebugviewvertexbonemap
    0xb54aa: fdebugviewvertexboneweight
    0xebf32: fdebugviewvertexbonenum
    0x82812: fdebugviewvertexprelight
    0x49cf0: vs_materialdebug
    0x77073: fdebugviewpixel
    0xcd45c: fdebugviewpixeldefault
    0x96449: fdebugviewpixelbasemap
    0x69b78: fdebugviewpixelbasemapalpha
    0x5da1: fdebugviewpixeltangentnormalmap
    0xe5821: fdebugviewpixelworldnormalmap
    0xe4ca7: fdebugviewpixelnormal
    0x8df6b: fdebugviewpixeltangent
    0xbc71d: fdebugviewpixelbinormal
    0xe6393: fdebugviewpixelmaskmap
    0xac53b: fdebugviewpixelprelight
    0x73d77: fdebugviewpixelocclusion
    0x5f514: ps_materialdebug
    0x4706f: ffiltervelocity
    0x40d19: ffiltermotionblursource
    0x13134: ffiltermotionblur8
    0x2b3a3: ffiltermotionblur8median
    0x77d1f: ffiltermotionblur4
    0x2d9d7: ffiltermotionblur4median
    0x29a5c: ffiltermotionblurvelocityblend
    0x99b4f: ffiltermotionblurreductionblend
    0xf9432: deconstructvelocity
    0x58c6b: ffiltermotionblurtilemax
    0x2302a: ffiltermotionblurneighbormax
    0xd166d: depthcompare
    0xed9dc: spreadcompare
    0x7481b: sampleweight
    0x72f1b: ffiltermotionblurreconstruct
    0x39c61: fmaterialvelocitywposnml
    0xaddbd: fmaterialvelocitywposnmlsoftbody
    0xf195d: fmaterialvlocityinflate
    0x4afef: fmaterialvlocityinflateenable
    0x46ae2: vs_materialvelocity
    0xe76be: vs_materialvelocity2
    0xe0009: vs_materialvelocityedge
    0x861f1: ps_materialvelocity
    0xb5d17: tmaterialvelocityedge_nostretch_vs_materialvelocityedge
    0xdd438: tmaterialvelocityedge_stretch_vs_materialvelocityedge
    0xecd99: foutlineblend
    0x84a8d: foutlineblendhdrencode
    0x519f7: foutlineblendadd
    0xca01d: foutlineblendalpha
    0x41f50: foutlineblendmodulate
    0xeadfb: foutlinefade
    0x7cea0: maskoutlinechannel
    0x2c8bd: maskoutlinegeometry
    0x9baf6: foutlinefadedepth
    0xfc6d4: foutlinedetector
    0xf59a7: foutlinedetector0
    0x86931: foutlinedetector1
    0x1388b: foutlinedetector2
    0x6081d: foutlinedetector3
    0x9be24: foutlinedetectorid
    0xb5bf: foutlinedetectordepth
    0xd929f: foutlinedetectordepthwrap
    0x2c964: foutlinecomposite
    0xf5653: foutlinecompositemodulate
    0xa0a70: foutlinecompositeblend
    0xa4090: foutlinecompositeadd
    0xe022d: foutlinecompositemultimodulate
    0x25a88: foutlinecompositemultiblend
    0x4aa1b: foutlinecompositemultiadd
    0x179e8: foutlinesample
    0xadf86: foutlinesample4
    0x4790f: foutlinesample12
    0x52c9: ffilteroutlinethick
    0x8186c: ffilteroutlinethick1v
    0x7250f: ffilteroutlinethick1h
    0x54baf: ffilteroutlinethick2v
    0xa76cc: ffilteroutlinethick2h
    0x22f25: ffilteroutlineblur
    0x8a01c: ffilteroutlineblur1h
    0x79d7f: ffilteroutlineblur1v
    0x5f3df: ffilteroutlineblur2h
    0xacebc: ffilteroutlineblur2v
    0x161e1: ffilteroutlinesample
    0xca88c: ffilteroutlinecomposite
    0x8386f: ffilteroutlinecompositebloomf
    0xe8242: ffilteroutlinecompositeemit
    0x59ea0: ffilteroutlinesamplecomposite
    0x16b0b: ffilteroutlinedetector
    0xd026c: ffilteroutlinedirect
    0xd92a4: vs_materialoutline
    0x12e21: ps_materialoutline
    0x260f0: ps_materialoutline2
    0x360e1: fshadowreceivefaceattn
    0xff2ce: fshadowreceivefaceattnincrease
    0xdb3e5: fshadowreceivefaceattndecrease
    0x4ca2c: fshadowreceivefaceattncut
    0x8187a: fshadowreceiveattn
    0x94b58: fshadowreceiveattnfade
    0x8f6c: fshadowreceiveattnviewdistance
    0xc6bf7: fshadowreceiveattndistance
    0x1990d: fshadowreceiveattndistancefade
    0xedc8b: fshadowreceiveattnspot
    0x80e45: fshadowreceiveattnspotfade
    0x4d27d: fshadowisoutofrange
    0xd2179: fshadowisoutofrangeenable
    0xe9ec4: sampledepth
    0xa9231: sampledepthcomp
    0x4d364: samplevariance
    0xdec9d: samplelevelvariance
    0x51056: fshadowfilter
    0xbe09e: calcpcf2x2
    0x858ec: fshadowfilterpcf2x2
    0x1f8a: fshadowfilterpcf2x2comp
    0xeba3f: calcpcf3x3
    0xd024d: fshadowfilterpcf3x3
    0x73d8e: fshadowfilterpcf3x3comp
    0x53919: calcpcf4x4
    0x6816b: fshadowfilterpcf4x4
    0xdf10: fshadowfilterpcf4x4comp
    0x6f61a: calcpmax
    0x4c59a: fshadowfiltervsm
    0x27820: fshadowfiltervlsm
    0xa8287: filtercascadevssm
    0x66ca: filtercascadevlsm
    0x4bdab: getcubetexturecordinate
    0xf45c2: fshadowfilterpoint
    0xa7410: fshadowfilterpointpcf2x2
    0xf2eb1: fshadowfilterpointpcf3x3
    0x4ad97: fshadowfilterpointpcf4x4
    0xcc411: fshadowfilterpointvsm
    0x765c6: fshadowlightface
    0x2da0e: fshadowlightfacepoint
    0x2499e: vs_shadowreceive
    0xa97eb: fshadowreceive
    0xada61: fshadowreceivert
    0x4b2d4: fshadowreceivecascadessm
    0xb1b4: fshadowreceivecascadessmrt
    0x1b35c: fshadowreceivecascadessmlite
    0x5398c: fshadowreceivecascadessmrtlite
    0x25edb: fshadowreceivesmoothcascadessm
    0x4539e: fshadowreceivesmoothcascadessmrt
    0xed204: fshadowreceivesmoothcascadessmlite
    0x29e71: fshadowreceivesmoothcascadessmrtlite
    0x61e84: fshadowreceivelsm
    0xba101: fshadowreceivelsmrt
    0xe5699: fshadowreceivecascadelsm
    0xb1e7: fshadowreceivecascadelsmrt
    0x8ba96: fshadowreceivesmoothcascadelsm
    0x453cd: fshadowreceivesmoothcascadelsmrt
    0x5d0bf: fshadowreceivecascadevssm
    0x5a01d: fshadowreceivecascadevssmrt
    0xf34f2: fshadowreceivecascadevlsm
    0x5a04e: fshadowreceivecascadevlsmrt
    0x313b9: fshadowreceivespotvsm
    0x2f257: fshadowreceivespotvsmrt
    0xf2b90: fshadowreceivepoint
    0x3207a: ps_shadowreceive
    0x5e765: ps_shadowreceivetransparent
    0x67a11: getmaterialshadowrt
    0x6e49a: flightmaskrtsolid0
    0x1d40c: flightmaskrtsolid1
    0xb9fe2: flightmaskrttransparent0
    0xcaf74: flightmaskrttransparent1
    0x5a65a: vs_shadowreceivedeferredrectangle
    0xac470: ps_shadowreceivedeferredrectangle
    0x12fc4: fparaboloidprojection
    0x9b0c8: vs_dualparaboloid
    0xd07c0: ps_dualparaboloid
    0x240b2: fdeferredlightingencodeparameter
    0xa2c95: fdeferredlightingencodeparameterhalflambert
    0xbece2: fdeferredlightingencodeparameteroverlap
    0x7292: fdeferredlightingencodeparametermrt
    0x4ddf4: fdeferredlightingencodeparametermrthalflambert
    0x1a0b7: fdeferredlightingdecodeparameter
    0x1afe6: fdeferredlightingdecodeparameterhalflambert
    0x69157: fdeferredlightinggetlightparam
    0x407f9: fdeferredlightinggetlightparamfadeout
    0xfafde: fbrdfdeferredlighting
    0x57bea: fdynamiclightingdeferredlighting
    0x5bcba: fdeferredlightinglightvolumelightmask
    0x23f6b: fdeferredlightinglightvolumelightmasksolid0
    0x50ffd: fdeferredlightinglightvolumelightmasksolid1
    0xbfad5: fdeferredlightinglightvolumelightmasksolid01
    0xf3c5b: fdeferredlightinglightvolumelightmasktransparentfullsize
    0x20e44: fdeferredlightinglightvolumelightmasktransparentquartersize
    0xd1697: fdeferredlightinglightvolumelightmasktransparent0
    0xa2601: fdeferredlightinglightvolumelightmasktransparent1
    0xb7bcb: fdeferredlightinglightvolumelightmasktransparent01
    0xc2822: fdeferredlightinglightvolumelightmaskrtsolid0
    0xb18b4: fdeferredlightinglightvolumelightmaskrtsolid1
    0xcb3f3: fdeferredlightingcompareequallightgroup
    0xce9a3: fdeferredlightingcompareequallightgroupdisable
    0xcefdc: freconstructviewdepthfromdepth
    0xff182: freconstructviewdepthfromlineardepth
    0x1522e: freconstructworldposition
    0x42482: freconstructworldpositiondualpalaboloid
    0xf8d45: fdepthboundstest
    0xc7569: fdepthboundstestenable
    0x69ac6: fbumpmapfromgbuffer
    0xd2afd: fdeferredlightinggetlightingparameter
    0xaf71: fdeferredlightinggetlightingresult
    0x1a2c5: vs_deferredlighting_lightvolume
    0x274ae: vs_deferredlighting_lightvolumerectangle
    0x1e162: ps_deferredlighting_lightvolume_nolighting
    0x255ba: ps_deferredlighting_lightvolume_nolighting_mrt
    0xd38c: ps_deferredlighting_lightvolume_nolighting_lightgroup
    0xd2ddc: ps_deferredlighting_lightvolume_nolighting_lightgroup_mrt
    0x1d023: ps_deferredlighting_lightvolume
    0x25a69: ps_deferredlighting_lightvolume_mrt
    0xf4237: fdeferredlightingencodeoutputlog
    0x188a8: fambientmask
    0x51533: fambientmaskenable
    0x4d7b: fencodersmparameter
    0x8ef80: fdecodersmparameter
    0x72e97: frsmcomputeindirectlighting
    0xfbf4e: frsmgatherindirectlighting
    0x9783c: frsmgatherindirectlightinglargesize
    0xf378a: frsmgatherindirectlightinghighquality
    0x48c44: frsmgatherindirectlightingvariable
    0x1991b: frsmgetindirectlighting
    0x123ee: ps_deferredlighting_indirectlighting
    0x8eb5: ps_deferredlighting_gbufferreduction
    0x3f38a: ps_deferredlighting_bilateralblurh_size8
    0xc7304: ps_deferredlighting_bilateralblurh_size12
    0x1b71d: ps_deferredlighting_bilateralblurh_size16
    0x21419: ps_deferredlighting_bilateralblurv_size8
    0xd501d: ps_deferredlighting_bilateralblurv_size12
    0x9404: ps_deferredlighting_bilateralblurv_size16
    0x7fa35: ps_deferredlighting_bilateralupsampling
    0x257df: ps_deferredlighting_bilinearupsampling
    0x79ffd: vs_materialstd
    0x5d44b: ps_materialstd
    0x9ba69: ps_deferredlighting_gbufferpass
    0x35898: ps_deferredlighting_gbufferpassmrt
    0xc809d: ps_reflectiveshadowmap
    0x3f1fd: vs_adhesion
    0x35f81: doadhesioneachlighting
    0x55cfa: doadhesiondynamiclighting
    0x9fe33: fadhesionalbedo
    0x47799: fadhesionalbedosubtract
    0x63bbe: ps_adhesion
    0xb560c: vs_adhesionpv
    0xe89d1: ps_adhesionpv
    0x4c713: fsssirradiance
    0x69eb7: fsssfillmarginh
    0x9a3d4: fsssfillmarginv
    0x629ec: fsssgaussianfilterh
    0x9148f: fsssgaussianfilterv
    0xdc321: ps_materialsss
    0x7cac4: ps_materialsssirradiance
    0x85fd3: ps_materialsssdistortion
    0x672ad: vs_materialstdest
    0x2c5a5: ps_materialstdest
    0x13c0b: ps_deferredlighting_gbufferpassest
    0x98f25: ps_deferredlighting_gbufferpassmrtest
    0x23f86: ps_reflectiveshadowmapest
    0xe8e83: vs_modelfog
    0xb44c0: ps_modelfog
    0x66993: vs_materialconstant
    0xa6280: ps_materialconstant
    0x3bf5f: getadaptivefactor
    0x32645: hs_pntrianglesconstant
    0xe956d: hs_materialpn
    0x42c96: ds_materialpn
    0xf9ac0: hs_phtrianglesconstant
    0xd3058: hs_materialph
    0x789a3: ds_materialph
    0xfcdcf: hs_dmtrianglesconstant
    0x91382: hs_materialdm
    0x3aa79: ds_materialdm
    0xbcd50: vs_materialstdcafetes
    0x4d0b2: fshadowbias
    0xed98e: fshadowdepthbias
    0xa9708: fshadowbiasdisable
    0x96e6f: vs_shadowcast
    0xb031f: fshadowcast
    0xe42a5: fshadowcastdepth
    0xbe2b0: fshadowcastdistance
    0xcb1b2: ps_shadowcast
    0xeb4a9: ps_shadowcasttransparent
    0x95250: ps_shadowcastzoffset
    0xbeed1: ps_shadowcasttransparentzoffset
    0xef9ff: fshadowisoutofrange0
    0x9c969: fshadowisoutofrange1
    0x98d3: fshadowisoutofrange2
    0x7a845: fshadowisoutofrange3
    0xa904c: fshadowlightface0
    0xda0da: fshadowlightface1
    0x4f160: fshadowlightface2
    0x3c1f6: fshadowlightface3
    0xda122: fshadowreceivefaceattn0
    0xa91b4: fshadowreceivefaceattn1
    0x3c00e: fshadowreceivefaceattn2
    0x4f098: fshadowreceivefaceattn3
    0x8f096: fshadowreceiveattn0
    0xfc000: fshadowreceiveattn1
    0x691ba: fshadowreceiveattn2
    0x1a12c: fshadowreceiveattn3
    0xb0bb8: fshadowreceivert0
    0xc3b2e: fshadowreceivert1
    0x56a94: fshadowreceivert2
    0x25a02: fshadowreceivert3
    0xbd17d: fshadowfilter0
    0xce1eb: fshadowfilter1
    0x5b051: fshadowfilter2
    0x280c7: fshadowfilter3
    0x5dc75: fshadowfilterpoint0
    0x2ece3: fshadowfilterpoint1
    0xbbd59: fshadowfilterpoint2
    0xc8dcf: fshadowfilterpoint3
    0xbf5e3: fshadowfiltermulti
    0xb329d: fshadowfilterpointmulti
    0x56a59: fshadowmultiplereceivert
    0xe2c23: fshadowmultireceivecascadessmrt
    0xd2da3: fshadowmultireceivesmoothcascadessmrt
    0x682e1: fshadowmultireceivelsmrt
    0xe2c70: fshadowmultireceivecascadelsmrt
    0xd2df0: fshadowmultireceivesmoothcascadelsmrt
    0x1f5d2: fshadowmultireceivespotvsmrt
    0x20870: fshadowmultireceivepoint
    0x6ae3d: flightmaskshadowmultirt0
    0x19eab: flightmaskshadowmultirt1
    0xd4a85: flightmaskshadowmultirt01
    0xaf972: fgaussianfilterh
    0x5c411: fgaussianfilterv
    0xddf19: fintensityweight
    0xe0db9: fintensityweightgrayscale
    0xcbd42: fintensityweightrgb
    0x7dd07: fintensityweightrgba
    0x9b576: fdispersionmap
    0xfdd78: fbilateralfilterh
    0xe01b: fbilateralfilterv
    0x79aab: convzvalue
    0x7ac11: fclampsceneuv
    0x9f126: fclampsceneuvclip
    0x92205: fclampsceneuvsmooth
    0x7969d: fprimitivesample
    0x90f67: fprimitivesamplenotexture
    0x309bf: fprimitivesamplebasemap
    0xc5c9b: fprimitivesamplebasemapparalax
    0x328b0: fprimitivesamplebasemaplin
    0x833ef: fprimitivesamplebasemapparalaxlin
    0x21006: fprimitivesamplealphamap
    0x6188f: fprimitivesamplealphamappoint
    0x68560: fprimitivesamplealphamapparallaxpoint
    0x7351c: fprimitivesamplealphamaplin
    0x73a75: fprimitivesamplealphamapparallaxlin
    0x6ab1d: fprimitiveocclusionsphere
    0xee836: fprimitiveocclusionlensflare
    0x7219a: fprimitiveocclusionfactor
    0xeabd6: fprimitiveocclusionfactordefault
    0x9ef69: fprimitiveocclusionfactoroccmap
    0xebe13: fprimitiveocclusionfactorps
    0xab745: fprimitivepsocclusion
    0x1ffe8: fprimitivepsocclusiondefault
    0xbdb59: fprimitivecoltexinfluence
    0x72e14: fprimitivecoltexinfluencedefault
    0x5463c: fprimitivecoltexinfluencetexrgbcola
    0x72458: fprimitivecalccolorint
    0x96d71: fprimitivecalccolorintdefault
    0x2a876: fprimitivecalcintensity
    0x9da92: fprimitivecalcintensitydefault
    0x3849d: fprimitivecalcfresnel
    0x44de4: fprimitivecalcfresneldefault
    0x568cf: fprimitivescenesampler
    0x48295: fprimitivescenesamplerblur
    0x56fd7: fprimitivescenesamplerblurnotex
    0xf9a81: fprimitivescenesamplerrefract
    0x76483: fprimitivescenesamplerrefractnotex
    0x5e4c6: fprimitivescenesamplerrefractz
    0x6d45: fprimitivescenesamplerrefractzblur
    0x746d2: fprimitivescenesamplerrefractznotex
    0x3f677: fprimitivescenesamplerrefractzblurnotex
    0xf09e: fprimitivescenesamplerdistortion
    0x958ca: fprimitivescenesamplerdistortionnotex
    0x67203: fprimitivetonemap
    0x537e: fprimitivetonemapnone
    0x5ee6e: fprimitivemaskmap
    0x33a48: fprimitivemaskmapdefault
    0xf46d8: fprimitivemaskmapparallax
    0xd12e2: fprimitivecalcnormalmap
    0xe7117: fprimitivecalcnormalmapdefault
    0x847f6: fprimitivecalcnormalmapparallax
    0xb506: fprimitivecalcnormalmapmask
    0xfe61f: fprimitiveclip
    0xfd5ea: fprimitiveclipdefault
    0xfe190: fprimitivevsalphaclip
    0xb0932: fprimitivevsalphaclipdefault
    0xb36e: fprimitivealphatocolor
    0xa2887: fprimitivealphatocolordefault
    0x88784: fprimitiveuvoffset
    0xd16c6: fprimitiveuvoffsetdefault
    0xe2cac: fprimitivemodelscenesampler
    0x55048: fprimitivemodelscenesamplerblur
    0xbbd9: fprimitivemodelscenesamplerrefract
    0xead99: fprimitivemodelscenesamplerrefractalpha
    0xd633d: fprimitivemodelscenesamplerrefractdisplaceuv
    0x7c075: fprimitivemodelsmoothalpha
    0xdebb2: fprimitivemodelsmoothalphadefault
    0xa428d: fprimitivemodelsmoothalphainverse
    0x70250: fprimitivemodelsmoothalphavertexnormal
    0x18ba1: fprimitivemodelsmoothalphavertexnormalinverse
    0x42c02: fprimitivetransparency
    0x9ff11: fprimitivetransparencyvolume
    0x2db03: fprimitivelevelcorrection
    0x13cc7: fprimitivelevelcorrectionlinear
    0xaab69: fprimitivelevelcorrectionneg
    0x719e4: fprimitivelevelcorrectionpos
    0x4aa01: fprimitivelevelcorrectionalphalinear
    0x8442e: fprimitivelevelcorrectionalphaneg
    0x5f6a3: fprimitivelevelcorrectionalphapos
    0x8a9f: fblendfogprimalpha
    0xdc2dd: fblendfogprimblend
    0x9e920: fprimitevecolormodifier
    0x181e9: focclusionfactorfilter
    0xcfc44: ffocclusionfactor
    0xc5b36: ffocclusionfactorfromtexture
    0x602a0: fradialfiltersamplecolorscale
    0xbdd2c: fradialfiltersamplecolorscalefade
    0x5c42e: fradialfiltermask
    0x3fa1c: fradialfiltermaskdisable
    0x6c183: fradialfilteralpha
    0x55296: fradialfilteralphacolor
    0x50b1a: fradialblurwidth
    0x9ca74: fradialblurwidthocclusion
    0xf775f: fradialbluralpha
    0x1a5f8: fradialbluralphaocclusion
    0xb53a4: vs_radialblurfilter
    0x758b7: ps_radialblurfilter
    0x93155: ffeedbackblurfilter
    0xb1253: vs_tvnoisefilter
    0xa7bb7: ps_tvnoisefilter
    0x778fa: ftvnoisefilterscanline
    0xba89d: ffisheye
    0xb157: ffiltercolorcorrect
    0xbab81: ffiltercolorcorrecttable
    0x272fe: ffiltercolorcorrectvolumeinterpolatehq
    0xef754: ffiltercolorcorrectvolumeinterpolate
    0x9c764: ffiltercolorcorrectvolume
    0x31ad3: ffiltercolorcorrectvolumesrgb
    0x53495: ffiltercolorcorrectvolumeinterpolateblend
    0x72db5: ffiltercolorcorrectvolumeblend
    0x13a76: ffiltercolorcorrectvolumesrgbblend
    0x7d40d: ffilterhermitetonecurve
    0xd6d5b: fvariancefilter
    0xa7887: fcubemapvariancefilter
    0xd209e: fcubemapvariancefilterdir
    0x5ecb3: fvariancefilterh
    0xad1d0: fvariancefilterv
    0x898b2: fvariancefiltercubedirh
    0xd2a8b: fvariancefiltercubeh
    0x7a5d1: fvariancefiltercubedirv
    0x217e8: fvariancefiltercubev
    0x753ad: fvariancemakemiplevel
    0x10536: fvariancemakemiplevelcube
    0x32036: vs_variancefilter
    0x7973e: ps_variancefilter
    0x97a5f: vs_cubemapvariancefilter
    0x4280f: ps_cubemapvariancefilter
    0x3d2c2: fdepthtovariance
    0x59b2c: ps_bloomfinalout
    0xf392c: ps_bloomextraction
    0x417bf: ps_bloomextractionctr
    0x7f59b: ps_bloomdownsample4
    0x1ead7: vs_bloomconeblur
    0xbbb02: vs_bloomgaussblur
    0xf0c0a: ps_bloomgaussblur
    0x8333: ps_bloomconeblur
    0x80078: ps_bloomgather
    0x479: fbaselightscattering
    0xf00a1: ffoglightscattering
    0xc3647: ffogvtflightscattering
    0xb6750: ffilterlightscatteringmul
    0x5db48: ffilterlightscatteringmulrc
    0x33516: ffilterlightscatteringadd
    0x78aad: ffilterlightscattering
    0x132b0: fimageblend
    0x525d5: fimageblendscreen
    0x1cc80: fimageblendoverlay
    0x112bf: fimageblendsoftlight
    0x96667: fimageblendhardlight
    0xa6763: fimageblenddodge
    0xda258: fimageblendburn
    0x8699c: fimageblenddarken
    0x730c3: fimageblendlighten
    0x4f6e6: fimageblenddifference
    0x919c: fimageblendexclusion
    0x23413: vs_imageplanefilter
    0x9cce6: ps_imageplanefilterbase
    0x3833f: ps_imageplanefiltercube
    0x64c46: ps_imageplanefilterbaseex
    0xf9e5b: ps_imageplanefiltercubeex
    0x46443: ffilterhaze
    0x834ff: ffilterhazeinverse
    0x19665: ffilterhazedepth
    0x26e93: ftonemaplinear
    0x2304d: ftonemapexposure
    0xec1c8: ftonemapexposureex
    0xecb08: ftonemapreinhard
    0x11225: vs_avgloginit
    0xcef8b: vs_avglog16
    0x925c8: ps_avglog16
    0x85c69: ps_avglogfinal
    0x4cdf8: ps_avgloginit
    0xc83bc: ps_averagecount
    0x2d7b0: ffiltercolorfog
    0xd1bd3: ffiltercolorfogheight
    0x33138: vs_cubicblur
    0xe94d8: ps_cubicblur
    0xb0c3: vs_cubicblend
    0x56f1e: ps_cubicblend
    0xc4beb: fdoffilterdownscale
    0x60f70: correctdepthsub
    0xcaad8: fdoffilterpoisson
    0x42759: fdoffilterlight
    0xffcf7: fdoffilterlight2
    0xef51f: fgsdofcopy
    0x9077: vs_gsdoffilter
    0xd4d6d: gs_gsdoffilter
    0x2dbc1: ps_gsdoffilter
    0x138d6: fssaofilterdepthdownscale
    0xd8e2d: fssaofilterlineardepthdownscale
    0x5c230: fssaofiltermakelineardepth
    0x7b79c: vs_ssaomakenormal
    0x30094: ps_ssaomakenormal
    0x319f5: vs_ssaomakeocclusionmap
    0xf4a68: fssaobounce
    0x961b8: fssaobouncedisable
    0x99f62: getintensitybothfaces
    0x1b77b: getintensitysingleface
    0x512bf: fssaointensitydisable
    0x21f: getbiasedviewposition
    0x7913a: getoccludermatrix
    0xe5955: getscaleoffset
    0x96b8f: ps_ssaomakeocclusionmap
    0x939c1: ps_ssaomakesinglefaceocclusionmap
    0x7cb3d: fssaoapplyambientocclusion
    0xaf755: fssaoapplyindirectbounce
    0xbb7bc: fbokehalpha
    0xc22fb: fbokehcompressfactor
    0x85631: fbokehcompressrangefactor
    0x7b7ee: fbokehbleeding
    0x91bf3: fbokehantibleeding
    0xd7090: fbokehmask
    0x23b63: fbokehmaskdither
    0x4e727: fbokehreductionblend
    0x7077f: fbokehnearcopy
    0x253fc: fbokehinflatemask
    0x1282f: fbokehmaskvalue
    0x56a09: fbokehinversemaskvalue
    0x89867: fbokehantibleedingmaskvalue
    0x68972: fbokehantibleedinginversemaskvalue
    0x1196d: fbokehcalculation
    0x3c0be: fbokehdefaultfarz
    0x70a6c: fbokehreductionfarz
    0xe397a: fbokehfarfilter
    0x8ba48: fbokehnearfilter
    0xc717: ffilteredgeantialiasinggetdepth
    0x2e65a: ffilteredgeantialiasinggetedgeweight
    0x466d3: ffilteredgeantialiasinggetedgeweightfast
    0xf07a0: ffilteredgeantialiasing
    0x7ca01: ffilteredgeantialiasingdynamicbranch
    0xd0799: ffilteredgeantialiasingoutputweight
    0xf5d2c: ffiltergodraysalpha
    0x45115: ffiltergodraysalphaocclusion
    0x941c2: ffiltergodraysscale
    0x70e8a: ffiltergodraysscaleocclusion
    0xe82aa: ffiltergodrayssourcecolor
    0xcec1a: ffiltergodrayssourcegraycolor
    0xe79be: ffiltergodraysthreshold
    0x27aa0: ffiltergodraysthresholdwithz
    0x12ced: ffiltergodraysthreshold3dboundmaskweightzero
    0xa5c8d: ffiltergodraysthreshold3dbound
    0xe373: fgodraysdirection
    0x966ca: ffiltergodraysiteratorsc
    0x2156e: ffiltergodraysblend
    0x39a90: ffiltergodraysp2o
    0x17328: ffiltergodrayso2p
    0xaf153: ffiltergodraysbegin
    0xc38f8: ffiltergodrays16samplesiterator
    0xab85d: ffiltergodrays8samplesiterator
    0x936e8: ffiltergodrayscopy
    0xbaf32: ffiltergodraysgammacopy
    0xddef1: fblurdistancemask
    0xd182c: fblurdistancemaskenable
    0x68641: fbluralphamask
    0x7dc90: fbluralphamaskenable
    0xc72ab: fblurmaskfilter
    0x3cf24: fblurmaskcopycolor
    0xd5ebe: fcafisheye
    0x3acfb: fcanormalmap
    0x3db34: fchromaticaberrationfilter
    0x7dcc7: fchromaticaberrationfilterhq
    0x1847f: fchromaticaberrationfilterdownsample
    0x2426f: vs_tangentfilter
    0x6d720: ps_tangentfilter_blur4
    0x9b0b: ps_tangentfilter_blur8
    0xa6f71: ftangentmodifier
    0xfb7fe: nulllighttexture
    0x25de: spotlighttexture
    0x69cc2: pointlighttexture
    0x7618e: spotpointlighttexture
    0xb2191: fbruteforcelighting
    0x4d71a: fbruteforcelightingnulllighttexture
    0x7a5b5: fbruteforceapproximatelighting
    0x91a61: calcscreenztoviewdepth
    0xc8da1: calcscreenuvtoviewdepth
    0x1a46: calcfog
    0xc3985: fprimitivecalctexcoord
    0x6484a: fprimitivecalctexcoordnormalize
    0x3d89b: fprimitivecalctexcoordtexel
    0x9dc30: calczoffset
    0xaf198: fprimitivecalcpos
    0xb636f: fprimitivecalcposparticle
    0x26087: fprimitivecalcposparticlent
    0x7a80e: fprimitivecalcpospolyline
    0x6faa7: fprimitivecalcposcloudbillboard
    0x5a1db: fprimitivecalcposcloud
    0xfb0c5: fprimitivecalcdepthblend
    0xfec75: fprimitivecalcdepthblenddefault
    0x1835b: fprimitivecalcvolumeblend
    0x46b62: fprimitivecalcvolumeblenddefault
    0x7705e: fprimitivecalcvolumeblendps
    0xb7e4f: fprimitivecalcvolumeblendpsvolume
    0xf1900: fprimitivecalcvolumeblendpsinvvolume
    0x1a020: fprimitivecalcvolumeblendpsdepthvolume
    0xa939d: fprimitivecalcposvolumeblenddepthvolume
    0x37b44: fprimitivecalcposvolumeblenddepthvolumedefault
    0xbfa27: fprimitivecalcfog
    0xc87c7: fprimitivecalcfogcolor
    0xaf644: fprimitivecalcfogalpha
    0x7be06: fprimitivecalcfogblend
    0x47e36: fprimitivecalcfogps
    0x8a2bb: fprimitivecalcfogpsdefault
    0xe44a1: fprimitivecalcshade
    0x84a67: fprimitivecalcshadecolor
    0xaf54f: fprimitivecalcshadecolorratio
    0xb9085: fprimitivecalceye
    0x363d2: fprimitivecalceyedefault
    0xe90e0: fprimitivecalcntb
    0x4b753: fprimitivecalcntbpolygon
    0x221fc: fprimitivecalcntbparticle
    0xeea9d: fprimitivecalcntbpolyline
    0xc887d: fprimitivecalcntbtessparticle
    0xdfb73: fprimitivecalcdiffuse
    0x8c0f6: fprimitivecalcdiffusenormalmap
    0xf7b65: fprimitiveuvclamp
    0x5c0a8: fprimitiveuvclampdefault
    0x55759: fprimitiveparallax
    0x5e445: fprimitiveparallaxdefault
    0x68129: fprimitiveparallaxscale
    0x516ac: fprimitiveparallaxscaledefault
    0xf40d5: fprimitivecalcspecular
    0xb268c: fprimitivecalcspeculardefault
    0xd7d26: fprimitivedepthcomparison
    0x25c07: fprimitivedepthcomparisonenable
    0x6441e: fprimitivecloudenv
    0xd65b3: fprimitivecloudenvdefault
    0x3936b: fprimitivecloudcolor
    0xe3689: fprimitivecloudcolordefault
    0x3b76f: fprimitivetessellate
    0xe2a78: fprimitivetessellateparticle
    0x8fb4a: vs_primitive
    0x55eaa: ps_primitive
    0xa5d61: vs_cloudprimitive
    0xeea69: ps_cloudprimitive
    0x6352b: vs_primitivetessellate
    0x8092: primitiveconsths
    0x303ea: hs_primitivetessellate
    0x1b6ea: ds_primitivetessellate
    0x76fab: ps_primitivetessellate
    0x2966d: calczoffset2d
    0xb43ba: fprimitive2dvirtualscreen
    0xf9955: fprimitive2dvirtualscreenfullscreen
    0xbce5d: fprimitive2dvirtualscreenpanscan
    0x3b57: fprimitive2dvirtualscreenletterbox
    0x45c10: fprimitive2dcalcpos
    0xbd7c0: fprimitive2dcalcpospolyline
    0x68286: fprimitive2dcalcpossprite
    0xe976e: fprimitive2dcalcposlensflare
    0x17a6e: fprimitive2dcalctexcoord
    0x50df8: fprimitive2dcalctexcoordnormalize
    0x75ca: fprimitive2dcalctexcoordtexel
    0x4da3f: fprimitive2dlensflareintensity
    0xc7d28: fprimitive2dlensflareintensitydefault
    0x8e66b: vs_primitive2d
    0xaaddd: ps_primitive2d
    0x26b0e: fwaterwposprot
    0x705c4: fwaterwposprotfrommodel
    0x28d71: fwaterunitprot
    0x65879: fwaterunitprotfrommodel
    0x66db6: calcwavephase
    0x14cb8: calcwaveheight
    0x896fd: calcwaveplane
    0x5cff6: fwaterdetailcoodinate
    0xf0914: fwaterdetailworldcoodinate
    0xf1c5e: fwaterdetailtexturecoodinate
    0xdb41d: fwaterripple
    0xf1bdd: fwaterripplefrustum
    0x16cf0: fwaterrippledisable
    0xcbd1c: fwaternormal
    0xaa047: fwaterdetailnormal
    0xf46e8: fwaterdetailnormalmulti
    0xbcf4: calcfluctuation
    0x87593: fwatercaustics
    0x9c693: fwatercausticsdisable
    0xa3ee5: fwatercausticsfilter
    0xb3aef: fwaterreflection
    0x6400a: fwaterreflectionenvironmentmap
    0xb9f6a: fwaterrefraction
    0x3bf19: fwaterrefractionscene
    0x900dd: fwaterrefractionocean
    0xe27fc: fwaterbubblecoordinate
    0x54b8e: fwaterbubbleworldcoordinate
    0x16553: fwaterbubbletexturecoordinate
    0x1b889: getbubblecolor
    0x267f8: fwaterbubblemask
    0xe76a0: fwaterbubblemapmask
    0x9240f: fwaterbubble
    0x447b1: fwaterbubblenormal
    0x9a4c2: fwaterbubbledepth
    0xcca5a: fwaterbubbleheight
    0xf57d5: fwatershadow
    0xcc910: fwatershadowdisable
    0xf87ff: fwatervolumeblend
    0xd5386: fwatervolumeblenddisable
    0x7f3e5: fwatertransform
    0xada81: waterwindeffect
    0x971c0: fwaterwindtransform
    0x4a85b: fwatertransformvtf
    0x15f1c: vs_water
    0xe569b: ps_water
    0x8466a: vs_watermask
    0x5e38a: ps_watermask
    0x33edd: fwatercombiner
    0xd2878: vs_watershadowmap
    0x99f70: ps_watershadowmap
    0x114ca: fwatershadowface
    0x33e10: fwatershadowreceivecascadelsm
    0x8161a: fwatershadowreceivesinglelsm
    0xab570: fwatershadowreceive
    0xc5da6: encoderippleheight
    0x4ff5d: decoderippleheight
    0xb074c: vs_waterripple
    0x94cfa: ps_waterripple
    0x43252: fwaterheight2normal
    0xc3216: vs_waterwposb
    0x9edcb: ps_waterwposb
    0xb4dcd: fguicalcposition
    0x841dd: fguicalcposition2d
    0x3709c: fguicalcposition3d
    0xd8320: fguicalcpositiondev
    0x4bacd: fguicalcpositiondev2d
    0xf8b8c: fguicalcpositiondev3d
    0xc0585: fguicalcuv
    0xf6ee2: fguicalcuvwrap
    0x40f4: fguicalcuvclamp
    0x774a2: fguicalcuvalphamask
    0x237fc: fguicalcuvalphamaskon
    0xcc20b: fguigetvertexcolor
    0x46884: fguigetvertexcolorstatic
    0x5078e: fguicalccolorscaling
    0xfd886: fguicalccolorscalingon
    0x9a4d7: fguicalccolorattribute
    0x9cb55: fguicalccolorattributeon
    0x2cf62: fguicalccoloralphamask
    0x128b0: fguicalccoloralphamaskwrite
    0x5def0: fguicalccoloralphamaskapply
    0x3a00a: fguicalccolor
    0xf1cff: fguitexturesampling
    0xe4a77: vs_gui_polygon
    0xc6617: vs_gui_texture
    0xf1049: vs_gui_blend
    0xb64d7: vs_gui_dev
    0xc01c1: ps_gui_polygon
    0xe2da1: ps_gui_texture
    0x2b5a9: ps_gui_blend
    0x51490: ps_gui_dev
    0x30313: fdegamma
    0x6ac91: fdegammadesable
    0xd0700: fyuvdecoder
    0x1af6: fprojectiontexturecolor
    0x667eb: fprojectiontexturecolorr
    0xb8300: fprojectiontexturecolorg
    0x1778f: fprojectiontexturecolorb
    0x82635: fprojectiontexturecolora
    0x41119: getprojectiontexture
    0xd8b7a: fprojectiontexture
    0xa548: vs_textureblend
    0xa71ba: ps_textureblend
    0x94af6: ps_textureblendcube
    0xcc589: convrot
    0x27838: fgpuparticlecalcpos
    0x58491: fgpuparticlecalcposparticle
    0x192b0: fgpuparticlecalcposlineparticle
    0x35c88: fgpuparticlecalcpospolylineparticle
    0x2d29d: fgpuparticleintensity
    0x5e1f9: fgpuparticleintensitydefault
    0x4e2e1: fgpuparticlecalctexcoord
    0xa1dd8: fgpuparticlecalctexcoordnone
    0xfe9fd: fgpuparticlecalctexcoorddefault
    0x36b00: fgpuparticlecalctexcoordpolyline
    0x11752: fgpuparticlesample
    0x7e899: fgpuparticlesamplenotexture
    0xcb425: fgpuparticlesamplebasemap
    0x8894c: fgpuparticlesamplebasemaplin
    0xefba3: fgpuparticletonemap
    0x1727: fgpuparticletonemapdefault
    0xcfceb: fgpuparticletonemapnone
    0xf9522: fgpuparticlecalcdepthblend
    0x31448: fgpuparticlecalcdepthblendnone
    0x690e6: fgpuparticlecalcdepthblenddefault
    0x30f6f: fgpuparticlefogvs
    0x94fc4: fgpuparticlefogvscolor
    0xf3e47: fgpuparticlefogvsalpha
    0x27605: fgpuparticlefogvsblend
    0x9a8e9: fgpuparticlefogps
    0x34d39: fgpuparticlefogpsdefault
    0x34e05: fgpuparticlevsalphaclip
    0x36ec6: fgpuparticlevsalphaclipdefault
    0x48c5b: fgpuparticlelevelcorrection
    0xc2431: fgpuparticlelevelcorrectionlinear
    0x43997: fgpuparticlelevelcorrectionneg
    0x98b1a: fgpuparticlelevelcorrectionpos
    0xcb561: vs_gpuparticle
    0x5cfb: vs_gpuparticle2
    0x111f9: calcpos
    0x1687b: gs_gpuparticle
    0xefed7: ps_gpuparticle
    0xe760d: vs_lightshaft
    0x8026d: calclightshaftsearchlength
    0xba9d0: ps_lightshaft
    0xfb1bd: fmarkpoint
    0xd2ff3: fmarkline
    0x7a78c: fmarklooppoint
    0x1300b: fmarkloopline
    0xdec2b: fmarkdisable
    0xc2758: fmark
    0xec675: fgrassmaterialnormal
    0xa9507: fgrassinput
    0x3a706: fgrasscompressedinput
    0x2635e: fgrassposition
    0xffe1a: fgrassbillboardposition
    0x64d6b: fgrasschainposition
    0x2d697: fgrassuv
    0x73448: fgrassbillboarduv
    0x7fb36: fgrasschainuv
    0x7771a: fgrassnormal
    0x4108c: fgrassbillboardnormal
    0x37ac9: fgrasschainnormal
    0x9a961: fgrasstangent
    0x1bc77: fgrassbillboardtangent
    0x77e02: fgrasschaintangent
    0x7201f: fgrasscossin
    0x4047: fgrasscossinfromangle
    0xa804d: fgrassshapeinvisible
    0xb9287: fgrassxzrotate
    0xce871: fgrassxzrotateenable
    0x2f679: fgrassuvswitchdisable
    0xef436: fgrassuvswitch
    0x6fbfa: fgrassuvmixer
    0xaad2d: fgrassuvmixerenable
    0x2398: fpervertexshadowfilter4x4
    0x7c847: getdepthcolumn6
    0xa96da: fpervertexshadowfilter6x6
    0xfe540: getdepthcolumn8
    0xc96d7: fpervertexshadowfilter8x8
    0x174a8: ffixedcoordinate
    0x274f8: fgrassdiffuse
    0x127ee: fgrassfade
    0xfefeb: fbrdfgrassdiffuse
    0x3945: fbrdfgrassdefault
    0xbc971: fgrassadjustnormal
    0x72835: fgrassadjustnormaldisable
    0x1f06f: fgrassillumination
    0x7aca5: fgrasslightmask
    0x2e92f: fgrasspervertexlightmask
    0xd227b: fgrasspervertexshading
    0xdc762: fgrassperpixellightmask
    0xc46c1: fgrassuseposition
    0xec07a: fgrassusepointposition
    0x9b71e: fgrassperpixelshading
    0xebf5f: fgrassshadingdisable
    0xf92f0: fdirectionalwind
    0x5afcb: fgrassglobalwind
    0x51759: fgrassglobalwind_disable
    0x4eed9: fdynamiceditmapcoordinate
    0x3da31: fdynamiceditmapreject
    0x34441: fdynamiceditmapfade
    0x86e24: fdynamiceditmapscaling
    0x16bf0: fdynamiceditmaplying
    0x693b8: fdynamiceditmapcoordinateenable
    0xd2941: fdynamiceditmaprejectenable
    0x27ccc: fdynamiceditmapfadeenable
    0xdd52: fdynamiceditmapscalingenable
    0xdf895: fdynamiceditmaplyingenable
    0xca942: fgrassconstraint
    0x6be78: fgrassconstraintbillboard
    0xdfb19: fgrassinfo
    0xe6474: fgrassinfowithnormal
    0xc2c4f: vs_grasslowest
    0xfd435: vs_grass
    0xddb2: ps_grass
    0xd444: ps_grassfinalcombiner
    0x9d4c3: vs_grassshadowreceive
    0x1fd1a: ps_grassshadowreceivetransparent
    0x432f8: ps_grassshadowreceivezpass
    0xfbe17: vs_grasspointmap
    0xed7f3: ps_grasspointmap
    0xb0464: vs_transitiondynamicedit
    0x65634: ps_transitiondynamicedit
    0x476ef: vs_dynamicedit
    0x63d59: ps_dynamicedit
    0xd7b08: vs_grass_deferred
    0x9cc00: ps_grass_deferred
    0x17ddb: ffilterdeferredrendering
    0x61957: vs_grassoutsourceing
    0x4389f: vs_grassdummy
    0x1e742: ps_grassdummy
    0x27310: vs_grassshadowdummy
    0xe7803: ps_grassshadowdummy
    0xabf76: fmiragemodcolor
    0x1b348: fmiragemodcolordebug
    0xed727: fmiragesamplescene
    0x75f3: fmiragesamplescenerefractionmap
    0xdfb26: fmiragerefract
    0x9d1da: fmiragerefractdefault
    0x88b9c: fmiragecalcoutput
    0xab760: fmiragecalcoutputnoise
    0xcd3c0: fmiragedepthblend
    0xe7a09: fmiragedepthblenddefault
    0x276f0: fmiragesectcombiner
    0x658c5: fmirageclamp
    0x1d57: fmirageclampnearfar
    0x913ef: vs_mirage
    0x36a65: ps_mirage
    0x87985: vs_miragesect
    0xda658: ps_miragesect
    0xc63aa: vs_heatdepth
    0x1c64a: ps_heatdepth
    0x2be33: fsimwatersimpletexvs
    0x819b5: fsimwatersimpletexps
    0xdd696: sbpositiontotexcoordx
    0xae600: sbpositiontotexcoordy
    0x28f5c: sbpositiontotexcoord
    0x889fa: sbtexcoordtopositionx
    0xfb96c: sbtexcoordtopositiony
    0x3c00: sbtexcoordtoposition
    0x7925b: sbidxtotexuv
    0xbc824: sbidxtotexcoord
    0xb77d8: sbidxtoposition
    0x538da: sbnormalpackf16
    0x8f4f1: sbnormalunpackf16
    0xe9e41: sbnormalpackf32
    0x3526a: sbnormalunpackf32
    0xd827c: fsbrand
    0xec115: fsbrand2
    0x2343d: unpacku8u8
    0x93350: sbpassthroughvs
    0x2fdfa: sbapplyworldoffsetps
    0x90389: sbapplyworldoffsetps_xbox
    0xbdc66: sbtolocalspaceps
    0xc8b7f: sbtolocalspaceps_xbox
    0x73ee8: sbinitps
    0x99472: sbinitps_xbox
    0xfad3f: sblodtransps
    0x34e74: sblodtransps_xbox
    0x6bc16: sbpsskinningps
    0xc348e: sbpsskinningps_xbox
    0x5b584: sbpsskinningaddposps
    0xb5ea6: sbpsskinningaddposps_xbox
    0xcdcbc: sbintegrateps
    0xdf426: sbintegrateps_xbox
    0x5987e: sbplaneconstraint
    0xf984c: sbsphereconstraint
    0xe9bac: sbcapsuleconstraint
    0xb8ac: sbboxconstraint
    0x4fed6: sbtriangleconstraint
    0x21277: sbisccalcft
    0x6da86: sbisccalcbk
    0x58303: sbprimcollision
    0x994b4: sbsolveconstps
    0x9989d: sbsolveconstps_xbox
    0x15c61: sbsolveedgeconst2ps
    0xba525: sbsolveedgeconst2ps_xbox
    0xce4fd: sbiscconstraint
    0x811e3: sbsolveconstiscps
    0xef44f: sbsolveconstiscps_xbox
    0xc4ee3: sbcreatedepthnormvs
    0x23481: sbcreatedepthnormfrontps
    0xa6fe8: sbcreatedepthnormbackps
    0x62e88: sbfilterdepthnormps
    0x814f1: ftattoouv
    0x357e6: ftattoouvnormalmap
    0xa562c: vs_tattoo
    0xc56ab: ftattoooutput
    0xcd82c: ftattoooutputheight
    0x2fa6: ps_tattoo
    0xc1186: gettattooheight
    0x5c0c8: ftattooheighttonormal
    0xb9ffc: vs_tattoonormalblend2d
    0xac57c: ps_tattoonormalblend2d
    0x3c91b: fbuildersample
    0xdc3ef: fbuildersamplebasemap
    0xb4f4: vs_builder
    0xec4b3: ps_builder
    0x4c280: getopticaldepth
    0x22411: getcrosspoint
    0xc013c: frayleighdepthmap
    0x49a07: fmiedepthmap
    0xc49a: getatmospheredepth
    0x43aac: getaerosoldepth
    0xf30b6: getrayleighscatter
    0x5e2b4: getmiescatter
    0x1fff8: getcloudscatter
    0x91e4d: getopticaldepthmap
    0x4eb16: updatedepth
    0xfcdf4: updatedensity
    0x93208: getclouddepth2
    0x555a6: getclouddepth
    0x889a5: updateclouddepth
    0x3ac1a: calcscatter
    0x1b716: calcscattering
    0x83b45: fskymapbeginend
    0x148d7: fskymapbeginendrayleigh
    0x35374: fskymapbeginendmie
    0xfd138: fskymapbeginendcloud
    0x2d056: fskymapoutputselect
    0x861e8: fskymapoutputselectrayleigh
    0x40e62: fskymapoutputselectmie
    0xde721: fskymapoutputselectcloud
    0x1af82: fskycorrecthorizon
    0xec5c7: fskycorrecthorizondisable
    0x62762: fskycorrecthorizonenable
    0x4588c: vs_skymap
    0xe2106: ps_skymap
    0x3c130: fskyfog
    0x1a7e5: fskyfinalcombiner
    0xdf444: vs_sky
    0x41759: ps_sky
    0xf28ec: getastralscattering
    0x7eb00: vs_skyastralbody
    0x65a7f: ps_skysunbody
    0x30648: ps_skymoonbody
    0x75964: vs_skystar
    0x92923: ps_skystar
    0x1d412: vs_skystarryskycolor
    0x249c7: ps_skystarryskycolor
    0xa32f7: fdiffusereflectancemodel
    0xbbf07: ftexsintan
    0x9515a: ftexorennayar
    0x2166d: forennayarmodel
    0x2f631: forennayarrgbmodel
    0xa0eb5: fspecularreflectancemodel
    0x80b84: ftexbeckmannmodel
    0x23fbd: fbeckmannmodel
    0xe4f16: fcooktorrancemodel
    0xaaa19: fkelemenszirmaymodel
    0x253f2: strandspecular
    0x2db5f: fscheuermannmodel
    0x95be4: ftexanisotropicphongspecularmodel
    0x1b7eb: ftex2anisotropicphongspecularmodel
    0xa8fda: fanisotropicphongspecularmodel
    0x815f2: ftexanisotropicphongdiffusegmodel
    0xbc1cc: fanisotropicphongdiffusegmodel
    0xd91d2: fbrdfcray
    0x97e13: fbrdfbeckmann
    0x2ab9f: fbrdfmetal
    0x9517d: fbrdfskin
    0x7587a: fbrdfhair
    0xf9bba: fbrdfhairhalflambert
    0x1582c: fbrdfanisotropicphong
    0x16563: vs_ambientshadow
    0x44eb2: fambientshadowdecay
    0x2e316: fambientshadowdecayuniform
    0x88b4a: fambientshadowdecayperspective
    0xf8d4b: fambientshadowimage
    0x5339e: fambientshadowtexture
    0x4aaac: fambientshadowcircular
    0x7bc43: fambientshadowcircularspread
    0xc87: ps_ambientshadow
    0xd03a9: ps_ambientshadowalpha
    0x1e753: vs_occlusinquery_basic
    0xbdd3: ps_occlusinquery_basic
    0x32248: foutputtexcoord
    0xfe5: fmrtnormalcombinear
    0xf441e: ftrianglevertexselector
    0xc6f8b: ftrianglevertex1
    0x53e31: ftrianglevertex2
    0x542a8: vs_vertexoutput
    0xf965a: ps_vertexoutput
    0x5305d: ps_vertexoutput3t
    0x54a8e: vs_modelnormalize
    0x1fd86: ps_modelnormalize
    0x6f91b: ps_normalizedseparation
    0x9dfc3: fmirrorfilter
    0x30109: vs_mirror
    0x97883: ps_mirror
    0xb41e7: calcprng
    0xad066: calccurveposition
    0x8c954: calcparticleratio
    0xb86a: calcparticleintensity
    0x7f98: finfparticlerandomizepos
    0x8e9f8: finfparticlerandomizeposdefault
    0xd1292: finfparticlepos
    0x91d0c: finfparticleposspline
    0x6808f: finfparticleposbezier
    0xadc7a: finfparticlecolor
    0x52bf3: finfparticlecolorconstant
    0xfcac3: finfparticlecolorconstantblend
    0x8f4c5: finfparticlecolorlerp
    0xde400: finfparticlecolorlerpblend
    0xeeaff: calcparticlerotation
    0x59724: finfparticlesample
    0x3ad32: finfparticlesamplealbedo
    0xfc268: finfparticlecalctexcoord
    0x2b0bf: finfparticlecalctexcoordpattern
    0xdfe21: finfparticletexturepattern
    0x8a2ac: finfparticletexturepatternindependent
    0x64df8: finfparticletexturepatternanimate
    0x1bfe5: finfparticlevsalphaclip
    0x43f17: finfparticlevsalphaclipdefault
    0x5188: vs_infparticle
    0x85ac3: vs_infparticle2
    0x5e3d: calctexcoord
    0xd8c92: gs_infparticle
    0x21a3e: ps_infparticle
    0x86a45: fuvdistortionmap
    0x27afa: fuvalbedoblend2map
    0x489f6: fbumpdetailnormalu_vmap
    0xedbfd: fbumpdetailmasknormalu_vmap
    0x74890: colorlerp
    0x9f2aa: fcolormaskalbedomapmodulate
    0xee344: falbedomap2
    0xb8c07: fspecular2map
    0xb521a: ffresnelschlick2
    0x33253: fshininess2
    0x1cf68: fcolormaskalbedomap
    0x446f0: fcolormasktransparencymap
    0xcd63e: fblendratealbedomap
    0x6c54d: fbdistortionrefract
    0x76346: fblendalbedomap
    0x725a5: falbedomapblenduv
    0x9ea79: falbedomapmodulateuv
    0xeedfd: fblendspecularmap
    0x5feca: fblendshininessmap
    0xbb785: fblendbumpdetailnormalmap
    0xddb9a: fblend2bumpdetailnormalmap
    0x22031: fblendratenormalmap
    0xc2d02: falbedo2mapmodulate
    0x5be60: ffinalcombinerscan
    0x138ae: ffiltercolorcorrectdepth
    0x376d5: fspecularsh
    0xb75bc: fhairsh
    0x3f419: fbumphairnormal
    0x21080: ffresnellegacy
    0x2c85b: fwrinkledetailnormalmap
    0xdddb9: fhairblur
    0xda99b: ps_materialhud
    0xf189a: fnvfinalcombiner
    0xf8162: fnvmodeldiscard
    0xe5d07: fnvmodelvignetteblend
    0xeb4a1: vs_nvgaussblur
    0xcff17: ps_nvgaussblur
    0xfa0e1: ps_vignetteextraction
    0x2269b: ps_vignettegather
    0xf7842: ps_nvdownsample4
    0x249c3: fupperposydiscardcolormodifier
    0xd54ad: flowerposydiscardcolormodifier
    0x26096: falbedotextureblendmap
    0x631a4: falbedotextureblendmapviewnormal
    0x7f3ca: fcolormodifieropticalcamouflage
    0xa0be9: initmaterialcontextlite
    0xa0380: creatematerialcontextlite
    0x89977: fcalchemispherelight
    0x825f9: fuvtransformoffsetlite
    0xce5db: fuvtransformoffset2lite
    0xa75de: fcalcshadowmapuv
    0xf6614: fshadowattenuation
    0xfc00c: fcalcprimarycolorstdlitedefault
    0x5d9e0: fcalcprimarycolorstdlitehemi
    0x99b9f: fcalcprimarycolorstdlitealphadefault
    0x11173: fcalcprimarycolorstdlitealphavertex
    0xce651: fmaterialstdalbedodefault
    0x89b10: fmaterialstdalbedoprocalphablend
    0x3e598: fmaterialstdalbedoprocblendvertexalpha
    0xf89a0: fmaterialstdalbedoprocmodulate
    0xb1175: fmaterialstdalbedoprocadd
    0xfdb60: fmaterialstdalbedoextendalphablend
    0x437cb: fmaterialstdalbedoextendblendconstantalpha
    0x38745: fmaterialstdalbedoextendblendvertexalpha
    0x61651: fmaterialstdalbedoextendmodulate
    0x60489: fmaterialstdalbedoextendadd
    0x6b09d: fmaterialstdspecularmaskdefault
    0xf73ce: fmaterialstdspecularmaskalbedo
    0x139db: fmaterialstdspecularmaskextend
    0x5d7ad: fmaterialstdspecularmaskproc
    0x23146: fmaterialstdspecularmaskexaddproc
    0x50ac0: fmaterialstdspecularmaskexmodulateproc
    0x25cc6: fmaterialstdspecularmaskexaddextend
    0xbeb8: fmaterialstdspecularmaskexmodulateextend
    0xc08c4: fmaterialstdspecularmaskexvertexcolorr
    0x1ec2f: fmaterialstdspecularmaskexvertexcolorg
    0xb18a0: fmaterialstdspecularmaskexvertexcolorb
    0x77040: fmaterialstdfresneldefault
    0x4009a: fmaterialstdfresnelenable
    0x7f082: fmaterialstdvertexcolorshadowdefault
    0xfc060: fmaterialstdvertexcolorshadowenable
    0xf2047: fmaterialstdspecularcolortypedefault
    0xaf8d8: fmaterialstdspecularcolortypealbedo
    0x4b2cd: fmaterialstdspecularcolortypeextend
    0x22695: fmaterialstdspecularcolortypeproc
    0xdac78: fmaterialstdspecularcolortypevertexcolor
    0x2b310: fmaterialstdreflectiontypeextend
    0xab59: fmaterialstdreflectiontypeproc
    0x1187e: fmaterialstdreflectiontyperim
    0x95538: fmaterialstdreflectiontypevertexcolorrim
    0x2a82: fmaterialstdreflectiontypelightrim
    0xcb202: fmaterialstdreflectiontypealbedorim
    0xeea8b: fmaterialstdreflectiontypeextendrim
    0xce4cb: fmaterialstdreflectiontypeprocrim
    0x91a93: fmaterialstdspecularcolortypedefault2
    0x1a357: fmaterialstdreflectiontypeextend2
    0x21b8d: fmaterialstdreflectiontypeextend2mask
    0xb187b: fmaterialstdreflectiontypeproc2
    0x31c0d: fmaterialstdreflectiontypeproc2mask
    0x2ca3: fmaterialstdreflectiontyperim2
    0x94e9b: fmaterialstdreflectiontyperim2mask
    0x86511: fmaterialstdreflectiontypedefault2
    0x2298: fmaterialstdreflectiontypedefault2mask
    0xbaf2a: fmaterialstdalphadefault
    0x7c77b: fmaterialstdalphaalbedo
    0x5d70b: fmaterialstdalphaalbedovertex
    0xbb033: fmaterialstdalphareflectvertex
    0x103c7: fmaterialstdvertexocclusiondefault
    0xa7285: fmaterialstdvertexocclusionenable
    0xc92ec: fcalcuvsecondarydefault
    0xf4877: fcalcuvsecondaryspheremap
    0xf61ce: fuvextendmapprimary
    0x13c5: fuvextendmapsecondary
    0x8a3d0: fbrdf_lite
    0x8726d: fperpixellightingvs
    0x2d5eb: fperpixellightingps
    0xd6c3f: fpervertexlightingvs
    0x7cbb9: fpervertexlightingps
    0x75dc: vs_materialstdlite
    0xcc959: ps_materialstdlite
    0x6a9fc: fcalcprimarycolorconstantlitedefault
    0xff54f: fcalcprimarycolorconstantlitevertex
    0xa8bf6: fcalcprimarycolorconstantliteuber
    0x8ad6b: vs_materialconstantlite
    0x2df11: ps_materialconstantlite
    0xa8ee1: frimnone
    0x32510: frimaddbase
    0x67115: frimaddcolor
    0x70f66: frimmodulate
    0x7d9e4: frimblend
    0xd9120: frimuber
    0xf8344: toonvertexcolordisable
    0x2a8e0: toonvertexcolorenable
    0x20801: toonvertexcoloruber
    0x1a8c1: toonshadowmaskdisable
    0x22f1a: toonshadowmaskenable
    0x10d07: toonshadowmaskuber
    0x7a064: fcalcprimarycolortoondefault
    0xe9b83: fcalcprimarycolortoonvertexcolor
    0x49389: fcalcprimarycolortoonuber
    0x2ea3f: fbrdf_toon_lite
    0x2e6da: fperpixellightingtoonvs
    0x8415c: fperpixellightingtoonps
    0x72966: fpervertexlightingtoonvs
    0xd8ee0: fpervertexlightingtoonps
    0xbbf08: fperpixellightingtoonlmtvs
    0x1188e: fperpixellightingtoonlmtps
    0xb662c: vs_materialtoonsm
    0xfd124: ps_materialtoonsm
    0xa583b: tsystem
    0x3d31e: tproceduraltexture
    0x47bf2: tantialiasing
    0xb3467: tdevelop
    0xf0408: tcollision
    0x316ad: tfilter
    0x4af70: tmaterialnull
    0x10fdc: tmaterialdummy
    0x53e9b: tdummy
    0x8a043: tmaterialdummyedge
    0x48a50: tmaterialdummypicker
    0xba44: tmaterialdebug
    0x76b01: tmaterialvelocity
    0x54393: tmaterialvelocityedge
    0x90af1: tmaterialoutline
    0x66f2a: tshadowreceive
    0x3d37b: tdualparaboloid
    0x87a4a: tdeferredlighting
    0x85f0: treflectiveshadowmap
    0x25fcf: tmaterialstd
    0xe04e: tadhesion
    0xa48a5: tmaterialsss
    0xc111e: tmaterialstdest
    0xd9f30: tmodelfog
    0x56870: tmaterialconstant
    0x9f515: tmaterialstdpn
    0xa5020: tmaterialstdph
    0xe73fa: tmaterialstddm
    0xf46ba: tmaterialstdcafetes
    0x17e15: tshadowcast
    0x85247: tradialblurfilter
    0xf34e7: ttvnoisefilter
    0x94385: tvariancefilter
    0x236fc: tbloomfilter
    0x135f0: timageplanefilter
    0xf29d7: tlogaverage
    0x54624: tcubemapfilter
    0x55045: tgsdoffilter
    0xd7309: tssao
    0x664db: ttangentfilter
    0xdea6d: tprimitive
    0xd2659: tprimitive2d
    0x2d87e: twater
    0xd7376: tgui
    0x78108: ttextureblend
    0x5f420: tgpuparticle
    0x66677: tlightshaft
    0xc5357: tgrass
    0xef994: tgrassoutsourceing
    0xc28e5: tgrassdummy
    0x172f3: tgrassshadowdummy
    0xa401c: tmirage
    0x6f49f: tsimwatersimpletex
    0xee2da: tsoftbody
    0x905df: ttattoo
    0x79401: tbuilder
    0xe530b: tsky
    0x543d7: tambientshadow
    0xb0751: tocclusionquery
    0xf1cca: trecalcnormal
    0x52fa: tmirror
    0x591ba: tinfparticle
    0xa221f: tmaterialhud
    0xd356d: tnvfilter
    0x4ed89: tmaterialstdlite
    0x3eef1: tmaterialconstantlite
    0x1059f: tmaterialtoonsm
    0xd23d5: fddmaterialcalcborderblendrate
    0x747bd: fddmaterialcalcborderblendalphamap
    0xc491c: fddmaterialbump
    0x13f1f: fddmaterialalbedo
    0x77e03: fddmaterialspecular
    0x51c7a: fappclip
    0x1763: fappoutline
    0x37f0e: fintegratedoutlinecolor
    0xc6df3: fddmaterialfinalcombiner
    0xd8dd3: feditsimplealbedomapalphamap
    0x2d616: fdamagesimplealbedomap
    0x59b93: freflectcubemapshadowlight
    0xdc4af: falbedomapblendmaxalpha
    0xf2161: fdamagesimplealbedomapalphamap
    0x5f2a0: fdamagesimplealbedomapburnmap
    0xf6ec9: fburnemissionmapblend
    0xe5d83: fburnsimplealbedomapburnmap
    0x752d4: fdamagespecularmap
    0xf32b9: fburnalbedomapburnmap
    0xf04df: fdamagebumpdetailnormalmap
    0x7af47: talbedoburnmap
    0x6E11: tnormalburnmap
    0xa463e: tspecularburnmap
    0x17009: tburnemissionmap
    0xce407: fuvalbedoburnmap
    0x49B33: treflectwatermap
    0xcc68b: cbddmaterialparam
    0x6d828: cbburncommon
    0x7275e: cbappclipplane
    0x50d2: cboutlineex
    0xdeace: cbappreflect
    0xd7d4e: cbappreflectshadowlight
    0xe6d24: cbddmaterialparaminnercorrect
    0xB4974: cbburnemission
    0x1F0C6: cbspecularblend
    0x247ee: cbuvrotationoffset
