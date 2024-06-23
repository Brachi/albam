from binascii import crc32
import functools
import io
import re

import bpy
from kaitaistruct import KaitaiStream

from albam.exceptions import AlbamCheckFailure
from albam.lib.blender import get_bl_materials
from albam.registry import blender_registry
from albam.vfs import VirtualFileData
from .defines import get_shader_objects
from .structs.mrl import Mrl
from .texture import (
    assign_textures,
    build_blender_textures,
    serialize_textures,
    TextureType,
    NODE_NAMES_TO_TYPES,
    TEX_TYPE_MAP_2,

)

MTFW_SHADER_NODEGROUP_NAME = "MT Framework shader"

MAPPER_SERIALIZE_FUNCS = {
    156: lambda: _serialize_materials_data_156,
    210: lambda: _serialize_materials_data_21,
    211: lambda: _serialize_materials_data_21,
}

VERSION_USES_MRL = {210, 211}
VERSION_USES_MATERIAL_NAMES = {210}
MRL_DEFAULT_VERSION = {
    "re0": 34,
    "re1": 34,
    "re6": 33,
    "rev1": 32,
    "rev2": 34,
}
MRL_FILLER = 0xDCDC
MRL_PAD = 16
MRL_UNK_01 = {
    "re0": 0x419a398d,
    "re1": 0x244bbc26,
    "re6": 0x6a5489b8,
    "rev1": 0xe333fde9,
    "rev2": 0x478ed2d7,
}


MRL_CBGLOBALS_MAP = {
    "re0": Mrl.CbGlobals1,
    "re1": Mrl.CbGlobals1,
    "re6": Mrl.CbGlobals3,
    "rev1": Mrl.CbGlobals1,
    "rev2": Mrl.CbGlobals2,
}


MRL_BLEND_STATE_STR = {
    0x62b2d: "BSSolid",
    0x23baf: "BSBlendAlpha",
    0xd3b1d: "BSAddAlpha",
    0xc4064: "BSRevSubAlpha",
}

MRL_DEPTH_STENCIL_STATE_STR = {
    0x7d2f6: "DSZTest",
    0xb8139: "DSZTestWrite",
    0xc80a6: "DSZTestWriteStencilWrite",
    0x30511: "DSZTestStencilWrite",
    0xa967c: "DSZWrite",
}

MRL_RASTERIZER_STATE_STR = {
    0x108cf: "RSMesh",
    0x92333: "RSMeshCN",
    0x2ab01: "RSMeshCF",
    0xc220b: "RSMeshBias1",
    0x573b1: "RSMeshBias2",
    0x24327: "RSMeshBias3",
    0x6d684: "RSMeshBias4",
    0x1e612: "RSMeshBias5",
    0x8b7a8: "RSMeshBias6",
    0x9aaf: "RSMeshBias8",
    0x7aa39: "RSMeshBias9",
    0xb5506: "RSMeshBias10",
    0xc6590: "RSMeshBias11",
    0x5342a: "RSMeshBias12",
}


def build_blender_materials(mod_file_item, context, parsed_mod, name_prefix="material"):
    app_id = mod_file_item.app_id
    materials = {}
    mrl = _infer_mrl(context, mod_file_item, app_id)
    if parsed_mod.header.version in VERSION_USES_MRL and not mrl:
        return materials

    textures = build_blender_textures(app_id, context, parsed_mod, mrl)
    if parsed_mod.header.version in VERSION_USES_MRL:
        src_materials = mrl.materials
    else:
        src_materials = parsed_mod.materials_data.materials

    material_names_available = parsed_mod.header.version in VERSION_USES_MATERIAL_NAMES
    mat_inverse_hashes = {}
    if material_names_available:
        mat_inverse_hashes = {
            crc32(mn.encode()) ^ 0xFFFFFFFF: mn for mn in parsed_mod.materials_data.material_names
        }

    _create_mtfw_shader()
    for idx_material, material in enumerate(src_materials):
        default_mat_name = f"{name_prefix}_{str(idx_material).zfill(2)}"
        mat_name_hash = getattr(material, "name_hash_crcjam32", default_mat_name)
        mat_name = mat_inverse_hashes.get(mat_name_hash, str(mat_name_hash))
        if material_names_available and mat_name == default_mat_name:
            # don't create materials present in the mrl but not referenced
            # by the mod file (will result in un-named materials)
            continue
        blender_material = bpy.data.materials.new(mat_name)
        albam_custom_props = blender_material.albam_custom_properties
        custom_props_top_level = albam_custom_props.get_custom_properties_for_appid(app_id)
        if parsed_mod.header.version in VERSION_USES_MRL:
            blend_state_type = MRL_BLEND_STATE_STR[material.blend_state_hash >> 12]
            depth_stencil_state_type = MRL_DEPTH_STENCIL_STATE_STR[(material.depth_stencil_state_hash >> 12)]
            rasterizer_state_type = MRL_RASTERIZER_STATE_STR[(material.rasterizer_state_hash >> 12)]
            custom_props_top_level.blend_state_type = blend_state_type
            custom_props_top_level.depth_stencil_state_type = depth_stencil_state_type
            custom_props_top_level.rasterizer_state_type = rasterizer_state_type
            custom_props_top_level.unk_flags = material.unk_flags
            custom_props_top_level.unk_01 = material.unk_01
            # verified in tests that $Globals and CBMaterial resources are present if there are resources
            # see tests.mtfw.test_parsing_mrl::test_global_resources_mandatory
            if material.resources:
                _copy_resources_to_bl_mat(app_id, material, blender_material)
        else:
            custom_props_top_level.copy_custom_properties_from(material)

        blender_material.use_nodes = True
        blender_material.blend_method = "CLIP"
        node_to_delete = blender_material.node_tree.nodes.get("Principled BSDF")
        blender_material.node_tree.nodes.remove(node_to_delete)
        shader_node_group = blender_material.node_tree.nodes.new("ShaderNodeGroup")
        shader_node_group.node_tree = bpy.data.node_groups[MTFW_SHADER_NODEGROUP_NAME]
        shader_node_group.name = "MTFrameworkGroup"
        shader_node_group.width = 300
        material_output = blender_material.node_tree.nodes.get("Material Output")
        material_output.location = (400, 0)
        link = blender_material.node_tree.links.new
        link(shader_node_group.outputs[0], material_output.inputs[0])

        assign_textures(material, blender_material, textures, mrl=mrl)

        if not bool(mrl):
            materials[idx_material] = blender_material
        else:
            materials[material.name_hash_crcjam32] = blender_material

    return materials


