meta:
  id: mtframework_mod2
  endian: le
  title: MTFramework model format 2.1
  file-extension: mod
  license: CC0-1.0
  ks-version: 0.8

seq:
  - {id: id_magic, contents: [0x4d, 0x4f, 0x44, 0x00]}
  - {id: version, type: u1}
  - {id: revision, type: u1}
  - {id: num_bones, type: u2}
  - {id: num_meshes, type: u2}
  - {id: num_materials, type: u2}
  - {id: num_vertices, type: u4}
  - {id: num_faces, type: u4}
  - {id: num_edges, type: u4}
  - {id: size_vertex_buffer, type: u4}
  - {id: reserved_01, type: u4}
  - {id: num_groups, type: u4}
  - {id: offset_bones, type: u4}
  - {id: offset_groups, type: u4}
  - {id: offset_material, type: u4}
  - {id: offset_meshes, type: u4}
  - {id: offset_buffer_vertices, type: u4}
  - {id: offset_buffer_indices, type: u4}
  - {id: size_file, type: u4}
  - {id: bounding_sphere, type: vec4}
  - {id: bounding_box_min, type: vec4}
  - {id: bounding_box_max, type: vec4}
  - {id: unk_01, type: u4}
  - {id: unk_02, type: u4}
  - {id: unk_03, type: u4}
  - {id: unk_04, type: u4} # TODO: like 16 bytes

instances:
  meshes:
    {pos: offset_meshes, type: mesh, repeat: expr, repeat-expr: num_meshes}
  vertex_buffer:
    {pos: offset_buffer_vertices, size: size_vertex_buffer}
  index_buffer:
    {pos: offset_buffer_indices, size: num_faces * 2}

types:
  mesh:
    seq:
      - {id: idx_group, type: u2}
      - {id: num_vertices, type: u2}
      - {id: index_group, type: u1}
      - {id: index_material, type: u2}
      - {id: level_of_detail, type: u1}
      - {id: type_mesh, type: u1}
      - {id: unk_class_mesh, type: u1}
      - {id: vertex_stride, type: u1}
      - {id: unk_render_mode, type: u1}
      - {id: vertex_position, type: u4}
      - {id: vertex_offset, type: u4}
      - {id: vertex_format, type: u4}
      - {id: face_position, type: u4}
      - {id: face_count, type: u4}
      - {id: face_offset, type: u4}
      - {id: bone_id_start, type: u1}
      - {id: num_unique_bone_ids, type: u1}
      - {id: mesh_index, type: u2}
      - {id: min_index, type: u2}
      - {id: max_index, type: u2}
      - {id: hash, type: u4}

  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

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
