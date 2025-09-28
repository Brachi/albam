from ctypes import Structure, c_ulonglong
import io
import struct

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix

from ...registry import blender_registry
from .structs.lmt import Lmt


HACKY_BONE_INDEX_IK_FOOT_RIGHT = 19
HACKY_BONE_INDEX_IK_FOOT_LEFT = 23
HACKY_BONE_INDICES_IK_FOOT = {HACKY_BONE_INDEX_IK_FOOT_RIGHT, HACKY_BONE_INDEX_IK_FOOT_LEFT}
ROOT_UNK_BONE_ID = 254
ROOT_MOTION_BONE_ID = 255
ROOT_MOTION_BONE_NAME = 'root_motion'
ROOT_BONE_NAME = '0'


@blender_registry.register_import_function(app_id="re5", extension='lmt', file_category="ANIMATION")
def load_lmt(file_item, context):
    lmt_bytes = file_item.get_bytes()
    lmt = Lmt(KaitaiStream(io.BytesIO(lmt_bytes)))
    armature = context.scene.albam.import_options_lmt.armature
    mapping = _create_bone_mapping(armature)

    # DEBUG_BLOCK = 2
    DEBUG_BLOCK = None

    for block_index, block in enumerate(lmt.block_offsets):
        if block.offset == 0:
            continue
        if DEBUG_BLOCK is not None and DEBUG_BLOCK != block_index:
            continue
        armature.animation_data_create()
        name = f"{armature.name}.{file_item.display_name}.{str(block_index).zfill(4)}"
        action = bpy.data.actions.new(name)
        action.use_fake_user = True

        for track_index, track in enumerate(block.block_header.tracks):
            bone_index = mapping.get(str(track.bone_index))

            if bone_index is None and track.bone_index == ROOT_MOTION_BONE_ID:
                bone_index = _get_or_create_root_motion_bone(armature, mapping)

            elif bone_index is None and track.bone_index == ROOT_UNK_BONE_ID:
                # Probably some kind of object tracker bone (weapon?)
                # TODO: do something with this
                continue
            elif bone_index is None:
                # TODO: better stats
                print(f"bone_index not found!: [{track.bone_index}]")
                continue
            if track.bone_index in HACKY_BONE_INDICES_IK_FOOT:
                bone_index = _get_or_create_ik_bone(armature, track.bone_index, bone_index, mapping)

            if track.buffer_type == 6:
                TRACK_MODE = "rotation_quaternion"  # TODO: improve naming
                decoded_frames = decode_type_6(track.data)
            elif track.buffer_type == 2:
                TRACK_MODE = "location"
                decoded_frames = decode_type_2(track.data)
                decoded_frames = _parent_space_to_local(decoded_frames, armature, bone_index)
            elif track.buffer_type == 9:
                TRACK_MODE = "location"
                decoded_frames = decode_type_9(track.data)
                decoded_frames = _parent_space_to_local(decoded_frames, armature, bone_index)

            else:
                # TODO: print statistics of missing tracks
                # print("Unknown buffer_type, skipping", track.buffer_type)
                continue

            group_name = str(bone_index)
            group = action.groups.get(group_name) or action.groups.new(group_name)
            data_path = f"pose.bones[\"{bone_index}\"].{TRACK_MODE}"
            num_curv = len(decoded_frames[0])
            try:
                curves = [action.fcurves.new(data_path=data_path, index=i) for i in range(num_curv)]
                for c in curves:
                    c.group = group
            except RuntimeError as err:
                print('unknown error:', err)
                continue
            for frame_index, frame_data in enumerate(decoded_frames):
                if frame_data is None:
                    continue
                for curve_idx, curve in enumerate(curves):
                    curve.keyframe_points.add(1)
                    curve.keyframe_points[-1].co = (frame_index + 1, frame_data[curve_idx])
                    curve.keyframe_points[-1].interpolation = 'LINEAR'


def _create_bone_mapping(armature_obj):
    bone_names = {}
    for b_idx, mapped_bone in enumerate(armature_obj.data.bones):
        reference_bone_id = mapped_bone.get('mtfw.anim_retarget')  # TODO: better name
        if reference_bone_id is None:
            print(f"WARNING: {armature_obj.name}->{mapped_bone.name} doesn't contain a mapped bone")
            continue
        if reference_bone_id in bone_names:
            print(f"WARNING: bone_id {b_idx} already mapped. TODO")
        bone_names[reference_bone_id] = mapped_bone.name
    return bone_names


class FrameQuat4_14(Structure):
    _fields_ = (
        ('_w', c_ulonglong, 14),
        ('_z', c_ulonglong, 14),
        ('_y', c_ulonglong, 14),
        ('_x', c_ulonglong, 14),
        ('duration', c_ulonglong, 8)
    )
    RANGE_ALL = 2 ** 14 - 1
    RANGE_SPLIT = 2 ** 13 - 1

    @classmethod
    def _clip_and_divide(cls, num):
        if num > cls.RANGE_SPLIT:
            num -= cls.RANGE_ALL
        return num / 4096

    @property
    def w(self):
        return self._clip_and_divide(self._w)

    @property
    def x(self):
        return self._clip_and_divide(self._x)

    @property
    def y(self):
        return self._clip_and_divide(self._y)

    @property
    def z(self):
        return self._clip_and_divide(self._z)


