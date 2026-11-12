meta:
  endian: le
  file-extension: ccl
  id: ccl_156
  ks-version: '0.11'
  title: MTFramework chain collision (.ccl, rChainCol) version 0x80618
doc: |
  Chain collision resource: a table of collision primitives, each bound to one
  or two bones of the skeleton

    rChainCol / nChain           : cResource
    rChainCol::Header / nChain   : magic, version, colinfo_num, data_size   (0x10)
    rChainCol::ColInfo           : 0x40 = 64 bytes per collision
    nChain::ColInfo              : same fields, offsets 0x00..0x3c
    rChainCol::DATA_VERSION      : 0x80618

  The old version of this template read 68 bytes per record (an extra u4 after
  the 12 "payload" values), which shifts every record after the first one and
  overruns the file.  The record is 64 bytes:

    0x00 u4 attr             0x04 u2 ref_joint_no    0x06 u2 pair_joint_no
    0x08 u1 shape            0x09 3 bytes reserve    0x0c f4 reserve1
    0x10 f3 position         0x1c u4 id              0x20 f3 extent
    0x2c f4 radius           0x30 f3 angle           0x3c f4 reserve2

  Units: centimetres, angles in radians.  File size = 16 + 64 * colinfo_num and
  the header's data_size is 64 * colinfo_num.

seq:
  - {id: magic, contents: [0x43, 0x43, 0x4c, 0x00]}   # 'CCL\0'
  - {id: version, type: u4, valid: 0x80618}
  - {id: num_col_infos, type: u4}   # rChainCol::Header::colinfo_num
  - {id: data_size, type: u4}       # 64 * num_col_infos
  - {id: col_infos, type: col_info, repeat: expr, repeat-expr: num_col_infos}

instances:
  expected_data_size:
    value: 64 * num_col_infos
  expected_size:
    value: 16 + 64 * num_col_infos

types:
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  col_info:  # rChainCol::ColInfo / nChain::ColInfo /* size : 0x40 */
    doc: |
      ref_joint_no is the bone function id of the .mod bone table; pair_joint_no
      is the second bone for a capsule, otherwise NO_REF_PAIRJOINT (the enum
      declares 0xfff, retail files write 0xffff).

      position / extent / radius / angle are in the bone's local space:
        sphere  (0): position = centre, radius = radius
        capsule (1): position = head, extent = tail, radius = radius
        aabb    (2): position = centre, extent = half size
        obb     (3): position = centre, extent = half size, angle = rotation
      In many sphere records extent is (1,1,1) or (0,0,0), so for spheres its
      meaning is not certain.

      The game does not write reserve / reserve1 / reserve2: retail files hold
      0xcd filler, zeroes or leftover heap bytes there.  Keep them as is.
    seq:
      - {id: attr, type: u4}                  # COLLISION_ATTRIBUTE, 1 = COL_ATTR_ATTACHED
      - {id: ref_joint_no, type: u2}
      - {id: pair_joint_no, type: u2}
      - {id: shape, type: u1, enum: shape}
      - {id: reserve, size: 3}
      - {id: reserve1, type: f4}
      - {id: position, type: vec3}
      - {id: id, type: u4}
      - {id: extent, type: vec3}
      - {id: radius, type: f4}
      - {id: angle, type: vec3}
      - {id: reserve2, type: f4}

enums:
  shape:  # rChainCol::ColInfo::COLLISION_SHAPE
    0: sphere
    1: capsule
    2: aabb
    3: obb
