"""An .mrl texture slot stores its path in a fixed 64-byte field, so a
longer path can't be exported. Needs no game data: the check runs before
any texture is serialized.
"""
import bpy
import pytest

from albam.engines.mtfw.texture import MRL_TEXTURE_PATH_MAX_LEN, serialize_textures
from albam.exceptions import AlbamCheckFailure


@pytest.fixture
def bl_material(request):
    """A material with one image node linked to Base Color, so the export
    machinery picks the image up.
    """
    name = request.node.name
    bl_mat = bpy.data.materials.new(name)
    if not bl_mat.node_tree:  # created on demand before Blender 5
        bl_mat.use_nodes = True
    im_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
    bl_im = bpy.data.images.new(name, 4, 4)
    bl_im.albam_asset.app_id = "re1"
    im_node.image = bl_im
    bsdf = bl_mat.node_tree.nodes["Principled BSDF"]
    bl_mat.node_tree.links.new(im_node.outputs["Color"], bsdf.inputs["Base Color"])

    yield bl_mat

    bpy.data.materials.remove(bl_mat)
    bpy.data.images.remove(bl_im)


@pytest.mark.parametrize("extra_chars", [1, 20])
def test_texture_path_too_long(bl_material, extra_chars):
    bl_im = bl_material.node_tree.nodes["Image Texture"].image
    path = "x" * (MRL_TEXTURE_PATH_MAX_LEN + extra_chars)
    bl_im.albam_asset.relative_path = path + ".tex"

    with pytest.raises(AlbamCheckFailure) as excinfo:
        serialize_textures("re1", [bl_material])

    assert path in excinfo.value.details


def test_texture_path_at_limit_is_not_rejected(bl_material):
    bl_im = bl_material.node_tree.nodes["Image Texture"].image
    bl_im.albam_asset.relative_path = "x" * MRL_TEXTURE_PATH_MAX_LEN + ".tex"

    # the image has no file backing it, so serialization fails later when it
    # goes looking for dds data - reaching that point is what this asserts
    with pytest.raises(FileNotFoundError):
        serialize_textures("re1", [bl_material])
