"""Regression tests for issue #294: with two same-named archives mounted,
resolving a .mod's .mrl/.tex through vfs.get_vfile() could silently pick the
wrong archive's copy - file_id is built from app_id + relative path only,
with no root baked in (see get_vfile's own docstring), so a plain lookup
always resolves to whichever root was mounted first.

Self-contained: mounts two in-memory FS roots (via conftest.py's
mount_vfs_root fixture) holding distinct bytes at the same relative path,
rather than depending on real game archives - see conftest.py's
game_fs_root for why nothing else in this package needs that.
"""
import bpy
import pytest
from fs.memoryfs import MemoryFS
from fs.path import dirname

from albam.engines.mtfw import material as mtfw_material
from albam.engines.mtfw import texture as mtfw_texture

APP_ID = "re5"


def _memory_fs(files):
    mem_fs = MemoryFS()
    for path, data in files.items():
        full_path = "/" + path
        mem_fs.makedirs(dirname(full_path), recreate=True)
        mem_fs.writebytes(full_path, data)
    return mem_fs


class _FakeTex:
    """Stands in for a parsed Tex112. Every attribute build_blender_textures
    reads off a real Tex112 (the DDS header fields, then
    Tex112CustomProperties.set_from_source()'s sweep over its own
    annotations) defaults to 0 unless overridden here, which is enough to
    run that real DDS/PropertyGroup code untouched. Only the vfs lookup -
    the thing under test - is what should determine what comes out.
    """

    def __init__(self, **overrides):
        self._overrides = overrides

    def __getattr__(self, name):
        return self._overrides.get(name, 0)


@pytest.fixture
def two_roots_same_path(mount_vfs_root):
    """Two roots, same relative paths inside, distinct bytes - the exact
    setup issue #294 describes ("two same-named archives mounted")."""
    root1 = mount_vfs_root(APP_ID, _memory_fs({
        "models/dup.mod": b"MOD-BYTES-ROOT-1",
        "models/dup.mrl": b"MRL-BYTES-ROOT-1",
        "models/dup.tex": b"TEX-BYTES-ROOT-1",
    }), display_name="dup.arc")
    root2 = mount_vfs_root(APP_ID, _memory_fs({
        "models/dup.mod": b"MOD-BYTES-ROOT-2",
        "models/dup.mrl": b"MRL-BYTES-ROOT-2",
        "models/dup.tex": b"TEX-BYTES-ROOT-2",
    }), display_name="dup.arc")
    return root1, root2


def test_infer_mrl_resolves_through_the_mod_files_own_root(two_roots_same_path, monkeypatch):
    """_infer_mrl() must resolve the .mrl next to the *specific* .mod being
    imported (the second root here), not whichever same-path .mrl happened
    to be mounted first (the first root).
    """
    root1, root2 = two_roots_same_path
    vfs = bpy.context.scene.albam.vfs

    monkeypatch.setattr(
        mtfw_material, "parse",
        lambda cls, data, app_id: _FakeTex(materials=[data], textures=[data]),
    )

    mod_vfile = vfs.get_vfile(APP_ID, "models/dup.mod", root_id=root2.name)
    assert mod_vfile.get_bytes() == b"MOD-BYTES-ROOT-2"

    mrl = mtfw_material._infer_mrl(bpy.context, mod_vfile, APP_ID, root_id=mod_vfile.tree_node.root_id)

    assert mrl is not None
    assert mrl.materials[0] == b"MRL-BYTES-ROOT-2"


def test_build_blender_textures_resolves_through_the_mod_files_own_root(two_roots_same_path, monkeypatch):
    """build_blender_textures() must resolve a .tex through the same root
    the .mod (and its .mrl) came from, not whichever same-path .tex
    happened to be mounted first.
    """
    root1, root2 = two_roots_same_path

    monkeypatch.setattr(
        mtfw_texture, "parse",
        lambda cls, data, app_id: _FakeTex(
            compression_format=14, height=2, width=2,
            num_mipmaps_per_image=1, num_images=1, dds_data=b"\x00\x00\x00\x00",
        ),
    )

    class _FakeMaterialsData:
        textures = ["models/dup"]

    class _FakeParsedMod:
        materials_data = _FakeMaterialsData()

    textures = mtfw_texture.build_blender_textures(
        APP_ID, bpy.context, _FakeParsedMod(), root_id=root2.name)

    assert len(textures) == 1
    bl_image = textures[0]
    assert bl_image is not None
    assert bytes(bl_image.albam_asset.original_bytes) == b"TEX-BYTES-ROOT-2"


def test_infer_mrl_still_falls_back_when_only_reachable_through_another_root(
        two_roots_same_path, monkeypatch):
    """root_id is a preference, not a restriction (see get_vfile's own
    docstring): a shared .mrl mounted as its own archive, reachable only
    through a *different* root than the .mod referencing it, must still
    resolve rather than error out.
    """
    root1, root2 = two_roots_same_path
    vfs = bpy.context.scene.albam.vfs

    monkeypatch.setattr(
        mtfw_material, "parse",
        lambda cls, data, app_id: _FakeTex(materials=[data], textures=[data]),
    )

    # A .mod with no matching .mrl in either root - only reachable through
    # root1's namespace, so root_id="does-not-exist" can never match, and
    # the lookup has to fall back to root1's .mrl instead of raising.
    mod_vfile = vfs.get_vfile(APP_ID, "models/dup.mod", root_id=root1.name)

    mrl = mtfw_material._infer_mrl(bpy.context, mod_vfile, APP_ID, root_id="does-not-exist")

    assert mrl is not None
    assert mrl.materials[0] == b"MRL-BYTES-ROOT-1"
