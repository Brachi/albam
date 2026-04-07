meta:
  endian: le
  bit-endian: le
  file-extension: lmt
  id: lmt
  ks-version: 0.11
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
      is_used:
        value: offset != 0
      lmt_ver:
        value: _parent.version
      block_header:
        pos: offset
        type:
          switch-on: lmt_ver
          cases:
            51: block_header51
            67: block_header67
        if: is_used

  block_header51: # MOTION_INFO
    seq:
      - {id: ofs_frame, type: u4}
      - {id: num_tracks, type: u4}
      - {id: num_frames, type: u4}
      - {id: loop_frame, type: u4}
      - {id: init_position, type: f4, repeat: expr, repeat-expr: 3}
      - {id: filler, type: u4}
      - {id: init_quaterion, type: f4, repeat: expr, repeat-expr: 4}
      - {id: collision_events, type: event_collision}
      - {id: motion_sound_effects, type: motion_se}
    instances:
      tracks:
        {pos: ofs_frame, type: track51, repeat: expr, repeat-expr: num_tracks}

  block_header67: # MOTION_INFO
    seq:
      - {id: ofs_frame, type: u4}
      - {id: num_tracks, type: u4}
      - {id: num_frames, type: u4}
      - {id: loop_frame, type: s4}
      - {id: init_position, type: f4, repeat: expr, repeat-expr: 3}
      - {id: filler, type: u4}
      - {id: init_quaterion, type: f4, repeat: expr, repeat-expr: 4}
      - {id: attr, type: b16}
      - {id: kf_num, type: b5}
      - {id: seq_num, type: b3}
      - {id: duplicate, type: b3}
      - {id: reserved, type: b5}
      - {id: ofs_sequence_infos, type: u4}
      - {id: ofs_keyframe_infos, type: u4} # padding after it
    instances:
      tracks:
        {pos: ofs_frame, type: track67, repeat: expr, repeat-expr: num_tracks}
      sequence_infos:
        {pos: ofs_sequence_infos, type: sequence_info, repeat: expr, repeat-expr: seq_num}
      key_infos:
        {pos: ofs_keyframe_infos, type: keyframe_info, repeat: expr, repeat-expr: kf_num}

  track51: # MOTION_PARAM
    seq:
      - {id: buffer_type, type: u1}
      - {id: usage, type: u1}
      - {id: joint_type, type: u1}
      - {id: bone_index, type: u1}
      - {id: weight, type: f4}
      - {id: len_data, type: u4}
      - {id: ofs_data, type: u4}
      - {id: reference_data, type: f4, repeat: expr, repeat-expr: 4}
    instances:
      data:
        {pos: ofs_data, size: len_data}
  
  track67:
    seq:
      - {id: buffer_type, type: u1}
      - {id: usage, type: u1}
      - {id: joint_type, type: u1}
      - {id: bone_index, type: u1}
      - {id: weight, type: f4}
      - {id: len_data, type: u4}
      - {id: ofs_data, type: u4}
      - {id: reference_data, type: f4, repeat: expr, repeat-expr: 4}
      - {id: ofs_bounds, type: u4}
    instances:
      data:
        {pos: ofs_data, size: len_data}
      is_used:
        value: ofs_bounds != 0
      bounds:
        {pos: ofs_bounds, type: float_buffer, if: is_used}
       
  attr:
    seq:
      - {id: group, type: u4}
      - {id: frame, type: u4}
  
  seq_info_attr:
    seq:
      - {id: unk_00, type: u2}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u4}


  float_buffer:
    seq:
      - {id: addin, type: f4, repeat: expr, repeat-expr: 4} # names were took from Crazy's template
      - {id: offset, type: f4, repeat: expr, repeat-expr: 4}
  
  sequence_info:
    seq:
      - {id: work, type: u2, repeat: expr, repeat-expr: 32}
      - {id: num_seq, type: u4}
      - {id: ofs_seq, type: u4}
    instances:
      attributes:
        {pos: ofs_seq, type: seq_info_attr, repeat: expr, repeat-expr: num_seq} # type is a placeholder for now
        
  keyframe_block:
    seq:
      - {id: unk_00, type: u2}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: f4}
      - {id: unk_03, type: f4}
      - {id: unk_04, type: f4}
        
  keyframe_info:
    seq:
      - {id: type, type: b8}
      - {id: work, type: b16}
      - {id: attr, type: b8}
      - {id: num_key, type: u4}
      - {id: ofs_seq, type: u4}
    instances:
      keyframe_blocks:
        {pos: ofs_seq, type: keyframe_block, repeat: expr, repeat-expr: num_key}
      
  event_collision:
    seq:
      - {id: event_id, type: u2, repeat: expr, repeat-expr: 32}
      - {id: num_events, type: u4}
      - {id: ofs_events, type: u4}
    instances:
      attributes:
        {pos: ofs_events, type: attr, repeat: expr, repeat-expr: num_events}
  
  motion_se:
    seq:
      - {id: event_id, type: u2, repeat: expr, repeat-expr: 32}
      - {id: num_events, type: u4}
      - {id: ofs_events, type: u4}
    instances:
      attributes:
        {pos: ofs_events, type: attr, repeat: expr, repeat-expr: num_events}
  
  
  quadratic_vector3:
    seq:
      - {id: size, type: u1}
      - {id: flags, type: u1}
      - {id: duration, type: u2}
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: outtangent_x, type: f4, if: flags >> 1 > 0}
      - {id: outtangent_y, type: f4, if: flags >> 2 > 0}
      - {id: outtangent_z, type: f4, if: flags >> 4 > 0}
      - {id: nextframeintangent_x, type: f4, if: flags >> 8 > 0}
      - {id: nextframeintangent_y, type: f4, if: flags >> 16 > 0}
      - {id: nextframeintangent_z, type: f4, if: flags >> 32 > 0}
    instances:
      size_:
        value: size

  vec3_frame12:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
    instances:
      size_:
        value: 12
  
  vec3_frame16:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: duration, type: u4}
    instances:
      size_:
        value: 16
  
  quatized8_vec3:
    seq:
    - {id: x, type: u1}
    - {id: y, type: u1}
    - {id: z, type: u1}
    - {id: duration, type: u1}
    instances:
      size_:
        value: 4

  quatized16_vec3:
    seq:
      - {id: x, type: u2}
      - {id: y, type: u2}
      - {id: z, type: u2}
      - {id: duration, type: u2}
    instances:
      size_:
        value: 8
        
  quat3_frame: # w component calculater
    seq:
     - {id: x, type: f4}
     - {id: y, type: f4}
     - {id: z, type: f4}
    instances:
      size_:
        value: 12
      
  quat_framev14:
    seq:
      - {id: w, type: b14}
      - {id: z, type: b14}
      - {id: y, type: b14}
      - {id: x, type: b14}
      - {id: duration, type: b8}
    instances:
      size_:
        value: 8
     
  quatized32_quat:
    seq:
      - {id: w, type: b7}
      - {id: z, type: b7}
      - {id: y, type: b7}
      - {id: x, type: b7}
      - {id: duration, type: b4}
    instances:
      size_:
        value: 4

  xw_quat:
    seq:
      - {id: x, type: b14}
      - {id: w, type: b14}
      - {id: duration, type: b4}
    instances:
      size_:
        value: 4
    
  yw_quat:
    seq:
      - {id: y, type: b14}
      - {id: w, type: b14}
      - {id: duration, type: b4}
    instances:
      size_:
        value: 4
  
  zw_quat:
    seq:
      - {id: z, type: b14}
      - {id: w, type: b14}
      - {id: duration, type: b4}
    instances:
      size_:
        value: 4
    
  quatized11_quat:
    seq:
      - {id: x, type: b11}
      - {id: y, type: b11}
      - {id: z, type: b11}
      - {id: w, type: b11}
      - {id: duration, type: b4}
    instances:
      size_:
        value: 6
  
  quatized9_quat:
    seq:
      - {id: x, type: b9}
      - {id: y, type: b9}
      - {id: z, type: b9}
      - {id: w, type: b9}
      - {id: duration, type: b4}
    instances:
      size_:
        value: 5
 
      
  polar_frame:
    seq:
      - {id: x, type: b17}
      - {id: y, type: b17}
      - {id: w, type: b19}
      - {id: flags, type: b3}
      - {id: duration, type: b8}
    instances:
      size_:
        value: 8
  
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
