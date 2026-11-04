meta:
  bit-endian: le
  endian: le
  file-extension:
    - lot
    - sce
    - fsm
    - lsp
    - rvt
    - seg
    - smh
    - lku
    - lnk
    - los
    - lom
    - cmi
    - glp
    - bmse
  id: xfs
  ks-version: '0.11'
  title: MTFramework XFS property container

doc: |
  Self-describing container holding a tree of objects whose classes are
  declared up front: a table of class definitions, each a type hash and a list
  of named, typed properties, followed by the values themselves.

  Not a format of its own so much as the serialization every property-driven
  resource uses - the same header carries stage layout (.lot), scene (.sce),
  state machines (.fsm) and a dozen others, distinguished by the minor version
  and by which classes they declare. Modelled against a verified dataset
  spanning fourteen extensions: major version 6 throughout, minor 1 to 14.

  Every offset in the file is relative to the end of the fixed header, i.e. to
  absolute offset 16, never to the start of the file.

seq:
  - {id: header, type: xfs_header}
  - {id: class_def_offsets, type: u4, repeat: expr, repeat-expr: header.num_class_defs}
  - {id: class_defs, type: class_def, repeat: expr, repeat-expr: header.num_class_defs}
  - {id: name_table, size: _root.header.offset_data + 16 - _io.pos}
  - {id: data, type: data_section}

enums:
  # Only the values actually present in the modelled files are named; the gaps
  # are values not seen rather than values that do not exist. Sizes are certain,
  # being carried in the property itself and agreeing across every occurrence,
  # and several types name themselves through the properties that use them:
  # mConstS32 is a 10, Quat a 22, AABB a 47, m_inertiaTensor and Mat make 19 a
  # matrix44 at sixty-four bytes, and mUIPos makes 16 two floats at eight.
  #
  # Four are named for their width alone, and all four appear in one extension
  # only, on a handful of properties: unk_36 (mClampUV), unk_54 (SeqNo, PatNo),
  # unk_55 (BaseSize, Intensity, RotY) and unk_57 (mUVScaleCurve). Their widths
  # are known and their meaning is not settled here.
  property_type:
    1: class_
    2: class_ref
    3: bool_
    4: u8
    5: u16
    6: u32
    8: s8
    9: s16
    10: s32
    12: f32
    14: string
    15: color
    16: point
    18: rect
    19: matrix44
    20: vector3
    21: vector4
    22: quaternion
    36: float4
    47: aabb
    54: range
    55: rangef
    57: hermitecurve
    58: resource # custom

