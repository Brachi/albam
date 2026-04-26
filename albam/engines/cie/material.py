import bpy
from ...lib.blender import get_bl_materials, ShaderGroupCompat

# from .textures import _process_tpls
RE4UHD_NORMAL_GROUP_NAME = "RE4 UHD Normal Map"
REUHD_SHADER_NODEGROUP_NAME = "RE4 UHD shader"


def _build_materials(mesh_ob, bin, root_id):
    # textures_db = _process_tpls(root_id)
    for mat in bin.materials:
        print(f"Building material: {mat.name}")
        diffuse_slot = mat.texture_slots[0] if len(mat.texture_slots) > 0 else None
        bump_slot = mat.texture_slots[1] if len(mat.texture_slots) > 1 else None
        opacity_slot = mat.texture_slots[2] if len(mat.texture_slots) > 2 else None

        bl_mat = bpy.data.materials.new(name=mat.name)
        _create_cie_shader(bl_mat, mesh_ob.image_cache, diffuse_slot, bump_slot, opacity_slot)
        mesh_ob.blender_object.data.materials.append(bl_mat)


def _get_or_create_normal_group():
    """
    Create (once) a node group for RE4 UHD's swizzled normal map format.

    RE4 UHD stores normals with X in the R channel (G and B are identical to R)
    and Y in the Alpha channel. Z is not stored and must be approximated.
    Using B=1.0 as the Z approximation is accurate for typical surface normals
    and avoids unnecessary math node complexity.

    Compatible with Blender 4.x and 5.x (no deprecated RGB nodes).
    """
    existing = bpy.data.node_groups.get(RE4UHD_NORMAL_GROUP_NAME)
    if existing:
        return existing

    g = bpy.data.node_groups.new(RE4UHD_NORMAL_GROUP_NAME, "ShaderNodeTree")

    def new_socket(name, in_out, stype):
        if hasattr(g, "interface"):
            return g.interface.new_socket(name=name, in_out=in_out, socket_type=stype)
        col = g.inputs if in_out == "INPUT" else g.outputs
        return col.new(stype, name)

    new_socket("Color",  "INPUT",  "NodeSocketColor")
    new_socket("Alpha",  "INPUT",  "NodeSocketFloat")
    new_socket("Normal", "OUTPUT", "NodeSocketVector")

    def n(node_type, loc):
        nd = g.nodes.new(node_type)
        nd.location = loc
        return nd

    lk = g.links.new

    group_in = n("NodeGroupInput",  (-600, 0))
    group_out = n("NodeGroupOutput", (600, 0))

    # X from Red channel, Y from Alpha, Z approximated as 1.0 (neutral forward)
    sep = n("ShaderNodeSeparateColor", (-350, 0))
    lk(group_in.outputs["Color"], sep.inputs["Color"])

    combine = n("ShaderNodeCombineColor", (0, 0))
    combine.inputs["Blue"].default_value = 1.0
    lk(sep.outputs["Red"],        combine.inputs["Red"])
    lk(group_in.outputs["Alpha"], combine.inputs["Green"])

    nm = n("ShaderNodeNormalMap", (300, 0))
    lk(combine.outputs["Color"], nm.inputs["Color"])
    lk(nm.outputs["Normal"], group_out.inputs["Normal"])

    return g


def _create_cie_shader(bl_mat, image_cache, diffuse_slot, bump_slot, opacity_slot):
    """Creates shader node group to hide all nodes from users under the hood"""
    existing = bpy.data.node_groups.get(REUHD_SHADER_NODEGROUP_NAME)
    if existing:
        return existing

    shader_group = bpy.data.node_groups.new(REUHD_SHADER_NODEGROUP_NAME, "ShaderNodeTree")
    group_inputs = shader_group.nodes.new("NodeGroupInput")
    group_inputs.location = (-2000, -200)
    bl_major, _, _ = bpy.app.version
    compat = "OLD" if bl_major <= 3 else "NEW"

    sg = ShaderGroupCompat(shader_group, compat)
    # Create group inputs
    sg.new_socket("Diffuse BM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Alpha BM", in_out="INPUT", socket_type="NodeSocketFloat")
    sg.inputs["Alpha BM"].default_value = 1
    sg.new_socket("Albedo Blend BM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Albedo Blend 2 BM", in_out="INPUT", socket_type="NodeSocketColor", )
    sg.new_socket("Normal NM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.inputs["Normal NM"].default_value = (1, 0.5, 1, 1)
    sg.new_socket("Alpha NM", in_out="INPUT", socket_type="NodeSocketFloat", )
    sg.inputs["Alpha NM"].default_value = 0.5
    sg.new_socket("Specular MM", in_out="INPUT", socket_type="NodeSocketColor")