
SUPPORTED_LMT_VERSIONS = (51, 67)


def test_lmt(parsed_lmt_from_arc):
    lmt = parsed_lmt_from_arc
    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
    if lmt.version == 67:
        for block in lmt.block_offsets:
            if block.offset != 0:
                anim_header = getattr(block, "block_header")
                assert anim_header.ofs_buffer_2 == 0
