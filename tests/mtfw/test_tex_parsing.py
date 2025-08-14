from albam.engines.mtfw.texture import (
    TEX_FORMAT_MAPPER,
    Tex157,
    Tex112
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
    # assert tex.width in ACCEPTABLE_SIZES
    # assert tex.height in ACCEPTABLE_SIZES
    assert tex.num_images in (1, 6)  # XXX FAILS sometimes
    assert tex.compression_format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
    assert 0 < tex.num_mipmaps_per_image <= 13  # XXX FAILS sometimes

    if type(tex) is Tex157:
        assert tex.version in TEX_VERSIONS_157
        assert tex.unk in UNK
        assert tex.attr == 0
        assert tex.prebias in TEX_PREBIAS_157
        assert tex.type in TEX_TYPES_157  # 2D-3D-Cube
        assert tex.depth in {1, 32}  # 32 for no mipmaps
    elif type(tex) is Tex112:
        assert tex.padding == 0  # not 0 only in modded files probably because of the old parser
        assert tex.attr == 0  # enum for FILLMARGIN, GRAYSCALE, NUKI, DITHER, RGBIENCODED, not used for PC RE5
        assert tex.depend_screen == 0
        assert tex.render_target == 0
