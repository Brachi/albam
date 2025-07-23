from enum import Enum
import io
import functools
from pathlib import PureWindowsPath
import math

import bpy
from kaitaistruct import KaitaiStream

from albam.exceptions import AlbamCheckFailure
from albam.lib.blender import (
    get_bl_teximage_nodes,
    get_bl_materials,
    is_blimage_dds,
)
from albam.lib.dds import DDSHeader
from albam.registry import blender_registry
from albam.vfs import VirtualFileData
# from .defines import get_shader_objects
from .structs.tex_112 import Tex112
from .structs.tex_157 import Tex157
from .structs.rtex_112 import Rtex112
from .structs.rtex_157 import Rtex157
from .structs.mrl import Mrl


class TextureType2(Enum):  # TODO: unify
    # TODO: complete
    DIFFUSE = 20
    SPECULAR = 25
    NORMAL = 31


class TextureType(Enum):  # TODO: TextureTypeSlot
    DIFFUSE = 1
    NORMAL = 2
    SPECULAR = 3
    LIGHTMAP = 4
    UNK_01 = 5
    ALPHAMAP = 6
    ENVMAP = 7
    NORMAL_DETAIL = 8
    #  HERE ends RE5 support
    ALBEDO_BLEND = 9
    VERTEX_DISPLACEMENT = 10
    VERTEX_DISPLACEMENT_MASK = 11
    HAIR_SHIFT = 12
    EMISSION = 13
    ALBEDO_BLEND_2 = 14
    HEIGHTMAP = 15
    TRANSPARENCY_MAP = 16
    NORMAL_BLEND = 17
    OCCLUSION = 18
    SPHERE = 19
    NORMAL_DETAIL_2 = 20
    INDIRECT = 21
    SPECULAR_BLEND = 22


TEX_TYPE_MAP_2 = {
    "basemap": TextureType.DIFFUSE,
    "normalmap": TextureType.NORMAL,
    "maskmap": TextureType.SPECULAR,
    "lightmap": TextureType.LIGHTMAP,
    "shadowmap": TextureType.UNK_01,
    "additionalmap": TextureType.ALPHAMAP,
    "envmap": TextureType.ENVMAP,
    "detailmap": TextureType.NORMAL_DETAIL,
    "occlusionmap": TextureType.ALBEDO_BLEND,
    "talbedomap": TextureType.DIFFUSE,
    "talbedoblendmap": TextureType.ALBEDO_BLEND,
    "talbedoblend2map": TextureType.ALBEDO_BLEND_2,
    "tnormalmap": TextureType.NORMAL,
    "tdetailnormalmap": TextureType.NORMAL_DETAIL,
    "tdetailnormalmap2": TextureType.NORMAL_DETAIL_2,
    "tspecularmap": TextureType.SPECULAR,
    "tenvmap": TextureType.ENVMAP,
    "tvtxdisplacement": TextureType.VERTEX_DISPLACEMENT,
    "tvtxdispmask": TextureType.VERTEX_DISPLACEMENT_MASK,
    "thairshiftmap": TextureType.HAIR_SHIFT,
    "temissionmap": TextureType.EMISSION,
    "theightmap": TextureType.HEIGHTMAP,
    "tlightmap": TextureType.LIGHTMAP,
    "ttransparencymap": TextureType.TRANSPARENCY_MAP,
    "tnormalblendmap": TextureType.NORMAL_BLEND,
    "tocclusionmap": TextureType.OCCLUSION,
    "tspheremap": TextureType.SPHERE,
    "tindirectmap": TextureType.INDIRECT,
    "tspecularblendmap": TextureType.SPECULAR_BLEND,
}


NODE_NAMES_TO_TYPES = {
    'Diffuse BM': TextureType.DIFFUSE,
    'Normal NM': TextureType.NORMAL,
    'Specular MM': TextureType.SPECULAR,
    'Lightmap LM': TextureType.LIGHTMAP,
    'Alpha Mask AM': TextureType.ALPHAMAP,
    'Environment CM': TextureType.ENVMAP,
    'Detail DNM': TextureType.NORMAL_DETAIL,
    'Detail 2 DNM': TextureType.NORMAL_DETAIL_2,
    'Special Map': TextureType.UNK_01,
    'Albedo Blend BM': TextureType.ALBEDO_BLEND,
    'Albedo Blend 2 BM': TextureType.ALBEDO_BLEND_2,
    'Vertex Displacement': TextureType.VERTEX_DISPLACEMENT,
    'Vertex Displacement Mask': TextureType.VERTEX_DISPLACEMENT_MASK,
    'Hair Shift': TextureType.HAIR_SHIFT,
    'Height Map': TextureType.HEIGHTMAP,
    'Emission': TextureType.EMISSION,
}

