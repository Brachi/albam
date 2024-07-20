meta:
  endian: le
  file-extension: rtex
  id: rtex_157
  ks-version: 0.11
  title: MTFramework texture render target format version 157

seq:
  - {id: id_magic, contents: [0x52, 0x54, 0x58, 0x00]}
  - {id: packed_data_1, type: u4}
  - {id: packed_data_2, type: u4}
  - {id: packed_data_3, type: u4}

instances:
  size_before_data_:
    value: 16
  unk_type:
    value: packed_data_1 & 0xffff
  reserved_01:
    value: (packed_data_1  >> 16) & 0x00ff
  shift:
    value: (packed_data_1 >> 24) & 0x000f
  dimension:
    value: (packed_data_1 >> 28) & 0x000f

  num_mipmaps_per_image:
    value: packed_data_2 & 0x3f
  width:
    value: (packed_data_2 >> 6) & 0x1fff
  height:
    value: (packed_data_2 >> 19) & 0x1fff

  num_images:
    value: (packed_data_3) & 0xff
  compression_format:
    value: (packed_data_3 >> 8) & 0xff
  constant:
    value: (packed_data_3 >> 16) & 0x1fff
  reserved_02:
    value: (packed_data_3 >> 29) & 0x003
