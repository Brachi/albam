import json
import bpy
import os
from mathutils import Quaternion


KEYFRAMES = {}


HANDS_VG = {
    "l": ["hand_l", "lowerarm_hand_twist_l"],
    "r": ["hand_r", "lowerarm_hand_twist_r"],
}

LEFT_HAND_VG = [
    "hand_l",
    "lowerarm_hand_twist_l",
    "palm_l",
    "thumb_01_l",
    "thumb_02_l",
    "thumb_03_l",
    "index_01_l",
    "index_02_l",
    "index_03_l",
    "middle_01_l",
    "middle_02_l",
    "middle_03_l",
    "ring_01_l",
    "ring_02_l",
    "ring_03_l",
    "pinky_01_l",
    "pinky_02_l",
    "pinky_03_l",
]

RIGHT_HAND_VG = [
    "hand_r",
    "lowerarm_hand_twist_r",
    "palm_r",
    "thumb_01_r",
    "thumb_02_r",
    "thumb_03_r",
    "index_01_r",
    "index_02_r",
    "index_03_r",
    "middle_01_r",
    "middle_02_r",
    "middle_03_r",
    "ring_01_r",
    "ring_02_r",
    "ring_03_r",
    "pinky_01_r",
    "pinky_02_r",
    "pinky_03_r",
]

frames_folder = "stored_frames\\"
frames_path = os.path.join(os.path.dirname(__file__), frames_folder)


def _get_bone_rotation(bone):
    rot = bone.rotation_quaternion
    quat_value = (rot[0], rot[1], rot[2], rot[3])
    return quat_value


def _get_bone_location(bone):
    loc = bone.location
    loc_value = (loc[0], loc[1], loc[2])
    return loc_value


def dump_frames(filepath, armature, frame_interval, side="left"):
    buffer = {}
    hand_vg = LEFT_HAND_VG if side == "left" else RIGHT_HAND_VG
    scene = bpy.context.scene
    scene.frame_current = 0
    while scene.frame_current <= scene.frame_end:
        keyframe = {}
        scene.frame_set(scene.frame_current)
        for bone in armature.pose.bones:
            deforms = []
            if bone.name in hand_vg:
                if bone.rotation_mode != 'QUATERNION':
                    bone.rotation_mode = 'QUATERNION'
                deforms.append(_get_bone_location(bone))
                deforms.append(_get_bone_rotation(bone))
                keyframe[bone.name] = deforms
        buffer[scene.frame_current] = keyframe
        scene.frame_current += frame_interval

    with open(filepath, 'w') as file:
        json.dump(buffer, file, indent=4)


def set_poses(armature, keyframe, frame):
    ob = armature
    # ob.animation_data_clear()
    # bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='POSE')

    for bone_name, qframe in keyframe.items():
        pbone = ob.pose.bones[bone_name]
        pbone.rotation_mode = 'QUATERNION'
        # Why?
        pbone.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        pbone.keyframe_insert(data_path="rotation_quaternion", frame=0)
        pbone.rotation_quaternion = Quaternion(qframe[1])

        pbone.location = qframe[0]
        bpy.ops.object.mode_set(mode='OBJECT')
        pbone.keyframe_insert(
            data_path="rotation_quaternion", frame=int(frame))
        pbone.keyframe_insert(data_path="location", frame=int(frame))


def bake_pose(object, frame, side_id):
    ob_og = object

    # Duplicate the object
    ob_copy = ob_og.copy()
    ob_copy.data = ob_og.data.copy()

    # Link the duplicated object to the current collection
    bpy.context.collection.objects.link(ob_copy)

    if side_id == "l":
        side = "hand_l"
    else:
        side = "hand_r"

    armature_modifier = None
    for modifier in ob_copy.modifiers:
        if modifier.type == 'ARMATURE':
            armature_modifier = modifier
            break

    # Assign a custom name to the duplicated object
    ob_copy.name = "pose_" + side + "_" + str(frame)
    with bpy.context.temp_override(object=ob_copy):
        bpy.ops.object.modifier_apply(modifier=armature_modifier.name)

    # Merge vertex groups
    for vg in ob_copy.vertex_groups:
        if vg.name not in HANDS_VG[side_id]:
            merge_vgroups(ob_copy, side, vg.name)
    ob_copy.parent = None
    ob_copy.matrix_parent_inverse.identity()


def remove_vertex_group(obj, group_to_remove):
    group_index = obj.vertex_groups[group_to_remove].index

    # Iterate through vertices
    for vertex in obj.data.vertices:
        # Get the weight of the vertex in the group to remove
        weight_to_distribute = 0
        for group in vertex.groups:
            if group.group == group_index:
                weight_to_distribute = group.weight
                break

        # Distribute the weight to other groups
        if weight_to_distribute > 0:
            total_weight = sum(
                group.weight for group in vertex.groups if group.group != group_index)
            for group in vertex.groups:
                if group.group != group_index:
                    obj.vertex_groups[group.group].add(
                        [vertex.index], group.weight +
                        weight_to_distribute *
                        (group.weight / total_weight), 'REPLACE')

        # Remove the group from the vertex
        obj.vertex_groups[group_index].remove([vertex.index])

    # Remove the vertex group from the object
    obj.vertex_groups.remove(obj.vertex_groups[group_to_remove])


def merge_vgroups(ob, vg_a, vg_b):
    # based on https://blender.stackexchange.com/a/42779

    if (vg_a in ob.vertex_groups and vg_b in ob.vertex_groups):

        vg_merged = ob.vertex_groups.new(name=vg_a + "+" + vg_b)

        for id, vert in enumerate(ob.data.vertices):
            available_groups = [
                v_group_elem.group for v_group_elem in vert.groups]
            A = B = 0
            if ob.vertex_groups[vg_a].index in available_groups:
                A = ob.vertex_groups[vg_a].weight(id)
            if ob.vertex_groups[vg_b].index in available_groups:
                B = ob.vertex_groups[vg_b].weight(id)

            # only add to vertex group is weight is > 0
            sum = A + B
            if sum > 0:
                vg_merged.add([id], sum, 'REPLACE')
        # remove two vertex groups and rename the third as Group A
        ob.vertex_groups.remove(ob.vertex_groups[vg_a])
        ob.vertex_groups.remove(ob.vertex_groups[vg_b])
        vg_merged.name = vg_a


def handshake(filepath, bl_obj):
    with open(filepath, 'r') as file:
        KEYFRAMES = json.load(file)
    filename = os.path.splitext(os.path.basename(filepath))[0]
    side = filename.split("_")[-1]
    print("side is: ", side)
    armature = bpy.context.active_object
    print("lenght is {} frames".format(len(KEYFRAMES)))
    for frame, key in KEYFRAMES.items():
        set_poses(armature, key, frame)
        bpy.context.scene.frame_set(int(frame))
        bake_pose(bl_obj, frame, side)
