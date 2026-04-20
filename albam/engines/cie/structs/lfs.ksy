meta:
  id: lfs
  file-extension: lfs
  endian: le
  bit-endian: le
  ks-version: "0.11"
  title: RE4UHD archive compressed with xcompression
  
seq:
  - {id: header, type: lfs_header}
  - {id: file_entries, type: file_entry, repeat: expr, repeat-expr: header.num_files}
  
types:
  lfs_header:
    seq:
    - {id: id_magic, contents: [0x52, 0x44, 0x4c, 0x58]}
    - {id: file_id, type: u4} # 0xaabaeefe
    - {id: size_decompressed, type: u4}
    - {id: size_compressed, type: u4}
    - {id: num_files, type: u4}
  file_entry:
    seq:
    - {id: size_compressed, type: u2}
    - {id: size_decompressed, type: u2}
    - {id: offset, type: u4}
    instances:
      raw_data:
        {pos: (offset & ~1) + 20, size: size_compressed}