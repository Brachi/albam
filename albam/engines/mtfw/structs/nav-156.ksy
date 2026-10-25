meta:
  id: nav_156
  file-extension: nav
  endian: le
  ks-version: '0.11'
  title: Resident Evil 5 navmesh
doc: |
    Tail layout: the footer holds a node count (0x1555 = 5461), which is a full
    quadtree for a 64x64 leaf grid:
        4096 leaves (64x64) + 1024 + 256 + 64 + 16 + 4 + 1 = 5461 nodes.
    The first 1365 nodes (32x32 down to 1x1) are all zero in every sample; the
    last 4096 entries are the leaf cells, stored in Morton (Z-order) order.
    Leaf cell size = (node_info.upper - node_info.lower) / 64 on X and Z.

seq:
  - {id: indent, contents: [0x4e, 0x41, 0x56, 0x00]}
  - {id: version, type: u4, valid: 2}
  - {id: reserved, type: u4}
  - {id: num_vertices, type: u4}
  - {id: num_faces, type: u4}
  - {id: num_node_infos, type: u4}
  - {id: vertices, type: vertex, repeat: expr, repeat-expr: num_vertices}
  - {id: faces, type: face, repeat: expr, repeat-expr: num_faces}
  - {id: node_infos, type: node_info, repeat: expr, repeat-expr: num_node_infos}
  - {id: footer_tag, contents: [0x07]}
  - {id: num_grid_nodes, type: u4}
  - {id: internal_nodes, type: grid_cell, repeat: expr, repeat-expr: num_grid_nodes - 4096}
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
      - {id: num_neighbors, type: u4}
      - {id: neighbors, type: neighbor, repeat: expr, repeat-expr: num_neighbors}

  neighbor:
    seq:
      - {id: face_index, type: u4}  # linkNode
      - {id: padding, type: u4}     # per-edge attribute; 0 in samples
      - {id: edge, type: u4, enum: edge} # portal_number, equals edge index 0/1/2
      - {id: centroid_distance, type: f4} # = centroid distance in metres her

  node_info:
    doc: |
      36 bytes on disk; runtime struct is 0x30. The 4-byte pads are
      uninitialized in some builds (0xCDCDCDCD = MSVC debug fill).
      node_offset is probably an offset to grid data in case of multiple node_info
      but there is no example in RE5 files
    seq:
      - {id: node_offset, type: u4}
      - {id: lower, type: vertex}
      - {id: padding_00, size: 4}
      - {id: upper, type: vertex}
      - {id: padding_01, size: 4}

  grid_cell:
    seq:
      - {id: num_faces, type: u4}
      - {id: faces, type: grid_face, repeat: expr, repeat-expr: num_faces}

  grid_face:
    seq:
      - {id: face_index, type: u4}
      - {id: padding, type: u4}

enums:
  edge:
    0: v1_v2
    1: v2_v3
    2: v1_v3