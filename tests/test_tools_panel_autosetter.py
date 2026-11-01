"""Autosetter's texture naming (#276 item 3).

Synthetic: builds its own material/shader/image, no game data needed.
"""

import bpy

from albam.blender_ui.tools_panel import set_image_albam_attr

LOCAL_PATH = "pawn\\pl\\pl00\\model\\"


def _material_with_connected_image(created, image_name, socket_name):
    """A material whose single TEX_IMAGE node's Color output feeds the
    named socket on a throwaway node group - enough for
    blender_texture_to_texture_code to classify it the same way it would a
    real MTFrameworkGroup socket, without building the real shader.
    """
    mat = bpy.data.materials.new("mat")
    mat.use_nodes = True
    created.append(mat)

    group = bpy.data.node_groups.new("fake_shader", "ShaderNodeTree")
    created.append(group)
    group.interface.new_socket(socket_name, in_out="INPUT", socket_type="NodeSocketColor")
    group_node = mat.node_tree.nodes.new("ShaderNodeGroup")
    group_node.node_tree = group

    tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    image = bpy.data.images.new(image_name, 4, 4)
    created.append(image)
    tex_node.image = image
    mat.node_tree.links.new(tex_node.outputs["Color"], group_node.inputs[socket_name])
    return mat, image


def test_autosetter_appends_the_slot_suffix_to_a_fresh_name():
    created = []
    try:
        mat, image = _material_with_connected_image(created, "my_new_diffuse", "Diffuse BM")
        set_image_albam_attr(mat, "re5", LOCAL_PATH)
        assert image.albam_asset.relative_path == LOCAL_PATH + "my_new_diffuse_BM.tex"
    finally:
        _cleanup(created)


def test_autosetter_does_not_double_up_an_already_suffixed_name():
    """A texture re-imported from a real game file already carries its own
    suffix (e.g. "pl0000_BM") - only one that never had one needs it added.
    """
    created = []
    try:
        mat, image = _material_with_connected_image(created, "pl0000_BM", "Diffuse BM")
        set_image_albam_attr(mat, "re5", LOCAL_PATH)
        assert image.albam_asset.relative_path == LOCAL_PATH + "pl0000_BM.tex"
    finally:
        _cleanup(created)


def test_autosetter_leaves_an_unconnected_image_unsuffixed():
    """blender_texture_to_texture_code returns None for a node with no
    outgoing link - the same as any slot type it doesn't classify at all -
    so no suffix is guessed for it, same as before this existed."""
    created = []
    try:
        mat = bpy.data.materials.new("mat")
        mat.use_nodes = True
        created.append(mat)
        tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        image = bpy.data.images.new("loose_image", 4, 4)
        created.append(image)
        tex_node.image = image

        set_image_albam_attr(mat, "re5", LOCAL_PATH)
        assert image.albam_asset.relative_path == LOCAL_PATH + "loose_image.tex"
    finally:
        _cleanup(created)


def _cleanup(created):
    for obj in reversed(created):
        if isinstance(obj, bpy.types.Material):
            bpy.data.materials.remove(obj)
        elif isinstance(obj, bpy.types.NodeTree):
            bpy.data.node_groups.remove(obj)
        elif isinstance(obj, bpy.types.Image):
            bpy.data.images.remove(obj)
