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
      # num_bones/ofs_bones/ofs_unk_01/ofs_unk_02 point at further sections
      # (bone data, at least) not modeled here - see
      # albam/engines/hexn/edgemodel_roundtrip.py for why: their real
      # extents don't reduce to a clean per-file formula (tried and
      # reverted - see git history), so round-trip fidelity is handled
      # generically there (byte-diff against known ranges) instead of by
      # guessing more fields here.

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
      # Real (non-padding) data sits between here and _parent.ofs_materials
      # on every file checked, partially reverse-engineered as num_groups-
      # and _parent.unk_flags_1-driven (see git history for the formulas -
      # >99.6%/99.8% exact across a full-game sample, but not exact: a
      # weapon LOD/SHADOW sub-variant breaks both, and modeling it as a
      # mandatory field here turned "one bad mesh" into "whole file fails
      # to parse" for those - worse than not modeling it. Left opaque;
      # round-trip fidelity is handled generically instead - see
      # albam/engines/hexn/edgemodel_roundtrip.py.
    instances:
      buffer_indices:
        {pos: ofs_buffer_indices, size: size_buffer_indices}
      buffer_vertices:
        {pos: ofs_buffer_vertices, size: size_buffer_vertices}
      buffer_weights:
        {pos: ofs_buffer_weights, size: size_buffer_weights}