NODE_NAMES_TO_TYPES_2 = {  # TODO: unify
    'Diffuse BM': TextureType2.DIFFUSE,
    'Normal NM': TextureType2.NORMAL,
    'Specular MM': TextureType2.SPECULAR,
    'Detail DNM': TextureType2.NORMAL
}


TEX_FORMAT_MAPPER = {
    2: b"DXT1",  # FIXME: unchecked
    14: b"",  # uncompressed
    19: b"DXT1",  # BM/Diffuse without alpha
    20: b"DXT1",  # ? env cubemap in RE1, env spheremap in RE0
    23: b"DXT5",  # BM/Diffuse with alpha
    24: b"DXT5",  # BM/Diffuse (UI?)
    25: b"DXT1",  # MM/Specular
    31: b"DXT5",  # NM/Normal
    32: b"DXT5",
    35: b"DXT5",
    39: b"",  # uncompressed
    40: b"",  # uncompressed
    43: b"DXT1",  # FIXME: unchecked
    "DXT1": b"DXT1",
    "DXT3": b"DXT3",
    "DXT5": b"DXT5",
    '\x15\x00\x00\x00': b"",
}

# FIXME: take into account type of texture (BM/NM/MM, etc.)
DDS_FORMAT_MAP = {
    b"DXT1": 20,
    b"DXT5": 31,
}

APPID_SERIALIZE_MAPPER = {
    "re0": lambda: _serialize_texture_21,
    "re1": lambda: _serialize_texture_21,
    "re5": lambda: _serialize_texture_156,
    "re6": lambda: _serialize_texture_21,
    "rev1": lambda: _serialize_texture_21,
    "rev2": lambda: _serialize_texture_21,
    "dd": lambda: _serialize_texture_21,
}

APPID_TEXCLS_MAP = {
    "re0": Tex157,
    "re1": Tex157,
    "re5": Tex112,
    "re6": Tex157,
    "rev1": Tex157,
    "rev2": Tex157,
    "dd": Tex157,
}

APPID_RTEXCLS_MAP = {
    "re0": Rtex157,
    "re1": Rtex157,
    "re5": Rtex112,
    "re6": Rtex157,
    "rev1": Rtex157,
    "rev2": Rtex157,
    "dd": Rtex157,
}

TEX_TYPE_MAPPER = {
    0xcd06f: TextureType.DIFFUSE,
    0x22660: TextureType.NORMAL,
    0xaa6f0: TextureType.LIGHTMAP,
    0xed1b: TextureType.SPECULAR,
    0x75a53: TextureType.NORMAL_DETAIL,
    0x64c43: TextureType.ENVMAP,
    0x1698a: TextureType.ALPHAMAP,  # tTransparencyMap
    0xff5be: TextureType.UNK_01,  # tAlbedoBlendMap
    # 0x1cb2a: TextureType.UNK_01, # ttHairShiftMap
    # 0xed93b: TextureType.UNK_01, # tEmissionMap
    # 0xa9787: TextureType.UNK_01, # tShininessMap
    # 0x39c0:  TextureType.UNK_01, # tVtxDispMask
    # 0x4934a: TextureType.UNK_01, # tVtxDisplacement
    # 0xed6be: TextureType.UNK_01, # tNormalBlendMap
    # 0x1e421: TextureType.UNK_01, # tOcclusionMap
    # 0x343f4: TextureType.UNK_01, # tSphereMap
    # 0x57C1C: TextureType.UNK_01, # not in rev2 mxt
    # 0x6ab7e: TextureType.UNK_01, # tIndirectMap
    # 0x181cf: TextureType.UNK_01, # tSpecularBlendMap
    # 0xd4694: TextureType.UNK_01, # tDetailNormalMap2
    # 0x7b571: TextureType.UNK_01, # tHeightMap
    # 0x5f2a:  TextureType.UNK_01, # tThinMap
    # 0xc3df7: TextureType.UNK_01, # not in re6 mxt
    # 0x88165: TextureType.UNK_01, # tDetailMaskMap
    # 0x7e9aa: TextureType.UNK_01, # not in re6 mxt
    # 0x62fde: TextureType.UNK_01, # not in re6 mxt
    # 0x52e1:  TextureType.UNK_01, # not in re6 mxt
}

