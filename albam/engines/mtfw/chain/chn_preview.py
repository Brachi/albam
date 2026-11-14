"""Build CCL-style child mesh previews for CHN joints stored on pose bones."""

import bpy
from math import cos, pi, sin
from mathutils import Vector

from ..bone import get_anim_retarget
from .ccl_preview import _append_capsule, _append_sphere
from .graph import ordered_links_from_strands
from .properties import (
    get_ccl_bone_properties,
    get_chn_file_properties,
    get_chn_joint_preview_properties,
)


CHN_MATERIAL_NAME = "Albam CHN Collision"
CHN_COLOR = (0.0, 0.49, 0.55, 1.0)
CHN_ANGLE_COLORS = (
    (0.95, 0.12, 0.10, 1.0),  # X
    (0.14, 0.82, 0.20, 1.0),  # Y
    (0.12, 0.35, 1.0, 1.0),  # Z
)
CHN_ANGLE_AXES = ("X", "Y", "Z")


def _joint_preview_name(record, anim_id):
    return f"CHN_{anim_id:03d}_C{record.chain_index:03d}_J{record.joint_index:03d}"


def _angle_preview_name(record, anim_id, axis):
    return f"{_joint_preview_name(record, anim_id)}_ANGLE_{axis}"


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
    material = bpy.data.materials.get(CHN_MATERIAL_NAME)
    if material is None:
        material = bpy.data.materials.new(CHN_MATERIAL_NAME)
    material.diffuse_color = CHN_COLOR
    return material


def _angle_material(axis_index):
    name = f"Albam CHN Angle {CHN_ANGLE_AXES[axis_index]}"
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
    material.diffuse_color = CHN_ANGLE_COLORS[axis_index]
    return material


def _remove_previews(root_object, file_props):
    pose_bones = file_props.armature.pose.bones if file_props.armature else ()
    for pose_bone in pose_bones:
        for record in get_ccl_bone_properties(pose_bone).chn_joints:
            record.preview_object = None
    for record in file_props.orphans:
        record.preview_object = None
    for child in tuple(root_object.children):
        if not (child.get("_albam_chn_joint_preview", False) or
                child.get("_albam_chn_angle_preview", False)):
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
    preview.color = CHN_COLOR
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


def _new_angle_preview(root_object, armature, record, pose_bone, anim_id,
                       axis_index, vertices, edges, origin):
    axis = CHN_ANGLE_AXES[axis_index]
    name = _angle_preview_name(record, anim_id, axis)
    mesh = bpy.data.meshes.new(name)
    local_vertices = [tuple(Vector(vertex) - origin) for vertex in vertices]
    mesh.from_pydata(local_vertices, edges, [])
    mesh.materials.append(_angle_material(axis_index))
    mesh.update()

    preview = bpy.data.objects.new(name, mesh)
    preview.parent = root_object
    preview.matrix_parent_inverse = root_object.matrix_world.inverted_safe()
    preview.show_in_front = True
    preview.display_type = "WIRE"
    preview.color = CHN_ANGLE_COLORS[axis_index]
    preview.hide_select = True
    preview.hide_render = True
    preview["_albam_chn_angle_preview"] = True
    for collection in root_object.users_collection:
        collection.objects.link(preview)

    copy_location = preview.constraints.new(type="COPY_LOCATION")
    copy_location.target = armature
    copy_location.subtarget = pose_bone.name
    copy_location.target_space = "WORLD"
    copy_location.owner_space = "WORLD"


def _angle_arc_geometry(matrix, origin, axis_index, minimum, maximum, radius):
    """Build a colored line arc in the reference bone's local axis plane."""
    local_axes = (
        Vector((1.0, 0.0, 0.0)),
        Vector((0.0, 1.0, 0.0)),
        Vector((0.0, 0.0, 1.0)),
    )
    basis = matrix.to_3x3()
    axis = (basis @ local_axes[axis_index]).normalized()
    first = basis @ local_axes[(axis_index + 1) % 3]
    first = (first - axis * first.dot(axis)).normalized()
    second = axis.cross(first).normalized()

    sweep = maximum - minimum
    segments = max(1, min(128, int(abs(sweep) / (pi / 24.0)) + 1))
    vertices = []
    edges = []

    def point(angle, point_radius=radius):
        return origin + point_radius * (first * cos(angle) + second * sin(angle))

    for index in range(segments + 1):
        angle = minimum + sweep * index / segments
        vertices.append(point(angle))
        if index:
            edges.append((index - 1, index))

    # Endpoint ticks also make a zero-width range visible.
    for angle in (minimum, maximum):
        start = len(vertices)
        vertices.extend((point(angle, radius * 0.88), point(angle, radius * 1.12)))
        edges.append((start, start + 1))

    return vertices, edges


def _use_object_wire_colors():
    """Make per-object preview colors visible in this screen's 3D Views."""
    screen = bpy.context.screen
    if screen is None:
        return
    for area in screen.areas:
        if area.type == "VIEW_3D":
            shading = area.spaces.active.shading
            if shading.wireframe_color_type != "OBJECT":
                shading.wireframe_color_type = "OBJECT"


def rebuild_chn_previews(root_object):
    if root_object is None or root_object.type != "EMPTY":
        return
    file_props = get_chn_file_properties(root_object)
    armature = file_props.armature
    _remove_previews(root_object, file_props)
    if armature is None or armature.type != "ARMATURE":
        return
    _use_object_wire_colors()

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
    show_angle_limits = file_props.show_angle_limits
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
        if show_angle_limits:
            rest_bone = armature.data.bones.get(reference_bone.name)
            angle_radius = max(0.03 * world_scale,
                               (rest_bone.length if rest_bone else 0.0) *
                               world_scale * 0.18,
                               radius * 1.25)
            for axis_index, (minimum, maximum) in enumerate(
                    zip(record.min_angle, record.max_angle)):
                arc_vertices, arc_edges = _angle_arc_geometry(
                    matrix, center, axis_index, minimum, maximum,
                    angle_radius * (1.0 + 0.06 * axis_index))
                _new_angle_preview(
                    root_object, armature, record, reference_bone, anim_id,
                    axis_index, arc_vertices, arc_edges, center)
