import io
import struct

import bpy
from kaitaistruct import KaitaiStream
from pybc7 import unpack_dds

from ...registry import blender_registry
from .apps import APPS_TODO
from .structs.reengine_tex import ReengineTex


KNOWN_TEXTURE_TYPES = {
    "AlphaTranslucentOcclusionSSSMap",
    "BaseMap",
    "BaseAlphaMap",
    "BaseShiftMap",
    "BaseDielectricMap",
    "BaseMetalMap",
    "NormalRoughnessMap",
}


@blender_registry.register_import_function("re2_non_rt", extension="tex.10", albam_asset_type="TEXTURE")
@blender_registry.register_import_function("re2", extension="tex.34")
@blender_registry.register_import_function("re3_non_rt", extension="tex.190820018",
                                           albam_asset_type="TEXTURE")
@blender_registry.register_import_function("re3", extension="tex.34", albam_asset_type="TEXTURE")
@blender_registry.register_import_function("re8", extension="tex.30", albam_asset_type="TEXTURE")
def import_texture(file_list_item, context):

    tex_bytes = file_list_item.get_bytes()
    tex = ReengineTex(KaitaiStream(io.BytesIO(tex_bytes)))

    dds_data = tex.mipmaps[0].dds_data
    pixel_bytes = unpack_dds(io.BytesIO(dds_data), tex.width, tex.height, 'BC7', 0)

    num_pixels = len(pixel_bytes)
    pixels = [p / 255 for p in struct.unpack(f'{num_pixels}B', pixel_bytes)]

    image = bpy.data.images.new(file_list_item.display_name, tex.width, tex.height)
    image.alpha_mode = "CHANNEL_PACKED"
    image.pixels = pixels
    image.pack()


def build_blender_images(app_id, texture_headers, context):
    blender_images = {}
    done = set()

    app_data = APPS_TODO[app_id]
    prefix = app_data[0]  # TODO: configure to use higher quality textures (prefix += streaming/)
    tex_version = app_data[3]
    skipped_types = set()

    for tex_header in texture_headers:
        if tex_header.texture_type not in KNOWN_TEXTURE_TYPES:
            skipped_types.add(tex_header.texture_type)
            continue
        if tex_header.texture_path in done:
            continue
        tex_path = f"{prefix}/{tex_header.texture_path.lower()}.{tex_version}"
        try:
            tex_virtual_file = context.scene.albam.vfs.get_vfile(app_id, tex_path)
        except KeyError:
            print("Texture not found in virtual file system, ignoring", tex_path)
            continue

        try:
            tex_bytes = tex_virtual_file.get_bytes()
            tex = ReengineTex(KaitaiStream(io.BytesIO(tex_bytes)))

            if tex.format == 98 or tex.format == 99:
                tex_format = "BC7"
            elif tex.format == 71 or tex.format == 72:
                tex_format = "DXT1"
            else:
                print(f"WARNING: unrecognized format: {tex.format}. Attempting with BC7")
                tex_format = "BC7"

            dds_data = tex.mipmaps[0].dds_data
            pixel_bytes = unpack_dds(io.BytesIO(dds_data), tex.width, tex.height, tex_format, 0)

            num_pixels = len(pixel_bytes)
            pixels = [p / 255 for p in struct.unpack(f'{num_pixels}B', pixel_bytes)]

            # TODO: check cases for DXT1 with no alpha
            image = bpy.data.images.new(tex_virtual_file.display_name, tex.width, tex.height, alpha=True)
            image.alpha_mode = "CHANNEL_PACKED"
            image.pixels = pixels
            image.pack()
            blender_images[tex_header.texture_path] = image
            done.add(tex_header.texture_path)
        except Exception as err:
            print(f"Failed to build texture {tex_path} with error: {err}")

    print(f"Skipped {len(skipped_types)} textures from MDF: {sorted(skipped_types)}")
    return blender_images


def assign_textures(bl_material, mdf_mat, blender_images):

    for tex_header in mdf_mat.textures:
        if tex_header.texture_type not in KNOWN_TEXTURE_TYPES:
            continue
        bl_image = blender_images.get(tex_header.texture_path)
        if not bl_image:
            print(f"WARNING: {tex_header.texture_path} not found")
            continue
        texture_node = bl_material.node_tree.nodes.new("ShaderNodeTexImage")
        texture_node.image = bl_image
        bsdf_node = bl_material.node_tree.nodes.get("Principled BSDF")
        if tex_header.texture_type == "BaseMap" or tex_header.texture_type == "BaseShiftMap":
            bl_material.node_tree.links.new(texture_node.outputs["Color"], bsdf_node.inputs["Base Color"])
        elif tex_header.texture_type == "BaseAlphaMap":
            bl_material.node_tree.links.new(texture_node.outputs["Color"], bsdf_node.inputs["Base Color"])
            bl_material.node_tree.links.new(texture_node.outputs["Alpha"], bsdf_node.inputs["Alpha"])
        elif tex_header.texture_type == "BaseDielectricMap":
            bl_material.node_tree.links.new(texture_node.outputs["Color"], bsdf_node.inputs["Base Color"])
            # TODO
            # bl_material.node_tree.links.new(texture_node.outputs["Alpha"], bsdf_node.inputs["Alpha"])
        elif tex_header.texture_type == "BaseMetalMap":
            bl_material.node_tree.links.new(texture_node.outputs["Color"], bsdf_node.inputs["Base Color"])
            bl_material.node_tree.links.new(texture_node.outputs["Alpha"], bsdf_node.inputs["Metallic"])
        elif tex_header.texture_type == "NormalRoughnessMap":
            texture_node.image.colorspace_settings.name = 'Non-Color'
            normal_map_node = bl_material.node_tree.nodes.new("ShaderNodeNormalMap")
            bl_material.node_tree.links.new(texture_node.outputs["Color"], normal_map_node.inputs["Color"])
            bl_material.node_tree.links.new(normal_map_node.outputs["Normal"], bsdf_node.inputs["Normal"])
            bl_material.node_tree.links.new(texture_node.outputs["Alpha"], bsdf_node.inputs["Roughness"])
        elif tex_header.texture_type == "AlphaTranslucentOcclusionSSSMap":
            separate_color_node = bl_material.node_tree.nodes.new("ShaderNodeSeparateColor")
            bl_material.node_tree.links.new(
                texture_node.outputs["Color"], separate_color_node.inputs["Color"]
            )
            if mdf_mat.alpha_flags.alpha_mask_used:
                bl_material.node_tree.links.new(separate_color_node.outputs["Red"], bsdf_node.inputs["Alpha"])
