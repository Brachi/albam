meta:
  id: hexane_anims
  endian: be
  title: Hexane Engine Animation Archive format (RE:ORC .anims.ssg)
  file-extension: ssg
  license: CC0-1.0
  ks-version: '0.11'

doc: |
  RE:ORC's `Animation/Projects/*.anims.ssg` bundles many named animation
  clips for one or more skeletons into a single archive. The container is
  structurally the regular Hexane .ssg archive (see ssg.ksy) - same 32-byte
  header, same 32-byte-per-entry file table, same trailing `buffer_chunks`
  blob - but big-endian instead of little-endian, and `id_magic` is 5 or 6
  rather than always 6. Entries pack into `buffer_chunks` back-to-back with
  no padding between them, unlike the little-endian .ssg where each file is
  padded up to `size_padding`. `size_chunks_info`, the zlib chunk-size
  table, is 0 here: chunk decompression is not implemented for this format
  (hexane_ssg.py's SsgFS holds the little-endian precedent to follow if a
  compressed *.anims.ssg turns up).

  An entry's name follows a `<clip_path>--<skeleton_name>` convention;
  splitting on the last `--` gives the skeleton the clip plays on, filed at
  `dlc/pack1/Characters/skel/<skeleton_name>.ssg`. `file_info.file_type` is
  5 for a clip entry, 4 for a skeleton entry in the sibling `skel/*.ssg`
  archives, which share this same big-endian container.

  A clip's own bytes - sliced out of `buffer_chunks` in Python, the way
  hexane_ssg.py's SsgFS does, not in this .ksy - are a little-endian header
  (`anim_clip` below) followed by keyframe data in Sony's PS3 "Edge"
  middleware animation format, `EdgeAnimAnimation` (RE:ORC's .edgemodel
  meshes reuse Sony's Edge model format the same way). Past `size_header`
  the format is a bit-packed, adaptively-interpolated keyframe stream:
  constant channels store one value, animated channels split into
  "framesets" bracketing each frame between two explicit keys found through
  a per-frame bitmask, interpolated between. That is left opaque here
  (`body`) rather than expressed in Kaitai's field model;
  `albam.engines.hexn.animation` decodes it in Python from the same raw
  bytes.

seq:
  - id: id_magic
    type: u4
    doc: 5 or 6; meaning not identified.
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
    doc: Always 0 here - zlib chunk decompression is not implemented for this format. See meta.doc.
  - id: size_padding
    type: u4
    doc: Unused - entries pack with no padding at all. Kept for round-trip. See meta.doc.
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
        contents: [0x34, 0x30, 0x41, 0x45] # ASCII "40AE"
      - id: duration_seconds
        type: f4le
      - id: framerate
        type: f4le
        doc: Always 30.0.
      - id: size_header
        type: u2le
        doc: >
          Byte offset from the clip's own start to where the per-frameset
          keyframe data begins. Derivable from the channel counts below:
          the aligned per-channel-type index arrays, the constant-channel
          data and the per-frameset dma/info tables, each 16-byte aligned.
      - id: num_bones
        type: u2le
        doc: The referenced skeleton's own node count.
      - id: num_frames
        type: u2le
        doc: round(duration_seconds * framerate) + 1.
      - id: num_frame_sets
        type: u2le
      - id: buffer_size
        type: u2le
        doc: Runtime evaluation buffer size in bytes; scales with num_bones, not with clip content.
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
        doc: Always 0 - no array.
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
        doc: Always 0 - unused.
      - id: offset_custom_data
        type: u4le
      - id: size_custom_data
        type: u4le
      - id: reserved_or_align
        size: 8
        doc: >
          Padding up to offset 96, the 16-byte-aligned base everything past
          here is measured from. Kept opaque.
      - id: body
        size-eos: true
        doc: >-
          Channel index arrays, constant-channel data, the per-frameset
          dma/info tables, and the bit-packed per-frameset keyframe
          streams - everything from byte 96 to the clip's own end. Not
          modeled here (see meta.doc); decoded from these raw bytes by
          albam.engines.hexn.animation.
