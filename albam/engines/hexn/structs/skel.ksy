meta:
  id: hexane_skel
  endian: le
  title: Hexane Engine Skeleton Format (RE:ORC dlc/pack1/Characters/skel/*.ssg)
  license: CC0-1.0
  ks-version: '0.11'

# A character's skeleton lives apart from its mesh:
# dlc/pack1/Characters/skel/<name>.ssg, stem-matching the
# dlc/pack1/characters/<name>/models/<name>.edgemodel it rigs.
#
# Despite the extension, this is not the chunk-compressed container modeled
# in ssg.ksy - it's a single payload starting at byte 0, parsed straight
# from the raw bytes (see skeleton.py).
#
# The outer header (0x00-0xBF) is big-endian; the body, from the "20SE" tag
# at 0xC0 on, is little-endian.
#
# The u4 fields from 0xD8 on are self-relative offsets: the field's own
# absolute position plus its stored value gives the position it points to.

seq:
  - {id: magic, contents: [0x00, 0x00, 0x00, 0x06]}
  - {id: reserved_01, type: u4be}
  - id: header_size
    type: u4be
    doc: Constant 32.
  - id: name_field_size
    type: u4be
    doc: Constant 128 - own_path's fixed field size below.
  - id: body_size
    type: u4be
    doc: >
      filesize - 0xC0, including the zero padding after the body content
      ends (see `total` and trailing_padding). File sizes satisfy
      filesize % 128 == 64.
  - {id: reserved_02, type: u4be}
  - {id: reserved_03, type: u4be}
  - id: reserved_04
    type: u4be
    doc: Constant 0x00800000.
  - id: checksum_1
    type: u4be
    doc: Per-file value, paired with checksum_2. Not needed for import.
  - {id: reserved_05, type: u4be}
  - id: inner_body_size
    type: u4be
    doc: Big-endian duplicate of the body's own `total` (0xC4).
  - id: reserved_06
    type: u4be
    doc: Constant 1.
  - {id: reserved_07, type: u4be}
  - id: reserved_08
    type: u4be
    doc: Constant 4.
  - id: checksum_2
    type: u4be
    doc: See checksum_1.
  - {id: reserved_09, type: u4be}
  - id: own_path
    size: 128
    type: strz
    encoding: ASCII
    doc: >
      The file's own virtual path, "dlc/pack1/characters/skel/<name>"
      (lowercase, unlike the directory it's filed under on disk),
      null-padded to the fixed 128-byte field.
  - {id: tag, contents: "20SE"}
  - id: total
    type: u4
    doc: >
      Body content size from `tag` (0xC0) to the end of the real content,
      before the padding to the file's alignment boundary: body_end below
      is 0xC0 + total.
  - id: c8_unk
    type: u4
    doc: >
      Purpose not identified; captured for round-trip. Nothing below is
      located through it - every section comes from node_count,
      hierarchy_size and the self-relative offsets.
  - id: hierarchy_size
    type: u4
    doc: >
      Byte size of both `hierarchy` and `hash_array`:
      round_up(node_count * 4, 16).
  - id: node_count
    type: u4
    doc: >
      Entry count for `hierarchy`, `local_transforms`, `parents`,
      `name_offsets` and `names` alike, and the space the rigged
      .edgemodel's own vertex weight bone indices range over (its
      edge_header.num_bones matches this, not second_count).
  - id: second_count
    type: u4
    doc: >
      A smaller count, roughly a quarter to a third of node_count. Not the
      deforming-bone count - vertex weights index the full node_count range
      (see node_count). Purpose not identified; captured for round-trip.
  - id: d8_ofs_local_transforms
    type: u4
    doc: Self-relative offset to `local_transforms`.
  - id: dc_ofs_parents
    type: u4
    doc: Self-relative offset to the end of `local_transforms` / start of `parents`.
  - id: e0_ofs_hash_array
    type: u4
    doc: Self-relative offset to `hash_array`.
  - id: e4_ofs_body_end_a
    type: u4
    doc: Self-relative offset to body_end, redundant with `total`/e8_ofs_body_end_b.
  - id: e8_ofs_body_end_b
    type: u4
    doc: Self-relative offset to body_end - see e4_ofs_body_end_a.
  - id: ec_ofs_u16_array_end
    type: u4
    doc: >
      Self-relative offset to the unpadded end of `parents`, i.e.
      dc_ofs_parents's target plus node_count * 2 bytes.
  - id: f0_ofs_name_offsets
    type: u4
    doc: >
      Self-relative offset to `name_offsets`, i.e. ec_ofs_u16_array_end's
      target rounded up to the next 16-byte boundary.
  - {id: reserved_10, type: u4}
  - {id: reserved_11, type: u4}
  - {id: reserved_12, type: u4}
  - id: hierarchy
    type: hierarchy_entry
    repeat: expr
    repeat-expr: node_count
    doc: node_count entries of 4 bytes, at a fixed 0x100.

instances:
  hierarchy_end:
    value: 0x100 + hierarchy_size
  hierarchy_padding:
    pos: 0x100 + (node_count * 4)
    size: hierarchy_size - (node_count * 4)
    if: hierarchy_size > node_count * 4
    doc: >
      The gap between the node_count real entries and hierarchy_end. Not
      alignment padding - it holds the same 4-bytes-per-entry shape as
      `hierarchy` itself, just beyond node_count. Purpose not identified;
      captured opaquely, and as its own field so that it round-trips (a
      `seq` array only writes back its repeat-expr entries).
  local_transforms_start:
    value: 0xD8 + d8_ofs_local_transforms
  pre_transforms_data:
    pos: hierarchy_end
    size: local_transforms_start - hierarchy_end
    if: local_transforms_start > hierarchy_end
    doc: >
      Per-file data between `hierarchy` and `local_transforms`, 0 to 224
      bytes, continuing `hierarchy`'s u16-pair shape rather than padding it
      out. Purpose not identified; captured opaquely.
  local_transforms:
    pos: local_transforms_start
    type: local_trs
    repeat: expr
    repeat-expr: node_count
    doc: >
      Per-node bind-pose transform, relative to the node's parent in
      `parents`. node_count entries of 48 bytes, Y-up (skeleton.py converts
      to Blender's Z-up on import).
  local_transforms_end:
    value: local_transforms_start + node_count * 48
  name_offsets_start:
    value: 0xF0 + f0_ofs_name_offsets
  parents:
    pos: local_transforms_end
    type: u2
    repeat: expr
    repeat-expr: node_count
    doc: >
      The parent table: one entry per node, in the same order as
      `hierarchy`/`local_transforms`/`names`, holding that node's parent
      index in those arrays. 0xffff marks a root - node 0 is the only root
      on a character skeleton. Every other entry is less than its own node
      index, so world transforms compose in a single forward pass.
  parents_end:
    value: local_transforms_end + node_count * 2
  parents_padding:
    pos: parents_end
    size: name_offsets_start - parents_end
    if: name_offsets_start > parents_end
    doc: >
      Zero padding from the end of `parents` to name_offsets_start, i.e. up
      to round_up(node_count * 2, 16). Its own field so that it round-trips
      - see hierarchy_padding.
  name_offsets:
    pos: name_offsets_start
    type: u4
    repeat: expr
    repeat-expr: node_count
    doc: >
      Each node's name offset within `names`. Cumulative (offsets[i] is the
      total length, terminators included, of every earlier name), so
      `names` below reads sequentially instead of through this table; it is
      still modeled as real data for round-trip.
  names_start:
    value: name_offsets_start + node_count * 4
  names:
    pos: names_start
    type: strz
    encoding: ASCII
    repeat: expr
    repeat-expr: node_count
    doc: >
      node_count null-terminated ASCII bone names, one per `hierarchy`/
      `local_transforms` entry in the same order.
  hash_array_start:
    value: 0xE0 + e0_ofs_hash_array
  hash_array:
    pos: hash_array_start
    size: hierarchy_size
    doc: >
      One u4 per node, starting at the end of `names` rounded up to the next
      16-byte absolute boundary and running exactly to body_end. Not fnv1,
      fnv1a, djb2 or crc32 of the bone name; a per-node hash or id of some
      other kind. Captured opaquely.
  body_end:
    value: 0xC0 + total
  trailing_padding:
    pos: body_end
    size: _io.size - body_end
    if: _io.size > body_end
    doc: Zero padding out to the file's size - see body_size.

types:
  hierarchy_entry:
    seq:
      - id: unk_a
        type: u2
        doc: >
          Node-index-like value, loosely increasing across the array but
          not a running index; the last entry reaches node_count - 1.
          Purpose not identified.
      - id: unk_b
        type: u2
        doc: >
          Node-index-like value in the same space as unk_a, 0xffff on the
          array's first few entries, top bit (0x8000) set on a minority of
          the rest. Not the parent table - see `parents`. Purpose not
          identified.

  local_trs:
    seq:
      - id: rotation
        type: vec4f
        doc: Rotation quaternion (x, y, z, w).
      - id: position
        type: vec4f
        doc: Position (x, y, z); w is a homogeneous coordinate, always 1.0.
      - id: scale
        type: vec4f
        doc: >
          Scale (x, y, z), usually but not always (1, 1, 1); w is a
          homogeneous coordinate, always 1.0.

  vec4f:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
