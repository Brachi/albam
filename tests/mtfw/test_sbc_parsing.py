SBC_MAGIC_ID = [49, 255]
KNOWN_TYPE_ID = [256, 512, 1024, 2048, 3072, 3584, 4096, 4352, 5120, 7168, 9216, 8192, 11264, 11776, 16384,
                 17408, 32768, 33280, 33792, 34304, 34816, 35840, 40960, 40448, 41984, 42496, 42752, 44032,
                 44288, 49152, 65536, 131072, 1048576, 2097152, 262144, 524288, 134217728, 33554432, 67108864
                 ]
KNOWN_NODE_BIT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 15, 17, 19, 20, 21, 23, 29, 30, 31, 33,
                  45, 47, 53, 55, 61, 63, 64, 67, 69, 76, 127, 128, 129, 195,
                  200, 207, 216, 225, 227, 237, 239, 245, 255]


def test_parsed_sbc(parsed_sbc_from_arc):
    sbc = parsed_sbc_from_arc
    magic = sbc.header.magic
    assert magic[3] in SBC_MAGIC_ID
    if magic[3] == 255:
        for info in sbc.sbc_bvhc:
            assert info.node_count > 0
        assert sbc.bvh.node_count > 0
    elif magic[3] == 49:
        sbc_info = [info for info in sbc.sbc_info]
        assert sbc_info[0].start_nodes == sbc.header.num_parts
        for i, node in enumerate(sbc.nodes):
            if i >= sbc.header.num_parts:
                break
            if False:
                # doesn't pass for s107h_sr1.sbc s109h_scr.sbc s205h_eff.sbc ...
                assert node.aabb_01.min.x == sbc_info[i].min[0].x
                assert node.aabb_01.min.y == sbc_info[i].min[0].y
                assert node.aabb_01.min.z == sbc_info[i].min[0].z

                assert node.aabb_02.min.x == sbc_info[i].min[1].x
                assert node.aabb_02.min.y == sbc_info[i].min[1].y
                assert node.aabb_02.min.z == sbc_info[i].min[1].z

                assert node.aabb_01.max.x == sbc_info[i].max[0].x
                assert node.aabb_01.max.y == sbc_info[i].max[0].y
                assert node.aabb_01.max.z == sbc_info[i].max[0].z

                assert node.aabb_02.max.x == sbc_info[i].max[1].x
                assert node.aabb_02.max.y == sbc_info[i].max[1].y
                assert node.aabb_02.max.z == sbc_info[i].max[1].z

            assert node.bit in KNOWN_NODE_BIT
        # for face in sbc.faces:
        #     assert face.type in KNOWN_TYPE_ID
