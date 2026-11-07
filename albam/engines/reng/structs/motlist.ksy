meta:
    id: reengine_motlist
    endian: le
    title: RE Engine motion list (.motlist) and motion (.mot) formats
    ks-version: '0.11'

doc: |
  One spec for both files, because a .motlist embeds whole .mot files: the
  top level reads version + magic and hands the file to `motlist` ("mlst")
  or `mot` ("mot "). Every offset inside a mot is relative to the mot's own
  start, so each one is parsed in a substream that begins there.

  Written against Resident Evil 2 (ray-tracing build): motlist 524, mot 492
  (the numeric suffixes of the file names). The version switches below are
  the ones alphaZomega's Noesis plugin (fmt_RE_MESH.py) and the community
  010 template (RE_Engine_motlist.bt) make; versions other than 524/492 are
  untested here.

  Sources: https://github.com/alphazolam/fmt_RE_MESH-Noesis-Plugin
  (fmt_RE_MESH.py, motFile/motlistFile) and
  https://github.com/kagenocookie/RE-Engine-010-Templates (RE_Engine_motlist.bt).

seq:
    - {id: version, type: u4}
    - {id: magic, type: str, size: 4, encoding: ASCII}

instances:
  motlist:
    {pos: 0, size-eos: true, type: motlist, if: magic == "mlst"}
  mot:
    {pos: 0, size-eos: true, type: mot, if: magic == "mot "}

