meta:
    id: reengine_mesh
    endian: le
    title: RE Engine mesh format
    ks-version: '0.11'

seq:
    - {id: id_magic, contents: [77, 69, 83, 72]}
    - {id: version, type: u4}
    - {id: file_size, type: u4}
    - {id: lod_group_name_hash, type: u4} # hash used to look up LOD-distance scaling by object category
    - {id: header, type: header}

instances:

  model_info:
    {pos: header.offset_data, type: model_info, if: header.offset_data != 0}

  bones_header:
    {pos: header.offset_bones, type: bone_header, if: header.offset_bones != 0}

  bone_aabb_group:
    {pos: header.offset_bone_aabb, type: bone_aabb_group, if: header.offset_bone_aabb != 0}

  shadow_header:
    {pos: header.offset_shadow_mesh_group, type: shadow_header, if: header.offset_shadow_mesh_group != 0}

  # A single lod_group (same type model_info.lod_group_offsets[N] each
  # point to), for occlusion-culling geometry - reached directly, with no
  # wrapping model_info-style array of LOD levels. This is what a mesh
  # with no main model tree (offset_data == 0, e.g. an "_occ.mesh" file)
  # actually has instead.
  occlusion_mesh_group:
    {pos: header.offset_occlusion_mesh_group, type: lod_group, if: header.offset_occlusion_mesh_group != 0}

  buffers_data:
    {pos: header.offset_buffers_header, type: buffers_header}

  named_nodes:
    {pos: header.offset_names, type: name_offset, repeat: expr, repeat-expr: header.num_named_nodes}

  # header.num_named_nodes's shared string table is sub-divided into 3
  # separate name-remap tables (materials/bones/blend shapes) - this one's
  # count is model_info.num_materials. Guarded the same way model_info/
  # bones_header are (both may legitimately be absent, e.g. a
  # buffers-only occlusion mesh).
  material_name_remap:
    {
      pos: header.offset_material_name_remap, type: u2, repeat: expr,
      repeat-expr: model_info.num_materials,
      if: header.offset_material_name_remap != 0 and header.offset_data != 0,
    }

  bone_name_remap:
    {
      pos: header.offset_bone_name_remap, type: u2, repeat: expr,
      repeat-expr: bones_header.num_bones,
      if: header.offset_bone_name_remap != 0 and header.offset_bones != 0,
    }

  blend_shape_name_remap:
    pos: header.offset_blend_shape_name_remap
    type: u2
    repeat: expr
    repeat-expr: >
      header.num_named_nodes -
      (header.offset_data != 0 ? model_info.num_materials : 0) -
      (header.offset_bones != 0 ? bones_header.num_bones : 0)
    if: header.offset_blend_shape_name_remap != 0

