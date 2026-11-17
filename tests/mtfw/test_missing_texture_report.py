"""Regression tests for issue #374: a material referencing a texture not
found in any loaded arc used to only print to the console. build_blender_textures
must instead record it (via texture.record_missing_texture) so the import
operator can warn about it once, at the end of the whole import.

Synthetic, mirroring tests/mtfw/test_root_id_resolution.py: mounts an
in-memory FS missing the referenced texture, rather than depending on real
game archives.
"""
import bpy
import pytest
from fs.memoryfs import MemoryFS
from fs.path import dirname

from albam.engines.mtfw import texture as mtfw_texture

APP_ID = "re5"


def _memory_fs(files):
    mem_fs = MemoryFS()
    for path, data in files.items():
        full_path = "/" + path
        mem_fs.makedirs(dirname(full_path), recreate=True)
        mem_fs.writebytes(full_path, data)
    return mem_fs


class _FakeMaterialsData:
    def __init__(self, textures):
        self.textures = textures


class _FakeParsedMod:
    def __init__(self, textures):
        self.materials_data = _FakeMaterialsData(textures)


@pytest.fixture(autouse=True)
def _reset_missing_textures():
    # Isolates each test from whatever another import (or another test)
    # left behind in the module-level accumulator.
    mtfw_texture.reset_missing_textures()
    yield
    mtfw_texture.reset_missing_textures()


def test_build_blender_textures_records_a_genuinely_missing_texture(mount_vfs_root):
    root_id = mount_vfs_root(APP_ID, _memory_fs({
        "models/dup.mod": b"MOD-BYTES",
    }), display_name="dup.arc")

    textures = mtfw_texture.build_blender_textures(
        APP_ID, bpy.context, _FakeParsedMod(["models/not_here"]), root_id=root_id)

    assert textures == [None]
    assert mtfw_texture.get_missing_textures() == [(APP_ID, "models/not_here")]


def test_build_blender_textures_does_not_record_the_dummy_placeholder(mount_vfs_root):
    root_id = mount_vfs_root(APP_ID, _memory_fs({
        "models/dup.mod": b"MOD-BYTES",
    }), display_name="dup.arc")

    textures = mtfw_texture.build_blender_textures(
        APP_ID, bpy.context, _FakeParsedMod([mtfw_texture.DUMMY_TEXTURE_PATH_PREFIX + "/01"]),
        root_id=root_id)

    assert textures == [None]
    assert mtfw_texture.get_missing_textures() == []


def test_build_blender_textures_deduplicates_the_same_missing_path(mount_vfs_root):
    root_id = mount_vfs_root(APP_ID, _memory_fs({
        "models/dup.mod": b"MOD-BYTES",
    }), display_name="dup.arc")

    mtfw_texture.build_blender_textures(
        APP_ID, bpy.context,
        _FakeParsedMod(["models/not_here", "models/not_here"]),
        root_id=root_id)

    assert mtfw_texture.get_missing_textures() == [(APP_ID, "models/not_here")]


def test_build_missing_textures_report_hints_at_the_known_shared_archive():
    message = mtfw_texture.build_missing_textures_report(
        [("rev2", "models/hair/sheen")])

    assert "1 texture(s)" in message
    assert "models/hair/sheen" in message
    assert "Core.arc" in message


def test_build_missing_textures_report_has_no_hint_for_an_app_without_one():
    message = mtfw_texture.build_missing_textures_report(
        [(APP_ID, "models/foo/bar")])

    assert "Core.arc" not in message
    assert "load it before importing" not in message


def test_build_missing_textures_report_truncates_a_long_list():
    missing = [(APP_ID, f"models/foo/bar{i}") for i in range(8)]

    message = mtfw_texture.build_missing_textures_report(missing)

    assert "8 texture(s)" in message
    assert "+3 more" in message


def test_build_missing_textures_report_is_none_when_nothing_is_missing():
    assert mtfw_texture.build_missing_textures_report([]) is None
