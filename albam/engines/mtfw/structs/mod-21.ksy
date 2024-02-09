meta:
  endian: le
  file-extension: mod
  id: mod_21
  ks-version: 0.11
  title: MTFramework model format 210 and 211

seq:
  - {id: header, type: mod_header}
  - {id: bsphere, type: vec4}
  - {id: bbox_min, type: vec4}
  - {id: bbox_max, type: vec4}
  - {id: unk_01, type: u4}
  - {id: unk_02, type: u4}
  - {id: unk_03, type: u4}
  - {id: unk_04, type: u4}
  - {id: num_weight_bounds, type: u4, if: _root.header.version == 210}
  # TODO: padding

instances:
  bones_data:
    {pos: header.offset_bones_data, type: bones_data, if: header.num_bones != 0}
  bones_data_size_:
    value: "header.num_bones == 0 ? 0 : bones_data.size_"
  groups:
    {pos: header.offset_groups, type: group, repeat: expr, repeat-expr: header.num_groups}
  groups_size_:
    value: "groups[0].size_ * header.num_groups"
  materials_data:
    {pos: header.offset_materials_data, type: materials_data, if: header.offset_materials_data > 0}
  meshes_data:
    {pos: header.offset_meshes_data, type: meshes_data, if: header.offset_meshes_data > 0}
  vertex_buffer:
    {pos: header.offset_vertex_buffer, size: header.size_vertex_buffer }
  index_buffer:
    {pos: header.offset_index_buffer, size: (header.num_faces * 2)}
  size_top_level_:
    value: "_root.header.version == 210 ? _root.header.size_ + 68 : _root.header.size_ + 64"

