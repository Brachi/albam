from ctypes import Structure, c_ulonglong
import io
import struct

import bpy
from mathutils import Matrix

from ...lib.kaitai_utils import parse
from ...registry import blender_registry
from .structs.lmt import Lmt


HACKY_BONE_INDEX_IK_FOOT_RIGHT = 19
HACKY_BONE_INDEX_IK_FOOT_LEFT = 23
HACKY_BONE_INDICES_IK_FOOT = {HACKY_BONE_INDEX_IK_FOOT_RIGHT, HACKY_BONE_INDEX_IK_FOOT_LEFT}
ROOT_UNK_BONE_ID = 254
ROOT_MOTION_BONE_ID = 255
ROOT_MOTION_BONE_NAME = 'root_motion'
ROOT_BONE_NAME = '0'

LMT_VERSION_67 = 67
UNITS_PER_METER = 100

TRACK_MODE_ROTATION = "rotation_quaternion"
TRACK_MODE_LOCATION = "location"
TRACK_MODE_SCALE = "scale"

# track67.usage - which pose bone channel a track drives. The reference
# value of a usage carries that channel's identity when the track has no
# keyframes of its own: an identity quaternion, a zero vector, a unit
# scale. The 3/4/5 variants show up on the root motion bone.
TRACK_MODES_67 = {
    0: TRACK_MODE_ROTATION,
    1: TRACK_MODE_LOCATION,
    2: TRACK_MODE_SCALE,
    3: TRACK_MODE_ROTATION,
    4: TRACK_MODE_LOCATION,
    5: TRACK_MODE_SCALE,
}

# track67.buffer_type - how the keyframes of a version 67 track are stored.
BUFFER_TYPE_SINGLE_VECTOR3 = 1
BUFFER_TYPE_SINGLE_QUATERNION = 2
BUFFER_TYPE_LINEAR_VECTOR3 = 3
BUFFER_TYPE_BILINEAR_VECTOR3_16BIT = 4
BUFFER_TYPE_BILINEAR_VECTOR3_8BIT = 5
BUFFER_TYPE_LINEAR_QUATERNION_14BIT = 6
BUFFER_TYPE_BILINEAR_QUATERNION_7BIT = 7


def _get_action_channels(action, armature):
    """The container an action keeps its fcurves and groups in.

    Blender 4.4 moved both behind an action's layers and slots, and 5.0
    removed the flat Action.fcurves/Action.groups shortcuts altogether.
    """
    if hasattr(action, "fcurves"):
        return action
    slot = action.slots.new(id_type='OBJECT', name=armature.name)
    strip = action.layers.new("Layer").strips.new(type='KEYFRAME')
    return strip.channelbag(slot, ensure=True)


@blender_registry.register_import_function(app_id="re5", extension='lmt', albam_asset_type="ANIMATION")
@blender_registry.register_import_function(app_id="umvc3", extension='lmt', albam_asset_type="ANIMATION")
def load_lmt(file_item, context):
    lmt_bytes = file_item.get_bytes()
    lmt = parse(Lmt, lmt_bytes, file_item.app_id)
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
        channels = _get_action_channels(action, armature)

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
            is_ik_foot = track.bone_index in HACKY_BONE_INDICES_IK_FOOT
            if lmt.version != LMT_VERSION_67 and is_ik_foot:
                bone_index = _get_or_create_ik_bone(armature, track.bone_index, bone_index, mapping)

            if lmt.version == LMT_VERSION_67:
                decoded = decode_track_67(track)
            else:
                decoded = decode_track_51(track)
            if decoded is None:
                # TODO: print statistics of missing tracks
                continue
            TRACK_MODE, decoded_frames = decoded  # TODO: improve naming
            if not decoded_frames:
                continue
            if TRACK_MODE == TRACK_MODE_LOCATION:
                decoded_frames = _parent_space_to_local(decoded_frames, armature, bone_index)

            group_name = str(bone_index)
            group = channels.groups.get(group_name) or channels.groups.new(group_name)
            data_path = f"pose.bones[\"{bone_index}\"].{TRACK_MODE}"
            num_curv = len(decoded_frames[0])
            try:
                curves = [channels.fcurves.new(data_path=data_path, index=i)
                          for i in range(num_curv)]
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


def _get_action_channels(action, armature):
    """The container an action keeps its fcurves and groups in.

    Blender 4.4 moved both behind an action's layers and slots, and 5.0
    dropped the flat lists that used to sit on the action itself.
    """
    if hasattr(action, "fcurves"):
        return action
    slot = action.slots.new(id_type='OBJECT', name=armature.name)
    strip = action.layers.new("Layer").strips.new(type='KEYFRAME')
    return strip.channelbag(slot, ensure=True)


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


