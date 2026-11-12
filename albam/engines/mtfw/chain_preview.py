"""Build non-selectable CCL child objects from pose-bone properties."""

import math

import bpy
from mathutils import Euler, Matrix, Vector

from .bone import get_anim_retarget
from .chain_props import (
    get_ccl_bone_properties,
    get_ccl_file_properties,
    get_ccl_primitive_properties,
)


_SHAPE_INDEX = {"SPHERE": 0, "CAPSULE": 1, "AABB": 2, "OBB": 3}
_MATERIALS = (
    ("Albam CCL Sphere", (0.27, 0.81, 0.42, 0.45)),
    ("Albam CCL Capsule", (0.56, 0.72, 0.16, 0.45)),
    ("Albam CCL AABB", (0.47, 0.11, 0.58, 0.45)),
    ("Albam CCL OBB", (0.81, 0.91, 0.57, 0.45)),
)


def _bone_matrix(armature, pose_bone):
    return armature.matrix_world @ armature.data.bones[pose_bone.name].matrix_local


def _local_point(game_xyz):
    # CCL vectors are already in the referenced bone's local space. Apply only
    # the centimetre-to-metre scale here; the bone matrix handles orientation.
    return Vector(game_xyz) * 0.01


def _world_point(armature, pose_bone, game_xyz):
    return _bone_matrix(armature, pose_bone) @ _local_point(game_xyz)


def _joint_map(armature):
    result = {}
    for pose_bone in sorted(armature.pose.bones, key=lambda bone: bone.name):
        value = get_anim_retarget(pose_bone, "re5")
        if not value:
            continue
        try:
            joint_id = int(value.split("_", 1)[0])
        except ValueError:
            continue
        result.setdefault(joint_id, pose_bone)
    return result


def _append_sphere(vertices, faces, face_materials, center, radius, material_index):
    if radius <= 0.0:
        return
    segments = 16
    rings = 8
    first_pole = len(vertices)
    vertices.append(tuple(center + Vector((0.0, 0.0, -radius))))
    ring_starts = []
    for ring in range(1, rings):
        latitude = -math.pi / 2.0 + math.pi * ring / rings
        z = radius * math.sin(latitude)
        ring_radius = radius * math.cos(latitude)
        ring_starts.append(len(vertices))
        for segment in range(segments):
            longitude = math.tau * segment / segments
            point = center + Vector((ring_radius * math.cos(longitude),
                                     ring_radius * math.sin(longitude), z))
            vertices.append(tuple(point))

    last_pole = len(vertices)
    vertices.append(tuple(center + Vector((0.0, 0.0, radius))))
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append((first_pole,
                      ring_starts[0] + next_segment,
                      ring_starts[0] + segment))
        face_materials.append(material_index)
        for ring_index in range(len(ring_starts) - 1):
            lower = ring_starts[ring_index]
            upper = ring_starts[ring_index + 1]
            faces.append((lower + segment, lower + next_segment,
                          upper + next_segment, upper + segment))
            face_materials.append(material_index)
        faces.append((ring_starts[-1] + segment,
                      ring_starts[-1] + next_segment,
                      last_pole))
        face_materials.append(material_index)


def _append_box(vertices, faces, face_materials, center, axes, material_index):
    signs = ((-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1),
             (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1))
    start = len(vertices)
    for sx, sy, sz in signs:
        point = center + axes[0] * sx + axes[1] * sy + axes[2] * sz
        vertices.append(tuple(point))
    faces.extend((
        (start + 0, start + 1, start + 3, start + 2),
        (start + 4, start + 6, start + 7, start + 5),
        (start + 0, start + 4, start + 5, start + 1),
        (start + 2, start + 3, start + 7, start + 6),
        (start + 0, start + 2, start + 6, start + 4),
        (start + 1, start + 5, start + 7, start + 3),
    ))
    face_materials.extend((material_index,) * 6)


