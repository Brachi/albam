meta:
  endian: le
  file-extension: chn
  id: chn
  ks-version: '0.11'
  title: MTFramework chain (.chn, rChain) version 0x80618
doc: |
  Chain (cloth / hair "chain" simulation) resource of the older MT Framework
  generation: Resident Evil 5 and DMC4 Special Edition (both expose
  rChain::getExt -> "chn").  DMC4 (2008) does not have this class - its cloth
  chain is rCnsChain, extension "clt".

    rChain::Header      0x10  magic, version, data_size, chain_info_num, reserve[3]
    rChain::ChainInfo   0x20  joint_info_num, chain_type, reserve, joint_info_offset,
                                    reserve1[2], grav_scaler, time_scaler, dump_scaler, freserve
    rChain::JointInfo   0x60  attr, ref_joint_no, node_num, reserve0, reserve1[2],
                                    min_angle, spring_coef, max_angle, dumping_coef, mass,
                                    restrict_flag, col_shape, reserve2[2], col_radius,
                                    air_regist, node_joint_no[8], friction, soft_coef,
                                    bend_regist, reserve[3]

  rChain::DATA_VERSION = 0x80618 (rChain::load compares the header version with
  it).  rChain::load reads 16 header bytes, allocates data_size bytes and reads
  them; getExt returns "chn".

  Layout: the 16-byte header is followed by a table of chain_info_num ChainInfo
  records (32 bytes each, all of them first), then the JointInfo records
  (96 bytes each).  A chain's joints start at

      chain_info_position + joint_info_offset      (chain_info_position = 16 + 32 * index)

  and data_size = 32 * chain_info_num + 96 * sum(joint_info_num).
  File size = 16 + data_size

seq:
  - {id: magic, contents: [0x43, 0x48, 0x4e, 0x00]}   # 'CHN\0'
  - {id: version, type: u4, valid: 0x80618}
  - {id: data_size, type: u4}          # bytes of the chain table after the header
  - {id: num_chain_infos, type: u1}    # rChain::Header::chain_info_num
  - {id: reserve, size: 3}
  - {id: chain_infos, type: chain_info(_index), repeat: expr, repeat-expr: num_chain_infos}

instances:
  expected_size:
    value: 16 + data_size

types:
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  chain_info:  # rChain::ChainInfo /* size : 0x20 */
    params:
      - {id: index, type: u4}
    doc: |
      joint_info_offset is relative to the start of this ChainInfo record, so the
      joints of chain `i` live at 16 + 32 * i + joint_info_offset.
    seq:
      - {id: num_joints, type: u1}      # rChain::ChainInfo::joint_info_num
      - {id: chain_type, type: u1, enum: chain_type}
      - {id: reserve, type: u2}
      - {id: joint_info_offset, type: u4}
      - {id: reserve1, type: u4, repeat: expr, repeat-expr: 2}
      - {id: grav_scaler, type: f4}
      - {id: time_scaler, type: f4}
      - {id: dump_scaler, type: f4}
      - {id: freserve, type: f4}
    instances:
      position:
        value: 16 + 32 * index
      joints_pos:
        value: position + joint_info_offset
      joints:
        pos: joints_pos
        type: joint_info
        repeat: expr
        repeat-expr: num_joints

  joint_info:  # rChain::JointInfo /* size : 0x60 */
    doc: |
      attr is a bit set of JOINT_ATTRIBUTE (1 constraint, 2 attached, 4 no rotate);
      col_shape is a JOINT_COL_SHAPE (1 sphere, 2 capsule).  node_joint_no holds
      up to JOINT_NODE_MAX (8) bone ids of the nodes this joint drags, node_num is
      how many of them are used.  min_angle / max_angle are the angle limits.
    seq:
      - {id: attr, type: u4}
      - {id: ref_joint_no, type: u2}
      - {id: node_num, type: u1}
      - {id: reserve0, type: u1}
      - {id: reserve1, type: u4, repeat: expr, repeat-expr: 2}
      - {id: min_angle, type: vec3}
      - {id: spring_coef, type: f4}
      - {id: max_angle, type: vec3}
      - {id: dumping_coef, type: f4}
      - {id: mass, type: f4}
      - {id: restrict_flag, type: u1}
      - {id: col_shape, type: u1, enum: col_shape}
      - {id: reserve2, size: 2}
      - {id: col_radius, type: f4}
      - {id: air_regist, type: f4}
      - {id: node_joint_no, type: u1, repeat: expr, repeat-expr: 8}
      - {id: friction, type: f4}
      - {id: soft_coef, type: f4}
      - {id: bend_regist, type: f4}
      - {id: reserve, type: u4, repeat: expr, repeat-expr: 3}

enums:
  chain_type:  # rChain::ChainInfo::CHAIN_TYPE
    1: chain
    2: shake
  col_shape:  # rChain::JointInfo::JOINT_COL_SHAPE
    1: sphere
    2: capsule
