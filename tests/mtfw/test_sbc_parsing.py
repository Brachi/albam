from albam.engines.mtfw.collision import KNOWN_RUNTIME_ATTR
SBC_MAGIC_ID = [49, 255]
KNOWN_NODE156_BIT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 15, 17, 19, 20, 21, 23, 29, 30, 31, 33,
                     45, 47, 53, 55, 61, 63, 64, 67, 69, 76, 127, 128, 129, 195,
                     200, 207, 216, 225, 227, 237, 239, 245, 255]

KNOWN_TYPE156 = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 8192, 16384, 32768, 131072,
                 524288, 1048576, 209715, 262144, 4194304, 2097152, 8388608, 67108864, 536870912,
                 134217728,]  # power of 2 flags ?

KNOWN_SBC_INFO156_ID = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 15, 17, 18, 19, 20, 21, 22, 23,
                        24, 25, 26, 27, 28, 29, 31, 30, 32, 33, 35, 34, 37, 307, 308, 309, 310, 311, 500, 501,
                        502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 4294967295]

KNOWN_SPECIAL_ATTR = [0]
KNOWN_SURFACE_ATTR = [0]

SBC21_VERSION = [2011120601,  # rev2
                 2010091000,  # re6
                 ]


def test_parsed_sbc(parsed_sbc_from_arc):
    sbc = parsed_sbc_from_arc
    magic = sbc.header.indent
    assert magic[3] in SBC_MAGIC_ID
    if magic[3] == 255:
        assert sbc.header.unk_00 in SBC21_VERSION
        for info in sbc.sbc_bvhc:
            assert info.num_nodes > 0
        assert sbc.bvh.num_nodes > 0
    elif magic[3] == 49:
        sbc_info = [info for info in sbc.sbc_info]
        assert sbc_info[0].start_nodes == sbc.header.num_objects_nodes
        for info in sbc_info:
            assert info.index_id in KNOWN_SBC_INFO156_ID
        for i, node in enumerate(sbc.nodes):
            if i < sbc.header.num_objects_nodes:
                # doesn't pass for s107h_sr1 s109h_scr s205h_eff s205h_scr s304h_scr s312h_scr s316h_eff
                # s316h_scr
                assert node.boxes[0].min[0] == sbc_info[i].vmin[0].x
                assert node.boxes[0].min[1] == sbc_info[i].vmin[0].y
                assert node.boxes[0].min[2] == sbc_info[i].vmin[0].z

                assert node.boxes[1].min[0] == sbc_info[i].vmin[1].x
                assert node.boxes[1].min[1] == sbc_info[i].vmin[1].y
                assert node.boxes[1].min[2] == sbc_info[i].vmin[1].z

                assert node.boxes[0].max[0] == sbc_info[i].vmax[0].x
                assert node.boxes[0].max[1] == sbc_info[i].vmax[0].y
                assert node.boxes[0].max[2] == sbc_info[i].vmax[0].z

                assert node.boxes[1].max[0] == sbc_info[i].vmax[1].x
                assert node.boxes[1].max[1] == sbc_info[i].vmax[1].y
                assert node.boxes[1].max[2] == sbc_info[i].vmax[1].z
                sbc_child0 = sbc_info[i].child_index[0]
                sbc_child1 = sbc_info[i].child_index[1]
                if sbc_child0:
                    assert node.child_index[0] == sbc_child0
                if sbc_child1:
                    assert node.child_index[1] == sbc_child1
        for face in sbc.faces:
            assert face.runtime_attr in KNOWN_RUNTIME_ATTR
            assert face.type in KNOWN_TYPE156
            assert face.special_attr in KNOWN_SPECIAL_ATTR
            assert face.surface_attr in KNOWN_SURFACE_ATTR
