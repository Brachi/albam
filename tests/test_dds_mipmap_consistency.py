"""DDSHeader.from_dds_bytes() / check_mipmap_consistency() catch a DDS whose
pixel data is shorter than the mipmap chain its header declares, before
export writes mipmap offsets past the end of it. Pure Python: building the
header and its payload synthetically needs no game data or Blender image.
"""
import pytest

from albam.exceptions import AlbamCheckFailure
from albam.lib.dds import DDSHeader


def _make_dds(width, height, mipmap_count, fourcc=b"DXT1", data_size=None, cubemap=False):
    header = DDSHeader(
        dwHeight=height,
        dwWidth=width,
        dwMipMapCount=mipmap_count,
        pixelfmt_dwFourCC=fourcc,
    )
    header.set_constants()
    header.set_variables(compressed=bool(fourcc), cubemap=cubemap)
    if data_size is None:
        data_size = sum(header.mipmap_sizes) * header.image_count
    return bytes(header) + b"\x00" * data_size


def test_consistent_full_mip_chain_is_not_rejected():
    DDSHeader.from_dds_bytes(_make_dds(256, 256, 9), "ok.dds")


def test_zero_mipmaps_is_read_as_one_level():
    # GIMP, Paint.NET and NVTT leave dwMipMapCount at 0 when saving without
    # mipmaps; the base level's bytes are there.
    header = DDSHeader.from_dds_bytes(_make_dds(64, 64, 0, data_size=32 * 32 * 2), "no_mips.dds")

    assert header.dwMipMapCount == 1
    assert len(header.calculate_mimpap_offsets(0)) == 1


def test_mipmap_count_taller_than_the_data_is_rejected():
    dds = _make_dds(64, 64, 7, data_size=16 * 16 * 8)  # only the base level's worth of bytes

    with pytest.raises(AlbamCheckFailure) as excinfo:
        DDSHeader.from_dds_bytes(dds, "truncated.dds")

    assert "truncated.dds" in excinfo.value.message
    assert "has 2048" in excinfo.value.details


def test_non_power_of_two_chain_with_halved_block_counts_is_not_rejected():
    # Capcom's own 400x400 DXT1 .tex files with 9 mipmaps hold 106536 bytes,
    # fewer than the 106864 that rounding each level's pixel size up gives.
    DDSHeader.from_dds_bytes(_make_dds(400, 400, 9, data_size=106536), "npot.dds")


def test_non_power_of_two_chain_with_rounded_up_levels_is_not_rejected():
    DDSHeader.from_dds_bytes(_make_dds(400, 400, 9, data_size=106864), "npot.dds")


def test_extra_data_is_not_rejected():
    # e.g. a volume texture whose depth slices follow the first one
    DDSHeader.from_dds_bytes(_make_dds(32, 32, 1, fourcc=b"", data_size=32 * 32 * 4 * 32), "volume.dds")


def test_unsupported_format_is_not_size_checked():
    DDSHeader.from_dds_bytes(_make_dds(64, 64, 7, fourcc=b"ATI2", data_size=16), "bc5.dds")


def test_cubemap_counts_six_faces():
    dds = _make_dds(16, 16, 5, cubemap=True)
    header = DDSHeader.from_dds_bytes(dds, "cube.dds")
    assert header.image_count == 6

    with pytest.raises(AlbamCheckFailure):
        DDSHeader.from_dds_bytes(dds[:len(dds) - 8], "cube.dds")


def test_volume_flag_is_not_a_cubemap():
    header = DDSHeader.from_dds_bytes(_make_dds(16, 16, 1), "flat.dds")
    header.dwCaps2 = DDSHeader.DDSCAPS2_VOLUME

    assert header.image_count == 1