types:
  motlist:
    seq:
      - {id: version, type: u4}
      - {id: id_magic, contents: [0x6d, 0x6c, 0x73, 0x74]}  # mlst
      - {id: reserved_00, type: u8}
      - {id: ofs_motions, type: u8}
      - {id: ofs_motion_ids, type: u8}
      - {id: ofs_name, type: u8}
      - {id: ofs_path, type: u8, if: version > 60}  # motlistPathOffset in the 010 template
      - {id: num_motions, type: u4}
    instances:
      name_raw:  # Hack to overcome https://github.com/kaitai-io/kaitai_struct/issues/187
        {pos: ofs_name, type: u2, repeat: until, repeat-until: _ == 0}
      name:
        {pos: ofs_name, type: str, encoding: UTF-16LE, size: (name_raw.size * 2) - 2}
      motions:
        {pos: ofs_motions, type: motion_pointer, repeat: expr, repeat-expr: num_motions}
      motion_ids:
        {pos: ofs_motion_ids, type: motion_id, repeat: expr, repeat-expr: num_motions}

  motion_pointer:
    doc: |
      Pointers can be 0 or repeat an earlier one; both readers skip those.
      What sits at the pointer is usually a mot; the 010 template also knows
      motion trees ("mtre"), camera motions ("mcam") and links (version 1).
    seq:
      - {id: ofs_motion, type: u8}
    instances:
      magic:
        {pos: ofs_motion + 4, type: str, size: 4, encoding: ASCII, if: ofs_motion != 0}
      mot:
        {pos: ofs_motion, size-eos: true, type: mot, if: ofs_motion != 0 and magic == "mot "}

  motion_id:
    doc: 72 bytes per entry for motlist >= 484 (Noesis motionIDsData [72, 8]).
    seq:
      - {id: ofs_extra_clips, type: u8}
      - {id: motion_id, type: u2}
      - {id: switch, type: u2}
      - {id: unk_00, type: u4}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u1, repeat: expr, repeat-expr: 3}
      - {id: num_extra_clips, type: u1}
      - {id: unk_03, type: u4, repeat: expr, repeat-expr: 3}
      - {id: reserved, size: 36}

  mot:
    seq:
      - {id: version, type: u4}
      - {id: id_magic, contents: [0x6d, 0x6f, 0x74, 0x20]}  # "mot "
      - {id: unk_00, type: u4}
      - {id: size_mot, type: u4}  # 0 for mots embedded in a motlist
      - {id: ofs_bones_header, type: u8}
      - {id: ofs_bone_clip_headers, type: u8}
      - {id: ofs_property_tracks, type: u8}
      - {id: reserved_00, type: u8}
      - {id: ofs_clips, type: u8}
      - {id: ofs_jmap, type: u8}
      - {id: ofs_end_clips, type: u8}
      - {id: ofs_end_clip_frame_values, type: u8, if: version >= 456}
      - {id: ofs_property_tree, type: u8}
      - {id: ofs_name, type: u8}
      - {id: num_frames, type: f4}
      - {id: blending, type: f4}
      - {id: unk_float_00, type: f4}
      - {id: unk_float_01, type: f4}
      - {id: num_bones, type: u2}
      - {id: num_bone_clip_headers, type: u2}
      - {id: num_clips, type: u1}
      - {id: num_end_clips, type: u1}
      - {id: unk_01, type: u2, if: version >= 458}
      - {id: frame_rate, type: u2}
      - {id: num_property_tracks, type: u2}
      - {id: unk_02, type: u2}
    instances:
      name_raw:
        {pos: ofs_name, type: u2, repeat: until, repeat-until: _ == 0, if: ofs_name != 0}
      name:
        {pos: ofs_name, type: str, encoding: UTF-16LE, size: (name_raw.size * 2) - 2, if: ofs_name != 0}
      has_bones:
        doc: |
          In a motlist usually only the first mot carries the skeleton; the
          others point ofs_bones_header at (or past) their own end. Readers
          then reuse the bones of an earlier mot (Noesis: motlist.boneHeaders).
        value: ofs_bones_header != 0 and (size_mot == 0 or size_mot > ofs_bones_header)
      bones_header:
        {pos: ofs_bones_header, type: bones_header, if: has_bones}
      bone_clip_headers:
        pos: ofs_bone_clip_headers
        type: bone_clip_header(version)
        repeat: expr
        repeat-expr: num_bone_clip_headers

  bones_header:
    doc: The motion's own copy of the skeleton (bind pose, local space).
    seq:
      - {id: ofs_bones, type: u8}
      - {id: num_bones, type: u8}
    instances:
      bones:
        {pos: ofs_bones, type: bone, repeat: expr, repeat-expr: num_bones}

  bone:
    seq:
      - {id: ofs_name, type: u8}
      - {id: ofs_parent, type: u8}  # offset of the parent's bone entry, 0 for a root
      - {id: ofs_child, type: u8}
      - {id: ofs_next_sibling, type: u8}
      - {id: translation, type: f4, repeat: expr, repeat-expr: 4}
      - {id: rotation, type: f4, repeat: expr, repeat-expr: 4}  # x, y, z, w
      - {id: index, type: u4}
      - {id: name_hash, type: u4}  # murmur3 (seed 0xffffffff) of the UTF-16LE name
      - {id: reserved, type: u8}
    instances:
      name_raw:
        {pos: ofs_name, type: u2, repeat: until, repeat-until: _ == 0}
      name:
        {pos: ofs_name, type: str, encoding: UTF-16LE, size: (name_raw.size * 2) - 2}
      idx_parent:
        value: 'ofs_parent == 0 ? -1 : (ofs_parent - _parent.ofs_bones) / 80'

  bone_clip_header:
    params:
      - {id: version, type: u4}
    seq:
      - {id: bone_index, type: u2}
      - {id: track_flags, type: u1}  # bit 0 translation, bit 1 rotation, bit 2 scale
      - {id: unk_flags, type: u1}
      - {id: bone_hash, type: u4}  # murmur3 of the bone name, as in bone.name_hash
      - {id: unk_float_00, type: f4, if: version == 65}
      - {id: reserved_00, type: u4, if: version == 65}
      - id: ofs_tracks
        type:
          switch-on: version
          cases:
            43: u8
            65: u8
            _: u4
    instances:
      has_translation:
        value: track_flags & 1 != 0
      has_rotation:
        value: track_flags & 2 != 0
      has_scale:
        value: track_flags & 4 != 0
      tracks:
        pos: ofs_tracks
        type: bone_tracks(version, track_flags)

  bone_tracks:
    params:
      - {id: version, type: u4}
      - {id: track_flags, type: u1}
    seq:
      - id: translation
        type: track(version, 0)
        if: track_flags & 1 != 0
      - id: rotation
        type: track(version, 1)
        if: track_flags & 2 != 0
      - id: scale
        type: track(version, 2)
        if: track_flags & 4 != 0

  track:
    doc: |
      One channel of one bone. `keys` holds the raw keys; turning them into
      values takes `unpack` (u) as below, with n = v / (2^bits - 1) for each
      packed component v (verified on every RE2 RT figure motion: the packed
      components of each track reach both 0 and 2^bits - 1).

      Translation / scale:
        full, x / y / z / xyz:  the floats as read; the axes a single-axis
                                key leaves out are u[0], u[1], u[2] in order
                                (x key -> (k, u1, u2), y -> (u0, k, u2), z -> (u0, u1, k)),
                                xyz -> (k, k, k)
        5bit, 10bit, 21bit:     (u0*nx + u3, u1*ny + u4, u2*nz + u5)
        x_16bit:                (u0*n + u1, u2, u3); y_16bit (u1, u0*n + u2, u3);
                                z_16bit (u1, u2, u0*n + u3); xyz_16bit all = u0*n + u1
      Rotation (quaternion x, y, z, w; w = sqrt(max(0, 1 - x^2 - y^2 - z^2))
      for everything but `full`):
        5bit, 8bit, 10bit, 13bit, 16bit, 18bit, 21bit:
                                (u0*nx + u4, u1*ny + u5, u2*nz + u6)
        x_16bit / y_16bit / z_16bit: that axis = u0*n + u1, the other two 0
        x / y / z:              that axis = the float, the other two 0
        3component(_b):         the three floats as read
      The quaternions are in the same convention as the mesh's bind matrices
      (Noesis conjugates them because of its own convention).

      A track with one key has no frame indices; the key is at frame 0.
    params:
      - {id: version, type: u4}
      - {id: kind, type: u1}  # 0 translation, 1 rotation, 2 scale
    seq:
      - {id: flags, type: u4}
      - {id: num_keys, type: u4}
      - {id: frame_rate, type: u4, if: version < 78}
      - {id: max_frame, type: f4, if: version < 78}
      - id: ofs_frame_indices
        type:
          switch-on: version >= 78
          cases:
            true: u4
            false: u8
      - id: ofs_frame_data
        type:
          switch-on: version >= 78
          cases:
            true: u4
            false: u8
      - id: ofs_unpack
        type:
          switch-on: version >= 78
          cases:
            true: u4
            false: u8
    instances:
      compression:
        doc: Key encoding, flags & 0xff000 (Noesis readFrame, 010 Load* names).
        value: flags & 0xff000
      frame_index_type:
        doc: Width of the frame numbers, flags >> 20 (2 u1, 4 u2, 5 u4).
        value: flags >> 20
      encoding:
        doc: |
          compression tagged with the track kind, since the same bits mean
          different things for rotations. Scales use the translation codes
          (Noesis reads both through the same branch). Only the meanings of
          mot >= 78 (RE3 onwards, which includes RE2 RT's 492) are listed.
        value: '(kind == 1 ? 0x100000 : 0) | compression'
        enum: key_encoding
      frame_indices:
        doc: Absent (offset 0) when the track has a single key, which is then at frame 0.
        pos: ofs_frame_indices
        type:
          switch-on: frame_index_type
          cases:
            2: u1
            4: u2
            5: u4
        repeat: expr
        repeat-expr: num_keys
        if: ofs_frame_indices != 0
      num_unpack:
        doc: |
          Floats the quantized encodings scale and offset their keys with.
          The single-axis encodings (compression & 0xf000 != 0) use four,
          the others eight; see the `track` doc for which slot is which.
        value: '(compression & 0xf000) != 0 ? 4 : 8'
      unpack:
        pos: ofs_unpack
        type: f4
        repeat: expr
        repeat-expr: num_unpack
        if: ofs_unpack != 0
      keys:
        pos: ofs_frame_data
        type:
          switch-on: encoding
          cases:
            key_encoding::translation_full: vec3
            key_encoding::translation_5bit: packed_5bit
            key_encoding::translation_x_16bit: u2_value
            key_encoding::translation_y_16bit: u2_value
            key_encoding::translation_z_16bit: u2_value
            key_encoding::translation_xyz_16bit: u2_value
            key_encoding::translation_10bit: packed_10bit
            key_encoding::translation_x: f4_value
            key_encoding::translation_y: f4_value
            key_encoding::translation_z: f4_value
            key_encoding::translation_xyz: f4_value
            key_encoding::translation_21bit: packed_21bit
            key_encoding::rotation_full: vec4
            key_encoding::rotation_5bit: packed_5bit
            key_encoding::rotation_x_16bit: u2_value
            key_encoding::rotation_y_16bit: u2_value
            key_encoding::rotation_z_16bit: u2_value
            key_encoding::rotation_8bit: u1_vec3
            key_encoding::rotation_10bit: packed_10bit
            key_encoding::rotation_x: f4_value
            key_encoding::rotation_y: f4_value
            key_encoding::rotation_z: f4_value
            key_encoding::rotation_13bit: packed_13bit_be
            key_encoding::rotation_16bit: u2_vec3
            key_encoding::rotation_18bit: packed_18bit_be
            key_encoding::rotation_21bit: packed_21bit
            key_encoding::rotation_3component: vec3
            key_encoding::rotation_3component_b: vec3
        repeat: expr
        repeat-expr: num_keys
        if: version >= 78

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

  f4_value:
    seq:
      - {id: value, type: f4}

  u2_value:
    seq:
      - {id: value, type: u2}

  u1_vec3:
    seq:
      - {id: x, type: u1}
      - {id: y, type: u1}
      - {id: z, type: u1}

  u2_vec3:
    seq:
      - {id: x, type: u2}
      - {id: y, type: u2}
      - {id: z, type: u2}

  packed_5bit:
    meta:
      bit-endian: le
    seq:
      - {id: x, type: b5}
      - {id: y, type: b5}
      - {id: z, type: b5}
      - {id: reserved, type: b1}

  packed_10bit:
    meta:
      bit-endian: le
    seq:
      - {id: x, type: b10}
      - {id: y, type: b10}
      - {id: z, type: b10}
      - {id: reserved, type: b2}

  packed_21bit:
    meta:
      bit-endian: le
    seq:
      - {id: x, type: b21}
      - {id: y, type: b21}
      - {id: z, type: b21}
      - {id: reserved, type: b1}

  packed_13bit_be:
    doc: 5 bytes read as a big-endian 40-bit integer, x in its lowest 13 bits.
    meta:
      bit-endian: be
    seq:
      - {id: reserved, type: b1}
      - {id: z, type: b13}
      - {id: y, type: b13}
      - {id: x, type: b13}

  packed_18bit_be:
    doc: 7 bytes read as a big-endian 56-bit integer, x in its lowest 18 bits.
    meta:
      bit-endian: be
    seq:
      - {id: reserved, type: b2}
      - {id: z, type: b18}
      - {id: y, type: b18}
      - {id: x, type: b18}

enums:
  key_encoding:
    0x00000: translation_full         # LoadVector3sFull
    0x20000: translation_5bit         # LoadVector3s5BitB
    0x21000: translation_x_16bit      # LoadVector3sXAxis16Bit
    0x22000: translation_y_16bit      # LoadVector3sYAxis16Bit
    0x23000: translation_z_16bit      # LoadVector3sZAxis16Bit
    0x24000: translation_xyz_16bit    # LoadVector3sXYZAxis16Bit
    0x40000: translation_10bit        # LoadVector3s10BitB
    0x41000: translation_x            # LoadVector3sXAxis
    0x42000: translation_y            # LoadVector3sYAxis
    0x43000: translation_z            # LoadVector3sZAxis
    0x44000: translation_xyz          # LoadVector3sXYZAxis
    0x80000: translation_21bit        # LoadVector3s21BitB
    0x100000: rotation_full           # LoadQuaternionsFull
    0x120000: rotation_5bit           # LoadQuaternions5Bit
    0x121000: rotation_x_16bit        # LoadQuaternionsXAxis16Bit
    0x122000: rotation_y_16bit        # LoadQuaternionsYAxis16Bit
    0x123000: rotation_z_16bit        # LoadQuaternionsZAxis16Bit
    0x130000: rotation_8bit           # LoadQuaternions8Bit
    0x140000: rotation_10bit          # LoadQuaternions10Bit
    0x141000: rotation_x              # LoadQuaternionsXAxis
    0x142000: rotation_y              # LoadQuaternionsYAxis
    0x143000: rotation_z              # LoadQuaternionsZAxis
    0x150000: rotation_13bit          # LoadQuaternions13Bit
    0x160000: rotation_16bit          # LoadQuaternions16Bit
    0x170000: rotation_18bit          # LoadQuaternions18Bit
    0x180000: rotation_21bit          # LoadQuaternions21Bit
    0x1b0000: rotation_3component     # LoadQuaternions3Component
    0x1c0000: rotation_3component_b   # LoadQuaternions3Component
