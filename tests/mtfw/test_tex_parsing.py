from albam.engines.mtfw.texture import (
    TEX_FORMAT_MAPPER,
    Tex157,
)

ACCEPTABLE_SIZES = {2 ** n for n in range(2, 12)}  # min:8; max:2048
ACCEPTABLE_SIZES.add(360)
ACCEPTABLE_SIZES.add(384)
ACCEPTABLE_SIZES.add(640)
ACCEPTABLE_SIZES.add(720)
ACCEPTABLE_SIZES.add(768)
ACCEPTABLE_SIZES.add(1280)
ACCEPTABLE_SIZES.add(1920)
ACCEPTABLE_SIZES.add(1080)
TEX_VERSIONS_157 = {153, 154, 157, 158}
TEX_TYPES_157 = {0x2, 0x3, 0x6}
TEX_ATTR_157 = {0x0}
UNK = {0, 32, 160}
TEX_PREBIAS_157 = {0, 1, 2}


def test_parse_tex(parsed_tex_from_arc):
    tex = parsed_tex_from_arc
    assert tex.width in ACCEPTABLE_SIZES
    assert tex.height in ACCEPTABLE_SIZES
    assert tex.num_images in (1, 6)  # XXX FAILS sometimes
    assert tex.format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
    assert 0 < tex.num_mipmaps_per_image <= 12  # XXX FAILS sometimes

    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.version in TEX_VERSIONS_157)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.unk in UNK)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.attr in TEX_ATTR_157)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.prebias in TEX_PREBIAS_157)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.type in TEX_TYPES_157)  # tex.dimension 
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.depth == 1)
    #assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.shift == 0)
    #assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.dimension in (2, 3, 6))
    #assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.constant in (1, 32))  # 32 nomipmap?
    #assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.reserved_02 == 0)
