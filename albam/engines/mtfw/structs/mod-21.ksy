meta:
  endian: le
  file-extension: mod
  id: mod_21
  ks-version: 0.10
  title: MTFramework model format 210 and 211

seq:
  - {id: header, type: mod_header}
  - {id: bones, type: bone, repeat: expr, repeat-expr: header.num_bones}
  - {id: parent_space_matrices, type: matrix4x4, repeat: expr, repeat-expr: header.num_bones}
  - {id: inverse_bind_matrices, type: matrix4x4, repeat: expr, repeat-expr: header.num_bones}
  - {id: bone_map, size: 256, if: header.num_bones != 0}
  - {id: groups, type: group, repeat: expr, repeat-expr: header.num_groups}
  - {id: material_names, type: str, encoding: ascii, size: 128, terminator: 0, repeat: expr, repeat-expr: header.num_material_names, if: header.version == 210}
  - {id: material_hashes, type: u4, repeat: expr, repeat-expr: header.num_material_hashes, if: header.version == 211}
  - {id: meshes, type: mesh, repeat: expr, repeat-expr: header.num_meshes}
  - {id: num_weight_bounds_211, type: u4, if: header.version == 211}
  - {id: weight_bounds_210, type: weight_bound, repeat: expr, repeat-expr: header.num_weight_bounds_210, if: header.version == 210}
  - {id: weight_bounds_211, type: weight_bound, repeat: expr, repeat-expr: num_weight_bounds_211, if: header.version == 211}
  - {id: vertex_buffer, size: header.size_vertex_buffer}
  - {id: index_buffer, size: header.num_faces * 2}
  # TODO: padding