types:
  xfs_header:
    seq:
      - {id: ident, contents: [0x58, 0x46, 0x53, 0x00]}
      - {id: version_major, type: u2} # version
      - {id: version_minor, type: u2} # file_type
      - {id: num_class_defs, type: u2} # num_classes
      - {id: reserved, type: u2}
      - {id: offset_data, type: u4}
    doc: |
      version_major is 6 everywhere seen; version_minor identifies the schema
      the declared classes belong to and tracks the extension rather than the
      container (.fsm is 6.1, .lot 6.4, .sce 6.11, .lnk 6.14).

  class_def:
    seq:
      - {id: type_hash, type: u4}
      - {id: num_properties, type: u4}
      - {id: properties, type: property_def, repeat: expr, repeat-expr: num_properties}
    doc: |
      Class definitions are stored back to back in the order class_def_offsets
      lists them, each exactly 8 + 24 * num_properties bytes, so the offsets
      are redundant with walking them in sequence - checked to agree on every
      file modelled.

      type_hash is a hash of the class's own name: CRC32 with its final
      complement undone and the top bit cleared, which is
      `(~crc32(name)) & 0x7FFFFFFF`. That makes a name recoverable wherever
      one can be found to hash - see xfs_classes.py, which carries the ones
      confirmed so far. Confirmed against every layout that stores the name of
      the class it points at beside the class itself, with no disagreements.

  property_def:
    seq:
      - {id: name_offset, type: u4}
      - {id: type, type: u1, enum: property_type}
      - {id: flags, type: u1}
      - {id: size, type: u2}
      - {id: reserved, size: 16}
    doc: |
      size is the property's width in the value stream for every type that has
      a fixed one: 1 for bool_ and the 8-bit integers, 2 for the 16-bit ones,
      4 for the 32-bit types and for colour and the two class types, 8 for
      point, unk_54 and unk_55, 16 for rect, vector3, vector4, quaternion and
      unk_36, 32 for aabb, and 64 for matrix44 and unk_57.

      string and resource also declare 4, the width a loaded property needs
      for the pointer it ends up holding, but neither occupies four bytes in
      the file: both are written inline and are as long as their text. A
      reader that trusts size for those two desynchronises the value stream
      from that point on.

      reserved is 16 zero bytes in every file seen, the room a loaded property
      needs for pointers the file itself has no use for.
    instances:
      name:
        io: _root._io
        pos: 16 + name_offset
        type: str
        encoding: ASCII
        terminator: 0

  data_section:
    seq:
      - {id: num_roots, type: u4}
      - {id: size_, type: u4}
      - {id: root, type: object_body(0)}
    doc: |
      size_ counts itself, so what follows is size_ - 4 bytes and runs to the
      end of the file. num_roots is 1 in every file modelled.

      The root is an instance of the first class declared, written straight
      out with no header of its own - only nested objects carry one.

  object_body:
    params:
      - {id: class_index, type: s4}
    seq:
      - id: properties
        type: property_values(class_index, _index)
        repeat: expr
        repeat-expr: _root.class_defs[class_index].num_properties
    doc: |
      An object is just its class's properties in declaration order. Nothing
      is aligned and nothing is padded, so a position inside the value stream
      only means something to a reader that has walked everything before it.

  property_values:
    params:
      - {id: class_index, type: s4}
      - {id: prop_index, type: s4}
    seq:
      - {id: num_values, type: u4}
      - id: values
        repeat: expr
        repeat-expr: num_values
        type:
          switch-on: property.type
          cases:
            'property_type::string': string_value
            'property_type::resource': resource_value
            'property_type::class_': object_ref
            'property_type::class_ref': object_ref
            _: raw_value(property.size)
    doc: |
      Every property is a count followed by that many values, one for a plain
      scalar and zero for an empty array or an unset reference. Types the
      property carries a width for are taken at that width, whatever they
      mean; string and resource are written where they stand and ignore it.
    instances:
      property:
        value: _root.class_defs[class_index].properties[prop_index]

  raw_value:
    params:
      - {id: len_value, type: s4}
    seq:
      - {id: value, size: len_value}

  string_value:
    seq:
      - {id: value, type: str, encoding: ASCII, terminator: 0}
    doc: Written into the value stream where it stands, not into a table.

  resource_value:
    seq:
      - {id: kind, type: u1}
      - {id: class_name, type: str, encoding: ASCII, terminator: 0}
      - {id: path, type: str, encoding: ASCII, terminator: 0}
    doc: |
      A reference to another resource, named rather than numbered: the class
      that will load it and the path it lives at, both inline and both
      terminated. The path carries no extension - the class supplies it.

      An unset reference is still written out in full, with the literal class
      name `null` and an empty path, so a resource property is present whether
      or not it points anywhere - roughly half of those in the modelled data
      are null. kind is 2 in every value seen, null ones included.

  object_ref:
    seq:
      - {id: tag, type: u2}
      - {id: index, type: u2}
      - {id: size_, type: u4, if: is_inline}
      - {id: body, type: object_body(class_index), size: size_ - 4, if: is_inline}
    doc: |
      A reference points at nothing, carries an object inline, or names one
      already written; tag says which, and only the inline form has a body.

      tag is 0xfffe for a null reference. An odd tag carries an object inline
      and encodes its class as 2 * class_index + 1. An even tag is a
      back-reference to an object emitted earlier - `index` identifies it and
      nothing follows - which is how one object points at another without the
      tree having to nest, as a sprite does at its parent.

      index counts objects as they are written, from one, and is present in
      every form; it is unused for a null reference. size_ counts itself, as
      it does in the data section.

      Every back-reference in the modelled data carries tag 4, so the class
      encoding for the even form is consistent with tag / 2 but rests on that
      one value.
    instances:
      is_null:
        value: tag >= 0xfffe
      is_inline:
        value: 'not is_null and (tag % 2) == 1'
      class_index:
        value: 'is_inline ? (tag - 1) / 2 : tag / 2'
