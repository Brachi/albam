meta:
  endian: le
  file-extension: rtex
  id: rtex_112
  ks-version: 0.11
  title: MTFramework texture format version 112

seq:
  - {id: id_magic, contents: [0x52, 0x54, 0x58, 0x00]}
  - {id: version, type: u2}
  - {id: revision, type: u2}
  - {id: num_mipmaps_per_image, type: u1}
  - {id: num_images, type: u1}
  - {id: unk_02, type: u1}
  - {id: unk_03, type: u1}
  - {id: width, type: u2}
  - {id: height, type: u2}
  - {id: reserved, type: u4}
  - {id: compression_format, type: str, encoding: ASCII, size: 4}
  - {id: red, type: f4}
  - {id: green, type: f4}
  - {id: blue, type: f4}
  - {id: alpha, type: f4}

instances:
  size_before_data_:
    value: 40
