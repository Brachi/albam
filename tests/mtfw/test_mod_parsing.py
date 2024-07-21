SUPPORTED_MOD_VERSIONS = (156, 210, 211)

KNOWN_VERTEX_FORMATS = {
    0, 1, 2, 3, 4, 5, 6, 7, 8,
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


def test_mod(mod_imported):
    mod = mod_imported
    vertex_formats = {m.vertex_format for m in mod.meshes_data.meshes}
    total_num_weight_bounds = sum(m.num_weight_bounds for m in mod.meshes_data.meshes)
    # FIXME: mod.header.version == 211
    num_weight_bounds = (
        mod.num_weight_bounds if mod.header.version == 210
        else mod.meshes_data.num_weight_bounds
    )

    assert mod.header.ident == b"MOD\x00"
    assert mod.header.version in SUPPORTED_MOD_VERSIONS
    assert not vertex_formats.difference(KNOWN_VERTEX_FORMATS)
    assert total_num_weight_bounds == num_weight_bounds == len(mod.meshes_data.weight_bounds)
