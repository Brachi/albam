meta:
  id: mt_types
  endian: le
  bit-endian: le
  ks-version: "0.11"
  title: MTFramework library of engine types

types:
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
        encoding: utf-8
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