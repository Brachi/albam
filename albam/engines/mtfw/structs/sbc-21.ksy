meta:
  endian: le
  file-extension: sbc
  id: sbc_21
  ks-version: '0.11'
  title: MTFramework collision format version 210

doc: |
  FIELD NAMES:
    file header        = rCollision::Header
    info[]             = rCollision::PartsInfo
    face[]             = rCollision::Triangle
    vertex[]           = rCollision::Vertex
    collision_type[]   = rCollision::MaterialInfo (: nCollision::ScrMaterialInfo)
    pairs[]            = rCollision::Leaf
    bvh_collision      = cBVHCollision::Header + cBVHCollision::NodeQuad
    pair_aabb[]        = cGridCollisionRegistInfo (first 28 bytes)
    grco               = cGridCollision (mMagic 'grco', mVersion 2009111700)

  space division types (rCollision::ESPACE_DIVISION_TYPE):
    0 = BVH_QUAD, 1 = BVH_BINARY, 2 = GRID, 3 = MAX
  -> header.unk_02 / header.unk_03 hold exactly this enum; the REV1 "grid"
     files are simply `SpaceDivisionTypeTriangle == GRID`.

seq:
  - {id: header, type: sbc_header}
  - {id: sbc_info, type: info, repeat: expr, repeat-expr: header.num_objects}
  # REV1 grid variant only: one inflated AABB per collision pair
  # (cGridCollisionRegistInfo, 28 bytes each).
  - {id: pair_aabbs, type: pair_aabb, repeat: expr, repeat-expr: 'header.is_grid ? header.num_pairs : 0'}
  # Grid variant has a single (root) BVH block; the classic layout has one per
  # object plus a trailing root block.
  - {id: sbc_bvhc, type: bvh_collision, repeat: expr, repeat-expr: 'header.is_grid ? 1 : header.num_objects'}
  - {id: bvh, type: bvh_collision, if: not header.is_grid}
  - {id: faces, type: face, repeat: expr, repeat-expr: header.num_faces}
  - {id: vertices, type: vertex, repeat: expr, repeat-expr: header.num_vertices}
  - {id: collision_types, type: collision_type, repeat: expr, repeat-expr: header.num_stages}
  - {id: pairs_collections, type: s_face_pair, repeat: expr, repeat-expr: header.num_pairs}
  # REV1 grid variant only: trailing uniform collision grid (cGridCollision).
  - {id: grco, type: grco_block, if: header.is_grid}

