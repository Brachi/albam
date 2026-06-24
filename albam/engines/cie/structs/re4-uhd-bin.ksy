
meta:
  id: re4_uhd_bin
  endian: le
  ks-version: "0.11"
  title: Capcom Internal Engine 3d model file

seq:
  - {id: header, type: uhd_bin_header}

instances:
  bones:
    {pos: header.offset_bones, type: bone, repeat: expr, repeat-expr: header.num_bones}
  weights:
    pos: header.offset_weights
    type:
      switch-on: header.num_weights2 > 255
      cases:
        true: fmtbin_weight_ext
        false: fmtbin_weight
    repeat: expr
    repeat-expr: header.num_weights
  bone_pairs:
    {pos: header.offset_bonepairs, type: bone_pair, if: header.offset_bonepairs > 0}
  adjacent:
    {pos: header.offset_adjacents, type: bone_adj, if: header.offset_adjacents > 0}
  vertex_positions:
    {pos: header.offset_vertex_position, type: vec3, repeat: expr, repeat-expr: header.num_vertices}
  normals:
    {pos: header.offset_vertex_normals, type: vec3, repeat: expr, repeat-expr: header.num_vertex_normals}
  indexes:
    {pos: header.offset_index_buffer, type: u2, repeat: expr, repeat-expr: header.num_vertices, if: header.offset_index_buffer > 0}
  indexes2:
    {pos: header.offset_index_buffer2, type: u2, repeat: expr ,repeat-expr: header.num_vertices, if: header.offset_index_buffer2 > 0}
  vertex_colors:
    {pos: header.offset_vertex_colors, type: rgba, repeat: expr, repeat-expr: header.num_vertices, if: header.offset_vertex_colors > 0}
  texcoords:
    {pos: header.offset_vertex_texcoord, type: uv, repeat: expr ,repeat-expr: header.num_vertices}

  materials:
    pos: header.offset_materials
    type: material
    repeat: expr
    repeat-expr: header.num_materials

types:
  uhd_bin_header:
    seq:
      - {id: offset_bones, type: u4} # bone_offset
      - {id: unk_00, type: u4} # unknown_x04 //--zeros
      - {id: unk_01, type: u4} #unknown_x08 adress to blank area
      - {id: offset_vertex_colors, type: u4} # vertex_colour_offset
      - {id: offset_vertex_texcoord, type: u4} # vertex_texcoord_offset
      - {id: offset_weights, type: u4} # weight_offset
      - {id: num_weights, type: u1} # weights_count
      - {id: num_bones, type: u1} # bone_count
      - {id: num_materials, type: u2} # material_count
      - {id: offset_materials, type: u4} # material_offset
      - {id: texture1_flags, type: u2} # bin flags
      - {id: texture2_flags, type: u2}
      - {id: num_tpl, type: u4} # tpl_count
      - {id: vertex_scale, type: u1}
      - {id: unk_02, type: u1}
      - {id: num_weights2, type: u2} # weight2_count
      - {id: offset_morphs, type: u4} # morph_offset
      - {id: offset_vertex_position, type: u4} # vertex_position_offset
      - {id: offset_vertex_normals, type: u4} # vertex_normal_offset
      - {id: num_vertices, type: u2} #  vertex_position_count
      - {id: num_vertex_normals, type: u2} # vertex_normal_count
      - {id: version_flags, type: u4}
      - {id: offset_bonepairs, type: u4} # bonepair_offset
      - {id: offset_adjacents, type: u4} # adjacent_offset
      - {id: offset_index_buffer, type: u4} # vertex_weight_index_offset
      - {id: offset_index_buffer2, type: u4} # vertex_weight2_index_offset
    instances:
      size_:
        value: 96

  bone_adj:
    seq:
      - {id: count, type: u1, repeat: expr, repeat-expr: 4}
      - id: adj
        type: u2
        repeat: expr
        repeat-expr: count[3] # num bones?
    instances:
      size_:
        value: 4 + count[3] * 2

  bone_pair:
    seq:
      - {id: num_pair, type: u4}
      - {id: line, type: pair_line, repeat: expr, repeat-expr: num_pair}
    instances:
      size_:
        value: 4 + 8*num_pair

  pair_line:
    seq:
      - {id: data, size: 8}

  bone:
    seq:
      - {id: bone_id, type: u1}
      - {id: parent, type: u1}
      - {id: filler, type: u2}
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  material:
    seq:
      - {id: unk_min_11, type: u1}
      - {id: unk_min_10, type: u1}
      - {id: unk_min_09, type: u1}
      - {id: unk_min_08, type: u1}
      - {id: unk_min_07, type: u1}
      - {id: unk_min_06, type: u1}
      - {id: unk_min_05, type: u1}
      - {id: unk_min_04, type: u1}
      - {id: unk_min_03, type: u1}
      - {id: unk_min_02, type: u1}
      - {id: unk_min_01, type: u1}
      - {id: material_flag, type: u1}
      - {id: diffuse_map, type: u1}
      - {id: bump_map, type: u1}
      - {id: opacity_map, type: u1}
      - {id: generic_specular_map, type: u1}
      - {id: intensity_specular_r, type: u1}
      - {id: intensity_specular_g, type: u1}
      - {id: intensity_specular_b, type: u1}
      - {id: unk_00, type: u1}
      - {id: unk_01, type: u1}
      - {id: specular_scale, type: u1}
      - {id: unk_02, type: u1}
      - {id: custom_specular_map, type: u1}
      - {id: face_index, type: face_index}

  face_index:
    seq:
      - {id: buffer_size, type: u4}
      - {id: count, type: u4}
      - {id: strip_count, type: u4}
      - {id: strips, type: strip, repeat: expr, repeat-expr: strip_count}
      - {id: padding, size: buffer_size - (strip_count * 4 + 4)}

  strip:
    seq:
      - {id: ftype, type: u2}
      - {id: fcount, type: u2}

  fmtbin_weight_ext: #bone id 2bytes
    seq:
      - {id: bone_ids, type: u2, repeat: expr, repeat-expr: 3}
      #- {id: bone_id2, type: u2}
      #- {id: bone_id3, type: u2}
      - {id: count, type: u2}
      - {id: weights, type: u1, repeat: expr, repeat-expr: 3}
      #- {id: weight2, type: u1}
      #- {id: weight3, type: u1}
      - {id: unk00, type: u1}

  fmtbin_weight:
    seq:
      - {id: bone_ids, type: u1, repeat: expr, repeat-expr: 3}
      #- {id: bone_id2, type: u1}
      #- {id: bone_id3, type: u1}
      - {id: count, type: u1}
      - {id: weights, type: u1, repeat: expr, repeat-expr: 3}
      #- {id: weight2, type: u1}
      #- {id: weight3, type: u1}
      - {id: unk00, type: u1}

  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  uv:
    seq:
      - {id: u, type: f4}
      - {id: v, type: f4}

  rgba:
    seq:
      - {id: a, type: u1}
      - {id: r, type: u1}
      - {id: g, type: u1}
      - {id: b, type: u1}
