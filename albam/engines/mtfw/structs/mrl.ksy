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
        pos: _parent._io.pos + value_cmd.as<cmd_ofs_buffer>.ofs_float_buff
        type: 
          switch-on: shader_object_hash
          cases:
            0x7b2c215f: shd_s_globals # $Globals re0
            0x6c801200: shd_cb_material # CBMaterial re0
            0x7b2c2159: shd_s_globals # $Globals rehd
            0x6c8011f9: shd_cb_material # CBMaterial rehd
            0x7b2c2155: shd_s_globals # $Globals rer1
            0x6c8011f4: shd_cb_material # CBMaterial rer1
            0x7b2c215e: shd_s_globals # $Globals rer2
            0x6c8011fe: shd_cb_material # CBMaterial rer2
            0x7b2c214c: shd_s_globals # $Globals re6
            0x6c8011ea: shd_cb_material # CBMaterial re6
        if: info.cmd_type == 1
        
  texture_slot:
    seq:
      - {id: type_hash, type: u4} # rTexture
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}
      - {id: texture_path, type: str, size: 64, encoding: ascii, terminator: 0}
      
  material:
    seq:
      - {id: type_hash, type: u4} #hash not in mfx
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
  
  anim_data:
    seq:
      - {id: entry_count, type: u4}
      - {id: ofs_entry, type: u4}
      - {id: unk_00, type: u4, repeat: expr, repeat-expr: entry_count} # seconds?
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
        pos: _parent._parent.ofs_anim_data + ofc_block
        type: anim_entry
      
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
      
  anim_entry:
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
     - {id: header, type: u1, repeat: expr, repeat-expr: 12}
     - {id: values, type: u1, repeat: expr, repeat-expr: 8 * _parent.info.num_entry}
    
  anim_sub_entry1:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 24}
     - {id: values, type: u1, repeat: expr, repeat-expr: 20 * (_parent.info.num_entry -1)}
  
  anim_sub_entry2:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 12}
     - {id: values, type: u1, repeat: expr, repeat-expr: 8 * _parent.info.num_entry}

  anim_sub_entry3:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 24}
     - {id: values, type: u1, repeat: expr, repeat-expr: 16 * (_parent.info.num_entry -1)}
      
  anim_sub_entry4:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 4}
     - {id: values, type: f4, repeat: expr, repeat-expr: 20 * _parent.info.num_entry}
     - {id: hash, type: u4}
     
  anim_sub_entry5:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 12}
     - {id: values, type: u1, repeat: expr, repeat-expr: 8 * _parent.info.num_entry}
     
  anim_sub_entry6:
    seq:
     - {id: header, type: u1, repeat: expr, repeat-expr: 36}
     - {id: values, type: u1, repeat: expr, repeat-expr: 24 * (_parent.info.num_entry -1)}
  
  anim_sub_entry7:
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
        
  shd_cb_material:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 32}
  shd_s_globals:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 76}
  shd_diff_col_correct:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  shd_half_lambert:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  shd_toon2:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 4}
  shd_indirect_user:
    seq:
      - {id: data, type: f4, repeat: expr, repeat-expr: 12}
        
  tex_offset:
    seq:
      - {id: texture_id, type: u4}
  
  shd_hash:
    seq:
      - {id: shader_hash, type: u4}
  
  ofs_buff:
    seq:
      - {id: ofs_const_buff, type: u4}
