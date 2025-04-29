SBC_MAGIC_ID = [49, 255]


def test_parsed_sbc(parsed_sbc_from_arc):
    sbc = parsed_sbc_from_arc
    magic = sbc.header.magic
    assert magic[3] in SBC_MAGIC_ID
    if magic[3] == 255:
        for info in sbc.sbc_bvhc:
            assert info.node_count > 0
        assert sbc.bvh.node_count > 0
