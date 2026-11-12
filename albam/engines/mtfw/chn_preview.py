"""Build CCL-style child mesh previews for CHN joints stored on pose bones."""

import bpy
from mathutils import Vector

from .bone import get_anim_retarget
from .chain_preview import _append_capsule, _append_sphere
from .chn_graph import ordered_links_from_strands
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


def _record_anim_id(record, pose_bone):
    raw_id = get_anim_retarget(pose_bone, "re5") if pose_bone is not None else None
    try:
        return int(raw_id.split("_", 1)[0]) if raw_id else record.ref_joint_no
    except ValueError:
        return record.ref_joint_no


def _links_for_chain(chain_props, records):
    id_remap = {
        (record.source_ref_joint_no
         if record.source_ref_joint_no >= 0 else record.ref_joint_no):
        _record_anim_id(record, pose_bone)
        for record, pose_bone in records
    }
    if chain_props.topology_dirty:
        strands = [
            {"joints": [id_remap.get(joint.anim_id, joint.anim_id)
                        for joint in strand.joints],
             "closed": strand.closed}
            for strand in chain_props.strands
        ]
        raw_links = {}
        for record, pose_bone in records:
            try:
                slots = bytes.fromhex(record.raw_node_slots)
            except ValueError:
                slots = b""
            if len(slots) == 8 and 0 <= record.raw_node_num <= 8:
                raw_links[_record_anim_id(record, pose_bone)] = {
                    id_remap.get(target, target)
                    for target in slots[:record.raw_node_num]
                }
        return ordered_links_from_strands(strands, raw_links)

    links = {}
    has_raw = bool(records) and all(record.raw_node_num >= 0 for record, _bone in records)
    if has_raw:
        for record, pose_bone in records:
            anim_id = _record_anim_id(record, pose_bone)
            try:
                slots = bytes.fromhex(record.raw_node_slots)
            except ValueError:
                slots = b""
            if len(slots) == 8 and 0 <= record.raw_node_num <= 8:
                links[anim_id] = {
                    id_remap.get(target, target)
                    for target in slots[:record.raw_node_num]
                }
            else:
                links[anim_id] = set()
        return links

    # Backward compatibility for scenes saved before raw node slots existed.
    ordered = sorted(records, key=lambda pair: pair[0].joint_index)
    for index, (record, pose_bone) in enumerate(ordered):
        neighbors = set()
        if index:
            neighbors.add(_record_anim_id(*ordered[index - 1]))
        if index + 1 < len(ordered):
            neighbors.add(_record_anim_id(*ordered[index + 1]))
        links[_record_anim_id(record, pose_bone)] = neighbors
    return links


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
                 vertices, faces, material, origin):
    name = _joint_preview_name(record, anim_id)
    mesh = bpy.data.meshes.new(name)
    local_vertices = [tuple(Vector(vertex) - origin) for vertex in vertices]
    mesh.from_pydata(local_vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()

    preview = bpy.data.objects.new(name, mesh)
    preview.parent = root_object
    preview.matrix_parent_inverse = root_object.matrix_world.inverted_safe()
    preview.show_in_front = True
    preview.display_type = "WIRE"
    preview.color = _CHN_COLOR
    preview.hide_select = True
    preview.hide_render = True
    preview["_albam_chn_joint_preview"] = True
    for collection in root_object.users_collection:
        collection.objects.link(preview)

    copy_location = preview.constraints.new(type="COPY_LOCATION")
    copy_location.target = armature
    copy_location.subtarget = pose_bone.name
    copy_location.target_space = "WORLD"
    copy_location.owner_space = "WORLD"

    preview_props = get_chn_joint_preview_properties(preview)
    preview_props.armature = armature
    preview_props.reference_bone_name = pose_bone.name
    preview_props.anim_id = anim_id
    preview_props.chain_index = record.chain_index
    preview_props.joint_index = record.joint_index
    preview_props.shape = record.col_shape
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
    records_by_chain = {}
    for pose_bone in armature.pose.bones:
        for record in get_ccl_bone_properties(pose_bone).chn_joints:
            anim_id = _record_anim_id(record, pose_bone)
            record_map.setdefault((record.chain_index, anim_id), (record, pose_bone))
            records_by_chain.setdefault(record.chain_index, []).append((record, pose_bone))
            mapped_records.append((record, pose_bone))
    for record in file_props.orphans:
        record_map.setdefault((record.chain_index, record.ref_joint_no), (record, None))
        records_by_chain.setdefault(record.chain_index, []).append((record, None))

    chain_props_by_index = {chain.chain_index: chain for chain in file_props.chains}
    links_by_chain = {
        chain_index: _links_for_chain(chain_props_by_index[chain_index], records)
        for chain_index, records in records_by_chain.items()
        if chain_index in chain_props_by_index
    }

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
        if record.col_shape == "SPHERE":
            _append_sphere(vertices, faces, face_materials, center, radius, 0)
        elif record.col_shape == "CAPSULE":
            links = links_by_chain.get(record.chain_index, {})
            neighbor_ids = links.get(anim_id, set())
            endpoints = []
            for neighbor_id in sorted(neighbor_ids):
                neighbor = record_map.get((record.chain_index, neighbor_id))
                next_bone = neighbor[1] if neighbor else None
                next_matrix = _bone_world_matrix(armature, next_bone) if next_bone else None
                if next_matrix is not None:
                    endpoints.append(next_matrix.translation.copy())
            if not endpoints:
                _append_sphere(vertices, faces, face_materials, center, radius, 0)
            else:
                for endpoint in endpoints:
                    _append_capsule(vertices, faces, face_materials,
                                    center, endpoint, radius, 0)
        _new_preview(root_object, armature, record, reference_bone, anim_id,
                     vertices, faces, material, center)
