"""Build CCL-style child mesh previews for CHN joints stored on pose bones."""

import bpy

from .bone import get_anim_retarget
from .chain_preview import _append_capsule, _append_sphere
from .chain_props import (
    get_ccl_bone_properties,
    get_chn_file_properties,
    get_chn_joint_preview_properties,
)


_CHN_MATERIAL_NAME = "Albam CHN Collision"
_CHN_COLOR = (1.0, 0.32, 0.06, 0.42)


def _joint_preview_name(record, anim_id):
    return f"CHN_{anim_id:03d}_C{record.chain_index:03d}_J{record.joint_index:03d}"


def _bone_world_matrix(armature, pose_bone):
    rest_bone = armature.data.bones.get(pose_bone.name)
    if rest_bone is None:
        return None
    return armature.matrix_world @ rest_bone.matrix_local


def _collision_material():
    material = bpy.data.materials.get(_CHN_MATERIAL_NAME)
    if material is None:
        material = bpy.data.materials.new(_CHN_MATERIAL_NAME)
    material.diffuse_color = _CHN_COLOR
    return material


def _remove_previews(root_object, file_props):
    pose_bones = file_props.armature.pose.bones if file_props.armature else ()
    for pose_bone in pose_bones:
        for record in get_ccl_bone_properties(pose_bone).chn_joints:
            record.preview_object = None
    for record in file_props.orphans:
        record.preview_object = None
    for child in tuple(root_object.children):
        if not child.get("_albam_chn_joint_preview", False):
            continue
        old_mesh = child.data if child.type == "MESH" else None
        bpy.data.objects.remove(child, do_unlink=True)
        if old_mesh and old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)


def _new_preview(root_object, armature, record, pose_bone, anim_id,
                 vertices, faces, material):
    name = _joint_preview_name(record, anim_id)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()

    preview = bpy.data.objects.new(name, mesh)
    preview.parent = root_object
    preview.display_type = "WIRE"
    preview.color = _CHN_COLOR
    preview.hide_select = True
    preview.hide_render = True
    preview["_albam_chn_joint_preview"] = True
    for collection in root_object.users_collection:
        collection.objects.link(preview)

    preview_props = get_chn_joint_preview_properties(preview)
    preview_props.armature = armature
    preview_props.reference_bone_name = pose_bone.name
    preview_props.anim_id = anim_id
    preview_props.chain_index = record.chain_index
    preview_props.joint_index = record.joint_index
    preview_props.shape = {1: "SPHERE", 2: "CAPSULE"}.get(record.col_shape, "UNKNOWN")
    record.preview_object = preview


def rebuild_chn_previews(root_object):
    if root_object is None or root_object.type != "EMPTY":
        return
    file_props = get_chn_file_properties(root_object)
    armature = file_props.armature
    _remove_previews(root_object, file_props)
    if armature is None or armature.type != "ARMATURE":
        return

    record_map = {}
    mapped_records = []
    for pose_bone in armature.pose.bones:
        for record in get_ccl_bone_properties(pose_bone).chn_joints:
            key = (record.chain_index, record.joint_index)
            record_map.setdefault(key, (record, pose_bone))
            mapped_records.append((record, pose_bone))
    for record in file_props.orphans:
        record_map.setdefault((record.chain_index, record.joint_index), (record, None))

    material = _collision_material()
    for record, reference_bone in mapped_records:
        matrix = _bone_world_matrix(armature, reference_bone)
        if matrix is None:
            continue
        raw_anim_id = get_anim_retarget(reference_bone, "re5")
        try:
            anim_id = int(raw_anim_id.split("_", 1)[0]) if raw_anim_id else record.ref_joint_no
        except ValueError:
            anim_id = record.ref_joint_no
        center = matrix.translation.copy()
        world_scale = max(abs(value) for value in matrix.to_scale())
        radius = max(0.0, record.col_radius) * 0.01 * world_scale
        vertices = []
        faces = []
        face_materials = []
        if record.col_shape == 1:
            _append_sphere(vertices, faces, face_materials, center, radius, 0)
        elif record.col_shape == 2:
            next_joint = record_map.get((record.chain_index, record.joint_index + 1))
            next_bone = next_joint[1] if next_joint else None
            next_matrix = _bone_world_matrix(armature, next_bone) if next_bone else None
            if next_matrix is None:
                _append_sphere(vertices, faces, face_materials, center, radius, 0)
            else:
                _append_capsule(
                    vertices, faces, face_materials,
                    center, next_matrix.translation.copy(), radius, 0)
        _new_preview(root_object, armature, record, reference_bone, anim_id,
                     vertices, faces, material)
