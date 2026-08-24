meta:
  id: hexane_anims
  endian: be
  title: Hexane Engine Animation Archive format (RE:ORC .anims.ssg)
  file-extension: ssg
  license: CC0-1.0
  ks-version: '0.11'

doc: |
  RE:ORC's `Animation/Projects/*.anims.ssg` bundles many named animation
  clips for one or more skeletons into a single archive. The outer
  container is structurally identical to the regular Hexane .ssg archive
  (see ssg.ksy) - same 32-byte header, same 32-byte-per-entry file table,
  same trailing `buffer_chunks` blob - except every multi-byte integer is
  stored big-endian here instead of little-endian, and `id_magic` is 5 or
  6 rather than always 6 (both observed on real files; meaning not
  confirmed - possibly "uncompressed"/short archives get 5). Verified
  against the committed test dataset: every entry packs into
  `buffer_chunks` back-to-back with *no* padding between entries (unlike
  the regular, little-endian .ssg where each file is padded up to
  `size_padding`) - `size_padding` itself is present here too but never
  matches a real per-entry gap on any file checked, so it's kept only for
  round-trip fidelity, not used to compute entry offsets. `size_chunks_info`
  (the zlib chunk-size table) is always 0 on every real archive checked
  except a handful of leftover dev/test archives, which hold a garbage
  value far larger than the whole file and have a different, unrelated
  internal layout (confirmed by their file_info's own `reserved_01` field
  being 1 instead of 0, unlike every real archive) and fail to parse here;
  zlib chunk decompression itself is not implemented in this format for
  that reason - see hexane_ssg.py's own SsgFS for the (little-endian)
  precedent this would follow if a real compressed *.anims.ssg ever turns
  up.

  Each entry's own name follows an `<clip_path>--<skeleton_name>` naming
  convention - splitting on the last `--` recovers the skeleton this clip
  is meant to be played on, matching real files under
  `dlc/pack1/Characters/skel/<skeleton_name>.ssg` (weapon rigs use their
  own distinct skeleton names too, separate from humanoid/creature ones).
  `file_info.file_type` is always 5 for a clip entry here
  (vs. 4 for a skeleton entry in the sibling `skel/*.ssg` archives, which
  share this exact same big-endian container).

  A clip's own raw bytes (sliced out of `buffer_chunks` the same way
  hexane_ssg.py's SsgFS does, in Python, not in this .ksy) are themselves
  a small, little-endian header (`anim_clip` below) followed by the actual
  keyframe data. That inner format is Sony's PS3 "Edge" middleware
  animation format (`EdgeAnimAnimation`) - RE:ORC's own tooling reused it
  wholesale (`dlc/pack1/Characters/*.edgemodel` reusing Sony's "Edge"
  model format the same way is already established in edgemodel.ksy).
  `anim_clip`'s header fields (through `size_custom_data`, 88 bytes) are
  modeled field-for-field against a community Blender import script that
  documents `EdgeAnimAnimation`'s C struct layout - cross-checked here,
  not taken on faith: independently re-deriving `size_header` from the
  channel-count fields (aligned per-channel-type index arrays + const-
  channel data + the per-frameset dma/info tables, all 16-byte-aligned
  per the reference) reproduces the real stored `size_header` value
  exactly across the whole verified dataset (every clip entry except the
  handful of dev/test archives above) - 100% match, not a single byte
  off. Past `size_header`,
  the format is a bit-packed, adaptively-interpolated keyframe stream
  (constant channels store one value; animated channels are split into
  "framesets" that bracket each frame between two explicit keys located
  via a per-frame bitmask search, then slerp/lerp between them) - left
  entirely opaque here (`body`) since expressing that in Kaitai's own
  field model isn't practical; `albam.engines.hexn.animation` decodes it
  directly against these same raw bytes in Python instead, porting the
  reference script's algorithm (itself re-verified against real bytes,
  not trusted blindly).

