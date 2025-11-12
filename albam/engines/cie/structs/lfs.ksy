meta:
  id: lfs
  file-extension: lfs
  bit-endian: le
  endian: le
  
  
seq:
   - {id: lfs_header, type: header}
   - {id: data_chunks, type: data_chunk, repeat: expr, repeat-expr: lfs_header.num_chunks }
  

types:
  header:
    seq:
    - {id: id_magic, contents: [0x52, 0x44, 0x4c, 0x58]}
    - {id: id_magic_2, type: u4}
    - {id: size_decompressed, type: u4}
    - {id: size_compressed, type: u4}
    - {id: num_chunks, type: u4}
    instances:
      size:
        value: 20
      
  data_chunk:
    seq:
      - {id: size_compressed, type: u2}
      - {id: size_decompressed, type: u2}
      - {id: offset, type: u4}
    instances:
      comp_offset:
         value: offset & ~1 # one bit "is compressed?" flag
      chunk:
        pos: comp_offset + _root.lfs_header.size
        size: size_compressed