NON_SRGB_IMAGE_TYPE = [2, 8]


def build_blender_textures(app_id, context, parsed_mod, mrl=None):
    textures = []

    src_textures = getattr(parsed_mod.materials_data, "textures", None) or getattr(mrl, "textures", None)
    if not src_textures:
        return textures
    TexCls = APPID_TEXCLS_MAP[app_id]
    RtexCls = APPID_RTEXCLS_MAP[app_id]

    for i, texture_slot in enumerate(src_textures):
        texture_path = getattr(texture_slot, "texture_path", None) or texture_slot
        texture_type = getattr(texture_slot, "type_hash", None)
        is_rtex = False
        ext = ".tex"
        if RtexCls == Rtex157 and texture_type == 2013850128:
            is_rtex = True
            ext = ".rtex"
        try:
            texture_vfile = context.scene.albam.vfs.get_vfile(app_id, texture_path + ext)
            tex_bytes = texture_vfile.get_bytes()
        except KeyError:
            tex_bytes = None
        if RtexCls == Rtex112 and not tex_bytes:
            try:
                texture_vfile = context.scene.albam.vfs.get_vfile(app_id, texture_path + ".rtex")
                tex_bytes = texture_vfile.get_bytes()
                is_rtex = True
            except KeyError:
                tex_bytes = None
        if not tex_bytes:
            print(f"texture_path {texture_path} not found in arc")
            textures.append(None)
            # TODO: handle missing texture
            continue
        if is_rtex:
            tex = RtexCls.from_bytes(tex_bytes)
        else:
            tex = TexCls.from_bytes(tex_bytes)
        tex._read()
        if not is_rtex:
            try:
                compression_fmt = TEX_FORMAT_MAPPER[tex.compression_format]
                dds_header = DDSHeader(
                    dwHeight=tex.height,
                    dwWidth=tex.width,
                    pixelfmt_dwFourCC=compression_fmt,
                    dwMipMapCount=tex.num_mipmaps_per_image
                )
                dds_header.set_constants()
                dds_header.set_variables(compressed=bool(compression_fmt), cubemap=tex.num_images > 1)
                dds = bytes(dds_header) + tex.dds_data
            except Exception as err:
                # TODO: log this instead of printing it
                print(f'Error converting "{texture_path}" to dds: {err}')
                textures.append(None)
                continue

        tex_name = PureWindowsPath(texture_path).name
        if is_rtex:
            bl_image = bpy.data.images.new(f"{tex_name}.rtex", tex.width, tex.height)
            bl_image.generated_type = 'UV_GRID'
            bl_image.albam_asset.app_id = app_id
            bl_image.albam_asset.relative_path = texture_path + ".rtex"
            bl_image.albam_asset.extension = "rtex"
        else:
            bl_image = bpy.data.images.new(f"{tex_name}.dds", tex.width, tex.height)
            bl_image.source = "FILE"
            bl_image.pack(data=dds, data_len=len(dds))

            bl_image.albam_asset.original_bytes = tex_bytes
            bl_image.albam_asset.app_id = app_id
            bl_image.albam_asset.relative_path = texture_path + ".tex"
            bl_image.albam_asset.extension = "tex"

        custom_properties = bl_image.albam_custom_properties.get_custom_properties_for_appid(app_id)
        custom_properties.set_from_source(tex)

        textures.append(bl_image)

    if len(src_textures) != len(textures):
        import ntpath
        from pprint import pprint
        a = {ntpath.basename(t.texture_path) for t in src_textures}
        b = {t.name for t in textures if t}
        pprint(list(zip(sorted(a), sorted(b))))
        pprint(sorted(b))
    return textures


