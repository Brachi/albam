"""Conditions caused by the user's scene or file that raise AlbamCheckFailure
(see #376). All synthetic: each case only needs just enough bytes/scene state
to reach the check, no game data required.
"""
import bpy
import pytest

from albam.exceptions import AlbamCheckFailure


class _FakeVFile:
    """Duck-types just what each function reads before the check under
    test runs: `app_id` and `get_bytes()`.
    """
    def __init__(self, app_id, data=b""):
        self.app_id = app_id
        self._data = data

    def get_bytes(self):
        return self._data


# -- texture.py: image app_id and relative paths ---------------------------

def test_serialize_textures_rejects_wrong_appid_image(new_bl_material):
    from albam.engines.mtfw.texture import serialize_textures

    bl_mat, bl_im = new_bl_material("re1")  # exporting for a different app below

    with pytest.raises(AlbamCheckFailure) as excinfo:
        serialize_textures("re5", [bl_mat])

    assert bl_im.name in excinfo.value.details
    assert "re1" in excinfo.value.details


def test_serialize_textures_rejects_duplicated_relative_path(new_bl_material):
    from albam.engines.mtfw.texture import serialize_textures

    shared_path = "common/shared_texture.tex"
    bl_mats = [new_bl_material("re5", shared_path)[0] for _ in range(2)]

    with pytest.raises(AlbamCheckFailure) as excinfo:
        serialize_textures("re5", bl_mats)

    assert shared_path in excinfo.value.details


def test_serialize_textures_accepts_images_without_relative_path(new_bl_material):
    from albam.engines.mtfw.texture import serialize_textures

    # with no relative path, each image is exported under its own name
    bl_mats = [new_bl_material("re5")[0] for _ in range(2)]

    # the images have no file backing them, so serialization fails later when
    # it goes looking for dds data - reaching that point is what this asserts
    with pytest.raises(FileNotFoundError):
        serialize_textures("re5", bl_mats)


# -- mesh.py: no mesh to export --------------------------------------------

def test_export_mod_rejects_object_with_no_mesh(request, monkeypatch):
    from albam.engines.mtfw import mesh as mesh_module

    # The no-mesh check runs after the source .mod is parsed, so a fake
    # object's empty original_bytes would fail earlier with an unrelated
    # EndOfStreamError; stubbing parse() isolates the check under test.
    monkeypatch.setattr(mesh_module, "parse", lambda *a, **kw: None)

    bl_obj = bpy.data.objects.new(request.node.name, None)
    bl_obj.albam_asset.app_id = "re5"
    bpy.context.scene.collection.objects.link(bl_obj)
    try:
        with pytest.raises(AlbamCheckFailure) as excinfo:
            mesh_module.export_mod(bl_obj)
        assert bl_obj.name in excinfo.value.details
    finally:
        bpy.data.objects.remove(bl_obj, do_unlink=True)


# -- short files ------------------------------------------------------------

@pytest.mark.parametrize("module_name, func_name, app_id", [
    ("collision", "load_sbc", "re5"),
    ("mesh", "build_blender_model", "re5"),
])
def test_import_rejects_file_shorter_than_header(module_name, func_name, app_id):
    import importlib
    module = importlib.import_module(f"albam.engines.mtfw.{module_name}")

    with pytest.raises(AlbamCheckFailure) as excinfo:
        getattr(module, func_name)(_FakeVFile(app_id, b"SB"), context=None)

    assert "truncated" in excinfo.value.message


# -- collision.py: .sbc header checks --------------------------------------

RE0_SBC_HEADER = b"SBC\xff" + (0x781ACA20).to_bytes(4, "little")
RE6_SBC_HEADER = b"SBC\xff" + (0x77CF8DF8).to_bytes(4, "little")
RE5_SBC_HEADER = b"SBC1" + bytes([22, 0, 1, 0])


@pytest.mark.parametrize("app_id, sbc_bytes", [
    ("re0", RE6_SBC_HEADER),  # Sbc21 app, Sbc211 file: misparses as "truncated"
    ("re6", RE0_SBC_HEADER),  # Sbc211 app, Sbc21 file
    ("re0", RE5_SBC_HEADER),  # Sbc21 app, Sbc156 file
])
def test_load_sbc_rejects_file_from_another_app(app_id, sbc_bytes):
    from albam.engines.mtfw.collision import load_sbc

    with pytest.raises(AlbamCheckFailure) as excinfo:
        load_sbc(_FakeVFile(app_id, sbc_bytes + bytes(100)), context=None)

    assert "correct App" in excinfo.value.solution


def test_load_sbc_rejects_bad_magic_bytes():
    from albam.engines.mtfw.collision import load_sbc

    sbc_bytes = b"XYZ\xff" + bytes(100)

    with pytest.raises(AlbamCheckFailure) as excinfo:
        load_sbc(_FakeVFile("re0", sbc_bytes), context=None)

    assert "ID Magic" in excinfo.value.details


def test_load_sbc_rejects_truncated_file():
    from albam.engines.mtfw.collision import load_sbc

    # a valid RE0 header start, but the rest of the header is missing
    with pytest.raises(AlbamCheckFailure) as excinfo:
        load_sbc(_FakeVFile("re0", RE0_SBC_HEADER), context=None)

    assert "truncated" in excinfo.value.message


# -- navmesh.py: no mesh to export ------------------------------------------

def test_export_nav_rejects_object_with_no_mesh(request):
    from albam.engines.mtfw.navmesh import export_nav

    bl_obj = bpy.data.objects.new(request.node.name, None)
    bl_obj.albam_asset.app_id = "re5"
    bpy.context.scene.collection.objects.link(bl_obj)
    try:
        with pytest.raises(AlbamCheckFailure) as excinfo:
            export_nav(bl_obj)
        assert bl_obj.name in excinfo.value.details
    finally:
        bpy.data.objects.remove(bl_obj, do_unlink=True)
