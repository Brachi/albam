import json
import bpy
import os
from mathutils import Quaternion


relative_path = "stored_frames\\rev2_hand_l.json"
frames_path = os.path.join(os.path.dirname(__file__), relative_path)


def _get_bone_rotation(bone):
    rot = bone.rotation_quaternion
    quat_value = (rot[0], rot[1], rot[2], rot[3])
    return quat_value


def dump_frames(filepath, armature, frame_interval):
    buffer = {}
    scene = bpy.context.scene
    scene.frame_current = 0
    while scene.frame_current <= scene.frame_end:
        keyframe = {}
        scene.frame_set(scene.frame_current)
        for bone in armature.pose.bones:
            keyframe[bone.name] = _get_bone_rotation(bone)
        buffer[scene.frame_current] = keyframe
        scene.frame_current += frame_interval

    with open(filepath, 'w') as file:
        json.dump(buffer, file, indent=4)


KEYFRAMES = {}

HAND_VG = [
    "hand_r",
    "lowerarm_hand_twist_r",
    "hand_l",
    "lowerarm_hand_twist_l",
]


def set_poses(armature, keyframe, frame):
    ob = armature
    ob.animation_data_clear()
    #  bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='POSE')

    for k, v in keyframe.items():
        pbone = ob.pose.bones[k]
        pbone.rotation_mode = 'QUATERNION'
        # Why?
        pbone.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        pbone.keyframe_insert(data_path="rotation_quaternion", frame=0)
        pbone.rotation_quaternion = Quaternion(v)

        bpy.ops.object.mode_set(mode='OBJECT')
        pbone.keyframe_insert(
            data_path="rotation_quaternion", frame=int(frame))


def bake_pose(object, frame):
    # Select the object you want to duplicate
    ob_og = object

    # Duplicate the object
    ob_copy = ob_og.copy()
    ob_copy.data = ob_og.data.copy()

    # Link the duplicated object to the current collection
    bpy.context.collection.objects.link(ob_copy)

    if "hand_l" in ob_copy.vertex_groups:
        side = "hand_l"
    else:
        side = "hand_r"

    # Assign a custom name to the duplicated object
    ob_copy.name = "pose_" + side + "_" + str(frame)
    with bpy.context.temp_override(object=ob_copy):
        bpy.ops.object.modifier_apply(modifier="armature")

    for vg in ob_copy.vertex_groups:
        if vg.name not in HAND_VG:
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

    armature = bpy.context.active_object
    #mesh = bpy.data.objects['pl2202.mod_0001']
    print("lenght is ", len(KEYFRAMES))
    for frame, key in KEYFRAMES.items():
        set_poses(armature, key, frame)
        bake_pose(bl_obj, frame)
