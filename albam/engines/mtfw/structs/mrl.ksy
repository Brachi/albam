meta:
  endian: le
  bit-endian: le
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
  texture_slot:
    seq:
      - {id: type_hash, type: u4} # rTexture not in mfx
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}
      - {id: texture_path, type: str, size: 64, encoding: ascii, terminator: 0}
      
  material:
    seq:
      - {id: type_hash, type: u4} # TYPE_nDraw_MaterialStd not in mfx
      - {id: name_hash_crcjam32, type: u4}
      - {id: cmd_buffer_size, type: u4}
      - {id: blend_state_hash, type: u4}
      - {id: depth_stencil_state_hash, type: u4}
      - {id: rasterizer_state_hash, type: u4}
      - {id: cmd_list_info, type: hash_block}
      - {id: material_info_flags, type: u1, repeat: expr, repeat-expr: 4}
      - {id: unk_nulls, type: u4, repeat: expr, repeat-expr: 4}
      - {id: anim_data_size, type: u4}
      - {id: ofs_cmd, type: u4}
      - {id: ofs_anim_data, type: u4}
    instances:
      resources:
        {pos: ofs_cmd, type: resource_binding, repeat: expr, repeat-expr: cmd_list_info.index}
      anims:
        {pos: ofs_anim_data, type: anim_data, if anim_data_size != 0}
        
  resource_binding:
    seq:
      - {id: info, type: cmd_info} # value type
      - id: value_cmd
        type:
          switch-on: info.cmd_type
          cases:
            0: hash_block
            1: cmd_ofs_buffer
            2: hash_block
            3: cmd_tex_idx
            4: hash_block
      - {id: shader_object_hash, type: u4}
    instances:
      float_buffer:
        pos: _parent.ofs_cmd + value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
        type: 
          switch-on: shader_object_hash
          cases:
            0x7b2c215f: str_rehd_cb_globals # re0 
            0x6c801200: str_cb_material
            0x7b2c2159: str_rehd_cb_globals # rehd
            0x6c8011f9: str_cb_material
            0xefca3222: str_cb_distortion
            0xc48f7223: str_cb_vtx_distortion_refract
            0x7b2c2155: str_rehd_cb_globals # rer1
            0x6c8011f4: str_cb_material
            0xefca322b: str_cb_distortion
            0xc48f722c: str_cb_vtx_distortion_refract
            0x7b2c215e: str_rev2_cb_globals #rer2
            0x6c8011fe: str_cb_material
            0x15419236: str_cb_vtx_displacement
            0x51814237: str_cb_vtx_displacement2
            0x22882238: str_cb_vtx_displacement3
            0x6f01631b: str_cb_color_mask
            0x61c6e23d: str_cb_vtx_disp_mask_uv
            0xaee37319: str_cb_ba_alpha_clip
            0xefca3227: str_cb_distortion
            0xc48f7228: str_cb_vtx_distortion_refract
            0x7b2c214c: cb_s_globals # Re6
            0x6c8011ea: str_cb_material
            0xaee3730c: cb_unk_01 #2934141708 alpha clip?
            0x6F01630e: cb_unk_02 # color mas ?
            0xc48f7221: cb_unk_01 #3297735201 distortion refract ?
            0xefca3220: str_cb_distortion
            0x84115310: cb_unk_03 #2215727888
            0x61E43233: str_cb_vtx_disp_ex
            0x1541922f: str_cb_vtx_displacement
            0x51814230: str_cb_vtx_displacement2
            0x22882231: str_cb_vtx_displacement3 #579346993
        if: info.cmd_type == 1
      #test_ofs:
        #value: _parent.ofs_cmd
        
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
      
  hash_block:
    seq:
      - {id: index, type: b12}
      - {id: value, type: b20}
      
  cmd_info:
    seq:
      - {id: cmd_type, type: b4}
      - {id: unk, type: b16}
      - {id: shader_obj_idx, type: b12}
      
  cmd_ofs_buffer:
    seq:
      - {id: ofs_float_buff, type: u4}
      
  cmd_tex_idx:
    seq:
      - {id: tex_idx, type: u4}

  #$Globals re6
  cb_s_globals:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 84}
      
  cb_unk_01:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
      
  cb_unk_02:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 24}
      
  cb_unk_03:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 8}
      
  cb_unk_04:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 16}
        
  tex_offset:
    seq:
      - {id: texture_id, type: u4}
  
  shd_hash:
    seq:
      - {id: shader_hash, type: u4}
  
  ofs_buff:
    seq:
      - {id: ofs_const_buff, type: u4}
      
  str_rev2_cb_globals: #120 floats
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
      
  str_rehd_cb_globals: #re0-rehd-rev 72 floats
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
      - {id: f_emission_color, type: f4, repeat: expr, repeat-expr: 4} #44
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
      
  str_cb_material: #all games 32 floats
    seq:
      - {id: f_diffuse_color, type: f4, repeat: expr, repeat-expr: 3}
      - {id: f_transparency, type: f4}
      - {id: f_reflective_color, type: f4, repeat: expr, repeat-expr: 3}
      - {id: f_transparency_volume, type: f4}
      - {id: f_uv_transform, type: f4, repeat: expr, repeat-expr: 8}
      - {id: f_uv_transform2, type: f4, repeat: expr, repeat-expr: 8}
      - {id: f_uv_transform3, type: f4, repeat: expr, repeat-expr: 8}
      
  str_cb_ba_alpha_clip: # 4 floats 0xaee37319
    seq:
      - {id: f_b_alpha_clip_threshold, type: f4}
      - {id: f_b_blend_rate, type: f4}
      - {id: f_b_blend_band, type: f4}
      - {id: filler, type: f4}

  str_cb_vtx_displacement: # CBVertexDisplacement 0x15419236 rev2 8 floats
    seq:
      - {id: f_vtx_disp_start, type: f4}
      - {id: f_vtx_disp_scale, type: f4}
      - {id: f_vtx_disp_inv_area, type: f4}
      - {id: f_vtx_disp_rcn, type: f4}
      - {id: f_vtx_disp_tilt_u, type: f4}
      - {id: f_vtx_disp_tilt_v, type: f4}
      - {id: filler, type: f4, repeat: expr, repeat-expr: 2}
      
  str_cb_vtx_displacement2: # CBVertexDisplacement2 0x51814237 rev2 4 floats
    seq:
      - {id: f_vtx_disp_start2, type: f4}
      - {id: f_vtx_disp_scales, type: f4}
      - {id: f_vtx_disp_inv_area2, type: f4}
      - {id: f_vtx_disp_rcn2, type: f4}
      
  str_cb_vtx_displacement3: # CBVertexDisplacement3 0x22882238 rev2 4 floats
    seq:
      - {id: f_vtx_disp_direction, type: f4, repeat: expr, repeat-expr: 3}
      - {id: filler, type: f4}
      
  str_cb_color_mask: # 24 floats
    seq:
      - {id: f_color_mask_threshold, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask_offset, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_clip_threshold, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask_color, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask2_threshold, type: f4, repeat: expr, repeat-expr: 4}
      - {id: f_color_mask2_color, type: f4, repeat: expr, repeat-expr: 4}
      
  str_cb_vtx_disp_mask_uv: #CBVertexDispMaskUV 0x61c6e23d 8 floats
    seq:
      - {id: f_vertex_disp_mask_uv, type: f4, repeat: expr, repeat-expr: 8}
      
  str_cb_distortion: #CBDistortion 0xefca3227 4 floats
    seq:
      - {id: f_distortion_factor, type: f4}
      - {id: f_distortion_blend, type: f4}
      - {id: filler, type: f4, repeat: expr, repeat-expr: 2}
      
  str_cb_vtx_distortion_refract:   #CBDistortionRefract 0xc48f7228
    seq:
      - {id: f_distortion_refract, type: f4}
      - {id: filler, type: f4, repeat: expr, repeat-expr: 3}

  str_cb_vtx_disp_ex: # re6 CBVertexDisplacementExplosion  0x61E43233 16 floats
    seq:
      - {id: f_vtx_disp_ex_scale0, type: f4}
      - {id: f_vtx_disp_ex_scale1, type: f4}
      - {id: f_vtx_disp_ex_scale2, type: f4}
      - {id: f_vtx_disp_ex_scale3, type: f4}
      - {id: f_vtx_disp_ex_scale4, type: f4}
      - {id: f_vtx_disp_ex_scale5, type: f4}
      - {id: f_vtx_disp_ex_scale6, type: f4}
      - {id: f_vtx_disp_ex_scale7, type: f4}
      - {id: f_vtx_disp_ex_radius, type: f4}
      - {id: f_vtx_disp_ex_rot_x, type: f4}
      - {id: f_vtx_disp_ex_rot_y, type: f4}
      - {id: f_vtx_disp_ex_rot_z, type: f4}
      - {id: f_vtx_disp_ex_rot_origin_x, type: f4}
      - {id: f_vtx_disp_ex_rot_origin_y, type: f4}
      - {id: f_vtx_disp_ex_rot_origin_z, type: f4}
      - {id: filler, type: f4}