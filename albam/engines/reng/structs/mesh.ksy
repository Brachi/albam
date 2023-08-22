meta:
    id: reengine_mesh
    endian: le
    title: RE Engine mesh format
    ks-version: 0.10

seq:
    - {id: id_magic, contents: [77, 69, 83, 72]}
    - {id: version, type: u4}
    - {id: size_file, type: u8}
    - {id: header, type: header}

instances:

  model_info:
    {pos: header.offset_data, type: model_info}

  bones_header:
    {pos: header.offset_bones, type: bone_header, if: header.offset_bones != 0}

  buffers_data:
    {pos: header.offset_buffers_header, type: buffers_header}

  named_nodes:
    {pos: header.offset_names, type: test_name, repeat: expr, repeat-expr: header.num_named_nodes}

  id_to_names_remap:
    {pos: header.offset_test_remap, type: u2, repeat: expr, repeat-expr: header.num_named_nodes}

types:
  header:
    seq:
      - {id: unk1, type: u2}
      - {id: num_named_nodes, type: u2}
      - {id: reserved_02 , type: u4} # padding?
      - {id: offset_data, type: u8} # 0 ModelPointers
      - {id: offset_unk_1, type: u8} # 1 BonesDataHeaderPointer
      - {id: offset_unk_2, type: u8} # 2 UnkPointer01
      - {id: offset_bones, type: u8} # 3 UnkPointer02
      - {id: offset_unk_3, type: u8} # 4 UnkPointer03
      - {id: offset_unk_4, type: u8} # 5 GeometryPointer
      - {id: offset_unk_5, type: u8} # 6 UnkPointer05
      - {id: offset_buffers_header, type: u8} # 7 GeometryPointer
      - {id: offset_unk_6, type: u8} # 8  UnkPointer05
      - {id: offset_test_remap, type: u8} # 9 MaterialsNamesPointer
      - {id: offset_unk_8, type: u8} # 10 BonesNamesPointer
      - {id: offset_unk_9, type: u8} # 11 UnkPointer08
      - {id: offset_names, type: u8} # 12 StringTablePointer

  model_info:
    seq:
      - {id: len_offsets_models, type: u1}
      - {id: num_materials, type: u1}
      - {id: num_uv_layers, type: u1}
      - {id: num_skin_weights, type: u1}
      - {id: num_meshes, type: u4}
      - {id: reserved_01, type: u8, if: _root.version == 386270720}  # XXX FIXME: enum with versions
      - {id: box, type: f4, repeat: expr, repeat-expr: 12}
      - {id: offset_lod_info, type: u4}
      - {id: reserved_02, type: u4}
    instances:
      model_offsets:
        {pos: offset_lod_info, type: model_offset, repeat: expr, repeat-expr: len_offsets_models}


  test_name:
    seq:
      - {id: offset, type: u8}
    instances:
      value:
        {pos: offset, type: strz, encoding: ascii}

  primitive_accessor:
    seq:
      - {id: primitive_type, type: u2}  # TODO: enum 0: POSITION; 1: NORMAL; 2: TEXCOORD; 4: JOINT_WEIGHT
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
      - {id: unk_00_a, type: u4, if: _root.version == 21041600 and unk_00 == 0}
      - {id: unk_00_b, type: u4, if: _root.version == 21041600 and unk_00 == 0}

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
      inverse_bind_matrices:
        {pos: offset_inverse_bind_matrices, type: matrix4x4, repeat: expr, repeat-expr: num_bones}

  bone:
    seq:
      - {id: idx, type: u2}
      - {id: parent_idx, type: u2}
      - {id: unk_02, type: u2, repeat: expr, repeat-expr: 6}

  name_offset: # Thanks: https://github.com/kaitai-io/kaitai_struct/issues/14
    seq:
      - {id: offset, type: u8}
    instances:
      name:
        {pos: offset, type: str, terminator: 0, encoding: ascii}

  mesh_group_test:
    seq:
      - {id: offset, type: u8}
    instances:
      mesh_group:
        {pos: offset, type: mesh_group}

  model_offset:
    seq:
      - {id: offset, type: u8}
    instances:
      model:
        {pos: offset, type: model}

  model:
    seq:
      - {id: num_mesh_groups, type: u4}
      - {id: unk, type: u4}
      - {id: offset_main_mesh_header, type: u8}
      - {id: mesh_groups, type: mesh_group_test, repeat: expr, repeat-expr: num_mesh_groups}
      - {id: padding, type: u8} # ??

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
      - {id: material_id, type: u4}
      - {id: num_indices, type: u4}
      - {id: pos_index_buffer, type: u4}
      - {id: pos_vertex_buffer, type: u4}
      - {id: unk_01, type: u8, if: _root.version != 386270720}

    instances:
      normals:
        pos: >
          _root.buffers_data.offset_vertex_buffer +
          _root.buffers_data.primitive_accessors[1].offset +
          _root.buffers_data.primitive_accessors[1].size * pos_vertex_buffer
        type: s1
        repeat: expr
        repeat-expr: 100  # FIXME: calculate num_vertices


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