def assign_textures(mtfw_material, bl_material, textures, mrl):
    if not mrl:
        old_assignment(mtfw_material, bl_material, textures)
        return
    set_texture_resources = [(r, i) for i, r in enumerate(mtfw_material.resources)
                             if r.cmd_type == Mrl.CmdType.set_texture]

    assert len(mrl.textures) == len(textures), f"{len(mrl.textures)} != {len(textures)}"
    for ri, (resource, i) in enumerate(set_texture_resources):
        tex_index = resource.value_cmd.tex_idx
        real_tex_index = tex_index - 1
        try:
            resource.shader_object_hash.name
        except AttributeError:
            print(resource.shader_object_hash)
            continue
        tex_type_mtfw = resource.shader_object_hash.name
        try:
            tex_type_blender = TEX_TYPE_MAP_2.get(tex_type_mtfw)
            if not tex_type_blender:
                print("         Unknown tex type: ", tex_type_mtfw)
                continue

            if tex_index > 0:
                texture_target = textures[real_tex_index]
            else:
                texture_target = None

            texture_node = bl_material.node_tree.nodes.new("ShaderNodeTexImage")
            if texture_target is not None:
                texture_node.image = texture_target
            texture_code_to_blender_texture(tex_type_blender.value, texture_node, bl_material)
            if texture_node.image and tex_type_blender.value in NON_SRGB_IMAGE_TYPE:
                try:
                    texture_node.image.colorspace_settings.name = "Non-Color"
                except AttributeError:
                    print("Missing texture")
        except IndexError:
            print(f"tex_index {tex_index} not found. Texture len(): {len(textures)}")
            continue


def old_assignment(mtfw_material, bl_material, textures, from_mrl=False):
    for texture_type in TextureType:
        if texture_type.value > 8:
            break
        tex_index = _find_texture_index(mtfw_material, texture_type, from_mrl)
        if tex_index == 0:
            continue
        try:
            texture_target = textures[tex_index - 1]
        except IndexError:
            print(f"tex_index {tex_index} not found. Texture len(): {len(textures)}")
            continue
        if texture_target is None:
            # This means the conversion failed before
            continue
        texture_node = bl_material.node_tree.nodes.new("ShaderNodeTexImage")
        texture_node.image = texture_target
        texture_code_to_blender_texture(texture_type.value, texture_node, bl_material)
        # change color settings for normal and detail maps
        if texture_node.image and texture_type.value in NON_SRGB_IMAGE_TYPE:
            texture_node.image.colorspace_settings.name = "Non-Color"


def _find_texture_index(mtfw_material, texture_type, from_mrl=False):
    tex_index = 0
    tex_slot = ""
    for tex_type, tex_value in TEX_TYPE_MAP_2.items():
        if tex_value == texture_type:
            tex_slot = tex_type
            break
    tex_index = getattr(mtfw_material, tex_slot)
    return tex_index