types:
  sbc_header: #rCollision::Header  (80 bytes; sbc21 appends bb_size -> 84)
    seq:
     - {id: indent, contents: [0x53, 0x42, 0x43, 0xff]}
     - {id: version, type: u4}
     - {id: space_div_type_part, type: u4}          # SpaceDivisionTypeParts   0 = BVH_QUAD
     - {id: space_div_type_triangle, type: u4}      # SpaceDivisionTypeTriangle 0 = BVH_QUAD, 2 = GRID
     - {id: num_objects, type: u2}     # PartsInfoNum
     - {id: num_stages, type: u2}      # MaterialInfoNum
     - {id: num_pairs, type: u4}       # TotalLeafNum   ("pairs" are collision leaves)
     - {id: num_faces, type: u4}       # TotalTriangleNum
     - {id: num_vertices, type: u4}    # TotalVertexNum
     - {id: nulls, type: u4, repeat: expr, repeat-expr: 4}
       # [0] = TotalModifyNum (count of mpSbcModifyClassIDArray entries, 0 here)
       # [1..3] = reserved / padding (0 in every REV1 file)
     - {id: bounding_box, type: bbox4} # TotalAABB (MtAABB)
     - {id: bb_size, type: u4}         # not an engine field: export-time total
                                       # = 112*nodes [+ 8*cells + 2*params for grid]
    instances:
      size_:
        value: 84
      is_grid:
        doc: True when the file uses the REV1 pair-AABB + 'grco' grid layout.
        value: space_div_type_triangle != 0

  info: #rCollision::PartsInfo (80 bytes) - one per collision object / part
    seq:
      - {id: bounding_box, type: bbox4}   # bv  (MtAABB)
      - {id: unk_01, type: u4}            # pBvh            (0 in grid files)
      - {id: nulls_01, type: u4, repeat: expr, repeat-expr: 2}
        # [0] = pGrid            (non-zero in grid files)
        # [1] = pGridRegistInfo  (non-zero in grid files)
      - {id: start_pairs, type: u4}       # LeafIndex
      - {id: num_pairs, type: u4}         # LeafNum     (u16 + 2 bytes padding)
      - {id: start_faces, type: u4}       # TriangleIndex
      - {id: num_faces, type: u4}         # TriangleNum (u16 + 2 bytes padding)
      - {id: start_vertices, type: u4}    # VertexIndex
      - {id: num_vertices, type: u4}      # VertexNum   (u16 + 2 bytes padding)
      - {id: index_id, type: u4}          # Id
      - {id: nulls_02, type: u4, repeat: expr, repeat-expr: 2}   # padding
    instances:
      size_:
        value: 80

  pair_aabb: #cGridCollisionRegistInfo  The box is the pair's geometry AABB inflated by 1 unit on every side.
    doc: |
      28 bytes: { f4 min[3]; u4 pair_index; f4 max[3] }.
      `pair_index` runs 0..num_pairs-1 in file order (mRegistParam).
    seq:
      - {id: aabb_min, type: f4, repeat: expr, repeat-expr: 3}  # mRegistAABBMinPos
      - {id: pair_index, type: u4}                              # mRegistParam
      - {id: aabb_max, type: f4, repeat: expr, repeat-expr: 3}  # mRegistAABBMaxPos
    instances:
      size_:
        value: 28

  bvh_collision: #cBVHCollision::Header (64 bytes)
    seq:
      - {id: bvhc, type: u4, repeat: expr, repeat-expr: 2}
        # [0] = magic 'BVHC' (1128814146), [1] = version (2008120100)
      - {id: soh, type: u4}               # type
      - {id: unk_01, type: u4}            # padding
      - {id: bounding_box, type: bbox4}   # aabb (MtAABB)
      - {id: num_nodes, type: u4}         # NodeNum
      - {id: nulls, type: u4, repeat: expr, repeat-expr: 3}
        # [0] = LeafNum  (number of leaves stored in this tree)
        # [1] = FlgBasicAllocedMultiple (u8) + FlgNodeOutsideAllocateMemory (u8)
        # [2] = padding
      - {id: nodes, type: bvh_node, repeat: expr, repeat-expr: num_nodes}

  bvh_node: #cBVHCollision::NodeQuad (112 bytes) = NodeQuadBase (12) + pad + NodeAABB
    seq:
      - {id: node_type, type: u1, repeat: expr, repeat-expr: 4}
        # NodeQuadBase::Status (u32) written byte-wise:
        #   0x10 = leaf, other values = quad/child markers (Status0/1/2 bitfields)
      - {id: node_id, type: u2, repeat: expr, repeat-expr: 4}   # ChildIndex[4]
      - {id: unk_05, type: u4}            # padding (0xCDCDCDCD debug fill)
      - {id: min_aabb, type: aabb_block}  # NodeAABB.minpos4 (MtAABB4)
      - {id: max_aabb, type: aabb_block}  # NodeAABB.maxpos4 (MtAABB4)


  face: #rCollision::Triangle (32 bytes)
    seq:
      - {id: normal, type: f4, repeat: expr, repeat-expr: 3}   # normal (MtFloat3)
      - {id: vert, type: u2, repeat: expr, repeat-expr: 3}     # vert_index[3]
      - {id: type, type: u2}             # material_index (material id, values 0..15!)
      - {id: nulls, type: u4}            # attribute[3] (0x14..0x16) + 1 byte padding
      - {id: adjacent, type: u1, repeat: expr, repeat-expr: 3}  # adjustParam[3]
      - {id: nulls_01, type: u1}         # reserved
      - {id: nulls_02, type: u4}         # PhysicsReserved


  aabb_block: #MtCollisionUtil::MtSoaVector3 - side by side (x[4], y[4], z[4]) layout
    seq:
      - {id: x, type: f4, repeat: expr, repeat-expr: 4}
      - {id: y, type: f4, repeat: expr, repeat-expr: 4}
      - {id: z, type: f4, repeat: expr, repeat-expr: 4}

  vertex: #rCollision::Vertex (16 bytes)
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4} # attribute (u32, always 0 in files)


  # unsigned int attribute;
  # unsigned int attr[4];
  # unsigned int pading[3];
  collision_type: #rCollision::MaterialInfo : nCollision::ScrMaterialInfo (32 bytes)
    seq:
      - {id: attribute, type: u4}           # attribute (u32)
      - {id: unk_02, type: u2}           # attr[0..1]
      - {id: unk_03, type: u2}           # attr[2..3]
      - {id: unk_04, type: u4, repeat: expr, repeat-expr: 3}   # attr[4..15]
      - {id: jp_path, type: u1, repeat: expr, repeat-expr: 12} # pading[12] (padding, 0xFE)
    instances:
      size_:
        value: 32

  s_face_pair: # rCollision::Leaf (10 bytes)
    seq:
      - {id: face_01, type: u2}          # TriangleIndex[0]
      - {id: face_02, type: u2}          # TriangleIndex[1] (0xffff == single triangle)
      - {id: quad_order, type: u1, repeat: expr, repeat-expr: 4}
        # actually two u16: CommonUseVertexIndex (0x04) + NoCommonVertexIndex (0x06)
        # (0xffff == "no common vertex")
      - {id: type, type: u2}             # MaterialIndex (material id, values 0..15)

  bbox4: #MtAABB (32 bytes) - used by the header TotalAABB and by PartsInfo::bv
    seq:
    - {id: min, type: f4, repeat: expr, repeat-expr: 4}   # minpos (MtVector3 + w)
    - {id: max, type: f4, repeat: expr, repeat-expr: 4}   # maxpos (MtVector3 + w)


  grco_block: # REV1 tail for SpaceDivisionTypeTriangle = GRID
    doc: |
      'grco' == Grid Collision.  Grid cells index the collision *leaves*
      (`pairs_collections`): a cell covers regist_params[leaf_start : leaf_start
      + leaf_num].  With flg_static_mode == 0 the grid is rebuilt on load and the
      file stores neither the cells nor the params (not seen in REV1 files).
    seq:
      - {id: magic, contents: [0x67, 0x72, 0x63, 0x6f]}   # mMagic 'grco'
      - {id: version, type: u4}                          # mVersion (2009111700)
      - {id: bounding_box, type: bbox4}   # mBoundingAABB (== SBC header bbox)
      - {id: grid_num_x, type: u2}        # mGridNumX
      - {id: grid_num_z, type: u2}        # mGridNumZ
      - {id: cell_mode, type: u1}         # mCellMode 0 = CELLMODE_U32, 1 = CELLMODE_U16
      - {id: flg_static_mode, type: u1}   # mFlgStaticMode (1 = cells stored)
      - {id: cells, type: grco_cell, repeat: expr, repeat-expr: grid_num_x * grid_num_z}
      - {id: num_regist_params, type: u4} # mStaticGridRegistParamNum
      - id: regist_params_u16
        type: u2
        repeat: expr
        repeat-expr: 'cell_mode == 1 ? num_regist_params : 0'
        doc: Leaf indices (mStaticGridRegistParam, cell_mode == CELLMODE_U16).
      - id: regist_params_u32
        type: u4
        repeat: expr
        repeat-expr: 'cell_mode == 0 ? num_regist_params : 0'
        doc: Leaf indices (mStaticGridRegistParam, cell_mode == CELLMODE_U32).

  grco_cell:   # cGridCollision::StaticGridInfo (8 bytes)
    seq:
      - {id: leaf_num, type: u2}     # mLeafNum   (0 == empty cell)
      - {id: pad, type: u2}          # padding
      - {id: leaf_start, type: u4}   # mLeafStart (index into regist_params)
