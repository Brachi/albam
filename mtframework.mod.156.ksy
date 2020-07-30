meta:
  id: mtframework_mod
  endian: le
  title:  Resident Evil 5 (MTFramework) model format (Mod format version 1.56)
  application: Resident Evil 5/Biohazard 5
  file-extension: mod
  license: CC0-1.0
  ks-version: 0.8

seq:
  - id: header
    type: mod_header

  - id: bones
    type: bone
    repeat: expr
    repeat-expr: header.num_bones

  - id: bones_matrix_1
    type: matrix4x4
    repeat: expr
    repeat-expr: header.num_bones

  - id: bones_matrix_2
    type: matrix4x4
    repeat: expr
    repeat-expr: header.num_bones

  - id: bone_map
    size: 256
    if: header.num_bones != 0

  - id: bones_mapping
    type: bone_mapping
    repeat: expr
    repeat-expr: header.num_bone_mappings

  - id: groups
    type: group
    repeat: expr
    repeat-expr: header.num_groups

  - id: textures
    type: str
    encoding: ascii
    size: 64
    repeat: expr
    repeat-expr: header.num_textures

  - id: materials
    type: material
    repeat: expr
    repeat-expr: header.num_materials

  - id: meshes
    type: mesh
    repeat: expr
    repeat-expr: header.num_meshes

  - id: num_meshes2
    type: u4

  - id: meshes2
    type: mesh2
    repeat: expr
    repeat-expr: num_meshes2

  - id: vertex_buffer
    size: header.size_vertex_buffer

  - id: vertex_buffer_2
    size: header.size_vertex_buffer_2

  - id: index_buffer
    size: (header.num_faces * 2) - 2

types:
  vec3:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

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

  bone:
    seq:
      - id: idx_anim_map
        type: u1
      - id: idx_parent
        type: u1
      - id: idx_mirror
        type: u1
      - id: idx_mapping
        type: u1
      - id: unk_01
        type: f4
      - id: parent_distance
        type: f4
      - id: location
        type: vec3

  bone_mapping:
    seq:
      - id: unk_01
        type: u4
      - id: values
        size: 32
  group:
    seq:
      - id: group_index
        type: u4
      - id: unk_02
        type: f4
      - id: unk_03
        type: f4
      - id: unk_04
        type: f4
      - id: unk_05
        type: f4
      - id: unk_06
        type: f4
      - id: unk_07
        type: f4
      - id: unk_08
        type: f4

  material:
    seq:
      - id: unk_01
        type: u2
      - id: unk_flags
        type: u2
      - id: unk_shorts
        type: u2
        repeat: expr
        repeat-expr: 10
      - id: texture_indices
        type: u4
        repeat: expr
        repeat-expr: 8
      - id: unk_floats
        type: f4
        repeat: expr
        repeat-expr: 26

  mesh:
    seq:
      - id: idx_group
        type: u2
      - id: idx_material
        type: u2
      - id: constant  # always 1
        type: u1

      - id: level_of_detail
        type: u1

      - id: unk_01
        type: u1

      - id: vertex_fmt
        type: u1
      - id: vertex_stride
        type: u1
      - id: unk_02
        type: u1
      - id: unk_03
        type: u1
      - id: unk_flags  # TODO: there's one known: cast_shadows
        type: u1
      - id: num_vertices
        type: u2
      - id: vertex_index_end  # TODO: better name
        type: u2
      - id: vertex_index_start_1
        type: u4
      - id: vertex_offset
        type: u4
      - id: unk_05
        type: u4
      - id: face_position  # TODO: better name
        type: u4
      - id: face_count
        type: u4
      - id: face_offset
        type: u4
      - id: unk_06
        type: u1
      - id: unk_07
        type: u1
      - id: vertex_index_start_2
        type: u2
      - id: vertex_group_count
        type: u1
      - id: bone_palette_index
        type: u1
      - id: unk_08
        type: u1
      - id: unk_09
        type: u1
      - id: unk_10
        type: u2
      - id: unk_11
        type: u2

  mesh2:
    seq:
      - id: unk_01
        type: f4
        repeat: expr
        repeat-expr: 16
      - id: unk_02
        type: f4
        repeat: expr
        repeat-expr: 16
      - id: unk_03
        type: f4
        repeat: expr
        repeat-expr: 4



  mod_header:
    seq:
      - id: ident
        contents: [0x4d, 0x4f, 0x44, 0x00]
      - id: version_must_be_156
        contents: [ 156, 1]
      - id: num_bones
        type: u2
      - id: num_meshes
        type: u2
      - id: num_materials
        type: u2
      - id: num_vertices
        type: u4
      - id: num_faces
        type: u4
      - id: num_edges
        type: u4
      - id: size_vertex_buffer
        type: u4
      - id: size_vertex_buffer_2
        type: u4
      - id: num_textures
        type: u4
      - id: num_groups
        type: u4
      - id: num_bone_mappings
        type: u4
      - id: offset_bones
        type: u4
      - id: offset_groups
        type: u4
      - id: offset_textures
        type: u4
      - id: offset_meshes
        type: u4
      - id: offset_buffer_vertices
        type: u4
      - id: offset_buffer_vertices_2
        type: u4
      - id: offset_buffer_indices
        type: u4
      - id: reserved_01
        type: u4
      - id: reserved_02
        type: u4
      - id: bounding_sphere
        type: vec4
      - id: bounding_box_min
        type: vec4
      - id: bounding_box_max
        type: vec4
      - id: unk_01
        type: u4
      - id: unk_02
        type: u4
      - id: unk_03
        type: u4
      - id: unk_04
        type: u4
      - id: unk_05
        type: u4
      - id: unk_06
        type: u4
      - id: unk_07
        type: u4
      - id: unk_08
        type: u4
      - id: unk_09
        type: u4
      - id: unk_10
        type: u4
      - id: unk_11
        type: u4
      - id: reserved_03
        type: u4
      - id: unk_12
        size: offset_bones - 176
        if: unk_08 !=  0