def _copy_resources_to_bl_mat(app_id, material, blender_material):
    shader_objects = get_shader_objects()
    albam_custom_props = blender_material.albam_custom_properties
    features = (albam_custom_props.get_custom_properties_secondary_for_appid(app_id)["features"])

    def copy_feature(shader_object_enum, custom_prop_name, enabler=None):
        resource = [r for r in material.resources
                    if r.shader_object_hash == getattr(Mrl.ShaderObjectHash, shader_object_enum, None)]
        if resource:
            param = resource[0].value_cmd.name_hash.name
            param = [k for k, v in shader_objects.items() if v["friendly_name"] == param][0]
            setattr(features, custom_prop_name, param)
        if enabler and not resource:
            setattr(features, enabler, False)
        elif enabler and resource:
            setattr(features, enabler, True)

    def copy_float_buffer(buffer_name, custom_prop_name):
        cb = [r for r in material.resources
              if r.shader_object_hash == getattr(Mrl.ShaderObjectHash, buffer_name)]
        if cb:
            cb = cb[0]
        else:
            return
        cb_custom_props = (albam_custom_props
                           .get_custom_properties_secondary_for_appid(app_id)[custom_prop_name])
        cb_custom_props.copy_custom_properties_from(cb.float_buffer.app_specific)

    copy_feature("fvertexdisplacement", "f_vertex_displacement_param")
    copy_feature("fvdgetmask", "f_vd_get_mask_param")
    copy_feature("fvdmaskuvtransform", "f_vd_mask_uv_transform_param")
    copy_feature("fuvtransformsecondary", "f_uv_transform_secondary_param")
    copy_feature("fuvvertexdisplacement", "f_uv_vertex_displacement_param")
    copy_feature("fuvocclusionmap", "f_uv_occlusion_map_param")
    copy_feature("ftransparency", "f_transparency_param")
    copy_feature("fuvtransparencymap", "f_uv_transparency_map_param")
    copy_feature("fspecular", "f_specular_param")
    copy_feature("falbedo", "f_albedo_param")
    copy_feature("fuvalbedomap", "f_uv_albedo_map_param")
    copy_feature("fuvalbedoblendmap", "f_uv_albedo_blend_map_param")
    copy_feature("fuvalbedoblend2map", "f_uv_albedo_blend_2_map_param")
    copy_feature("fbump", "f_bump_param")
    copy_feature("ffresnel", "f_fresnel_param", "f_fresnel_enabled")
    copy_feature("freflect", "f_reflect_param", "f_reflect_enabled")
    copy_feature("fshininess", "f_shininess_param", "f_shininess_enabled")
    copy_feature("fuvnormalmap", "f_uv_normal_map_param")
    copy_feature("fuvtransformprimary", "f_uv_transform_primary_param")
    copy_feature("fuvemissionmap", "f_uv_emission_map_param")
    copy_feature("fuvdetailnormalmap", "f_uv_detail_normal_map_param")
    copy_feature("fuvdetailnormalmap2", "f_uv_detail_normal_map_2_param")
    copy_feature("fbrdf", "f_brdf_param")
    copy_feature("fdiffuse", "f_diffuse_param")
    copy_feature("fambient", "f_ambient_param")
    copy_feature("fuvspecularmap", "f_uv_specular_map_param")
    copy_feature("femission", "f_emission_param")
    copy_feature("focclusion", "f_occlusion_param")
    copy_feature("fdistortion", "f_distortion_param")
    copy_float_buffer("globals", "globals")
    copy_float_buffer("cbmaterial", "cb_material")
    copy_float_buffer("cbcolormask", "cb_color_mask")
    copy_float_buffer("cbvertexdisplacement", "cb_vertex_disp")
    copy_float_buffer("cbvertexdisplacement2", "cb_vertex_disp2")

    ssenvmap = [r for r in material.resources
                if r.shader_object_hash == Mrl.ShaderObjectHash.ssenvmap]
    features.ssenvmap_enabled = bool(ssenvmap)


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
        custom_properties = bl_mat.albam_custom_properties.get_custom_properties_for_appid(app_id)
        custom_properties.copy_custom_properties_to(mat)
        if src_mod.bones_data is not None:
            bl_mat.albam_custom_properties.use_8_bones = 0
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
    export_settings = bpy.context.scene.albam.export_settings

    mrl = Mrl(app_id=app_id)
    mrl.id_magic = b"MRL\x00"
    mrl.version = MRL_DEFAULT_VERSION[app_id]
    mrl.unk_01 = MRL_UNK_01[app_id]
    mrl.textures = []
    mrl.materials = []
    current_commands_offset = 0

    shader_objects = get_shader_objects()

    for bl_mat_idx, bl_mat in enumerate(bl_materials):
        bl_mat_name = bl_mat.name
        if export_settings.remove_duplicate_materials_suffix:
            bl_mat_name = re.sub(r"\.\d\d\d$", "", bl_mat_name)
        try:
            material_hash = int(bl_mat_name)
        except ValueError:
            material_hash = crc32(bl_mat_name.encode()) ^ 0xFFFFFFFF

        dst_mod.materials_data.material_names.append(bl_mat_name)
        dst_mod.materials_data.material_hashes.append(material_hash)

        albam_custom_props = bl_mat.albam_custom_properties
        mrl_params = albam_custom_props.get_custom_properties_for_appid(app_id)
        custom_props_secondary = albam_custom_props.get_custom_properties_secondary_for_appid(app_id)
        blend_state_index = shader_objects[mrl_params.blend_state_type]["apps"][app_id]["shader_object_index"]
        depth_stencil_state_index = shader_objects[mrl_params.depth_stencil_state_type]["apps"][app_id]["shader_object_index"]  # noqa
        rasterizer_state_index = shader_objects[mrl_params.rasterizer_state_type]["apps"][app_id]["shader_object_index"]  # noqa

        mat = mrl.Material(_parent=mrl, _root=mrl._root)
        mat.type_hash = mrl.MaterialType.type_n_draw__material_std
        mat.name_hash_crcjam32 = material_hash
        mat.blend_state_hash = (shader_objects[mrl_params.blend_state_type]["hash"] << 12) + blend_state_index
        mat.depth_stencil_state_hash = (shader_objects[mrl_params.depth_stencil_state_type]["hash"] << 12) + depth_stencil_state_index  # noqa
        mat.rasterizer_state_hash = (shader_objects[mrl_params.rasterizer_state_type]["hash"] << 12) + rasterizer_state_index  # noqa
        mat.unk_01 = mrl_params.unk_01
        mat.unk_flags = mrl_params.unk_flags
        mat.reserved = [0, 0, 0, 0]
        mat.anim_data_size = 0
        mat.ofs_anim_data = 0

        tex_types = _gather_tex_types(bl_mat, exported_textures, mrl.textures, mrl=mrl)
        resources = _create_resources(app_id, tex_types, mat, mrl_params, custom_props_secondary)
        mat.resources = _insert_constant_buffers(resources, app_id, mat, custom_props_secondary)

        mat.num_resources = len(mat.resources)
        resources_size = sum(r.size_ for r in mat.resources)
        padding = -resources_size % MRL_PAD
        float_buffer_sizes = [r.float_buffer.app_specific.size_
                              for r in mat.resources if getattr(r, "float_buffer")]
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
    mrl_vf = VirtualFileData(app_id, mrl_relative_path, data_bytes=stream.to_byte_array())

    return exported_materials_map, mrl_vf


def _insert_constant_buffers(resources, app_id, mrl_mat, custom_props):
    set_constant_buffer = functools.partial(_create_cb_resource, app_id, mrl_mat, custom_props)

    globals_users = {
        # FBump
        'fblend2bumpdetailnormalmap',
        'fbumpdetailnormalmap',
        'fbumpdetailnormalmap2',
        'fbumphair',
        'fbumphairnormal',
        # 'fbumpnormalmap',
        'fbumpnormalmapblendtransparencymap',
        'fbumpparallaxocclusion',
        # FAlbedo
        "falbedomap",
        "falbedomapadd",
        "falbedomapmodulate",
        "fbumpparallaxocclusion"
    }

    cb_material_users = {
        # FDiffuse
        "fdiffuse",
        'fdiffuseconstant',
        'fdiffuselightmap',
        'fdiffuselightmapocclusion',
        'fdiffusesh',
        'fdiffusevertexcolor',
        'fdiffusevertexcolorocclusion',
        "ftransparencyalpha",
        "ftransparencyvolume",
        "fuvtransformoffset",
    }
    cb_color_mask_users = {
        "fcolormaskalbedomapmodulate"
    }

    # calculate insertion index (1 after the first user)
    # and adjust based on position relative to other constant buffers to be inserted
    current_position = 0
    cb_used = {}

    for ri, resource in enumerate(resources):
        if resource.cmd_type != Mrl.CmdType.set_flag:
            continue
        if resource.value_cmd.name_hash.name in globals_users and not cb_used.get("$Globals"):
            pos = current_position
            current_position += 1
            cb_used["$Globals"] = [ri + 1, pos]
        elif resource.value_cmd.name_hash.name in cb_material_users and not cb_used.get("CBMaterial"):
            pos = current_position
            current_position += 1
            cb_used["CBMaterial"] = [ri + 1, pos]
        elif resource.value_cmd.name_hash.name in cb_color_mask_users and not cb_used.get("CBColorMask"):
            pos = current_position
            current_position += 1
            cb_used["CBColorMask"] = [ri + 1, pos]

    for cb_name, (idx, pos) in sorted(cb_used.items(), key=lambda item: item[1][1]):
        resources.insert(idx + pos, set_constant_buffer(cb_name))

    return resources


