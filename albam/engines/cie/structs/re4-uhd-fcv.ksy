meta:
  id: re4_uhd_fcv
  endian: le
  ks-version: "0.11"
  title: RE4UHD skeletal motion (.fcv)

# One motion clip: per animated joint, three Hermite curves (x, y, z) of
# rotation, translation or scale. It is the GameCube "MotionData" layout
# (game/motion.cpp MotionSetCore and HermiteInterpolation in the RE4
# decompilation at github.com/adonis-singh/re4, tools/motion/fcv.py) written
# little-endian - except `size`, which stays big-endian.
#
# Where they are: character, enemy and weapon archives (BIO4/Em/*.udas.lfs)
# hold them as numbered entries next to the models, 12962 in all; events
# (BIO4/Evd/*.evd.lfs) hold them by name, the cam/*.fcv ones being camera
# moves rather than skeletons (every joint on channel 6, see joint_info).
# Each archive also carries .seq entries, the playback tables the game pairs
# with a motion (sound / effect triggers per frame), which this does not read.
#
# Units: angles in radians, composed as the game's RotMatrix does,
# Rz * Ry * Rx (x applied first); translations in model units (the same
# millimetres as a model's vertices and bone offsets); 30 frames a second.
# A joint's local matrix is T(pos) * R(ang) * S(scale), and the values are
# absolute, not offsets from the rest pose - an unkeyed part keeps its rest
# translation, zero rotation and unit scale.
#
# Read literally, the translation keys on an IK chain's end joint are
# wrong: see joint_info.is_ik_root for what they actually are.
seq:
  # Bits 14-15 are flags set on some event camera motions; the game masks
  # them off (see max_frame).
  - {id: max_frame_raw, type: u2}
  - {id: num_joints, type: u1}
  - {id: joint_infos, type: joint_info, repeat: expr, repeat-expr: num_joints}
  # The model part (bone id) each joint drives.
  - {id: parts_nos, type: u1, repeat: expr, repeat-expr: num_joints}
  - {id: padding, size: (4 - (3 + 3 * num_joints) % 4) % 4}
  # The entry's size including its trailing 0xCD (or 0x00) padding to 32
  # bytes, big-endian even here: 12912 of 12933 parsed motions across BIO4/Em
  # match their own length that way, none little-endian. Event camera
  # motions store 0. The game steps over it unread.
  - {id: size, type: u4be}
  # Where each joint's key block starts, from the start of the entry. The
  # blocks are back to back but not in joint order.
  - {id: key_offsets, type: u4, repeat: expr, repeat-expr: num_joints}
  - {id: joints, type: joint(_index), repeat: expr, repeat-expr: num_joints}

instances:
  # The last frame. A motion plays frames 0 to max_frame inclusive, and
  # every curve's last key sits on it.
  max_frame:
    value: max_frame_raw & 0x3fff

types:
  joint_info:
    seq:
      - {id: raw, type: u2}
    instances:
      # Bits 0-7. What the curves drive, tested in this order by
      # MotionMoveCore:
      #   1     root position: the character's displacement over the clip
      #         (root motion), applied to the whole model rather than a part
      #   0x40  root rotation, likewise
      #   &2    rotation
      #   &4    translation
      #   &8    scale
      #   &0x30 rotation of an IK chain's root (see is_ik_root)
      # 0x80 only ever comes with 0x20 (0xa0, the arms).
      kind:
        value: raw & 0xff
      # Bits 8-11. On a chain root (is_ik_root), the axis the chain bends
      # about: 0 +y, 1 -y, 2 +x, 3 -x, 4 +z, 5 -z. 6 and 7 are camera
      # channels (position, target, roll, fov...), which only an event
      # camera attached to the motion reads; a handful of weapon motions
      # carry broken channel 6 joints the game never touches, with key
      # offsets past the end of the entry.
      channel:
        value: (raw >> 8) & 0xf
      # Bits 12-15. How each key is stored - see key.
      key_type:
        value: raw >> 12
      # A chain root (kind & 0x30) starts an IK chain of the next parts in
      # bone order: root, joint, effector (and, for 0xa0, one more). The
      # translation keys on the effector - the ankle and wrist joints - are
      # not its local offset: they are the position the solver
      # (game/ik.cpp) pulls the chain towards, in model space, and the
      # effector's rotation keys are model space too. With 0x20 the target
      # is where the effector's child (the toe) goes, and the effector is
      # placed so that it does. Applied as plain bone transforms they give
      # stretched or folded limbs.
      is_ik_root:
        value: (kind & 0x30) != 0
      is_camera:
        value: channel == 6 or channel == 7

  joint:
    params:
      - {id: i, type: u2}
    instances:
      info:
        value: _parent.joint_infos[i]
      parts_no:
        value: _parent.parts_nos[i]
      axes:
        pos: _parent.key_offsets[i]
        type: axis(info.key_type)
        repeat: expr
        repeat-expr: 3

  axis:
    params:
      - {id: key_type, type: u1}
    seq:
      - {id: num_keys, type: u2}
      # Ascending; the first is 0 and the last max_frame.
      - {id: frames, type: u2, repeat: expr, repeat-expr: num_keys}
      - {id: keys, type: key(key_type), repeat: expr, repeat-expr: num_keys}

  # Between keys k0 and k1 the curve is the cubic Hermite through
  # value[k0] and value[k1] with tangents out_tangent[k0] and in_tangent[k1],
  # over t = (frame - frame[k0]) / (frame[k1] - frame[k0]); the tangents are
  # not scaled by the span. key_type is two 2-bit fields, value storage
  # times 4 plus tangent storage: 0 f4, 1 s2, 2 s1, where an s2 or s1 is
  # the value times 10000. 15 is an f4 value without tangents, which only
  # the event cameras use.
  key:
    params:
      - {id: key_type, type: u1}
    seq:
      - id: value_raw
        type:
          switch-on: key_type >> 2
          cases:
            1: s2
            2: s1
            _: f4
      - id: in_tangent_raw
        if: key_type != 15
        type:
          switch-on: key_type & 3
          cases:
            1: s2
            2: s1
            _: f4
      - id: out_tangent_raw
        if: key_type != 15
        type:
          switch-on: key_type & 3
          cases:
            1: s2
            2: s1
            _: f4
    instances:
      value:
        value: '(key_type >> 2) == 0 or (key_type >> 2) == 3 ? value_raw : value_raw * 0.0001'
      in_tangent:
        value: 'key_type == 15 ? 0.0 : (key_type & 3) == 0 ? in_tangent_raw : in_tangent_raw * 0.0001'
      out_tangent:
        value: 'key_type == 15 ? 0.0 : (key_type & 3) == 0 ? out_tangent_raw : out_tangent_raw * 0.0001'
