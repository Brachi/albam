
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
  # num_weights is a u1 and cannot hold the real count past 255; num_weights2
  # is the u2 that takes over there. The entry layout does not change with it
  # - the two files known to use 2-byte bone ids are an anomaly of their own,
  # not something this count selects.
  weights:
    pos: header.offset_weights
    type: fmtbin_weight
    repeat: expr
    repeat-expr: 'header.num_weights2 > 255 ? header.num_weights2 : header.num_weights'
    if: header.offset_weights > 0
  morphs:
    {pos: header.offset_morphs, type: morph_block, if: header.offset_morphs > 0 }
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
      # Doubles as the header's own size: 0x40, 0x50 or 0x60. The shorter
      # ones stop before the four trailing offsets. albam writes 0x60.
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
      # One word of flags, nothing to do with textures. 0x80000000 is set on
      # every mesh .bin and on nothing else, which is what tells a model
      # apart from the camera, lighting and collision data that share the
      # extension. Values seen across a sampled model set, and no others:
      # 0x80000000, 0x80000200, 0x80000300, 0xa0000000, 0xa0000200,
      # 0xa0000300.
      #   0x80000000 always set on a mesh
      #   0x40000000 vertex colours are used - never seen set, though every
      #              sampled model still carries a non-zero colour offset
      #   0x20000000 alternate normals
      #   0x00000200 the adjacency block is present
      #   0x00000100 the bone-pair block is present
      - {id: flags, type: u4}
      # How many .tpl slots the materials address. A model does not name its
      # .tpl, so this count is one of the things that pairs it with the right
      # one in its archive - see albam/engines/cie/mesh.py's choose_tpl.
      - {id: num_tpl, type: u4} # tpl_count
      # The exponent of the divisor morph deltas are stored against:
      # delta / 2 ** vertex_scale.
      - {id: vertex_scale, type: u1} # used for converting morphs
      - {id: unk_02, type: u1}
      - {id: num_weights2, type: u2} # weight2_count
      - {id: offset_morphs, type: u4} # morph_offset
      - {id: offset_vertex_position, type: u4} # vertex_position_offset
      - {id: offset_vertex_normals, type: u4} # vertex_normal_offset
      # Both counts are u2 and the format shares no vertices between faces,
      # so a model needing more than 0xFFFF corners cannot state it here.
      - {id: num_vertices, type: u2} #  vertex_position_count
      - {id: num_vertex_normals, type: u2} # vertex_normal_count
      # A build stamp, shipped as one of exactly two date-shaped values:
      # 0x20030818 where the adjacency and bone-pair blocks are present,
      # 0x20010801 where they are not, always in step with unk_01.
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

  morph_block:
    seq:
      - {id: num_morph_groups, type: u4}
      - {id: morph_groups, type: morph_group, repeat: expr, repeat-expr: num_morph_groups}

  morph_group:
    seq:
      - {id: offset, type: u4}
      - {id: num_vertices, type: u4}
    instances:
      body:
        pos: _root.header.offset_morphs + offset
        type: morph_group_body

  morph_group_body:
    seq:
      - {id: header, type: u4}
      - {id: vertices, type: morph_vertex, repeat: expr, repeat-expr: _parent.num_vertices}

  morph_vertex:
    seq:
      - {id: id, type: u2}
      - {id: position, type: vec3s2}
      #- {id: pos_x, type: s2}
      #- {id: pos_y, type: s2}
      #- {id: pos_z, type: s2}

  bone_pair:
    seq:
      - {id: num_pair, type: u4}
      - {id: line, type: pair_line, repeat: expr, repeat-expr: num_pair}
    instances:
      size_:
        value: 4 + 8*num_pair

  # Four bone ids; what the fourth is for is unknown.
  pair_line:
    seq:
      - {id: data, size: 8}

  # Positions are local offsets from the parent, in the same units as
  # vertices. Bone ids are not guaranteed unique across a model.
  bone:
    seq:
      - {id: bone_id, type: u1}
      # 0xFF means no parent.
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
      # Which of the texture slots below the game actually binds:
      #   0x01 bump_map
      #   0x02 generic_specular_map
      #   0x04 opacity_map
      #   0x10 custom_specular_map
      # 0x08, 0x20, 0x40 and 0x80 are unexplained. A slot holding 0xFF is
      # unused regardless.
      - {id: material_flag, type: u1}
      - {id: diffuse_map, type: u1}
      - {id: bump_map, type: u1}
      - {id: opacity_map, type: u1}
      # Unlike the other slots this is not an index into the model's .tpl:
      # it is a texture id inside one fixed texture pack.
      - {id: generic_specular_map, type: u1}
      - {id: intensity_specular_r, type: u1}
      - {id: intensity_specular_g, type: u1}
      - {id: intensity_specular_b, type: u1}
      - {id: unk_00, type: u1}
      - {id: unk_01, type: u1}
      # Two nibbles of UV tiling for the specular map: (high + 1) across,
      # (low + 1) down.
      - {id: specular_scale, type: u1}
      - {id: unk_02, type: u1}
      - {id: custom_specular_map, type: u1}
      - {id: face_index, type: face_index}

  face_index:
    seq:
      # Measured from the strip_count word, padded up to 16.
      - {id: buffer_size, type: u4}
      # The number of triangles the strips below expand to - checked against
      # the expansion over every material group of a sampled model set.
      - {id: num_triangles, type: u4}
      - {id: strip_count, type: u4}
      - {id: strips, type: strip, repeat: expr, repeat-expr: strip_count}
      - {id: padding, size: buffer_size - (strip_count * 4 + 4)}

  # Vertices are consumed sequentially, across strips and across materials:
  # the mesh is non-indexed, so a strip's `fcount` is how many entries of
  # every per-vertex array it takes, not indices into a shared pool.
  #   ftype 5  triangle list, fcount / 3 triangles
  #   ftype 6  triangle strip, fcount - 2 triangles, alternating winding
  #   ftype 7  triangle fan around the first vertex, fcount - 2 triangles
  #   ftype 8  quad list, 2 * (fcount / 4) triangles
  # Types 5, 6 and 8 occur in real models; 7 did not appear in a sampled set.
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

  # Up to three bones per vertex. Weights are percentages out of 100, not
  # fractions of 255, and the active ones do not always sum to 100 - the
  # remainder is simply unweighted.
  fmtbin_weight:
    seq:
      - {id: bone_ids, type: u1, repeat: expr, repeat-expr: 3}
      #- {id: bone_id2, type: u1}
      #- {id: bone_id3, type: u1}
      # How many of the three slots are live, 1 to 3.
      - {id: count, type: u1}
      - {id: weights, type: u1, repeat: expr, repeat-expr: 3}
      - {id: unk00, type: u1}

  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  vec3s2:
    seq:
      - {id: x, type: s2}
      - {id: y, type: s2}
      - {id: z, type: s2}

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
