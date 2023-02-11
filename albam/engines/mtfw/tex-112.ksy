meta:
  endian: le
  file-extension: tex
  id: tex_112
  ks-version: 0.10
  title: MTFramework texture format version 112

seq:
  - {id: id_magic, contents: [0x54, 0x45, 0x58, 0x00]}
  - {id: version, type: u2}
  - {id: revision, type: u2}
  - {id: num_mipmaps_per_image, type: u1}
  - {id: num_images, type: u1}
  - {id: unk_02, type: u1}
  - {id: unk_03, type: u1}
  - {id: width, type: u2}
  - {id: height, type: u2}
  - {id: reserved, type: u4}
  - {id: compression_format, type: str, encoding: ascii, size: 4}
  - {id: red, type: f4}
  - {id: green, type: f4}
  - {id: blue, type: f4}
  - {id: alpha, type: f4}
  - {id: unk_offset, type: u4, repeat: expr, repeat-expr: + 27, if: num_images > 1}
  - {id: offsets_mipmaps, type: u4, repeat: expr, repeat-expr: num_mipmaps_per_image * num_images}
  - {id: dds_data, size-eos: true}
