meta:
  id: dat
  file-extension: dat
  endian: le
  ks-version: "0.11"
  title: Capcom Internal Engine file container
  
seq:
  - {id: header, type: dat_header}

types:
  dat_header:
    seq:
    - {id: num_files, type: u4}
    - {id: padding, type: u4, repeat: expr, repeat-expr: 3}
    - {id: offsets, type: u4, repeat: expr, repeat-expr: num_files}
    - {id: file_extension, type: extension, repeat: expr, repeat-expr: num_files}
    instances:
      file_size:
         value: _io.size
      file_entries:
        type: file_entry(_index) # <= pass `_index` into file_body
        repeat: expr
        repeat-expr: num_files
  
  file_entry:
    params:
      - {id: i, type: s4} # => receive `_index` as `i` here
    instances:
      raw_data:
        pos: _parent.offsets[i]
        size: "i == _parent.num_files - 1 ? 
              (_root.header.file_size - _parent.offsets[i]) :
              (_parent.offsets[i + 1] - _parent.offsets[i])"
  
  extension:
    seq:
      - {id: ext, type: str , size: 4, encoding: UTF-8, terminator: 0}