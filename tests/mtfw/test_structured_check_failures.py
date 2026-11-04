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


def _pack_dxt1(bl_im, block):
    from albam.lib.dds import DDSHeader

    header = DDSHeader(dwWidth=4, dwHeight=4, pixelfmt_dwFourCC=b"DXT1", dwMipMapCount=1)
    header.set_constants()
    header.set_variables(compressed=True)
    data = bytes(header) + block
    bl_im.pack(data=data, data_len=len(data))


@pytest.mark.parametrize("same_pixels", [True, False])
def test_serialize_textures_same_relative_path(new_bl_material, same_pixels):
    from albam.engines.mtfw.texture import serialize_textures

    # e.g. pl_VTF and pl_VTF.001, the same game texture imported twice
    shared_path = "common/shared_texture.tex"
    (mat_a, im_a), (mat_b, im_b) = [new_bl_material("re5", shared_path) for _ in range(2)]
    _pack_dxt1(im_a, b"\x00" * 8)
    _pack_dxt1(im_b, b"\x00" * 8 if same_pixels else b"\xff" * 8)

    if same_pixels:
        exported = serialize_textures("re5", [mat_a, mat_b])
        assert exported[im_a.name]["serialized_vfile"] is exported[im_b.name]["serialized_vfile"]
        return

    with pytest.raises(AlbamCheckFailure) as excinfo:
        serialize_textures("re5", [mat_a, mat_b])
    assert shared_path in excinfo.value.details
    assert "pixel data" in excinfo.value.details


def test_serialize_textures_accepts_images_without_relative_path(new_bl_material):
    from albam.engines.mtfw.texture import serialize_textures

    # with no relative path, each image is exported under its own name
    bl_mats = [new_bl_material("re5")[0] for _ in range(2)]

    # the images have no file backing them, so serialization fails later when
    # it goes looking for dds data - reaching that point is what this asserts
    with pytest.raises(FileNotFoundError):
        serialize_textures("re5", bl_mats)


@pytest.mark.parametrize("fourcc, prop_format, expected", [
    (b"DXT5", 31, (31, False)),  # the property picks within the DDS's family
    (b"DXT5", 20, (24, True)),   # DXT1 code on DXT5 data: derived from slot + header
    (b"DX10", 31, None),         # nothing to derive from: refused
])
def test_tex157_compression_format_follows_dds_header(fourcc, prop_format, expected):
    from types import SimpleNamespace
    from albam.engines.mtfw.texture import _resolve_compression_format_21
    from albam.lib.dds import DDSHeader

    header = DDSHeader.from_dds_bytes(
        bytes(DDSHeader(id_magic=b"DDS ", dwWidth=4, dwHeight=4, pixelfmt_dwFourCC=fourcc)) + bytes(16), "im")
    link = SimpleNamespace(to_socket=SimpleNamespace(name="Diffuse BM"))
    node = SimpleNamespace(outputs={"Color": SimpleNamespace(links=[link])})
    dict_tex = {"image": SimpleNamespace(name="pl_BM"), "materials": {"mat": (None, node)}}

    if expected is None:
        with pytest.raises(AlbamCheckFailure) as excinfo:
            _resolve_compression_format_21("re1", dict_tex, prop_format, header)
        assert "pl_BM" in excinfo.value.details and "DX10" in excinfo.value.details
        return

    compression_format, warning = _resolve_compression_format_21("re1", dict_tex, prop_format, header)
    assert (compression_format, bool(warning)) == expected
    if warning:
        assert "pl_BM" in warning and str(prop_format) in warning and "DXT5" in warning


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
