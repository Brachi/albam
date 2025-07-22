meta:
  endian: le
  bit-endian: le
  file-extension: tex
  id: tex_157
  ks-version: 0.10
  title: MTFramework texture format version 157

seq:
  - {id: id_magic, contents: [0x54, 0x45, 0x58, 0x00]}
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
  - {id: cube_faces, type: cube_face, repeat: expr, repeat-expr: 3, if: num_images == 6}
  - {id: mipmap_offsets, type: u4, repeat: expr, repeat-expr: num_mipmaps_per_image * num_images}
  - {id: dds_data, size-eos: true}

instances:
  size_before_data_:
    value: "num_images == 1 ? 16 + (4 * num_mipmaps_per_image * num_images) : 16 + (4 * num_mipmaps_per_image * num_images)  + 36 * 3"
  #unk_type:
  #  value: packed_data_1 & 0xffff
  #reserved_01:
  #  value: (packed_data_1  >> 16) & 0x00ff
  #shift:
  #  value: (packed_data_1 >> 24) & 0x000f
  #dimension:
  #  value: (packed_data_1 >> 28) & 0x000f

  #num_mipmaps_per_image:
  #  value: packed_data_2 & 0x3f
  #width:
  #  value: (packed_data_2 >> 6) & 0x1fff
  #height:
  #  value: (packed_data_2 >> 19) & 0x1fff

  #num_images:
  #  value: (packed_data_3) & 0xff
  #compression_format:
  #  value: (packed_data_3 >> 8) & 0xff
  #constant:
  #  value: (packed_data_3 >> 16) & 0x1fff
  #reserved_02:
  #  value: (packed_data_3 >> 29) & 0x003

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
