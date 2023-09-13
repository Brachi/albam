
SUPPORTED_MOD_VERSIONS = (156, 210, 211)
SUPPORTED_LMT_VERSIONS = (51, )
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

    assert not vertex_formats.difference(KNOWN_VERTEX_FORMATS)


def test_lmt(lmt):

    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
