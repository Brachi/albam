meta:
  id: hexane_matb
  endian: le
  title: Hexane Engine Material Format
  file-extension: matb
  license: CC0-1.0
  ks-version: '0.11'

# Modeled against a full-game sweep of a real RE:ORC install
# (24360 successfully-parsed .matb, tests/hexn/test_matb_parsing.py) - see
# that file/its dataset for the verification. `version` varies in the wild
# (1, 3, 6, 7 all seen, all real/unmodified game files, not corruption) and
# only changes how many `extra_flags` words the fixed header carries -
# `header_size` self-describes that, so one seq below covers every version
# instead of a per-version type like mtfw's mod_153/156/21.

seq:
  - {id: id_magic, contents: [0x4d, 0x41, 0x54]}  # "MAT"
  - {id: version, type: u1}  # 1, 3, 6 and 7 all seen on real files
  - {id: ofs_names, type: u4}
  - {id: num_textures, type: u4}
  - id: num_params
    type: u4
    doc: >
      Number of trailing param_entry records right before the name/string
      block at ofs_names (verified exact against ofs_names - ofs_params on
      every sample: 0 mismatches over 24360 real files).
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
      Absolute file offset where the param_entry table starts. Always
      exactly header_size + 8*num_textures (verified on every sample) -
      i.e. right after the texture table - but stored explicitly rather
      than computed, so it's read as-is instead of re-derived.
  - id: extra_flags
    type: u4
    repeat: expr
    repeat-expr: (header_size - 24) / 4
    doc: >
      Per-version material/render flag words not fully decoded yet. Byte-
      level inspection (version 7 only, where there are 4 of these) shows
      they're not one opaque number each: word 0 and word 1 are almost
      always constant across every real file except for one or two
      independent 0/1 bytes inside them (looks like packed boolean render
      flags, e.g. two-sided/cast-shadow-style toggles - which byte means
      what is not identified); word 2 decodes cleanly as a single f4 whose
      real-world values (0.0 most commonly, else round numbers like -10,
      -150, -200, -1500) correlate with decal.msb/skybox*.msb shaders -
      consistent with a depth/polygon-offset bias, though not confirmed
      against known-good in-engine values; word 3 is a near-constant small
      int (11 for ~99.5% of files) that jumps to other small values only
      for skybox/glow_tint/lit_bling_env_glass_dns_skinned shaders -
      consistent with a render-layer/pass selector. Versions 3 and 6 carry
      only the first 3 of these words (no float-bias-shaped one seen there
      in the samples checked); version 1 carries none.
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
          normal/specular/envmap/...) - a hash of some engine-internal
          slot name, not the file's own hash/CRC and not a plain array
          index (confirmed: the same hash value recurs at different
          positions in the texture list across different shaders/files,
          and always correlates with the same texture-path suffix, e.g.
          0xb3acde3f only ever pairs with a "..._d.dds" path). The exact
          hash algorithm/source string is not identified.
      - id: ofs_path
        type: u4
        doc: >
          Absolute file offset of this texture's own null-terminated path
          string inside the shared name block at ofs_names - verified
          byte-exact against the sequential offsets `shader.textures`
          below decodes to, on every sample (0 mismatches over 65715
          texture entries).
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
          Identifies which shader parameter this overrides - same kind of
          opaque hash as texture_entry.usage_hash, not identified further.
          Strongly correlates with shader (a given shader always uses the
          same fixed set of param_hash values across every material that
          uses it).
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
    doc: >
      A shader-parameter override: hash + a 4-float value. Some params use
      only x (a scalar, e.g. glow intensity), others use all 4 as an RGBA
      color (values cluster in 0.0-1.0 with w=1.0 in those cases).
  names_block:
    seq:
      - {id: shader, type: strz, encoding: ASCII}
      - {id: textures, type: strz, encoding: ASCII, repeat: expr, repeat-expr: _parent.num_textures}