def texture_code_to_blender_texture(texture_code, blender_texture_node, blender_material):
    """
    Function for detecting texture type and map it to blender shader sockets
    texture_code : index for detecting type of a texture
    blender_texture_node : image texture node
    blender_material : shader material
    """
    # blender_texture_node.use_map_alpha = True
    shader_node_grp = blender_material.node_tree.nodes.get("MTFrameworkGroup")
    link = blender_material.node_tree.links.new

    if texture_code == 1:
        # Diffuse _BM
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Diffuse BM"])
        link(blender_texture_node.outputs["Alpha"], shader_node_grp.inputs["Alpha BM"])
        blender_texture_node.location = (-300, 350)
        # blender_texture_node.use_map_color_diffuse = True
    elif texture_code == 2:
        # Normal _NM
        blender_texture_node.location = (-300, 0)
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Normal NM"])
        link(blender_texture_node.outputs["Alpha"], shader_node_grp.inputs["Alpha NM"])

    elif texture_code == 3:
        # Specular _MM
        blender_texture_node.location = (-300, -350)
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Specular MM"])

    elif texture_code == 4:
        # Lightmap _LM
        blender_texture_node.location = (-300, -700)
        uv_map_node = blender_material.node_tree.nodes.new("ShaderNodeUVMap")
        uv_map_node.location = (-500, -700)
        uv_map_node.uv_map = "uv2"
        link(uv_map_node.outputs[0], blender_texture_node.inputs[0])
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Lightmap LM"])
        shader_node_grp.inputs["Use Lightmap"].default_value = 1

    elif texture_code == 5:
        # Lightmap with Alpha mask in Re5
        blender_texture_node.location = (-300, -1050)
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Special Map"])

    elif texture_code == 6:
        # Alpha mask _AM
        blender_texture_node.location = (-300, -1400)
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Alpha Mask AM"])
        shader_node_grp.inputs["Use Alpha Mask"].default_value = 1

    elif texture_code == 7:
        # Enviroment _CM
        blender_texture_node.location = (-800, -350)
        link(blender_texture_node.outputs['Color'], shader_node_grp.inputs["Environment CM"])

    elif texture_code == 8:
        # Detail normal map
        blender_texture_node.location = (-300, -1750)
        tex_coord_node = blender_material.node_tree.nodes.new("ShaderNodeTexCoord")
        tex_coord_node.location = (-700, -1750)
        mapping_node = blender_material.node_tree.nodes.new("ShaderNodeMapping")
        mapping_node.location = (-500, -1750)

        link(tex_coord_node.outputs[2], mapping_node.inputs[0])
        link(mapping_node.outputs[0], blender_texture_node.inputs[0])
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Detail DNM"])
        link(blender_texture_node.outputs["Alpha"], shader_node_grp.inputs["Alpha DNM"])

        shader_node_grp.inputs["Use Detail Map"].default_value = 1
        # TODO move it to function
        # Link the material properites value
        for x in range(3):
            d = mapping_node.inputs[3].driver_add("default_value", x)
            var1 = d.driver.variables.new()
            var1.name = "detail_multiplier"
            var1.targets[0].id_type = "MATERIAL"
            var1.targets[0].id = blender_material
            var1.targets[0].data_path = 'albam_custom_properties.re5__mod_156_material.detail_factor[1]'
            d.driver.expression = var1.name

    elif texture_code == 9:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Albedo Blend BM"])
        blender_texture_node.location = (-600, 350)

    elif texture_code == 14:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Albedo Blend 2 BM"])
        blender_texture_node.location = (-900, 350)

    elif texture_code == 10:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Vertex Displacement"])
        blender_texture_node.location = (-600, -1800)

    elif texture_code == 11:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Vertex Displacement Mask"])
        blender_texture_node.location = (-600, -1850)

    elif texture_code == 12:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Hair Shift"])
        blender_texture_node.location = (-600, -1900)

    elif texture_code == 13:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Emission"])
        blender_texture_node.location = (-600, -1950)

    elif texture_code == 15:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Height Map"])
        blender_texture_node.location = (-600, -700)

    elif texture_code == 20:
        link(blender_texture_node.outputs["Color"], shader_node_grp.inputs["Detail 2 DNM"])
        blender_texture_node.location = (-600, -800)

    else:
        print("texture_code not supported", texture_code)


def serialize_textures(app_id, bl_materials):
    # XXX Only works with `MT Framework shader`, and no checks performed yet
    exported_textures = get_bl_teximage_nodes(bl_materials)
    serialize_func = APPID_SERIALIZE_MAPPER[app_id]()

    bad_appid = []
    for im_name, data in exported_textures.items():
        if data["image"].albam_asset.app_id != app_id:
            bad_appid.append((im_name, data["image"].albam_asset.app_id))
    if bad_appid:
        raise AttributeError(
            f"The following images have an incorrect app_id (needs: {app_id}): {bad_appid}\n"
            "Go to Image -> tools -> Albam and select the proper app_id for each."
        )

    for dict_tex in exported_textures.values():
        vfile = serialize_func(app_id, dict_tex)
        dict_tex["serialized_vfile"] = vfile

    return exported_textures


def _serialize_texture_156(app_id, dict_tex):
    bl_im = dict_tex["image"]
    custom_properties = bl_im.albam_custom_properties.get_custom_properties_for_appid(app_id)
    # is_rtex = bl_im.albam_asset.render_target
    is_rtex = custom_properties.render_target

    if is_rtex:
        tex = Rtex112()
        tex.id_magic = b"RTX\x00"
        tex.version = 112
        # tex.revision = 514
        tex.num_mipmaps_per_image = int(math.log(max(bl_im.size[0], bl_im.size[1]), 2)) + 1
        tex.num_images = 1
        tex.width = bl_im.size[0]
        tex.height = bl_im.size[1]
        # tex.reserved = 0
        tex.compression_format = b"\x15\x00\x00\x00".decode("ascii")
        dds_data_len = 0
    else:
        dds_header = DDSHeader.from_bl_image(bl_im)
        tex = Tex112()
        tex.id_magic = b"TEX\x00"
        tex.version = 112
        #  revision = 34
        # if dds_header.image_count > 1:
        #    revision = 3
        # tex.revision = revision
        tex.num_mipmaps_per_image = dds_header.dwMipMapCount
        tex.num_images = dds_header.image_count
        tex.width = bl_im.size[0]
        tex.height = bl_im.size[1] // dds_header.image_count  # cubemaps are a vertical strip in Blender

        fmt = dds_header.pixelfmt_dwFourCC.decode()
        if fmt == "":
            fmt = b"\x15\x00\x00\x00".decode("ascii")
        tex.compression_format = fmt
        tex.cube_faces = [] if dds_header.image_count == 1 else _calculate_cube_faces_data(tex)
        tex.mipmap_offsets = dds_header.calculate_mimpap_offsets(tex.size_before_data_)
        tex.dds_data = dds_header.data
        dds_data_len = len(tex.dds_data)
    tex.padding = 0
    custom_properties.set_to_dest(tex)

    tex._check()

    final_size = tex.size_before_data_ + dds_data_len
    stream = KaitaiStream(io.BytesIO(bytearray(final_size)))
    tex._write(stream)
    relative_path = _handle_relative_path(bl_im, custom_properties.render_target)
    vf = VirtualFileData(app_id, relative_path, data_bytes=stream.to_byte_array())
    return vf