types:
  header:
    # Field identities cross-referenced against RE-Mesh-Editor (a separate,
    # more mature, non-Kaitai RE Engine mesh importer/exporter) - see
    # RESULTS.md. Every offset below is 1:1 with its pre-SF6 FileHeader,
    # same order.
    seq:
      - {id: content_flags, type: u2} # bitflags: bit0 aabb, bit1 skeleton, bit2 blend shapes, bit3 group-pivot, others unidentified
      - {id: num_named_nodes, type: u2}
      - {id: unk_01, type: u4} # real field (not padding), meaning still unknown even in RE-Mesh-Editor
      - {id: offset_data, type: u8} # main LOD/mesh-group tree (-> model_info)
      - {id: offset_shadow_mesh_group, type: u8} # -> shadow_header (metadata only - shadow LODs always alias model_info's own lod_group_offsets, never separate geometry)
      - {id: offset_occlusion_mesh_group, type: u8} # occlusion-culling mesh tree - a single LOD group (-> occlusion_mesh_group), not a full model_info
      - {id: offset_bones, type: u8}
      - {id: offset_normal_recalc, type: u8} # normal-recalculation data block, layout not modeled here
      - {id: offset_blend_shapes, type: u8} # blend shape (morph target) data, layout not modeled here
      - {id: offset_bone_aabb, type: u8} # -> bone_aabb_group (one AABB per bone_header.num_bone_maps entry, not per bone overall)
      - {id: offset_buffers_header, type: u8}
      - {id: offset_floats, type: u8} # array of unidentified Vec3 floats - unexplained upstream too
      - {id: offset_material_name_remap, type: u8} # -> material_name_remap (u2 indices into named_nodes, count = model_info.num_materials)
      - {id: offset_bone_name_remap, type: u8} # -> bone_name_remap (u2 indices into named_nodes, count = bones_header.num_bones)
      - {id: offset_blend_shape_name_remap, type: u8} # -> blend_shape_name_remap (u2 indices into named_nodes, remaining count)
      - {id: offset_names, type: u8}

  model_info:
    seq:
      - {id: num_lod_groups, type: u1}
      - {id: num_materials, type: u1}
      - {id: num_uv_layers, type: u1}
      - {id: num_skin_weights, type: u1}
      - {id: num_meshes, type: u2}
      - {id: has_32bit_index_buffer, type: u1}
      - {id: shared_lod_bits, type: u1}
      - {id: reserved_01, type: u8, if: _root.version == 386270720}  # XXX FIXME: enum with versions
      - {id: box, type: f4, repeat: expr, repeat-expr: 12} # bounding sphere (x,y,z,r) followed by AABB min/max (2 vec4)
      - {id: offset_lod_group_list, type: u8}
    instances:
      lod_group_offsets:
        {pos: offset_lod_group_list, type: lod_group_offset, repeat: expr, repeat-expr: num_lod_groups}


  name_offset:
    seq:
      - {id: offset, type: u8}
    instances:
      value:
        {pos: offset, type: strz, encoding: ascii}

  primitive_accessor:
    seq:
      - {id: primitive_type, type: u2, enum: primitive_type}
      - {id: size, type: u2}
      - {id: offset, type: u4}

  buffers_header:
    seq:
      - {id: offset_primitive_accessors, type: u8}
      - {id: offset_vertex_buffer, type: u8}
      - {id: offset_index_buffer, type: u8}
      - {id: unk_00, type: u8, if: _root.version == 21041600}
      - {id: size_vertex_buffer, type: u4}
      - {id: size_index_buffer, type: u4}
      - {id: num_unk, type: u2}
      - {id: num_primitive_accessors, type: u2}
      - {id: unk_01, type: u4}
      - {id: reserved_01, type: u4}
      - {id: unk_2, type: u2}
      - {id: unk_3, type: u2}
      - {id: unk_04, type: u8, if: _root.version == 21041600}

    instances:
      vertex_buffer:
        {pos: offset_vertex_buffer, size: size_vertex_buffer}
      index_buffer:
        {pos: offset_index_buffer, size: size_index_buffer}
      primitive_accessors:
        {pos: offset_primitive_accessors, type: primitive_accessor, repeat: expr, repeat-expr: num_primitive_accessors}


  bone_header:
    seq:
      - {id: num_bones, type: u4}
      - {id: num_bone_maps, type: u4}
      - {id: reserved_01, type: u4}
      - {id: reserved_02, type: u4}
      - {id: offset_parent_bone, type: u8}
      - {id: offset_matrix_1, type: u8}
      - {id: offset_matrix_2, type: u8}
      - {id: offset_inverse_bind_matrices, type: u8}
      - {id: bone_maps, type: u2, repeat: expr, repeat-expr: num_bone_maps}
    instances:
      bones:
        {pos: offset_parent_bone, type: bone, repeat: expr, repeat-expr: num_bones}
      # num_bones matrix4x4 entries each - confirmed via byte-range
      # (diffing a real file's round trip against itself) and plausible
      # float content (diagonal 1.0s at 20-byte strides).
      local_matrices:
        {pos: offset_matrix_1, type: matrix4x4, repeat: expr, repeat-expr: num_bones}
      world_matrices:
        {pos: offset_matrix_2, type: matrix4x4, repeat: expr, repeat-expr: num_bones}
      inverse_bind_matrices:
        {pos: offset_inverse_bind_matrices, type: matrix4x4, repeat: expr, repeat-expr: num_bones}

  bone:
    seq:
      - {id: idx, type: u2}
      # parent/sibling/child/symmetric/use_secondary_weight are all signed
      # - -1 is used as a "none" sentinel (e.g. root bones have no parent).
      - {id: parent_idx, type: s2}
      - {id: sibling_idx, type: s2}
      - {id: child_idx, type: s2}
      - {id: symmetric_idx, type: s2}
      - {id: use_secondary_weight, type: s2}
      - {id: padding_0, type: u2}
      - {id: padding_1, type: u2}

  # Confirmed against RE-Mesh-Editor's actual BoneAABBGroup.read()/write()
  # (modules/mesh/file_re_mesh.py). num_entries is bone_header.num_bone_maps's
  # count (one AABB per bone actually used for skinning, bone_maps[i]),
  # not num_bones - every sample file has num_entries < num_bones.
  bone_aabb_group:
    seq:
      - {id: num_entries, type: u8}
      # Self-referential in every sample seen (always == the position
      # right after this header) - RE-Mesh-Editor's own reader doesn't
      # seek to it either, it just reads `entries` sequentially, same as
      # here. Kept as a real field for byte-fidelity, not trusted as a
      # pointer to seek through.
      - {id: offset_entries, type: u8}
      - {id: entries, type: aabb, repeat: expr, repeat-expr: num_entries}
      # Same 16-byte file-absolute alignment pad as lod_group's own
      # trailing padding field.
      - {id: padding, size: (16 - (_io.pos % 16)) % 16}

  aabb:
    seq:
      - {id: min, type: vec4}
      - {id: max, type: vec4}

  # Confirmed against RE-Mesh-Editor's actual ShadowHeader.read()/write()
  # (modules/mesh/file_re_mesh.py) and empirically: lod_group_offsets here
  # is byte-identical to model_info's own lod_group_offsets on every real
  # file with a shadow header - shadow LODs always alias the main model's
  # geometry (RE-Mesh-Editor's own writer comment: shadow meshes can't
  # have unique LODs, the game crashes if they do). So this header is the
  # entire shadow-mesh-group region; there's no separate geometry to read.
  shadow_header:
    seq:
      - {id: lod_group_count, type: u1}
      - {id: material_count, type: u1}
      - {id: uv_count, type: u1}
      - {id: skin_weight_count, type: u1}
      - {id: total_mesh_count, type: u4}
      - {id: null_padding, type: u8, if: _root.version == 386270720}
      # Self-referential in every sample seen (always == the position
      # right after this field) - not trusted as a pointer to seek
      # through, same as bone_aabb_group's offset_entries.
      - {id: offset_offset, type: u8}
      - {id: reserved_0, type: u8, repeat: expr, repeat-expr: 6}
      - {id: lod_group_offsets, type: u8, repeat: expr, repeat-expr: lod_group_count}
      - {id: padding, size: (16 - (_io.pos % 16)) % 16}

  mesh_group_offset:
    seq:
      - {id: offset, type: u8}
    instances:
      mesh_group:
        {pos: offset, type: mesh_group}

  lod_group_offset:
    seq:
      - {id: offset, type: u8}
    instances:
      lod_group:
        {pos: offset, type: lod_group}

  # One LOD level's mesh-group tree (also what a standalone
  # occlusion_mesh_group is).
  lod_group:
    seq:
      - {id: num_mesh_groups, type: u1}
      - {id: vertex_format, type: u1}
      - {id: reserved_01, type: u2}
      - {id: distance, type: f4} # LOD switch distance
      - {id: offset_main_mesh_header, type: u8}
      - {id: mesh_groups, type: mesh_group_offset, repeat: expr, repeat-expr: num_mesh_groups}
      # Pad to 16-byte file-absolute alignment - 0 or 8 bytes depending on
      # whether num_mesh_groups is even/odd.
      - {id: padding, size: (16 - (_io.pos % 16)) % 16}

  mesh_group:
    seq:
      - {id: type, type: u1}
      - {id: num_meshes, type: u1}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u4}
      - {id: num_vertices, type: u4}
      - {id: num_indices, type: u4}
      - {id: meshes, type: mesh, repeat: expr, repeat-expr: num_meshes}

  mesh:
    seq:
      - {id: material_index, type: u1}
      - {id: is_quad, type: u1}
      - {id: vertex_buffer_index, type: u1}
      - {id: padding, type: u1}
      - {id: num_indices, type: u4}
      - {id: pos_index_buffer, type: u4}
      - {id: pos_vertex_buffer, type: u4}
      - {id: unk_01, type: u8, if: _root.version != 386270720}
    # No normals/vertex-count instance here: per-submesh vertex count
    # comes from the *next* sibling submesh's pos_vertex_buffer (or the
    # parent mesh_group's num_vertices for the last submesh in a group),
    # which Kaitai's Python target can't express from a lazily-evaluated
    # instance (no working sibling/_index lookup). The real importer
    # derives vertex count from unique index-buffer values instead (see
    # build_blender_mesh in albam/engines/reng/mesh.py).


  matrix4x4:
    seq:
      - {id: row_1, type: vec4}
      - {id: row_2, type: vec4}
      - {id: row_3, type: vec4}
      - {id: row_4, type: vec4}
        #instances:
        #array:
        #po

  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}

enums:
  # From RE-Mesh-Editor's typeNameMapping (re_mesh_parse.py).
  primitive_type:
    0: position
    1: nor_tan # packed signed-byte normal+tangent interleaved, not normal alone
    2: uv
    3: uv2 # second UV channel - there are 2 separate UV types, not one generic "texcoord"
    4: weight
    5: color
    6: sf6_unknown_vertex_data_type # game-specific, unexplained even upstream
    7: extra_weight # extra 4 bone weights, for 6-weights-per-vertex setups
