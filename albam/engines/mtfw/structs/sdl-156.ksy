    
meta:
  endian: le
  bit-endian: le
  id: sdl_156
  file-extension: sdl
  ks-version: "0.11"
  title: MTFramework scene sheduler format

seq:
  - {id: header, type: base_header}
  - {id: tracks, type: track, repeat: expr, repeat-expr: header.num_tracks}

#instances:
#  tracks:
#    {pos: 0x14, type: track, repeat: expr, repeat-expr: header.num_tracks}

types:
  base_header:
    seq:
      - {id: magic, contents: [0x53, 0x44, 0x4c, 0x00]}
      - {id: version, type: u2}
      - {id: num_tracks, type: u2}
      - {id: frame_max, type: b24}
      - {id: floor_frame, type: b1}
      - {id: reserved, type: b7}
      - {id: ofs_dti_table, type: u4}
      - {id: ofs_names, type: u4}
  
  track:
    seq:
      - {id: track_type, type: u1} # track_type
      - {id: prop_type, type: u1}
      - {id: num_frames, type: u2}
      - {id: parent, type: u4}
      - {id: ofs_name, type: u4}
      - {id: dti_ref, type: u4}  # extension hash for files
      - {id: ofs_timing, type: u4} # key_frame
      - {id: ofs_data, type: u4}
    instances:
      size_:
        value: 24
      timing_frames:
        pos: ofs_timing
        type: timing_frame
        repeat: expr
        repeat-expr: num_frames
      data:
        if: ofs_data > 0 and track_type > 5
        pos: ofs_data
        type:
          switch-on: prop_type
          cases:
            3: bool # bool
            4: u8 # u8
            5: u16 # u16
            6: u32 # u32
            7: u64 # u64
            8: s8 # s8
            9: s16 # s16
            10: s32 # s32
            11: s64 # s64
            12: f32 # f32
            13: f64 # f64
            14: mt_str #string
            15: color
            20: vec3
            21: vec4
            22: quaternion
            24: u4  # event size 4 probably u2?
            28: u4  # event32 size 4 probably u4?
            34: float2
            35: float3
            36: float4
            40: mt_easecurve
            55: u4 # RANGE
            57: u4 # HERMITECURVE
            58: resource
        repeat: expr
        repeat-expr: num_frames
      name:
        pos: ofs_name + _root.header.ofs_names
        type: str
        encoding: UTF-8
        terminator: 0

  resource:
    seq:
      - {id: ref_ofs, type: u4}
    instances:
      ref_dti:
        if: ref_ofs != 0
        pos: ref_ofs + _root.header.ofs_names
        type: u4
      ref_path:
        if: ref_ofs != 0
        pos: ref_ofs + _root.header.ofs_names + 4
        type: str
        encoding: UTF-8
        terminator: 0
       
  timing_frame:
    seq:
      - {id: frame, type: b24}
      - {id: type, type: b8}
    #instances:
    #  frame:
    #    value: val & 0xffffff
    #  type:
    #    value: val >> 24
        
  bool:
    seq:
      - {id: val, type: u1}
    instances:
      size_:
        value: 4  # has padding
  u8:
    seq:
      - {id: val, type: u1}
    instances:
      size_:
        value: 4  # has padding
  u16:
    seq:
      - {id: val, type: u2}
    instances:
      size_:
        value: 4  # has padding
  u32:
    seq:
      - {id: val, type: u4}
    instances:
      size_:
        value: 4
  u64:
    seq:
      - {id: val, type: u8}
    instances:
      size_:
        value: 8 # not tested
  s8:
    seq:
      - {id: val, type: s1}
    instances:
      size_:
        value: 4  # has padding
  s16:
    seq:
      - {id: val, type: s2}
    instances:
      size_:
        value: 4  # has padding
  s32:
    seq:
      - {id: val, type: s4}
    instances:
      size_:
        value: 4 
  s64:
    seq:
      - {id: val, type: s8}
    instances:
      size_:
        value: 8 # not tested
  f32:
    seq:
      - {id: val, type: f4}
    instances:
      size_:
        value: 4
  f64:
    seq:
      - {id: val, type: f8}
    instances:
      size_:
        value: 8 # not tested
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
    instances:
      size_:
        value: 16  # has padding
          
  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
    instances:
      size_:
        value: 16 # not tested
  
  quaternion:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
    instances:
      size_:
        value: 16 # not tested
     
  color:
    seq:
      - {id: r, type: f4}
      - {id: g, type: f4}
      - {id: b, type: f4}
      - {id: a, type: f4}
    instances:
      size_:
        value: 16 # not tested
  
  point:
    seq:
      - {id: x, type: s4}
      - {id: y, type: s4}
      
  size:
    seq:
      - {id: w, type: s4}
      - {id: h, type: s4}
      
  mt_str:
    seq:
      - {id: ptr, type: u4}
    instances:
      string:
        pos: ptr
        type: str
        encoding: UTF-8
        terminator: 0
      
  rect:
    seq:
      - {id: l, type: s4}
      - {id: t, type: s4}
      - {id: r, type: s4}
      - {id: b, type: s4}
      

  mat3x3:
    seq:
      - {id: r0, type: vec3}
      - {id: r1, type: vec3}
      - {id: r2, type: vec3}
      
  mat4x3:
    seq:
      - {id: r0, type: vec3}
      - {id: r1, type: vec3}
      - {id: r2, type: vec3}
      - {id: r3, type: vec3}
      
  mat4x4:
    seq:
      - {id: r0, type: vec4}
      - {id: r1, type: vec4}
      - {id: r2, type: vec4}
      - {id: r3, type: vec4}

  float2:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}

  float3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}

  float4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}

  mt_easecurve:
    seq:
    - {id: p1, type: f4}
    - {id: p2, type: f4}