meta:
  id: xfs
  endian: le
  bit-endian: le
  ks-version: "0.11"
  title: MTFramework binary xml configuration file
  imports:
    - mt_types
seq:
  - {id: header, type: xfs_header}
  
instances:
  objects:
    type: obj(_index)
    repeat: expr
    repeat-expr: header.object_num
  data_buffer:
    pos: header.data_size + 0x10
    #size: _io.size - header.data_size - 0x10
    size-eos: true
    
types:
  xfs_header:
    seq:
    - {id: magic, contents: [0x58, 0x46, 0x53, 0x00]}
    - {id: major_ver, type: u2}
    - {id: minor_ver, type: u2}
    - {id: object_num, type: u4}
    - {id: data_size, type: u4}
    - {id: obj_pos, type: u4, repeat: expr, repeat-expr: object_num}
    
  obj:
    params:
      - {id: i, type: u4}
    instances:
      data:
        pos: _root.header.obj_pos[i] + 0x10
        type: object_data
    
  object_data:
    seq:
    - {id: dti, type: u4}
    - {id: prop_num, type: b15}
    - {id: init, type: b1}
    - {id: reserved, type: u2}
    - {id: prop, type: mt_property, repeat: expr, repeat-expr: prop_num}
    
    
  mt_property:
    seq:
    - {id: name_ofs, type: u4}
    - {id: type, type: u1}
    - {id: attr, type: u1}
    - {id: bytes, type: b15}
    - {id: disable, type: b1}
    - {id: getter, type: u4}
    - {id: getcount, type: u4}
    - {id: setter, type: u4}
    - {id: setcount, type: u4}
    instances:
      name:
        pos: name_ofs + 0x10
        type: str
        encoding: utf-8
        terminator: 0
      parent_index:
        value: _parent._parent.i