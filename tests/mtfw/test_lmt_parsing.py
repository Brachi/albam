
SUPPORTED_LMT_VERSIONS = (51, 67)
SUPPORTED_BUFFER_TYPES = [1, 2, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re0 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re1 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# rev1 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13]
# rev2 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re 5[2, 4, 6, 9]
# re 6[1, 2, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]


def test_lmt(parsed_lmt_from_arc, capsys):
    lmt = parsed_lmt_from_arc
    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
    anim_blocks = {ab.block_header for ab in lmt.block_offsets if ab.offset != 0}

    for ab in anim_blocks:
        tracks = getattr(ab, "tracks")
        for tr in tracks:
            assert tr.buffer_type in SUPPORTED_BUFFER_TYPES
