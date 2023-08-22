import io

import bpy
from kaitaistruct import KaitaiStream

from .structs.reengine_mdf import ReengineMdf
from .texture import build_blender_images, assign_textures
from .apps import APPS_TODO


def build_blender_materials(mesh_vfile, context):
    blender_materials = {}
    app_id = mesh_vfile.app_id

    possible_mdf_virtual_paths = _get_heuristic_mdf_names(app_id, mesh_vfile.name)
    mdf_found = False
    for mdf_virtual_path in possible_mdf_virtual_paths:
        try:
            mdf_virtual_file = context.scene.albam.file_explorer.file_list[mdf_virtual_path]
            mdf_found = True
            break
        except KeyError:
            pass
    if not mdf_found:
        print(f"MDF file not found. Attempted: {possible_mdf_virtual_paths}")
        return blender_materials

    mdf_bytes = mdf_virtual_file.get_bytes()
    mdf_version = int(mdf_virtual_path.rpartition(".")[2])

    mdf = ReengineMdf(mdf_version, KaitaiStream(io.BytesIO(mdf_bytes)))
    images_to_build = {texture_header for mat in mdf.materials for texture_header in mat.textures}
    blender_images = build_blender_images(app_id, images_to_build, context)

    for mdf_material in mdf.materials:
        blender_material = bpy.data.materials.new(mdf_material.name)
        blender_material.use_nodes = True
        blender_material.blend_method = "HASHED" if mdf_material.alpha_flags.alpha_mask_used else "OPAQUE"
        assign_textures(blender_material, mdf_material, blender_images)
        blender_materials[mdf_material.name] = blender_material

    return blender_materials


def _get_heuristic_mdf_names(app_id, mesh_name):
    mesh_extension = f"mesh.{APPS_TODO[app_id][1]}"
    mdf_extension = f"mdf2.{APPS_TODO[app_id][2]}"

    a = mesh_name.replace(mesh_extension, mdf_extension)
    b = mesh_name.replace(f".{mesh_extension}", f"_mat.{mdf_extension}")
    return [a, b]
