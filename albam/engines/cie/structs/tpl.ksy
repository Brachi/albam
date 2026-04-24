meta:
  id: tpl
  file-extension: tpl
  endian: le
  ks-version: "0.11"
  title: Capcom Internal Engine texture palette
  
seq:
  - {id: magic, type: u4}
  - {id: num_tpl, type: u4}
  - {id: offset, type: u4}
instances:
  tpl_entries:
    {pos: offset, type: tpl_entry, repeat: expr, repeat-expr: num_tpl}

types:
  tpl_entry:
    seq:
    - {id: offset_image_data, type: u4}
    - {id: offset_palette, type: u4}
    instances:
      image_data:
        {pos: offset_image_data, type: tpl_info}

  tpl_ids:
    seq:
      - {id: pack_id, type: u4}
      - {id: texture_id, type: u4}  

  tpl_info:
    seq:
      - {id: width, type: u2}
      - {id: height, type: u2}
      - {id: pixel_format_type, type: u4}
      - {id: id_offset, type: u4}
      - {id: wrap_s, type: u4}
      - {id: wrap_t, type: u4}
      - {id: min_filter, type: u4}
      - {id: mag_filter, type: u4}
      - {id: lod_bias, type: f4}
      - {id: enable_lod, type: u1}
      - {id: min_lod, type: u1}     
      - {id: max_lod, type: u1}       
      - {id: is_compressed, type: u1}
    instances:
      ids:
       {pos: id_offset, type:  tpl_ids}
