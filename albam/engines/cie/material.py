import bpy
RE4UHD_NORMAL_GROUP_NAME = "RE4 UHD Normal Map"


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
    """
    Build a clean Principled BSDF material with textures wired correctly.
    Compatible with Blender 4.x and 5.x.
    """
    bl_mat.use_nodes = True
    bl_mat.blend_method = "CLIP"
    nodes = bl_mat.node_tree.nodes
    links = bl_mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    diffuse_img = image_cache.get(diffuse_slot)
    if diffuse_img:
        diff = nodes.new("ShaderNodeTexImage")
        diff.image = diffuse_img
        diff.location = (-200, 250)
        links.new(diff.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(diff.outputs["Alpha"], bsdf.inputs["Alpha"])

    bump_img = image_cache.get(bump_slot) if bump_slot >= 0 else None
    if bump_img:
        bump = nodes.new("ShaderNodeTexImage")
        bump.image = bump_img
        bump.image.colorspace_settings.name = "Non-Color"
        bump.location = (-500, -150)

        ng = _get_or_create_normal_group()
        nm_group = nodes.new("ShaderNodeGroup")
        nm_group.node_tree = ng
        nm_group.label = "RE4 UHD Normal"
        nm_group.location = (-100, -150)

        links.new(bump.outputs["Color"], nm_group.inputs["Color"])
        links.new(bump.outputs["Alpha"], nm_group.inputs["Alpha"])
        links.new(nm_group.outputs["Normal"], bsdf.inputs["Normal"])
