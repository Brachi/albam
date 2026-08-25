meta:
  id: hexane_edgemodel
  endian: le
  title: Hexane Engine Model Format
  file-extension: edgemodel
  license: CC0-1.0
  ks-version: '0.11'

seq:
  - {id: header, type: edge_header}
  - {id: meshes_header, type: mesh_header, repeat: expr, repeat-expr: header.num_meshes}

types:
  edge_header:
    seq:
      - {id: id_magic, contents: [0x46, 0x4d, 0x36, 0x53]}
      - {id: version, type: u4}
      - {id: num_models, type: u4}
      - {id: num_meshes, type: u4}
      - {id: ofs_meshes_start, type: u4}
      - {id: ofs_meshes_end, type: u4}
      - {id: ofs_meshes_info, type: u4}
      - {id: num_bones, type: u4}
      - {id: ofs_bones, type: u4}
      - {id: reserved_01, type: u4}
      - {id: reserved_02, type: u4}
      - {id: reserved_03, type: u4}
      - {id: unk_matrix_1, type: f4, repeat: expr, repeat-expr: 8}
      - {id: unk_matrix_2, type: matrix4x4}
      - {id: num_material_per_mesh, type: u4}
      - {id: ofs_unk_01, type: u4}
      - {id: ofs_unk_02, type: u4}
      - {id: reserved_04, type: u4}
      - {id: ofs_models_start, type: u4, repeat: expr, repeat-expr: 5} # TODO: better name
      - {id: ofs_models_end, type: u4, repeat: expr, repeat-expr: 5}  # TODO: better name
      - {id: reserved_05, type: u4}
      - {id: reserved_06, type: u4}
    instances:
      # The data between the last mesh's own buffers and ofs_bones (or
      # ofs_unk_02, when there's no bones section): the last mesh's own
      # highest buffer end (materials_end is never the maximum, so it is
      # left out), aligned up to a 16-byte boundary, then 16 more bytes,
      # then a small record whose own first byte gives the rest of the
      # size - marker_record_byte0.
      last_mesh_header:
        value: _parent.meshes_header[num_meshes - 1]
      last_mesh_indices_end:
        value: last_mesh_header.mesh.ofs_buffer_indices + last_mesh_header.mesh.size_buffer_indices
      last_mesh_vertices_end:
        value: last_mesh_header.mesh.ofs_buffer_vertices + last_mesh_header.mesh.size_buffer_vertices
      last_mesh_weights_end:
        value: last_mesh_header.mesh.ofs_buffer_weights + last_mesh_header.mesh.size_buffer_weights
      last_mesh_max_end:
        value: >-
          last_mesh_indices_end > last_mesh_vertices_end
          ? (last_mesh_indices_end > last_mesh_weights_end ? last_mesh_indices_end : last_mesh_weights_end)
          : (last_mesh_vertices_end > last_mesh_weights_end ? last_mesh_vertices_end : last_mesh_weights_end)
      last_mesh_align_padding:
        value: (16 - (last_mesh_max_end % 16)) % 16
      marker_record_pos:
        value: last_mesh_max_end + last_mesh_align_padding + 16
      marker_record_byte0:
        pos: marker_record_pos
        type: u1
        if: num_meshes > 0 and marker_record_pos < _io.size
      # With bones: dist(marker -> ofs_bones) = 32 + 16*(byte0//2), never
      # scales with num_material_per_mesh (materials_table already
      # accounts for its own materials independently).
      marker_record_readable:
        value: num_meshes > 0 and marker_record_pos < _io.size
      pre_bones_data_size:
        value: >-
          marker_record_readable
          ? (last_mesh_align_padding + 16 + 32 + 16 * (marker_record_byte0 / 2))
          : 0
      pre_bones_data:
        pos: ofs_bones - pre_bones_data_size
        size: pre_bones_data_size
        if: marker_record_readable and num_bones > 0 and ofs_bones > pre_bones_data_size
      bones_data:
        pos: ofs_bones
        size: ofs_unk_02 - ofs_bones
        if: num_bones > 0 and ofs_unk_02 > ofs_bones
      # No bones: dist(marker -> ofs_unk_02) = 20 + 16*(byte0//2) +
      # 4*(num_material_per_mesh - 1) - the +4/material matches
      # materials_table.offsets' own 4-byte stride.
      pre_trailing_footer_size:
        value: >-
          marker_record_readable
          ? (last_mesh_align_padding + 16 + 20 + 16 * (marker_record_byte0 / 2)
          + 4 * (num_material_per_mesh - 1))
          : 0
      pre_trailing_footer:
        pos: ofs_unk_02 - pre_trailing_footer_size
        size: pre_trailing_footer_size
        if: >-
          marker_record_readable and num_bones == 0
          and ofs_unk_02 > pre_trailing_footer_size
      trailing_data:
        pos: ofs_unk_02
        size: _io.size - ofs_unk_02
        if: ofs_unk_02 > 0

  mesh_header:
    seq:
      - {id: num_groups, type: u4}
      - {id: ofs_data, type: u4}
      - {id: lod, type: u4}
      - {id: ofs_materials, type: u4}
      - {id: matrix_4x2_unk, type: f4, repeat: expr, repeat-expr: 8}
      - {id: matrix_4x4_unk, type: matrix4x4}
      - {id: unk_ofs_1, type: u4}
      - {id: unk_ofs_2, type: u4}
      - {id: unk_ofs_3, type: u4}
      - {id: unk_ofs_4, type: u4}
      - {id: unk_ofs_5, type: u4}
      - {id: unk_flags_1, type: u4}
      - {id: unk_ofs_6, type: u4}
      - {id: reserved_01, type: u4}
    instances:
      # Shared/default 48 bytes for every mesh but the first in a file
      # (identical regardless of the mesh's own content); the first
      # mesh's own version instead holds real-looking floats/offsets. Not
      # semantically understood either way - captured only so it round-
      # trips.
      pre_mesh_data:
        {pos: ofs_data - 48, size: 48, if: ofs_data >= 48}
      mesh:
        {pos: ofs_data, type: edgemesh}
      materials:
        {pos: ofs_materials, type: materials_table}
      # unk_ofs_3 gap: the region between materials_table's end and this
      # mesh's own first buffer. unk_ofs_3 -> count (u4), unk_ofs_3+4 ->
      # offset_a (u4, stored, not recomputed), unk_ofs_3+8 -> offset_b
      # (u4, stored). [unk_ofs_3+12, offset_a) is alignment filler;
      # [offset_a, offset_b) is count*16 bytes of per-entry data, left
      # unmodeled; [offset_b, offset_b + count*8) is a second real block;
      # anything up to the first buffer after that is padding. A distinct
      # sub-variant, where count is always 22, is guarded out below.
      materials_end:
        value: materials._io.pos
      buf_indices_or_sentinel:
        value: "mesh.ofs_buffer_indices > materials_end ? mesh.ofs_buffer_indices : 2147483647"
      buf_vertices_or_sentinel:
        value: "mesh.ofs_buffer_vertices > materials_end ? mesh.ofs_buffer_vertices : 2147483647"
      buf_weights_or_sentinel:
        value: "mesh.ofs_buffer_weights > materials_end ? mesh.ofs_buffer_weights : 2147483647"
      gap_end:
        value: >-
          buf_indices_or_sentinel < buf_vertices_or_sentinel
          ? (buf_indices_or_sentinel < buf_weights_or_sentinel ? buf_indices_or_sentinel : buf_weights_or_sentinel)
          : (buf_vertices_or_sentinel < buf_weights_or_sentinel ? buf_vertices_or_sentinel : buf_weights_or_sentinel)
      unk3_count:
        {pos: unk_ofs_3, type: u4, if: unk_ofs_3 > 0}
      unk3_offset_a:
        {pos: unk_ofs_3 + 4, type: u4, if: unk_ofs_3 > 0}
      unk3_offset_b:
        {pos: unk_ofs_3 + 8, type: u4, if: unk_ofs_3 > 0}
      unk3_region1_end:
        value: unk3_offset_b + 8 * unk3_count
      unk3_header_gap:
        pos: unk_ofs_3 + 12
        size: unk3_offset_a - (unk_ofs_3 + 12)
        if: unk_ofs_3 > 0 and unk3_offset_a > unk_ofs_3 + 12
      unk3_region0:
        pos: unk3_offset_a
        size: unk3_offset_b - unk3_offset_a
        if: unk_ofs_3 > 0 and unk3_offset_b > unk3_offset_a
      unk3_region1:
        pos: unk3_offset_b
        size: 8 * unk3_count
        if: unk_ofs_3 > 0 and unk3_region1_end <= gap_end
      unk3_trailing:
        pos: unk3_region1_end
        size: gap_end - unk3_region1_end
        if: unk_ofs_3 > 0 and unk3_region1_end <= gap_end and gap_end > unk3_region1_end

  materials_table:
    seq:
      - {id: offsets, type: u4, repeat: expr, repeat-expr: _parent._parent.header.num_material_per_mesh}
      # offsets[i] each point to their own null-terminated .matb path.
      # The strings are contiguous (offsets[i+1] is offsets[i] plus that
      # string's length and terminator), so they are read sequentially
      # rather than through a per-offset `pos:`, which the Python target of
      # kaitai-struct-compiler 0.11 miscompiles inside a repeated instance
      # (it references the repeat loop variable before it's bound).
      - {id: all_materials, type: str, terminator: 0, encoding: ASCII,
         repeat: expr, repeat-expr: _parent._parent.header.num_material_per_mesh}
    instances:
      first_material:
        value: all_materials[0]

  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: reserved_03, type: u4}

  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}

  matrix4x4:
    seq:
      - {id: row_1, type: vec4}
      - {id: row_2, type: vec4}
      - {id: row_3, type: vec4}
      - {id: row_4, type: vec4}

  edgemesh:
    seq:
      - {id: unk_1_flag, type: u2}
      - {id: unk_2_constant, type: u2}
      - {id: unk_3_flag, type: u4}
      - {id: num_vertices, type: u2}
      - {id: num_indices, type: u2}
      - {id: unk_4_flag, type: u4}
      - {id: ofs_buffer_indices, type: u4}
      - {id: size_buffer_indices, type: u4}
      - {id: reserved_01, type: u4, repeat: expr, repeat-expr: 5}
      - {id: ofs_buffer_vertices, type: u4}
      - {id: size_buffer_vertices, type: u4}
      - {id: reserved_06, type: u4}
      - {id: unk_5_flag, type: u4}
      - {id: size_buffer_weights, type: u4}
      - {id: ofs_buffer_weights, type: u4}
      - {id: unk_6_flag, type: u4}
      - {id: num_vertices_padding, type: u4} # ??
      - {id: reserved_02, type: u4, repeat: expr, repeat-expr: 9}
      - {id: unk_7_offset, type: u4}
      - {id: unk_8_offset, type: u4}
      - {id: reserved_16, type: u4}
      - {id: unk_9_size, type: u2}
      - {id: unk_10_size, type: u2}
      # Real (non-padding) data between here and _parent.ofs_materials:
      # 128*(num_groups-1) + 16*num_groups + 80*num_groups bytes, then
      # sum(20*2^bit for every set bit in _parent.unk_flags_1) bytes.
      # Guarded rather than unconditional: a weapon LOD/SHADOW sub-variant
      # breaks the formula (the size would come out negative), and this way
      # that variant only loses round-trip fidelity for this one section
      # instead of failing to parse at all.
      - id: group_and_flags_data
        size: _parent.ofs_materials - (_parent.ofs_data + 128)
        if: _parent.ofs_materials > (_parent.ofs_data + 128)
    instances:
      buffer_indices:
        {pos: ofs_buffer_indices, size: size_buffer_indices}
      buffer_vertices:
        {pos: ofs_buffer_vertices, size: size_buffer_vertices}
      buffer_weights:
        {pos: ofs_buffer_weights, size: size_buffer_weights}
