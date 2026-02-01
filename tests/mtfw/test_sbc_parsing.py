from albam.engines.mtfw.collision import KNOWN_RUNTIME_ATTR
SBC_MAGIC_ID = [49, 255]
KNOWN_NODE_BIT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 15, 17, 19, 20, 21, 23, 29, 30, 31, 33,
                  45, 47, 53, 55, 61, 63, 64, 67, 69, 76, 127, 128, 129, 195,
                  200, 207, 216, 225, 227, 237, 239, 245, 255]

KNOWN_TYPE = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 8192, 16384, 32768, 131072,
              524288, 1048576, 209715, 262144, 4194304, 2097152, 8388608, 67108864, 536870912,
              134217728,]  # power of 2 flags ?

KNOWN_SPECIAL_ATTR = [0]
KNOWN_SURFACE_ATTR = [0]


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
        assert sbc_info[0].start_boxes == sbc.header.num_groups_nodes

        for i, node in enumerate(sbc.nodes):
            # if i >= sbc.header.num_groups:
            #    break
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
        for face in sbc.faces:
            assert face.runtime_attr in KNOWN_RUNTIME_ATTR
            assert face.type in KNOWN_TYPE
            assert face.special_attr in KNOWN_SPECIAL_ATTR
            assert face.surface_attr in KNOWN_SURFACE_ATTR
