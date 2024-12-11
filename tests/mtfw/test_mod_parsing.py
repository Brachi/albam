SUPPORTED_MOD_VERSIONS = (156, 210, 211, 212)

KNOWN_CONNECT = {
    0xff, 254, 253, 252, 249, 248, 247, 246, 245, 244, 241, 240, 237, 236, 232, 233,
    225, 224, 223, 220, 216, 212, 208, 204, 200, 192, 189, 188, 185, 184, 173, 172,
    169, 168, 127, 125, 124, 121, 120, 119, 117, 109, 108, 105, 104, 101, 100, 96,
    92, 76, 72, 64, 41, 40,
    0x00,  # doesn't exist in vanilla models
}

KNOWN_VERTEX_FORMATS = {
    0, 1, 2, 3, 4, 5,
    0x14d40020,
    0x2f55c03d,
    0xa320c016,
    0xa8fab018,
    0xb0983013,
    0xbb424024,
    0xc31f201c,
    0xcb68015,
    0xdb7da014,
    0xa7d7d036,
    0x49b4f029,
    0x207d6037,
    0xd8297028,
    0xd1a47038,
    0xb86de02a,
    0x63b6c02f,
    0x926fd02e,
    0x9399c033,
    0xcbf6c01a,
    0xd877801b,
    0xb392101f,
    0x64593023,
    0x5e7f202c,
    0xafa6302d,
    0xa14e003c,
    0xc66fa03a,
    0x667b1019,
    0xa013501e,
    0xb6681034,
    0x12553032,
    0x2082f03b,
    0x37a4e035,
    0x4325a03e,
    0x77d87022,
    0xd84e3026,
    0xcbCF7027,
    0xdA55a021,
    0xd9e801d,
    0x747d1031,
    0x75c3e025,
}

KNOWN_VTYPE = {
    0x0,    # skin
    0x1,    # skin_ex
    0x2,    # non_skin
    0x3,    # non_skin_col
    0x4,    # shape
    0x5,    # skin_col - extremey rare, in effectes mainly
}

KNOWN_VDEC = {
    0x0,    # skin
    0x1,    # non skin
    0x2,    # skinex
    0x5,    # skin base
    0x6,    # non skin base
    0x7,    # skin ex base
    0x8,    # non skin color
    0x9,    # non skin color extended
    0xa,    # shape base
    0xb,    # shape
    0xc,    # skin color
}

KNOWN_FUNC_SKIN = {
    0x0,    # skin none
    0x1,    # skin 1wt
    0x2,    # skin 2wt
    0x3,    # skin 4wt
    0x4,    # skin 8wt
    0x5,    # skin 4wt shape
}


KNOWN_DRAW_MODE = {
    0,
    32,
    4128,
    58560,
    58561,
    58577,
    58579,
    58821,
    58853,
    59080,
    59340,
    59112,
    59341,
    60901,
    61439,
    62689,
    62691,
    62949,
    62965,
    63469,
    63485,
    64755,
    64997,
    64999,
    65013,
    65015,
    65517,
    65519,
    65533,
    65534,
    65535,
}

KNOWN_TOPOLOGY = {
    3,
    4,  # probably strips
}


def test_mod(parsed_mod_from_arc):
    mod = parsed_mod_from_arc
    if mod.header.version == 156:
        materials = [m for m in mod.materials_data.materials]
        for m in mod.meshes_data.meshes:
            if m.vertex_stride_2 == 4:  # stride_2 = 4 only in non skin, shape base
                assert m.vdeclbase in [0x6, 0xa]
                assert m.vdecl in [0x1, 0x6, 0x9, 0xa, 0xb]
                assert materials[m.idx_material].vtype in [0x2, 0x3, 0x4]
                assert materials[m.idx_material].func_skin in [0x0, 0x5]
            if m.vertex_stride_2 == 8:
                assert m.vdeclbase in [0x2, 0x7]
                assert m.vdecl in [0x2, 0x7]
                assert materials[m.idx_material].vtype in [0x1]
                assert materials[m.idx_material].func_skin in [0x4]
            # connect
            connect = {m.connective for m in mod.meshes_data.meshes}
            for c in connect:
                assert c in KNOWN_CONNECT
            # vtype actual vertex format
            vtype_types = {m.vtype for m in mod.materials_data.materials}
            for vtype in vtype_types:
                assert vtype in KNOWN_VTYPE
            # vdeclbase
            vdeclbase_types = {m.vdeclbase for m in mod.meshes_data.meshes}
            for vbase in vdeclbase_types:
                assert vbase in KNOWN_VDEC
            # vdecl
            vdecl_types = {m.vdecl for m in mod.meshes_data.meshes}
            for vdec in vdecl_types:
                assert vdec in KNOWN_VDEC
            # skin func
            skin_func = {m.func_skin for m in mod.materials_data.materials}
            for vf in skin_func:
                assert vf in KNOWN_FUNC_SKIN
        total_num_weight_bounds = sum(m.num_weight_bounds for m in mod.meshes_data.meshes)
        vertex_formats = vtype_types
    else:
        vertex_formats = {m.vertex_format for m in mod.meshes_data.meshes}
        draw_modes = {m.draw_mode for m in mod.meshes_data.meshes}
        topology = {m.topology for m in mod.meshes_data.meshes}
        assert not draw_modes.difference(KNOWN_DRAW_MODE)
        assert not topology.difference(KNOWN_TOPOLOGY)
    total_num_weight_bounds = sum(m.num_weight_bounds for m in mod.meshes_data.meshes)
    # FIXME: mod.header.version == 211
    num_weight_bounds = (
        mod.num_weight_bounds if mod.header.version == 210 or mod.header.version == 212
        else mod.meshes_data.num_weight_bounds
    )

    assert mod.header.ident == b"MOD\x00"
    assert mod.header.version in SUPPORTED_MOD_VERSIONS
    assert not vertex_formats.difference(KNOWN_VERTEX_FORMATS)
    assert total_num_weight_bounds == num_weight_bounds == len(mod.meshes_data.weight_bounds)
