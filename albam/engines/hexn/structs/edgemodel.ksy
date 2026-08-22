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
      # ofs_unk_02, when there's no bones section), derived against a
      # full-game sweep: align the last mesh's own highest
      # buffer end up to a 16-byte boundary, then a fixed-per-lod trailer
      # (+4 bytes per extra material, matching materials_table's own
      # per-material offsets entry). >99.6% exact for the with-bones case
      # (a fixed 48 or 80 bytes, no alignment needed - lod 4 vs. not) and
      # the no-bones lod-4 case; the no-bones lod-0 case has an
      # unexplained further +/-16 residual on ~18% of files not resolved
      # here. materials_end is never the true max on any file checked, so
      # left out of the comparison entirely.
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
      last_mesh_trailer_size:
        value: "(last_mesh_header.lod == 4 ? 36 : 68) + 4 * (num_material_per_mesh - 1)"
      pre_bones_data_size:
        value: "last_mesh_header.lod == 4 ? 48 : 80"
      pre_bones_data:
        pos: ofs_bones - pre_bones_data_size
        size: pre_bones_data_size
        if: num_meshes > 0 and num_bones > 0 and ofs_bones >= pre_bones_data_size
      bones_data:
        pos: ofs_bones
        size: ofs_unk_02 - ofs_bones
        if: num_bones > 0 and ofs_unk_02 > ofs_bones
      pre_trailing_footer_size:
        value: last_mesh_align_padding + last_mesh_trailer_size
      pre_trailing_footer:
        pos: ofs_unk_02 - pre_trailing_footer_size
        size: pre_trailing_footer_size
        if: num_meshes > 0 and num_bones == 0 and ofs_unk_02 > pre_trailing_footer_size
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

  materials_table:
    seq:
      - {id: offsets, type: u4, repeat: expr, repeat-expr: _parent._parent.header.num_material_per_mesh}
      # offsets[i] each point to their own separate null-terminated string
      # (confirmed against real data: 4 distinct .matb paths, one per
      # offset - not just first_material's) - modeled here as sequential
      # (offsets[i+1] always equals offsets[i] + len(string) + 1 on every
      # real file checked, i.e. they're contiguous, not independently
      # positioned) rather than pos-based per offsets[i]: the Python target
      # of kaitai-struct-compiler 0.11 generates broken code (references
      # the repeat loop variable before it's bound) for a `pos:` expression
      # that depends on `_index` inside a repeated instance.
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
      # sum(20*2^bit for every set bit in _parent.unk_flags_1) bytes -
      # >99.6%/99.8% exact across a full-game sample. Guarded rather than
      # unconditional: a weapon LOD/SHADOW sub-variant breaks the formula
      # (would compute a negative size), and this way that variant just
      # loses round-trip fidelity for this one section instead of failing
      # to parse at all.
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
