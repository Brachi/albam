meta:
  endian: le
  bit-endian: le
  file-extension: mfx
  id: mfx
  ks-version: 0.10
  title: MTFramework Shader List format
seq:
  - {id: id_magic, contents: [77, 70, 88, 0]}
  - {id: unk_01, type: u2}
  - {id: unk_02, type: u2}
  - {id: unk_03, type: u4}
  - {id: num_entries, type: u4}
  - {id: offset_string_table, type: u4}
  - {id: unk_04, type: u4}
  - {id: entry_pointers, type: mfx_entry_pointer, repeat: expr, repeat-expr: num_entries}

types:
  mfx_entry_pointer:
    seq:
      - {id: offset, type: u4}

    instances:
      mfx_entry:
        {pos: offset, type: mfx_entry}

  mfx_entry:
    seq:
      - {id: offset_string_1, type: u4}
      - {id: offset_string_2, type: u4}
      - {id: field_8_a, type: b6}
      - {id: field_8_b, type: b16}
      - {id: fill, type: b10}
      - {id: unk_01, type: u2}
      - {id: index, type: u2}
      - {id: field_c, type: u4}
      - {id: field_10, type: u4}
      - {id: num_attributes, type: u1}
      - {id: unk_02, type: u1}
      - {id: num_attributes0, type: u2}
      - id: attributes
        type:
          switch-on: field_8_a
          cases:
            8: attr_8
            9: attr_9
            0: attr_0

    instances:
      name:
        {pos: _root.offset_string_table + offset_string_1, type: str, encoding: ASCII, terminator: 0}
      friendly_name:
        {pos: _root.offset_string_table + offset_string_2, type: str, encoding: ASCII, terminator: 0}

  attr_8:
    seq:
      - {id: header, type: u4}
      - {id: body, type: mfx_attribute8, repeat: expr, repeat-expr: _parent.num_attributes}

  attr_9:
    seq:
      - {id: header, type: u4}
      - {id: body, type: mfx_attribute9, repeat: expr, repeat-expr: _parent.num_attributes}

  attr_0:
    seq:
    - {id: unk_ofs, type: u4}
    - {id: ofs_attr, type: u4}
    - {id: ofs_floats, type: u4}
    - {id: body, type: mfx_attribute0, repeat: expr, repeat-expr: _parent.num_attributes0}

  sub_attr0:
    seq:
      - {id: offset_name, type: u4}
      - {id: unk_00, type: u4}
      - {id: base_off, type: b4}
      - {id: instancing, type: b4}
      - {id: unk, type: b8}
      - {id: count, type: b8}
      - {id: comp_count, type: b8}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: unk_03, type: u4}
      - {id: unk_ofs_00, type: u4}
      - {id: unk_ofs_01, type: u4}
    instances:
      name:
        {pos: _root.offset_string_table + offset_name, type: str, encoding: ASCII, terminator: 0}

  mfx_attribute0:
    seq:
      - {id: offset_name, type: u4}
      - {id: unk_00, type: u2,repeat: expr, repeat-expr: 2}
      - {id: base_off, type: b4}
      - {id: count, type: b4}
      - {id: instancing, type: b8}
      - {id: unk_bit, type: b8}
      - {id: comp_count, type: b8}
      - {id: unk_01, type: u2}
      - {id: unk_02, type: u2}
      - {id: unk_b00, type: u1}
      - {id: float_buff_ofs, type: u1}
      - {id: unk_b01, type: u1}
      - {id: sub_attr_num, type: u1}
      - {id: sub_attr_ofs, type: u4}
      - {id: unk_ofs, type: u4}
    instances:
      name:
        {pos: _root.offset_string_table + offset_name, type: str, encoding: ASCII, terminator: 0}

  mfx_attribute8:
    seq:
      - {id: offset_name, type: u4}
      - {id: unk_01, type: b6}
      - {id: comp_type, type: b5}
      - {id: comp_count, type: b11}
      - {id: base_off, type: b9}
      - {id: instancing, type: b1}
      - {id: unk_02, type: u4, repeat: expr, repeat-expr: 5}
    instances:
      name:
        {pos: _root.offset_string_table + offset_name, type: str, encoding: ASCII, terminator: 0}

  mfx_attribute9:
    seq:
      - {id: offset_name, type: u4}
      - {id: unk_01, type: b6}
      - {id: comp_type, type: b5}
      - {id: comp_count, type: b11}
      - {id: base_off, type: b9}
      - {id: instancing, type: b1}
    instances:
      name:
        {pos: _root.offset_string_table + offset_name, type: str, encoding: ASCII, terminator: 0}