types:
  mod_header:
    seq:
      - {id: ident, contents: [0x4d, 0x4f, 0x44, 0x00]}
      - {id: version, type: u1}
      - {id: revision, type: u1}
      - {id: num_bones, type: u2}
      - {id: num_meshes, type: u2}
      - {id: num_materials, type: u2}
      - {id: num_vertices, type: u4}
      - {id: num_faces, type: u4}
      - {id: num_edges, type: u4}
      - {id: size_vertex_buffer, type: u4}
      - {id: reserved_01, type: u4}
      - {id: num_groups, type: u4}
      - {id: offset_bones_data, type: u4}
      - {id: offset_groups, type: u4}
      - {id: offset_materials_data, type: u4}
      - {id: offset_meshes_data, type: u4}
      - {id: offset_vertex_buffer, type: u4}
      - {id: offset_index_buffer, type: u4}
      - {id: size_file, type: u4}
    instances:
      size_:
        value: 64

  bones_data:
    seq:
      - {id: bones_hierarchy, type: bone, repeat: expr, repeat-expr: _root.header.num_bones}
      - {id: parent_space_matrices, type: matrix4x4, repeat: expr, repeat-expr: _root.header.num_bones}
      - {id: inverse_bind_matrices, type: matrix4x4, repeat: expr, repeat-expr: _root.header.num_bones}
      - {id: bone_map, size: 256, if: _root.header.num_bones != 0}
    instances:
      size_:
        value: |
          _root.header.num_bones > 0 ?
          _root.header.num_bones * bones_hierarchy[0].size_ +
          _root.header.num_bones * 64 +
          _root.header.num_bones * 64 +
          256 : 0

  bone:
    seq:
      - {id: idx_anim_map, type: u1}
      - {id: idx_parent, type: u1}
      - {id: idx_mirror, type: u1}
      - {id: idx_mapping, type: u1}
      - {id: unk_01, type: f4}
      - {id: parent_distance, type: f4}
      - {id: location, type: vec3}
    instances:
      size_:
        value: 24

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
    instances:
      size_:
        value: 32

  materials_data:
    seq:
      - {id: material_names, type: str, encoding: ASCII, size: 128, terminator: 0, repeat: expr, repeat-expr: _root.header.num_materials, if: _root.header.version == 210}
      - {id: material_hashes, type: u4, repeat: expr, repeat-expr: _root.header.num_materials, if: _root.header.version == 211}
    instances:
      size_:
        value: "_root.header.version == 210 ? 128 * _root.header.num_materials : 4 * _root.header.num_materials"

  meshes_data:
    seq:
      - {id: meshes, type: mesh, repeat: expr, repeat-expr: _root.header.num_meshes}
      - {id: num_weight_bounds, type: u4, if: _root.header.version == 211}
      - {id: weight_bounds, type: weight_bound, repeat: expr, repeat-expr: "_root.header.version == 210 ? _root.num_weight_bounds : num_weight_bounds"}
    instances:
      size_:
        value: |
          _root.header.version == 210 ?
          _root.header.num_meshes * meshes[0].size_ + _root.num_weight_bounds * weight_bounds[0].size_ :
          _root.header.num_meshes * meshes[0].size_ + num_weight_bounds * weight_bounds[0].size_
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
      - {id: num_indices, type: u4}
      - {id: face_offset, type: u4}
      - {id: bone_id_start, type: u1}
      - {id: num_unique_bone_ids, type: u1}
      - {id: mesh_index, type: u2}
      - {id: min_index, type: u2}
      - {id: max_index, type: u2}
      - {id: hash, type: u4}
    instances:
      size_:
        value: 48
      indices:
        pos: _root.header.offset_index_buffer + face_offset * 2 + face_position * 2
        repeat: expr
        repeat-expr: num_indices
        type: u2
      vertices:
        pos: _root.header.offset_vertex_buffer + vertex_offset + (vertex_position * vertex_stride)
        repeat: expr
        repeat-expr: num_vertices
        type:
          switch-on: vertex_format
          cases:
            0x4325a03e: vertex_4325 # IANonSkinTBN_4M
            0x2f55c03d: vertex_2f55 # IASkinOTB_4WT_4M
            0xa14e003c: vertex_a14e # IANonSkinBCA
            0x2082f03b: vertex_2082 # IANonSkinBLA
            0xc66fa03a: vertex_c66f # IANonSkinBA
            0xd1a47038: vertex_d1a4 # IANonSkinBL
            0x207d6037: vertex_207d # IANonSkinBC
            0xa7d7d036: vertex_a7d7 # IANonSkinB
            0x37a4e035: vertex_37a4 # IANonSkinTBNLA
            0xb6681034: vertex_b668 # IANonSkinTBNCA
            0x9399c033: vertex_9399 # IANonSkinTBCA
            0x12553032: vertex_1255 # IANonSkinTBLA
            0x747d1031: vertex_747d # IANonSkinTBNA
            0x63b6c02f: vertex_63b6 # IANonSkinTBNL
            0x926fd02e: vertex_926f # IANonSkinTBNC
            0xafa6302d: vertex_afa6 # IANonSkinTBA
            0x5e7f202c: vertex_5e7f # IANonSkinTBN
            0xb86de02a: vertex_b86d # IANonSkinTBL
            0x49b4f029: vertex_49b4 # IANonSkinTBC
            0xd8297028: vertex_8297 # IANonSkinTB
            0xcbcf7027: vertex_cbcf # IASkinTBNLA8wt
            0xd84e3026: vertex_d84e # IASkinTBC8wt
            0x75c3e025: vertex_75c3 # IASkinTBN8wt
            0xbb424024: vertex_bb42 # IASkinTB8wt
            0x64593023: vertex_6459 # IASkinTBNLA4wt
            0x77d87022: vertex_77d8 # IASkinTBC4wt
            0xdA55a021: vertex_da55 # IASkinTBN4wt
            0x14d40020: vertex_14d4 # IASkinTB4wt
            0xb392101f: vertex_b392 # IASkinTBNLA2wt
            0xa013501e: vertex_a013 # IASkinTBC2wt
            0xd9e801d:  vertex_d9e8 # IASkinTBN2wt
            0xc31f201c: vertex_c31f # IASkinTB2wt
            0xd877801b: vertex_d877 # IASkinTBNLA1wt
            0xcbf6c01a: vertex_cbf6 # IASkinTBC1wt
            0x667b1019: vertex_667b # IASkinTBN1wt
            0xa8fab018: vertex_a8fa # IASkinTB1wt
            0xa320c016: vertex_a320 # IASkinBridge8wt
            0xcb68015: vertex_cb68  # IASkinBridge4wt
            0xdb7da014: vertex_db7d # IASkinBridge2wt
            0xb0983013: vertex_b098 # IASkinBridge1wt

  vertex_4325: # 64 IANonSkinTBN_4M untested rev1 md000f mesh1 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
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
    instances:
      size_:
        value: 64

  vertex_2f55: # 64 IASkinOTB_4WT_4M rehd pl0b.arc pl0b.mod mesh2
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1} #signed in maxscript
      - {id: occlusion, type: u1}
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
    instances:
      size_:
        value: 64

  vertex_a14e: # 28 IANonSkinBCA untested md000d_00 mesh0 
    seq:
       - {id: position, type: vec3}
       - {id: normal, type: vec4_u1}
       - {id: uv, type: vec2_half_float}
       - {id: uv2, type: vec2_half_float}
       - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 28
        
  vertex_2082: # 28 IANonSkinBLA s1030_00scr s0503-7f mesh36 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
    instances:
      size_:
        value: 28

  vertex_c66f: # 24 IANonSkinBA usm9110.arc sm9110.mod mesh1 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 24

