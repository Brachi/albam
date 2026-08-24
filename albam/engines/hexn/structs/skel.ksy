meta:
  id: hexane_skel
  endian: le
  title: Hexane Engine Skeleton Format (RE:ORC dlc/pack1/Characters/skel/*.ssg)
  license: CC0-1.0
  ks-version: '0.11'

# RE:ORC's skeletons live in a completely separate file tree from the
# per-character .edgemodel meshes: dlc/pack1/Characters/skel/<name>.ssg (note
# the capitalized "Characters", a distinct directory tree from the lowercase
# dlc/pack1/characters/<name>/models/<name>.edgemodel meshes - the stem
# matches, e.g. <name>.edgemodel <-> skel/<name>.ssg). These are NOT the normal
# solid/chunk-compressed .ssg format modeled in ssg.ksy - the same ".ssg"
# extension is reused for a completely different single-payload container.
# HexaneSsg's own id_magic check (little-endian [0x06, 0, 0, 0]) rejects
# these outright (big-endian [0, 0, 0, 0x06] instead), which is why
# HexnFS.__init__'s try/except around SsgFS() silently swallows every one of
# these into failed_ssgs today - this .ksy parses the raw bytes directly
# instead (see mesh.py, which fetches them via vfs.get_vfile() the same way
# material.py fetches a .matb, not through SsgFS/HexnFS).
#
# Modeled against a full sweep of real dlc/pack1/Characters/skel/*.ssg
# files (humans and creatures alike - a handful of hand-verified samples
# first, then a wider pass confirming every structural formula below with
# zero exceptions). A couple of committed samples exist for local
# iteration without the full dataset: tests/data/orc/skel/ (gitignored
# like the rest of tests/data/, matching the character archives already
# committed-adjacent at tests/data/orc/).
#
# Byte-order oddity: this file was apparently never byte-swapped for the PC
# port the way the main content .ssg was - RE:ORC also shipped on Xbox
# 360/PS3 (both big-endian), and the outer header below is still big-endian
# on every platform's copy of this file. The inner body (from the "20SE" tag
# at 0xC0 onward) switches to little-endian instead - self-consistently
# proven by `total` appearing as a big-endian u32 at outer inner_body_size
# (0x28) AND as a little-endian u32 at body's own `total` (0xC4), same bytes
# reversed, same numeric value.
#
# A recurring convention through the inner body (confirmed exact for
# d8_ofs_local_transforms, dc_ofs_post_transforms, e0_ofs_hash_array,
# e4_ofs_body_end_a, e8_ofs_body_end_b, ec_ofs_u16_array_end and
# f0_ofs_name_offsets, every file in the verified dataset): each of these u4 fields is a
# self-relative offset - its own absolute file position (a compile-time
# literal here, since every field before hierarchy sits at a fixed offset)
# PLUS the field's stored value gives the absolute position it points to.

seq:
  - {id: magic, contents: [0x00, 0x00, 0x00, 0x06]}
  - {id: reserved_01, type: u4be}
  - id: header_size
    type: u4be
    doc: Constant 32 on every file checked. Meaning beyond that not pinned down.
  - id: name_field_size
    type: u4be
    doc: Constant 128 - matches own_path's fixed field size below.
  - id: body_size
    type: u4be
    doc: >
      filesize - 0xC0, confirmed exact on every file checked. Includes the
      zero-padded tail after the real body content ends (see `total` below,
      and trailing_padding) - every file's size is padded so
      filesize % 128 == 64, confirmed across the verified dataset.
  - {id: reserved_02, type: u4be}
  - {id: reserved_03, type: u4be}
  - id: reserved_04
    type: u4be
    doc: Constant 0x00800000 on every file checked.
  - id: checksum_1
    type: u4be
    doc: >
      Varies per file. Almost certainly a checksum of some kind (paired with
      checksum_2 below) - not chased further, not needed for import.
  - {id: reserved_05, type: u4be}
  - id: inner_body_size
    type: u4be
    doc: Big-endian duplicate of body's own `total` (0xC4) - see meta comment above.
  - id: reserved_06
    type: u4be
    doc: Constant 1 on every file checked.
  - {id: reserved_07, type: u4be}
  - id: reserved_08
    type: u4be
    doc: Constant 4 on every file checked.
  - id: checksum_2
    type: u4be
    doc: Varies per file - see checksum_1.
  - {id: reserved_09, type: u4be}
  - id: own_path
    size: 128
    type: strz
    encoding: ASCII
    doc: >
      The file's own virtual path, e.g. "dlc/pack1/characters/skel/<name>"
      (lowercase, unlike the "Characters" directory it's actually filed
      under on disk) - null-padded to fill the fixed 128-byte field.
  - {id: tag, contents: "20SE"}
  - id: total
    type: u4
    doc: >
      Body content size from `tag` (0xC0) to where the real content ends
      (before zero-padding to the file's own alignment boundary) - i.e.
      body_end (an instance below) equals 0xC0 + total exactly, confirmed on
      every file checked.
  - id: c8_unk
    type: u4
    doc: >
      Does not cleanly match any layout formula derived from the other
      fields (checked against several candidates: names-blob size alone,
      names-blob + hash-array, body_end - names_start - none hold on every
      file). Captured for round-trip only; not used to locate anything below
      - every section's position/size is instead derived from node_count,
      hierarchy_size and the self-relative offset fields.
  - id: hierarchy_size
    type: u4
    doc: >
      Byte size of the `hierarchy` array below AND (confirmed across the verified dataset) of
      `hash_array` further down - both share the formula
      round_up(node_count * 4, 16).
  - id: node_count
    type: u4
    doc: >
      Exact count of entries in `hierarchy`, `local_transforms`,
      `post_transforms_data`'s implicit per-node array, `name_offsets` and
      `names` alike (confirmed across the verified dataset). Also matches
      the corresponding .edgemodel's own edge_header.num_bones exactly
      (cross-checked against a real sample mesh/skeleton pair) - and real
      vertex weight bone indices in that mesh range up to node_count - 1,
      not second_count - 1, so
      node_count (not second_count) is the space vertex group / bone-name
      resolution should use.
  - id: second_count
    type: u4
    doc: >
      A second, smaller count (roughly a quarter to a third of node_count
      across the verified dataset). Not confirmed: doesn't match the count
      of bone names lacking an "_auto"/"_dyn"/"_face"/"mk_auto" suffix
      (close on real samples, but not exact), and real vertex-weight
      bone indices
      use the full node_count range, not this one (see node_count doc) - so
      it is NOT the deforming-bone count in the vertex-weight sense. Left
      unattributed; captured for round-trip only.
  - id: d8_ofs_local_transforms
    type: u4
    doc: Self-relative offset (0xD8 + value) to `local_transforms`. See meta comment.
  - id: dc_ofs_post_transforms
    type: u4
    doc: >
      Self-relative offset (0xDC + value) to the end of `local_transforms` /
      start of `post_transforms_data`. See meta comment.
  - id: e0_ofs_hash_array
    type: u4
    doc: >
      Self-relative offset (0xE0 + value) to `hash_array`. See meta comment
      and hash_array's own doc.
  - id: e4_ofs_body_end_a
    type: u4
    doc: >
      Self-relative offset (0xE4 + value); resolves to body_end on every
      file checked - redundant with `total`/e8_ofs_body_end_b.
  - id: e8_ofs_body_end_b
    type: u4
    doc: Self-relative offset (0xE8 + value); also resolves to body_end - see e4_ofs_body_end_a.
  - id: ec_ofs_u16_array_end
    type: u4
    doc: >
      Self-relative offset (0xEC + value) to the unpadded end of
      `post_transforms_data`'s implicit per-node u16 array (before its own
      round-up-to-16 padding) - i.e. dc_ofs_post_transforms's target plus
      exactly node_count * 2 bytes.
  - id: f0_ofs_name_offsets
    type: u4
    doc: >
      Self-relative offset (0xF0 + value) to `name_offsets` - i.e.
      ec_ofs_u16_array_end's target rounded up to the next 16-byte boundary.
  - {id: reserved_10, type: u4}
  - {id: reserved_11, type: u4}
  - {id: reserved_12, type: u4}
  - id: hierarchy
    type: hierarchy_entry
    repeat: expr
    repeat-expr: node_count
    doc: >
      Fixed at absolute 0x100 (right after the fields above, always exactly
      that size). node_count entries, 4 bytes each.

instances:
  hierarchy_end:
    value: 0x100 + hierarchy_size
  hierarchy_padding:
    pos: 0x100 + (node_count * 4)
    size: hierarchy_size - (node_count * 4)
    if: hierarchy_size > node_count * 4
    doc: >
      The gap between the real hierarchy entries (node_count * 4 bytes) and
      hierarchy_end. NOT plain alignment padding - real, non-zero data on
      most files checked, the same 4-bytes-per-entry shape as
      `hierarchy` itself (plausible small node-index-like u16 pairs), just
      not accounted for by node_count. Purpose not identified - captured
      opaquely, same convention as edgemodel.ksy's own unattributed
      regions. Modeled as its own field (rather than left to `hierarchy`'s
      own declared size) so it round-trips at all: a Kaitai `seq` array's
      write only emits its real repeat-expr entries, never bytes beyond
      them.
  local_transforms_start:
    value: 0xD8 + d8_ofs_local_transforms
  pre_transforms_data:
    pos: hierarchy_end
    size: local_transforms_start - hierarchy_end
    if: local_transforms_start > hierarchy_end
    doc: >
      Real (non-zero, non-constant) per-file data between the hierarchy
      array and local_transforms - NOT simply padding (sizes seen: 0, 16,
      32, 48, 80, 96, 208, 224 bytes across the sweep, and its bytes decode
      as plausible small node-index-like u16 pairs on inspection). Purpose
      not identified; captured opaquely for round-trip, same convention as
      edgemodel.ksy's own unattributed regions.
  local_transforms:
    pos: local_transforms_start
    type: local_trs
    repeat: expr
    repeat-expr: node_count
    doc: >
      Per-node bind-pose local transform (relative to the parent named in
      `hierarchy`), node_count entries of 48 bytes each - confirmed via an
      automated scan (unit-length quaternion, both trailing homogeneous w's
      exactly 1.0, verified against the following entry too to rule out a
      false positive) on the hand-checked samples, and the resulting
      recursively-composed world positions are a plausible humanoid bind
      pose (Y-up, confirmed by composing a real sample's full hierarchy -
      matches mesh.py's own (x, -z, y) game-to-Blender axis convention
      for vertex positions).
  local_transforms_end:
    value: local_transforms_start + node_count * 48
  name_offsets_start:
    value: 0xF0 + f0_ofs_name_offsets
  post_transforms_data:
    pos: local_transforms_end
    size: name_offsets_start - local_transforms_end
    if: name_offsets_start > local_transforms_end
    doc: >
      Contains an implicit node_count * 2 byte u16 array right after
      local_transforms (values loosely increasing but not strictly
      monotonic per node - possibly a hash-bucket/sort order artifact, not
      identified), padded with zeros up to name_offsets_start
      (round_up(node_count * 2, 16), confirmed via ec_ofs_u16_array_end /
      f0_ofs_name_offsets both resolving exactly as documented on those
      fields, across the verified dataset). Captured opaquely as one blob rather than split into
      the u16 array + its padding, since the array's own semantics aren't
      confirmed.
  name_offsets:
    pos: name_offsets_start
    type: u4
    repeat: expr
    repeat-expr: node_count
    doc: >
      Byte offset of each node's name within `names`, relative to the start
      of `names` - confirmed exactly cumulative (offsets[i] == sum of
      len(name)+1 for every earlier name) on all node_count entries across
      every file in the verified dataset, so `names` below is read directly as
      a sequential null-terminated array instead of via this table's own
      per-entry pos (this table is still modeled as real data for
      round-trip, same reasoning as edgemodel.ksy's materials_table.offsets).
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
      `local_transforms` entry in the same order (index 0 is always a root,
      e.g. a root bone name) - confirmed by cross-referencing name_offsets
      above exactly, and by real, character-appropriate bone names across
      both humanoid and creature rigs.
  hash_array_start:
    value: 0xE0 + e0_ofs_hash_array
  hash_array:
    pos: hash_array_start
    size: hierarchy_size
    doc: >
      node_count u32 values (hierarchy_size bytes total, same round-up-to-16
      formula as `hierarchy`), immediately followed by body_end with no
      further gap (confirmed across the verified dataset: hash_array_start rounds `names`' real
      end up to the next 16-byte ABSOLUTE file boundary, not a
      names-blob-relative one, and hash_array_start + hierarchy_size ==
      body_end exactly on every file). Values don't match fnv1, fnv1a,
      djb2 or crc32 of the corresponding bone name (all four checked
      against a real sample's names) - plausibly a per-node hash using some
      other algorithm, or an unrelated per-node id. Captured opaquely.
  body_end:
    value: 0xC0 + total
  trailing_padding:
    pos: body_end
    size: _io.size - body_end
    if: _io.size > body_end
    doc: Zero-filled alignment padding out to the file's own size (see body_size doc).

types:
  hierarchy_entry:
    seq:
      - id: sort_key
        type: u2
        doc: >
          Per-node value, loosely increasing across the array but not
          strictly monotonic (real local dips seen on real samples) - not
          a plain running index. Purpose not identified.
      - id: parent_raw
        type: u2
        doc: >
          0xffff marks a root (multiple roots seen on real files). Otherwise
          the low 15 bits give the real parent node
          index (see parent_index) - the top bit (0x8000) is set on a
          sizeable minority of non-root entries and its meaning isn't
          confirmed (candidates not verified: "has multiple children",
          "twist/helper bone", "IK-related" - no clean correlation with the
          "_auto"/"mk_auto" name-suffix convention was found either).
    instances:
      is_root:
        value: parent_raw == 0xffff
      parent_flag:
        value: (parent_raw & 0x8000) != 0
        doc: Unattributed - see parent_raw's own doc.
      parent_index:
        value: 'is_root ? -1 : (parent_raw & 0x7fff)'
        doc: >
          Real parent node index into this same hierarchy/local_transforms/
          names array, or -1 for a root. Every real file checked has every
          parent_index < its own node index (safe to resolve/compose world
          transforms in a single forward pass).

  local_trs:
    seq:
      - id: rotation
        type: vec4f
        doc: Local bind-pose rotation quaternion (x, y, z, w), relative to the parent node.
      - id: position
        type: vec4f
        doc: >
          Local bind-pose position (x, y, z); w is a homogeneous coordinate,
          confirmed always exactly 1.0.
      - id: scale
        type: vec4f
        doc: >
          Local bind-pose scale (x, y, z); w is a homogeneous coordinate,
          confirmed always exactly 1.0. Scale itself is almost always
          (1, 1, 1) but not guaranteed.

  vec4f:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
