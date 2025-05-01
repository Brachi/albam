SBC_MAGIC_ID = [49, 255]
KNOWN_TYPE_ID = [256, 512, 1024, 2048, 3072, 3584, 4096, 4352, 5120, 7168, 9216, 8192, 11264, 11776, 16384,
                 17408, 32768, 33280, 33792, 34304, 34816, 35840, 40960, 40448, 41984, 42496, 42752, 44032,
                 44288, 49152, 65536, 131072, 1048576, 2097152, 262144, 524288, 134217728, 33554432, 67108864
                 ]


def test_parsed_sbc(parsed_sbc_from_arc):
    sbc = parsed_sbc_from_arc
    magic = sbc.header.magic
    assert magic[3] in SBC_MAGIC_ID
    if magic[3] == 255:
        for info in sbc.sbc_bvhc:
            assert info.node_count > 0
        assert sbc.bvh.node_count > 0
    elif magic[3] == 49:
        for face in sbc.faces:
            assert face.type in KNOWN_TYPE_ID
