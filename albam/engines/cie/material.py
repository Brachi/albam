import bpy
from ...lib.blender import ShaderGroupCompat
from ...registry import blender_registry
from ..mtfw.material import BaseMaterialCustomProperties
from .textures import _process_tpls, _create_blender_image_from_tex

REUHD_SHADER_NODEGROUP_NAME = "RE4 UHD shader"


def build_blender_materials(bl_mesh, bin):
    app_id = "re4uhd"
    _create_cie_shader()
    for mat_i, mat in enumerate(bin.materials):
        mat_name = bl_mesh.name + "_" + str(mat_i).zfill(3)
        blender_material = bpy.data.materials.new(name=mat_name)
        albam_custom_props = blender_material.albam_custom_properties
        custom_props_top_level = albam_custom_props.get_custom_properties_for_appid(app_id)
        custom_props_top_level.copy_custom_properties_from(mat)
        blender_material.use_nodes = True
        blender_material.blend_method = "CLIP"

        node_to_delete = None
        for node in blender_material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node_to_delete = node
                blender_material.node_tree.nodes.remove(node_to_delete)
                break

        shader_node_group = blender_material.node_tree.nodes.new("ShaderNodeGroup")
        shader_node_group.node_tree = bpy.data.node_groups["RE4 UHD shader"]
        shader_node_group.name = "RE4 UHD shader group"
        shader_node_group.width = 300

        for node in blender_material.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                material_output = node
                break
        material_output.location = (400, 0)

        link = blender_material.node_tree.links.new
        link(shader_node_group.outputs[0], material_output.inputs[0])

        selected_tpl = bpy.context.scene.albam.import_options_bin.tpl_file_id
        # textures_db = _process_tpls(bin, bin_root_id)
        textures_db = _process_tpls(selected_tpl)
        if textures_db:
            diffuse_map = _get_texture_from_db(textures_db, mat.diffuse_map)
            bump_map = _get_texture_from_db(textures_db, mat.bump_map)
            opacity_map = _get_texture_from_db(textures_db, mat.opacity_map)
            # specular_map = _get_texture_from_db(textures_db, mat.generic_specular_map)
            specular_map = None  # looks like it's not used
            special_map = _get_texture_from_db(textures_db, mat.custom_specular_map)

            tex_code_mapper = {
                1: diffuse_map,
                2: bump_map,
                3: opacity_map,
                4: specular_map,
                5: special_map,
            }
            for tex_code, tex in tex_code_mapper.items():
                if tex:
                    blender_texture_node = blender_material.node_tree.nodes.new("ShaderNodeTexImage")
                    bl_image = _create_blender_image_from_tex(tex)
                    blender_texture_node.image = bl_image
                    if tex_code == 1:
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Diffuse BM"])
                        blender_texture_node.location = (-300, 350)
                    if tex_code == 2:
                        blender_texture_node.location = (-300, 0)
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Normal NM"])
                        link(blender_texture_node.outputs["Alpha"], shader_node_group.inputs["Alpha NM"])
                    if tex_code == 3:
                        blender_texture_node.location = (-600, 350)
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Alpha BM"])
                    if tex_code == 4:
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Specular MM"])
                        blender_texture_node.location = (-300, -350)
                    if tex_code == 5:
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Special MM"])
                        blender_texture_node.location = (-300, -700)

        bl_mesh.materials.append(blender_material)


def _get_texture_from_db(tex_db, tex_index):
    if tex_index == 255:
        return None
    return tex_db[tex_index] if 0 <= tex_index < len(tex_db) else None


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


@blender_registry.register_custom_properties_material("bin_cie_material", ("re4uhd",))
@blender_registry.register_blender_prop
class BinCIEMaterialCustomProperties(BaseMaterialCustomProperties):
    unk_min_11: bpy.props.IntProperty(name="Unk Min 11", default=0, options=set())
    unk_min_10: bpy.props.IntProperty(name="Unk Min 10", default=0, options=set())
    unk_min_09: bpy.props.IntProperty(name="Unk Min 09", default=0, options=set())
    unk_min_08: bpy.props.IntProperty(name="Unk Min 08", default=0, options=set())
    unk_min_07: bpy.props.IntProperty(name="Unk Min 07", default=0, options=set())
    unk_min_06: bpy.props.IntProperty(name="Unk Min 06", default=0, options=set())
    unk_min_05: bpy.props.IntProperty(name="Unk Min 05", default=0, options=set())
    unk_min_04: bpy.props.IntProperty(name="Unk Min 04", default=0, options=set())
    unk_min_03: bpy.props.IntProperty(name="Unk Min 03", default=0, options=set())
    unk_min_02: bpy.props.IntProperty(name="Unk Min 02", default=0, options=set())
    unk_min_01: bpy.props.IntProperty(name="Unk Min 01", default=0, options=set())
    material_flag: bpy.props.IntProperty(name="Material Flag", default=0, options=set())
    intensity_specular_r: bpy.props.IntProperty(name="Specular intensity R", default=0, options=set())
    intensity_specular_g: bpy.props.IntProperty(name="Specular intensity G", default=0, options=set())
    intensity_specular_b: bpy.props.IntProperty(name="Specular intensity B", default=0, options=set())
    unk_00: bpy.props.IntProperty(name="Unk 00", default=0, options=set())
    unk_01: bpy.props.IntProperty(name="Unk 01", default=0, options=set())
    specular_scale: bpy.props.IntProperty(name="Specular Scale", default=0, options=set())
    unk_02: bpy.props.IntProperty(name="Unk 02", default=0, options=set())
