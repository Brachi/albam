meta:
  id: nav_156
  file-extension: nav
  endian: le
  ks-version: "0.11"
  title: Resident Evil 5 navmesh

seq:
  - {id: indent, contents: [0x4e, 0x41, 0x56, 0x00]}
  - {id: version, type: u4, valid: 2}
  - {id: reserved, type: u4}
  - {id: vertex_count, type: u4}
  - {id: face_count, type: u4}
  - {id: header_padding, type: u4}
  - {id: vertices, type: vertex, repeat: expr, repeat-expr: vertex_count}
  - {id: faces, type: face, repeat: expr, repeat-expr: face_count}
  - {id: bbox, type: bounding_box}
  - {id: footer_magic, contents: [0x07, 0x55, 0x15, 0x00, 0x00]}
  - {id: footer_padding, size: 5460}
  - {id: lookup_grid, type: grid_cell, repeat: expr, repeat-expr: 4096}

types:
  vertex:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  face:
    seq:
      - {id: index, type: u4}
      - {id: unk_00, type: u4}
      - {id: flags, type: u4}
      - {id: vertex_per_face, type: u4}
      - {id: v1, type: u4}
      - {id: v2, type: u4}
      - {id: v3, type: u4}
      - {id: neighbor_count, type: u4}
      - {id: neighbors, type: neighbor, repeat: expr, repeat-expr: neighbor_count}

  neighbor:
    seq:
      - {id: face_index, type: u4}
      - {id: padding, type: u4}
      - {id: edge, type: u4, enum: edge}
      - {id: centroid_distance, type: f4}

  bounding_box:
    seq:
      - {id: padding0, type: u4}
      - {id: lower, type: vertex}
      - {id: padding1, size: 4}
      - {id: upper, type: vertex}
      - {id: padding2, size: 4}

  grid_cell:
    seq:
      - {id: face_count, type: u4}
      - {id: faces, type: grid_face, repeat: expr, repeat-expr: face_count}

  grid_face:
    seq:
      - {id: face_index, type: u4}
      - {id: padding, type: u4}

enums:
  edge:
    0: v1_v2
    1: v2_v3
    2: v1_v3