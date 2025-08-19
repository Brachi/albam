
SUPPORTED_LMT_VERSIONS = (51, 67)
SUPPORTED_BUFFER_TYPES = [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
LOCATION = [1, 4]
ROTATION = [0, 3]
SCALE = [2, 5]
BOUNDS_BUFF_TYPES = [4, 5, 7, 11, 12, 13, 14, 15]
# re0 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re1 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# rev1 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13]
# rev2 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re 5[2, 4, 6, 9]
# re 6[1, 2, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]


def test_lmt(parsed_lmt_from_arc):
    lmt = parsed_lmt_from_arc
    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
    anim_blocks = {ab.block_header for ab in lmt.block_offsets if ab.offset != 0}

    for ab in anim_blocks:
        if lmt.version == 67:
            assert ab.seq_num == 4  # as 3 bit value probably constant
            if ab.kf_num > 0:
                assert ab.kf_num == 4
        tracks = getattr(ab, "tracks")
        for tr in tracks:
            assert tr.buffer_type in SUPPORTED_BUFFER_TYPES
            if tr.buffer_type == 1:
                assert tr.usage in LOCATION or tr.usage in SCALE
            elif tr.buffer_type == 2:
                if lmt.version == 51:
                    assert tr.usage in SCALE or tr.usage in LOCATION  # RE5
                else:
                    assert tr.usage in ROTATION
            elif tr.buffer_type == 3:
                assert tr.usage in SCALE or tr.usage in LOCATION
            elif tr.buffer_type == 4:
                if lmt.version == 51:
                    assert tr.usage in ROTATION  # RE5
                else:
                    assert tr.usage in SCALE or tr.usage in LOCATION
                    assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 5:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 6:
                assert tr.usage in ROTATION
            elif tr.buffer_type == 7:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 9:
                assert tr.usage in SCALE or tr.usage in LOCATION
            elif tr.buffer_type == 11:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 12:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 13:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 14:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds.ofs_buffer != 0
            elif tr.buffer_type == 15:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds.ofs_buffer != 0

