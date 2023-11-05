meta:
  endian: le
  file-extension: mod
  id: mod_156
  ks-version: 0.11
  title: MTFramework model format 156

seq:
  - {id: header, type: mod_header}
  - {id: reserved_01, type: u4}
  - {id: reserved_02, type: u4}
  - {id: bsphere, type: vec4}
  - {id: bbox_min, type: vec4}
  - {id: bbox_max, type: vec4}
  - {id: unk_01, type: u4}
  - {id: unk_02, type: u4}
  - {id: unk_03, type: u4}
  - {id: unk_04, type: u4}
  - {id: unk_05, type: u4}
  - {id: unk_06, type: u4}
  - {id: unk_07, type: u4}
  - {id: unk_08, type: u4}
  - {id: num_vtx8_unk_faces, type: u4}
  - {id: num_vtx8_unk_uv, type: u4}
  - {id: num_vtx8_unk_normals, type: u4}
  - {id: reserved_03, type: u4}
  - {id: vtx8_unk_faces, type: unk_vtx8_block_00, repeat: expr, repeat-expr: num_vtx8_unk_faces}
  - {id: vtx8_unk_uv, type: unk_vtx8_block_01, repeat: expr, repeat-expr: num_vtx8_unk_uv}
  - {id: vtx8_unk_normals, type: unk_vtx8_block_02, repeat: expr, repeat-expr: num_vtx8_unk_normals}

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
    {pos: header.offset_vertex_buffer, size: header.size_vertex_buffer, if: header.offset_vertex_buffer > 0}
  vertex_buffer_2:
    {pos: header.offset_vertex_buffer, size: header.size_vertex_buffer_2, if: header.offset_vertex_buffer_2 > 0}
  index_buffer:
    {pos: header.offset_index_buffer, size: (header.num_faces * 2) - 2, if: header.offset_index_buffer > 0}
  size_top_level_:
    value: _root.header.size_ + 104

