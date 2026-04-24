meta:
  id: pack
  file-extension: pack
  endian: le
  ks-version: "0.11"
  title: Capcom Internal Engine texture bank

seq:
  - {id: pack_name, type: u4}
  - {id: num_files, type: u4}
  - {id: file_entries, type: file_entry, repeat: expr, repeat-expr: num_files}
  
types:
  file_entry:
    seq:
      - {id: offset, type: u4}
    instances:
      data:
        pos: offset
        type: file_body
        
    
  file_body:
    seq:
      - {id: size, type: u4}
      - {id: unk_00, type: u4}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: is_dds, type: u4}
      - {id: raw_data, size: size}