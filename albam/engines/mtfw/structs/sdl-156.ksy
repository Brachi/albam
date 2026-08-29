    
meta:
  endian: le
  bit-endian: le
  id: sdl_156
  file-extension: sdl
  ks-version: "0.11"
  title: MTFramework scene sheduler format

seq:
  - {id: header, type: base_header}

instances:
  tracks:
    {pos: 0x14, type: track, repeat: expr, repeat-expr: header.num_tracks}

types:
  base_header:
    seq:
      - {id: magic, contents: [0x53, 0x44, 0x4c, 0x00]}
      - {id: version, type: u2}
      - {id: num_tracks, type: u2}
      - {id: frames, type: u4}
      - {id: dti_table_offset, type: u4}
      - {id: name_offset, type: u4}
  
  track:
    seq:
      - {id: type, type: u1}
      - {id: prop_type, type: u1}
      - {id: num_frames, type: u2}
      - {id: parent, type: u4}
      - {id: name_ofs, type: u4}
      - {id: dti_ref, type: u4}
      - {id: timing_ref, type: u4}
      - {id: data_ref, type: u4}
    instances:
      size_:
        value: 24
      name:
        pos: name_ofs + _root.header.name_offset
        type: str
        encoding: UTF-8
        terminator: 0
      data:
        if: data_ref > 0 and type > 5
        pos: data_ref
        type:
          switch-on: prop_type
          cases:
            3: u1 # bool
            4: u1 # u8
            5: u2 # u16
            6: u4 # u32
            7: u8 # u64
            8: s1 # s8
            9: s2 # s16
            10: s4 # s32
            11: s8 # s64
            12: f4 # f32
            13: f8 # f64
            14: mt_str #string
            15: color
            20: vec3
            21: vec4
            22: vec4 #quat
            34: float2
            35: float3
            36: float4
            40: mt_easecurve
            58: resource
        repeat: expr
        repeat-expr: num_frames
      timing_frames:
        pos: timing_ref
        type: timing_frame
        repeat: expr
        repeat-expr: num_frames

  resource:
    seq:
      - {id: ref_ofs, type: u4}
    instances:
      ref_dti:
        pos: ref_ofs + _root.header.name_offset
        type: u4
      ref_path:
        pos: ref_ofs + _root.header.name_offset + 4
        type: str
        encoding: UTF-8
        terminator: 0
       
  timing_frame:
    seq:
      - {id: val, type: s4}
    instances:
      frame:
        value: val & 0xffffff
      type:
        value: val >> 24
        
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: padding, type: f4}
      
  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
      
  color:
    seq:
      - {id: r, type: f4}
      - {id: g, type: f4}
      - {id: b, type: f4}
      - {id: a, type: f4}
  
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