def _serialize_texture_21(app_id, dict_tex):
    bl_im = dict_tex["image"]
    custom_properties = bl_im.albam_custom_properties.get_custom_properties_for_appid(app_id)
    is_rtex = custom_properties.render_target
    # compression_format = custom_properties.compression_format or _infer_compression_format(dict_tex)

    if is_rtex:
        tex = Rtex157()
        tex.id_magic = b"RTX\x00"
        # tex.num_mipmaps_per_image = int(math.log(max(bl_im.size[0], bl_im.size[1]), 2)) + 1
        tex.num_mipmaps_per_image = 1
        dds_data_size = 0
    else:
        dds_header = DDSHeader.from_bl_image(bl_im)
        tex = Tex157()
        tex.id_magic = b"TEX\x00"

    tex.width = bl_im.size[0]
    if is_rtex:
        if custom_properties.type == "0x6":
            tex.num_images = 6
        else:
            tex.num_images = 1  # curently hardcoded
        tex.height = bl_im.size[1]
    else:
        tex.num_images = dds_header.image_count
        tex.height = bl_im.size[1] // dds_header.image_count  # cubemaps are a vertical strip in Blender
        tex.num_mipmaps_per_image = dds_header.dwMipMapCount

    if not is_rtex:
        tex.cube_faces = [] if dds_header.image_count == 1 else _calculate_cube_faces_data(tex)
        tex.mipmap_offsets = dds_header.calculate_mimpap_offsets(tex.size_before_data_)
        tex.dds_data = dds_header.data
        dds_data_size = len(tex.dds_data)

    custom_properties.set_to_dest(tex)
    tex._check()

    final_size = tex.size_before_data_ + dds_data_size
    stream = KaitaiStream(io.BytesIO(bytearray(final_size)))
    tex._write(stream)
    relative_path = _handle_relative_path(bl_im)
    vf = VirtualFileData(app_id, relative_path, data_bytes=stream.to_byte_array())
    return vf


def _infer_compression_format(dict_tex):
    """
    Infer the type of texture based on its usage in materials.
    E.g. if the bl_image is linked to a "BM" socket, it's diffuse.
    """
    # NOTE: this logic is duplicated in `_gather_tex_types`

    DEFAULT_COMPRESSION_FORMAT = TextureType2.DIFFUSE
    bl_im = dict_tex["image"]
    materials_dict = dict_tex["materials"]
    materials = [m[0] for m in materials_dict.values()]

    if not materials:
        # means texture is disconnected, could still happend
        # TODO: update then blender.lib function is updated
        return DEFAULT_COMPRESSION_FORMAT.value

    # Arbitrarily using the first material where the image is used to infer its type.
    # TODO: report discrepancies in texture usage (e.g. texture used both as Diffuse and Lightmap)
    bl_mat = materials[0]
    image_nodes = [node for node in bl_mat.node_tree.nodes if node.type == "TEX_IMAGE"]
    im_nodes = [node for node in image_nodes if node.image.name == bl_im.name]
    im_node = im_nodes[0] if im_nodes else None
    if not im_node:
        return DEFAULT_COMPRESSION_FORMAT.value
    links = im_node.outputs["Color"].links
    if not links:
        return DEFAULT_COMPRESSION_FORMAT.value
    mtfw_shader_link_name = links[0].to_socket.name
    try:
        tex_type = NODE_NAMES_TO_TYPES_2[mtfw_shader_link_name]
    except KeyError:
        print(f"Can\'t get correct compression_format for image '{bl_im.name}'."
              "Node '{mtfw_shader_link_name}' not supported yet. "
              "Using default {DEFAULT_COMPRESSION_FORMAT}. "
              "Set compression_format manually for now."
              )
        tex_type = DEFAULT_COMPRESSION_FORMAT

    return tex_type.value


