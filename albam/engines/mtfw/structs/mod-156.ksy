meta:
  endian: le
  file-extension: mod
  id: mod_156
  ks-version: 0.10
  title: MTFramework model format 156

seq:
  - {id: header, type: mod_header}
  - {id: bones, type: bone, repeat: expr, repeat-expr: header.num_bones}
  - {id: parent_space_matrices, type: matrix4x4, repeat: expr, repeat-expr: header.num_bones}
  - {id: inverse_bind_matrices, type: matrix4x4, repeat: expr, repeat-expr: header.num_bones}
  - {id: bone_map, size: 256, if: header.num_bones != 0}
  - {id: bones_mapping, type: bone_mapping, repeat: expr, repeat-expr: header.num_bone_mappings}
  - {id: groups, type: group, repeat: expr, repeat-expr: header.num_groups}
  - {id: textures, type: str, encoding: ascii, size: 64, terminator: 0, repeat: expr, repeat-expr: header.num_textures}
  - {id: materials, type: material, repeat: expr, repeat-expr: header.num_materials}
  - {id: meshes, type: mesh, repeat: expr, repeat-expr: header.num_meshes}
  - {id: num_weight_bounds, type: u4}
  - {id: weight_bounds, type: weight_bound, repeat: expr, repeat-expr: num_weight_bounds}
  - {id: vertex_buffer, size: header.size_vertex_buffer}
  - {id: vertex_buffer_2, size: header.size_vertex_buffer_2}
  - {id: index_buffer, size: (header.num_faces * 2) - 2}

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
      - {id: num_bone_mappings, type: u4}
      - {id: offset_bones, type: u4}
      - {id: offset_groups, type: u4}
      - {id: offset_textures, type: u4}
      - {id: offset_meshes, type: u4}
      - {id: offset_buffer_vertices, type: u4}
      - {id: offset_buffer_vertices_2, type: u4}
      - {id: offset_buffer_indices, type: u4}
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
      - {id: unk_09, type: u4}
      - {id: unk_10, type: u4}
      - {id: unk_11, type: u4}
      - {id: reserved_03, type: u4}
      - {id: unk_12, size: offset_bones - 176, if: unk_08 !=  0}

  bone:
    seq:
      - {id: idx_anim_map, type: u1}
      - {id: idx_parent, type: u1}
      - {id: idx_mirror, type: u1}
      - {id: idx_mapping, type: u1}
      - {id: unk_01, type: f4}
      - {id: parent_distance, type: f4}
      - {id: location, type: vec3}

  bone_mapping:
    seq:
      - {id: unk_01, type: u4}
      - {id: indices, size: 32}

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
      - {id: unk_flags, type: u2}
      - {id: unk_shorts, type: u2, repeat: expr, repeat-expr: 10}
      - {id: texture_slots, type: u4, repeat: expr, repeat-expr: 8}
      - {id: unk_floats, type: f4, repeat: expr, repeat-expr: 26}

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
      - {id: face_count, type: u4}
      - {id: face_offset, type: u4}
      - {id: unk_06, type: u1}
      - {id: unk_07, type: u1}
      - {id: vertex_position, type: u2}
      - {id: vertex_group_count, type: u1}
      - {id: bone_map_index, type: u1}
      - {id: unk_08, type: u1}
      - {id: unk_09, type: u1}
      - {id: unk_10, type: u2}
      - {id: unk_11, type: u2}
    instances:
      indices:
        pos: _root.header.offset_buffer_indices + face_offset * 2 + face_position * 2
        repeat: expr
        repeat-expr: face_count
        type: u2
      vertices:
        # XXX vertex_position and vertex_position_2 are equal most of the time
        # But if using vertex_position_2 when they are not, vertices import wrongly
        # needs investigation
        pos: _root.header.offset_buffer_vertices + (vertex_position * vertex_stride) + vertex_offset
        repeat: expr
        repeat-expr: num_vertices # TODO: special case
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