# IANonSkinBL_LA not found

  vertex_d1a4: # 24 IANonSkinBL
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 24

  vertex_207d: # 24 IANonSkinBC
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 24
        
  vertex_a7d7: #20 IANonSkinB rev1 s10a_1_scroll.arc s10a_bgl1.mod 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
    instances:
      size_:
        value: 20

  vertex_37a4: # 36 IANonSkinTBNLA s1010_00Scr.arc s0102_g  mesh1 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
    instances:
      size_:
        value: 36
        
  vertex_b668: # 36 IANonSkinTBNCA untested md002b_00 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
      - {id: uv3, type: vec2_half_float}
    instances:
      size_:
        value: 36
        
  vertex_9399: # 32 IANonSkinTBCA
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 32

  vertex_1255: # 32 IANonSkinTBLA s2304_00scr.arc rouka mesh10 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float} #lightmaps
    instances:
      size_:
        value: 32

  vertex_747d: # 32 IANonSkinTBNA re6 md0022_03 
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
    instances:
      size_:
        value: 32

# IANonSkinTBNL_LA not found

  vertex_63b6: # 36 IANonSkinTBNL s2304_00scr.arc rouka.mod mesh0
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: vertex_alpha, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: occlusion, type: u4}
    instances:
      size_:
        value: 36

  vertex_926f: # 32 IANonSkinTBNC
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1} 
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 32

  vertex_afa6: # 28 IANonSkinTBA untested md0303 mesh0
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 28

  vertex_5e7f: # 28 IANonSkinTBN untested md0020 mesh0
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 28

