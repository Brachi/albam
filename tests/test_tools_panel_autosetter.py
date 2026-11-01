"""Autosetter's texture naming (#276 item 3).

Synthetic: builds its own material/shader/image, no game data needed.
"""

import bpy
import pytest

from albam.blender_ui.tools_panel import set_image_albam_attr

LOCAL_PATH = "pawn\\pl\\pl00\\model\\"


@pytest.fixture
def created():
    objs = []
    yield objs
    # Materials reference node groups and images, so they go first
    for kind, collection in ((bpy.types.Material, bpy.data.materials),
                             (bpy.types.NodeTree, bpy.data.node_groups),
                             (bpy.types.Image, bpy.data.images)):
        for obj in objs:
            if isinstance(obj, kind):
                collection.remove(obj)


def _new_image(created, name):
    image = bpy.data.images.new(name, 4, 4)
    created.append(image)
    return image


def _material(created, wiring):
    """A material with one TEX_IMAGE node per (image, socket_name) pair, each
    node's Color output feeding that socket on a throwaway node group. Enough
    for the Autosetter to classify it the same way it would a real
    MTFrameworkGroup socket, without building the real shader.
    """
    mat = bpy.data.materials.new("mat")
    mat.use_nodes = True
    created.append(mat)

    group = bpy.data.node_groups.new("fake_shader", "ShaderNodeTree")
    created.append(group)
    for socket_name in dict.fromkeys(socket for _, socket in wiring):
        group.interface.new_socket(socket_name, in_out="INPUT", socket_type="NodeSocketColor")
    group_node = mat.node_tree.nodes.new("ShaderNodeGroup")
    group_node.node_tree = group

    for image, socket_name in wiring:
        tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = image
        mat.node_tree.links.new(tex_node.outputs["Color"], group_node.inputs[socket_name])
    return mat


def test_autosetter_appends_the_slot_suffix_to_a_fresh_name(created):
    image = _new_image(created, "my_new_diffuse")
    mat = _material(created, [(image, "Diffuse BM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "my_new_diffuse_BM.tex"


def test_autosetter_does_not_double_up_an_already_suffixed_name(created):
    """A texture re-imported from a real game file already carries its own
    suffix (e.g. "pl0000_BM"), so only one that never had one needs it added.
    """
    image = _new_image(created, "pl0000_BM")
    mat = _material(created, [(image, "Diffuse BM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "pl0000_BM.tex"


def test_autosetter_keeps_a_name_carrying_another_slots_suffix(created):
    image = _new_image(created, "pl0000_BM")
    mat = _material(created, [(image, "Alpha Mask AM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "pl0000_BM.tex"


@pytest.mark.parametrize("sockets", [
    ("Diffuse BM", "Alpha Mask AM"),
    ("Alpha Mask AM", "Diffuse BM"),
])
def test_autosetter_leaves_an_image_in_disagreeing_slots_unsuffixed(created, sockets):
    image = _new_image(created, "body")
    mat = _material(created, [(image, socket) for socket in sockets])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "body.tex"


def test_autosetter_suffixes_an_image_whose_slots_agree(created):
    image = _new_image(created, "detail")
    mat = _material(created, [(image, "Detail DNM"), (image, "Detail 2 DNM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "detail_DNM.tex"


def test_autosetter_skips_a_suffix_that_collides_with_another_image_name(created):
    image = _new_image(created, "body")
    other = _new_image(created, "body_BM")
    mat = _material(created, [(image, "Diffuse BM"), (other, "Diffuse BM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "body.tex"
    assert other.albam_asset.relative_path == LOCAL_PATH + "body_BM.tex"


def test_autosetter_skips_a_suffix_that_collides_with_another_relative_path(created):
    image = _new_image(created, "skin")
    other = _new_image(created, "unrelated")
    other.albam_asset.relative_path = LOCAL_PATH + "skin_BM.tex"
    mat = _material(created, [(image, "Diffuse BM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "skin.tex"


def test_autosetter_strips_only_the_last_extension(created):
    image = _new_image(created, "pl00.body.png")
    mat = _material(created, [(image, "Diffuse BM")])
    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "pl00.body_BM.tex"


def test_autosetter_leaves_an_unconnected_image_unsuffixed(created):
    """An image with no outgoing link has no slot to take a suffix from."""
    mat = bpy.data.materials.new("mat")
    mat.use_nodes = True
    created.append(mat)
    tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    image = _new_image(created, "loose_image")
    tex_node.image = image

    set_image_albam_attr(mat, "re5", LOCAL_PATH)
    assert image.albam_asset.relative_path == LOCAL_PATH + "loose_image.tex"