types:

  mod_header:
    seq:
      - {id: ident, contents: [0x4d, 0x4f, 0x44, 0x00]}
      - {id: version, type: u1}
      - {id: revision, type: u1}
      - {id: num_bones, type: u2}
      - {id: num_meshes, type: u2}
      - {id: num_material_names, type: u2, if: version == 210}
      - {id: num_material_hashes, type: u2, if: version == 211}
      - {id: num_vertices, type: u4}
      - {id: num_faces, type: u4}
      - {id: num_edges, type: u4}
      - {id: size_vertex_buffer, type: u4}
      - {id: reserved_01, type: u4}
      - {id: num_groups, type: u4}
      - {id: offset_bones, type: u4}
      - {id: offset_groups, type: u4}
      - {id: offset_material, type: u4}
      - {id: offset_meshes, type: u4}
      - {id: offset_buffer_vertices, type: u4}
      - {id: offset_buffer_indices, type: u4}
      - {id: size_file, type: u4}
      - {id: bsphere, type: vec4}
      - {id: bbox_min, type: vec4}
      - {id: bbox_max, type: vec4}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u4}
      - {id: unk_03, type: u4}
      - {id: unk_04, type: u4}
      - {id: num_weight_bounds_210, type: u4, if: version == 210}

  mesh:
    seq:
      - {id: idx_group, type: u2}
      - {id: num_vertices, type: u2}
      - {id: unk_01, type: u1}
      - {id: idx_material, type: u2}
      - {id: level_of_detail, type: u1}
      - {id: type_mesh, type: u1}
      - {id: unk_class_mesh, type: u1}
      - {id: vertex_stride, type: u1}
      - {id: unk_render_mode, type: u1}
      - {id: vertex_position, type: u4}
      - {id: vertex_offset, type: u4}
      - {id: vertex_format, type: u4}
      - {id: face_position, type: u4}
      - {id: face_count, type: u4}
      - {id: face_offset, type: u4}
      - {id: bone_id_start, type: u1}
      - {id: num_unique_bone_ids, type: u1}
      - {id: mesh_index, type: u2}
      - {id: min_index, type: u2}
      - {id: max_index, type: u2}
      - {id: hash, type: u4}
    instances:
      indices:
        pos: _root.header.offset_buffer_indices + face_offset * 2 + face_position * 2
        repeat: expr
        repeat-expr: face_count
        type: u2
      vertices:
        pos: _root.header.offset_buffer_vertices + vertex_offset + (vertex_position * vertex_stride)
        repeat: expr
        repeat-expr: num_vertices
        type:
          switch-on: vertex_format
          cases:
            0x14d40020: vertex_14d4
            0x2f55c03d: vertex_2f55
            0xa320c016: vertex_a320
            0xa8fab018: vertex_a8fa
            0xb0983013: vertex_b098
            0xbb424024: vertex_bb42
            0xc31f201c: vertex_c31f
            0xcb68015: vertex_cb68
            0xdb7da014: vertex_db7d
            0xa7d7d036: vertex_a7d7 #static
            0x49b4f029: vertex_49b4 #static
            0x207d6037: vertex_207d #static
            0xd8297028: vertex_8297 #static
            0xd1a47038: vertex_d1a4 #static
            0xb86de02a: vertex_b86d #static
            0x63b6c02f: vertex_63b6 #static
            0x926fd02e: vertex_926f #static
            0x9399c033: vertex_9399 #static
            0xcbf6c01a: vertex_cbf6
            0xd877801b: vertex_d877
            0xb392101f: vertex_b392
            0x64593023: vertex_6459
            0x5e7f202c: vertex_5e7f
            0xafa6302d: vertex_afa6
            0xa14e003c: vertex_a14e
            0xc66fa03a: vertex_c66f
            0x667b1019: vertex_667b
            0xa013501e: vertex_a013
            0x12553032: vertex_1255
            0xb6681034: vertex_b668
            0x2082f03b: vertex_2082
            0x37a4e035: vertex_37a4
            0x4325a03e: vertex_4325
            0x77d87022: vertex_77d8
            0xd84e3026: vertex_d84e # rehd
            0xdA55a021: vertex_da55 # re6
            0xcbcf7027: vertex_cbcf # re6
            0xd9e801d:  vertex_d9e8 # re6
            0x747d1031: vertex_747d # re6
            0x75c3e025: vertex_75c3 # re6
            
  vertex_75c3: #untested re6 em4801 mesh20 IASkinTBN8wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2}
      - {id: tangent, type: vec4_u1}
      - {id: uv2, type: vec2_half_float}
            
  vertex_747d: # untested re6 md0022_03 IANonSkinTBNA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      
  vertex_d9e8: #untested re6 sm6290 IASkinTBN2wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2}
      - {id: uv, type: vec2_half_float}
            
  vertex_cbcf: #untested re6 em5030 mesh82 IASkinTBNLA8wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2}
      - {id: tangent, type: vec4_u1}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
      
  vertex_da55: # untested re6 sm5933 IASkinTBN4wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}
      - {id: uv2, type: vec2_half_float}
            
  vertex_d84e: # ok rehd r313_g05 IASkinTBC8wt
    seq:
      - {id: position, type: vec4_s2} # w1
      - {id: normal, type: vec4_u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: tangent, type: vec4_u1}
      - {id: rgba, type: vec4_u1}
            
  vertex_77d8: # ok rev1 bl_center_t2 IASkinTBC4wt
    seq:
      - {id: position, type: vec4_s2} # w = w1
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: rgba, type: vec4_u1}
            
  vertex_4325: # untested rev1 md000f mesh1 IANonSkinTBN_4M
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: morph_position, type: vec3_s2}
      - {id: morph_position2, type: vec3_s2}
      - {id: morph_position3, type: vec3_s2}
      - {id: morph_position4, type: vec3_s2}
      - {id: morph_normal, type: vec3_u1}
      - {id: morph_normal2, type: vec3_u1} 
      - {id: morph_normal3, type: vec3_u1} 
      - {id: morph_normal4, type: vec3_u1} 

  vertex_37a4: #ok s1010_00Scr.arc s0102_g  mesh1 IANonSkinTBNLA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
      
            
  vertex_2082: #ok s1030_00scr s0503-7f mesh36 IANonSkinBLA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
  
  vertex_b668: #untested md002b_00 IANonSkinTBNCA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
      - {id: uv3, type: vec2_half_float}
  
  vertex_1255: #ok s2304_00scr.arc rouka mesh10 IANonSkinTBLA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float} #lightmaps
            
  vertex_a013: #untested uSm8754.arc sm8754.mod mesh2 IASkinTBC2wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1} 
      - {id: uv, type: vec2_half_float}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2} # half float probably
      - {id: rgba, type: vec4_u1}
            
  vertex_667b: #ok uSm8771.arc sm8771.mod mesh1  IASkinTBN1wt
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      
  vertex_c66f: #ok usm9110.arc sm9110.mod mesh1 IANonSkinBA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
            
  vertex_a14e: #untested md000d_00 mesh0 IANonSkinBCA
    seq:
       - {id: position, type: vec3}
       - {id: normal, type: vec4_u1}
       - {id: uv, type: vec2_half_float}
       - {id: uv2, type: vec2_half_float}
       - {id: rgba, type: vec4_u1}
  
  vertex_afa6: #untested md0303 mesh0 IANonSkinTBA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
  
  vertex_5e7f: #untested md0020 mesh0 IANonSkinTBN
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      
      
  vertex_6459: #ok wp1800 mesh4 IASkinTBNLA4wt
    seq:
      - {id: position, type: vec4_s2} # w = w1
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
      
  vertex_b392: #ok wp1800 mesh8 IASkinTBNLA2wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 2}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
            
  vertex_d877: # ok wp1800 mesh6 IASkinTBNLA1wt
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
            
  vertex_cbf6: #ok wp3000 mesh1 weight hardcoded to 1.0 IASkinTBC1wt
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}

  vertex_9399: #IANonSkinTBCA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
  
  vertex_926f: #IANonSkinTBNC
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1} # 4th byte occlusion
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
  
  vertex_63b6: # ok s2304_00scr.arc rouka.mod mesh0 IANonSkinTBNL
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: vertex_alpha, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: occlusion, type: u4}
            
  vertex_b86d: # rer2 s2304_00Scr.arc bedroom.mod mesh14 IANonSkinTBL
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: vertex_alpha, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: occlusion, type: u4}
  
  vertex_d1a4: #IANonSkinBL
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      
  vertex_8297: # ok rev1 s500_scroll.arc s500_2.mod mesh0 IANonSkinTB
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
            
  vertex_207d: # 24 IANonSkinBC
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
  
  vertex_49b4: # s1030_00scr.arc cast_a.mod IANonSkinTBC
    seq:
       - {id: position, type: vec3}
       - {id: normal, type: vec4_u1}
       - {id: tangent, type: vec4_u1}
       - {id: uv, type: vec2_half_float}
       - {id: rgba, type: vec4_u1}
  
  vertex_a7d7: #20 rev1 s10a_1_scroll.arc s10a_bgl1.mod IANonSkinB
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      
  vertex_14d4: # 28 ok rev2 wp1500 IASkinTB4wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float

  vertex_2f55: # 64 rehd pl0b.arc pl0b.mod mesh2 IASkinOTB_4WT_4M
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1} #signed in maxscript
      - {id: tangent, type: vec4_u1} #signed in maxscript
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
       # first weight in position.w, 4th is remaining until 1.0
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: morph_position, type: vec3_s2}
      - {id: morph_position2, type: vec3_s2}
      - {id: morph_position3, type: vec3_s2}
      - {id: morph_position4, type: vec3_s2}
      - {id: morph_normal, type: vec3_u1}
      - {id: morph_normal2, type: vec3_u1} 
      - {id: morph_normal3, type: vec3_u1} 
      - {id: morph_normal4, type: vec3_u1} 

  vertex_a320: #untested lines rehd pl0b.arc pl0b.mod mesh35 IASkinBridge8wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8} 
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 8}
      - {id: normal, type: vec4_u1}

  vertex_a8fa: #ok rev2 wp6040.mod mesh4 IASkinTB1wt
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1} # maybe bone and weight
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}

  vertex_b098: #ok sm8799.mod weight hardcoded to 1.0 IASkinBridge1wt
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec4_u1} 

  vertex_bb42: # rev2 sm8683.mod mesh4 uncorrect weights IASkinTB8wt
    seq:
      - {id: position, type: vec4_s2} # w1
      - {id: normal, type: vec4_u1}
       # TODO: weights
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 8} # w2-w5
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2} # w6-w7
      - {id: tangent, type: vec4_u1}

  vertex_c31f: #ok rev2 fig01.arc pl2200.mod mesh17 posed hands IASkinTB2wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2}

  vertex_cb68: #ok line rev2 uwp3010.mod sm8698.mod mesh3 IASkinBridge4wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4} 
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: normal, type: vec4_u1}# probably rgba
  
  vertex_db7d: #ok line rev2 uwp3010.mod sm8698.mod mesh2 IASkinBridge2wt
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4} # strange 0x80 2 and 4 values

  vec2_half_float:
    seq:
      - {id: u, size: 2}
      - {id: v, size: 2}
      
  vec4_u1:
    seq:
      - {id: x, type: u1}
      - {id: y, type: u1}
      - {id: z, type: u1}
      - {id: w, type: u1}
      
  vec3_u1:
    seq:
      - {id: x, type: u1}
      - {id: y, type: u1}
      - {id: z, type: u1}
      
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}

  vec4_s2:
    seq:
      - {id: x, type: s2}
      - {id: y, type: s2}
      - {id: z, type: s2}
      - {id: w, type: s2}

  vec3_s2:
    seq:
      - {id: x, type: s2}
      - {id: y, type: s2}
      - {id: z, type: s2}

  matrix4x4:
    seq:
      - {id: row_1, type: vec4}
      - {id: row_2, type: vec4}
      - {id: row_3, type: vec4}
      - {id: row_4, type: vec4}

  bone:
    seq:
      - {id: idx_anim_map, type: u1}
      - {id: idx_parent, type: u1}
      - {id: idx_mirror, type: u1}
      - {id: idx_mapping, type: u1}
      - {id: unk_01, type: f4}
      - {id: parent_distance, type: f4}
      - {id: location, type: vec3}

  group:
    seq:
      - {id: group_index, type: u4}
      - {id: unk_02, type: f4}
      - {id: unk_03, type: f4}
      - {id: unk_04, type: f4}
      - {id: unk_05, type: f4}
      - {id: unk_06, type: f4}
      - {id: unk_07, type: f4}
      - {id: unk_08, type: f4}

  material:
    seq:
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: unk_floats, type: f4, repeat: expr, repeat-expr: 30}

  weight_bound:
    seq:
      - {id: bone_id, type: u4}
      - {id: unk_01, type: vec3}
      - {id: bsphere, type: vec4}
      - {id: bbox_min, type: vec4}
      - {id: bbox_max, type: vec4}
      - {id: oabb_matrix, type: matrix4x4}
      - {id: oabb_dimension, type: vec4}
