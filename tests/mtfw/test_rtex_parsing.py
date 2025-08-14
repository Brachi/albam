from albam.engines.mtfw.texture import (
    TEX_FORMAT_MAPPER,
    # Rtex112,
    # Rtex157,
)


def test_parse_rtex(parsed_rtex_from_arc):
    rtex = parsed_rtex_from_arc
    if rtex.type == 6:
        assert rtex.num_images == 6
    assert rtex.num_images in (1, 6)
    assert rtex.compression_format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
