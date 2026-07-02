meta:
  id: evd
  title: RE4 EVD File Format
  file-extension: evd
  endian: le
  ks-version: "0.11"

seq:
  - {id: header, type: evd_header}
instances:
  packets:
    pos: header.offset_pac
    type: evp_header
    repeat: until
    repeat-until: _io.pos >= header.offset_pac + header.size_pac
  file_entries:
    pos: header.offst_bin_tbl
    type: file_entry(_index)
    repeat: expr
    repeat-expr: header.num_bin_tbl
 
types:
  evd_info:
    seq:
      - {id: name, type: str, size: 32, encoding: UTF-8}
      - {id: room_no, type: str, size: 8, encoding: UTF-8}
      - {id: event_no, type: str, size: 8, encoding: UTF-8}
      - {id: serial_no, type: u4}
      - {id: evd_flag, type: u4}
      - {id: filler, type: u4, repeat: expr, repeat-expr: 2}
  evd_header:
    seq:
      - {id: info, type: evd_info}
      - {id: offset_pac, type: u4}
      - {id: size_pac, type: u4} # size of evd_header +data
      - {id: num_bin_tbl, type: u4}
      - {id: offst_bin_tbl, type: u4}
  evp_header:
    seq:
      - {id: evp_type, type: u4, enum: evp_tp}
      - {id: flag_common, type: u4}
      - {id: no_cut, type: u2}
      - {id: frame, type: u2}
      - {id: size, type: u2}
      - {id: no_pack, type: u2}
      - id: data
        type:
          switch-on: evp_type
          cases:
            #'evp_tp::evp_tp_begin_evt': u1 # empty
            'evp_tp::evp_tp_set_pl': evp_set_pl
            'evp_tp::evp_tp_set_em': evp_set_em
            'evp_tp::evp_tp_set_om': evp_set_om
            'evp_tp::evp_tp_set_parts': evp_set_parts
            'evp_tp::evp_tp_set_list': evp_set_list
            'evp_tp::evp_tp_cam': evp_cam
            'evp_tp::evp_tp_cam_pos': evp_cam_pos
            'evp_tp::evp_tp_cam_dammy': evp_cam_dammy
            'evp_tp::evp_tp_pos': evp_pos
            'evp_tp::evp_tp_pos_pl': evp_pos_pl
            'evp_tp::evp_tp_mot': evp_mot
            'evp_tp::evp_tp_shp': evp_shp
            'evp_tp::evp_tp_esp': evp_esp
            'evp_tp::evp_tp_lit': evp_lit
            'evp_tp::evp_tp_str': evp_str
            'evp_tp::evp_tp_se': evp_se
            'evp_tp::evp_tp_mes': evp_mes
            'evp_tp::evp_tp_func': evp_func
            'evp_tp::evp_tp_parent_on': evp_parent_on
            'evp_tp::evp_tp_parent_off': evp_parent_off
            'evp_tp::evp_tp_end_pl': evp_end_pl
            'evp_tp::evp_tp_end_em': evp_end_em
            'evp_tp::evp_tp_end_om': evp_end_om
            'evp_tp::evp_tp_end_parts': evp_end_parts
            'evp_tp::evp_tp_end_list': evp_end_list
            #'evp_tp::evp_tp_end_evt': u1 # empty
            #'evp_tp::evp_tp_end_pac': u1 # empty
            'evp_tp::evp_tp_set_eff': evp_set_eff
            'evp_tp::evp_tp_fade': evp_fade
            'evp_tp::evp_tp_fog': evp_fog
            'evp_tp::evp_tp_focus': evp_focus
            'evp_tp::evp_tp_set_mdt': evp_set_mdt
  file_entry:
    params:
      - id: i
        type: s4
    seq:
      - {id: name_file, type: str, size: 48, encoding: UTF-8, terminator: 0}
      - {id: offset, type: u4}
      - {id: size, type: u4}
      - {id: filler, size: 8}
    instances:
      raw_data:
        pos: offset
        size: "i == _parent.header.num_bin_tbl - 1 ? (_io.size - offset) : (_parent.file_entries[i + 1].offset - offset)"
      
  evp_set_pl:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}  
      - {id: filler, size: 4}
  evp_set_em:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}  
      - {id: filler, size: 4}
  evp_set_om:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
      - {id: name_tpl, type: str, size: 48, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}
  evp_set_parts:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_oya, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
      - {id: name_tpl, type: str, size: 48, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 8}
  evp_set_eff:
    seq:
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
  evp_set_list:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: no_list, type: u4}
      - {id: filler, size: 1}
  evp_cam:
    seq:
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
  evp_cam_pos:
    seq:
      - {id: pos, type: vec3}
      - {id: ang, type: vec3}
      - {id: filler, size: 8}
  evp_cam_dammy:
    seq:
      - {id: time, type: u4}
      - {id: filler, size: 12}
  evp_pos:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_oya, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: pos, type: vec3}
      - {id: ang, type: vec3}
      - {id: parts_no, type: u4}
      - {id: filler, size: 12}
  evp_pos_pl:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 8}
  evp_mot:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_bin, type: str, size: 48, encoding: UTF-8}
      - {id: filler, size: 4}
  evp_shp:
     seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}
  evp_esp:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: kind, type: u4, enum: evt_esp_kind_id}
      - {id: id_est, type: u4}
      - {id: filler, size: 12}
  evp_lit:
    seq:
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
  evp_fog:
    seq:
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
  evp_focus:
    seq:
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
  evp_str:
    seq:
      - {id: no_tar, type: u4}
      - {id: no_str, type: u4}
      - {id: filler, size: 8}
  evp_se:
    seq:
      - {id: no_tar, type: u4}
      - {id: no_se, type: u4}
      - {id: filler, size: 8}
  evp_fade:
    seq:
      - {id: flat, type: u4, enum: evt_fade}
      - {id: fade_no, type: u4}
      - {id: timer, type: u4}
      - {id: filler, size: 4}
  evp_mes:
    seq:
      - {id: no_mes, type: u4}
      - {id: timer, type: u4}
      - {id: filler, size: 8}  
  evp_func:
    seq:
      - {id: no_func, type: u4}
      - {id: param, type: u4}
      - {id: filler, size: 8}  
  evp_parent_on:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: name_oya, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 8}     
  evp_parent_off:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}     
  evp_end_pl:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}
  evp_end_em:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}
  evp_end_om:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}
  evp_end_list:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}
  evp_end_parts:
    seq:
      - {id: name_mod, type: str, size: 12, encoding: UTF-8, terminator: 0}
      - {id: filler, size: 4}    
  evp_set_mdt:
    seq:
      - {id: name_bin, type: str, size: 48, encoding: UTF-8, terminator: 0}
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
enums:
  evp_tp:
    0: evp_tp_begin_evt # empty?
    1: evp_tp_set_pl
    2: evp_tp_set_em
    3: evp_tp_set_om
    4: evp_tp_set_parts
    5: evp_tp_set_list
    6: evp_tp_cam
    7: evp_tp_cam_pos
    8: evp_tp_cam_dammy
    9: evp_tp_pos
    10: evp_tp_pos_pl
    11: evp_tp_mot
    12: evp_tp_shp
    13: evp_tp_esp
    14: evp_tp_lit
    15: evp_tp_str
    16: evp_tp_se
    17: evp_tp_mes
    18: evp_tp_func
    19: evp_tp_parent_on
    20: evp_tp_parent_off
    21: evp_tp_end_pl
    22: evp_tp_end_em
    23: evp_tp_end_om
    24: evp_tp_end_parts
    25: evp_tp_end_list
    26: evp_tp_end_evt
    27: evp_tp_end_pac
    28: evp_tp_set_eff
    29: evp_tp_fade
    30: evp_tp_fog
    31: evp_tp_focus
    32: evp_tp_set_mdt

  evt_esp_kind_id:
    0: evt_esp_room
    1: evt_esp_core
    2: evt_esp_pl
    3: evt_esp_em
    4: evt_esp_wep
    5: evt_esp_evt
    6: evt_esp_et00

  evt_fade:
    0: evt_fade_in
    1: evt_fade_out