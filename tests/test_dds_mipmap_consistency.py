"""DDSHeader.check_mipmap_consistency() catches a DDS whose header disagrees
with its own pixel data before export ever trusts it - see the docstring on
that method for the raw ConsistencyError crash this replaces. Pure Python:
building the header and its payload synthetically needs no game data or
Blender image.
"""
import pytest

from albam.exceptions import AlbamCheckFailure
from albam.lib.dds import DDSHeader


def _make_header(width, height, mipmap_count, fourcc=b"DXT1", data_size=None):
    header = DDSHeader(
        dwHeight=height,
        dwWidth=width,
        dwMipMapCount=mipmap_count,
        pixelfmt_dwFourCC=fourcc,
    )
    header.set_constants()
    header.set_variables()
    if data_size is None:
        data_size = sum(header.mipmap_sizes) * header.image_count
    header._dds_data = b"\x00" * data_size
    return header


def test_consistent_single_level_is_not_rejected():
    header = _make_header(4, 4, 1)

    header.check_mipmap_consistency(source_name="ok.dds")


def test_consistent_full_mip_chain_is_not_rejected():
    header = _make_header(256, 256, 9)

    header.check_mipmap_consistency(source_name="ok.dds")


def test_zero_mipmaps_is_rejected():
    # The "DDS saved without mipmaps" case: the base level's bytes are
    # there, but the header claims 0 mipmaps instead of 1.
    header = _make_header(4, 4, 1)
    header.dwMipMapCount = 0

    with pytest.raises(AlbamCheckFailure) as excinfo:
        header.check_mipmap_consistency(source_name="no_mips.dds")

    assert "claims 0 mipmaps" in excinfo.value.details
    assert "no_mips.dds" in excinfo.value.message


def test_mipmap_count_taller_than_the_data_is_rejected():
    header = _make_header(4, 4, 2, data_size=8)  # only the base level's worth of bytes

    with pytest.raises(AlbamCheckFailure) as excinfo:
        header.check_mipmap_consistency(source_name="truncated.dds")

    assert "8 bytes" in excinfo.value.details


def test_non_power_of_two_size_with_mipmaps_is_rejected():
    header = _make_header(100, 60, 2)

    with pytest.raises(AlbamCheckFailure) as excinfo:
        header.check_mipmap_consistency(source_name="npot.dds")

    assert "power of two" in excinfo.value.details


def test_non_power_of_two_size_without_mipmaps_is_not_rejected():
    # A single level never needs halving, so there's nothing to check.
    header = _make_header(100, 60, 1)

    header.check_mipmap_consistency(source_name="npot_no_mips.dds")
