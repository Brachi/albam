meta:
  id: reengine_tex
  endian: le
  title: RE Engine texture format
  file-extension: tex
  license: CC0-1.0
  ks-version: '0.11'


seq:
  - {id: ident, contents: [0x54, 0x45, 0x58, 0x00]}
  - {id: version, type: u4}
  - {id: width, type: u2}
  - {id: height, type: u2}
  - {id: depth, type: u2} # 3D/volume-texture depth (was "unk_00") - mip level N's depth is max(depth >> N, 1)
  # Real condition (per RE-Mesh-Editor) is "version > 11 and version != 190820018"
  # -> layout B (mipmap_header_2), else layout A (mipmap_header_1) - not a
  # fixed per-version list. Every version albam currently supports still
  # resolves the same way through this expression as the old hardcoded
  # cases did, but this also gets any future version right without needing
  # to guess which literal list it belongs in.
  - id: mipmap_header
    type:
      switch-on: version > 11 and version != 190820018
      cases:
          false: mipmap_header_1
          true: mipmap_header_2
  - {id: format, type: u4, enum: dxgi_format} # real DXGI_FORMAT-compatible enum
  - {id: swizzle_control, type: s4} # console/platform texture-swizzle control; -1 = no swizzle (PC, i.e. every case albam handles)
  - {id: cubemap_marker, type: u4} # cubemap flag/marker
  # Was one u4 "unk_04" - 3 packed sub-fields, still unnamed/unexplained
  # upstream too (RE-Mesh-Editor's own names are literally unkn04/unkn05/null0).
  - {id: unk_04a, type: u1}
  - {id: unk_04b, type: u1}
  - {id: unk_05_null, type: u2}
  # Was one u8 "unk_05" - 5 packed sub-fields: swizzle metadata (unused on
  # PC, same as swizzle_control above) plus two fields upstream names
  # suggest are constant markers ("seven"/"one"), still unexplained.
  # Real gate is "version > 27 and version != 190820018" (independent from
  # the mipmap_header threshold above, not the same condition) - again
  # every currently-supported version still resolves the same way.
  - id: swizzle_height_depth
    type: u1
    if: version > 27 and version != 190820018
  - id: swizzle_width
    type: u1
    if: version > 27 and version != 190820018
  - id: unk_06_null
    type: u2
    if: version > 27 and version != 190820018
  - id: unk_07_seven
    type: u2
    if: version > 27 and version != 190820018
  - id: unk_08_one
    type: u2
    if: version > 27 and version != 190820018
  - id: mipmaps
    type: mipmap_data
    repeat: expr
    repeat-expr: 'version > 11 and version != 190820018 ? mipmap_header.as<mipmap_header_2>.num_mipmaps : mipmap_header.as<mipmap_header_1>.num_mipmaps'
types:
  mipmap_data:
    seq:
      # Was split into two bogus u4s ("ofs_data"/"unk_01") - it's one real
      # u8 offset. Only harmless today because no real file is anywhere
      # near 4GB, so the high 32 bits (what used to be read as "unk_01")
      # are always 0.
      - {id: ofs_data, type: u8}
      - {id: scanline_length, type: u4} # row pitch in bytes (was "unk_02") - used upstream to strip per-row padding when actual data doesn't match the expected mip size
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

enums:
  # The standard Microsoft DXGI_FORMAT enum (stable, published Win32 API -
  # RE Engine's own values are confirmed to match it 1:1 for every format
  # actually seen so far). albam's own decode logic (texture.py) only
  # special-cases a handful of these (BC7/BC1) today; an unmatched value
  # here just falls back to the plain int (see KaitaiStream.resolve_enum),
  # so this doesn't require covering every value to stay safe - it's for
  # documentation/future decode work, not a completeness guarantee.
  dxgi_format:
    0: unknown
    1: r32g32b32a32_typeless
    2: r32g32b32a32_float
    3: r32g32b32a32_uint
    4: r32g32b32a32_sint
    5: r32g32b32_typeless
    6: r32g32b32_float
    7: r32g32b32_uint
    8: r32g32b32_sint
    9: r16g16b16a16_typeless
    10: r16g16b16a16_float
    11: r16g16b16a16_unorm
    12: r16g16b16a16_uint
    13: r16g16b16a16_snorm
    14: r16g16b16a16_sint
    15: r32g32_typeless
    16: r32g32_float
    17: r32g32_uint
    18: r32g32_sint
    19: r32g8x24_typeless
    20: d32_float_s8x24_uint
    21: r32_float_x8x24_typeless
    22: x32_typeless_g8x24_uint
    23: r10g10b10a2_typeless
    24: r10g10b10a2_unorm
    25: r10g10b10a2_uint
    26: r11g11b10_float
    27: r8g8b8a8_typeless
    28: r8g8b8a8_unorm
    29: r8g8b8a8_unorm_srgb
    30: r8g8b8a8_uint
    31: r8g8b8a8_snorm
    32: r8g8b8a8_sint
    33: r16g16_typeless
    34: r16g16_float
    35: r16g16_unorm
    36: r16g16_uint
    37: r16g16_snorm
    38: r16g16_sint
    39: r32_typeless
    40: d32_float
    41: r32_float
    42: r32_uint
    43: r32_sint
    44: r24g8_typeless
    45: d24_unorm_s8_uint
    46: r24_unorm_x8_typeless
    47: x24_typeless_g8_uint
    48: r8g8_typeless
    49: r8g8_unorm
    50: r8g8_uint
    51: r8g8_snorm
    52: r8g8_sint
    53: r16_typeless
    54: r16_float
    55: d16_unorm
    56: r16_unorm
    57: r16_uint
    58: r16_snorm
    59: r16_sint
    60: r8_typeless
    61: r8_unorm
    62: r8_uint
    63: r8_snorm
    64: r8_sint
    65: a8_unorm
    66: r1_unorm
    67: r9g9b9e5_sharedexp
    68: r8g8_b8g8_unorm
    69: g8r8_g8b8_unorm
    70: bc1_typeless
    71: bc1_unorm
    72: bc1_unorm_srgb
    73: bc2_typeless
    74: bc2_unorm
    75: bc2_unorm_srgb
    76: bc3_typeless
    77: bc3_unorm
    78: bc3_unorm_srgb
    79: bc4_typeless
    80: bc4_unorm
    81: bc4_snorm
    82: bc5_typeless
    83: bc5_unorm
    84: bc5_snorm
    85: b5g6r5_unorm
    86: b5g5r5a1_unorm
    87: b8g8r8a8_unorm
    88: b8g8r8x8_unorm
    89: r10g10b10_xr_bias_a2_unorm
    90: b8g8r8a8_typeless
    91: b8g8r8a8_unorm_srgb
    92: b8g8r8x8_typeless
    93: b8g8r8x8_unorm_srgb
    94: bc6h_typeless
    95: bc6h_uf16
    96: bc6h_sf16
    97: bc7_typeless
    98: bc7_unorm
    99: bc7_unorm_srgb

