meta:
  endian: le
  bit-endian: le
  file-extension: rtex
  id: rtex_157
  ks-version: 0.10
  title: MTFramework texture render target format version 157

seq:
  - {id: id_magic, contents: [0x52, 0x54, 0x58, 0x00]}
  - {id: version, type: b8}
  - {id: unk, type: b8}
  - {id: attr, type: b8}
  - {id: prebias, type: b4}
  - {id: type, type: b4}
  - {id: num_mipmaps_per_image, type: b6}
  - {id: width, type: b13}
  - {id: height, type: b13}
  - {id: num_images, type: b8}
  - {id: compression_format, type: b8}
  - {id: depth, type: b13}
  - {id: auto_resize, type: b1}
  - {id: render_target, type: b1}
  - {id: use_vtf, type: b1}

instances:
  size_before_data_:
    value: 16