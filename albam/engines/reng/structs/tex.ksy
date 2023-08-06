meta:
  id: reengine_tex
  endian: le
  title: RE Engine texture format
  file-extension: tex
  license: CC0-1.0
  ks-version: 0.8


seq:
  - {id: ident, contents: [0x54, 0x45, 0x58, 0x00]}
  - {id: version, type: u4}
  - {id: width, type: u2}
  - {id: height, type: u2}
  - {id: unk_00, type: u2}
  - id: mipmap_header
    type:
      switch-on: version
      cases:
          10: mipmap_header_1
          190820018: mipmap_header_1
          30: mipmap_header_2
          34: mipmap_header_2
  - {id: format, type: u4}
  - {id: unk_02, type: u4}
  - {id: unk_03, type: u4}
  - {id: unk_04, type: u4}
  - {id: unk_05, type: u8, if: version == 30 or version == 34}
  - {id: mipmaps, type: mipmap_data, repeat: expr, repeat-expr: 'version == 10 or version == 190820018 ? mipmap_header.as<mipmap_header_1>.num_mipmaps : mipmap_header.as<mipmap_header_2>.num_mipmaps' }
types:
  mipmap_data:
    seq:
      - {id: ofs_data, type: u4}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u4}
      - {id: size_data, type: u4}
    instances:
      dds_data:
        {pos: ofs_data, size: size_data}
  mipmap_header_1:
    seq:
      - {id: num_mipmaps, type: u1}
      - {id: num_images, type: u1}
  mipmap_header_2:
    seq:
      - {id: num_images, type: u1}
      - {id: size_mipmap_header, type: u1}
    instances:
      num_mipmaps:
        value: size_mipmap_header / 16

