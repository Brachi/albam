from binascii import crc32
import io

import bpy
from kaitaistruct import KaitaiStream

from albam.lib.blender import get_bl_materials
from albam.registry import blender_registry
from albam.vfs import VirtualFile
from .defines import get_shader_objects
from .structs.mrl import Mrl
from .texture import (
    assign_textures,
    build_blender_textures,
    serialize_textures,
    TextureType,
    NODE_NAMES_TO_TYPES,
)

# Probably better with app_id
MAPPER_SERIALIZE_FUNCS = {
    156: lambda: _serialize_materials_data_156,
    210: lambda: _serialize_materials_data_21,
    211: lambda: _serialize_materials_data_21,
}

VERSION_USES_MRL = {210, 211}
VERSION_USES_MATERIAL_NAMES = {210}
MRL_DEFAULT_VERSION = 34
MRL_UNK_01 = 0x478ed2d7
MRL_BLEND_STATE_HASH = 0x62B2D176  # TODO: verify in tests always the same or enums
MRL_DEPTH_STENCIL_STATE_HASH = 0xC80A61AE  # TODO: verify
MRL_RASTERIZER_STATE_HASH = 0x108CF1B2  # TODO: verify
MRL_FILLER = 0xDCDC
MRL_PAD = 16
MRL_APPID_USES_ALBEDO2 = {"rev2"}


def build_blender_materials(mod_file_item, context, parsed_mod, name_prefix="material"):
    app_id = mod_file_item.app_id
    materials = {}
    mrl = _infer_mrl(context, mod_file_item)
    if parsed_mod.header.version in VERSION_USES_MRL and not mrl:
        return materials

    textures = build_blender_textures(mod_file_item, context, parsed_mod, mrl)
    if parsed_mod.header.version in VERSION_USES_MRL:
        src_materials = mrl.materials
    else:
        src_materials = parsed_mod.materials_data.materials

    material_names_available = parsed_mod.header.version in VERSION_USES_MATERIAL_NAMES
    mat_inverse_hashes = {}
    if material_names_available:
        mat_inverse_hashes = {
            crc32(mn.encode()) ^ 0xFFFFFFFF : mn for mn in parsed_mod.materials_data.material_names
        }

    _create_mtfw_shader()
    for idx_material, material in enumerate(src_materials):
        default_mat_name = f"{name_prefix}_{str(idx_material).zfill(2)}"
        mat_name_hash = getattr(material, "name_hash_crcjam32", "")
        mat_name = mat_inverse_hashes.get(mat_name_hash, default_mat_name)
        if material_names_available and mat_name == default_mat_name:
            # don't create materials present in the mrl but not referenced
            # by the mod file (will result in un-named materials)
            continue
        blender_material = bpy.data.materials.new(mat_name)
        custom_properties = blender_material.albam_custom_properties.get_appid_custom_properties(app_id)
        if parsed_mod.header.version in VERSION_USES_MRL and material.resources:
            # verified in tests that $Globals and CBMaterial resources are always present
            # see tests.mtfw.test_parsing_mrl::test_global_resources_mandatory
            gr = [r for r in material.resources if r.shader_object_hash == Mrl.ShaderObjectHash.globals][0]
            custom_properties.set_from_source(gr.float_buffer)
        else:
            custom_properties.set_from_source(material)

        blender_material.use_nodes = True
        blender_material.blend_method = "CLIP"
        node_to_delete = blender_material.node_tree.nodes.get("Principled BSDF")
        blender_material.node_tree.nodes.remove(node_to_delete)
        shader_node_group = blender_material.node_tree.nodes.new("ShaderNodeGroup")
        shader_node_group.node_tree = bpy.data.node_groups["MT Framework shader"]
        shader_node_group.name = "MTFrameworkGroup"
        shader_node_group.width = 300
        material_output = blender_material.node_tree.nodes.get("Material Output")
        material_output.location = (400, 0)
        link = blender_material.node_tree.links.new
        link(shader_node_group.outputs[0], material_output.inputs[0])

        assign_textures(material, blender_material, textures, from_mrl=bool(mrl))

        if not bool(mrl):
            materials[idx_material] = blender_material
        else:
            materials[material.name_hash_crcjam32] = blender_material

    return materials


def serialize_materials_data(model_asset, bl_objects, src_mod, dst_mod):

    bl_materials = get_bl_materials(bl_objects)

    exported_textures = serialize_textures(model_asset.app_id, bl_materials)
    serialize_func = MAPPER_SERIALIZE_FUNCS[dst_mod.header.version]()
    materials_data, mrl = serialize_func(model_asset, bl_materials, exported_textures, src_mod, dst_mod)

    return materials_data, mrl, [t["serialized_vfile"] for t in exported_textures.values()]


