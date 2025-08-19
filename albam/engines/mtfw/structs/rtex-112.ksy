meta:
  endian: le
  bit-endian: le
  file-extension: rtex
  id: rtex_112
  ks-version: 0.10
  title: MTFramework texture format version 112

seq:
  - {id: id_magic, contents: [0x52, 0x54, 0x58, 0x00]}
  - {id: version, type: u2}
  - {id: texture_type, type: b4}
  - {id: encoded_type, type: b4}
  - {id: depend_screen, type: b1}
  - {id: render_target, type: b1}
  - {id: attr, type: b6}
  - {id: num_mipmaps_per_image, type: u1}
  - {id: num_images, type: u1}
  - {id: padding, type: u2}
  - {id: width, type: u2}
  - {id: height, type: u2}
  - {id: depth, type: u4}
  - {id: compression_format, type: str, encoding: ASCII, size: 4}
  - {id: red, type: f4}
  - {id: green, type: f4}
  - {id: blue, type: f4}
  - {id: alpha, type: f4}

instances:
  size_before_data_:
    value: 40
