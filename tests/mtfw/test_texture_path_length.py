"""An .mrl texture slot stores its path in a fixed 64-byte field, so a
longer path can't be exported. Needs no game data: the check runs before
any texture is serialized.
"""
import pytest

from albam.engines.mtfw.texture import MRL_TEXTURE_PATH_MAX_LEN, serialize_textures
from albam.exceptions import AlbamCheckFailure


@pytest.mark.parametrize("extra_chars", [1, 20])
def test_texture_path_too_long(new_bl_material, extra_chars):
    path = "x" * (MRL_TEXTURE_PATH_MAX_LEN + extra_chars)
    bl_mat, _ = new_bl_material("re1", path + ".tex")

    with pytest.raises(AlbamCheckFailure) as excinfo:
        serialize_textures("re1", [bl_mat])

    assert path in excinfo.value.details


def test_texture_path_at_limit_is_not_rejected(new_bl_material):
    bl_mat, _ = new_bl_material("re1", "x" * MRL_TEXTURE_PATH_MAX_LEN + ".tex")

    # the image has no file backing it, so serialization fails later when it
    # goes looking for dds data - reaching that point is what this asserts
    with pytest.raises(FileNotFoundError):
        serialize_textures("re1", [bl_mat])
