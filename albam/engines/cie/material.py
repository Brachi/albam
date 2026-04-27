import bpy
from ...lib.blender import ShaderGroupCompat

# from .textures import _process_tpls
RE4UHD_NORMAL_GROUP_NAME = "RE4 UHD Normal Map"
REUHD_SHADER_NODEGROUP_NAME = "RE4 UHD shader"


def _create_cie_shader():
    """Creates shader node group to hide all nodes from users under the hood

    RE4 UHD stores normals with X in the R channel (G and B are identical to R)
    and Y in the Alpha channel. Z is not stored and must be approximated.
    Using B=1.0 as the Z approximation is accurate for typical surface normals
    and avoids unnecessary math node complexity.

    """
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
    sg.new_socket("Normal NM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.inputs["Normal NM"].default_value = (1, 0.5, 1, 1)
    sg.new_socket("Alpha NM", in_out="INPUT", socket_type="NodeSocketFloat", )
    sg.inputs["Alpha NM"].default_value = 0.5
    sg.new_socket("Specular MM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Special Specular MM", in_out="INPUT", socket_type="NodeSocketColor")

    # Create group outputs
    group_outputs = shader_group.nodes.new("NodeGroupOutput")
    group_outputs.location = (300, -90)
    sg.new_socket("Surface", in_out="OUTPUT", socket_type="NodeSocketShader")

    # Shader node
    bsdf_shader = shader_group.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_shader.location = (0, -90)
    # RGB nodes
    normal_separate = shader_group.nodes.new("ShaderNodeSeparateColor")
    normal_separate.name = "separate_normal"
    normal_separate.label = "Separate Normal"
    normal_separate.location = (-1700, -950)

    normal_combine = shader_group.nodes.new("ShaderNodeCombineColor")
    normal_combine.inputs["Blue"].default_value = 1.0
    normal_combine.name = "combine_normal"
    normal_combine.label = "Combine Normal"
    normal_combine.location = (-1500, -900)

    # Curve RGB for correct normal map display in blender
    invert_green = shader_group.nodes.new("ShaderNodeRGBCurve")
    invert_green.location = (-250, -1000)
    curve_g = invert_green.mapping.curves[1]
    curve_g.points[0].location = (1, 0)
    curve_g.points[1].location = (0, 1)
    invert_green.mapping.update()

    # Invert node
    invert_spec = shader_group.nodes.new("ShaderNodeInvert")
    invert_spec.location = (-200, -350)

    # Normal node
    normal_map = shader_group.nodes.new("ShaderNodeNormalMap")  # create normal map node
    normal_map.inputs[0].default_value = 1.5
    normal_map.location = (-200, -720)

    # Link nodes
    link = shader_group.links.new

    link(bsdf_shader.outputs[0], group_outputs.inputs[0])
    link(group_inputs.outputs["Diffuse BM"], bsdf_shader.inputs["Base Color"])
    link(group_inputs.outputs["Alpha BM"], bsdf_shader.inputs["Alpha"])
    link(normal_map.outputs[0], bsdf_shader.inputs["Normal"])
    link(group_inputs.outputs["Normal NM"], normal_separate.inputs["Color"])
    link(normal_separate.outputs["Red"], normal_combine.inputs["Red"])
    link(group_inputs.outputs["Alpha NM"], normal_combine.inputs["Green"])
    link(normal_combine.outputs[0], invert_green.inputs["Color"])
    link(invert_green.outputs[0], normal_map.inputs[1])
    link(group_inputs.outputs["Specular MM"], invert_spec.inputs["Color"])
    link(invert_spec.outputs["Color"], bsdf_shader.inputs["Roughness"])
