meta:
  endian: le
  bit-endian: le
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
  - {id: model_info, type: model_info}
  - {id: rcn_header, type: rcn_header}
  - {id: rcn_tables, type: rcn_table, repeat: expr, repeat-expr: rcn_header.num_tbl}
  - {id: rcn_vertices, type: rcn_vertex, repeat: expr, repeat-expr: rcn_header.num_vtx}
  - {id: rcn_trianlges, type: rcn_triangle, repeat: expr, repeat-expr: rcn_header.num_tri}

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

  model_info:
    seq:
      - {id: middist, type: s4}
      - {id: lowdist, type: s4}
      - {id: light_group, type: u4}
      - {id: strip_type, type: u1}
      - {id: memory, type: u1}
      - {id: reserved, type: u2}
    instances:
      size_:
        value: 16
        
  rcn_header:
    seq:
      - {id: ptri, type: u4}
      - {id: pvtx, type: u4}
      - {id: ptb, type: u4}
      - {id: num_tri, type: u4}
      - {id: num_vtx, type: u4}
      - {id: num_tbl, type: u4}
      - {id: parts, type: u4}
      - {id: reserved, type: u4}
    instances:
      size_:
        value: 32
      
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

  rcn_table:
    seq:
      - {id: vindex, type: b21}
      - {id: noffset, type: b10}
      - {id: edge, type: b1}

  rcn_vertex:
    seq:
      - {id: x, type: u2}
      - {id: y, type: u2}
      - {id: z, type: u2}
      - {id: w, type: u2}
      - {id: w0, type: u1}
      - {id: w1, type: u1}
      - {id: w2, type: u1}
      - {id: w3, type: u1}
      - {id: j0, type: u1}
      - {id: j1, type: u1}
      - {id: j2, type: u1}
      - {id: j3, type: u1}

  rcn_triangle:
    seq:
      - {id: v0, type: b21}
      - {id: v1, type: b21}
      - {id: v2, type: b21}
      - {id: reserved, type: b1}

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

  group: # parts_info
    seq:
      - {id: group_index, type: u4}
      - {id: reserved, type: u4, repeat: expr, repeat-expr: 3}
      - {id: pos, type: vec3} # sphere
      - {id: radius, type: f4}
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
      - {id: fog_enable, type: b1}
      - {id: zwrite, type: b1}
      - {id: attr, type: b12}
      - {id: num, type: b8}
      - {id: envmap_bias, type: b5}
      - {id: vtype, type: b3}
      - {id: uvscroll_enable, type: b1}
      - {id: ztest, type: b1}
      
      - {id: func_skin, type: b4}
      - {id: func_reserved2, type: b2}
      - {id: func_lighting, type: b4}
      - {id: func_normalmap, type: b4}
      - {id: func_specular, type: b4} 
      - {id: func_lightmap, type: b4}
      - {id: func_multitexture, type: b4}
      - {id: func_reserved, type: b6}

      - {id: htechnique, type: u4}
      - {id: pipeline, type: u4}
      - {id: pvdeclbase, type: u4}
      - {id: pvdecl, type: u4}
      - {id: basemap, type: u4}
      - {id: normalmap, type: u4}
      - {id: maskmap, type: u4}
      - {id: lightmap, type: u4}
      - {id: shadowmap, type: u4}
      - {id: additionalmap, type: u4}
      - {id: envmap, type: u4}
      - {id: detailmap, type: u4}
      - {id: occlusionmap, type: u4}
      - {id: transparency, type: f4}

      - {id: fresnel_factor, type: f4, repeat: expr, repeat-expr: 4}
      - {id: lightmap_factor, type: f4, repeat: expr, repeat-expr: 4}
      - {id: detail_factor, type: f4, repeat: expr, repeat-expr: 4}
      - {id: reserved1, type: u4}
      - {id: reserved2, type: u4}
      - {id: lightblendmap, type: u4}
      - {id: shadowblendmap, type: u4}
      - {id: parallax_factor, type: f4, repeat: expr, repeat-expr: 2}
      - {id: flip_binormal, type: f4}
      - {id: heightmap_occ, type: f4}
      - {id: blend_state, type: u4}
      - {id: alpha_ref, type: u4}
      - {id: heightmap, type: u4}
      - {id: glossmap, type: u4}
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
      - {id: disp, type: u1}
      - {id: level_of_detail, type: u1}
      - {id: alpha_priority, type: u1} # alphapri
      - {id: max_bones_per_vertex, type: u1} # weight_num
      - {id: vertex_stride, type: u1}
      - {id: vertex_stride_2, type: u1}
      - {id: connective, type: u1}
      - {id: shape, type: b1}
      - {id: env, type: b1}
      - {id: refrect, type: b1}
      - {id: reserved2, type: b2}
      - {id: shadow_cast, type: b1}
      - {id: shadow_receive, type: b1}
      - {id: sort, type: b1}
      - {id: num_vertices, type: u2}
      - {id: vertex_position_end, type: u2}
      - {id: vertex_position_2, type: u4}
      - {id: vertex_offset, type: u4}
      - {id: vertex_offset_2, type: u4} # second vertex buffer offset
      - {id: face_position, type: u4} # index_ofs
      - {id: num_indices, type: u4}
      - {id: face_offset, type: u4} # index_base
      - {id: vdeclbase, type: u1}
      - {id: vdecl, type: u1}
      - {id: vertex_position, type: u2} # min_index
      - {id: num_weight_bounds, type: u1} # probably num of OABB boundng volumes
      - {id: idx_bone_palette, type: u1} # envelope
      - {id: rcn_base, type: u2} 
      - {id: boundary, type: u4} # pointer in theory to the related weight_bounds
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
          switch-on: _root.materials_data.materials[idx_material].vtype
          cases:
            0: vf_skin
            1: vf_skin_ex
            2: vf_non_skin
            3: vf_non_skin_col
            4: vf_skin # shape
            5: vf_skin # skin color?
      vertices2:
        pos: _root.header.offset_vertex_buffer_2 + (vertex_position_2 * vertex_stride_2) + vertex_offset_2
        repeat: expr
        repeat-expr: num_vertices
        type:
          switch-on: vertex_stride_2
          cases:
            4: vertex2_4
            8: vertex2_8
        if: vertex_stride_2>0

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

  vec2:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}

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

  vf_non_skin:
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: uv3, type: vec2_half_float}

  vf_non_skin_col:
    seq:
      - {id: position, type: vec3}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}
      - {id: rgba, type: vec4_u1}

  vf_skin:
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 4}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 4}
      - {id: normal, type: vec4_u1}
      - {id: tangent, type: vec4_u1}
      - {id: uv, type: vec2_half_float}
      - {id: uv2, type: vec2_half_float}

  vf_skin_ex:
    seq:
      - {id: position, type: vec4_s2}
      - {id: bone_indices, type: u1, repeat: expr, repeat-expr: 8}
      - {id: weight_values, type: u1, repeat: expr, repeat-expr: 8}
      - {id: normal, type: vec4_u1}
      - {id: uv, type: vec2_half_float}

  vertex2_4:
    seq:
      - {id: occlusion, type: vec4_u1}

  vertex2_8:
    seq:
      - {id: occlusion, type: vec4_u1}
      - {id: tangent, type: vec4_u1}