from binascii import crc32
import functools
import io
import re

import bpy
from kaitaistruct import KaitaiStream

from albam.exceptions import AlbamCheckFailure
from albam.lib.blender import get_bl_materials, ShaderGroupCompat
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
    212: lambda: _serialize_materials_data_21,
}

VERSION_USES_MRL = {210, 211, 212}
VERSION_USES_MATERIAL_NAMES = {210, 212}
MRL_DEFAULT_VERSION = {
    "re0": 34,
    "re1": 34,
    "re6": 33,
    "rev1": 32,
    "rev2": 34,
    "dd": 32,
}
MRL_FILLER = 0xDCDC
MRL_PAD = 16
MRL_SHADER_VERSION = {
    "re0": 0x419a398d,
    "re1": 0x244bbc26,
    "re6": 0x6a5489b8,
    "rev1": 0xe333fde9,
    "rev2": 0x478ed2d7,
    "dd": 0xb46006d5,
}


MRL_CBGLOBALS_MAP = {
    "re0": Mrl.CbGlobals1,
    "re1": Mrl.CbGlobals1,
    "re6": Mrl.CbGlobals3,
    "rev1": Mrl.CbGlobals1,
    "rev2": Mrl.CbGlobals2,
    "dd": Mrl.CbGlobals4,
}
MRL_MATERIAL_TYPE_STR = {
    # 0x315ECCA9: "TYPE_nDraw__MaterialNull",
    0x854D484: "TYPE_nDraw__MaterialNull",  # nDraw::MaterialNull
    0x5FB0EBE4: "TYPE_nDraw__MaterialStd",  # ̾nDraw::MaterialStd 1605430244
    0x7D2B31B3: "TYPE_nDraw__MaterialStdEst",  # nDraw::MaterialStdEst 2099982771
    0x1CAB245E: "TYPE_nDraw__DDMaterialStd",  # nDraw::DDMaterialStd
    0x26D9BA5C: "TYPE_nDraw__DDMaterialInner",  # nDraw::DDMaterialInner
    0x30DBA54F: "TYPE_nDraw__DDMaterialWater",  # nDraw::DDMaterialWater
}

MRL_MATERIAL_TYPE_STR_TO_ID = {ext_desc: h for h, ext_desc in MRL_MATERIAL_TYPE_STR.items()}

