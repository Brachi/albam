
SUPPORTED_LMT_VERSIONS = (51, 67)


def test_lmt(lmt):

    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
