"""check_dds_textures() used to refuse any non-DDS image outright. It now
encodes it in place instead, picking the DDS format from the texture slot
(see _choose_export_dds_fourcc) and the engine compression_format code from
the texture slot and app_id (see _choose_export_compression_format and
TEX_COMPRESSION). Needs no game data - a small synthetic image and material
are enough to exercise the real decorator end to end.
"""
import bpy
import pytest

from albam.engines.mtfw.texture import check_dds_textures
from albam.exceptions import AlbamCheckFailure
from albam.lib.blender import is_blimage_dds
from albam.lib.dds import DDSHeader


@pytest.fixture
def export_target(request):
    """A root Object with one mesh child, whose material has a single
    TEX_IMAGE node wired into a shader socket named `socket_name` - the same
    shape check_dds_textures() walks on a real export. The image starts out
    packed as a non-DDS (PNG) file, like a texture a user loaded from disk.
    """
    socket_name = getattr(request, "param", "Diffuse BM")
    name = request.node.name

    bl_im = bpy.data.images.new(name, 4, 4, alpha=True)
    bl_im.pixels.foreach_set([1.0, 0.0, 0.0, 1.0] * 16)
    bl_im.file_format = "PNG"
    bl_im.pack()
    bl_im.albam_asset.app_id = "re1"

    bl_mat = bpy.data.materials.new(name)
    if not bl_mat.node_tree:  # created on demand before Blender 5
        bl_mat.use_nodes = True
    im_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
    im_node.image = bl_im
    # A plain node with one of its input sockets renamed to the MTFW
    # shader-group socket name under test - cheaper than building the real
    # "MTFrameworkGroup" node tree just to get a socket called "Normal NM".
    mix_node = bl_mat.node_tree.nodes.new("ShaderNodeMixRGB")
    mix_node.inputs[1].name = socket_name
    bl_mat.node_tree.links.new(im_node.outputs["Color"], mix_node.inputs[1])

    mesh = bpy.data.meshes.new(name)
    mesh.materials.append(bl_mat)
    mesh_ob = bpy.data.objects.new(name + "_mesh", mesh)
    root_ob = bpy.data.objects.new(name + "_root", None)
    mesh_ob.parent = root_ob
    bpy.context.scene.collection.objects.link(root_ob)
    bpy.context.scene.collection.objects.link(mesh_ob)

    yield root_ob, bl_im

    bpy.data.objects.remove(mesh_ob)
    bpy.data.objects.remove(root_ob)
    bpy.data.meshes.remove(mesh)
    bpy.data.materials.remove(bl_mat)
    bpy.data.images.remove(bl_im)


@check_dds_textures
def _fake_export(bl_obj):
    return "exported"


# re1's own TEX_COMPRESSION entry is (24, 20, 19, 31) - note Specular (MM)
# is 19 there, unlike every other game below, which all use 25.
@pytest.mark.parametrize(
    "export_target, expected_fourcc, expected_compression_format",
    [
        ("Normal NM", b"DXT5", 31),
        ("Specular MM", b"DXT1", 19),
        ("Diffuse BM", b"DXT5", 24),  # has an alpha channel
    ],
    indirect=["export_target"],
)
def test_non_dds_image_is_encoded_per_slot(export_target, expected_fourcc, expected_compression_format):
    root_ob, bl_im = export_target
    assert not is_blimage_dds(bl_im)

    result = _fake_export(root_ob)

    assert result == "exported"
    assert is_blimage_dds(bl_im)
    dds_header = DDSHeader.from_bl_image(bl_im)
    assert dds_header.pixelfmt_dwFourCC == expected_fourcc
    # 4x4 -> 4, 2, 1
    assert dds_header.dwMipMapCount == 3

    custom_properties = bl_im.albam_custom_properties.get_custom_properties_for_appid("re1")
    assert custom_properties.compression_format == expected_compression_format


@pytest.mark.parametrize("export_target", ["Specular MM"], indirect=True)
def test_compression_format_is_app_id_specific(export_target):
    """The whole point of keeping TEX_COMPRESSION app_id-aware: re1 alone
    uses 19 for Specular (see test above), where rev2 - same slot, same
    source image - uses 25.
    """
    root_ob, bl_im = export_target
    bl_im.albam_asset.app_id = "rev2"

    _fake_export(root_ob)

    custom_properties = bl_im.albam_custom_properties.get_custom_properties_for_appid("rev2")
    assert custom_properties.compression_format == 25