def _create_resources(app_id, tex_types, mrl_mat, custom_props=None, custom_props_sec=None):

    set_flag = functools.partial(_create_set_flag_resource, app_id, mrl_mat)
    set_sampler_state = functools.partial(_create_set_sampler_state_resource, app_id, mrl_mat)
    set_texture = functools.partial(_create_set_texture_resource, app_id, mrl_mat, tex_types)
    set_constant_buffer = functools.partial(_create_cb_resource, app_id, mrl_mat, custom_props_sec)
    features = custom_props_sec["features"]

    TT = TextureType
    tt = tex_types
    HAS_NORMAL_MAPS = TT.NORMAL in tt or TT.HAIR_SHIFT in tt
    USES_PARALLAX = features.f_bump_param == "FBumpParallaxOcclusion"

    r = [
        set_flag("FVertexDisplacement", features.f_vertex_displacement_param),
        set_constant_buffer("CBVertexDisplacement", onlyif=TT.VERTEX_DISPLACEMENT in tt),
        set_constant_buffer("CBVertexDisplacement2", onlyif=TT.VERTEX_DISPLACEMENT in tt),
        set_flag("FUVVertexDisplacement", features.f_uv_vertex_displacement_param, onlyif=TT.VERTEX_DISPLACEMENT in tt),  # noqa: E501
        set_texture("tVtxDisplacement", onlyif=TT.VERTEX_DISPLACEMENT in tt),
        set_flag("FVDGetMask", features.f_vd_get_mask_param, onlyif=TT.VERTEX_DISPLACEMENT_MASK in tt),
        set_texture("tVtxDispMask", onlyif=TT.VERTEX_DISPLACEMENT_MASK in tt),
        set_flag("FVDMaskUVTransform", features.f_vd_mask_uv_transform_param, onlyif=TT.VERTEX_DISPLACEMENT_MASK in tt),  # noqa: E501

        set_flag("FUVTransformPrimary", features.f_uv_transform_primary_param),
        set_flag("FUVTransformSecondary", features.f_uv_transform_secondary_param),
        set_flag("FUVTransformUnique"),  # always same param
        set_flag("FUVTransformExtend"),  # always same param

        set_flag("FOcclusion", features.f_occlusion_param),
        set_texture("tOcclusionMap", onlyif=TT.OCCLUSION in tt),
        set_flag("FUVOcclusionMap", features.f_uv_occlusion_map_param, onlyif=TT.OCCLUSION in tt),
        set_flag("FChannelOcclusionMap", onlyif=TT.OCCLUSION in tt),

        set_flag("FBump", features.f_bump_param),
        set_flag("FUVNormalMap", features.f_uv_normal_map_param, onlyif=HAS_NORMAL_MAPS and USES_PARALLAX),
        set_texture("tHeightMap", onlyif=TT.HEIGHTMAP in tt),
        set_texture("tNormalMap", onlyif=TT.NORMAL in tt and TT.HAIR_SHIFT not in tt),
        set_texture("tHairShiftMap", onlyif=TT.HAIR_SHIFT in tt),
        set_sampler_state("SSNormalMap", onlyif=HAS_NORMAL_MAPS and not USES_PARALLAX),
        set_flag("FUVNormalMap", features.f_uv_normal_map_param, onlyif=HAS_NORMAL_MAPS and not USES_PARALLAX),  # noqa: E501
        set_texture("tNormalMap", onlyif=TT.NORMAL in tt and TT.HAIR_SHIFT in tt),
        set_texture("tDetailNormalMap", onlyif=TT.NORMAL_DETAIL in tt),
        set_flag("FUVDetailNormalMap", features.f_uv_detail_normal_map_param, onlyif=TT.NORMAL_DETAIL in tt),
        set_texture("tDetailNormalMap2", onlyif=TT.NORMAL_DETAIL_2 in tt),
        set_flag("FUVDetailNormalMap2", features.f_uv_detail_normal_map_2_param, onlyif=TT.NORMAL_DETAIL_2 in tt),  # noqa: E501

        set_flag("FAlbedo", features.f_albedo_param),
        set_texture("tAlbedoMap", onlyif=TT.DIFFUSE in tt),
        set_sampler_state("SSAlbedoMap", onlyif=TT.DIFFUSE in tt),
        set_flag("FUVAlbedoMap", features.f_uv_albedo_map_param, onlyif=TT.DIFFUSE in tt),
        set_texture("tAlbedoBlendMap", onlyif=TT.ALBEDO_BLEND in tt),
        set_flag("FUVAlbedoBlendMap", features.f_uv_albedo_blend_map_param, onlyif=TT.ALBEDO_BLEND in tt),
        set_texture("tAlbedoBlend2Map", onlyif=TT.ALBEDO_BLEND_2 in tt),
        set_flag("FUVAlbedoBlend2Map", features.f_uv_albedo_blend_2_map_param, onlyif=TT.ALBEDO_BLEND_2 in tt),  # noqa: E501

        set_flag("FTransparency", features.f_transparency_param),
        set_texture("tTransparencyMap", onlyif=TT.TRANSPARENCY_MAP in tt),
        set_flag("FUVTransparencyMap", features.f_uv_transparency_map_param, onlyif=TT.TRANSPARENCY_MAP in tt),  # noqa: E501
        set_flag("FChannelTransparencyMap", onlyif=TT.TRANSPARENCY_MAP in tt),

        set_flag("tIndirectMap", onlyif=TT.INDIRECT in tt),
        set_flag("FUVIndirectMap", onlyif=TT.INDIRECT in tt),  # no params found
        set_flag("FUVIndirectSource", onlyif=TT.INDIRECT in tt),  # no params found

        set_flag("FShininess", features.f_shininess_param),
        set_flag("FLighting"),  # no params found
        set_flag("FBRDF", features.f_brdf_param),
        set_flag("FDiffuse", features.f_diffuse_param),

        set_texture("tLightMap", onlyif=TT.LIGHTMAP in tt),
        set_flag("FUVLightMap", "FUVUnique", onlyif=TT.LIGHTMAP in tt),  # same param always

        set_flag("FAmbient", features.f_ambient_param),
        set_flag("FSpecular", features.f_specular_param),

        set_texture("tSphereMap", onlyif=TT.SPHERE in tt),

        set_flag("FReflect", features.f_reflect_param, onlyif=features.f_reflect_enabled),

        set_texture("tEnvMap", onlyif=TT.ENVMAP in tt),
        set_sampler_state("SSEnvMap", onlyif=features.ssenvmap_enabled),

        set_texture("tSpecularMap", onlyif=TT.SPECULAR in tt),
        set_sampler_state("SSSpecularMap", onlyif=TT.SPECULAR in tt),
        set_flag("FUVSpecularMap", features.f_uv_specular_map_param, onlyif=TT.SPECULAR in tt),
        set_flag("FChannelSpecularMap", onlyif=TT.SPECULAR in tt),  # same param always

        set_flag("FFresnel", features.f_fresnel_param, onlyif=features.f_fresnel_enabled),

        set_flag("FEmission", features.f_emission_param),
        set_texture("tEmissionMap", onlyif=TT.EMISSION in tt),
        set_flag("FUVEmissionMap", features.f_uv_emission_map_param, onlyif=TT.EMISSION in tt),
        set_flag("FChannelEmissionMap", onlyif=TT.EMISSION in tt),  # same param always

        set_flag("FDistortion"),
    ]

    r = [item for item in r if item is not None]

    return r