MRL_PER_MATERIAL_FEATURES = {
    0x854D484: [],
    0x5FB0EBE4: ["FVertexDisplacement"],
    0x7D2B31B3: ["FVertexDisplacement"],
    0x1CAB245E: ["CBDDMaterialParam",
                 "FDDMaterialCalcBorderBlendRate",
                 "FDDMaterialCalcBorderBlendAlphaMap",
                 "FUVAlbedoMap",
                 "SSAlbedoMap",
                 "FDDMaterialBump",
                 "FDDMaterialAlbedo",
                 "FDDMaterialSpecular",
                 "FDDMaterialSpecular",
                 "FAppClip",
                 "CBAppClipPlane",
                 "FAppOutline",
                 "CBOutlineEx",
                 "FIntegratedOutlineColor",
                 "FDDMaterialFinalCombiner",
                 ],
    0x26D9BA5C: ["CBDDMaterialParamInnerCorrect",
                 "CBDDMaterialParam",
                 "FDDMaterialCalcBorderBlendRate",
                 "FDDMaterialCalcBorderBlendAlphaMap",
                 "FUVAlbedoMap",
                 "SSAlbedoMap",
                 "FDDMaterialBump",
                 "FDDMaterialAlbedo",
                 "FDDMaterialSpecular",
                 "FDDMaterialSpecular",
                 "FAppClip",
                 "CBAppClipPlane",
                 "FAppOutline",
                 "CBOutlineEx",
                 "FIntegratedOutlineColor",
                 "FDDMaterialFinalCombiner",
                 ],
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
            material_type = MRL_MATERIAL_TYPE_STR[material.type_hash]
            blend_state_type = MRL_BLEND_STATE_STR[material.blend_state_hash >> 12]
            depth_stencil_state_type = MRL_DEPTH_STENCIL_STATE_STR[(material.depth_stencil_state_hash >> 12)]
            rasterizer_state_type = MRL_RASTERIZER_STATE_STR[(material.rasterizer_state_hash >> 12)]
            custom_props_top_level.material_type = material_type
            custom_props_top_level.blend_state_type = blend_state_type
            custom_props_top_level.depth_stencil_state_type = depth_stencil_state_type
            custom_props_top_level.rasterizer_state_type = rasterizer_state_type
            custom_props_top_level.reserverd1 = material.reserverd1
            custom_props_top_level.id = material.id
            custom_props_top_level.fog = material.fog
            custom_props_top_level.tangent = material.tangent
            custom_props_top_level.half_lambert = material.half_lambert
            custom_props_top_level.stencil_ref = material.stencil_ref
            custom_props_top_level.alphatest_ref = material.alphatest_ref
            custom_props_top_level.polygon_offset = material.polygon_offset
            custom_props_top_level.alphatest = material.alphatest
            custom_props_top_level.alphatest_func = material.alphatest_func
            custom_props_top_level.draw_pass = material.draw_pass
            custom_props_top_level.layer_id = material.layer_id
            custom_props_top_level.deffered_lighting = material.deffered_lighting

            # verified in tests that $Globals and CBMaterial resources are present if there are resources
            # see tests.mtfw.test_parsing_mrl::test_global_resources_mandatory
            if material.resources:
                _copy_resources_to_bl_mat(app_id, material, blender_material)
        else:
            custom_props_top_level.copy_custom_properties_from(material)

        blender_material.use_nodes = True
        blender_material.blend_method = "CLIP"
        node_to_delete = None
        for node in blender_material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node_to_delete = node
                blender_material.node_tree.nodes.remove(node_to_delete)
                break
        shader_node_group = blender_material.node_tree.nodes.new("ShaderNodeGroup")
        shader_node_group.node_tree = bpy.data.node_groups[MTFW_SHADER_NODEGROUP_NAME]
        shader_node_group.name = "MTFrameworkGroup"
        shader_node_group.width = 300
        for node in blender_material.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                material_output = node
                break
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
            try:
                resource[0].value_cmd.name_hash.name
                param = resource[0].value_cmd.name_hash.name
                param = [k for k, v in shader_objects.items() if v["friendly_name"] == param][0]
                setattr(features, custom_prop_name, param)
            except AttributeError:
                print(resource[0].value_cmd.name_hash)
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
        if hasattr(cb.float_buffer, 'app_specific'):
            cb_custom_props.copy_custom_properties_from(cb.float_buffer.app_specific)
        else:
            cb_custom_props.copy_custom_properties_from(cb.float_buffer)

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
    copy_float_buffer("cbburncommon", "cb_burn_common")
    copy_float_buffer("cbburnemission", "cb_burn_emission")
    copy_float_buffer("cbappclipplane", "cb_app_clip_plane")
    copy_float_buffer("cbspecularblend", "cb_specular_blend")
    copy_float_buffer("cbappreflect", "cb_app_reflect")
    copy_float_buffer("cbappreflectshadowlight", "cb_app_refl_sh_lt")
    copy_float_buffer("cboutlineex", "cb_outline_ex")
    copy_float_buffer("cbddmaterialparam", "cb_dd_mat_param")
    copy_float_buffer("cbuvrotationoffset", "cb_uv_rot_offset")
    copy_float_buffer("cbddmaterialparaminnercorrect", "cb_dd_m_p_inn_cor")
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

        tex_types = _gather_tex_types(
            bl_mat, exported_textures, dst_mod.materials_data.textures, app_id=app_id)
        mat.basemap = tex_types.get(TextureType.DIFFUSE, -1) + 1
        mat.normalmap = tex_types.get(TextureType.NORMAL, -1) + 1
        mat.maskmap = tex_types.get(TextureType.SPECULAR, -1) + 1
        mat.lightmap = tex_types.get(TextureType.LIGHTMAP, -1) + 1
        mat.shadowmap = tex_types.get(TextureType.UNK_01, -1) + 1
        mat.additionalmap = tex_types.get(TextureType.ALPHAMAP, -1) + 1
        mat.envmap = tex_types.get(TextureType.ENVMAP, -1) + 1
        mat.detailmap = (tex_types.get(TextureType.NORMAL_DETAIL, -1) + 1)
        mat.occlusionmap = 0
        mat.lightblendmap = 0
        mat.shadowblendmap = 0
        mat.heightmap = 0
        mat.glossmap = 0
        mat.func_reserved = 0
        mat.func_reserved2 = 0
        mat.reserved1 = 0
        mat.reserved2 = 0
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
    mrl.shader_version = MRL_SHADER_VERSION[app_id]
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
        mat_type = mrl_params.material_type

        mat = mrl.Material(_parent=mrl, _root=mrl._root)
        mat.type_hash = MRL_MATERIAL_TYPE_STR_TO_ID[mat_type]
        mat.name_hash_crcjam32 = material_hash
        mat.blend_state_hash = (shader_objects[mrl_params.blend_state_type]["hash"] << 12) + blend_state_index
        mat.depth_stencil_state_hash = (shader_objects[mrl_params.depth_stencil_state_type]["hash"] << 12) + depth_stencil_state_index  # noqa
        mat.rasterizer_state_hash = (shader_objects[mrl_params.rasterizer_state_type]["hash"] << 12) + rasterizer_state_index  # noqa
        mat.reserverd1 = mrl_params.reserverd1
        mat.id = mrl_params.id
        mat.fog = mrl_params.fog
        mat.tangent = mrl_params.tangent
        mat.half_lambert = mrl_params.half_lambert
        mat.stencil_ref = mrl_params.stencil_ref
        mat.alphatest_ref = mrl_params.alphatest_ref
        mat.polygon_offset = mrl_params.polygon_offset
        mat.alphatest = mrl_params.alphatest
        mat.alphatest_func = mrl_params.alphatest_func
        mat.draw_pass = mrl_params.draw_pass
        mat.layer_id = mrl_params.layer_id
        mat.deffered_lighting = mrl_params.deffered_lighting
        mat.blend_factor = [0, 0, 0, 0]
        mat.anim_data_size = 0
        mat.ofs_anim_data = 0

        tex_types = _gather_tex_types(bl_mat, exported_textures, mrl.textures, mrl=mrl, app_id=app_id)
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

        exported_materials_map[bl_mat.name] = bl_mat_idx
        exported_materials_map[material_hash] = bl_mat_idx
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

    cb_app_refl_sh_lt_users = {
        "freflectcubemapshadowlight"
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
        elif (
            resource.value_cmd.name_hash.name in cb_app_refl_sh_lt_users and
            not cb_used.get("CBAppReflectShadowLight")
        ):
            pos = current_position
            current_position += 1
            cb_used["CBAppReflectShadowLight"] = [ri + 1, pos]
            pos = current_position
            current_position += 1
            cb_used["CBAppReflect"] = [ri + 1, pos]

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
    MF = MRL_PER_MATERIAL_FEATURES[mrl_mat.type_hash]

    r = [
        set_constant_buffer("CBDDMaterialParamInnerCorrect", onlyif="CBDDMaterialParamInnerCorrect" in MF),
        set_flag("FVertexDisplacement",
                 features.f_vertex_displacement_param,
                 onlyif="FVertexDisplacement" in MF),
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

        set_constant_buffer("CBDDMaterialParam", onlyif="CBDDMaterialParam" in MF),
        set_flag("FDDMaterialCalcBorderBlendRate", onlyif="FDDMaterialCalcBorderBlendRate" in MF),
        set_flag("FDDMaterialCalcBorderBlendAlphaMap", onlyif="FDDMaterialCalcBorderBlendAlphaMap" in MF),
        set_flag("FUVAlbedoMap", "FUVPrimary", onlyif="FUVAlbedoMap" in MF),
        set_sampler_state("SSAlbedoMap", onlyif="SSAlbedoMap" in MF),

        set_flag("FOcclusion", features.f_occlusion_param),
        set_texture("tOcclusionMap", onlyif=TT.OCCLUSION in tt),
        set_flag("FUVOcclusionMap", features.f_uv_occlusion_map_param, onlyif=TT.OCCLUSION in tt),
        set_flag("FChannelOcclusionMap", onlyif=TT.OCCLUSION in tt),

        set_flag("FDDMaterialBump", onlyif="FDDMaterialBump" in MF),

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

        set_flag("FDDMaterialAlbedo", onlyif="FDDMaterialAlbedo" in MF),

        set_flag("FAlbedo", features.f_albedo_param),
        set_texture("tAlbedoMap", onlyif=TT.DIFFUSE in tt),
        set_sampler_state("SSAlbedoMap", onlyif=TT.DIFFUSE in tt and "SSAlbedoMap" not in MF),
        set_flag("FUVAlbedoMap",
                 features.f_uv_albedo_map_param,
                 onlyif=TT.DIFFUSE in tt and "FUVAlbedoMap" not in MF),
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
        set_flag("FDDMaterialSpecular", onlyif="FDDMaterialSpecular" in MF),
        set_flag("FSpecular", features.f_specular_param),

        set_texture("tSphereMap", onlyif=TT.SPHERE in tt),

        set_flag("FReflect", features.f_reflect_param, onlyif=features.f_reflect_enabled),
        set_constant_buffer("CBAppReflect", onlyif="CBAppReflect" in MF),

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

        set_flag("FAppClip", onlyif="FAppClip" in MF),
        set_constant_buffer("CBAppClipPlane", onlyif="CBAppClipPlane" in MF),
        set_flag("FAppOutline", onlyif="FAppOutline" in MF),
        set_constant_buffer("CBOutlineEx", onlyif="CBOutlineEx" in MF),
        set_flag("FIntegratedOutlineColor", onlyif="FIntegratedOutlineColor" in MF),
        set_flag("FDDMaterialFinalCombiner", onlyif="FDDMaterialFinalCombiner" in MF),
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
        "CBBurnCommon", "CBBurnEmission", "CBAppClipPlane", "CBSpecularBlend",
        "CBAppReflect", "CBAppReflectShadowLight", "CBOutlineEx", "CBDDMaterialParam",
        "CBUVRotationOffset", "CBDDMaterialParamInnerCorrect",

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

    elif cb_name == "CBDDMaterialParam":
        float_buffer_parent = Mrl.CbDdMaterialParam(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbDdMaterialParam1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_dd_mat_param"]

    elif cb_name == "CBAppReflectShadowLight":
        float_buffer_parent = Mrl.CbAppReflectShadowLight(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbAppReflectShadowLight1(_parent=float_buffer_parent,
                                                    _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_app_refl_sh_lt"]

    elif cb_name == "CBAppReflect":
        float_buffer_parent = Mrl.CbAppReflect(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbAppReflect1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_app_reflect"]

    elif cb_name == "CBAppClipPlane":
        float_buffer_parent = Mrl.CbAppClipPlane(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbAppClipPlane1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_app_clip_plane"]

    elif cb_name == "CBOutlineEx":
        float_buffer_parent = Mrl.CbOutlineEx(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbOutlineEx1(_parent=float_buffer_parent, _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_outline_ex"]

    elif cb_name == "CBDDMaterialParamInnerCorrect":
        float_buffer_parent = Mrl.CbDdMaterialParamInnerCorrect(_parent=resource, _root=resource._root)
        # Always the same for all apps, no need for map
        float_buffer = Mrl.CbDdMaterialParamInnerCorrect1(_parent=float_buffer_parent,
                                                          _root=float_buffer_parent._root)
        float_buffer_parent.app_specific = float_buffer
        float_buffer_custom_props = custom_props["cb_dd_m_p_inn_cor"]

    float_buffer_custom_props.copy_custom_properties_to(float_buffer)
    float_buffer_parent._check()
    float_buffer._check()
    resource.float_buffer = float_buffer_parent

    return resource


def _gather_tex_types(bl_mat, exported_textures, textures_list, mrl=None, app_id=None):
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
        custom_properties = im_node.image.albam_custom_properties.get_custom_properties_for_appid(app_id)
        image_name = im_node.image.name
        vfile = exported_textures[image_name]["serialized_vfile"]
        relative_path_no_ext = vfile.relative_path.replace(".tex", "")
        relative_path_no_ext = relative_path_no_ext.replace(".rtex", "")
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
                if custom_properties.render_target is True:
                    tex.type_hash = 2013850128  # TYPE_rRenderTargetTexture
                else:
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
    sg.new_socket("Lightmap LM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Use Lightmap", in_out="INPUT", socket_type="NodeSocketInt")
    sg.inputs["Use Lightmap"].min_value = 0
    sg.inputs["Use Lightmap"].max_value = 1
    sg.new_socket("Alpha Mask AM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Use Alpha Mask", in_out="INPUT", socket_type="NodeSocketInt")
    sg.inputs["Use Alpha Mask"].min_value = 0
    sg.inputs["Use Alpha Mask"].max_value = 1
    sg.new_socket("Environment CM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Detail DNM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Detail 2 DNM", in_out="INPUT", socket_type="NodeSocketColor")
    sg.inputs["Detail DNM"].default_value = (1, 0.5, 1, 1)
    sg.inputs["Detail 2 DNM"].default_value = (1, 0.5, 1, 1)
    sg.new_socket("Alpha DNM", in_out="INPUT", socket_type="NodeSocketFloat")
    sg.inputs["Alpha DNM"].default_value = 0.5
    sg.new_socket("Use Detail Map", in_out="INPUT", socket_type="NodeSocketInt")
    sg.inputs["Use Detail Map"].min_value = 0
    sg.inputs["Use Detail Map"].max_value = 1
    sg.new_socket("Special Map", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Vertex Displacement", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Vertex Displacement Mask", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Hair Shift", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Height Map", in_out="INPUT", socket_type="NodeSocketColor")
    sg.new_socket("Emission", in_out="INPUT", socket_type="NodeSocketColor", )

    # Create group outputs
    group_outputs = shader_group.nodes.new("NodeGroupOutput")
    group_outputs.location = (300, -90)
    sg.new_socket("Surface", in_out="OUTPUT", socket_type="NodeSocketShader")

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
    link(use_lightmap.outputs[0], bsdf_shader.inputs["Base Color"])
    link(group_inputs.outputs["Alpha BM"], use_alpha_mask.inputs[1])
    link(use_alpha_mask.outputs[0], bsdf_shader.inputs["Alpha"])
    link(group_inputs.outputs["Normal NM"], normal_separate.inputs[0])
    link(normal_separate.outputs[1], normal_combine.inputs[1])
    link(normal_separate.outputs[2], normal_combine.inputs[2])
    link(group_inputs.outputs["Alpha NM"], normal_combine.inputs[0])
    link(normal_combine.outputs[0], use_detail_map.inputs[1])
    link(normal_combine.outputs[0], separate_rgb_n.inputs[0])

    link(group_inputs.outputs["Specular MM"], invert_spec.inputs[1])
    link(invert_spec.outputs[0], bsdf_shader.inputs["Roughness"])
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
    link(normal_map.outputs[0], bsdf_shader.inputs["Normal"])
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
    attr_enum = bpy.props.EnumProperty(
        name="Attribute",
        description="Select surface attribute",
        items=[
            ("0x1", "ATTR_BRIDGE", "", 1),
            ("0x8", "ATTR_NUKI", "", 2),
            ("0x10", "ATTR_SOLID", "", 3),
            ("0x20", "ATTR_OVERLAP", "", 4),
            ("0x40", "ATTR_TRANSPARENT", "", 5),
        ],
        default="0x10",
        options=set()
    )
    vtype_enum = bpy.props.EnumProperty(
        name="VTYPE",
        description="Select vertex type",
        items=[
            ("0x0", "VTYPE_SKIN", "Skinned mesh with up to 4wt", 1),
            ("0x1", "VTYPE_SKINEX", "Skinned mesh extended", 2),
            ("0x2", "VTYPE_NONSKIN", "Static mesh", 3),
            ("0x3", "VTYPE_NONSKIN_COL", "Static mesh with vertex colors", 4),
            ("0x4", "VTYPE_SHAPE", "", 5),
            ("0x5", "VTYPE_SKIN_COL", "", 6),
        ],
        default="0x0",
        options=set()
    )
    func_skin_enum = bpy.props.EnumProperty(
        name="VSKIN",
        description="Select max bone influences",
        items=[
            ("0x0", "SKIN_NONE", "Static mesh", 1),
            ("0x1", "SKIN_1WT", "1 bone per vertex", 2),
            ("0x2", "SKIN_2WT", "2 bones per vertex", 3),
            ("0x3", "SKIN_4WT", "4 bones per vertex", 4),
            ("0x4", "SKIN_8WT", "8 bones per vertex", 5),
            ("0x5", "SKIN_4WT_SHAPE", "", 6),
            ("0x6", "SKIN_STREAM_OUT", "", 7),
            ("0x7", "SKIN_RESERVE", "", 8),
            ("0x8", "MAX_SKIN", "", 9),
        ],
        default="0x3",
        options=set()
    )
    func_lighting_enum = bpy.props.EnumProperty(
        name="func ligting",
        description="select lighting type",
        items=[
            ("0x0", "LIGHTING_NONE", "", 1),
            ("0x1", "LIGHTING_4SPOT", "", 2),
            ("0x2", "LIGHTING_SH4SPOT", "", 3),
            ("0x3", "LIGHTING_EMITSH4SPOT", "", 4),
            ("0x4", "LIGHTING_THINSH4SPOT", "", 5),
            ("0x5", "LIGHTING_RESERVE0", "", 6),
            ("0x6", "LIGHTING_RESERVE1", "", 7),
            ("0x7", "LIGHTING_RESERVE2", "", 8),
            ("0x8", "LIGHTING_TEX4SPOT", "", 9),
            ("0x9", "MAX_LIGHTING", "", 9),
        ],
        default="0x2",
        options=set()
    )
    func_normalmap_enum = bpy.props.EnumProperty(
        name="func normal map",
        description="Select normal map type",
        items=[
            ("0x0", "NORMALMAP_NONE", "", 1),
            ("0x1", "NORMALMAP_STANDARD", "", 2),
            ("0x2", "NORMALMAP_DETAIL", "", 3),
            ("0x3", "NORMALMAP_PARALLAX", "", 4),
            ("0x4", "MAX_NORMALMAP", "", 5),
        ],
        default="0x1",
        options=set()
    )
    func_specular_enum = bpy.props.EnumProperty(
        name="func specular map",
        description="Select normal map type",
        items=[
            ("0x0", "SPECULAR_NONE", "", 1),
            ("0x1", "SPECULAR_STANDARD", "", 2),
            ("0x2", "SPECULAR_MIRROR", "", 3),
            ("0x3", "SPECULAR_POWMAP", "", 4),
            ("0x4", "SPECULAR_RIM", "", 5),
            ("0x5", "MAX_SPECULAR", "", 6),
        ],
        default="0x1",
        options=set()
    )
    func_lightmap_enum = bpy.props.EnumProperty(
        name="func lightmap",
        description="Select light map type",
        items=[
            ("0x0", "LIGHTMAP_NONE", "", 1),
            ("0x1", "LIGHTMAP_STANDARD", "", 2),
            ("0x2", "LIGHTMAP_SHADOW", "", 3),
            ("0x3", "LIGHTMAP_BLEND", "", 4),
            ("0x4", "LIGHTMAP_BLENDSHADOW", "", 5),
            ("0x5", "LIGHTMAP_VCOLOR", "", 6),
            ("0x6", "LIGHTMAP_HDRVCOLOR", "", 7),
            ("0x7", "LIGHTMAP_TEXCOLOR", "", 8),
            ("0x8", "MAX_LIGHTMAP", "", 9),
        ],
        default="0x0",
        options=set()
    )
    func_multitexture_enum = bpy.props.EnumProperty(
        name="func multitexture",
        description="Select multitexture type",
        items=[
            ("0x0", "MULTITEXTURE_NONE", "", 1),
            ("0x1", "MULTITEXTURE_ALPHA", "", 2),
            ("0x2", "MULTITEXTURE_BASE", "", 3),
            ("0x3", "MULTITEXTURE_FREEZE", "", 4),
            ("0x4", "MULTITEXTURE_VOLUME", "", 5),
            ("0x5", "MULTITEXTURE_SPEC", "", 6),
            ("0x6", "MULTITEXTURE_BLUR", "", 7),
            ("0x7", "MAX_MULTITEXTURE", "", 8),
        ],
        default="0x0",
        options=set()
    )
    fog_enable: bpy.props.BoolProperty(name="Fog Enable", default=True, options=set())  # noqa: F821
    zwrite: bpy.props.BoolProperty(name="Z-write", default=True, options=set())  # noqa: F821
    attr: attr_enum
    num: bpy.props.IntProperty(name="Material Number", default=0, options=set())  # noqa: F821
    envmap_bias: bpy.props.IntProperty(name="Environmental Bias",
                                       default=4, options=set())  # noqa: F821
    vtype: vtype_enum
    uvscroll_enable: bpy.props.BoolProperty(name="UV scroll enable",
                                            default=False, options=set())  # noqa: F821
    ztest: bpy.props.BoolProperty(name="Z-test", default=True, options=set())  # noqa: F821
    func_skin: func_skin_enum
    func_lighting: func_lighting_enum
    func_normalmap: func_normalmap_enum
    func_specular: func_specular_enum
    func_lightmap: func_lightmap_enum
    func_multitexture: func_multitexture_enum
    htechnique: bpy.props.StringProperty(name="H-technique",  # noqa: F821
                                         default="0x8727e606", options=set())  # noqa: F821
    pipeline: bpy.props.IntProperty(name="Pipline", default=379, options=set())  # noqa: F821
    pvdeclbase: bpy.props.IntProperty(name="PV declaration base", default=0, options=set())  # noqa: F821
    pvdecl: bpy.props.StringProperty(name="PV declaration", default="0x0", options=set())  # noqa: F821

    transparency: bpy.props.FloatProperty(name="Transparency", default=1.0, options=set())  # noqa: F821
    fresnel_factor: bpy.props.FloatVectorProperty(
        name="FresnelFactor", size=4, default=(0.0, 0.5, 7.0, 0.6), options=set())  # noqa: F821
    lightmap_factor: bpy.props.FloatVectorProperty(
        name="LightmapFactor",  # noqa: F821
        size=4, default=(1.0, 1.0, 1.0, 0), options=set(), subtype="COLOR")  # noqa: F821
    detail_factor: bpy.props.FloatVectorProperty(
        name="DetailFactor", size=4, default=(0.5, 10, 0.0, 0.5), options=set())  # noqa: F821
    parallax_factor: bpy.props.FloatVectorProperty(
        name="ParalaxFactor", size=2, default=(0.0, 0.0), options=set())  # noqa: F821
    flip_binormal: bpy.props.FloatProperty(name="Flip Binormals", default=1.0, options=set())  # noqa: F821
    heightmap_occ: bpy.props.FloatProperty(name="Heightmap Occlusion",
                                           default=0.2, options=set())  # noqa: F821
    blend_state: bpy.props.IntProperty(name="Blend State", default=44172837, options=set())  # noqa: F821
    alpha_ref: bpy.props.IntProperty(name="Alpha Reference", default=8, options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            if type(getattr(self, attr_name)) is str:
                setattr(dst_obj, attr_name, int(getattr(self, attr_name), 16))
            else:
                setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except TypeError:
                setattr(self, attr_name, hex(getattr(src_obj, attr_name)))


@blender_registry.register_custom_properties_material("mrl_params",
                                                      ("re0", "re1", "re6", "rev1", "rev2", "dd"))
@blender_registry.register_blender_prop
class MrlMaterialCustomProperties(bpy.types.PropertyGroup):  # noqa: F821
    material_type_enum = bpy.props.EnumProperty(
        name="Material Type",
        items=[
            ("TYPE_nDraw__MaterialNull", "MaterialNull", "", 1),
            ("TYPE_nDraw__MaterialStd", "MaterialStd", "", 2),
            ("TYPE_nDraw__MaterialStdEst", "MaterialStdEst", "", 3),
            ("TYPE_nDraw__DDMaterialStd", "DDMaterialStd", "", 4),
            ("TYPE_nDraw__DDMaterialInner", "DDMaterialInne", "", 5),
            ("type_n_draw__dd_material_water", "DDMaterialWater", "", 6),
        ],
        default="TYPE_nDraw__MaterialStd",
        options=set()
    )
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
    material_type: material_type_enum
    blend_state_type: blend_state_enum
    depth_stencil_state_type: depth_stencil_enum
    rasterizer_state_type: rasterizer_state_enum
    reserverd1: bpy.props.IntProperty(
        name="Reserved1",  # noqa: F821
        min=0, max=0x1FF
    )
    id: bpy.props.IntProperty(
        name="ID",  # noqa: F821
        min=0, max=0xFF
    )
    fog: bpy.props.BoolProperty(
        name="Fog",  # noqa: F821
    )
    tangent: bpy.props.BoolProperty(
        name="Tangent",  # noqa: F821
    )
    half_lambert: bpy.props.BoolProperty(
        name="Half Lambert",  # noqa: F821
    )
    stencil_ref: bpy.props.IntProperty(
        name="Stencil Ref",  # noqa: F821
        min=0, max=0xFF
    )
    alphatest_ref: bpy.props.IntProperty(
        name="AlphaTest Ref",  # noqa: F821
        min=0, max=0xFF
    )
    polygon_offset: bpy.props.IntProperty(
        name="Polygon Offset",  # noqa: F821
        description="Polygon Offset (4 bits)",  # noqa: F821
        min=0, max=0xF
    )
    alphatest: bpy.props.BoolProperty(
        name="AlphaTest",  # noqa: F821
    )
    alphatest_func: bpy.props.IntProperty(
        name="AlphaTest Func",  # noqa: F821
        min=0, max=0x7
    )
    draw_pass: bpy.props.IntProperty(
        name="Draw Pass",  # noqa: F821
        min=0, max=0x1F
    )
    layer_id: bpy.props.IntProperty(
        name="Layer ID",  # noqa: F821
        min=0, max=0x3
    )
    deffered_lighting: bpy.props.BoolProperty(
        name="Deferred Lighting",  # noqa: F821
    )
    #  unk_01: bpy.props.IntProperty(name="Unk_01", options=set())  # noqa: F821

    #  unk_flags: bpy.props.IntVectorProperty(
    #    name="Unknown Flags", size=4, default=(0, 0, 128, 140), options=set())

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


@blender_registry.register_custom_properties_material(
    "features", ("re0", "re1", "rev1", "rev2", "re6", "dd"),
    is_secondary=True, display_name="Features")
@blender_registry.register_blender_prop
class FeaturesMaterialCustomProperties(bpy.types.PropertyGroup):
    f_vertex_displacement_param: bpy.props.EnumProperty(
        name="FVertexDisplacement",  # noqa: F821
        items=[
            ("FVertexDisplacement", "Default", "", 1),  # noqa: F821
            ("FVertexDisplacementCurveUV", "FVertexDisplacementCurveUV", "", 2),  # noqa: F821
            ("FVertexDisplacementCurveU", "FVertexDisplacementCurveU", "", 3),  # noqa: F821
            ("FVertexDisplacementCurveV", "FVertexDisplacementCurveV", "", 4),  # noqa: F821
            ("FVertexDisplacementDirUV", "FVertexDisplacementDirUV", "", 5),  # noqa: F821
            ("FVertexDisplacementDirU", "FVertexDisplacementDirU", "", 6),  # noqa: F821
            ("FVertexDisplacementDirV", "FVertexDisplacementDirV", "", 7),  # noqa: F821
        ],
        options=set(),
    )
    f_uv_vertex_displacement_param: bpy.props.EnumProperty(
        name="FUVVertexDisplacement",  # noqa: F821
        items=[
            ("FVDUVPrimary", "FVDUVPrimary", "", 1),  # noqa: F821
            ("FVDUVSecondary", "FVDUVSecondary", "", 2),  # noqa: F821
            ("FVDUVExtend", "FVDUVExtend", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_vd_mask_uv_transform_param: bpy.props.EnumProperty(
        name="FVDMaskUVTransform",  # noqa: F821
        items=[
            ("FVDMaskUVTransform", "Default", "", 1),  # noqa: F821
            ("FVDMaskUVTransformOffset", "FVDMaskUVTransformOffset", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_vd_get_mask_param: bpy.props.EnumProperty(
        name="FVDGetMask",  # noqa: F821
        items=[
            ("FVDGetMask", "Default", "", 1),  # noqa: F821
            ("FVDGetMaskFromAO", "FVDGetMaskFromAO", "", 2),  # noqa: F821
        ],
        options=set()
    )
    f_uv_transform_primary_param: bpy.props.EnumProperty(  # noqa: F82
        name="FUVTransformPrimary",  # noqa: F821
        items=[
            ("FUVTransformPrimary", "Default", "", 1),  # noqa: F821
            ("FUVTransformOffset", "FUVTransformOffset", "", 2),  # noqa: F821
            ("FUVTransformOffset2", "FUVTransformOffset2", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_uv_transform_secondary_param: bpy.props.EnumProperty(
        name="FUVTransformSecondary",  # noqa: F821
        items=[
            ("FUVTransformSecondary", "Default", "", 1),  # noqa: F821
            ("FUVTransformOffset", "FUVTransformOffset", "", 2),  # noqa: F821
            ("FUVTransformOffset2", "FUVTransformOffset2", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_occlusion_param: bpy.props.EnumProperty(
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
            ("FUVIndirect", "FUVIndirect", "", 3),  # noqa: F821
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
            ("FBumpHairNormal", "FBumpHairNormal", "", 6),  # noqa: F821
            ("FBumpNormalMap", "FBumpNormalMap", "", 7),  # noqa: F821
            ("FBumpNormalMapBlendTransparencyMap", "FBumpNormalMapBlendTransparencyMap", "", 8),  # noqa: F821
            ("FBumpParallaxOcclusion", "FBumpParallaxOcclusion", "", 9),  # noqa: F821
            ("FBumpDetailMaskNormalMap", "FBumpDetailMaskNormalMap", "", 10),  # noqa: F821
            ("FBlendBumpDetailNormalMap", "FBlendBumpDetailNormalMap", "", 11),  # noqa: F821
            ("FDamageBumpDetailNormalMap", "FDamageBumpDetailNormalMap", "", 12),  # noqa: F821
        ],
        options=set()
    )
    f_uv_normal_map_param : bpy.props.EnumProperty(
        name="FUVNormalMap",  # noqa: F821
        items=[
            ("FUVNormalMap", "Default", "", 1),  # noqa: F821
            ("FUVPrimary", "FUVPrimary", "", 2),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 3),  # noqa: F821
        ],
        options=set()
    )
    f_uv_detail_normal_map_param : bpy.props.EnumProperty(  # noqa: F82
        name="FUVDetailNormalMap",  # noqa: F821
        items=[
            ("FUVSecondary", "FUVSecondary", "", 1),  # noqa: F821
            ("FUVPrimary", "FUVPrimary", "", 2),  # noqa: F821
            ("FUVUnique", "FUVUnique", "", 3),  # noqa: F821
            ("FUVIndirect", "FUVIndirect", "", 4),  # noqa: F821
        ],
        options=set()
    )
    f_uv_detail_normal_map_2_param : bpy.props.EnumProperty(  # noqa: F82
        name="FUVDetailNormalMap2",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 2),  # noqa: F821
            ("FUVExtend", "FUVExtend", "", 3),  # noqa: F821
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
            ("FColorMaskAlbedoMap", "FColorMaskAlbedoMap", "", 12),  # noqa: F821
            ("FEditSimpleAlbedoMapAlphaMap", "FEditSimpleAlbedoMapAlphaMap", "", 13),  # noqa: F821
            ("FDamageSimpleAlbedoMap", "FDamageSimpleAlbedoMap", "", 14),  # noqa: F821
            ("FAlbedoMapBlendMaxAlpha", "FAlbedoMapBlendMaxAlpha", "", 15),  # noqa: F821
            ("FDamageSimpleAlbedoMapAlphaMap", "FDamageSimpleAlbedoMapAlphaMap", "", 16),  # noqa: F821
            ("FBurnSimpleAlbedoMapBurnMap", "FBurnSimpleAlbedoMapBurnMap", "", 17),  # noqa: F821
            ("FDamageSimpleAlbedoMapBurnMap", "FDamageSimpleAlbedoMapBurnMap", "", 18),  # noqa: F821
            ("FBurnAlbedoMapBurnMap", "FBurnAlbedoMapBurnMap", "", 19),  # noqa: F821
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
            ("FUVIndirect", "FUVIndirect", "", 5),  # noqa: F821
            ("FUVUnique", "FUVUnique", "", 6),  # noqa: F821
            ("FUVExtend", "FUVExtend", "", 7),  # noqa: F821
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
            ("FTransparencyAlphaClip", "FTransparencyAlphaClip", "", 4),  # noqa: F821
            ("FTransparencyMap", "FTransparencyMap", "", 5),  # noqa: F821
            ("FColorMaskTransparencyMap", "FColorMaskTransparencyMap", "", 6),  # noqa: F821
        ],
        options=set()
    )
    f_uv_transparency_map_param : bpy.props.EnumProperty(
        name="FUVTransparencyMap",  # noqa: F821
        items=[
            ("FVDUVPrimary", "FVDUVPrimary", "", 1),  # noqa: F821
            ("FVDUVSecondary", "FVDUVSecondary", "", 2),  # noqa: F821
            ("FVDUVExtend", "FVDUVExtend", "", 3),  # noqa: F821
            ("FUVExtend", "FUVExtend", "", 4),  # noqa: F821
            ("FUVPrimary", "FUVPrimary", "", 5),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 6),  # noqa: F821
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
            ("FBRDFFur", "FBRDFFur", "", 5),  # noqa: F821
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
            ("FDiffuseVertexColorOcclusion", "FDiffuseVertexColorOcclusion", "", 7),  # noqa: F821
            ("FDiffuseThin", "FDiffuseThin", "", 8)  # noqa: F821
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
            ("FDamageSpecularMap", "FDamageSpecularMap", "", 6),  # noqa: F821
        ],
        options=set(),
    )
    f_uv_specular_map_param : bpy.props.EnumProperty(  # noqa: F821
        name="FUVSpecularMap",  # noqa: F821
        items=[
            ("FUVPrimary", "FUVPrimary", "", 1),  # noqa: F821
            ("FUVSecondary", "FUVSecondary", "", 2),  # noqa: F821
            ("FUVUnique", "FUVUnique", "", 3),  # noqa: F821
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
            ("FReflectCubeMapShadowLight", "FReflectCubeMapShadowLight", "", 5),  # noqa: F821
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
            ("FBurnEmissionMapBlend", "FBurnEmissionMapBlend", "", 4),  # noqa: F821
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
    "cb_material", ("re0", "re1", "rev1", "rev2", "re6", "dd"),
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
    is_secondary=True, display_name="CB Vertex Displacement 2")
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
        # TODO: warning of missing attributes
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except AttributeError:
                print(f"{attr_name} not found on source object {src_obj}")


@blender_registry.register_custom_properties_material(
    "cb_burn_common", ("dd",),
    is_secondary=True, display_name="CB Burn Common")
@blender_registry.register_blender_prop
class CBBurnCommon(bpy.types.PropertyGroup):
    f_b_blend_map_color: bpy.props.FloatVectorProperty(
        name="fBBlendMapColor", size=3, subtype="COLOR", options=set())  # noqa: F821
    f_b_alpha_clip_threshold: bpy.props.FloatProperty(
        name="fBAlphaClipThreshold", options=set())  # noqa: F821
    f_b_blend_alpha_threshold: bpy.props.FloatProperty(
        name="fBBlendAlphaThreshold", options=set())  # noqa: F821
    f_b_blend_alpha_band: bpy.props.FloatProperty(
        name="fBBlendAlphaBand", options=set())  # noqa: F821
    f_b_specular_blend_rate: bpy.props.FloatProperty(
        name="fBSpecularBlendRate", options=set())  # noqa: F821
    f_b_albedo_blend_rate: bpy.props.FloatProperty(
        name="fBAlbedoBlendRate", options=set())  # noqa: F821
    f_b_albedo_blend_rate2: bpy.props.FloatProperty(
        name="fBAlbedoBlendRate2", options=set())  # noqa: F821
    padding: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0), options={"HIDDEN"})  # noqa: F821

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
    "cb_burn_emission", ("dd",),
    is_secondary=True, display_name="CB Burn Emission")
@blender_registry.register_blender_prop
class CBBurnEmission(bpy.types.PropertyGroup):
    f_b_emission_factor: bpy.props.FloatProperty(
        name="fBEmissionFactor", options=set())  # noqa: F821
    f_b_emission_alpha_band: bpy.props.FloatProperty(
        name="fBEmissionAlphaBand", options=set())  # noqa: F821
    padding_1: bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821
    f_burn_emission_color: bpy.props.FloatVectorProperty(
        name="fBurnEmissionColor", size=3, subtype="COLOR", options=set())  # noqa: F821
    padding_2: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821

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
    "cb_app_clip_plane", ("dd",),
    is_secondary=True, display_name="CB Clip Plane")
@blender_registry.register_blender_prop
class CBAppClipPlane(bpy.types.PropertyGroup):
    f_plane_normal: bpy.props.FloatVectorProperty(
        name="fPlaneNormal", size=3, subtype="COLOR", options=set())  # noqa: F821
    padding_1: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_plane_point: bpy.props.FloatVectorProperty(
        name="fPlanePoint", size=3, subtype="COLOR", options=set())  # noqa: F821
    padding_2: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_app_clip_mask: bpy.props.FloatProperty(
        name="fAppClipMask", options=set())  # noqa: F821
    padding_3: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821

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
    "cb_specular_blend", ("dd",),
    is_secondary=True, display_name="CB Specular Blend")
@blender_registry.register_blender_prop
class CBSpecularBlend(bpy.types.PropertyGroup):
    f_plane_normal: bpy.props.FloatVectorProperty(
        name="fPlaneNormal", size=4, subtype="COLOR", options=set())  # noqa: F821

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
    "cb_app_reflect", ("dd",),
    is_secondary=True, display_name="CB App Reflect")
@blender_registry.register_blender_prop
class CBAppReflect(bpy.types.PropertyGroup):
    f_app_water_reflect_scale: bpy.props.FloatProperty(
        name="fAppWaterReflectScale", options=set())  # noqa: F821
    f_app_shadow_light_scale: bpy.props.FloatProperty(
        name="fAppShadowLightScale", options=set())  # noqa: F821
    padding: bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821

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
    "cb_app_refl_sh_lt", ("dd",),  # cb_app_reflect_shadow_light
    is_secondary=True, display_name="CB App Reflect Shadow Light")
@blender_registry.register_blender_prop
class CBAppReflectShadowLight(bpy.types.PropertyGroup):
    f_app_reflect_shadow_dir: bpy.props.FloatVectorProperty(
        name="fAppReflectShadowDir", size=3, subtype="COLOR", options=set())  # noqa: F821
    padding: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821

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
    "cb_outline_ex", ("dd",),
    is_secondary=True, display_name="CB Outline Ex")
@blender_registry.register_blender_prop
class CBOutlineEx(bpy.types.PropertyGroup):
    f_outline_outer_color: bpy.props.FloatVectorProperty(
        name="fOutlineOuterColor", size=4, subtype="COLOR", options=set())  # noqa: F821
    f_outline_inner_color: bpy.props.FloatVectorProperty(
        name="fOutlineInnerColor", size=4, subtype="COLOR", options=set())  # noqa: F821
    f_outline_balance_offset: bpy.props.FloatProperty(
        name="fOutlineBalanceOffset", options=set())  # noqa: F821
    f_outline_balance_scale: bpy.props.FloatProperty(
        name="fOutlineBalanceScale", options=set())  # noqa: F821
    f_outline_balance: bpy.props.FloatProperty(
        name="fOutlineBalance", options=set())  # noqa: F821
    padding: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_outline_blend_mask: bpy.props.FloatVectorProperty(
        name="fOutlineBlendMask", size=4, subtype="COLOR", options=set())  # noqa: F821

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
    "cb_dd_mat_param", ("dd",),  # cb_dd_material_param
    is_secondary=True, display_name="CB DD Material Param")
@blender_registry.register_blender_prop
class CBDDMaterialParam(bpy.types.PropertyGroup):
    f_dd_material_blend_color: bpy.props.FloatVectorProperty(
        name="fDDMaterialBlendColor", size=4, subtype="COLOR", options=set())  # noqa: F821
    f_dd_material_color_blend_rate: bpy.props.FloatVectorProperty(
        name="fDDMaterialColorBlendRate", size=2, options=set())  # noqa: F821
    f_dd_material_area_mask: bpy.props.FloatVectorProperty(
        name="fDDMaterialAreaMask", size=2, options=set())  # noqa: F821
    f_dd_material_border_blend_mask: bpy.props.FloatVectorProperty(
        name="fDDMaterialBorderBlendMask", size=4, subtype="COLOR", options=set())  # noqa: F821
    f_dd_material_border_shade_band: bpy.props.FloatProperty(
        name="fDDMaterialBorderShadeBand", options=set())  # noqa: F821
    f_dd_material_base_power: bpy.props.FloatProperty(
        name="fDDMaterialBasePower", options=set())  # noqa: F821
    f_dd_material_normal_blend_rate: bpy.props.FloatProperty(
        name="fDDMaterialNormalBlendRate", options=set())  # noqa: F821
    f_dd_material_reflect_blend_color: bpy.props.FloatProperty(
        name="fDDMaterialReflectBlendColor", options=set())  # noqa: F821
    f_dd_material_specular_factor: bpy.props.FloatProperty(
        name="fDDMaterialSpecularFactor", options=set())  # noqa: F821
    f_dd_material_specular_map_factor: bpy.props.FloatProperty(
        name="fDDMaterialSpecularMapFactor", options=set())  # noqa: F821
    f_dd_material_env_map_blend_color: bpy.props.FloatProperty(
        name="fDDMaterialEnvMapBlendColor", options=set())  # noqa: F821
    f_dd_material_area_alpha: bpy.props.FloatProperty(
        name="fDDMaterialAreaAlpha", options=set())  # noqa: F821
    f_dd_material_area_pos: bpy.props.FloatVectorProperty(
        name="fDDMaterialAreaPos", size=4, options=set())  # noqa: F821
    f_dd_material_albedo_uv_scale: bpy.props.FloatProperty(
        name="fDDMaterialAlbedoUVScale", options=set())  # noqa: F821
    f_dd_material_normal_uv_scale: bpy.props.FloatProperty(
        name="fDDMaterialNormalUVScale", options=set())  # noqa: F821
    f_dd_material_normal_power: bpy.props.FloatProperty(
        name="fDDMaterialNormalPower", options=set())  # noqa: F821
    f_dd_material_base_env_map_power: bpy.props.FloatProperty(
        name="fDDMaterialBaseEnvMapPower", options=set())  # noqa: F821
    f_dd_material_lantern_color: bpy.props.FloatVectorProperty(
        name="fDDMaterialLanternColor", size=3, subtype="COLOR", options=set())  # noqa: F821
    padding_1: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_dd_material_lantern_pos: bpy.props.FloatVectorProperty(
        name="fDDMaterialLanternPos", size=3, options=set())  # noqa: F821
    padding_2: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_dd_material_lantern_param: bpy.props.FloatVectorProperty(
        name="fDDMaterialLanternParam", size=3, options=set())  # noqa: F821
    padding_3: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821

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
    "cb_uv_rot_offset", ("dd",),  # cb_uv_rotation_offset
    is_secondary=True, display_name="CB UV Rotation Offset")
@blender_registry.register_blender_prop
class CBUVRotationOffset(bpy.types.PropertyGroup):
    f_uv_rotation_center: bpy.props.FloatVectorProperty(
        name="fUVRotationCenter", size=2, options=set())  # noqa: F821
    f_uv_rotation_angle: bpy.props.FloatVectorProperty(
        name="fUVRotationAngle", size=2, options=set())  # noqa: F821
    padding: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_uv_rotation_offset: bpy.props.FloatVectorProperty(
        name="fUVRotationOffset", size=2, options=set())   # noqa: F821
    f_uv_rotation_scale: bpy.props.FloatVectorProperty(
        name="fUVRotationScale", size=2, options=set())  # noqa: F821

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
    "cb_dd_m_p_inn_cor",  # cb_dd_material_param_inner_correct
    ("dd",),
    is_secondary=True, display_name="CB DD Material Param Inner Correct")
@blender_registry.register_blender_prop
class CBDDMaterialParamInnerCorrect(bpy.types.PropertyGroup):
    f_dd_material_inner_correct_offset: bpy.props.FloatProperty(
        name="fDDMaterialInnerCorrectOffset", default=0, options=set())  # noqa: F821
    padding: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0), options={"HIDDEN"})  # noqa: F821

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
    padding_1: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
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

    padding_2: bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821

    f_light_map_color: bpy.props.FloatVectorProperty(
        name="fLightMapColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_3: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821

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
    padding_4: bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821
    f_primary_color: bpy.props.FloatVectorProperty(
        name="fPrimaryColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_5: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_secondary_color: bpy.props.FloatVectorProperty(
        name="fSecondaryColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_6: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_albedo_color_2: bpy.props.FloatVectorProperty(
        name="fAlbedoColor2", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_7: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_specular_color_2: bpy.props.FloatVectorProperty(
        name="fSpecularColor2", default=(0.5, 0.5, 0.5), subtype="COLOR", options=set())  # noqa: F821
    f_fresnel_schlick_2: bpy.props.FloatProperty(
        name="fFresnelSchlick2", default=1, options=set())  # noqa: F821
    f_shininess_2: bpy.props.FloatProperty(
        name="fShininess2", default=30, options=set())  # noqa: F821
    padding_8: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0), options={"HIDDEN"})  # noqa: F821
    f_transparency_clip_threshold: bpy.props.FloatVectorProperty(
        name="fTransparencyClipThreshold", size=4, default=(0, 0, 0, 0), options=set())  # noqa: F821
    f_blend_uv: bpy.props.FloatProperty(
        name="fBlendUV", default=1, options=set())  # noqa: F821
    padding_9: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0), options={"HIDDEN"})  # noqa: F821
    f_albedo_blend2_color: bpy.props.FloatVectorProperty(
        name="fAlbedoBlend2Color", size=4, default=(1, 1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_detail_normalu_vscale: bpy.props.FloatVectorProperty(
        name="fDetailNormalU_VScale", size=2, default=(0, 0), options=set())  # noqa: F821
    padding_10: bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821

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
    ("dd",), is_secondary=True, display_name="$Globals")
@blender_registry.register_blender_prop
class GlobalsCustomProperties4(bpy.types.PropertyGroup):
    f_albedo_color: bpy.props.FloatVectorProperty(
        name="fAlbedoColor", default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_1: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
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
    padding_2: bpy.props.FloatVectorProperty(size=2, default=(0, 0), options={"HIDDEN"})  # noqa: F821
    f_light_map_color: bpy.props.FloatVectorProperty(
        name="fLightMapColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_3: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
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
    f_roughness: bpy.props.FloatProperty(
        name="fRoughness", default=1, options=set())  # noqa: F821
    f_roughness_rgb: bpy.props.FloatVectorProperty(
        name="fRoughnessRGB", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    f_anisotoropic_direction: bpy.props.FloatVectorProperty(
        name="fAnisotoropicDirection",  # noqa: F821
        size=3, default=(1, 1, 1),
        subtype="COLOR", options=set())  # noqa: F821
    f_smoothness: bpy.props.FloatProperty(
        name="fSmoothness", default=1, options=set())  # noqa: F821
    f_anistropic_uv: bpy.props.FloatVectorProperty(
        name="fAnistropicUV", size=2, options=set())  # noqa: F821
    f_primary_expo: bpy.props.FloatProperty(
        name="fPrimaryExpo", default=1, options=set())  # noqa: F821
    f_secondary_expo: bpy.props.FloatProperty(
        name="fSecondaryExpo", default=0.2, options=set())  # noqa: F821
    f_primary_color: bpy.props.FloatVectorProperty(
        name="fPrimaryColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_4: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    f_secondary_color: bpy.props.FloatVectorProperty(
        name="fSecondaryColor", size=3, default=(1, 1, 1), subtype="COLOR", options=set())  # noqa: F821
    padding_5: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    xyzw_sepalate: bpy.props.FloatVectorProperty(
        name="xyzwSepalate", size=16, options=set())  # noqa: F821

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
