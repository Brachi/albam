
SUPPORTED_LMT_VERSIONS = (51, 67)
SUPPORTED_BUFFER_TYPES = [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
LOCATION = [1, 4]
ROTATION = [0, 3]
SCALE = [2, 5]
BOUNDS_BUFF_TYPES = [4, 5, 7, 11, 12, 13, 14, 15]
JOINT_TYPES = [0, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 42, 43, 44, 48, 49]
BONES_WITH_JOINT_TYPES = [16, 11, 20, 6, 254]  # 20: "thigh_l",
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
            assert tr.joint_type in JOINT_TYPES
            assert tr.buffer_type in SUPPORTED_BUFFER_TYPES
            if tr.buffer_type == 1:
                assert tr.usage in LOCATION or tr.usage in SCALE
                assert tr.len_data == 0
            elif tr.buffer_type == 2:
                if lmt.version == 51:
                    assert tr.usage in SCALE or tr.usage in LOCATION  # RE5
                else:
                    assert tr.usage in ROTATION
                    assert tr.len_data % 12 == 0
            elif tr.buffer_type == 3:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.len_data % 16 == 0
            elif tr.buffer_type == 4:
                if lmt.version == 51:
                    assert tr.usage in ROTATION  # RE5
                    assert tr.len_data % 12 == 0
                else:
                    assert tr.usage in SCALE or tr.usage in LOCATION
                    assert tr.ofs_bounds != 0
                    assert tr.len_data % 8 == 0
            elif tr.buffer_type == 5:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 6:
                assert tr.usage in ROTATION
                assert tr.len_data % 8 == 0
            elif tr.buffer_type == 7:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 9:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.len_data % 16 == 0
            elif tr.buffer_type == 11:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 12:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 13:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 14:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 6 == 0
            elif tr.buffer_type == 15:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 5 == 0


def is_strictly_increasing(lst):
    return all(lst[i] < lst[i+1] for i in range(len(lst)-1))


def test_joint(parsed_lmt_from_arc):
    lmt = parsed_lmt_from_arc
    anim_blocks = {ab.block_header for ab in lmt.block_offsets if ab.offset != 0}
    for ab in anim_blocks:
        tracks = getattr(ab, "tracks")
        bones_joint_index = []
        seq = {}
        for track in tracks:
            # looks like 254 is some index for multiple service objects
            if track.bone_index == 254:
                # FAILED [fig29.arc::id\\figdata\\fig29\\fig29.lmt]
                # FAILED [uOma004_Collapse.arc::pawn\\om\\oma004\\motion\\oma004_pf.lmt]
                assert track.joint_type != 0
            if track.bone_index not in (254, 255):
                key = (track.bone_index, track.usage, track.joint_type)
                # assert key not in bones_joint_index
                bones_joint_index.append(key)
                if track.bone_index not in seq:
                    seq[track.bone_index] = [track.usage]
                else:
                    seq[track.bone_index].append(track.usage)
        for k, v in seq.items():
            if len(v) > 1:
                # looks like it's a sequence of usage per bone [0, 1, 2]
                assert is_strictly_increasing(v)

    # print(bones_joint_index)
