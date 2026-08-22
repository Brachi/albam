import io
import os

import bpy
from kaitaistruct import KaitaiStream

from .texture import build_blender_textures
from .structs.hexane_matb import HexaneMatb

# A .matb's texture paths end in a two-character suffix identifying their
# role (e.g. "..._skel_d.dds", "..._skel_n.dds") - confirmed against a
# full-game sweep, see matb.ksy/tests/hexn/test_matb_parsing.py. Maps each
# suffix to the Principled BSDF input it feeds and the color space its DDS
# should be read as (data maps like normal/specular aren't color, so must
# be Non-Color or Blender's color management will darken them). Only these
# four are wired up here; other suffixes seen in the wild (roughness/mask/
# env-map-like ones) aren't handled yet.
TEXTURE_SLOTS = {
    "_d": ("Base Color", "sRGB"),
    "_n": ("Normal", "Non-Color"),
    "_s": ("Specular IOR Level", "Non-Color"),
    "_g": ("Emission Color", "sRGB"),
}


def _texture_suffix(texture_path):
    stem = os.path.basename(texture_path).rsplit(".", 1)[0]
    return stem[-2:].lower()


def build_blender_materials(edgemodel, context):

    material_paths = set()
    matbs = []
    bl_materials = {}
    texture_paths = set()

    for mesh_header in edgemodel.meshes_header:
        path = mesh_header.materials.first_material
        material_paths.add(path)

    vfs = context.scene.albam.vfs

    for material_path in material_paths:
        matb_vfile = vfs.get_vfile("reorc", material_path)
        matb_bytes = matb_vfile.get_bytes()
        matb = HexaneMatb(KaitaiStream(io.BytesIO(matb_bytes)))
        matb._read()
        matbs.append((matb, material_path))
        for texture_path in matb.shader.textures:
            if _texture_suffix(texture_path) in TEXTURE_SLOTS:
                texture_paths.add(texture_path)

    tex_mapping = build_blender_textures(texture_paths, context)

    for matb, material_path in matbs:
        if not matb.shader.textures:
            continue

        bl_material = bpy.data.materials.new(os.path.basename(material_path))
        bl_material.use_nodes = True
        node_tree = bl_material.node_tree
        bsdf = next(node for node in node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        link = node_tree.links.new

        for texture_path in matb.shader.textures:
            slot = TEXTURE_SLOTS.get(_texture_suffix(texture_path))
            if slot is None:
                continue
            socket_name, color_space = slot
            bl_image = tex_mapping[texture_path]
            bl_image.colorspace_settings.name = color_space

            texture_node = node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.image = bl_image
            texture_node.label = os.path.basename(texture_path)

            if socket_name == "Normal":
                normal_map_node = node_tree.nodes.new("ShaderNodeNormalMap")
                link(texture_node.outputs["Color"], normal_map_node.inputs["Color"])
                link(normal_map_node.outputs["Normal"], bsdf.inputs["Normal"])
            else:
                link(texture_node.outputs["Color"], bsdf.inputs[socket_name])
                if socket_name == "Emission Color":
                    bsdf.inputs["Emission Strength"].default_value = 1.0

        bl_materials[material_path] = bl_material

    return bl_materials