def decode_track_51(track):
    """Returns (track mode, one entry per frame) for a version 51 track,
    or None when its buffer type isn't decoded yet."""
    if track.buffer_type == 6:
        return TRACK_MODE_ROTATION, decode_type_6(track.data)
    if track.buffer_type == 2:
        return TRACK_MODE_LOCATION, decode_type_2(track.data)
    if track.buffer_type == 9:
        return TRACK_MODE_LOCATION, decode_type_9(track.data)
    return None


def decode_track_67(track):
    """Returns (track mode, one entry per frame) for a version 67 track,
    or None when its usage or buffer type isn't decoded yet.

    A frame entry is None when the previous entry's duration still covers
    it. Translations come out in meters, everything else unit-less.
    """
    track_mode = TRACK_MODES_67.get(track.usage)
    if track_mode is None:
        return None

    reference = track.unk_reference_data
    buffer_type = track.buffer_type

    if buffer_type == BUFFER_TYPE_SINGLE_VECTOR3:
        frames = [tuple(reference[:3])]
    elif buffer_type == BUFFER_TYPE_SINGLE_QUATERNION:
        frames = [(reference[3], reference[0], reference[1], reference[2])]
    elif buffer_type == BUFFER_TYPE_LINEAR_VECTOR3:
        frames = decode_linear_vector3(track.data)
    elif buffer_type == BUFFER_TYPE_LINEAR_QUATERNION_14BIT:
        frames = decode_type_6(track.data)
    elif buffer_type in (BUFFER_TYPE_BILINEAR_VECTOR3_16BIT,
                         BUFFER_TYPE_BILINEAR_VECTOR3_8BIT,
                         BUFFER_TYPE_BILINEAR_QUATERNION_7BIT):
        scale, base = _get_bilinear_range(track)
        if scale is None:
            return None
        if buffer_type == BUFFER_TYPE_BILINEAR_QUATERNION_7BIT:
            frames = decode_bilinear_quaternion(track.data, scale, base)
        else:
            num_bits = 16 if buffer_type == BUFFER_TYPE_BILINEAR_VECTOR3_16BIT else 8
            frames = decode_bilinear_vector3(track.data, scale, base, num_bits)
    else:
        return None

    if track_mode == TRACK_MODE_LOCATION:
        frames = [f if f is None else tuple(c / UNITS_PER_METER for c in f)
                  for f in frames]
    return track_mode, frames


def _get_bilinear_range(track):
    """The (scale, base) vectors a bi-linear buffer type quantizes against:
    each component is stored as an integer fraction of its own range, so
    component i of a frame is base[i] + raw[i] / max_raw * scale[i].
    """
    float_buffer = track.ofs_floats.body
    if float_buffer is None:
        return None, None
    floats = float_buffer.unk_00
    return floats[0:4], floats[4:8]


def decode_linear_vector3(data):
    """Three floats plus a u32 duration per entry."""
    decoded_frames = []
    CHUNK_SIZE = 16

    for start in range(0, len(data) - CHUNK_SIZE + 1, CHUNK_SIZE):
        x, y, z, duration = struct.unpack_from("<fffI", data, start)
        decoded_frames.append((x, y, z))
        decoded_frames.extend([None] * (duration - 1))

    return decoded_frames


def decode_bilinear_vector3(data, scale, base, num_bits):
    """Three num_bits-wide components plus a duration of the same width."""
    decoded_frames = []
    chunk_size = num_bits // 2
    max_raw = float((1 << num_bits) - 1)

    for start in range(0, len(data) - chunk_size + 1, chunk_size):
        if num_bits == 8:
            raw = data[start: start + chunk_size]
        else:
            raw = struct.unpack_from("<4H", data, start)
        floats = tuple(base[i] + (raw[i] / max_raw) * scale[i] for i in range(3))
        decoded_frames.append(floats)
        decoded_frames.extend([None] * (raw[3] - 1))

    return decoded_frames


def decode_bilinear_quaternion(data, scale, base):
    """Four 7 bit components, w z y x from the low bit up, plus a 4 bit
    duration, packed into one u32."""
    decoded_frames = []
    CHUNK_SIZE = 4
    MAX_RAW = float(2 ** 7 - 1)

    for start in range(0, len(data) - CHUNK_SIZE + 1, CHUNK_SIZE):
        packed = struct.unpack_from("<I", data, start)[0]
        x, y, z, w = (base[i] + (((packed >> (7 * (3 - i))) & 0x7F) / MAX_RAW) * scale[i]
                      for i in range(4))
        decoded_frames.append((w, x, y, z))
        decoded_frames.extend([None] * ((packed >> 28) - 1))

    return decoded_frames


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
    root_bone_name = mapping.get(ROOT_BONE_NAME)
    if root_bone_name is not None:
        pose_bone = armature.pose.bones[root_bone_name]
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
