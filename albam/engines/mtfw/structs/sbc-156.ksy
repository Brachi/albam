meta:
  endian: le
  file-extension: sbc
  id: sbc_156
  ks-version: 0.10
  title: MTFramework collision format version 156
seq:
  - {id: header, type: sbc_header}
  - {id: nodes, type: bvh_node, repeat: expr, repeat-expr: header.num_nodes}
  - {id: sbc_info, type: info, repeat: expr, repeat-expr: header.num_infos}
  - {id: faces, type : face, repeat: expr, repeat-expr: header.num_faces}
  - {id: vertices, type: vec4, repeat: expr, repeat-expr: header.num_vertices}
  
types:

  sbc_header:
    seq:
      - {id: magic, contents: [0x53, 0x42, 0x43, 0x31]} # SBC1
      - {id: version, type: u2}
      - {id: num_infos, type: u2} # parts info num
      - {id: num_parts, type: u2} # parts node num
      - {id: num_parts_nest, type: u1} # max parts nest count
      - {id: max_nest_count, type: u1} # max nest count
      - {id: num_nodes, type: u4} # total node num
      - {id: num_faces, type: u4} # total triangle num
      - {id: num_vertices, type: u4} # total vertex num
      - {id: box, type: bbox}

  info: #96 bytes
    seq:
      - {id: flags, type: u4}
      - {id: start_tris, type: u4}
      - {id: start_nodes, type: u4} # ?
      - {id: start_vertices, type: u4}
      - {id: index_id, type: u4}
      - {id: bounding_box, type: bbox}
      - {id: min, type: vec3, repeat: expr, repeat-expr: 2} # binary tree for bboxes?
      - {id: max, type: vec3, repeat: expr, repeat-expr: 2}
      - {id: child_index, type: u2, repeat: expr, repeat-expr: 2}

  face: #28 bytes
    seq:
      - {id: vert, type: u2, repeat: expr, repeat-expr: 3}
      - {id: unk_00, type: u1, repeat: expr, repeat-expr: 2}
      - {id: type, type: u4} # attribute
      - {id: attr, type: u4, repeat: expr, repeat-expr: 4}

  
  bvh_node: # 80 bytes
    seq:
      - {id: aabb_01, type: aabb}
      - {id: aabb_02, type: aabb}
      - {id: bit, type: u1} # always 0-255
      - {id: unk, type: u1}
      - {id: child_index, type: u2, repeat: expr, repeat-expr: 2}
      - {id: nulls, type: u1, repeat: expr, repeat-expr: 10}
      
  vertex:
    seq:
      - {id: vector, type: vec4}
  
  bbox:
    seq:
      - {id: min, type: vec3}
      - {id: max, type: vec3}
      
  pbox:
    seq:
      - {id: min, type: vec4}
      - {id: max, type: vec4}
      
  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}

  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      
  rgba:
    seq:
      - {id: red, type: u1}
      - {id: green, type: u1}
      - {id: blue, type: u1}
      - {id: alpha, type: u1}
  aabb:
    seq:
      - {id: min, type: vec4}
      - {id: max, type: vec4}
       
