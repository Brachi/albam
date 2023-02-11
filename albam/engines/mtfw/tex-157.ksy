meta:
  endian: le
  file-extension: tex
  id: tex_157
  ks-version: 0.10
  title: MTFramework texture format version 157

seq:
  - {id: id_magic, contents: [0x54, 0x45, 0x58, 0x00]}
  - {id: packed_data_1, type: u4}
  - {id: packed_data_2, type: u4}
  - {id: num_images, type: u1}
  - {id: compression_format, type: u1}
  - {id: unk_01, type: u1}
  - {id: unk_02, type: u1}
  - {id: mipmap_offsets, type: u4, repeat: expr, repeat-expr: num_mipmaps_per_image * num_images}
  - {id: dds_data, size-eos: true}

instances:
  num_mipmaps_per_image:
    value: packed_data_2 & 0x3f
  width:
    value: (packed_data_2 >> 6) & 0x1fff
  height:
    value: (packed_data_2 >> 19) & 0x1fff


