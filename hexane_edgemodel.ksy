---

meta:
  id: hexane_edgemodel
  endian: le
  title: Resident Evil ORC (Hexane) model format
  application: Resident Evil Operation Raccoon City
  file-extension: edgemodel
  license: CC0-1.0
  ks-version: 0.8

seq:
  - id: header
    type: edge_header
  - id: meshes_header
    type: mesh_header
    repeat: expr
    repeat-expr: header.num_meshes

types:
  edge_header:
    seq:
      - id: id_magic
        contents: [0x46, 0x4d, 0x36, 0x53]
      - id: version
        type: u4
      - id: num_models
        type: u4
      - id: num_meshes
        type: u4
      - id: ofs_meshes_start
        type: u4
      - id: ofs_meshes_end
        type: u4
      - id: ofs_meshes_info
        type: u4
      - id: num_bones
        type: u4
      - id: ofs_bones
        type: u4
      - id: reserved_01
        type: u4
      - id: reserved_02
        type: u4
      - id: reserved_03
        type: u4
      - id: unk_matrix_1
        type: f4
        repeat: expr
        repeat-expr: 8
      - id: unk_matrix_2
        type: matrix4x4
      - id: num_material_per_mesh
        type: u4
      - id: ofs_unk_01
        type: u4
      - id: ofs_unk_02
        type: u4
      - id: reserved_04
        type: u4
      - id: ofs_models_start  # TODO: better name
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: ofs_models_end  # TODO: better name
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: reserved_05
        type: u4
      - id: reserved_06
        type: u4

  mesh_header:
    seq:
      - id: num_groups
        type: u4
      - id: ofs_data
        type: u4
      - id: lod
        type: u4
      - id: ofs_materials
        type: u4
      - id: matrix_4x2_unk
        type: f4
        repeat: expr
        repeat-expr: 8
      - id: matrix_4x4_unk
        type: matrix4x4
      - id: unk_ofs_1
        type: u4
      - id: unk_ofs_2
        type: u4
      - id: unk_ofs_3
        type: u4
      - id: unk_ofs_4
        type: u4
      - id: unk_ofs_5
        type: u4
      - id: unk_flags_1
        type: u4
      - id: unk_ofs_6
        type: u4
      - id: reserved_01
        type: u4
    instances:
      mesh:
        pos: ofs_data
        type: edgemesh
      materials:
        pos: ofs_materials
        size: 308


  vec3:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: reserved_03
        type: u4

  vec4:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: w
        type: f4

  matrix4x4:
    seq:
      - id: row_1
        type: vec4
      - id: row_2
        type: vec4
      - id: row_3
        type: vec4
      - id: row_4
        type: vec4

  edgemesh:
    seq:
      - id: unk_1_flag
        type: u2
      - id: unk_2_constant
        type: u2
      - id: unk_3_flag
        type: u4
      - id: num_vertices
        type: u2
      - id: num_indices
        type: u2
      - id: unk_4_flag
        type: u4
      - id: ofs_buffer_indices
        type: u4
      - id: size_buffer_indices
        type: u4
      - id: reserved_01
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: ofs_buffer_vertices
        type: u4
      - id: size_buffer_vertices
        type: u4
      - id: reserved_06
        type: u4
      - id: unk_5_flag
        type: u4
      - id: size_buffer_weights
        type: u4
      - id: ofs_buffer_weights
        type: u4
      - id: unk_6_flag
        type: u4
      - id: num_vertices_padding  # ??
        type: u4  # ??
      - id: reserved_02
        type: u4
        repeat: expr
        repeat-expr: 9
      - id: unk_7_offset
        type: u4
      - id: unk_8_offset
        type: u4
      - id: reserved_16
        type: u4
      - id: unk_9_size
        type: u2
      - id: unk_10_size
        type: u2
    instances:
      buffer_indices:
        pos: ofs_buffer_indices
        size: size_buffer_indices
      buffer_vertices:
        pos: ofs_buffer_vertices
        size: size_buffer_vertices
      buffer_weights:
        pos: ofs_buffer_vertices
        size: size_buffer_vertices

        #import ctypes as c
        #from albam.lib.structure import DynamicStructure, DynamicArray
        #
        #class EdgeMeshHeader(c.Structure):
        #
        #    # 4I 8f 16f 8I'
        #    _fields_ = (
        #        ('count_group', c.c_uint),
        #        ('offset_data', c.c_uint),
        #        ('lod',  c.c_uint),
        #        ('offset_materials', c.c_uint),
        #        ('matrix_4x2_unk', c.c_float * 8),
        #        ('matrix_4x4_unk', c.c_float * 16),
        #        ('_offset_1', c.c_uint),
        #        ('_offset_2', c.c_uint),
        #        ('_offset_3', c.c_uint),
        #        ('_offset_4', c.c_uint),
        #        ('_offset_5', c.c_uint),
        #        ('_flag_unk_1', c.c_uint),
        #        ('_offset_6', c.c_uint),
        #        ('reserved_1', c.c_uint),
        #        )
        #
        #
        #class EdgeMeshData(DynamicStructure):
        #
        #    _fields_ = (
        #
        #    # '2H I 2H 4B 2I 5I 2I 3I 2I 13I 2H'
        #        ('_1_flag', c.c_ushort),
        #        ('_2_constant', c.c_ushort),
        #        ('_3_flag', c.c_uint),
        #        ('count_vertices', c.c_ushort),
        #        ('count_indices', c.c_ushort),
        #        ('_4_flag', c.c_uint),
        #        ('offset_index_buffer', c.c_uint),
        #        ('size_index_buffer', c.c_uint),
        #        ('reserved_01', c.c_uint),
        #        ('reserved_02', c.c_uint),
        #        ('reserved_03', c.c_uint),
        #        ('reserved_04', c.c_uint),
        #        ('reserved_05', c.c_uint),
        #        ('offset_vertex_buffer',  c.c_uint),
        #        ('size_vertex_buffer', c.c_uint),
        #        ('reserved_06', c.c_uint),
        #        ('_5_flag', c.c_uint),
        #        ('size_weight_buffer', c.c_uint),
        #        ('offset_weight_buffer', c.c_uint),
        #        ('_6_flag', c.c_uint),
        #        ('count_vert', c.c_uint),  # ??
        #        ('reserved_07', c.c_uint),
        #        ('reserved_08', c.c_uint),
        #        ('reserved_09', c.c_uint),
        #        ('reserved_10', c.c_uint),
        #        ('reserved_11', c.c_uint),
        #        ('reserved_12', c.c_uint),
        #        ('reserved_13', c.c_uint),
        #        ('reserved_14', c.c_uint),
        #        ('reserved_15', c.c_uint),
        #        ('_7_offset', c.c_uint),
        #        ('_8_offset', c.c_uint),
        #        ('reserved_16', c.c_uint),
        #        ('_9_size', c.c_ushort),
        #        ('_10_size', c.c_ushort),
        #        )
        #
        #
        #class EdgeModel(DynamicStructure):
        #
        #    _fields_ = (
        #        ('id_magic', c.c_char * 4),
        #        ('version', c.c_uint),
        #        ('size_models_array', c.c_uint),
        #        ('size_mesh_array', c.c_uint),
        #        ('offset_meshes_start', c.c_uint),
        #        ('offset_meshes_end', c.c_uint),
        #        ('offset_meshes_info', c.c_uint),
        #        ('size_bones_array', c.c_uint),
        #        ('offset_bones', c.c_uint),
        #        ('reserved_01', c.c_uint),
        #        ('reserved_02',c.c_uint),
        #        ('reserved_03',c.c_uint),
        #        ('matrix_4x2_unk', c.c_float * 8),
        #        ('matrix_4x4_unk', c.c_float * 16),
        #        ('count_material_per_mesh', c.c_uint),
        #        ('_offset_1', c.c_uint),
        #        ('_offset_2', c.c_uint),
        #        ('reserved_04', c.c_uint),
        #        ('array_offsets_models', c.c_uint * 5),
        #        ('array_offsets_models_end', c.c_uint * 5),
        #        ('reserved_05', c.c_uint),
        #        ('reserved_06', c.c_uint),
        #        ('array_mesh_headers', DynamicArray(EdgeMeshHeader, 'size_mesh_array')),
        #        #('tmp', EdgeMeshHeader),
        #        )
        #
