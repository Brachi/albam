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
      - {id: value, type: cmd_value} 
      - {id: shader_object_hash, type: u4}

  texture_slot:
    seq:
      - {id: type_hash, type: u4} # rTexture
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}
      - {id: texture_path, type: str, size: 64, encoding: ascii, terminator: 0}
  
  anim_data:
    seq:
      - {id: num_entry, type: u4}
      
  hash_block:
    seq:
      - {id: index, type: b12}
      - {id: value, type: b20}
      
  cmd_info:
    seq:
      - {id: cmd_type, type b4}
      - {id: unk, type b16}
      - {id: shader_obj_idx, type b12}
      
  cmd_value:
    seq:
      - {id: ofs_const_buff, type u4} #cmd info type 1
    instances:
      hash:
        value: ofs_const_buff #type 0, 2, 4
      texture_index:
        value: ofs_const_buff #type 3
        
  tex_offset:
    seq:
      - {id: texture_id, type: u4}
  
  shd_hash:
    seq:
      - {id: shader_hash, type: u4}
  
  ofs_buff:
    seq:
      - {id: ofs_const_buff, type: u4}
      
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
      values:
        {pos: ofs_cmd + 12 * cmd_list_info.index, size: cmd_buffer_size - 12 * cmd_list_info.index}
      #anims:
       # {pos: ofs_anim_data, size: anim_data_size, if anim_data_size != 0}