@pytest.mark.parametrize("export_target", ["Diffuse BM"], indirect=True)
def test_diffuse_without_alpha_is_dxt1(export_target):
    """Same Diffuse BM slot as the alpha case above, but on a source image
    with no alpha channel (depth 24) - `.pixels` always reports RGBA (see
    encode_bl_image_to_dds in lib/dds.py), only `.depth` tells the two apart.
    """
    root_ob, bl_im = export_target
    # alpha=False still leaves bl_im.pixels as RGBA, just with depth 24
    # instead of 32 - swap the image for one built that way instead of
    # mutating bl_im, since image.alpha isn't settable after creation.
    opaque_im = bpy.data.images.new("opaque", 4, 4, alpha=False)
    opaque_im.pixels.foreach_set([0.0, 1.0, 0.0, 1.0] * 16)
    opaque_im.file_format = "PNG"
    opaque_im.pack()
    opaque_im.albam_asset.app_id = bl_im.albam_asset.app_id
    assert opaque_im.depth == 24

    bl_mat = root_ob.children[0].data.materials[0]
    bl_mat.node_tree.nodes["Image Texture"].image = opaque_im

    try:
        result = _fake_export(root_ob)
        assert result == "exported"
        dds_header = DDSHeader.from_bl_image(opaque_im)
        assert dds_header.pixelfmt_dwFourCC == b"DXT1"
        custom_properties = opaque_im.albam_custom_properties.get_custom_properties_for_appid("re1")
        assert custom_properties.compression_format == 20
    finally:
        bpy.data.images.remove(opaque_im)


@pytest.mark.parametrize("export_target", ["Diffuse BM"], indirect=True)
def test_already_dds_image_is_left_untouched(export_target):
    root_ob, bl_im = export_target
    bl_mat = root_ob.children[0].data.materials[0]
    custom_properties = bl_im.albam_custom_properties.get_custom_properties_for_appid("re1")

    # Build a real (tiny) DDS and have the image "already be" that - as if
    # the user had converted and reassigned it externally themselves.
    header = DDSHeader(dwHeight=4, dwWidth=4, dwMipMapCount=1, pixelfmt_dwFourCC=b"DXT1")
    header.set_constants()
    header.set_variables()
    dds_bytes = bytes(header) + b"\x00" * 8
    bl_im.pack(data=dds_bytes, data_len=len(dds_bytes))
    # compression_format is an IntProperty clamped to [0, 43] - 7 is just a
    # sentinel unrelated to any real DXT1/DXT5 code here, to prove it
    # survives untouched.
    custom_properties.compression_format = 7

    assert bl_mat  # keep the material referenced/used

    result = _fake_export(root_ob)

    assert result == "exported"
    assert bytes(bl_im.packed_file.data) == dds_bytes
    assert custom_properties.compression_format == 7


@pytest.mark.parametrize("export_target", ["Diffuse BM"], indirect=True)
def test_encode_failure_raises_albam_check_failure(export_target, monkeypatch):
    import albam.lib.dds as dds_module

    root_ob, bl_im = export_target

    def _boom(*args, **kwargs):
        raise RuntimeError("bc7enc could not encode this image")

    monkeypatch.setattr(dds_module, "pack_dds", _boom)

    with pytest.raises(AlbamCheckFailure) as excinfo:
        _fake_export(root_ob)

    assert bl_im.name in excinfo.value.message
    # the image's own data is untouched by the failed attempt
    assert not is_blimage_dds(bl_im)


@pytest.mark.parametrize("export_target", ["Diffuse BM"], indirect=True)
def test_one_image_failing_does_not_leave_another_half_converted(export_target, monkeypatch):
    """check_dds_textures() plans every image's encode before applying any
    of them - a later image failing must not leave an earlier, successfully
    encoded one actually converted, since the export as a whole still
    aborts.
    """
    import albam.engines.mtfw.texture as texture_module

    root_ob, bl_im = export_target
    bl_mat = root_ob.children[0].data.materials[0]

    other_im = bpy.data.images.new("other", 4, 4, alpha=True)
    other_im.pixels.foreach_set([0.0, 0.0, 1.0, 1.0] * 16)
    other_im.file_format = "PNG"
    other_im.pack()
    other_im.albam_asset.app_id = bl_im.albam_asset.app_id
    other_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
    other_node.image = other_im
    mix_node = bl_mat.node_tree.nodes.new("ShaderNodeMixRGB")
    mix_node.inputs[2].name = "Normal NM"
    bl_mat.node_tree.links.new(other_node.outputs["Color"], mix_node.inputs[2])

    real_plan = texture_module._plan_non_dds_image_encode

    def _plan_or_boom(bl_im_dict):
        if bl_im_dict["image"].name == other_im.name:
            raise RuntimeError("bc7enc could not encode this image")
        return real_plan(bl_im_dict)

    monkeypatch.setattr(texture_module, "_plan_non_dds_image_encode", _plan_or_boom)

    try:
        with pytest.raises(AlbamCheckFailure):
            _fake_export(root_ob)

        # Neither image was actually converted: every plan has to succeed
        # before any of them is applied, regardless of which one failed.
        assert not is_blimage_dds(bl_im)
        assert not is_blimage_dds(other_im)
    finally:
        bpy.data.images.remove(other_im)
