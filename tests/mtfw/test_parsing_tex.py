from albam.engines.mtfw.texture import TEX_FORMAT_MAPPER

ACCEPTABLE_SIZES = {2 ** n for n in range(2, 12)}  # min:8; max:2048


def test_parse_tex(tex):
    assert tex.type in (0x209d, 0xa09d)
    assert tex.reserved_01 == 0
    assert tex.shift == 0
    assert tex.dimension in (2, 6)  # XXX fails
    assert tex.num_images in (1, 6)  # XXX fails
    assert tex.compression_format in TEX_FORMAT_MAPPER
    assert tex.constant == 1  # XXX fails, could be 32 too (LM)
    assert tex.reserved_02 == 0
    assert 0 < tex.num_mipmaps_per_image <= 11  # XXX FAILS
    # TODO num_mipmaps_per_image calulation
    assert tex.width in ACCEPTABLE_SIZES
    assert tex.height in ACCEPTABLE_SIZES