def _serialize_materials_data_156(model_asset, bl_materials, exported_textures, src_mod, dst_mod):
    app_id = model_asset.app_id
    dst_mod.header.num_materials = len(bl_materials)
    dst_mod.header.num_textures = len(exported_textures)
    dst_mod.materials_data = dst_mod.MaterialsData(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.materials_data.textures = []
    dst_mod.materials_data.materials = []
    exported_materials_map = {}  # <bl_mat.name> : material_id

    for mat_idx, bl_mat in enumerate(sorted(bl_materials, key=lambda x: x.name)):
        mat = dst_mod.Material(_parent=dst_mod.materials_data, _root=dst_mod.materials_data._root)
        custom_properties = bl_mat.albam_custom_properties.get_appid_custom_properties(app_id)
        custom_properties.set_to_dest(mat)
        mat.use_8_bones = 0  # limited before export

        tex_types = _gather_tex_types(bl_mat, exported_textures, dst_mod.materials_data.textures)
        mat.texture_slots = [0] * 8  # texture indices are 1-based. 0 means tex slot is not used
        mat.texture_slots[TextureType.DIFFUSE.value - 1] = tex_types.get(TextureType.DIFFUSE, -1) + 1
        mat.texture_slots[TextureType.NORMAL.value - 1] = tex_types.get(TextureType.NORMAL, -1) + 1
        mat.texture_slots[TextureType.SPECULAR.value - 1] = tex_types.get(TextureType.SPECULAR, -1) + 1
        mat.texture_slots[TextureType.LIGHTMAP.value - 1] = tex_types.get(TextureType.LIGHTMAP, -1) + 1
        mat.texture_slots[TextureType.ALPHAMAP.value - 1] = tex_types.get(TextureType.ALPHAMAP, -1) + 1
        mat.texture_slots[TextureType.ENVMAP.value - 1] = tex_types.get(TextureType.ENVMAP, -1) + 1
        mat.texture_slots[TextureType.NORMAL_DETAIL.value - 1] = (
            tex_types.get(TextureType.NORMAL_DETAIL, -1) + 1)
        dst_mod.materials_data.materials.append(mat)
        exported_materials_map[bl_mat.name] = mat_idx

    dst_mod.materials_data._check()
    return exported_materials_map, None


def _serialize_materials_data_21(model_asset, bl_materials, exported_textures, srcmod, dst_mod):
    dst_mod.header.num_materials = len(bl_materials)
    dst_mod.materials_data = dst_mod.MaterialsData(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.materials_data.material_names = []
    dst_mod.materials_data.material_hashes = []
    exported_materials_map = {}
    app_id = model_asset.app_id

    mrl = Mrl()
    mrl.id_magic = b"MRL\x00"
    mrl.version = MRL_DEFAULT_VERSION
    mrl.unk_01 = MRL_UNK_01
    mrl.textures = []
    mrl.materials = []
    current_commands_offset = 0

    for bl_mat_idx, bl_mat in enumerate(bl_materials):
        material_hash = crc32(bl_mat.name.encode()) ^ 0xFFFFFFFF
        dst_mod.materials_data.material_names.append(bl_mat.name)
        dst_mod.materials_data.material_hashes.append(material_hash)

        mat = mrl.Material(_parent=mrl, _root=mrl._root)
        mat.type_hash = mrl.MaterialType.type_n_draw__material_std
        mat.name_hash_crcjam32 = material_hash
        mat.blend_state_hash = MRL_BLEND_STATE_HASH
        mat.depth_stencil_state_hash = MRL_DEPTH_STENCIL_STATE_HASH
        mat.rasterizer_state_hash = MRL_RASTERIZER_STATE_HASH
        mat.unused = 0xA00DC  # TODO: research
        mat.material_info_flags = [16, 0, 128, 140]  # TODO: research
        mat.unk_nulls = [0, 0, 0, 0]  # TODO: verify in tests
        mat.anim_data_size = 0
        mat.ofs_anim_data = 0

        tex_types = _gather_tex_types(bl_mat, exported_textures, mrl.textures, mrl=mrl)
        # NOTE: taken from some observed REV2 models. Needs more research
        mat.resources = [
            _create_set_flag_resource(app_id, mrl, mat, "FVertexDisplacement"),
            _create_set_flag_resource(app_id, mrl, mat, "FUVTransformPrimary"),
            _create_set_flag_resource(app_id, mrl, mat, "FUVTransformSecondary"),
            _create_set_flag_resource(app_id, mrl, mat, "FUVTransformUnique"),
            _create_set_flag_resource(app_id, mrl, mat, "FUVTransformExtend"),
            _create_set_flag_resource(app_id, mrl, mat, "FOcclusion"),
            *_create_texture_normal_resources_init(mrl, mat, app_id, tex_types),
            _create_cb_resource(mrl, bl_mat, mat, app_id, "$Globals"),
            *_create_texture_normal_resources(mrl, mat, app_id, tex_types),
            *_create_texture_diffuse_resources(mrl, mat, app_id, tex_types),
            _create_set_flag_resource(app_id, mrl, mat, "FTransparency"),
            _create_set_flag_resource(app_id, mrl, mat, "FShininess", "FShininess2"),
            _create_set_flag_resource(app_id, mrl, mat, "FLighting"),
            _create_set_flag_resource(app_id, mrl, mat, "FBRDF"),
            _create_set_flag_resource(app_id, mrl, mat, "FDiffuse"),
            _create_cb_resource(mrl, bl_mat, mat, app_id, "CBMaterial"),
            _create_set_flag_resource(app_id, mrl, mat, "FAmbient", "FAmbientSH"),
            *_create_texture_specular_resources(mrl, mat, app_id, tex_types),
        ]
        mat.num_resources = len(mat.resources)
        resources_size = sum(r.size_ for r in mat.resources)
        padding = -resources_size % MRL_PAD
        float_buffer_sizes = [r.float_buffer.size_ for r in mat.resources if getattr(r, "float_buffer")]
        float_buffers_size = sum(float_buffer_sizes)
        total_resource_size = resources_size + padding + float_buffers_size

        mat.ofs_cmd = current_commands_offset  # will add absolute address later
        mat.cmd_buffer_size = total_resource_size

        float_buffers_current_offs = resources_size + padding
        float_buffer_index = 0
        for r in mat.resources:
            if getattr(r, "float_buffer"):
                float_buffer_size = float_buffer_sizes[float_buffer_index]
                r.value_cmd.ofs_float_buff = float_buffers_current_offs
                float_buffers_current_offs += float_buffer_size
                float_buffer_index += 1

        current_commands_offset += total_resource_size

        exported_materials_map[bl_mat.name] = bl_mat_idx * 16
        exported_materials_map[material_hash] = bl_mat_idx * 16
        mrl.materials.append(mat)

    mrl.num_textures = len(mrl.textures)
    mrl.num_materials = len(mrl.materials)
    mrl.ofs_textures = mrl.ofs_textures_calculated
    mrl.ofs_materials = mrl.ofs_materials_calculated
    for m in mrl.materials:
        m.ofs_cmd += mrl.ofs_resources_calculated
    dst_mod.materials_data._check()
    mrl._check()

    # TODO: size_todo name it "without_cmd_buffers" and use it here
    padding_1 = -mrl.size_todo_ % MRL_PAD
    final_size = mrl.size_todo_ + padding_1 + sum(m.cmd_buffer_size for m in mrl.materials)
    stream = KaitaiStream(io.BytesIO(bytearray(final_size)))
    mrl._write(stream)
    mrl_relative_path = model_asset.relative_path.replace(".mod", ".mrl")
    mrl_vf = VirtualFile(app_id, mrl_relative_path, data_bytes=stream.to_byte_array())

    return exported_materials_map, mrl_vf


def _create_texture_diffuse_resources(mrl, mat, app_id, tex_types):
    # NO Albedo Color Mask for now
    resources = []

    diffuse_texture_index = tex_types.get(TextureType.DIFFUSE, None)
    if diffuse_texture_index is None:
        return resources

    param_name = "FAlbedoMap2" if app_id in MRL_APPID_USES_ALBEDO2 else "FAlbedoMap"
    resource_1 = _create_set_flag_resource(app_id, mrl, mat, "FAlbedo", param_name)
    resource_2 = _create_set_texture_resource(mrl, mat, app_id, diffuse_texture_index + 1, "tAlbedoMap")
    resource_3 = _create_resource_set_sampler_state(app_id, mrl, mat, "SSAlbedoMap")
    resource_4 = _create_set_flag_resource(app_id, mrl, mat, "FUVAlbedoMap", "FUVPrimary")

    return [
        resource_1,
        resource_2,
        resource_3,
        resource_4,
    ]


# FIXME: dedupe
def _create_texture_normal_resources_init(mrl, mat, app_id, tex_types):
    resources = []

    normal_texture_index = tex_types.get(TextureType.NORMAL, None)
    if normal_texture_index is None:
        return resources

    normal_detail_texture_index = tex_types.get(TextureType.NORMAL_DETAIL, None)
    if normal_detail_texture_index is not None:
        param = "FBumpDetailNormalMap"
    else:
        param = "FBumpNormalMap"

    # forcing always Detail
    param = "FBumpDetailNormalMap"

    # Flag FBump already set
    # XXX maybe only for normaldetailmap? Verify
    resource_1 = _create_set_flag_resource(app_id, mrl, mat, "FBump", param)
    return [resource_1]


# FIXME: dedupe
def _create_texture_normal_resources(mrl, mat, app_id, tex_types):
    resources = []

    normal_texture_index = tex_types.get(TextureType.NORMAL, None)
    if normal_texture_index is None:
        return resources

    normal_detail_texture_index = tex_types.get(TextureType.NORMAL_DETAIL, None)
    if normal_detail_texture_index is None:
        normal_detail_texture_index = -1
    resource_2 = _create_set_texture_resource(mrl, mat, app_id, normal_texture_index + 1, "tNormalMap")
    resource_3 = _create_resource_set_sampler_state(app_id, mrl, mat, "SSNormalMap")
    resource_4 = _create_set_flag_resource(app_id, mrl, mat, "FUVNormalMap", "FUVPrimary")
    resource_5 = _create_set_texture_resource(
        mrl, mat, app_id, normal_detail_texture_index + 1, "tDetailNormalMap"
    )
    resource_6 = _create_set_flag_resource(app_id, mrl, mat, "FUVDetailNormalMap", "FUVPrimary")

    return [
        resource_2,
        resource_3,
        resource_4,
        resource_5,
        resource_6
    ]


# FIXME: dedupe
def _create_texture_specular_resources(mrl, mat, app_id, tex_types):
    resources = []

    specular_texture_index = tex_types.get(TextureType.SPECULAR, None)
    if specular_texture_index is None:
        return resources

    # TODO: decide if using version "2" per app
    resource_1 = _create_set_flag_resource(app_id, mrl, mat, "FSpecular", "FSpecular2Map")
    # XXX Not sure if it's associated with specular
    resource_2 = _create_set_flag_resource(app_id, mrl, mat, "FReflect")
    resource_3 = _create_set_texture_resource(mrl, mat, app_id, specular_texture_index + 1, "tSpecularMap")
    resource_4 = _create_resource_set_sampler_state(app_id, mrl, mat, "SSSpecularMap")
    resource_5 = _create_set_flag_resource(app_id, mrl, mat, "FUVSpecularMap", "FUVPrimary")
    resource_6 = _create_set_flag_resource(app_id, mrl, mat, "FChannelSpecularMap")

    return [
        resource_1,
        resource_2,
        resource_3,
        resource_4,
        resource_5,
        resource_6,
        _create_set_flag_resource(app_id, mrl, mat, "FFresnel"),
        _create_set_flag_resource(app_id, mrl, mat, "FEmission"),
        _create_set_flag_resource(app_id, mrl, mat, "FDistortion"),
    ]


def _create_set_texture_resource(mrl, mat, app_id, texture_index, resource_name):
    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[resource_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index

    resource = mrl.ResourceBinding(_parent=mat, _root=mat._root)
    resource.cmd_type = mrl.CmdType.set_texture
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    set_texture = mrl.CmdTexIdx(_parent=resource, _root=resource._root)
    set_texture.tex_idx = texture_index
    resource.value_cmd = set_texture

    return resource


# FIXME: super copy paste with set_flag
def _create_resource_set_sampler_state(app_id, mrl, mat, resource_name, param_name=None):
    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[resource_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index
    shader_obj_name_friendly = shader_obj_data["friendly_name"]

    resource = mrl.ResourceBinding(_parent=mat, _root=mat._root)
    resource.cmd_type = mrl.CmdType.set_sampler_state
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    so = mrl.ShaderObject(_parent=resource, _root=resource._root)
    if param_name is None:
        so.index = shader_obj_index
        so.name_hash = getattr(mrl.ShaderObjectHash, shader_obj_name_friendly)
    else:
        shader_obj_data_2 = shader_objects[param_name]
        shader_obj_index_2 = shader_obj_data_2["apps"][app_id]["shader_object_index"]
        shader_obj_name_friendly_2 = shader_obj_data_2["friendly_name"]
        so.index = shader_obj_index_2
        so.name_hash = getattr(mrl.ShaderObjectHash, shader_obj_name_friendly_2)

    resource.value_cmd = so

    return resource


def _create_cb_resource(mrl, bl_mat, mat, app_id, cb_name):
    known_names = {"$Globals", "CBMaterial"}
    assert cb_name in known_names, cb_name

    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[cb_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index

    resource = mrl.ResourceBinding(_parent=mat, _root=mat._root)
    resource.cmd_type = mrl.CmdType.set_constant_buffer
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    cb_offset = mrl.CmdOfsBuffer(_parent=resource, _root=resource._root)
    cb_offset.ofs_float_buff = 0  # will be set later
    resource.value_cmd = cb_offset

    if cb_name == "$Globals":
        # TODO: parametric type based on app-id. This won't work for app_id "re1"
        float_buffer = mrl.StrRev2CbGlobals(_parent=resource, _root=resource._root)

    else:   # "CBMaterial":
        float_buffer = mrl.StrCbMaterial(_parent=resource, _root=resource._root)

    # we will set some extra attributes, but it's OK since they won't be serialized
    custom_properties = bl_mat.albam_custom_properties.get_appid_custom_properties(app_id)
    custom_properties.set_to_dest(float_buffer)

    float_buffer._check()
    resource.float_buffer = float_buffer

    return resource


def _create_set_flag_resource(app_id, mrl, mat, resource_name, param_name=None):
    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[resource_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index
    shader_obj_name_friendly = shader_obj_data["friendly_name"]

    resource = mrl.ResourceBinding(_parent=mat, _root=mat._root)
    resource.cmd_type = mrl.CmdType.set_flag
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    so = mrl.ShaderObject(_parent=resource, _root=resource._root)
    if param_name is None:
        so.index = shader_obj_index
        so.name_hash = getattr(mrl.ShaderObjectHash, shader_obj_name_friendly)
    else:
        shader_obj_data_2 = shader_objects[param_name]
        shader_obj_index_2 = shader_obj_data_2["apps"][app_id]["shader_object_index"]
        shader_obj_name_friendly_2 = shader_obj_data_2["friendly_name"]
        so.index = shader_obj_index_2
        so.name_hash = getattr(mrl.ShaderObjectHash, shader_obj_name_friendly_2)

    resource.value_cmd = so

    return resource


def _gather_tex_types(bl_mat, exported_textures, textures_list, mrl=None):
    tex_types = {}
    for node in bl_mat.node_tree.nodes:
        if node.type != "TEX_IMAGE":
            continue
        links = node.outputs["Color"].links
        if not links:
            continue
        mtfw_shader_link_name = links[0].to_socket.name
        tex_type = NODE_NAMES_TO_TYPES[mtfw_shader_link_name]
        image_name = node.image.name
        vfile = exported_textures[image_name]["serialized_vfile"]
        relative_path_no_ext = vfile.relative_path.replace(".tex", "")
        if not mrl:
            try:
                real_tex_idx = textures_list.index(relative_path_no_ext)
            except ValueError:
                textures_list.append(relative_path_no_ext)
                real_tex_idx = len(textures_list) - 1
        else:
            try:
                real_tex_idx = [t.texture_path for t in textures_list].index(relative_path_no_ext)
            except ValueError:

                tex = mrl.TextureSlot(_parent=mrl, _root=mrl._root)
                tex.type_hash = mrl.TextureType.type_r_texture
                tex.unk_02 = 0  # TODO: research
                tex.unk_03 = 0  # TODO: research
                tex.texture_path = relative_path_no_ext
                tex.filler = [0xcd] * (64 - len(tex.texture_path) - 1)

                textures_list.append(tex)
                real_tex_idx = len(textures_list) - 1

        tex_types[tex_type] = real_tex_idx
    return tex_types


def _create_mtfw_shader():
    """Creates shader node group to hide all nodes from users under the hood"""
    existing = bpy.data.node_groups.get("MT Framework shader")
    if existing:
        return existing

    shader_group = bpy.data.node_groups.new("MT Framework shader", "ShaderNodeTree")
    group_inputs = shader_group.nodes.new("NodeGroupInput")
    group_inputs.location = (-2000, -200)

    # Create group inputs
    shader_group.inputs.new("NodeSocketColor", "Diffuse BM")
    shader_group.inputs.new("NodeSocketFloat", "Alpha BM")
    shader_group.inputs["Alpha BM"].default_value = 1
    shader_group.inputs.new("NodeSocketColor", "Normal NM")
    shader_group.inputs["Normal NM"].default_value = (1, 0.5, 1, 1)
    shader_group.inputs.new("NodeSocketFloat", "Alpha NM")
    shader_group.inputs["Alpha NM"].default_value = 0.5
    shader_group.inputs.new("NodeSocketColor", "Specular MM")
    shader_group.inputs.new("NodeSocketColor", "Lightmap LM")
    shader_group.inputs.new("NodeSocketInt", "Use Lightmap")
    shader_group.inputs["Use Lightmap"].min_value = 0
    shader_group.inputs["Use Lightmap"].max_value = 1
    shader_group.inputs.new("NodeSocketColor", "Alpha Mask AM")
    shader_group.inputs.new("NodeSocketInt", "Use Alpha Mask")
    shader_group.inputs["Use Alpha Mask"].min_value = 0
    shader_group.inputs["Use Alpha Mask"].max_value = 1
    shader_group.inputs.new("NodeSocketColor", "Environment CM")
    shader_group.inputs.new("NodeSocketColor", "Detail DNM")
    shader_group.inputs["Detail DNM"].default_value = (1, 0.5, 1, 1)
    shader_group.inputs.new("NodeSocketFloat", "Alpha DNM")
    shader_group.inputs["Alpha DNM"].default_value = 0.5
    shader_group.inputs.new("NodeSocketInt", "Use Detail Map")
    shader_group.inputs["Use Detail Map"].min_value = 0
    shader_group.inputs["Use Detail Map"].max_value = 1

    # Create group outputs
    group_outputs = shader_group.nodes.new("NodeGroupOutput")
    group_outputs.location = (300, -90)
    shader_group.outputs.new("NodeSocketShader", "Surface")

    # Shader node
    bsdf_shader = shader_group.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_shader.location = (0, -90)

    # Mix a diffuse map and a lightmap
    multiply_diff_light = shader_group.nodes.new("ShaderNodeMixRGB")
    multiply_diff_light.name = "mult_diff_and_light"
    multiply_diff_light.label = "Multiply with Lightmap"
    multiply_diff_light.blend_type = "MULTIPLY"
    multiply_diff_light.inputs[0].default_value = 0.8
    multiply_diff_light.location = (-450, -100)

    # RGB nodes
    normal_separate = shader_group.nodes.new("ShaderNodeSeparateRGB")
    normal_separate.name = "separate_normal"
    normal_separate.label = "Separate Normal"
    normal_separate.location = (-1700, -950)

    normal_combine = shader_group.nodes.new("ShaderNodeCombineRGB")
    normal_combine.name = "combine_normal"
    normal_combine.label = "Combine Normal"
    normal_combine.location = (-1500, -900)

    detail_separate = shader_group.nodes.new("ShaderNodeSeparateRGB")
    detail_separate.name = "separate_detail"
    detail_separate.label = "Separate Detail"
    detail_separate.location = (-1700, -1100)

    detail_combine = shader_group.nodes.new("ShaderNodeCombineRGB")
    detail_combine.name = "combine_detail"
    detail_combine.label = "Combine Detail"
    detail_combine.location = (-1500, -1050)

    separate_rgb_n = shader_group.nodes.new("ShaderNodeSeparateRGB")
    separate_rgb_n.name = "separate_rgb_n"
    separate_rgb_n.label = "Separate RGB N"
    separate_rgb_n.location = (-1250, -1050)

    separate_rgb_d = shader_group.nodes.new("ShaderNodeSeparateRGB")
    separate_rgb_d.name = "separate_rgb_d"
    separate_rgb_d.label = "Separate RGB D"
    separate_rgb_d.location = (-1250, -1250)

    combine_all_normals = shader_group.nodes.new("ShaderNodeCombineRGB")
    combine_all_normals.name = "combine_all_normals"
    combine_all_normals.label = "Combine All Normals"
    combine_all_normals.location = (-750, -1150)

    # Curve RGB for correct normal map display in blender
    invert_green = shader_group.nodes.new("ShaderNodeRGBCurve")
    invert_green.location = (-250, -1000)
    curve_g = invert_green.mapping.curves[1]
    curve_g.points[0].location = (1, 0)
    curve_g.points[1].location = (0, 1)
    invert_green.mapping.update()

    # Normalize normals nodes
    normalize_normals = shader_group.nodes.new("ShaderNodeVectorMath")
    normalize_normals.operation = "NORMALIZE"
    normalize_normals.name = "normalize_normals"
    normalize_normals.label = "Normalize Normals"
    normalize_normals.location = (-590, -1050)

    # Add nodes
    add_normals_red = shader_group.nodes.new("ShaderNodeMixRGB")
    add_normals_red.blend_type = "ADD"
    add_normals_red.name = "add_normals_red"
    add_normals_red.label = "Add Normals Red"
    add_normals_red.location = (-1000, -980)

    add_normals_green = shader_group.nodes.new("ShaderNodeMixRGB")
    add_normals_green.blend_type = "ADD"
    add_normals_green.name = "add_normals_green"
    add_normals_green.label = "Add Normals Green"
    add_normals_green.location = (-1000, -1200)

    add_normals_blue = shader_group.nodes.new("ShaderNodeMixRGB")
    add_normals_blue.blend_type = "ADD"
    add_normals_blue.name = "add_normals_blue"
    add_normals_blue.label = "Add Normals Blue"
    add_normals_blue.location = (-1000, -1420)

    # Invert node
    invert_spec = shader_group.nodes.new("ShaderNodeInvert")
    invert_spec.location = (-200, -350)

    # Normal node
    normal_map = shader_group.nodes.new("ShaderNodeNormalMap")  # create normal map node
    normal_map.inputs[0].default_value = 1.5
    normal_map.location = (-200, -720)

    # Logic gates
    use_lightmap = shader_group.nodes.new("ShaderNodeMixRGB")
    use_lightmap.name = "switch_lightmap"
    use_lightmap.label = "Lightmap Switcher"
    use_lightmap.location = (-200, -150)

    use_alpha_mask = shader_group.nodes.new("ShaderNodeMixRGB")
    use_alpha_mask.name = "switch_alpha_mask"
    use_alpha_mask.label = "Alpha Mask Switcher"
    use_alpha_mask.location = (-200, -500)

    use_detail_map = shader_group.nodes.new("ShaderNodeMixRGB")
    use_detail_map.name = "switch_detail_map"
    use_detail_map.label = "Detail Mask Switcher"
    use_detail_map.location = (-440, -825)

    # Link nodes
    link = shader_group.links.new

    link(bsdf_shader.outputs[0], group_outputs.inputs[0])
    link(group_inputs.outputs[0], multiply_diff_light.inputs[1])
    link(multiply_diff_light.outputs[0], use_lightmap.inputs[2])
    link(group_inputs.outputs[0], use_lightmap.inputs[1])
    link(use_lightmap.outputs[0], bsdf_shader.inputs[0])
    link(group_inputs.outputs[1], use_alpha_mask.inputs[1])
    link(use_alpha_mask.outputs[0], bsdf_shader.inputs[21])
    link(group_inputs.outputs[2], normal_separate.inputs[0])
    link(normal_separate.outputs[1], normal_combine.inputs[1])
    link(normal_separate.outputs[2], normal_combine.inputs[2])
    link(group_inputs.outputs[3], normal_combine.inputs[0])
    link(normal_combine.outputs[0], use_detail_map.inputs[1])
    link(normal_combine.outputs[0], separate_rgb_n.inputs[0])

    link(group_inputs.outputs[4], invert_spec.inputs[1])
    link(invert_spec.outputs[0], bsdf_shader.inputs[9])
    link(group_inputs.outputs[5], multiply_diff_light.inputs[2])
    link(group_inputs.outputs[6], use_lightmap.inputs[0])
    link(group_inputs.outputs[7], use_alpha_mask.inputs[2])  # use alpha mask > color 2
    link(group_inputs.outputs[8], use_alpha_mask.inputs[0])  # use alpha mask int

    link(group_inputs.outputs[10], detail_separate.inputs[0])
    link(group_inputs.outputs[11], detail_combine.inputs[0])
    link(detail_separate.outputs[1], detail_combine.inputs[1])
    link(detail_separate.outputs[2], detail_combine.inputs[2])
    link(detail_combine.outputs[0], separate_rgb_d.inputs[0])

    link(separate_rgb_n.outputs[0], add_normals_red.inputs[1])
    link(separate_rgb_d.outputs[0], add_normals_red.inputs[2])
    link(separate_rgb_n.outputs[1], add_normals_green.inputs[1])
    link(separate_rgb_d.outputs[1], add_normals_green.inputs[2])
    link(separate_rgb_n.outputs[2], add_normals_blue.inputs[1])
    link(separate_rgb_d.outputs[2], add_normals_blue.inputs[2])
    link(add_normals_red.outputs[0], combine_all_normals.inputs[0])
    link(add_normals_green.outputs[0], combine_all_normals.inputs[1])
    link(add_normals_blue.outputs[0], combine_all_normals.inputs[2])

    link(combine_all_normals.outputs[0], normalize_normals.inputs[0])
    link(normalize_normals.outputs[0], use_detail_map.inputs[2])
    link(use_detail_map.outputs[0], invert_green.inputs[1])
    link(invert_green.outputs[0], normal_map.inputs[1])
    link(normal_map.outputs[0], bsdf_shader.inputs[22])
    link(group_inputs.outputs[12], use_detail_map.inputs[0])

    return shader_group


def _infer_mrl(context, mod_file_item):
    """
    Assuming mrl file is next to the .mod file with
    the same name.
    It's not always like this, e.g. RE6
    """
    mrl_file_id = mod_file_item.name.replace(".mod", ".mrl")
    file_list = context.scene.albam.file_explorer.file_list

    try:
        mrl_file_item = file_list[mrl_file_id]
    except KeyError:
        return

    mrl_bytes = mrl_file_item.get_bytes()
    mrl = Mrl.from_bytes(mrl_bytes)
    mrl._read()
    return mrl


@blender_registry.register_custom_properties_material("mod_156_material", ("re5",))
@blender_registry.register_blender_prop
class Mod156MaterialCustomProperties(bpy.types.PropertyGroup):
    use_translucent: bpy.props.BoolProperty(default=0)
    use_opaque: bpy.props.BoolProperty(default=0)
    unk_flag_03: bpy.props.BoolProperty(default=0)
    unk_flag_04: bpy.props.BoolProperty(default=0)
    unk_flag_05: bpy.props.BoolProperty(default=0)
    unk_flag_06: bpy.props.BoolProperty(default=0)
    unk_flag_07: bpy.props.BoolProperty(default=0)
    unk_flag_08: bpy.props.BoolProperty(default=0)

    unk_flag_09: bpy.props.BoolProperty(default=0)
    unk_flag_10: bpy.props.BoolProperty(default=0)
    unk_flag_11: bpy.props.BoolProperty(default=0)
    unk_flag_12: bpy.props.BoolProperty(default=0)
    unk_flag_13: bpy.props.BoolProperty(default=0)
    unk_flag_14: bpy.props.BoolProperty(default=0)
    unk_flag_15: bpy.props.BoolProperty(default=0)
    use_alpha: bpy.props.BoolProperty(default=0)

    unk_flag_17: bpy.props.BoolProperty(default=0)
    unk_flag_18: bpy.props.BoolProperty(default=0)
    unk_flag_19: bpy.props.BoolProperty(default=0)
    unk_flag_20: bpy.props.BoolProperty(default=0)
    unk_flag_21: bpy.props.BoolProperty(default=0)
    unk_flag_22: bpy.props.BoolProperty(default=0)
    unk_flag_23: bpy.props.BoolProperty(default=0)
    unk_flag_24: bpy.props.BoolProperty(default=0)

    unk_flag_25: bpy.props.BoolProperty(default=0)
    unk_flag_26: bpy.props.BoolProperty(default=0)
    unk_flag_27: bpy.props.BoolProperty(default=0)
    unk_flag_28: bpy.props.BoolProperty(default=0)
    use_8_bones : bpy.props.BoolProperty(default=0)
    unk_flag_30: bpy.props.BoolProperty(default=0)
    unk_flag_31: bpy.props.BoolProperty(default=0)
    unk_flag_32: bpy.props.BoolProperty(default=0)

    unk_flag_33: bpy.props.BoolProperty(default=0)
    unk_flag_34: bpy.props.BoolProperty(default=0)
    unk_flag_35: bpy.props.BoolProperty(default=0)
    unk_flag_36: bpy.props.BoolProperty(default=0)
    unk_flag_37: bpy.props.BoolProperty(default=0)
    unk_flag_38: bpy.props.BoolProperty(default=0)
    unk_flag_39: bpy.props.BoolProperty(default=0)

    unk_flag_40: bpy.props.BoolProperty(default=0)
    unk_flag_41: bpy.props.BoolProperty(default=0)
    unk_flag_42: bpy.props.BoolProperty(default=0)
    unk_flag_43: bpy.props.BoolProperty(default=0)
    unk_flag_44: bpy.props.BoolProperty(default=0)
    unk_flag_45: bpy.props.BoolProperty(default=0)
    unk_flag_46: bpy.props.BoolProperty(default=0)
    unk_flag_47: bpy.props.BoolProperty(default=0)
    unk_flag_48: bpy.props.BoolProperty(default=0)

    unk_01: bpy.props.IntProperty(default=0)
    unk_02: bpy.props.IntProperty(default=0)
    unk_03: bpy.props.IntProperty(default=0)
    unk_04: bpy.props.IntProperty(default=0)
    unk_05: bpy.props.IntProperty(default=0)
    unk_06: bpy.props.IntProperty(default=0)
    unk_07: bpy.props.IntProperty(default=0)
    unk_08: bpy.props.IntProperty(default=0)
    unk_09: bpy.props.IntProperty(default=0)
    unk_param_01: bpy.props.FloatProperty(default=0.0)
    unk_param_02: bpy.props.FloatProperty(default=0.0)
    unk_param_03: bpy.props.FloatProperty(default=0.0)
    unk_param_04: bpy.props.FloatProperty(default=0.0)
    unk_param_05: bpy.props.FloatProperty(default=0.0)
    cubemap_roughness: bpy.props.FloatProperty(default=0.0)
    unk_param_07: bpy.props.FloatProperty(default=0.0)
    unk_param_08: bpy.props.FloatProperty(default=0.0)
    unk_param_09: bpy.props.FloatProperty(default=0.0)
    unk_param_10: bpy.props.FloatProperty(default=0.0)
    unk_param_11: bpy.props.FloatProperty(default=0.0)
    detail_normal_power: bpy.props.FloatProperty(default=0.0)
    unk_param_13: bpy.props.FloatProperty(default=0.0)
    unk_param_14: bpy.props.FloatProperty(default=0.0)
    unk_param_15: bpy.props.FloatProperty(default=0.0)
    unk_param_16: bpy.props.FloatProperty(default=0.0)
    unk_param_17: bpy.props.FloatProperty(default=0.0)
    unk_param_18: bpy.props.FloatProperty(default=0.0)
    unk_param_19: bpy.props.FloatProperty(default=0.0)
    unk_param_20: bpy.props.FloatProperty(default=0.0)
    normal_scale: bpy.props.FloatProperty(default=0.0)
    unk_param_22: bpy.props.FloatProperty(default=0.0)
    unk_param_23: bpy.props.FloatProperty(default=0.0)
    unk_param_24: bpy.props.FloatProperty(default=0.0)
    unk_param_25: bpy.props.FloatProperty(default=0.0)
    unk_param_26: bpy.props.FloatProperty(default=0.0)

    def set_from_source(self, mtfw_material):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            self.copy_attr(mtfw_material, self, attr_name)

    def set_to_dest(self, mtfw_material):
        for attr_name in self.__annotations__:
            self.copy_attr(self, mtfw_material, attr_name)

    @staticmethod
    def copy_attr(src, dst, name):
        # will raise, making sure there's consistency
        src_value = getattr(src, name)
        setattr(dst, name, src_value)


@blender_registry.register_custom_properties_material("mrl_params", ("re1", "rev2"))
@blender_registry.register_blender_prop
class MrlMaterialCustomProperties(bpy.types.PropertyGroup):

    f_alpha_clip_threshold: bpy.props.FloatProperty(default=0)
    f_albedo_color: bpy.props.FloatVectorProperty(default=(1, 1, 1))
    f_albedo_blend_color: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 1))
    f_detail_normal_power: bpy.props.FloatProperty(default=1)
    f_detail_normal_uv_scale: bpy.props.FloatProperty(default=1)
    f_detail_normal2_power: bpy.props.FloatProperty(default=1)
    f_detail_normal2_uv_scale: bpy.props.FloatProperty(default=1)
    f_primary_shift: bpy.props.FloatProperty(default=0)
    f_secondary_shift: bpy.props.FloatProperty()
    f_parallax_factor: bpy.props.FloatProperty()
    f_parallax_self_occlusion: bpy.props.FloatProperty(default=1)
    f_parallax_min_sample: bpy.props.FloatProperty(default=4)
    f_parallax_max_sample: bpy.props.FloatVectorProperty(default=(64, 0, 0))
    f_light_map_color: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 0))
    f_thin_map_color: bpy.props.FloatVectorProperty(default=(1, 1, 1))
    f_thin_scattering: bpy.props.FloatProperty()
    f_screen_uv_scale: bpy.props.FloatVectorProperty(size=2, default=(1, 1))
    f_screen_uv_offset: bpy.props.FloatVectorProperty(size=2)
    f_indirect_offset: bpy.props.FloatVectorProperty(size=2)
    f_indirect_scale: bpy.props.FloatVectorProperty(size=2)
    f_fresnel_schlick: bpy.props.FloatProperty(default=1)
    f_fresnel_schlick_rgb: bpy.props.FloatVectorProperty(default=(1, 1, 1))
    f_specular_color: bpy.props.FloatVectorProperty(default=(0.5, 0.5, 0.5))
    f_shininess: bpy.props.FloatProperty(default=30)
    f_emission_color: bpy.props.FloatVectorProperty(default=(0.5, 0.5, 0.5))
    f_emission_threshold: bpy.props.FloatProperty(default=0.5)
    f_constant_color: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 1))
    f_roughness: bpy.props.FloatProperty(default=1)
    f_roughness_rgb: bpy.props.FloatVectorProperty(default=(0.3, 0.3, 0.3))
    f_anisotoropic_direction: bpy.props.FloatVectorProperty(default=(0, 1, 0))
    f_smoothness: bpy.props.FloatProperty(default=1)
    f_anistropic_uv: bpy.props.FloatVectorProperty(size=2, default=(0.33, 1))
    f_primary_expo: bpy.props.FloatProperty(default=1)
    f_secondary_expo: bpy.props.FloatProperty(default=0.2)
    f_primary_color: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 0))
    f_secondary_color: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 0))
    # REV2 exclusive
    f_albedo_color2: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 0))
    f_specular_color2: bpy.props.FloatVectorProperty(default=(8, 8, 8))
    f_fresnel_schlick2: bpy.props.FloatProperty(default=1)
    f_shininess2: bpy.props.FloatVectorProperty(size=4, default=(500, 0, 0, 0))
    f_transparency_clip_threshold: bpy.props.FloatVectorProperty(size=4, default=(0, 0, 0, 0))
    f_blend_uv: bpy.props.FloatProperty(default=1)
    f_normal_power: bpy.props.FloatVectorProperty(default=(1, 0, 0))
    f_albedo_blend2_color: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 1))
    f_detail_normal_u_v_scale: bpy.props.FloatVectorProperty(size=2, default=(1, 1))
    f_fresnel_legacy: bpy.props.FloatVectorProperty(size=2, default=(1, 1))
    f_normal_mask_pow0: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 1))
    f_normal_mask_pow1: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 1))
    f_normal_mask_pow2: bpy.props.FloatVectorProperty(size=4, default=(1, 1, 1, 1))
    f_texture_blend_rate: bpy.props.FloatVectorProperty(size=4)
    f_texture_blend_color: bpy.props.FloatVectorProperty(size=4)

    # CBMaterial
    f_diffuse_color: bpy.props.FloatVectorProperty(default=(1, 1, 1))
    f_transparency: bpy.props.FloatProperty(default=1)
    f_reflective_color: bpy.props.FloatVectorProperty(default=(1, 1, 1))
    f_transparency_volume: bpy.props.FloatProperty(default=10)
    f_uv_transform: bpy.props.FloatVectorProperty(size=8, default=(1, 0, 0, 0, 0, 1, 0, 0))
    f_uv_transform2: bpy.props.FloatVectorProperty(size=8, default=(1, 0, 0, 0, 0, 1, 0, 0))
    f_uv_transform3: bpy.props.FloatVectorProperty(size=8, default=(1, 0, 0, 0, 0, 1, 0, 0))

    def set_from_source(self, resource):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            try:
                self.copy_attr(resource, self, attr_name)
            except AttributeError:
                # To ignore the extras in either Globals or CBMaterial.
                pass

    def set_to_dest(self, resource):
        for attr_name in self.__annotations__:
            self.copy_attr(self, resource, attr_name)

    @staticmethod
    def copy_attr(src, dst, name):
        # will raise, making sure there's consistency
        src_value = getattr(src, name)
        setattr(dst, name, src_value)
