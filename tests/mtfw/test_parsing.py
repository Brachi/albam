
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

KNOWN_FLOAT_BUFFER_HASHES = {
	0x7b2c215f,
	0x6c801200,
	0x7b2c2159,
	0x6c8011f9,
	0x7b2c2155,
	0x6c8011f4,
	0x7b2c215e,
	0x6c8011fe,
	0x15419236,
	0x51814237,
	0x22882238,
	0x6f01631b,
	0x61c6e23d,
	0xaee37319,
	0xefca3227,
	0xc48f7228,
	0x7b2c214c,
	0x6c8011ea,
	0xefca3222, # rehd
	0xc48f7223, # rehd
	0xaee3730c, # re6
	0x6F01630e, # re6
	0x1541922f, # re6
	0x51814230, # re6
	0xc48f7221,
	0xefca3220,
	0x84115310,
	0x22882231,	
}

TEX_TYPE_MAPPER = {
    0xcd06f,
    0x22660,
    0xaa6f0,
    0xed1b,
    0x75a53,
	0x64c43,
	0x1698a,
	0xff5be,
	0x1cb2a,
	0xed93b,
	0xa9787,
	0x39c0,
	0x4934a,
	0xed6be,
	0x1e421,
	0x343f4,
    0x57C1C,
    0x6ab7e,
    0x181cf,
    0xd4694,
	0x7b571,
	0x5f2a,
    0xc3df7,
    0x88165,
    0x7e9aa,
    0x62fde,
	0x52e1,
}


def test_mrl(mrl):
	materials = mrl.materials
	textures = mrl.textures
	assert mrl.id_magic == b"MRL\x00"
	assert mrl.num_materials == len(materials)
	assert mrl.num_textures == len(textures)
	set_buffer_hashes = set()
	for i, m in enumerate(mrl.materials):
		for j, res in enumerate(m.resources):
		#resources = {m.resources for m in mrl.materials}
		#set_buffer_hashes = {r.shader_object_hash for r in resources if r.info.cmd_type == 1 }
			if res.info.cmd_type == 3:
				set_buffer_hashes.add(res.shader_object_hash>>12)
	assert not set_buffer_hashes.difference(TEX_TYPE_MAPPER)

def test_mod(mod):

    assert mod.header.ident == b"MOD\x00"
    assert mod.header.version in SUPPORTED_MOD_VERSIONS

    vertex_formats = {m.vertex_format for m in mod.meshes}

    assert not vertex_formats.difference(KNOWN_VERTEX_FORMATS)


def test_lmt(lmt):

    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)