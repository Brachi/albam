meta:
  endian: le
  file-extension: sbc
  id: sbc_156
  ks-version: 0.11
  title:  Resident Evil 5 (MTFramework) collision format

seq:
  - {id: header, type: sbc_header}
  - {id: nodes, type: bvh_node, repeat: expr, repeat-expr: header.num_boxes}
  - {id: sbc_info, type: info, repeat: expr, repeat-expr: header.num_objects}
  - {id: faces, type : face, repeat: expr, repeat-expr: header.num_faces}
  - {id: vertices, type: vertex, repeat: expr, repeat-expr: header.num_vertices}

types:
  sbc_header:
    seq:
    - {id: indent, contents: [0x53, 0x42, 0x43, 0x31]} # SBC1
    - {id: version, type: u2}
    - {id: num_objects, type: u2}
    - {id: num_objects_nodes, type: u2} # parts node num
    - {id: num_max_objects_nest, type: u1} # max parts nest count
    - {id: num_max_nest, type: u1} # max nest count
    - {id: num_boxes, type: u4} # total node num
    - {id: num_faces, type: u4} # total triangle num
    - {id: num_vertices, type: u4} # total vertex num
    - {id: bounding_box, type: bbox3}


  info: #96 bytes unloaded
    seq:
      - {id: base, type: u4}
      - {id: start_faces, type: u4}
      - {id: start_nodes, type: u4} # ?
      - {id: start_vertices, type: u4}
      - {id: group_id, type: u4}
      - {id: bounding_box, type: bbox3}
      - {id: vmin, type: vec3, repeat: expr, repeat-expr: 2}
      - {id: vmax, type: vec3, repeat: expr, repeat-expr: 2}
      - {id: child_index, type: u2, repeat: expr, repeat-expr: 2}

  face: #28 bytes
    seq:
      - {id: vert, type: u2, repeat: expr, repeat-expr: 3}
      - {id: unk_00, type: u1} # probably junk u2 filler
      - {id: unk_01, type: u1}
      - {id: runtime_attr, type: u4} # 1 in scr  16 64 128 in eff
      - {id: type, type: u4} # 32 64 128
      - {id: special_attr, type: u4} # 0
      - {id: surface_attr, type: u4} # 0
      - {id: unk_02, type: u4}

  bvh_node: # 80 bytes unloaded
    seq:
      - {id: boxes, type: bbox4, repeat: expr, repeat-expr: 2}
      - {id: bit, type: u2} # always 0-255 nodeType ?
      - {id: child_index, type: u2, repeat: expr, repeat-expr: 2} # references to a box
      - {id: nulls, type: u1, repeat: expr, repeat-expr: 10}

  bbox4:
    seq:
    - {id: min, type: f4, repeat: expr, repeat-expr: 4}
    - {id: max, type: f4, repeat: expr, repeat-expr: 4}
    
  
  bbox3:
    seq:
    - {id: min, type: f4, repeat: expr, repeat-expr: 3}
    - {id: max, type: f4, repeat: expr, repeat-expr: 3}
    
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

  vertex:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}