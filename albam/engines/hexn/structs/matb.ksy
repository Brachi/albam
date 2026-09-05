meta:
  id: hexane_matb
  endian: le
  title: Hexane Engine Material Format
  file-extension: matb
  license: CC0-1.0
  ks-version: '0.11'

# `version` varies in the wild - 1, 3, 5, 6 and 7 are all real - and only
# changes how many `extra_flags` words the fixed header carries. Since
# `header_size` self-describes that, one seq below covers every version,
# rather than a per-version type like mtfw's mod_153/156/21.

seq:
  - {id: id_magic, contents: [0x4d, 0x41, 0x54]}  # "MAT"
  - id: version
    type: u1
    valid:
      any-of: [1, 3, 5, 6, 7]
  - {id: ofs_names, type: u4}
  - {id: num_textures, type: u4}
  - id: num_params
    type: u4
    doc: >
      Number of trailing param_entry records, right before the name/string
      block at ofs_names.
  - id: header_size
    type: u4
    doc: >
      Size in bytes of this fixed header (id_magic..extra_flags), i.e. the
      offset the texture table starts at. Self-describing: this is what
      lets a single .ksy cover every version - 24 for version 1 (no
      extra_flags), 36 for versions 3/6 (3 extra_flags words), 40 for
      version 7 (4 extra_flags words).
  - id: ofs_params
    type: u4
    doc: >
      Absolute file offset where the param_entry table starts, i.e.
      header_size + 8*num_textures, right after the texture table. Stored
      explicitly, so it's read as-is rather than re-derived.
  - id: extra_flags
    type: u4
    repeat: expr
    repeat-expr: (header_size - 24) / 4
    doc: >
      Material/render flag words, partly decoded, and not one opaque
      number each. In version 7, which has four of them: words 0 and 1 are
      near-constant apart from one or two independent 0/1 bytes inside
      them, in the shape of packed boolean render flags (which byte is
      which is not identified); word 2 is an f4, 0.0 or a round negative
      number on decal/skybox shaders, in the shape of a depth bias; word 3
      is a small int, 11 except on skybox/glow/glass shaders, in the shape
      of a render-layer selector. Versions 3 and 6 carry the first three
      words, version 1 none.
instances:
  textures_table:
    pos: header_size
    type: texture_entry
    repeat: expr
    repeat-expr: num_textures
    doc: >
      One entry per texture, immediately after the fixed header. Not the
      same data as `shader.textures` below (that's the plain path
      strings) - this is the shader-binding metadata for each one.
  params_table:
    pos: ofs_params
    type: param_entry
    repeat: expr
    repeat-expr: num_params
  shader:
    pos: ofs_names
    type: names_block
types:
  texture_entry:
    seq:
      - id: usage_hash
        type: u4
        doc: >
          Identifies which shader texture slot this binds to (diffuse/
          normal/specular/envmap/...): a hash of an engine-internal slot
          name, not the file's own hash and not an array index - the same
          value recurs at different positions in the texture list across
          shaders, always paired with the same texture-path suffix (e.g.
          0xb3acde3f with a "..._d.dds" path). The hash algorithm and its
          source string are not identified.
      - id: ofs_path
        type: u4
        doc: >
          Absolute file offset of this texture's own null-terminated path
          string inside the shared name block at ofs_names, matching what
          `shader.textures` below decodes sequentially.
    instances:
      path:
        pos: ofs_path
        type: strz
        encoding: ASCII
  param_entry:
    seq:
      - id: param_hash
        type: u4
        doc: >
          Identifies which shader parameter this overrides: the same kind
          of opaque hash as texture_entry.usage_hash, not identified
          further. A given shader always uses the same fixed set of
          param_hash values.
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
    doc: >
      A shader-parameter override: hash plus a 4-float value. Some params
      use only x, as a scalar (glow intensity and the like); others use all
      four as an RGBA color, in 0.0-1.0 with w=1.0.
  names_block:
    seq:
      - {id: shader, type: strz, encoding: ASCII}
      - {id: textures, type: strz, encoding: ASCII, repeat: expr, repeat-expr: _parent.num_textures}
