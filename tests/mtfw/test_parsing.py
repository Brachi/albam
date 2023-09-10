
SUPPORTED_MOD_VERSIONS = (156, 210)
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
}


def test_mrl(mrl):
    materials = mrl.materials
    textures = mrl.textures
    assert mrl.id_magic == b"MRL\x00"
    assert mrl.num_materials == len(materials)
    assert mrl.num_textures == len(textures)


def test_mod(mod):

    assert mod.header.ident == b"MOD\x00"
    assert mod.header.version in SUPPORTED_MOD_VERSIONS

    vertex_formats = {m.vertex_format for m in mod.meshes}

    assert all(v in KNOWN_VERTEX_FORMATS for v in vertex_formats)