def decode_type_9(data):
    decoded_frames = []
    CHUNK_SIZE = 16

    for start in range(0, len(data), CHUNK_SIZE):
        chunk = data[start: start + CHUNK_SIZE]
        u = struct.unpack("fffI", chunk)
        floats = u[:3]
        duration = u[3]
        floats = (u[0] / 100, u[1] / 100, u[2] / 100)

        decoded_frames.append(floats)
        decoded_frames.extend([None] * (duration - 1))

    return decoded_frames


def decode_type_2(data):
    decoded_frames = []
    CHUNK_SIZE = 12

    for start in range(0, len(data), CHUNK_SIZE):
        chunk = data[start: start + CHUNK_SIZE]
        u = struct.unpack("fff", chunk)
        floats = (u[0] / 100, u[1] / 100, u[2] / 100)
        decoded_frames.append(floats)
    return decoded_frames


def decode_type_6(data):
    decoded_frames = []

    for idx, start in enumerate(range(0, len(data), 8)):
        chunk = data[start: start + 8]
        frame = FrameQuat4_14()
        io.BytesIO(chunk).readinto(frame)

        decoded_frames.append((frame.w, frame.x, frame.y, frame.z))
        decoded_frames.extend([None] * (frame.duration - 1))

    return decoded_frames


def _get_or_create_ik_bone(armature, track_bone_index, bone_index, mapping):

    if track_bone_index == HACKY_BONE_INDEX_IK_FOOT_RIGHT:
        postfix = "R"
    else:
        postfix = "L"

    bone_name = f"IK_Foot.{postfix}"
    if bone_name in armature.data.bones:
        return bone_name

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    blender_bone = armature.data.edit_bones.new(bone_name)
    blender_bone.head = armature.data.edit_bones[bone_index].head
    blender_bone.tail = armature.data.edit_bones[bone_index].tail
    bpy.ops.object.mode_set(mode='OBJECT')

    pose_bone = armature.pose.bones[mapping.get(str(track_bone_index))]
    constraint = pose_bone.constraints.new('IK')
    constraint.target = armature
    constraint.subtarget = bone_name
    constraint.chain_count = 3
    constraint.use_rotation = True

    root_motion_bone = _get_or_create_root_motion_bone(armature, mapping)
    pose_bone = armature.pose.bones[bone_name]
    constraint = pose_bone.constraints.new('COPY_LOCATION')
    constraint.target = armature
    constraint.subtarget = root_motion_bone
    constraint.use_offset = True

    return bone_name


def _get_or_create_root_motion_bone(armature, mapping):
    bone_name = ROOT_MOTION_BONE_NAME
    if bone_name in armature.data.bones:
        return bone_name

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    blender_bone = armature.data.edit_bones.new(bone_name)
    blender_bone.tail[2] += 0.01
    bpy.ops.object.mode_set(mode='OBJECT')

    # set constrain for the root bone->root_motion
    pose_bone = armature.pose.bones[mapping.get(ROOT_BONE_NAME)]
    constraint = pose_bone.constraints.new('COPY_LOCATION')
    constraint.target = armature
    constraint.subtarget = bone_name
    constraint.use_offset = True

    return bone_name


def _parent_space_to_local(decoded_frames, armature, bone_index):
    local_space_frames = []
    for frame in decoded_frames:
        if frame is None:
            local_space_frames.append(None)
            continue
        bone = armature.data.bones[bone_index]
        if bone.parent:
            parent_space = bone.parent.matrix_local.inverted() @ bone.matrix_local
        else:
            # XXX Temp hack
            v = bone.matrix_local.to_translation()
            v = (v[0], v[2], -v[1])
            parent_space = Matrix.Identity(4).inverted() @ Matrix.Translation(v)
        local_space_frame = (parent_space.inverted() @ Matrix.Translation(frame)).to_translation()
        local_space_frames.append(local_space_frame)
    return local_space_frames


def filter_armatures(self, obj):
    # TODO: filter by custom properties that indicate is
    # a RE5 compatible armature
    return obj.type == 'ARMATURE'


@blender_registry.register_blender_prop_albam(name='import_options_lmt')
class ImportOptionsLMT(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(type=bpy.types.Object, poll=filter_armatures)


@blender_registry.register_import_options_custom_draw_func(extension='lmt')
def draw_lmt_options(panel_instance, context):
    panel_instance.bl_label = "LMT Options"
    panel_instance.layout.prop(context.scene.albam.import_options_lmt, 'armature')


@blender_registry.register_import_options_custom_poll_func(extension='lmt')
def poll_lmt_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension='lmt')
def poll_import_operator_for_lmt(panel_class, context):
    return bool(context.scene.albam.import_options_lmt.armature)