types:
  mod_header:
    seq:
      - {id: ident, contents: [0x4d, 0x4f, 0x44, 0x00]}
      - {id: version, type: u1}  # 156
      - {id: revision, type: u1}
      - {id: num_bones, type: u2}
      - {id: num_meshes, type: u2}
      - {id: num_materials, type: u2}
      - {id: num_vertices, type: u4}
      - {id: num_faces, type: u4}
      - {id: num_edges, type: u4}
      - {id: size_vertex_buffer, type: u4}
      - {id: size_vertex_buffer_2, type: u4}
      - {id: num_textures, type: u4}
      - {id: num_groups, type: u4}
      - {id: num_bone_palettes, type: u4}
      - {id: offset_bones_data, type: u4}
      - {id: offset_groups, type: u4}
      - {id: offset_materials_data, type: u4}
      - {id: offset_meshes_data, type: u4}
      - {id: offset_vertex_buffer, type: u4}
      - {id: offset_vertex_buffer_2, type: u4}
      - {id: offset_index_buffer, type: u4}
    instances:
      size_:
        value: 72
  bones_data:
    seq:
      - {id: bones_hierarchy, type: bone, repeat: expr, repeat-expr: _root.header.num_bones}
      - {id: parent_space_matrices, type: matrix4x4, repeat: expr, repeat-expr: _root.header.num_bones}
      - {id: inverse_bind_matrices, type: matrix4x4, repeat: expr, repeat-expr: _root.header.num_bones}
      - {id: bone_map, size: 256, if: _root.header.num_bones != 0}
      - {id: bone_palettes, type: bone_palette, repeat: expr, repeat-expr: _root.header.num_bone_palettes}
    instances:
      size_:
        value: |
          _root.header.num_bones > 0 ?
          _root.header.num_bones * bones_hierarchy[0].size_ +
          _root.header.num_bones * 64 +
          _root.header.num_bones * 64 +
          256 +
          _root.header.num_bone_palettes * bone_palettes[0].size_
          : 0

  unk_vtx8_block_00:
    seq:
      - {id: idx, type: u2}
      - {id: unk_00, type: u2}

  unk_vtx8_block_01:
    seq:
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: unk_03, type: u4}
      - {id: unk_05, type: u2}
      - {id: unk_06, type: u2}
      - {id: unk_07, type: u2}
      - {id: unk_08, type: u2}

  unk_vtx8_block_02:
    seq:
      - {id: unk_00, type: u2}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: unk_03, type: u2}

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

  bone_palette:
    seq:
      - {id: unk_01, type: u4}
      - {id: indices, type: u1, repeat: expr, repeat-expr: 32}
    instances:
      size_:
        value: 36

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
      - {id: textures, type: str, encoding: ASCII, size: 64, terminator: 0, repeat: expr, repeat-expr: _root.header.num_textures}
      - {id: materials, type: material, repeat: expr, repeat-expr: _root.header.num_materials}
    instances:
      size_:
        value: 64 * _root.header.num_textures + _root.header.num_materials * materials[0].size_

  material:
    seq:
      - {id: use_translucent, type: b1}
      - {id: use_opaque, type: b1}
      - {id: unk_flag_03, type: b1}
      - {id: unk_flag_04, type: b1}
      - {id: unk_flag_05, type: b1}
      - {id: unk_flag_06, type: b1}
      - {id: unk_flag_07, type: b1}
      - {id: unk_flag_08, type: b1}


      - {id: unk_flag_09, type: b1}
      - {id: unk_flag_10, type: b1}
      - {id: unk_flag_11, type: b1}
      - {id: unk_flag_12, type: b1}
      - {id: unk_flag_13, type: b1}
      - {id: unk_flag_14, type: b1}
      - {id: unk_flag_15, type: b1}
      - {id: use_alpha, type: b1}

      - {id: unk_flag_17, type: b1}
      - {id: unk_flag_18, type: b1}
      - {id: unk_flag_19, type: b1}
      - {id: unk_flag_20, type: b1}
      - {id: unk_flag_21, type: b1}
      - {id: unk_flag_22, type: b1}
      - {id: unk_flag_23, type: b1}
      - {id: unk_flag_24, type: b1}

      - {id: unk_flag_25, type: b1}
      - {id: unk_flag_26, type: b1}
      - {id: unk_flag_27, type: b1}
      - {id: unk_flag_28, type: b1}
      - {id: use_8_bones, type: b1}
      - {id: unk_flag_30, type: b1}
      - {id: unk_flag_31, type: b1}
      - {id: unk_flag_32, type: b1}

      - {id: unk_flag_33, type: b1}
      - {id: unk_flag_34, type: b1}
      - {id: unk_flag_35, type: b1}
      - {id: unk_flag_36, type: b1}
      - {id: unk_flag_37, type: b1}
      - {id: unk_flag_38, type: b1}
      - {id: unk_flag_39, type: b1}
      - {id: unk_flag_40, type: b1}
      - {id: unk_flag_41, type: b1}
      - {id: unk_flag_42, type: b1}
      - {id: unk_flag_43, type: b1}
      - {id: unk_flag_44, type: b1}
      - {id: unk_flag_45, type: b1}
      - {id: unk_flag_46, type: b1}
      - {id: unk_flag_47, type: b1}
      - {id: unk_flag_48, type: b1}


      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: unk_03, type: u2}
      - {id: unk_04, type: u2}
      - {id: unk_05, type: u2}
      - {id: unk_06, type: u2}
      - {id: unk_07, type: u2}
      - {id: unk_08, type: u2}
      - {id: unk_09, type: u2}
      - {id: texture_slots, type: u4, repeat: expr, repeat-expr: 8}
      - {id: unk_param_01, type: f4}
      - {id: unk_param_02, type: f4}
      - {id: unk_param_03, type: f4}
      - {id: unk_param_04, type: f4}
      - {id: unk_param_05, type: f4}
      - {id: cubemap_roughness, type: f4}
      - {id: unk_param_07, type: f4}
      - {id: unk_param_08, type: f4}
      - {id: unk_param_09, type: f4}
      - {id: unk_param_10, type: f4}
      - {id: unk_param_11, type: f4}
      - {id: detail_normal_power, type: f4}
      - {id: unk_param_13, type: f4}
      - {id: unk_param_14, type: f4}
      - {id: unk_param_15, type: f4}
      - {id: unk_param_16, type: f4}
      - {id: unk_param_17, type: f4}
      - {id: unk_param_18, type: f4}
      - {id: unk_param_19, type: f4}
      - {id: unk_param_20, type: f4}
      - {id: normal_scale, type: f4}
      - {id: unk_param_22, type: f4}
      - {id: unk_param_23, type: f4}
      - {id: unk_param_24, type: f4}
      - {id: unk_param_25, type: f4}
      - {id: unk_param_26, type: f4}
    instances:
      size_:
        value: 160

  meshes_data:
    seq:
      - {id: meshes, type: mesh, repeat: expr, repeat-expr: _root.header.num_meshes}
      - {id: num_weight_bounds, type: u4}
      - {id: weight_bounds, type: weight_bound, repeat: expr, repeat-expr: num_weight_bounds}
    instances:
      size_:
        value: |
          _root.header.num_meshes * meshes[0].size_ +
          4 +
          num_weight_bounds * weight_bounds[0].size_

  mesh:
    seq:
      - {id: idx_group, type: u2}
      - {id: idx_material, type: u2}
      - {id: constant, type: u1}
      - {id: level_of_detail, type: u1}
      - {id: unk_01, type: u1}
      - {id: vertex_format, type: u1}
      - {id: vertex_stride, type: u1}
      - {id: vertex_stride_2, type: u1}
      - {id: unk_03, type: u1}
      - {id: unk_flags, type: u1} # TODO: there's one known: cast_shadows
      - {id: num_vertices, type: u2}
      - {id: vertex_position_end, type: u2}
      - {id: vertex_position_2, type: u4}
      - {id: vertex_offset, type: u4}
      - {id: unk_05, type: u4}
      - {id: face_position, type: u4}
      - {id: num_indices, type: u4}
      - {id: face_offset, type: u4}
      - {id: unk_06, type: u1}
      - {id: unk_07, type: u1}
      - {id: vertex_position, type: u2}
      - {id: num_unique_bone_ids, type: u1}
      - {id: idx_bone_palette, type: u1}
      - {id: unk_08, type: u1}
      - {id: unk_09, type: u1}
      - {id: unk_10, type: u2}
      - {id: unk_11, type: u2}
    instances:
      size_:
        value: 52
      indices:
        pos: _root.header.offset_index_buffer + face_offset * 2 + face_position * 2
        repeat: expr
        repeat-expr: num_indices
        type: u2
      vertices:
        # XXX vertex_position and vertex_position_2 are equal most of the time
        # But if using vertex_position_2 when they are not, vertices import wrongly
        # needs investigation
        pos: "vertex_position > vertex_position_2 ?  _root.header.offset_vertex_buffer + (vertex_position * vertex_stride) + vertex_offset : _root.header.offset_vertex_buffer + (vertex_position * vertex_stride) + vertex_offset"
        repeat: expr
          #repeat-expr: num_vertices # TODO: special case
        repeat-expr: "vertex_position > vertex_position_2 ? vertex_position_end - vertex_position + 1 : num_vertices"
        type:
          switch-on: vertex_format
          cases:
            0: vertex_0
            1: vertex
            2: vertex
            3: vertex
            4: vertex
            5: vertex_5
            6: vertex_5
            7: vertex_5
            8: vertex_5

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

  vec4_u1:
    seq:
      - {id: x, type: u1}
      - {id: y, type: u1}
      - {id: z, type: u1}
      - {id: w, type: u1}

  vec4_s2:
    seq:
      - {id: x, type: s2}
      - {id: y, type: s2}
      - {id: z, type: s2}
      - {id: w, type: s2}

  vec2_half_float:
    seq:
      - {id: u, size: 2}
      - {id: v, size: 2}

  matrix4x4:
    seq:
      - {id: row_1, type: vec4}
      - {id: row_2, type: vec4}
      - {id: row_3, type: vec4}
      - {id: row_4, type: vec4}

  vertex_0:
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}

  vertex:
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}

  vertex_5:
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 8}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
