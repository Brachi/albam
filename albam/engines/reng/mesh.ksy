meta:
    id: reengine_mesh
    endian: le
    title: Resident Evil 2 Remake (RE Engine) mesh format
    application: Resident Evil 2 Remake
    license: CCO-1.0
    ks-version: 0.8

seq:
    - id: header
      type: header
    - id: len_offsets_models
      type: u1
    - id: num_materials
      type: u1
    - id: unk2
      type: u1
    - id: unk3
      type: u1
    - id: unk4
      type: u4
    - id: reserved_01
      type: u4
    - id: reserved_02
      type: u4
    - id: box
      type: f4
      repeat: expr
      repeat-expr: 12
    - id: offset_lod_info
      type: u4
    - id: reserved_03
      type: u4
    - id: model_offsets
      type: model_offset
      repeat: expr
      repeat-expr: len_offsets_models


instances:
  bones_header:
    pos: header.offset_bones
    type: bone_header

  buffers_data:
    pos: header.offset_buffers_header
    type: buffers_header

  names_data:
    pos: header.offset_names
    type: name_offset
    repeat: expr
    repeat-expr: num_materials + bones_header.num_bones

types:

  buffers_header:
    seq:
      - id: offset_element_rename_me
        type: u8
      - id: offset_vertex_buffer
        type: u8
      - id: offset_index_buffer
        type: u8
      - id: size_vertex_buffer
        type: u4
      - id: size_index_buffer
        type: u4
      - id: len_element_rename_me_1
        type: u2
      - id: len_element_rename_me_2
        type: u2
      - id: unk_01
        type: u4
      - id: reserved_01
        type: u4
      - id: unk_2
        type: u2
      - id: unk_3
        type: u2

    instances:
      vertex_buffer:
        pos: offset_vertex_buffer
        size: size_vertex_buffer
      index_buffer:
        pos: offset_index_buffer
        size: size_index_buffer


  bone_header:
    seq:
      - id: num_bones
        type: u4
      - id: num_bone_maps
        type: u4
      - id: reserved_01
        type: u4
      - id: reserved_02
        type: u4
      - id: offset_parent_bone
        type: u8
      - id: offset_matrix_1
        type: u8
      - id: offset_matrix_2
        type: u8
      - id: offset_matrix_3
        type: u8
      - id: bone_maps
        type: u2
        repeat: expr
        repeat-expr: num_bone_maps
    instances:
      bones:
        pos: offset_parent_bone
        type: bone
        repeat: expr
        repeat-expr: num_bones

  bone:
    seq:
      - id: unk_01
        type: u2
      - id: bone_id
        type: u2
      - id: unk_02
        type: u2
        repeat: expr
        repeat-expr: 6


  # Thanks: https://github.com/kaitai-io/kaitai_struct/issues/14
  name_offset:
    seq:
      - id: offset
        type: u8
    instances:
      name:
        pos: offset
        type: str
        terminator: 0
        encoding: ascii

  model_offset:
    seq:
      - id: offset
        type: u8
    instances:
      model:
        pos: offset
        type: model


  model:
    seq:
      - id: num_mesh_groups
        type: u4
      - id: unk
        type: u4
      - id: offset_main_mesh_header
        type: u8
      - id: offsets_mesh_groups
        type: u8
        repeat: expr
        repeat-expr: num_mesh_groups
      - id: padding # ??
        type: u8

      - id: mesh_groups
        type: mesh_group
        repeat: expr
        repeat-expr: num_mesh_groups


  mesh_group:
    seq:
      - id: type
        type: u1
      - id: num_meshes
        type: u1
      - id: unk_01
        type: u2
      - id: unk_02
        type: u4
      - id: num_vertices
        type: u4
      - id: num_indices
        type: u4
      - id: meshes
        type: mesh
        repeat: expr
        repeat-expr: num_meshes

  mesh:
    seq:
      - id: type
        type: u4
      - id: num_indices
        type: u4
      - id: pos_index_buffer
        type: u4
      - id: pos_vertex_buffer
        type: u4

  header:
    seq:
      - id: id_magic
        contents: [77, 69, 83, 72]
      - id: unk0
        type: u1
      - id: unk1
        type: u1
      - id: unk2
        type: u1
      - id: unk3
        type: u1
      - id: size_file
        type: u4
      - id: reserved_01
        type: u4
      - id: unk4
        type: u2
      - id: num_models
        type: u2

      - id: reserved_02
        type: u4
      - id: offset_data
        type: u8
      - id: offset_unk_1
        type: u8
      - id: offset_unk_2
        type: u8
      - id: offset_bones
        type: u8
      - id: offset_unk_3
        type: u8
      - id: offset_unk_4
        type: u8
      - id: offset_unk_5
        type: u8
      - id: offset_buffers_header
        type: u8
      - id: offset_unk_6
        type: u8
      - id: offset_unk_7
        type: u8
      - id: offset_unk_8
        type: u8
      - id: offset_unk_9
        type: u8
      - id: offset_names
        type: u8
      - id: offset_unk_10
        type: u8
