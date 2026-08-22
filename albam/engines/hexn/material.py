import io
import os

import bpy
from kaitaistruct import KaitaiStream

from .texture import build_blender_textures
from .structs.hexane_matb import HexaneMatb


def build_blender_materials(edgemodel, context):

    material_paths = set()
    matbs = []
    bl_materials = {}
    texture_paths = set()
    TEX_SLOT_DIFFUSE = 0

    for mesh_header in edgemodel.meshes_header:
        path = mesh_header.materials.first_material
        material_paths.add(path)

    vfs = context.scene.albam.vfs

    for material_path in material_paths:
        matb_vfile = vfs.get_vfile("reorc", material_path)
        matb_bytes = matb_vfile.get_bytes()
        matb = HexaneMatb(KaitaiStream(io.BytesIO(matb_bytes)))
        matbs.append((matb , material_path))
        if matb.shader.textures:
            tex_diffuse_path = matb.shader.textures[TEX_SLOT_DIFFUSE]
            texture_paths.add(tex_diffuse_path)

    tex_mapping = build_blender_textures(texture_paths, context)

    for matb, material_path in matbs:
        if matb.shader.textures:
            tex_diffuse_path = matb.shader.textures[TEX_SLOT_DIFFUSE]
            bl_image = tex_mapping[tex_diffuse_path]
            bl_material = bpy.data.materials.new(os.path.basename(material_path))
            bl_material.use_nodes = True
            texture_node = bl_material.node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.image = bl_image
            material_output = [node for node in bl_material.node_tree.nodes
                               if node.type == "OUTPUT_MATERIAL"][0]
            link = bl_material.node_tree.links.new
            link(texture_node.outputs[0], material_output.inputs[0])
            bl_materials[material_path] = bl_material
        else:
            continue

    return bl_materials
