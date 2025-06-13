meta:
  endian: le
  bit-endian: le
  file-extension: tex
  id: tex_112
  ks-version: 0.10
  title: MTFramework texture format version 112

seq:
  - {id: id_magic, contents: [0x54, 0x45, 0x58, 0x00]}
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
  - {id: cube_faces, type: cube_face, repeat: expr, repeat-expr: 3, if: num_images == 6}
  - {id: mipmap_offsets, type: u4, repeat: expr, repeat-expr: num_mipmaps_per_image * num_images}
  - {id: dds_data, size-eos: true}

instances:
  size_before_data_:
    value: "num_images == 1 ? 40 + (4 * num_mipmaps_per_image * num_images) : 40 + (4 * num_mipmaps_per_image * num_images) + 108"

types:
  cube_face:
    seq:
      - {id: field_00, type: f4}
      - {id: negative_co, type: f4, repeat: expr, repeat-expr: 3}
      - {id: positive_co, type: f4, repeat: expr, repeat-expr: 3}
      - {id: uv, type: f4, repeat: expr, repeat-expr: 2}
    instances:
      size_:
        value: 36
