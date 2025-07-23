meta:
  endian: le
  file-extension: sbc
  id: sbc_211
  ks-version: 0.10
  title: MTFramework collision format version 211
  
seq:
  - {id: header, type: sbc_header}
  - {id: sbc_info, type: info, repeat: expr, repeat-expr: header.object_count}
  - {id: pairs_collections, type: s_face_pair, repeat: expr, repeat-expr: header.pair_count}
  - {id: faces, type: face, repeat: expr, repeat-expr: header.face_count}
  - {id: vertices, type: vertex, repeat: expr, repeat-expr: header.vertex_count}
  - {id: collision_types, type: collision_type, repeat: expr, repeat-expr: header.stage_count}
  - {id: sbc_bvhc, type: bvh_collision, repeat: expr, repeat-expr: header.object_count}
  - {id: bvh, type: bvh_collision}
  
types:
  sbc_header:
    seq:
     - {id: magic, contents: [0x53, 0x42, 0x43, 0xff]}
     - {id: unk_00, type: u4}
     - {id: unk_02, type: u4}
     - {id: unk_03, type: u4}
     - {id: object_count, type: u2}
     - {id: stage_count, type: u2}
     - {id: pair_count, type: u4}
     - {id: face_count, type: u4}
     - {id: vertex_count, type: u4}
     - {id: nulls, type: u4, repeat: expr, repeat-expr: 4}
     - {id: box, type: bbox}
     #- {id: bb_size, type: u4}
    instances:
      size_:
        value: 84
    
  info:
    seq:
      - {id: bounding_box, type: bbox}
      - {id: unk_01, type: u4}
      - {id: nulls_01, type: u4, repeat: expr, repeat-expr: 2}
      - {id: pairs_start, type: u4}
      - {id: pairs_count, type: u4}
      - {id: faces_start, type: u4}
      - {id: face_count, type: u4}
      - {id: vertex_start, type: u4}
      - {id: vertex_count, type: u4}
      - {id: index_id, type: u4}
      - {id: nulls_02, type: u4, repeat: expr, repeat-expr: 2}
      
  bvh_collision:
    seq:  
      - {id: bvhc, type: u4, repeat: expr, repeat-expr: 2}
      - {id: soh, type: u4}
      - {id: unk_01, type: u4}
      - {id: bounding_box, type: bbox}
      - {id: node_count, type: u4}
      - {id: nulls, type: u4, repeat: expr, repeat-expr: 3}
      - {id: nodes, type: bvh_node, repeat: expr, repeat-expr: node_count}
    
  bvh_node:
    seq:
      - {id: node_type, type: u1, repeat: expr, repeat-expr: 4}
      - {id: node_id, type: u2, repeat: expr, repeat-expr: 4}
      - {id: unk_05, type: u4}
      - {id: min_aabb, type: aabb_block}
      - {id: max_aabb, type: aabb_block}
  
  face:
    seq:
      - {id: normal, type: f4, repeat: expr, repeat-expr: 3}
      - {id: vert, type: u2, repeat: expr, repeat-expr: 3}
      - {id: type, type: u2}
      - {id: nulls, type: u4}
      - {id: adjacent, type: u1, repeat: expr, repeat-expr: 3}
      - {id: nulls_01, type: u1}
      - {id: nulls_02, type: u4}
      
  aabb_block:
    seq:
      - {id: x, type: f4, repeat: expr, repeat-expr: 4}
      - {id: y, type: f4, repeat: expr, repeat-expr: 4}
      - {id: z, type: f4, repeat: expr, repeat-expr: 4}
      
  vertex:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
      
  collision_type:
    seq:
      - {id: unk_01, type: f4}
      - {id: unk_02, type: u2}
      - {id: unk_03, type: u2}
      - {id: unk_04, type: u4, repeat: expr, repeat-expr: 3}
      - {id: jp_path, type: u1, repeat: expr, repeat-expr: 12}
      
  s_face_pair: #When a face bounding box contains another face
    seq:
      - {id: face_01, type: u2}
      - {id: face_02, type: u2}
      - {id: quad_order, type: u1, repeat: expr, repeat-expr: 4}#CommonEdge1(f1),CommonEdge2(f1),NoncommonEdge(f1),NoncommonEdge(f2)
      - {id: type, type: u2} #0 floor, 1 wall, 2 airwall
      
  bbox:
    seq:
    - {id: min, type: f4, repeat: expr, repeat-expr: 4}
    - {id: max, type: f4, repeat: expr, repeat-expr: 4}