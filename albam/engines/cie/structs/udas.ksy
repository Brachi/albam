meta:
  id: udas
  file-extension: udas
  endian: le
  ks-version: "0.11"
  title: Capcom Internal Engine file container 

seq:
 - {id: header, type: udas_header}
  
types:
  udas_header:
    seq:
    - {id: id_magic, type: u4, repeat: expr, repeat-expr: 8}
    - {id: unk_00, type: u4}
    - {id: file_size, type: u4}
    - {id: unk_01, type: u4}
    - {id: data_offset, type: u4}
    instances:
     data_bloc:
      {pos: data_offset, type: udas_data}
  
  udas_data:
    seq:
    - {id: num_files, type: u4}
    - {id: padding, type: u4, repeat: expr, repeat-expr: 3}
    - {id: offsets, type: u4, repeat: expr, repeat-expr: num_files}
    - {id: file_extension, type: extension, repeat: expr, repeat-expr: num_files}
    instances:
     file_entries:
      type: file_entry(_index) # <= pass `_index` into file_body
      repeat: expr
      repeat-expr: num_files

  file_entry:
    params:
      - id: i               # => receive `_index` as `i` here
        type: s4
    instances:
      raw_data:
        pos: _parent.offsets[i] + _root.header.data_offset
        size: "i == _parent.num_files - 1 ? 
              (_root.header.file_size - _parent.offsets[i]) :
              (_parent.offsets[i + 1] - _parent.offsets[i])"
        
  extension:
    seq:
      - {id: ext, type: str ,terminator: 0, encoding: UTF-8}