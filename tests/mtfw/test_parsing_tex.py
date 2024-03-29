from albam.engines.mtfw.texture import (
    TEX_FORMAT_MAPPER,
    Tex157,
)

ACCEPTABLE_SIZES = {2 ** n for n in range(2, 12)}  # min:8; max:2048


def test_parse_tex(tex):

    assert tex.width in ACCEPTABLE_SIZES
    assert tex.height in ACCEPTABLE_SIZES
    assert tex.num_images in (1, 6)  # XXX FAILS sometimes
    assert tex.compression_format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
    assert 0 < tex.num_mipmaps_per_image <= 11  # XXX FAILS sometimes

    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.type in (0x209d, 0xa09d))
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.reserved_01 == 0)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.shift == 0)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.dimension in (2, 6))
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.constant == 1)
    assert type(tex) is not Tex157 or (type(tex) is Tex157 and tex.reserved_02 == 0)