def _handle_relative_path(bl_im, render_target=False):
    path = bl_im.albam_asset.relative_path or bl_im.name
    before, _, after = path.rpartition(".")
    if render_target:
        ext = "rtex"
    else:
        ext = "tex"
    if not before:
        path = f"{path}.{ext}"
    else:
        path = f"{before}.{ext}"
    return path


def _calculate_cube_faces_data(tex):
    # TODO: get real data
    # It seems having null data doesn't
    # affect the game much
    cube_faces = []
    for _ in range(3):
        cb = tex.CubeFace(_parent=tex, _root=tex._root)
        cb.field_00 = 0
        cb.negative_co = [0, 0, 0]
        cb.positive_co = [0, 0, 0]
        cb.uv = [0, 0]
        cube_faces.append(cb)
    return cube_faces


@blender_registry.register_custom_properties_image("tex_112", ("re5", ))
@blender_registry.register_blender_prop
class Tex112CustomProperties(bpy.types.PropertyGroup):
    texture_type: bpy.props.EnumProperty(  # noqa: F821
        name="Texture Type",
        items=[
            ("0x0", "Undefined", "", 1),  # noqa: F821
            ("0x1", "1D", "", 2),
            ("0x2", "2D", "", 3),
            ("0x3", "2D Cube", "", 4),
            ("0x4", "3D", "", 5),
        ],
        options=set()
    )
    encoded_type: bpy.props.EnumProperty(  # noqa: F821
        name="Encode Type",
        items=[
            ("0x0", "None", "", 1),
            ("0x1", "RGBI", "", 2),  # noqa: F821
            ("0x2", "RGBY", "", 3),  # noqa: F821
            ("0x3", "RGBN", "", 4),  # noqa: F821
            ("0x4", "Pal8", "", 5),  # noqa: F821
        ],
        options=set()
    )
    attr: bpy.props.EnumProperty(
        name="Attribute",   # noqa: F821
        items=[
            ("0x0", "FillMargin", "", 1),  # noqa: F821
            ("0x1", "Grayscale", "", 2),  # noqa: F821
            ("0x2", "Nuki", "", 3),  # noqa: F821
            ("0x3", "Dither", "", 4),  # noqa: F821
            ("0x4", "RGBI Encoded", "", 5),
        ],
        options=set()
    )
    depth: bpy.props.IntProperty(
        name="Depth",  # noqa: F821
        default=0,
    )
    depend_screen: bpy.props.BoolProperty(  # noqa: F821
        name="Depend on Screen",
        description="Does this texture depend on screen resolution?",
        default=False,
    )
    render_target: bpy.props.BoolProperty(  # noqa: F821
        name="Render Target",
        description="Is this texture a render target?",
        default=False,
    )
    red: bpy.props.FloatProperty(default=0.7)
    green: bpy.props.FloatProperty(default=0.7)
    blue: bpy.props.FloatProperty(default=0.7)
    alpha: bpy.props.FloatProperty(default=0.7)

    # XXX copy paste in mesh, material
    def set_from_source(self, mesh):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            self.copy_attr(mesh, self, attr_name)

    def set_to_dest(self, mesh):
        for attr_name in self.__annotations__:
            self.copy_attr(self, mesh, attr_name)

    @staticmethod
    def copy_attr(src, dst, name):
        # will raise, making sure there's consistency
        src_value = getattr(src, name)
        try:
            if isinstance(src_value, str):
                src_value = int(src_value, 16)
            setattr(dst, name, src_value)
        except TypeError:
            setattr(dst, name, hex(src_value))


