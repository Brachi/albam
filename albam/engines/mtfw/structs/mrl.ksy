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
            0x7b2c215f: rehd_cb_s_globals # re0 
            0x6c801200: cb_material  
            0x7b2c2159: rehd_cb_s_globals # rehd
            0x6c8011f9: cb_material 
            0xefca3222: cb_distortion 
            0xc48f7223: cb_vtx_distortion_refract
            0x7b2c2155: rehd_cb_s_globals # rer1
            0x6c8011f4: cb_material
            0xefca322b: cb_distortion
            0xc48f722c: cb_vtx_distortion_refract
            0x7b2c215e: rev2_cb_s_globals #rer2
            0x6c8011fe: cb_material
            0x15419236: cb_vtx_displacement
            0x51814237: cb_vtx_displacement2
            0x22882238: cb_vtx_displacement3
            0x6f01631b: cb_color_mask
            0x61c6e23d: cb_vtx_dispmask_uv
            0xaee37319: cb_ba_alpha_clip
            0xefca3227: cb_distortion
            0xc48f7228: cb_vtx_distortion_refract
            0x7b2c214c: cb_s_globals # Re6
            0x6c8011ea: cb_material
            0xaee3730c: cb_unk_01 #2934141708
            0x6F01630e: cb_unk_02
            0xc48f7221: cb_unk_01 #3297735201
            0xefca3220: cb_unk_01 #4023005728 CBDistortion
            0x84115310: cb_unk_03 #2215727888
            0x61E43233: cb_unk_04 #1642345011 CBVertexDisplacementExplosion
            0x1541922f: cb_vtx_displacement
            0x51814230: cb_vtx_displacement2
            0x22882231: cb_vtx_displacement2 #579346993
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
  #CBMaterial 0x6c8011fe size 32 rer2 
  cb_material:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 32}
  #$Globals rehd
  rehd_cb_s_globals:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 72}
  #$Globals
  cb_s_globals:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 84}
  #$Globals 0x7b2c215e size 120 rer2  
  rev2_cb_s_globals:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 120}
  #CBVertexDisplacement 0x15419236 size 8 rer2
  cb_vtx_displacement:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 8}
  #CBVertexDisplacement2 0x51814237 size 4 rer2
  cb_vtx_displacement2:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  #CBVertexDisplacement3 0x22882238 size 4 rer2
  cb_vtx_displacement3:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  #CBVertexDispMaskUV 0x61c6e23d size 8 rer2
  cb_vtx_dispmask_uv:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 8}
  #CBColorMask 0x6f01631b size 24 rer2
  cb_color_mask:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 24}
  #CBBAlphaClip 0xaee37319 size 4 rer2
  cb_ba_alpha_clip:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  #CBDistortion 0xefca3227 size 4 rer2
  cb_distortion:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  #CBDistortionRefract 0xc48f7228
  cb_vtx_distortion_refract:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
      
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
