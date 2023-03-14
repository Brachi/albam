meta:
  endian: le
  file-extension: lmt
  id: lmt
  ks-version: 0.10
  title: MTFramework animation format


seq:
  - {id: id_magic, contents: [0x4c, 0x4d, 0x54, 0x00]}
  - {id: version, type: u2}
  - {id: num_block_offsets, type: u2}
  - {id: block_offsets, type: block_offset, repeat: expr, repeat-expr: num_block_offsets}


types:
  block_offset:
    seq:
      - {id: offset, type: u4}
    instances:
      block_header:
        {type: block_header, pos: offset}

  block_header:
    seq:
      - {id: ofs_frame, type: u4}
      - {id: num_tracks, type: u4}
      - {id: num_frames, type: u4}
      - {id: unk_01, type: u4, repeat: expr, repeat-expr: 25}
      - {id: count_01, type: u4}
      - {id: ofs_buffer, type: u4}
      - {id: unk_02, type: u4, repeat: expr, repeat-expr: 16}
      - {id: count_02, type: u4}
      - {id: ofs_02, type: u4}
    instances:
      tracks:
        {pos: ofs_frame, type: track, repeat: expr, repeat-expr: num_tracks}


  track:
    seq:
      - {id: buffer_type, type: u1}
      - {id: usage, type: u1}
      - {id: joint_type, type: u1}
      - {id: bone_index, type: u1}
      - {id: unk_01, type: f4}
      - {id: len_data, type: u4}
      - {id: ofs_data, type: u4}
      - {id: unk_reference_data, type: f4, repeat: expr, repeat-expr: 4}
    instances:
      data:
        {pos: ofs_data, size: len_data}