@blender_registry.register_custom_properties_image("tex_157", ("re0", "re1", "re6", "rev1", "rev2", "dd",))
@blender_registry.register_blender_prop
class Tex157CustomProperties(bpy.types.PropertyGroup):  # noqa: F821
    unk: bpy.props.IntProperty(  # noqa: F821
        name="Unknown",  # noqa: F821
        default=0,
        description="Unknown property, usually 0"
    )
    version: bpy.props.EnumProperty(  # noqa: F821
        name="Tex format version",
        items=[
            ("0x99", "153", "", 1),
            ("0x9a", "154", "", 2),
            ("0x9d", "157", "", 3),
            ("0x9e", "158", "", 4),
        ],
        default="0x9d",
        options=set()
    )
    attr: bpy.props.EnumProperty(  # noqa: F821
        name="Attribute",   # noqa: F821
        items=[
            ("0x0", "FillMargin", "", 1),  # noqa: F821
            ("0x2", "Grayscale", "", 2),  # noqa: F821
            ("0x4", "Nuki", "", 3),  # noqa: F821
            ("0x8", "Dither", "", 4),  # noqa: F821
            ("0x10", "Linear", "", 5),  # noqa: F821
            ("0x20", "Special", "", 5),  # noqa: F821
        ],
        options=set()
    )
    prebias: bpy.props.IntProperty(name="Prebias", default=0)  # noqa: F821
    type: bpy.props.EnumProperty(
        name="Texture Type",
        items=[
            ("0x0", "Undefined", "", 1),  # noqa: F821
            ("0x1", "1D", "", 2),
            ("0x2", "2D", "", 3),
            ("0x3", "3D", "", 4),
            ("0x4", "1D Array", "", 5),
            ("0x5", "2D Array", "", 6),
            ("0x6", "Cube", "", 7),  # noqa: F821
            ("0x7", "Cube Array", "", 8),
            ("0x8", "2D Multisample", "", 9),
            ("0x9", "2D Multisample Array", "", 10),
        ],
        default="0x2",
        options=set()
    )
    compression_format: bpy.props.IntProperty(name="Compression Format", default=0, min=0, max=43)
    depth: bpy.props.IntProperty(
        name="Depth",  # noqa: F821
        default=1,
    )
    auto_resize: bpy.props.BoolProperty(  # noqa: F821
        name="Auto Resize",
        default=False,
    )
    render_target: bpy.props.BoolProperty(  # noqa: F821
        name="Render Target",
        description="Is this texture a render target?",
        default=False,
    )
    use_vtf: bpy.props.BoolProperty(  # noqa: F821
        name="Use VTF",
        default=False,
    )

    # XXX copy paste in mesh, material
    def set_from_source(self, mesh):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            self.copy_attr(mesh, self, attr_name)

    def set_to_dest(self, mesh):
        for attr_name in self.__annotations__:
            self.copy_attr(self, mesh, attr_name)

    @staticmethod
    def copy_attr(src, dst, name):
        # will raise, making sure there's consistency
        src_value = getattr(src, name)
        try:
            if isinstance(src_value, str):
                src_value = int(src_value, 16)
            setattr(dst, name, src_value)
        except TypeError:
            setattr(dst, name, hex(src_value))


def check_dds_textures(func):
    """
    Function decorator that checks if all the meshes of a bl_object
    have materials that use dds textures only
    Raises AlbamCheckFailure with the list of
    non-dds textures and materials where they are used
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bl_objects = [a for a in args if isinstance(a, bpy.types.Object)]
        if not bl_objects:
            result = func(*args, **kwargs)
        # No more than one root object in export functions
        meshes = [c for c in bl_objects[0].children_recursive if c.type == "MESH"]
        materials = get_bl_materials(meshes)
        images = get_bl_teximage_nodes(materials)
        non_dds = []
        for bl_im_name, bl_im_dict in images.items():
            app_id = bl_im_dict["image"].albam_asset.app_id
            image = bl_im_dict["image"]
            custom_propertins = image.albam_custom_properties.get_custom_properties_for_appid(app_id)
            if custom_propertins.render_target is True:
                continue
            if not is_blimage_dds(bl_im_dict["image"]):
                non_dds.append((bl_im_name, bl_im_dict))
        if any(non_dds):
            data = [
                f"Texture: {bl_im_name} -> materials: {list(bl_im_dict['materials'].keys())}"
                for bl_im_name, bl_im_dict in non_dds
            ]
            raise AlbamCheckFailure(
                "The materials to export contain some images that are not DDS",
                details=" ".join(data),
                solution="Edit the images externally (e.g. in GIMP) and reassign in the materials listed")
        result = func(*args, **kwargs)

        return result
    return wrapper