def _create_resource_generic(cmd_type, app_id, mat, resource_name, param_name=None, onlyif=True):
    if onlyif is False:
        return
    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[resource_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index
    shader_obj_name_friendly = shader_obj_data["friendly_name"]

    resource = Mrl.ResourceBinding(_parent=mat, _root=mat._root)
    resource.cmd_type = cmd_type
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    so = Mrl.ShaderObject(_parent=resource, _root=resource._root)
    if not param_name:
        so.index = shader_obj_index
        so.name_hash = getattr(Mrl.ShaderObjectHash, shader_obj_name_friendly)
    else:
        shader_obj_data_2 = shader_objects[param_name]
        shader_obj_index_2 = shader_obj_data_2["apps"][app_id]["shader_object_index"]
        shader_obj_name_friendly_2 = shader_obj_data_2["friendly_name"]
        so.index = shader_obj_index_2
        so.name_hash = getattr(Mrl.ShaderObjectHash, shader_obj_name_friendly_2)

    resource.value_cmd = so

    return resource


_create_set_flag_resource = functools.partial(
    _create_resource_generic, Mrl.CmdType.set_flag)
_create_set_sampler_state_resource = functools.partial(
    _create_resource_generic, Mrl.CmdType.set_sampler_state)


def _create_set_texture_resource(app_id, mat, tex_types, resource_name, onlyif=True):
    if onlyif is False:
        return None
    resource_name_friendly = resource_name.lower()
    target_tex_type = TEX_TYPE_MAP_2[resource_name_friendly]
    texture_index = tex_types[target_tex_type]

    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[resource_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index

    resource = Mrl.ResourceBinding(_parent=mat, _root=mat._root)
    resource.cmd_type = Mrl.CmdType.set_texture
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    set_texture = Mrl.CmdTexIdx(_parent=resource, _root=resource._root)
    set_texture.tex_idx = texture_index + 1  # zero is used for "dummy texture"
    resource.value_cmd = set_texture

    return resource


def _create_cb_resource(app_id, mrl_mat, custom_props, cb_name, onlyif=True):
    if onlyif is False:
        return None
    known_names = {
        "$Globals", "CBMaterial", "CBColorMask",
        "CBVertexDisplacement", "CBVertexDisplacement2",
    }
    assert cb_name in known_names, cb_name

    shader_objects = get_shader_objects()
    shader_obj_data = shader_objects[cb_name]

    shader_obj_index = shader_obj_data["apps"][app_id]["shader_object_index"]
    shader_obj_name_hash = shader_obj_data["hash"]
    shader_obj_id = (shader_obj_name_hash << 12) + shader_obj_index

    resource = Mrl.ResourceBinding(_parent=mrl_mat, _root=mrl_mat._root)
    resource.cmd_type = Mrl.CmdType.set_constant_buffer
    resource.unused = MRL_FILLER
    resource.shader_obj_idx = shader_obj_index
    resource.shader_object_id = shader_obj_id

    cb_offset = Mrl.CmdOfsBuffer(_parent=resource, _root=resource._root)
    cb_offset.ofs_float_buff = 0  # will be set later
    resource.value_cmd = cb_offset

    if cb_name == "$Globals":
        float_buffer_parent = Mrl.CbGlobals(_parent=resource, _root=resource._root)
        # TODO: app_id mapping
        CbGlobalsCls = MRL_CBGLOBALS_MAP[app_id]
        float_buffer = CbGlobalsCls(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["globals"]

    elif cb_name == "CBMaterial":
        float_buffer_parent = Mrl.CbMaterial(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbMaterial1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_material"]

    elif cb_name == "CBColorMask":
        float_buffer_parent = Mrl.CbColorMask(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbColorMask1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_color_mask"]

    elif cb_name == "CBVertexDisplacement":
        float_buffer_parent = Mrl.CbVertexDisplacement(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbVertexDisplacement1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_vertex_disp"]

    elif cb_name == "CBVertexDisplacement2":
        float_buffer_parent = Mrl.CbVertexDisplacement2(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbVertexDisplacement21(_parent=float_buffer_parent, _root=float_buffer_parent._root)  # noqa: E501
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_vertex_disp2"]

    float_buffer_custom_props.copy_custom_properties_to(float_buffer)
    float_buffer_parent._check()
    float_buffer._check()
    resource.float_buffer = float_buffer_parent

    return resource


def _gather_tex_types(bl_mat, exported_textures, textures_list, mrl=None):
    tex_types = {}
    image_nodes = [node for node in bl_mat.node_tree.nodes if node.type == "TEX_IMAGE"]
    for im_node in image_nodes:
        links = im_node.outputs["Color"].links
        if not links:
            continue
        mtfw_shader_link_name = links[0].to_socket.name
        tex_type = NODE_NAMES_TO_TYPES[mtfw_shader_link_name]
        if not im_node.image:
            # dummy texture, index 0
            tex_types[tex_type] = -1
            continue
        image_name = im_node.image.name
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
    existing = bpy.data.node_groups.get(MTFW_SHADER_NODEGROUP_NAME)
    if existing:
        return existing

    shader_group = bpy.data.node_groups.new(MTFW_SHADER_NODEGROUP_NAME, "ShaderNodeTree")
    group_inputs = shader_group.nodes.new("NodeGroupInput")
    group_inputs.location = (-2000, -200)

    # Create group inputs
    shader_group.inputs.new("NodeSocketColor", "Diffuse BM")
    shader_group.inputs.new("NodeSocketFloat", "Alpha BM")
    shader_group.inputs["Alpha BM"].default_value = 1
    shader_group.inputs.new("NodeSocketColor", "Albedo Blend BM")
    shader_group.inputs.new("NodeSocketColor", "Albedo Blend 2 BM")
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
    shader_group.inputs.new("NodeSocketColor", "Detail 2 DNM")
    shader_group.inputs["Detail DNM"].default_value = (1, 0.5, 1, 1)
    shader_group.inputs["Detail 2 DNM"].default_value = (1, 0.5, 1, 1)
    shader_group.inputs.new("NodeSocketFloat", "Alpha DNM")
    shader_group.inputs["Alpha DNM"].default_value = 0.5
    shader_group.inputs.new("NodeSocketInt", "Use Detail Map")
    shader_group.inputs["Use Detail Map"].min_value = 0
    shader_group.inputs["Use Detail Map"].max_value = 1
    shader_group.inputs.new("NodeSocketColor", "Special Map")
    shader_group.inputs.new("NodeSocketString", "Special Map type")
    shader_group.inputs.new("NodeSocketColor", "Vertex Displacement")  # TODO: Try to use it in Blender
    shader_group.inputs.new("NodeSocketColor", "Vertex Displacement Mask")  # TODO: Try to use it in Blender
    shader_group.inputs.new("NodeSocketColor", "Hair Shift")  # TODO: Try to use it in Blender
    shader_group.inputs.new("NodeSocketColor", "Height Map")  # TODO: Try to use it in Blender
    shader_group.inputs.new("NodeSocketColor", "Emission")  # TODO: Try to use it in Blender

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
    link(group_inputs.outputs["Diffuse BM"], multiply_diff_light.inputs[1])
    link(multiply_diff_light.outputs[0], use_lightmap.inputs[2])
    link(group_inputs.outputs["Diffuse BM"], use_lightmap.inputs[1])
    link(use_lightmap.outputs[0], bsdf_shader.inputs[0])
    link(group_inputs.outputs["Alpha BM"], use_alpha_mask.inputs[1])
    link(use_alpha_mask.outputs[0], bsdf_shader.inputs[21])
    link(group_inputs.outputs["Normal NM"], normal_separate.inputs[0])
    link(normal_separate.outputs[1], normal_combine.inputs[1])
    link(normal_separate.outputs[2], normal_combine.inputs[2])
    link(group_inputs.outputs["Alpha NM"], normal_combine.inputs[0])
    link(normal_combine.outputs[0], use_detail_map.inputs[1])
    link(normal_combine.outputs[0], separate_rgb_n.inputs[0])

    link(group_inputs.outputs["Specular MM"], invert_spec.inputs[1])
    link(invert_spec.outputs[0], bsdf_shader.inputs[9])
    link(group_inputs.outputs["Lightmap LM"], multiply_diff_light.inputs[2])
    link(group_inputs.outputs["Use Lightmap"], use_lightmap.inputs[0])
    link(group_inputs.outputs["Alpha Mask AM"], use_alpha_mask.inputs[2])  # use alpha mask > color 2
    link(group_inputs.outputs["Use Alpha Mask"], use_alpha_mask.inputs[0])  # use alpha mask int

    link(group_inputs.outputs["Detail DNM"], detail_separate.inputs[0])
    link(group_inputs.outputs["Alpha DNM"], detail_combine.inputs[0])
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
    link(group_inputs.outputs["Use Detail Map"], use_detail_map.inputs[0])

    return shader_group


def _infer_mrl(context, mod_vfile, app_id):
    """
    Assuming mrl file is next to the .mod file with
    the same name. Or try with different suffixes
    """
    vfs = context.scene.albam.vfs
    base = str(mod_vfile.relative_path_windows_no_ext)
    suffixes = [".mrl", "_0.mrl", "_1.mrl", "_2.mrl", "_3.mrl"]
    mrl = None

    for suffix in suffixes:
        try:
            mrl_vfile = vfs.get_vfile(app_id, base + suffix)
            mrl_bytes = mrl_vfile.get_bytes()
            mrl = Mrl(app_id, KaitaiStream(io.BytesIO(mrl_bytes)))
            mrl._read()
            assert mrl.materials and mrl.textures
            break
        except KeyError:
            pass
        except AssertionError:
            pass

    return mrl


def check_mtfw_shader_group(func):
    """
    Function decorator that checks if all the meshes of a bl_object
    have materials that contain the "MT Framework shader" node group.
    Raises AlbamCheckFailure with instructions on how to fix it for the affected
    materials
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bl_objects = [a for a in args if isinstance(a, bpy.types.Object)]
        if not bl_objects:
            result = func(*args, **kwargs)
        # No more than one root object in export functions
        meshes = [c for c in bl_objects[0].children_recursive if c.type == "MESH"]
        materials = get_bl_materials(meshes)
        checks = [_has_mtfw_shader_group(m) for m in materials]
        if not all(checks):
            data = sorted(mat.name for mat, status in zip(materials, checks) if status is False)
            raise AlbamCheckFailure(
                f"Some materials are not using the '{MTFW_SHADER_NODEGROUP_NAME}' group",
                details=f"materials: {data}",
                solution="In the Shader Editor, Add -> Group -> MT Framework shader for the materials listed")
        result = func(*args, **kwargs)

        return result
    return wrapper


def _has_mtfw_shader_group(bl_mat):
    mtfw_shader_group = None
    try:
        mtfw_shader_group = bpy.data.node_groups[MTFW_SHADER_NODEGROUP_NAME]
    except KeyError:
        return False
    existing_mtfw_shader_groups = [
        n for n in bl_mat.node_tree.nodes if isinstance(n, bpy.types.ShaderNodeGroup) and
        n.node_tree is mtfw_shader_group
    ]
    return bool(existing_mtfw_shader_groups)


@blender_registry.register_custom_properties_material("mod_156_material", ("re5",))
@blender_registry.register_blender_prop
class Mod156MaterialCustomProperties(bpy.types.PropertyGroup):
    surface_unk: bpy.props.BoolProperty(default=0)
    surface_opaque: bpy.props.BoolProperty(default=0)
    use_bridge_lines: bpy.props.BoolProperty(default=0)
    unk_flag_04: bpy.props.BoolProperty(default=0)
    unk_flag_05: bpy.props.BoolProperty(default=0)
    use_alpha_clip: bpy.props.BoolProperty(default=0)
    use_opaque: bpy.props.BoolProperty(default=0)
    use_translusent: bpy.props.BoolProperty(default=0)

    use_alpha_transparency: bpy.props.BoolProperty(default=0)
    unk_flag_10: bpy.props.BoolProperty(default=0)
    unk_flag_11: bpy.props.BoolProperty(default=0)
    unk_flag_12: bpy.props.BoolProperty(default=0)
    unk_flag_13: bpy.props.BoolProperty(default=0)
    unk_flag_14: bpy.props.BoolProperty(default=0)
    unk_flag_15: bpy.props.BoolProperty(default=0)
    unk_flag_16: bpy.props.BoolProperty(default=0)

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
    use_8_bones: bpy.props.BoolProperty(default=0)
    unk_flag_29: bpy.props.BoolProperty(default=0)
    unk_flag_30: bpy.props.BoolProperty(default=0)
    unk_flag_31: bpy.props.BoolProperty(default=0)
    unk_flag_32: bpy.props.BoolProperty(default=0)

    skin_weights_type: bpy.props.IntProperty(default=0)
    unk_flag_36: bpy.props.BoolProperty(default=0)
    unk_flag_37: bpy.props.BoolProperty(default=0)
    unk_flag_38: bpy.props.BoolProperty(default=0)
    unk_flag_39: bpy.props.BoolProperty(default=0)

    unk_flag_40: bpy.props.BoolProperty(default=0)
    use_emmisive_map: bpy.props.BoolProperty(default=0)
    unk_flag_42: bpy.props.BoolProperty(default=0)
    unk_flag_43: bpy.props.BoolProperty(default=0)
    use_detail_map: bpy.props.BoolProperty(default=0)
    unk_flag_45: bpy.props.BoolProperty(default=0)
    unk_flag_46: bpy.props.BoolProperty(default=0)
    use_cubemap: bpy.props.BoolProperty(default=0)
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
    detail_normal_power: bpy.props.FloatProperty(default=0.0)
    detail_normal_multiplier: bpy.props.FloatProperty(default=0.0)
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

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material("mrl_params", ("re0", "re1", "re6", "rev1", "rev2"))
@blender_registry.register_blender_prop
class MrlMaterialCustomProperties(bpy.types.PropertyGroup):  # noqa: F821
    blend_state_enum = bpy.props.EnumProperty(
        name="Blend State",
        description="select surface",
        items=[
            ("BSSolid", "BSSolid", "Opaque", 1),
            ("BSBlendAlpha", "BSBlendAlpha", "Alpha Channel transparency", 2),
            ("BSAddAlpha", "BSAddAlpha", "Additive transparency", 3),
            ("BSRevSubAlpha", "BSRevSubAlpha", "Unknown", 4),
        ],
        default="BSSolid",
        options=set()
    )
    # from MRL_DEPTH_STENCIL_STATE_STR
    depth_stencil_enum = bpy.props.EnumProperty(
        name="Depth Stencil State",
        items=[
            ("DSZTest", "DSZTest", "", 1),
            ("DSZTestWrite", "DSZTestWrite", "", 2),
            ("DSZTestWriteStencilWrite", "DSZTestWriteStencilWrite", "", 3),
            ("DSZTestStencilWrite", "DSZTestStencilWrite", "", 4),
            ("DSZWrite", "DSZWrite", "", 5)
        ],
        options=set()
    )
    # from MRL_RASTERIZER_STATE_STR
    rasterizer_state_enum = bpy.props.EnumProperty(
        name="Rasterizer State",
        items=[
            ("RSMesh", "RSMesh", "", 1),
            ("RSMeshCN", "RSMeshCN", "", 2),
            ("RSMeshCF", "RSMeshCF", "", 3),
            ("RSMeshBias1", "RSMeshBias1", "", 4),
            ("RSMeshBias2", "RSMeshBias2", "", 5),
            ("RSMeshBias3", "RSMeshBias3", "", 6),
            ("RSMeshBias4", "RSMeshBias4", "", 7),
            ("RSMeshBias5", "RSMeshBias5", "", 8),
            ("RSMeshBias6", "RSMeshBias6", "", 9),
            ("RSMeshBias8", "RSMeshBias8", "", 10),
            ("RSMeshBias9", "RSMeshBias9", "", 11),
            ("RSMeshBias10", "RSMeshBias10", "", 12),
            ("RSMeshBias11", "RSMeshBias11", "", 13),
            ("RSMeshBias12", "RSMeshBias12", "", 14)
        ],
        options=set()
    )

    blend_state_type: blend_state_enum
    depth_stencil_state_type: depth_stencil_enum
    rasterizer_state_type: rasterizer_state_enum
    unk_01: bpy.props.IntProperty(name="Unk_01", options=set())  # noqa: F821

    unk_flags: bpy.props.IntVectorProperty(
        name="Unknown Flags", size=4, default=(0, 0, 128, 140), options=set())

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "features", ("re0", "re1", "rev1", "rev2", "re6"),
    is_secondary=True, display_name="Features")
@blender_registry.register_blender_prop
class FeaturesMaterialCustomProperties(bpy.types.PropertyGroup):
    f_vertex_displacement_param : bpy.props.EnumProperty(
        name="FVertexDisplacement",  # noqa: F821
        items=[
            ("FVertexDisplacement", "Default", "", 1),  # noqa: F821
            ("FVertexDisplacementCurveUV", "FVertexDisplacementCurveUV", "", 2),  # noqa: F821
            ("FVertexDisplacementCurveU", "FVertexDisplacementCurveU", "", 3),  # noqa: F821
            ("FVertexDisplacementCurveV", "FVertexDisplacementCurveV", "", 4),  # noqa: F821
        ],
        options=set(),
    )
    f_uv_vertex_displacement_param : bpy.props.EnumProperty(
        name="FUVVertexDisplacement",  # noqa: F821
        items=[
            ("FVDUVPrimary", "FVDUVPrimary", "", 1),  # noqa: F821
            ("FVDUVSecondary", "FVDUVSecondary", "", 2),  # noqa: F821
            ("FVDUVExtend", "FVDUVExtend", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_vd_mask_uv_transform_param : bpy.props.EnumProperty(
        name="FVDMaskUVTransform",  # noqa: F821
        items=[
            ("FVDMaskUVTransform", "Default", "", 1),  # noqa: F821
            ("FVDMaskUVTransformOffset", "FVDMaskUVTransformOffset", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_vd_get_mask_param : bpy.props.EnumProperty(
        name="FVDGetMask",  # noqa: F821
        items=[
            ("FVDGetMask", "Default", "", 1),  # noqa: F821
            ("FVDGetMaskFromAO", "FVDGetMaskFromAO", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_uv_transform_primary_param : bpy.props.EnumProperty(  # noqa: F82
        name="FUVTransformPrimary",  # noqa: F821
        items=[
            ("FUVTransformPrimary", "Default", "", 1),  # noqa: F821
            ("FUVTransformOffset", "FUVTransformOffset", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_uv_transform_secondary_param : bpy.props.EnumProperty(
        name="FUVTransformSecondary",  # noqa: F821
        items=[
            ("FUVTransformSecondary", "Default", "", 1),  # noqa: F821
            ("FUVTransformOffset", "FUVTransformOffset", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_occlusion_param : bpy.props.EnumProperty(
        name="FOcclusion",  # noqa: F821
        items=[
            ("FOcclusion", "Default", "", 1),  # noqa: F821
            ("FOcclusionAmbient", "FOcclusionAmbient", "", 2),  # noqa: F821
            ("FOcclusionAmbientMap", "FOcclusionAmbientMap", "", 3),  # noqa: F821
            ("FOcclusionMap", "FOcclusionMap", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_uv_occlusion_map_param : bpy.props.EnumProperty(  # noqa: F821
        name="FUVOcclusionMap",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVUnique", "FUVUnique", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_bump_param : bpy.props.EnumProperty(
        name="FBump",  # noqa: F821
        items=[
            ("FBump", "Default", "", 1),  # noqa: F821
            ("FBlend2BumpDetailNormalMap", "FBlend2BumpDetailNormalMap", "", 2),  # noqa: F821
            ("FBumpDetailNormalMap", "FBumpDetailNormalMap", "", 3),  # noqa: F821
            ("FBumpDetailNormalMap2", "FBumpDetailNormalMap2", "", 4),  # noqa: F821
            ("FBumpHair", "FBumpHair", "", 5),  # noqa: F821
            ("FBumpHairNormal", "FBumpHair", "", 6),  # noqa: F821
            ("FBumpNormalMap", "FBumpNormalMap", "", 7),  # noqa: F821
            ("FBumpNormalMapBlendTransparencyMap", "FBumpNormalMapBlendTransparencyMap", "", 8),  # noqa: F821
            ("FBumpParallaxOcclusion", "FBumpParallaxOcclusion", "", 9),  # noqa: F821
        ],
        options=set()
    )
    f_uv_normal_map_param : bpy.props.EnumProperty(
        name="FUVNormalMap",  # noqa: F821
        items=[
            ("FUVNormalMap", "Default", "", 1),  # noqa: F821
            ("FUVPrimary", "FUVPrimary", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_uv_detail_normal_map_param : bpy.props.EnumProperty(  # noqa: F82
        name="FUVDetailNormalMap",  # noqa: F821
        items=[
            ("FUVSecondary", "FUVSecondary", "", 1),  # noqa: F821
            ("FUVPrimary", "FUVPrimary", "", 2),  # noqa: F821
            ("FUVUnique", "FUVUnique", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_uv_detail_normal_map_2_param : bpy.props.EnumProperty(  # noqa: F82
        name="FUVDetailNormalMap2",  # noqa: F821
        items=[
            ("FUVSecondary", "FUVSecondary", "", 1),  # noqa: F821
            ("FUVExtend", "FUVExtend", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_albedo_param : bpy.props.EnumProperty(  # noqa: F821
        name="FAlbedo",  # noqa: F821
        items=[
            ("FAlbedo", "Default", "", 1),  # noqa: F821
            ("FAlbedo2MapModulate", "FAlbedo2MapModulate", "", 2),  # noqa: F821
            ("FAlbedoMap", "FAlbedoMap", "", 3),  # noqa: F821
            ("FAlbedoMap2", "FAlbedoMap2", "", 4),  # noqa: F821
            ("FAlbedoMapAdd", "FAlbedoMapAdd", "", 5),  # noqa: F821
            ("FAlbedoMapBlend", "FAlbedoMapBlend", "", 6),  # noqa: F821
            ("FAlbedoMapBlendAlpha", "FAlbedoMapBlendAlpha", "", 7),  # noqa: F821
            ("FAlbedoMapBlendTransparencyMap", "FAlbedoMapBlendTransparencyMap", "", 8),  # noqa: F821
            ("FAlbedoMapModulate", "FAlbedoMapModulate", "", 9),  # noqa: F821
            ("FBlendAlbedoMap", "FBlendAlbedoMap", "", 10),  # noqa: F821
            ("FColorMaskAlbedoMapModulate", "FColorMaskAlbedoMapModulate", "", 11),  # noqa: F821
        ],
        options=set()
    )
    f_uv_albedo_map_param : bpy.props.EnumProperty(  # noqa: F821
        name="FUVAlbedoMap",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 2),  # noqa: F821
            ("FUVViewNormal", "FUVViewNormal", "", 3),  # noqa: F821
            ("FUVScreen", "FUVScreen", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_uv_albedo_blend_map_param : bpy.props.EnumProperty(  # noqa: F821
        name="FUVAlbedoBlendMap",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 2),  # noqa: F821
            ("FUVScreen", "FUVScreen", "", 3),  # noqa: F821
            ("FUVViewNormal", "FUVViewNormal", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_uv_albedo_blend_2_map_param : bpy.props.EnumProperty(  # noqa: F821
        name="FUVAlbedoBlend2Map",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 2),  # noqa: F821
            ("FUVScreen", "FUVScreen", "", 3),  # noqa: F821
            ("FUVViewNormal", "FUVViewNormal", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_transparency_param : bpy.props.EnumProperty(
        name="FTransparency",  # noqa: F821
        items=[
            ("FTransparency", "Default", "", 1),  # noqa: F821
            ("FTransparencyAlpha", "FTransparencyAlpha", "", 2),  # noqa: F821
            ("FTransparencyVolume", "FTransparencyVolume", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_uv_transparency_map_param : bpy.props.EnumProperty(
        name="FUVTransparencyMap",  # noqa: F821
        items=[
            ("FVDUVPrimary", "FVDUVPrimary", "", 1),  # noqa: F821
            ("FVDUVSecondary", "FVDUVSecondary", "", 2),  # noqa: F821
            ("FVDUVExtend", "FVDUVExtend", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_shininess_enabled : bpy.props.BoolProperty(
        name="FShininess", options=set())  # noqa: F821
    f_shininess_param : bpy.props.EnumProperty(
        name="FShininess",  # noqa: F821
        items=[
            ("FShininess", "Default", "", 1),  # noqa: F821
            ("FShininess2", "FShininess2", "", 2),  # noqa: F821
            ("FShininessMap", "FShininessMap", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_brdf_param : bpy.props.EnumProperty(
        name="FBRDF",  # noqa: F821
        items=[
            ("FBRDF", "Default", "", 1),  # noqa: F821
            ("FBRDFHair", "FBRDFHair", "", 2),  # noqa: F821
            ("FBRDFHairHalfLambert", "FBRDFHairHalfLambert", "", 3),  # noqa: F821
            ("FBRDFHalfLambert", "FBRDFHalfLambert", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_diffuse_param : bpy.props.EnumProperty(
        name="FDiffuse",  # noqa: F821
        items=[
            ("FDiffuse", "Default", "", 1),  # noqa: F821
            ("FDiffuseConstant", "FDiffuseConstant", "", 2),  # noqa: F821
            ("FDiffuseLightMap", "FDiffuseLightMap", "", 3),  # noqa: F821
            ("FDiffuseLightMapOcclusion", "FDiffuseLightMapOcclusion", "", 4),  # noqa: F821
            ("FDiffuseSH", "FDiffuseSH", "", 5),  # noqa: F821
            ("FDiffuseVertexColor", "FDiffuseVertexColor", "", 6),  # noqa: F821
            ("FDiffuseVertexColor", "FDiffuseVertexColor", "", 7),  # noqa: F821
            ("FDiffuseVertexColorOcclusion", "FDiffuseVertexColorOcclusion", "", 8),  # noqa: F821
        ],
        options=set()
    )
    f_ambient_param : bpy.props.EnumProperty(
        name="FAmbient",  # noqa: F821
        items=[
            ("FAmbient", "Default", "", 1),  # noqa: F821
            ("FAmbientSH", "FAmbientSH", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_specular_param : bpy.props.EnumProperty(
        name="FSpecular",  # noqa: F821
        items=[
            ("FSpecular", "Default", "", 1),  # noqa: F821
            ("FSpecularMap", "FSpecularMap", "", 2),  # noqa: F821
            ("FSpecular2Map", "FSpecular2Map", "", 3),  # noqa: F821
            ("FBlendSpecularMap", "FBlendSpecularMap", "", 4),  # noqa: F821
            ("FSpecularDisable", "FSpecularDisable", "", 5),  # noqa: F821
        ],
        options=set(),
    )
    f_uv_specular_map_param : bpy.props.EnumProperty(  # noqa: F821
        name="FUVSpecularMap",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_reflect_enabled : bpy.props.BoolProperty(
        name="FReflect", options=set())  # noqa: F821
    f_reflect_param : bpy.props.EnumProperty(
        name="FReflect",  # noqa: F821
        items=[
            ("FReflect", "Default", "", 1),  # noqa: F821
            ("FReflectCubeMap", "FReflectCubeMap", "", 2),  # noqa: F821
            ("FReflectGlobalCubeMap", "FReflectGlobalCubeMap", "", 3),  # noqa: F821
            ("FReflectSphereMap", "FReflectSphereMap", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_fresnel_enabled : bpy.props.BoolProperty(
        name="FFresnel Enabled", options=set())  # noqa: F821
    f_fresnel_param : bpy.props.EnumProperty(
        name="FFresnel",  # noqa: F821
        items=[
            ("FFresnel", "Default", "", 1),  # noqa: F821
            ("FFresnelSchlick", "FFresnelSchlick", "", 2),  # noqa: F821
            ("FFresnelSchlickRGB", "FFresnelSchlickRGB", "", 3),  # noqa: F821
            ("FFresnelSchlick2", "FFresnelSchlick2", "", 4),  # noqa: F821
            ("FFresnelLegacy", "FFresnelLegacy", "", 5),  # noqa: F821
        ],
        options=set()
    )
    f_emission_param : bpy.props.EnumProperty(  # noqa: F82
        name="FEmission",  # noqa: F821
        items=[
            ("FEmission", "Default", "", 1),  # noqa: F821
            ("FEmissionMap", "FEmissionMap", "", 2),  # noqa: F821
            ("FEmissionConstant", "FEmissionConstant", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_uv_emission_map_param : bpy.props.EnumProperty(  # noqa: F82
        name="FUVEmissionMap",  # noqa: F821
        items=[
            ("FUVSecondary", "FUVSecondary", "", 1),  # noqa: F821
            ("FUVViewNormal", "FUVViewNormal", "", 2),  # noqa: F821
            ("FUVPrimary", "FUVPrimary", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_distortion_param : bpy.props.EnumProperty(  # noqa: F821
        name="FDistortion",  # noqa: F821
        items=[
            ("FDistortion", "Default", "", 1),  # noqa: F821
            ("FDistortionRefract", "FDistortionRefract", "", 2),  # noqa: F821
        ],
        options=set()
    )
    ssenvmap_enabled : bpy.props.BoolProperty(
        name="SSEnvMap", options=set(), default=True)  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "cb_material", ("re0", "re1", "rev1", "rev2", "re6"),
    is_secondary=True, display_name="CB Material")
@blender_registry.register_blender_prop
class CBMaterialCustomProperties(bpy.types.PropertyGroup):
    f_diffuse_color: bpy.props.FloatVectorProperty(
        name="fDiffuseColor", default=(1, 1, 1), options=set(), subtype="COLOR")  # noqa: F821
    f_transparency: bpy.props.FloatProperty(
        name="fTransparency", default=1, options=set())  # noqa: F821
    f_reflective_color: bpy.props.FloatVectorProperty(
        name="fReflectiveColor", default=(1, 1, 1), options=set(), subtype="COLOR")  # noqa: F821
    f_transparency_volume: bpy.props.FloatProperty(
        name="fTransparencyVolume", default=10, options=set())  # noqa: F821
    f_uv_transform: bpy.props.FloatVectorProperty(
        name="fUVTransform", size=8, default=(1, 0, 0, 0, 0, 1, 0, 0), options=set())  # noqa: F821
    f_uv_transform2: bpy.props.FloatVectorProperty(
        name="fUVTransform2", size=8, default=(1, 0, 0, 0, 0, 1, 0, 0), options=set())  # noqa: F821
    f_uv_transform3: bpy.props.FloatVectorProperty(
        name="fUVTransform3", size=8, default=(1, 0, 0, 0, 0, 1, 0, 0), options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "cb_vertex_disp", ("re0", "re1", "rev1", "rev2", "re6"),
    is_secondary=True, display_name="CB Vertex Displacement")
@blender_registry.register_blender_prop
class CBVtxDisp(bpy.types.PropertyGroup):
    f_vtx_disp_start: bpy.props.FloatProperty(
        name="fVtxDispStart", options=set())  # noqa: F821
    f_vtx_disp_scale: bpy.props.FloatProperty(
        name="fVtxDispScale", options=set())  # noqa: F821
    f_vtx_disp_inv_area: bpy.props.FloatProperty(
        name="fVtxDispInvArea", options=set())  # noqa: F821
    f_vtx_disp_rcn: bpy.props.FloatProperty(
        name="fVtxDispRcn", options=set())  # noqa: F821
    f_vtx_disp_tilt_u: bpy.props.FloatProperty(
        name="fVtxDispTiltU", options=set())  # noqa: F821
    f_vtx_disp_tilt_v: bpy.props.FloatProperty(
        name="fVtxDispTiltV", options=set())  # noqa: F821
    filler: bpy.props.FloatVectorProperty(
        name="fVtxDispTiltV", size=2, options={"HIDDEN"})  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "cb_vertex_disp2", ("re0", "re1", "rev1", "rev2", "re6"),
    is_secondary=True, display_name="CB Vertex Displacement")
@blender_registry.register_blender_prop
class CBVtxDisp2(bpy.types.PropertyGroup):
    f_vtx_disp_start2: bpy.props.FloatProperty(
        name="fVtxDispStart2", options=set())  # noqa: F821
    f_vtx_disp_scale2: bpy.props.FloatProperty(
        name="fVtxDispScale2", options=set())  # noqa: F821
    f_vtx_disp_inv_area2: bpy.props.FloatProperty(
        name="fVtxDispInvArea2", options=set())  # noqa: F821
    f_vtx_disp_rcn2: bpy.props.FloatProperty(
        name="fVtxDispRcn2", options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "cb_color_mask", ("re0", "re1", "rev1", "rev2", "re6"),
    is_secondary=True, display_name="CB Color Mask")
@blender_registry.register_blender_prop
class CBColorMaskCustomProperties(bpy.types.PropertyGroup):
    f_color_mask_threshold: bpy.props.FloatVectorProperty(
        name="fColorMaskThreshold", size=4, options=set())  # noqa: F821
    f_color_mask_offset: bpy.props.FloatVectorProperty(
        name="fColorMaskOffset", size=4, options=set())  # noqa: F821
    f_clip_threshold: bpy.props.FloatVectorProperty(
        name="fClipThreshold", size=4, options=set())  # noqa: F821
    f_color_mask_color: bpy.props.FloatVectorProperty(
        name="fColorMaskColor", size=4, subtype="COLOR", options=set())  # noqa: F821
    f_color_mask2_threshold: bpy.props.FloatVectorProperty(
        name="fColorMask2Threshold", size=4, options=set())  # noqa: F821
    f_color_mask2_color: bpy.props.FloatVectorProperty(
        name="fColorMask2Color", size=4, subtype="COLOR", options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "globals",
    ("re0", "re1", "rev1"), is_secondary=True, display_name="$Globals")
@blender_registry.register_blender_prop
class GlobalsCustomProperties1(bpy.types.PropertyGroup):
    f_alpha_clip_threshold: bpy.props.FloatProperty(
        name="fAlphaClipThreshold", default=0, options=set())  # noqa: F821
    f_albedo_color: bpy.props.FloatVectorProperty(
        name="fAlbedoColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_albedo_blend_color: bpy.props.FloatVectorProperty(
        name="fAlbedoBlendColor", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_detail_normal_power: bpy.props.FloatProperty(
        name="fDetailNormalPower", default=1, options=set())  # noqa: F821
    f_detail_normal_uv_scale: bpy.props.FloatProperty(
        name="fDetailNormalUVScale", default=1, options=set())  # noqa: F821
    f_detail_normal2_power: bpy.props.FloatProperty(
        name="fDetailNormal2Power", default=1, options=set())  # noqa: F821
    f_detail_normal2_uv_scale: bpy.props.FloatProperty(
        name="fDetailNormal2UVScale", default=1, options=set())  # noqa: F821
    f_primary_shift: bpy.props.FloatProperty(
        name="fPrimaryShift", default=0, options=set())  # noqa: F821
    f_secondary_shift: bpy.props.FloatProperty(
        name="fSecondaryShift", options=set())  # noqa: F821
    f_parallax_factor: bpy.props.FloatProperty(
        name="fParalallaxFactor", options=set())  # noqa: F821
    f_parallax_self_occlusion: bpy.props.FloatProperty(
        name="fParalallaxSelfOcclusion", default=1, options=set())  # noqa: F821
    f_parallax_min_sample: bpy.props.FloatProperty(
        name="fParallaxMinSample", default=4, options=set())  # noqa: F821
    f_parallax_max_sample: bpy.props.FloatVectorProperty(
        name="fParallaxMaxSample", default=(64, 0, 0), options=set())  # noqa: F821
    f_light_map_color: bpy.props.FloatVectorProperty(
        name="fLightMapColor", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821
    f_thin_map_color: bpy.props.FloatVectorProperty(
        name="fThinMapColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_thin_scattering: bpy.props.FloatProperty(
        name="fThinScattering", options=set())  # noqa: F821
    f_screen_uv_scale: bpy.props.FloatVectorProperty(
        name="fScreenUVScale", size=2, default=(1, 1), options=set())  # noqa: F821
    f_screen_uv_offset: bpy.props.FloatVectorProperty(
        name="fScreenUVOffste", size=2, options=set())  # noqa: F821
    f_indirect_offset: bpy.props.FloatVectorProperty(
        name="fIndirectOffset", size=2, options=set())  # noqa: F821
    f_indirect_scale: bpy.props.FloatVectorProperty(
        name="fIndirectScale", size=2, options=set())  # noqa: F821
    f_fresnel_schlick: bpy.props.FloatProperty(
        name="fFresnelSchlick", default=1, options=set())  # noqa: F821
    f_fresnel_schlick_rgb: bpy.props.FloatVectorProperty(
        name="fFresnelSchlickRGB", default=(1, 1, 1), options=set())  # noqa: F821
    f_specular_color: bpy.props.FloatVectorProperty(
        name="fSpecularColor", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_shininess: bpy.props.FloatProperty(
        name="fShininess", default=30, options=set())  # noqa: F821
    f_emission_color: bpy.props.FloatVectorProperty(
        name="fEmissionColor", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_emission_threshold: bpy.props.FloatProperty(
        name="fEmissionThreshold", default=0.5, options=set())  # noqa: F821
    f_constant_color: bpy.props.FloatVectorProperty(
        name="fConstantColor", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_roughness: bpy.props.FloatProperty(
        name="fRoughness", default=1, options=set())  # noqa: F821
    f_roughness_rgb: bpy.props.FloatVectorProperty(
        name="fRoughnessRGB", default=(0.3, 0.3, 0.3), options=set())  # noqa: F821
    f_anisotoropic_direction: bpy.props.FloatVectorProperty(
        name="fAnisotoropicDirection", default=(0, 1, 0), options=set())  # noqa: F821
    f_smoothness: bpy.props.FloatProperty(
        name="fSmoothness", default=1, options=set())  # noqa: F821
    f_anistropic_uv: bpy.props.FloatVectorProperty(
        name="fAnistropicUV", size=2, default=(0.33, 1), options=set())  # noqa: F821
    f_primary_expo: bpy.props.FloatProperty(
        name="fPrimaryExpo", default=1, options=set())  # noqa: F821
    f_secondary_expo: bpy.props.FloatProperty(
        name="fSecondaryExpo", default=0.2, options=set())  # noqa: F821
    f_primary_color: bpy.props.FloatVectorProperty(
        name="fPrimaryColor", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821
    f_secondary_color: bpy.props.FloatVectorProperty(
        name="fSecondaryColor", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        # TODO: warning of missing attributes
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except AttributeError:
                print(f"{attr_name} not found on source object {src_obj}")


@blender_registry.register_custom_properties_material(
    "globals", ("rev2",), is_secondary=True, display_name="$Globals")
@blender_registry.register_blender_prop
class GlobalsCustomProperties2(bpy.types.PropertyGroup):
    f_alpha_clip_threshold: bpy.props.FloatProperty(
        name="fAlphaClipThreshold", default=0, options=set())  # noqa: F821
    f_albedo_color: bpy.props.FloatVectorProperty(
        name="fAlbedoColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_albedo_blend_color: bpy.props.FloatVectorProperty(
        name="fAlbedoBlendColor", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_detail_normal_power: bpy.props.FloatProperty(
        name="fDetailNormalPower", default=1, options=set())  # noqa: F821
    f_detail_normal_uv_scale: bpy.props.FloatProperty(
        name="fDetailNormalUVScale", default=1, options=set())  # noqa: F821
    f_detail_normal2_power: bpy.props.FloatProperty(
        name="fDetailNormal2Power", default=1, options=set())  # noqa: F821
    f_detail_normal2_uv_scale: bpy.props.FloatProperty(
        name="fDetailNormal2UVScale", default=1, options=set())  # noqa: F821
    f_primary_shift: bpy.props.FloatProperty(
        name="fPrimaryShift", default=0, options=set())  # noqa: F821
    f_secondary_shift: bpy.props.FloatProperty(
        name="fSecondaryShift", options=set())  # noqa: F821
    f_parallax_factor: bpy.props.FloatProperty(
        name="fParalallax_factor", options=set())  # noqa: F821
    f_parallax_self_occlusion: bpy.props.FloatProperty(
        name="fParalallaxSelfOcclusion", default=1, options=set())  # noqa: F821
    f_parallax_min_sample: bpy.props.FloatProperty(
        name="fParallaxMinSample", default=4, options=set())  # noqa: F821
    f_parallax_max_sample: bpy.props.FloatVectorProperty(
        name="fParallaxMaxSample", default=(64, 0, 0), options=set())  # noqa: F821
    f_light_map_color: bpy.props.FloatVectorProperty(
        name="fLightMapColor", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821
    f_thin_map_color: bpy.props.FloatVectorProperty(
        name="fThinMapColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_thin_scattering: bpy.props.FloatProperty(
        name="fThinScattering", options=set())  # noqa: F821
    f_screen_uv_scale: bpy.props.FloatVectorProperty(
        name="fScreenUVScale", size=2, default=(1, 1), options=set())  # noqa: F821
    f_screen_uv_offset: bpy.props.FloatVectorProperty(
        name="fScreenUVOffste", size=2, options=set())  # noqa: F821
    f_indirect_offset: bpy.props.FloatVectorProperty(
        name="fIndirectOffset", size=2, options=set())  # noqa: F821
    f_indirect_scale: bpy.props.FloatVectorProperty(
        name="fIndirectScale", size=2, options=set())  # noqa: F821
    f_fresnel_schlick: bpy.props.FloatProperty(
        name="fFresnelSchlick", default=1, options=set())  # noqa: F821
    f_fresnel_schlick_rgb: bpy.props.FloatVectorProperty(
        name="fFresnelSchlickRGB", default=(1, 1, 1), options=set())  # noqa: F821
    f_specular_color: bpy.props.FloatVectorProperty(
        name="fSpecularColor", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_shininess: bpy.props.FloatProperty(
        name="fShininess", default=30, options=set())  # noqa: F821
    f_emission_color: bpy.props.FloatVectorProperty(
        name="fEmissionColor", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_emission_threshold: bpy.props.FloatProperty(
        name="fEmissionThreshold", default=0.5, options=set())  # noqa: F821
    f_constant_color: bpy.props.FloatVectorProperty(
        name="fConstantColor", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_roughness: bpy.props.FloatProperty(
        name="fRoughness", default=1, options=set())  # noqa: F821
    f_roughness_rgb: bpy.props.FloatVectorProperty(
        name="fRoughnessRGB", default=(0.3, 0.3, 0.3), options=set())  # noqa: F821
    f_anisotoropic_direction: bpy.props.FloatVectorProperty(
        name="fAnisotoropicDirection", default=(0, 1, 0), options=set())  # noqa: F821
    f_smoothness: bpy.props.FloatProperty(
        name="fSmoothness", default=1, options=set())  # noqa: F821
    f_anistropic_uv: bpy.props.FloatVectorProperty(
        name="fAnistropicUV", size=2, default=(0.33, 1), options=set())  # noqa: F821
    f_primary_expo: bpy.props.FloatProperty(
        name="fPrimaryExpo", default=1, options=set())  # noqa: F821
    f_secondary_expo: bpy.props.FloatProperty(
        name="fSecondaryExpo", default=0.2, options=set())  # noqa: F821
    f_primary_color: bpy.props.FloatVectorProperty(
        name="fPrimaryColor", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821
    f_secondary_color: bpy.props.FloatVectorProperty(
        name="fSecondaryColor", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821
    f_albedo_color2: bpy.props.FloatVectorProperty(
        name="fAlbedoColor2", size=4, default=(1, 1, 1, 0), subtype="COLOR", options=set())  # noqa: F821
    f_specular_color2: bpy.props.FloatVectorProperty(
        name="fSpecularColor2", default=(8, 8, 8), subtype="COLOR", options=set())  # noqa: F821
    f_fresnel_schlick2: bpy.props.FloatProperty(
        name="fFresnelSchlick2", default=1, options=set())  # noqa: F821
    f_shininess2: bpy.props.FloatVectorProperty(
        name="fShininess2", size=4, default=(500, 0, 0, 0), options=set())  # noqa: F821
    f_transparency_clip_threshold: bpy.props.FloatVectorProperty(
        name="fTransparencyClipThreshold", size=4, default=(0, 0, 0, 0), options=set())  # noqa: F821
    f_blend_uv: bpy.props.FloatProperty(
        name="fBlendUV", default=1, options=set())  # noqa: F821
    f_normal_power: bpy.props.FloatVectorProperty(
        name="fNormalPower", default=(1, 0, 0), options=set())  # noqa: F821
    f_albedo_blend2_color: bpy.props.FloatVectorProperty(
        name="fAlbedoBlend2Color", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_detail_normal_u_v_scale: bpy.props.FloatVectorProperty(
        name="fDetailNormalUVScale", size=2, default=(1, 1), options=set())  # noqa: F821
    f_fresnel_legacy: bpy.props.FloatVectorProperty(
        name="fFresnelLegacy", size=2, default=(1, 1), options=set())  # noqa: F821
    f_normal_mask_pow0: bpy.props.FloatVectorProperty(
        name="fNormalMaskPow0", size=4, default=(1, 1, 1, 1), options=set())  # noqa: F821
    f_normal_mask_pow1: bpy.props.FloatVectorProperty(
        name="fNormalMaskPowe1", size=4, default=(1, 1, 1, 1), options=set())  # noqa: F821
    f_normal_mask_pow2: bpy.props.FloatVectorProperty(
        name="fNormalMaskPow2", size=4, default=(1, 1, 1, 1), options=set())  # noqa: F821
    f_texture_blend_rate: bpy.props.FloatVectorProperty(
        name="fTextureBlendRate", size=4, options=set())  # noqa: F821
    f_texture_blend_color: bpy.props.FloatVectorProperty(
        name="fTextureBlendcolor", size=4, subtype="COLOR", options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        # TODO: warning of missing attributes
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except AttributeError:
                print(f"{attr_name} not found on source object {src_obj}")


@blender_registry.register_custom_properties_material(
    "globals",
    ("re6",), is_secondary=True, display_name="$Globals")
@blender_registry.register_blender_prop
class GlobalsCustomProperties3(bpy.types.PropertyGroup):
    f_albedo_color: bpy.props.FloatVectorProperty(
        name="fAlbedoColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_1 : bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_albedo_blend_color: bpy.props.FloatVectorProperty(
        name="fAlbedoBlendColor", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_detail_normal_power: bpy.props.FloatProperty(
        name="fDetailNormalPower", default=1, options=set())  # noqa: F821
    f_detail_normal_uv_scale: bpy.props.FloatProperty(
        name="fDetailNormalUVScale", default=1, options=set())  # noqa: F821
    f_detail_normal2_power: bpy.props.FloatProperty(
        name="fDetailNormal2Power", default=1, options=set())  # noqa: F821
    f_detail_normal2_uv_scale: bpy.props.FloatProperty(
        name="fDetailNormal2UVScale", default=1, options=set())  # noqa: F821
    f_primary_shift: bpy.props.FloatProperty(
        name="fPrimaryShift", default=0, options=set())  # noqa: F821
    f_secondary_shift: bpy.props.FloatProperty(
        name="fSecondaryShift", options=set())  # noqa: F821
    f_parallax_factor: bpy.props.FloatProperty(
        name="fParalallaxFactor", options=set())  # noqa: F821
    f_parallax_self_occlusion: bpy.props.FloatProperty(
        name="fParalallaxSelfOcclusion", default=1, options=set())  # noqa: F821
    f_parallax_min_sample: bpy.props.FloatProperty(
        name="fParallaxMinSample", default=4, options=set())  # noqa: F821
    f_parallax_max_sample: bpy.props.FloatProperty(
        name="fParallaxMaxSample", options=set())  # noqa: F821

    padding_2 : bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821

    f_light_map_color: bpy.props.FloatVectorProperty(
        name="fLightMapColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_3 : bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821

    f_thin_map_color: bpy.props.FloatVectorProperty(
        name="fThinMapColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_thin_scattering: bpy.props.FloatProperty(
        name="fThinScattering", options=set())  # noqa: F821
    f_indirect_offset: bpy.props.FloatVectorProperty(
        name="fIndirectOffset", size=2, options=set())  # noqa: F821
    f_indirect_scale: bpy.props.FloatVectorProperty(
        name="fIndirectScale", size=2, options=set())  # noqa: F821
    f_fresnel_schlick: bpy.props.FloatProperty(
        name="fFresnelSchlick", default=1, options=set())  # noqa: F821
    f_fresnel_schlick_rgb: bpy.props.FloatVectorProperty(
        name="fFresnelSchlickRGB", default=(1, 1, 1), options=set())  # noqa: F821
    f_specular_color: bpy.props.FloatVectorProperty(
        name="fSpecularColor", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_shininess: bpy.props.FloatProperty(
        name="fShininess", default=30, options=set())  # noqa: F821
    f_emission_color: bpy.props.FloatVectorProperty(
        name="fEmissionColor", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_alpha_clip_threshold: bpy.props.FloatProperty(
        name="fAlphaClipThreshold", default=0, options=set())  # noqa: F821
    f_primary_expo: bpy.props.FloatProperty(
        name="fPrimaryExpo", default=1, options=set())  # noqa: F821
    f_secondary_expo: bpy.props.FloatProperty(
        name="fSecondaryExpo", default=0.2, options=set())  # noqa: F821
    padding_4 : bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821
    f_primary_color: bpy.props.FloatVectorProperty(
        name="fPrimaryColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_5 : bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_secondary_color: bpy.props.FloatVectorProperty(
        name="fSecondaryColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_6 : bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_albedo_color_2: bpy.props.FloatVectorProperty(
        name="fAlbedoColor2", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_7 : bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_specular_color_2: bpy.props.FloatVectorProperty(
        name="fSpecularColor2", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_fresnel_schlick_2: bpy.props.FloatProperty(
        name="fFresnelSchlick2", default=1, options=set())  # noqa: F821
    f_shininess_2: bpy.props.FloatProperty(
        name="fShininess2", default=30, options=set())  # noqa: F821
    padding_8 : bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0), options={"HIDDEN"})  # noqa: F821
    f_transparency_clip_threshold: bpy.props.FloatVectorProperty(
        name="fTransparencyClipThreshold", size=4, default=(0, 0, 0, 0), options=set())  # noqa: F821
    f_blend_uv: bpy.props.FloatProperty(
        name="fBlendUV", default=1, options=set())  # noqa: F821
    padding_9 : bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0), options={"HIDDEN"})  # noqa: F821
    f_albedo_blend2_color: bpy.props.FloatVectorProperty(
        name="fAlbedoBlend2Color", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_detail_normalu_vscale: bpy.props.FloatVectorProperty(
        name="fDetailNormalU_VScale", size=2, default=(0, 0), options=set())  # noqa: F821
    padding_10 : bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        # TODO: warning of missing attributes
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except AttributeError:
                print(f"{attr_name} not found on source object {src_obj}")
