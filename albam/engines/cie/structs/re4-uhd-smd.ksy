meta:
  id: re4_uhd_smd
  endian: le
  ks-version: "0.11"
  title: Capcom Internal Engine scenario file (room geometry and placement)

doc: |
  A room's own geometry, as opposed to the props standing in it.

  An .smd is a placement table plus the models it places: a list of fixed
  size entries, each naming a model by index and carrying the position,
  rotation and scale to put it at, followed - much later in the file - by
  two tables of offsets, one to the embedded models (the same format as a
  standalone mesh .bin, see re4-uhd-bin.ksy) and one to the embedded .tpl
  each entry addresses its textures through.

  Neither offset table states its own length: what ends one is a zero
  entry past its last real offset. The entries are no help there - a table
  can hold a model no entry places, and files sampled carry one spare that
  points at nothing readable - so the terminator is the only bound, and an
  offset only means something once an entry indexes it.

  A room too big for one file is split: the entries of the extra files can
  point at models embedded in the room's shared file rather than in
  themselves (see entry_status).

seq:
  - id: header
    type: smd_header
  # Fixed size, one per placed model, and every file sampled carries more
  # than it uses - the unused ones are zeroed and place nothing (see
  # smd_entry.is_placed).
  - id: entries
    type: smd_entry
    repeat: expr
    repeat-expr: header.num_entries

instances:
  # Offsets to the embedded models, each relative to the table's own
  # position rather than to the start of the file. Terminated by a zero.
  offsets_models:
    pos: header.offset_model_table
    type: u4
    repeat: until
    repeat-until: _ == 0
  # The same, for the embedded .tpl files.
  offsets_tpls:
    pos: header.offset_tpl_table
    type: u4
    repeat: until
    repeat-until: _ == 0

types:
  smd_header:
    seq:
      # Shipped as one of 0x0000, 0x0010, 0x0020, 0x0031, 0x0040 and
      # 0x0140, and a file carrying anything else is not a scenario. Only
      # 0x0140 changes the layout, adding the counts below. 0x0000 is a
      # stub: the files carrying it place nothing and their model table
      # points at no readable model.
      - id: magic
        type: u2
      - id: num_entries
        type: u2
      - id: offset_model_table
        type: u4
      - id: offset_tpl_table
        type: u4
      # Where the first embedded model starts. Redundant with the first
      # entry of the model table, and only a hint: nothing indexes it.
      - id: offset_first_model
        type: u4
      - id: extra
        type: extra_counts
        if: magic == 0x140

  # Only present on the 0x0140 magic, which is a room assembled out of
  # several files: one count of entries per file it is assembled from.
  extra_counts:
    seq:
      - id: num_values
        type: u4
      - id: values
        type: u4
        repeat: expr
        repeat-expr: num_values

  smd_entry:
    doc: |
      One placed model. The position is in the same unit as a model's own
      vertices, the angles are radians applied X then Y then Z, and the
      scale multiplies the rotated position per axis.
    seq:
      - id: position
        type: vec3f
      - id: angles
        type: vec3f
      - id: scale
        type: vec3f
      # Index into the model table - or into the shared file's model table,
      # when status says so.
      - id: model_id
        type: u1
      # Index into the .tpl table. Always into this file's own table, even
      # for a shared model.
      - id: tpl_id
        type: u1
      # 0xFF on every entry that places something, 0 on the zeroed spares.
      - id: enabled
        type: u1
      # Which entry of the room's .smx this model animates with, 0xFF for
      # none. The .smx itself is not modelled.
      - id: smx_id
        type: u1
      - id: unk_00
        type: u4
        repeat: expr
        repeat-expr: 7
      # Bit 0x10 means the model is not in this file at all: model_id
      # indexes the room's shared file instead. Bit 0x08 is set on every
      # entry that places something.
      - id: status
        type: u4
    instances:
      is_shared:
        value: (status & 0x10) != 0
      # A zeroed spare scales its model to nothing and places it at the
      # origin, so scale is what separates the entries that mean something
      # from the ones that are only there to be filled in later.
      is_placed:
        value: scale.x != 0.0 or scale.y != 0.0 or scale.z != 0.0

  vec3f:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