def _append_capsule(vertices, faces, face_materials, start, end, radius, material_index):
    direction = end - start
    distance = direction.length
    if distance <= 1e-7:
        _append_sphere(vertices, faces, face_materials, start, radius, material_index)
        return
    if radius <= 0.0:
        return

    axis = direction / distance
    reference = Vector((1.0, 0.0, 0.0)) if abs(axis.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    tangent = axis.cross(reference).normalized()
    bitangent = axis.cross(tangent).normalized()
    segments = 16
    hemisphere_steps = 6
    rings = []

    for step in range(1, hemisphere_steps + 1):
        angle = -math.pi / 2.0 + (math.pi / 2.0) * step / hemisphere_steps
        rings.append((start, radius * math.sin(angle), radius * math.cos(angle)))
    for step in range(hemisphere_steps):
        angle = (math.pi / 2.0) * step / hemisphere_steps
        rings.append((end, radius * math.sin(angle), radius * math.cos(angle)))

    ring_starts = []
    for center, axial_offset, ring_radius in rings:
        ring_starts.append(len(vertices))
        ring_center = center + axis * axial_offset
        for segment in range(segments):
            angle = math.tau * segment / segments
            point = ring_center + ring_radius * (
                tangent * math.cos(angle) + bitangent * math.sin(angle))
            vertices.append(tuple(point))

    start_pole = len(vertices)
    vertices.append(tuple(start - axis * radius))
    end_pole = len(vertices)
    vertices.append(tuple(end + axis * radius))

    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append((start_pole, ring_starts[0] + segment, ring_starts[0] + next_segment))
        face_materials.append(material_index)
        for ring_index in range(len(ring_starts) - 1):
            lower = ring_starts[ring_index]
            upper = ring_starts[ring_index + 1]
            faces.append((lower + segment, lower + next_segment,
                          upper + next_segment, upper + segment))
            face_materials.append(material_index)
        faces.append((ring_starts[-1] + segment, end_pole,
                      ring_starts[-1] + next_segment))
        face_materials.append(material_index)


def _record_geometry(armature, joint_map, pose_bone, record,
                     vertices, faces, face_materials):
    shape = record.shape
    material_index = _SHAPE_INDEX.get(shape)
    if material_index is None:
        return

    matrix = _bone_matrix(armature, pose_bone)
    center = matrix @ _local_point(record.position)
    radius_scale = max(abs(value) for value in matrix.to_scale())
    radius = max(0.0, float(record.radius)) * 0.01 * radius_scale

    if shape == "SPHERE":
        _append_sphere(vertices, faces, face_materials, center, radius, material_index)
        return

    if shape == "CAPSULE":
        pair_bone = joint_map.get(record.pair_joint_no)
        if pair_bone is None:
            return
        tail = _world_point(armature, pair_bone, record.extent)
        _append_capsule(vertices, faces, face_materials, center, tail, radius, material_index)
        return

    extent = Vector(record.extent)
    rotation = Matrix.Identity(3)
    if shape == "OBB":
        rotation = Euler(tuple(record.angle), "XYZ").to_matrix()
    axes = []
    for axis_index in range(3):
        game_axis = Vector((
            extent[0] if axis_index == 0 else 0.0,
            extent[1] if axis_index == 1 else 0.0,
            extent[2] if axis_index == 2 else 0.0,
        ))
        local_axis = (rotation @ game_axis) * 0.01
        axes.append(matrix.to_3x3() @ local_axis)
    _append_box(vertices, faces, face_materials, center, axes, material_index)


def _preview_materials():
    materials = []
    for name, color in _MATERIALS:
        material = bpy.data.materials.get(name)
        if material is None:
            material = bpy.data.materials.new(name)
        material.diffuse_color = color
        materials.append(material)
    return materials


def _remove_preview_children(bl_object):
    for child in tuple(bl_object.children):
        if not child.get("_albam_ccl_preview", False):
            continue
        old_mesh = child.data if child.type == "MESH" else None
        bpy.data.objects.remove(child, do_unlink=True)
        if old_mesh and old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)


def _preview_object_name(pose_bone, record, collection_index):
    raw_id = get_anim_retarget(pose_bone, "re5")
    joint_id = raw_id.split("_", 1)[0] if raw_id else "unmapped"
    try:
        joint_id = f"{int(joint_id):03d}"
    except ValueError:
        pass
    record_id = (f"{record.record_index:04d}" if record.record_index >= 0
                 else f"new_{collection_index:02d}")
    return f"CCL_{joint_id}_{record_id}"


def _create_preview_object(bl_object, armature, joint_map, pose_bone, record, collection_index,
                           name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.material_index = 0
    mesh.update()

    preview_object = bpy.data.objects.new(name, mesh)
    preview_object.parent = bl_object
    for collection in bl_object.users_collection:
        collection.objects.link(preview_object)
    preview_object.hide_select = True
    preview_object.hide_render = True
    preview_object["_albam_ccl_preview"] = True
    preview_object["albam_ccl_bone_name"] = pose_bone.name
    preview_object["albam_ccl_record_index"] = record.record_index
    preview_object["albam_ccl_record_slot"] = collection_index
    raw_anim_id = get_anim_retarget(pose_bone, "re5")
    anim_id = int(raw_anim_id.split("_", 1)[0]) if raw_anim_id else -1
    preview_object["albam_ccl_joint_id"] = anim_id

    bound_props = get_ccl_primitive_properties(preview_object)
    bound_props.armature = armature
    bound_props.reference_bone_name = pose_bone.name
    bound_props.anim_id = anim_id
    bound_props.record_index = record.record_index
    bound_props.record_slot = collection_index
    bound_props.shape = record.shape
    if record.shape == "CAPSULE":
        bound_props.pair_joint_id = record.pair_joint_no
        pair_bone = joint_map.get(record.pair_joint_no)
        bound_props.pair_bone_name = pair_bone.name if pair_bone else ""
    else:
        bound_props.pair_joint_id = -1
        bound_props.pair_bone_name = ""
    record.preview_object = preview_object
    return preview_object


def rebuild_ccl_preview(bl_object):
    file_props = get_ccl_file_properties(bl_object)
    armature = file_props.armature if file_props else None
    if armature is None or armature.type != "ARMATURE":
        return

    _remove_preview_children(bl_object)
    joint_map = _joint_map(armature)
    materials = _preview_materials()
    for pose_bone in armature.pose.bones:
        bone_props = get_ccl_bone_properties(pose_bone)
        for collection_index, record in enumerate(bone_props.records):
            vertices = []
            faces = []
            face_materials = []
            _record_geometry(armature, joint_map, pose_bone, record,
                             vertices, faces, face_materials)
            material_index = _SHAPE_INDEX.get(record.shape)
            if material_index is None:
                continue
            _create_preview_object(
                bl_object,
                armature,
                joint_map,
                pose_bone,
                record,
                collection_index,
                _preview_object_name(pose_bone, record, collection_index),
                vertices,
                faces,
                materials[material_index],
            )


def rebuild_armature_previews(armature):
    if armature is None or armature.type != "ARMATURE":
        return
    for bl_object in tuple(bpy.data.objects):
        if bl_object.type != "EMPTY" or bl_object.albam_asset.extension != "ccl":
            continue
        file_props = get_ccl_file_properties(bl_object)
        if file_props and file_props.armature == armature:
            try:
                rebuild_ccl_preview(bl_object)
            except (ReferenceError, RuntimeError):
                # Blender can invalidate RNA references while an object is being removed.
                continue
