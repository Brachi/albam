"""Conditions caused by the user's scene or file that used to raise a bare
assert/AttributeError instead of AlbamCheckFailure (see #376). All synthetic:
each case only needs just enough bytes/scene state to reach the check, no
game data required.
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


# -- texture.py: images with the wrong app_id ------------------------------

@pytest.fixture
def bl_material_with_image(request):
    name = request.node.name
    bl_mat = bpy.data.materials.new(name)
    if not bl_mat.node_tree:  # created on demand before Blender 5
        bl_mat.use_nodes = True
    im_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
    bl_im = bpy.data.images.new(name, 4, 4)
    im_node.image = bl_im
    bsdf = bl_mat.node_tree.nodes["Principled BSDF"]
    bl_mat.node_tree.links.new(im_node.outputs["Color"], bsdf.inputs["Base Color"])

    yield bl_mat, bl_im

    bpy.data.materials.remove(bl_mat)
    bpy.data.images.remove(bl_im)


def test_serialize_textures_rejects_wrong_appid_image(bl_material_with_image):
    from albam.engines.mtfw.texture import serialize_textures

    bl_mat, bl_im = bl_material_with_image
    bl_im.albam_asset.app_id = "re1"  # exporting for a different app below

    with pytest.raises(AlbamCheckFailure) as excinfo:
        serialize_textures("re5", [bl_mat])

    assert bl_im.name in excinfo.value.details
    assert "re1" in excinfo.value.details


def test_serialize_textures_rejects_duplicated_relative_path(request):
    from albam.engines.mtfw.texture import serialize_textures

    name = request.node.name
    shared_path = "common/shared_texture.tex"
    bl_mats = []
    bl_ims = []
    try:
        for i in range(2):
            mat_name = f"{name}_{i}"
            bl_mat = bpy.data.materials.new(mat_name)
            if not bl_mat.node_tree:  # created on demand before Blender 5
                bl_mat.use_nodes = True
            im_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
            bl_im = bpy.data.images.new(mat_name, 4, 4)
            bl_im.albam_asset.app_id = "re5"
            bl_im.albam_asset.relative_path = shared_path
            im_node.image = bl_im
            bsdf = bl_mat.node_tree.nodes["Principled BSDF"]
            bl_mat.node_tree.links.new(im_node.outputs["Color"], bsdf.inputs["Base Color"])
            bl_mats.append(bl_mat)
            bl_ims.append(bl_im)

        with pytest.raises(AlbamCheckFailure) as excinfo:
            serialize_textures("re5", bl_mats)

        assert shared_path in excinfo.value.details
    finally:
        for bl_mat in bl_mats:
            bpy.data.materials.remove(bl_mat)
        for bl_im in bl_ims:
            bpy.data.images.remove(bl_im)


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


# -- mesh.py: unsupported .mod version -------------------------------------

def test_build_blender_model_rejects_unmapped_mod_version(monkeypatch):
    from albam.engines.mtfw import mesh as mesh_module

    # 156 is a real, otherwise-valid version for re5 - removing its entry
    # from MOD_CLASS_MAPPER simulates a version this build's structs don't
    # know how to parse, the only way to reach this check since
    # MOD_VERSION_APPID_MAPPER already rejects anything truly unknown.
    monkeypatch.delitem(mesh_module.MOD_CLASS_MAPPER, 156)
    mod_bytes = b"MOD" + bytes([0, 156])
    fake_vfile = _FakeVFile("re5", mod_bytes)

    with pytest.raises(AlbamCheckFailure) as excinfo:
        mesh_module.build_blender_model(fake_vfile, context=None)

    assert "156" in excinfo.value.message


# -- collision.py: unsupported .sbc version --------------------------------

def test_load_sbc_rejects_unmapped_version():
    from albam.engines.mtfw.collision import load_sbc

    sbc_bytes = b"SBC" + bytes([7])  # 7 is neither 49 (Sbc156) nor 255 (Sbc21/211)
    fake_file_item = _FakeVFile("re5", sbc_bytes)

    with pytest.raises(AlbamCheckFailure) as excinfo:
        load_sbc(fake_file_item, context=None)

    assert "7" in excinfo.value.message


# -- collision.py: unsupported .sbc variant (Kaitai magic mismatch) -------

def test_load_sbc_rejects_bad_magic_bytes():
    from albam.engines.mtfw.collision import load_sbc

    # Byte 3 is 255, a known version (Sbc21), passing the version check
    # above, but the first 3 bytes aren't "SBC" so Kaitai's own header
    # validation fails - the raw ValidationNotEqualError this check guards.
    sbc_bytes = b"XYZ" + bytes([255])
    fake_file_item = _FakeVFile("re0", sbc_bytes)  # re0 -> Sbc21

    with pytest.raises(AlbamCheckFailure) as excinfo:
        load_sbc(fake_file_item, context=None)

    assert "not supported" in excinfo.value.message


def test_load_sbc_rejects_truncated_file():
    from albam.engines.mtfw.collision import load_sbc

    # Valid magic for Sbc21 ("SBC\xff"), but nothing after it - the header's
    # next field runs out of bytes mid-read, raising Kaitai's own
    # EndOfStreamError instead of ValidationNotEqualError.
    sbc_bytes = b"SBC" + bytes([255])
    fake_file_item = _FakeVFile("re0", sbc_bytes)  # re0 -> Sbc21

    with pytest.raises(AlbamCheckFailure) as excinfo:
        load_sbc(fake_file_item, context=None)

    assert "truncated" in excinfo.value.message


# -- navmesh.py: unsupported game -------------------------------------------

def test_build_navmesh_model_rejects_unsupported_app():
    from albam.engines.mtfw.navmesh import build_navmesh_model

    fake_vfile = _FakeVFile("re6")  # navmesh import only exists for re5

    with pytest.raises(AlbamCheckFailure) as excinfo:
        build_navmesh_model(fake_vfile, context=None)

    assert "re6" in excinfo.value.message


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