seq:
  - id: id_magic
    type: u4
    doc: Observed values are 5 or 6 on every real archive checked; meaning not confirmed.
  - id: reserved_01
    type: u4
  - id: size_files_info
    type: u4
  - id: size_file_names
    type: u4
  - id: size_chunks_buffer
    type: u4
  - id: reserved_02
    type: u4
  - id: size_chunks_info
    type: u4
    doc: Always 0 on every real shipped archive found - see meta.doc. Zlib chunk decompression is not implemented here.
  - id: size_padding
    type: u4
    doc: Present for round-trip fidelity only - never matches a real per-entry gap (entries pack with no padding at all). See meta.doc.
  - id: files_info
    type: file_info
    repeat: expr
    repeat-expr: size_files_info / 32
  - id: chunk_sizes
    type: u4
    repeat: expr
    repeat-expr: size_chunks_info / 4
  - id: file_names
    size: size_file_names

instances:
  buffer_chunks:
    pos: 32 + size_files_info + size_chunks_info + size_file_names
    size: size_chunks_buffer

types:
  file_info:
    seq:
      - {id: ident, type: u4}
      - {id: name_offset_rel, type: u4}
      - {id: size, type: u4}
      - {id: reserved_01, type: u4}
      - {id: reserved_02, type: u4}
      - {id: file_type, type: s4}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u4}
    instances: # convenience, although it's already read
      name:
        {type: str, terminator: 0, encoding: ASCII, pos: 32 + _parent.size_files_info + _parent.size_chunks_info + name_offset_rel}

  # A clip's own bytes (sliced out of buffer_chunks in Python - see
  # albam.engines.hexn.animation). Parsed standalone via
  # AnimClip.from_bytes(clip_bytes), so field-level endian overrides
  # (everything here is little-endian, unlike the outer container) are
  # used instead of a per-type meta.endian override.
  anim_clip:
    seq:
      - id: id_magic
        contents: [0x34, 0x30, 0x41, 0x45] # ASCII "40AE" - confirmed on every real clip entry checked (a community reference also allows "EA04", not observed here)
      - id: duration_seconds
        type: f4le
      - id: framerate
        type: f4le
        doc: 30.0 on every real clip checked.
      - id: size_header
        type: u2le
        doc: Byte offset from this clip's own start to where the per-frameset keyframe data begins - confirmed exactly reproducible from the fields below (see meta.doc).
      - id: num_bones
        type: u2le
        doc: Matches the referenced skeleton's total bone/node count (constant across every clip of the same character in every sample checked).
      - id: num_frames
        type: u2le
        doc: round(duration_seconds * framerate) + 1 on every real clip checked.
      - id: num_frame_sets
        type: u2le
      - id: buffer_size
        type: u2le
        doc: Required runtime evaluation buffer size in bytes - constant across every clip of the same character (scales with num_bones, not per-clip content).
      - id: num_const_r_channels
        type: u2le
      - id: num_const_t_channels
        type: u2le
      - id: num_const_s_channels
        type: u2le
      - id: num_const_user_channels
        type: u2le
      - id: num_anim_r_channels
        type: u2le
      - id: num_anim_t_channels
        type: u2le
      - id: num_anim_s_channels
        type: u2le
      - id: num_anim_user_channels
        type: u2le
      - id: flags
        type: u2le
      - id: size_joints_weight_array
        type: u4le
        doc: 0 (no array) on every real clip checked.
      - id: user_joints_weight_array
        type: u4le
      - id: offset_joints_weight_array
        type: u4le
      - id: offset_frame_set_dma_array
        type: u4le
      - id: offset_frame_set_info_array
        type: u4le
      - id: offset_const_r_data
        type: u4le
      - id: offset_const_t_data
        type: u4le
      - id: offset_const_s_data
        type: u4le
      - id: offset_const_user_data
        type: u4le
      - id: offset_packing_specs
        type: u4le
        doc: 0 (unused) on every real clip checked.
      - id: offset_custom_data
        type: u4le
      - id: size_custom_data
        type: u4le
      - id: reserved_or_align
        size: 8
        doc: Unread by the community reference this was cross-checked against ("we didn't read 2 x uint32_t") - likely just padding up to the 16-byte-aligned offset (96) everything past here is measured from. Kept opaque.
      - id: body
        size-eos: true
        doc: >-
          Channel index arrays, constant-channel data, the per-frameset
          dma/info tables, and the bit-packed per-frameset keyframe
          streams - everything from byte 96 to this clip's own end. Not
          modeled here (see meta.doc); decoded directly against these raw
          bytes by albam.engines.hexn.animation, not through this type.