# IANonSkinTBL_LA not found

  vertex_b86d: # 32 IANonSkinTBL rer2 s2304_00Scr.arc bedroom.mod mesh14
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: vertex_alpha, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: occlusion, type: u4}
    instances:
      size_:
        value: 32

  vertex_49b4: # 28 IANonSkinTBC s1030_00scr.arc cast_a.mod
    seq:
       - {id: position, type: vec3}
       - {id: normal, type: vec3_u1}
       - {id: occlusion, type: u1}
       - {id: tangent, type: vec4_u1}
       - {id: uv, type: vec2_half_float}
       - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 28

  vertex_8297: # 24 IANonSkinTB rev1 s500_scroll.arc s500_2.mod mesh0
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
    instances:
      size_:
        value: 24

  vertex_cbcf: # 48 IASkinTBNLA8wt untested re6 em5030 mesh82 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2}
      - {id: tangent, type: vec4_u1}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
    instances:
      size_:
        value: 48

  vertex_d84e: # 40 IASkinTBC8wt ok rehd r313_g05 
    seq:
      - {id: position, type: vec4_s2} # w1
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: tangent, type: vec4_u1}
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 40

  vertex_75c3: # 40 IASkinTBN8wt untested re6 em4801 mesh20 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2}
      - {id: tangent, type: vec4_u1}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 40

  # TODO: check rev2 sm8683.mod mesh4 uncorrect weights is fixes
  vertex_bb42: # 36 IASkinTB8wt
    seq:
      - {id: position, type: vec4_s2} # w1
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4} # w2-w5
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values2, size: 2, repeat: expr, repeat-expr: 2} # w6-w7
      - {id: tangent, type: vec4_u1}
    instances:
      size_:
        value: 36

  vertex_6459: # 40 IASkinTBNLA4wt wp1800 mesh4 
    seq:
      - {id: position, type: vec4_s2} # w = w1
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
    instances:
      size_:
        value: 40

  vertex_77d8: # 32 IASkinTBC4wt rev1 bl_center_t2 
    seq:
      - {id: position, type: vec4_s2} # w = w1
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 32

  vertex_da55: # 32 IASkinTBN4wt untested re6 sm5933 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1} # 4th byte occlusion
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 32

  vertex_14d4: # 28 IASkinTB4wt  _24 rev2 wp1500 
    seq:
      - {id: position, type: vec4_s2}  # FIXME upl2140.arc
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: uv, type: vec2_half_float}
      - {id: weight_values, size: 2, repeat: expr, repeat-expr: 2}  # half-float
    instances:
      size_:
        value: 28

  vertex_b392: # 36 IASkinTBNLA2wt wp1800 mesh8 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2}  # half-float
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
    instances:
      size_:
        value: 36

  vertex_a013: # 28 IASkinTBC2wt untested uSm8754.arc sm8754.mod mesh2 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1} 
      - {id: uv, type: vec2_half_float}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2} # half float probably
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 28

  vertex_d9e8: # 28 IASkinTBN2wt untested re6 sm6290 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2}
      - {id: uv, type: vec2_half_float}
    instances:
      size_:
        value: 28
        
  vertex_c31f: #  24 IASkinTB2wt rev2 fig01.arc pl2200.mod mesh17 posed hands 
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: bone_indices, size: 2, repeat: expr, repeat-expr: 2}
    instances:
      size_:
        value: 24

  vertex_d877: # 32 IASkinTBNLA1wt wp1800 mesh6 
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}
      - {id: uv4, type: vec2_half_float}
    instances:
      size_:
        value: 32

  vertex_cbf6: # 24 IASkinTBC1wt wp3000 mesh1 
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}
    instances:
      size_:
        value: 24

  vertex_667b: # 24 IASkinTBN1wt uSm8771.arc sm8771.mod mesh1  
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
    instances:
      size_:
        value: 24

  vertex_a8fa: # 20 IASkinTB1wt rev2 wp6040.mod mesh4 
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1} # maybe bone and weight
      - {id: normal, type: vec3_u1}
      - {id: occlusion, type: u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
    instances:
      size_:
        value: 20

# IASkinBridge4wt4M not found

  vertex_a320: # 28 IASkinBridge8wt rehd pl0b.arc pl0b.mod mesh35 
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8} 
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 8}
      - {id: normal, type: vec4_u1}
    instances:
      size_:
        value: 28

  vertex_cb68: # 20 IASkinBridge4wt line rev2 uwp3010.mod sm8698.mod mesh3
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4} 
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: normal, type: vec4_u1}
    instances:
      size_:
        value: 20

  vertex_db7d: # 16 IASkinBridge2wt rev2 uwp3010.mod sm8698.mod mesh2
    seq:
      - {id: position, type: vec4_s2}
      - {id: normal, type: vec4_u1}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4} # strange 0x80 2 and 4 values
    instances:
      size_:
        value: 16

  vertex_b098: # 12 IASkinBridge1wt sm8799.mod
    seq:
      - {id: position, type: vec3_s2}
      - {id: bone_indices, type: u2, repeat: expr, repeat-expr: 1}
      - {id: normal, type: vec4_u1}
    instances:
      size_:
        value: 12

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
      - {id: oabb, type: matrix4x4}
      - {id: oabb_dimension, type: vec4}

    instances:
      size_:
        value: 144
