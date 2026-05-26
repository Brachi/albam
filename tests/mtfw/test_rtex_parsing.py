from albam.engines.mtfw.texture import TEX_FORMAT_MAPPER
TEX_VERSIONS_157 = {153, 154, 155, 157, 158}


def test_parse_rtex(parsed_rtex_from_arc):
    rtex = parsed_rtex_from_arc
    rtex_version = rtex.version
    type_attr = "texture_type" if rtex_version == 112 else "type"
    if getattr(rtex, type_attr) == 6:
        assert rtex.num_images == 6
    assert rtex.num_images in (1, 6)
    assert rtex.compression_format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
    if rtex_version != 112:
        assert rtex.version in TEX_VERSIONS_157
