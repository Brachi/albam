from ctypes import Structure, c_ulonglong
import io
import struct
import math
from io import BytesIO
from albam.vfs import VirtualFileData

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix, Quaternion

from albam.registry import blender_registry
from .structs.lmt import Lmt


HACKY_BONE_INDEX_IK_FOOT_RIGHT = 19
HACKY_BONE_INDEX_IK_FOOT_LEFT = 23
HACKY_BONE_INDICES_IK_FOOT = {HACKY_BONE_INDEX_IK_FOOT_RIGHT, HACKY_BONE_INDEX_IK_FOOT_LEFT}
ROOT_UNK_BONE_ID = 254
ROOT_MOTION_BONE_ID = 255
ROOT_MOTION_BONE_NAME = 'root_motion'
ROOT_BONE_NAME = '0'
BOUNDS_BUFF_TYPES = [4, 5, 7, 11, 12, 13, 14, 15]
# Usage
# U_QUATERNION = 0x0, Local Rotation
# U_TRANSLATE = 0x1,  Local Position
# U_SCALE = 0x2, Local Scale
# U_NULL_QUATERNION = 0x3, Absolute Rotation
# U_NULL_TRANSLATE = 0x4, Absolute Position
# U_NULL_SCALE = 0x5, Unknown
USAGE = {
    0: "rotation",  # Local rotation
    1: "position",  # Local Position
    2: "scale",  # Local Scale
    3: "rotation",  # Absolute Rotation
    4: "position",  # Absolute Position
    5: "scale",  # Unknown
}

APPID_VERSION_MAPPER = {
    "re0": 67,
    "re1": 67,
    "re5": 51,
    "re6": 67,
    "rev1": 67,
    "rev2": 67,
    "dd": 67,
}


class LMTKeyframeBounds:
    def __init__(self, bound):
        self.addin = bound.addin
        self.offset = bound.offset

    def lerp3(self, fraction):
        """fraction: list/tuple/array of 4 floats"""
        # Returns only x, y, z (as point3)
        return [
            self.offset[i] + fraction[i] * self.addin[i]
            for i in range(3)
        ]

    def lerpq(self, fraction):
        """fraction: list/tuple/array of 4 floats"""
        # Returns quaternion (x, y, z, w)
        return [
            self.offset[0] + fraction[0] * self.addin[0],
            self.offset[1] + fraction[1] * self.addin[1],
            self.offset[2] + fraction[2] * self.addin[2],
            self.offset[3] + fraction[3] * self.addin[3],
        ]


@blender_registry.register_import_function(app_id="re5", extension='lmt', file_category="ANIMATION")
@blender_registry.register_import_function(app_id="rev1", extension='lmt', file_category="ANIMATION")
@blender_registry.register_import_function(app_id="rev2", extension='lmt', file_category="ANIMATION")
def load_lmt(file_list_item, context):
    app_id = file_list_item.app_id
    lmt_bytes = file_list_item.get_bytes()
    lmt = Lmt(KaitaiStream(io.BytesIO(lmt_bytes)))
    lmt._read()
    lmt_ver = lmt.version
    armature = context.scene.albam.import_options_lmt.armature
    mapping = _create_bone_mapping(armature)

    # DEBUG_BLOCK = 2
    DEBUG_BLOCK = None
    bl_object_name = file_list_item.display_name
    bl_object = bpy.data.objects.new(bl_object_name, None)

    for block_index, block in enumerate(lmt.block_offsets):
        anim_object_name = f"{file_list_item.display_name}.{str(block_index).zfill(4)}"
        anim_object = bpy.data.objects.new(anim_object_name, None)
        anim_object.parent = bl_object
        if block.offset == 0:
            continue
        if DEBUG_BLOCK is not None and DEBUG_BLOCK != block_index:
            continue
        armature.animation_data_create()
        name = f"{armature.name}.{file_list_item.display_name}.{str(block_index).zfill(4)}"
        action = bpy.data.actions.new(name)
        action.use_fake_user = True

        tracks = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
                "tracks"]
        for track_index, track in enumerate(block.block_header.tracks):
            # Custom attributes for a track
            item = tracks.tracks.add()
            item.copy_custom_properties_from(track)
            item.raw_data = track.data
            # print("Buffer type: ", track.buffer_type, "Usage:", USAGE[track.usage])
            if lmt_ver > 51:
                bounds = None
                bounds_body = track.bounds
                if bounds_body:
                    b_item = item.track_bounds.add()
                    b_item.copy_custom_properties_from(track.bounds)
                    bounds = LMTKeyframeBounds(track.bounds)

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

            TRACK_MODE = USAGE[track.usage]
            if track.len_data > 0:
                if track.buffer_type == 6:
                    # TRACK_MODE = "rotation_quaternion"  # TODO: improve naming
                    decoded_frames = decode_type_6(track.data)
                elif track.buffer_type == 4:
                    # TRACK_MODE = "rotation_quaternion"
                    decoded_frames = decode_type_4(track.data, lmt_ver, bounds)
                elif track.buffer_type == 2:
                    # TRACK_MODE = "location"
                    decoded_frames = decode_type_2(track.data)
                    # decoded_frames = _parent_space_to_local(decoded_frames, armature, bone_index)
                elif track.buffer_type == 9:
                    # TRACK_MODE = "location"
                    decoded_frames = decode_type_9(track.data)
                    # decoded_frames = _parent_space_to_local(decoded_frames, armature, bone_index)

                else:
                    # TODO: print statistics of missing tracks
                    print("Unknown buffer_type, skipping", track.buffer_type)
                    continue
            else:
                continue
                ref_data = track.reference_data
                decoded_frames = [ref_data]

            if track.usage > 2:
                decoded_frames = _parent_space_to_local(decoded_frames, armature, bone_index)

            group_name = str(bone_index)
            group = action.groups.get(group_name) or action.groups.new(group_name)
            data_path = f"pose.bones[\"{bone_index}\"].{TRACK_MODE}"
            num_curv = len(decoded_frames[0])
            try:
                curves = [action.fcurves.new(data_path=data_path, index=i) for i in range(num_curv)]
                for c in curves:
                    c.group = group
            except RuntimeError as err:
                print('unknown error:', err, "Block index: {0}, Track index:{1}".format(block_index, track_index))
                continue
            for frame_index, frame_data in enumerate(decoded_frames):
                if frame_data is None:
                    continue
                for curve_idx, curve in enumerate(curves):
                    curve.keyframe_points.add(1)
                    curve.keyframe_points[-1].co = (frame_index + 1, frame_data[curve_idx])
                    curve.keyframe_points[-1].interpolation = 'LINEAR'
        custom_properties = anim_object.albam_custom_properties.get_custom_properties_for_appid(
            app_id)
        custom_properties.copy_custom_properties_from(block.block_header)
        custom_properties.action = action
        if lmt_ver < 67:
            col_events = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
                "col_events"]
            col_events.copy_custom_properties_from(block.block_header.collision_events)
            for attr_index, attribute in enumerate(block.block_header.collision_events.attributes):
                item = col_events.attributes.add()
                item.copy_custom_properties_from(attribute)

            motion_se = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
                "motion_se"]
            motion_se.copy_custom_properties_from(block.block_header.motion_sound_effects)
            for attr_index, attribute in enumerate(block.block_header.motion_sound_effects.attributes):
                item = motion_se.attributes.add()
                item.copy_custom_properties_from(attribute)
        else:
            seq_infos = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
                "sequence_infos"]
            # seq_info.copy_custom_properties_from(block.block_header.sequence_infos)
            for s_index, s_info in enumerate(block.block_header.sequence_infos):
                item = seq_infos.sequence_info.add()
                item.copy_custom_properties_from(s_info)
                for attr_index, s_attr in enumerate(s_info.attributes):
                    a_item = item.attributes.add()
                    a_item.copy_custom_properties_from(s_attr)

            keyframe_infos = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
                "keyframe_infos"]
            if len(block.block_header.key_infos) > 0:
                for k_index, k_info in enumerate(block.block_header.key_infos):
                    item = keyframe_infos.keyframe_info.add()
                    item.copy_custom_properties_from(k_info)
                    for kb_index, k_block in enumerate(k_info.keyframe_blocks):
                        k_item = item.keyframe_blocks.add()
                        k_item.copy_custom_properties_from(k_block)

    bl_object.albam_asset.original_bytes = lmt_bytes
    bl_object.albam_asset.app_id = app_id
    bl_object.albam_asset.relative_path = file_list_item.relative_path
    bl_object.albam_asset.extension = file_list_item.extension

    exportable = context.scene.albam.exportable.file_list.add()
    exportable.bl_object = bl_object

    context.scene.albam.exportable.file_list.update()
    return bl_object


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


class LMTUniKey:
    def __init__(self):
        self.value = [0.0, 0.0, 0.0]
        self.intangenttype = "custom"
        self.outtangenttype = "custom"
        self.intangent = [0.0, 0.0, 0.0]
        self.outtangent = [0.0, 0.0, 0.0]


class LMTQuadraticVector3:
    def __init__(self, chunk):
        self.frame = LMTUniKey()
        self.relframe = 0
        self.nextframeintangent = [0.0, 0.0, 0.0]
        self.size = 0

        # Reading of the data
        addcount = int.from_bytes(chunk.read(1), "little")
        flags = int.from_bytes(chunk.read(1), "little")

        self.relframe = struct.unpack("<H", chunk.read(2))[0]
        self.frame.value = list(struct.unpack("<3f", chunk.read(12)))
        float_fmt = "<f"

        # Default tangents = 0
        self.frame.outtangent = [0.0, 0.0, 0.0]
        self.nextframeintangent = [0.0, 0.0, 0.0]

        # Read flags
        for b in range(1, 9):
            if flags & (1 << (b - 1)):
                if b == 1:
                    self.frame.outtangent[0] = struct.unpack(float_fmt, chunk.read(4))[0]
                elif b == 2:
                    self.frame.outtangent[1] = struct.unpack(float_fmt, chunk.read(4))[0]
                elif b == 3:
                    self.frame.outtangent[2] = struct.unpack(float_fmt, chunk.read(4))[0]
                elif b == 4:
                    self.nextframeintangent[0] = struct.unpack(float_fmt, chunk.read(4))[0]
                elif b == 5:
                    self.nextframeintangent[1] = struct.unpack(float_fmt, chunk.read(4))[0]
                elif b == 6:
                    self.nextframeintangent[2] = struct.unpack(float_fmt, chunk.read(4))[0]
                # b==7,8 not used

        # Scale tangents
        if self.relframe != 0:
            self.frame.outtangent = [x * (0.19 / self.relframe) for x in self.frame.outtangent]
            self.nextframeintangent = [x * (-0.19 / self.relframe) for x in self.nextframeintangent]
        self.size = addcount


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


class LMTQuatized32Quat(Structure):
    def __init__(self, ivalue):
        self.bitmask = 0x7f
        self.ivalue = ivalue


# LMTVec3 Single Vector
def decode_type_1(data):
    decoded_framers = []
    u = struct.unpack("fff", data)
    floats = (u[0] / 100, u[1] / 100, u[2] / 100)
    return decoded_framers[floats]


# LMTVec3Frame12 T_VECTOR3_CONST = 0x2,
def decode_type_2(data, bound):
    decoded_frames = []
    CHUNK_SIZE = 12

    for start in range(0, len(data), CHUNK_SIZE):
        chunk = data[start: start + CHUNK_SIZE]
        u = struct.unpack("fff", chunk)
        frame = (u[0] / 100, u[1] / 100, u[2] / 100)
        frame = bound.lerp3(frame)
        decoded_frames.append(frame)
    return decoded_frames


# LMTVec3Frame16
def decode_type_3(data):
    decoded_frames = []
    CHUNK_SIZE = 16
    for start in range(0, len(data), CHUNK_SIZE):
        chunk = data[start: start + CHUNK_SIZE]
        u = struct.unpack("fffI", chunk)
        decoded_frames.append(u[0] / 100, u[1] / 100, u[2] / 100)
        duration = u[3]
        decoded_frames.extend([None] * (duration - 1))
    return decoded_frames


# LMTQuat3Frame but LMTQuatized16Vec3 for ver55+
def decode_type_4(data, lmt_ver, bounds=None):
    decoded_frames = []
    if lmt_ver > 55:
        # LMTQuatized16Vec3
        CHUNK_SIZE = 8
        for start in range(0, len(data), CHUNK_SIZE):
            chunk = data[start: start + CHUNK_SIZE]
            u = struct.unpack("HHHH", chunk)
            frame = (u[0] / 100, u[1] / 100, u[2] / 100)
            frame = bounds.lerp3(frame)
            decoded_frames.append(frame)
            duration = u[3]
            decoded_frames.extend([None] * (duration - 1))
    else:
        # LMTQuat3Frame
        CHUNK_SIZE = 12
        for start in range(0, len(data), CHUNK_SIZE):
            chunk = data[start: start + CHUNK_SIZE]
            u = struct.unpack("fff", chunk)
            w = math.sqrt(1.0 - u[0]*u[0] - u[1]*u[1] - u[2]*u[2])
        decoded_frames.append((w, u[0], u[1], u[2]))
    return decoded_frames


# LMTQuadraticVector3 but LMTQuatized8Vec3 for ver55+
def decode_type_5(data, lmt_ver, bounds=None):
    decoded_frames = []
    if lmt_ver > 55:
        CHUNK_SIZE = 4
        for start in range(0, len(data), CHUNK_SIZE):
            chunk = data[start: start + CHUNK_SIZE]
            u = struct.unpack("BBBB", chunk)
            frame = (u[0] / 100, u[1] / 100, u[2] / 100)
            frame = bounds.lerp3(frame)
            decoded_frames.append(frame)
            duration = u[3]
            decoded_frames.extend([None] * (duration - 1))
    return decoded_frames


# LMTQuatFramev14 T_POLAR3KEY = 0x6, Spherical Rotation
def decode_type_6(data):
    decoded_frames = []
    CHUNK_SIZE = 8
    for idx, start in enumerate(range(0, len(data), CHUNK_SIZE)):
        chunk = data[start: start + CHUNK_SIZE]
        frame = FrameQuat4_14()
        io.BytesIO(chunk).readinto(frame)

        decoded_frames.append((frame.w, frame.x, frame.y, frame.z))
        # Add empty frames to fill gaps between keyframes
        decoded_frames.extend([None] * (frame.duration - 1))

    return decoded_frames


# LMTQuatized32Quat
def decode_type_7(data):
    print("Not Implemented")


# LMTVec3Frame_9 T_LINEARKEY = 0x9,
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


# LMTXWQuat
def decode_type_11(data):
    print("Not Implemented")


# LMTYWQuat
def decode_type_12(data):
    print("Not Implemented")


# LMTZWQuat
def decode_type_13(data):
    print("Not Implemented")


# LMTQuatized11Quat
def decode_type_14(data):
    print("Not Implemented")


# LMTQuatized9Quat
def decode_type_15(data):
    print("Not Implemented")


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


def _parent_space_to_local_rotation(decoded_frames, armature, bone_index):
    local_space_frame = []
    for frame in decoded_frames:
        if frame is None:
            local_space_frame.append(None)
            continue
        bone = armature.data.bones[bone_index]
        parent_matrix = bone.parent.matrix_local if bone.parent else Matrix.Identity(4)
        bone_matrix = bone.matrix_local

        parent_rot = parent_matrix.to_quaternion()
        bone_rot = Quaternion(frame)  # frame (w, x, y, z)
        local_rot = parent_rot.inverted() @ bone_rot
        local_space_frame.append(local_rot)
    return local_space_frame


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


def _pre_serialize_offset(dst_lmt, num_anim_blocks):
    block_offsets = []
    for i in range(num_anim_blocks):
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        block_offset.offset = 0
    return block_offsets


def _calculate_offsets_lmt51(bl_objects, app_id):
    HEADER_SIZE = 8
    BLOCK_OFFSET_SIZE = 4
    MOTION_HEADER_SIZE = 192
    ATTR_SIZE = 8
    TRACK_SIZE = 32

    num_blocks = len(bl_objects)
    block_offsets_table_size = num_blocks * BLOCK_OFFSET_SIZE

    block_offsets = []
    frame_offsets = []
    collision_attr_offsets = []
    motion_se_attr_offsets = []
    track_data_offsets = []

    total_headers_size = 0
    motion_body_sizes = []
    tracks_headers_sizes = []
    tracks_data_sizes = []
    collision_attr_sizes = []
    motion_se_attr_sizes = []
    tracks_raw_data_sizes = []

    cur_ofc_bloc_offsets = HEADER_SIZE + block_offsets_table_size
    for bl_obj in bl_objects:
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.ofs_frame != 0:
            ofc = cur_ofc_bloc_offsets
            block_offsets.append(ofc)
            cur_ofc_bloc_offsets += MOTION_HEADER_SIZE
            total_headers_size += MOTION_HEADER_SIZE

            second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
            tracks = getattr(second_props["tracks"], "tracks")
            t_size = len(tracks) * TRACK_SIZE
            raw_data_size = sum(len(track.raw_data) for track in tracks)
            tracks_headers_sizes.append(t_size)
            tracks_data_sizes.append(raw_data_size)
            tracks_raw_data_sizes.append([len(track.raw_data) for track in tracks])

            col_events_attr = getattr(second_props["col_events"], "attributes")
            ce_attr_size = len(col_events_attr) * ATTR_SIZE
            collision_attr_sizes.append(ce_attr_size)

            motion_se_attr = getattr(second_props["motion_se"], "attributes")
            mse_attr_size = len(motion_se_attr) * ATTR_SIZE
            motion_se_attr_sizes.append(mse_attr_size)

            motion_body_size = t_size + raw_data_size + ce_attr_size + mse_attr_size
            motion_body_sizes.append(motion_body_size)
        else:
            tracks_headers_sizes.append(0)
            tracks_data_sizes.append(0)
            collision_attr_sizes.append(0)
            motion_se_attr_sizes.append(0)
            tracks_raw_data_sizes.append([])
            motion_body_sizes.append(0)
            block_offsets.append(0)

    motion_body_start = HEADER_SIZE + block_offsets_table_size + total_headers_size
    cur_frame_offset = motion_body_start

    for i in range(num_blocks):
        if motion_body_sizes[i] > 0:
            frame_offsets.append(cur_frame_offset)
            collision_attr_offsets.append(cur_frame_offset + tracks_headers_sizes[i] + tracks_data_sizes[i])
            motion_se_attr_offsets.append(cur_frame_offset + tracks_headers_sizes[i] + tracks_data_sizes[i]
                                          + collision_attr_sizes[i])

            # Offset for raw data
            data_offsets = []
            temp_size = 0
            for t_size in tracks_raw_data_sizes[i]:
                data_offsets.append(cur_frame_offset + tracks_headers_sizes[i] + temp_size)
                temp_size += t_size
            track_data_offsets.append(data_offsets)

            cur_frame_offset += motion_body_sizes[i]
        else:
            frame_offsets.append(0)
            collision_attr_offsets.append(0)
            motion_se_attr_offsets.append(0)
            track_data_offsets.append([])

    final_size = (
        HEADER_SIZE +
        block_offsets_table_size +
        total_headers_size +
        sum(motion_body_sizes)
    )
    return {
        "block_offsets": block_offsets,
        "frame_offsets": frame_offsets,
        "collision_attr_offsets": collision_attr_offsets,
        "motion_se_attr_offsets": motion_se_attr_offsets,
        "track_data_offsets": track_data_offsets,
        "final_size": final_size
    }


def _calculate_offsets_lmt67(bl_objects, app_id):
    HEADER_SIZE = 8
    BLOCK_OFFSET_SIZE = 4
    MOTION_HEADER_SIZE = 64  # 4 bytes of padding, last one doesn't have it
    SQ_ATTR_SIZE = 8
    KF_ATTR_SIZE = 16
    TRACK_SIZE = 36
    BOUND_SIZE = 32
    SEQ_INFO_SIZE = 72
    KF_INFO_SIZE = 12
    BOUNDS_BUFF_TYPES = {4, 5, 7, 11, 12, 13, 14, 15}

    num_blocks = len(bl_objects)
    block_offsets_table_size = num_blocks * BLOCK_OFFSET_SIZE

    total_headers_size = 0
    sz_motion_body_sizes = []
    sz_track_headers = []
    sz_track_data = []
    sz_tracks_raw_data = []
    sz_seq_infos = []
    sz_seq_info_attrs = []
    sz_key_infos = []
    sz_key_info_attrs = []
    sz_bounds = []
    # first pass calculate sizes
    for bl_obj in bl_objects:
        block_body_size = 0
        track_raw_sizes = []
        bounds_size = 0
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if getattr(custom_props, "ofs_frame", 0) != 0:
            total_headers_size += MOTION_HEADER_SIZE

            second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
            tracks = getattr(second_props["tracks"], "tracks")
            t_size = len(tracks) * TRACK_SIZE
            raw_data_size = 0
            track_bounds = []
            num_bounds = 0
            for track in tracks:
                track_data_size = len(track.raw_data)
                if track_data_size % 4:
                    track_data_size += 4 - (track_data_size % 4)  # padding
                raw_data_size += track_data_size
                track_raw_sizes.append(track_data_size)
                if track.buffer_type in BOUNDS_BUFF_TYPES:
                    track_bounds.append(BOUND_SIZE)
                    num_bounds += 1
                else:
                    track_bounds.append(0)

            sz_track_headers.append(t_size)
            sz_track_data.append(raw_data_size)
            bounds_size = num_bounds * BOUND_SIZE
            sz_bounds.append(track_bounds)

            seq_infos = getattr(second_props["sequence_infos"], "sequence_info")
            seq_infos_size = 0
            seq_info_attrs_num = 0
            seq_info_attrs_size = 0
            s_info_attr_sizes = []
            for i, s_info in enumerate(seq_infos):
                seq_infos_size += SEQ_INFO_SIZE
                seq_info_attr = getattr(s_info, "attributes")
                seq_info_attrs_num += len(seq_info_attr)
                s_info_attr_sizes.append(len(seq_info_attr) * SQ_ATTR_SIZE)
            sz_seq_infos.append(seq_infos_size)
            seq_info_attrs_size = seq_info_attrs_num * SQ_ATTR_SIZE
            sz_seq_info_attrs.append(s_info_attr_sizes)

            kf_infos = getattr(second_props["keyframe_infos"], "keyframe_info")
            kf_infos_size = 0
            kf_info_attr_num = 0
            kf_info_attr_size = 0
            kf_info_attr_sizes = []
            for i, kf_info in enumerate(kf_infos):
                kf_infos_size += KF_INFO_SIZE
                kf_info_attr = getattr(kf_info, "keyframe_blocks")
                kf_info_attr_num += len(kf_info_attr)
                kf_info_attr_sizes.append(len(kf_info_attr) * KF_ATTR_SIZE)
            sz_key_infos.append(kf_infos_size)
            sz_key_info_attrs.append(kf_info_attr_sizes)
            kf_info_attr_size = kf_info_attr_num * KF_ATTR_SIZE

            block_body_size = (t_size + bounds_size + raw_data_size + seq_infos_size + seq_info_attrs_size +
                               kf_infos_size + kf_info_attr_size)
        else:
            sz_seq_infos.append(0)
            sz_seq_info_attrs.append([])
            sz_key_infos.append(0)
            sz_key_info_attrs.append([])
            sz_track_headers.append(0)
            sz_track_data.append(0)
            sz_bounds.append(0)
        sz_tracks_raw_data.append(track_raw_sizes)
        sz_motion_body_sizes.append(block_body_size)

    # Offset for motion headers
    motion_headers_start = HEADER_SIZE + block_offsets_table_size
    block_offsets = []
    cur_offset = motion_headers_start
    for bl_obj in bl_objects:
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if getattr(custom_props, "ofs_frame", 0) != 0:
            block_offsets.append(cur_offset)
            cur_offset += MOTION_HEADER_SIZE
        else:
            block_offsets.append(0)

    # Offset for motion body
    motion_body_start = HEADER_SIZE + block_offsets_table_size + total_headers_size - 4
    track_section_offsets = []
    track_data_offsets = []
    bounds_start_offsets = []
    seq_infos_offsets = []
    seq_info_attr_offsets = []
    key_info_offsets = []
    key_info_attr_offsets = []
    # Second pass
    cur_tracks_section_offset = motion_body_start
    for i, bl_obj in enumerate(bl_objects):
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if getattr(custom_props, "ofs_frame", 0) != 0:
            # track start
            _ofs = cur_tracks_section_offset
            track_section_offsets.append(_ofs)
            # track headers
            _ofs += sz_track_headers[i]
            cur_b_offsets = []
            for b_size in sz_bounds[i]:
                if b_size != 0:
                    cur_b_offsets.append(_ofs)
                else:
                    cur_b_offsets.append(0)
                _ofs += b_size
            bounds_start_offsets.append(cur_b_offsets)
            # track data start
            # _ofs += sum(sz_bounds[i])
            cur_track_data_offsets = []
            for t in sz_tracks_raw_data[i]:
                cur_track_data_offsets.append(_ofs)
                _ofs += t
            track_data_offsets.append(cur_track_data_offsets)
            # seq infos start
            seq_infos_offsets.append(_ofs)
            # seq infos attr
            _ofs += sz_seq_infos[i]
            s_attr_ofs = []
            for s_attr_size in sz_seq_info_attrs[i]:
                s_attr_ofs.append(_ofs)
                _ofs += s_attr_size
            seq_info_attr_offsets.append(s_attr_ofs)
            # key infos
            key_info_offsets.append(_ofs)
            _ofs += sz_key_infos[i]
            # key infos attr
            k_attr_ofs = []
            for k_attr_size in sz_key_info_attrs[i]:
                k_attr_ofs.append(_ofs)
                _ofs += k_attr_size
            key_info_attr_offsets.append(k_attr_ofs)
            cur_tracks_section_offset += sz_motion_body_sizes[i]
        else:
            track_section_offsets.append(0)
            bounds_start_offsets.append([])
            track_data_offsets.append([])
            seq_infos_offsets.append(0)
            seq_info_attr_offsets.append([])
            key_info_offsets.append(0)
            key_info_attr_offsets.append([])

    final_size = (
        HEADER_SIZE +
        block_offsets_table_size +
        total_headers_size +
        sum(sz_motion_body_sizes)
    )

    return {
        "block_offsets": block_offsets,
        "track_headers_offsets": track_section_offsets,
        "bounds_offsets": bounds_start_offsets,
        "track_data_offsets": track_data_offsets,
        "seq_info_offsets": seq_infos_offsets,
        "seq_info_attr_offsets": seq_info_attr_offsets,
        "key_info_offsets": key_info_offsets,
        "key_info_attr_offsets": key_info_attr_offsets,
        "final_size": final_size
    }


def _calculate_offsets(bl_objects, app_id):
    if app_id == "re5":
        return _calculate_offsets_lmt51(bl_objects, app_id)
    else:
        return _calculate_offsets_lmt67(bl_objects, app_id)


@blender_registry.register_export_function(app_id="re5", extension="lmt")
@blender_registry.register_export_function(app_id="rev2", extension="lmt")
def export_lmt(bl_obj):
    # export_settings = bpy.context.scene.albam.export_settings
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    vfiles = []
    print(f"Exporting LMT for {bl_obj.name} with app_id {app_id}")
    bl_objects = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    dst_lmt = Lmt()
    dst_lmt.id_magic = b"LMT\x00"
    dst_lmt.version = APPID_VERSION_MAPPER[app_id]
    dst_lmt.num_block_offsets = len(bl_objects)
    block_offsets = _pre_serialize_offset(dst_lmt, len(bl_objects))
    lmt_offsets = _calculate_offsets(bl_objects, app_id)
    ofc_block = lmt_offsets["block_offsets"]
    final_size = lmt_offsets["final_size"]
    if APPID_VERSION_MAPPER[app_id] == 51:
        ofc_frames = lmt_offsets["frame_offsets"]
        ofc_ce = lmt_offsets["collision_attr_offsets"]
        ofc_mse = lmt_offsets["motion_se_attr_offsets"]
        ofc_tr_data = lmt_offsets["track_data_offsets"]
    else:
        # ofc_motion_headers = lmt_offsets["motion_headers_offsets"]
        ofc_track_headers = lmt_offsets["track_headers_offsets"]
        ofc_bounds = lmt_offsets["bounds_offsets"]
        ofc_tr_data = lmt_offsets["track_data_offsets"]
        ofc_sq_info = lmt_offsets["seq_info_offsets"]
        ofc_sq_info_attr = lmt_offsets["seq_info_attr_offsets"]
        ofc_kf_info = lmt_offsets["key_info_offsets"]
        ofc_kf_info_attr = lmt_offsets["key_info_attr_offsets"]
        #return None
    # ofc_block, ofc_frames, ofc_ce, ofc_mse, ofc_tr_data, final_size = _calculate_offsets(bl_objects, app_id)
    for i, bl_obj in enumerate(bl_objects):
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.ofs_frame != 0:
            second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
            tracks = getattr(second_props["tracks"], "tracks")
            if APPID_VERSION_MAPPER[app_id] == 51:
                col_events = second_props["col_events"]
                col_events_attr = getattr(col_events, "attributes")
                motion_se = second_props["motion_se"]
                motion_se_attr = getattr(motion_se, "attributes")
            else:
                seq_infos = getattr(second_props["sequence_infos"], "sequence_info")
                kf_infos = getattr(second_props["keyframe_infos"], "keyframe_info")

            if APPID_VERSION_MAPPER[app_id] == 51:
                anim_header = dst_lmt.BlockHeader51(
                    _parent=block_offset, _root=dst_lmt)
                custom_props.copy_custom_properties_to(anim_header)
                anim_header.ofs_frame = ofc_frames[i]
                anim_header.num_tracks = len(tracks)
                anim_header.filler = 0

                dst_col_event_attr = []
                dst_collision_events = dst_lmt.EventCollision(_parent=anim_header, _root=dst_lmt)
                dst_collision_events.event_id = col_events.event_id
                dst_collision_events.num_events = len(col_events_attr)
                dst_collision_events.ofs_events = ofc_ce[i]
                for attr in col_events_attr:
                    dst_col_attr = dst_lmt.Attr(_parent=dst_collision_events, _root=dst_lmt)
                    attr.copy_custom_properties_to(dst_col_attr)
                    dst_col_event_attr.append(dst_col_attr)
                dst_collision_events.attributes = dst_col_event_attr
                anim_header.collision_events = dst_collision_events
                dst_collision_events._check()

                dst_motion_se_attr = []
                motion_sound_effects = dst_lmt.MotionSe(_parent=anim_header, _root=dst_lmt)
                motion_sound_effects.event_id = motion_se.event_id
                motion_sound_effects.num_events = len(motion_se_attr)
                motion_sound_effects.ofs_events = ofc_mse[i]
                for attr in motion_se_attr:
                    motion_se_attr = dst_lmt.Attr(_parent=motion_sound_effects, _root=dst_lmt)
                    attr.copy_custom_properties_to(motion_se_attr)
                    dst_motion_se_attr.append(motion_se_attr)
                motion_sound_effects.attributes = dst_motion_se_attr
                motion_sound_effects._check()

                anim_header.motion_sound_effects = motion_sound_effects

                dst_tracks = []
                track_ofc = ofc_tr_data[i]
                for j, track in enumerate(tracks):
                    dst_track = dst_lmt.Track51(_parent=anim_header, _root=dst_lmt)
                    track.copy_custom_properties_to(dst_track)
                    dst_track.len_data = len(track.raw_data)
                    dst_track.ofs_data = track_ofc[j]
                    dst_track.data = track.raw_data
                    dst_tracks.append(dst_track)
                anim_header.tracks = dst_tracks
                anim_header._check()
            else:
                # Motion Header
                anim_header = dst_lmt.BlockHeader67(
                    _parent=block_offset, _root=dst_lmt)
                custom_props.copy_custom_properties_to(anim_header)
                anim_header.ofs_sequence_infos = ofc_sq_info[i]
                anim_header.ofs_keyframe_infos = ofc_kf_info[i]
                anim_header.ofs_frame = ofc_track_headers[i]
                anim_header.num_tracks = len(tracks)
                anim_header.filler = 0
                # Sequence Info
                dst_seq_infos = []
                for j, s_info in enumerate(seq_infos):
                    dst_seq_info = dst_lmt.SequenceInfo(_parent=anim_header, _root=dst_lmt)
                    # s_info.copy_custom_properties_to(dst_seq_info)
                    s_attr = getattr(s_info, "attributes")
                    dst_seq_info.work = s_info.work
                    dst_seq_info.num_seq = len(s_attr)
                    dst_seq_info.ofs_seq = ofc_sq_info_attr[i][j]
                    si_attrs = []
                    for k, s_info_attr in enumerate(s_attr):
                        dst_si_attr = dst_lmt.SeqInfoAttr(_parent=dst_seq_info, _root=dst_lmt)
                        s_info_attr.copy_custom_properties_to(dst_si_attr)
                        si_attrs.append(dst_si_attr)
                    dst_seq_info.attributes = si_attrs
                    dst_seq_info._check()
                    dst_seq_infos.append(dst_seq_info)
                # Keyframe Info
                dst_kf_infos = []
                for j, kf_info in enumerate(kf_infos):
                    dst_kf_info = dst_lmt.KeyframeInfo(_parent=anim_header, _root=dst_lmt)
                    #kf_info.copy_custom_properties_to(dst_kf_info)
                    k_blocks = getattr(kf_info, "keyframe_blocks")
                    dst_kf_info.type = kf_info.type
                    dst_kf_info.work = kf_info.work
                    dst_kf_info.attr = kf_info.attr
                    dst_kf_info.num_key = len(k_blocks)
                    dst_kf_info.ofs_seq = ofc_kf_info_attr[i][j]

                    kf_blocks = []
                    for k, kf_info_attr in enumerate(k_blocks):
                        dst_k_attr = dst_lmt.KeyframeBlock(_parent=dst_kf_info, _root=dst_lmt)
                        kf_info_attr.copy_custom_properties_to(dst_k_attr)
                        kf_blocks.append(dst_k_attr)
                    dst_kf_info.keyframe_blocks = kf_blocks
                    dst_kf_info._check()
                    dst_kf_infos.append(dst_kf_info)
                # Tracks
                dst_tracks = []
                track_ofc = ofc_tr_data[i]
                for j, track in enumerate(tracks):
                    dst_track = dst_lmt.Track67(_parent=anim_header, _root=dst_lmt)
                    track.copy_custom_properties_to(dst_track)
                    track.bounds = None
                    if dst_track.buffer_type in BOUNDS_BUFF_TYPES:
                        # TODO move into calc offsets
                        #dst_track.ofs_bounds = ofc_bounds[i][j]
                        dst_track.ofs_bounds = ofc_bounds[i][j]
                        bound = getattr(track, "track_bounds")[0]
                        dst_bound = dst_lmt.FloatBuffer(_parent=dst_track, _root=dst_lmt)
                        bound.copy_custom_properties_to(dst_bound)
                        dst_bound._check()
                        dst_track.bounds = dst_bound
                    else:
                        dst_track.ofs_bounds = 0
                    dst_track.len_data = len(track.raw_data)
                    dst_track.ofs_data = track_ofc[j]
                    dst_track.data = track.raw_data
                    dst_track._check()
                    dst_tracks.append(dst_track)
                anim_header.tracks = dst_tracks
                anim_header.sequence_infos = dst_seq_infos
                anim_header.key_infos = dst_kf_infos
                anim_header._check()

            block_offset.block_header = anim_header
        block_offset.offset = ofc_block[i]
        block_offsets.append(block_offset)

    dst_lmt.block_offsets = block_offsets

    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_lmt._check()
    dst_lmt._write(stream)

    lmt_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
    vfiles.append(lmt_vf)
    return vfiles


@blender_registry.register_blender_type
class CustomPropsBase(bpy.types.PropertyGroup):
    """
    Base class for custom properties that provides methods
    for copying attributes
    """
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except AttributeError:
                pass


@blender_registry.register_custom_properties_animation("lmt_51_anim", ("re5",))
@blender_registry.register_blender_prop
class LMT51AnimationCustomProperties(CustomPropsBase):
    ofs_frame: bpy.props.IntProperty(name="Offset", default=0, options=set())
    num_tracks: bpy.props.IntProperty(name="Number of Tracks", default=0, options=set())
    num_frames: bpy.props.IntProperty(name="Number of Frames", default=0, options=set())
    loop_frame: bpy.props.IntProperty(name="Loop Frame", default=0, options=set())
    init_position: bpy.props.FloatVectorProperty(
        name="Initial Position", size=3, default=(0.0, 0.0, 0.0), options=set())
    init_quaterion: bpy.props.FloatVectorProperty(
        name="Initial Quaternion", size=4, default=(1.0, 0.0, 0.0, 0.0), options=set())
    action: bpy.props.PointerProperty(
        name="Stored Action",
        type=bpy.types.Action
    )


@blender_registry.register_custom_properties_animation("lmt_67_anim", ("re0", "re1", "re6", "rev1", "rev2", "dd",))
@blender_registry.register_blender_prop
class LMT67AnimationCustomProperties(CustomPropsBase):
    ofs_frame: bpy.props.IntProperty(name="Offset", default=0, options=set())
    num_tracks: bpy.props.IntProperty(name="Number of Tracks", default=0, options=set())
    num_frames: bpy.props.IntProperty(name="Number of Frames", default=0, options=set())
    loop_frame: bpy.props.IntProperty(name="Loop Frame", default=0, options=set())
    init_position: bpy.props.FloatVectorProperty(
        name="Initial Position", size=3, default=(0.0, 0.0, 0.0), options=set())
    init_quaterion: bpy.props.FloatVectorProperty(
        name="Initial Quaternion", size=4, default=(1.0, 0.0, 0.0, 0.0), options=set())
    attr: bpy.props.IntProperty(name="Attr", default=0, options=set())
    kf_num: bpy.props.IntProperty(name="Keyframe Number", default=0, options=set())
    seq_num: bpy.props.IntProperty(name="Sequence Number", default=0, options=set())
    duplicate: bpy.props.IntProperty(name="Duplicate", default=0, options=set())
    reserved: bpy.props.IntProperty(name="Reserved", default=0, options=set())
    action: bpy.props.PointerProperty(
        name="Stored Action",
        type=bpy.types.Action
    )


@blender_registry.register_blender_prop
class LMT51Attribute(CustomPropsBase):
    group: bpy.props.IntProperty(name="Group", default=0, options=set())
    frame: bpy.props.IntProperty(name="Frame", default=0, options=set())


@blender_registry.register_custom_properties_animation(
    "col_events",
    ("re5",), is_secondary=True, display_name="Collision Events")
@blender_registry.register_blender_prop
class ColEventsCustomProperties(CustomPropsBase):
    event_id: bpy.props.IntVectorProperty(
        name="Event ID",
        size=32,
        default=[0] * 32,
        description="Collision group ID")
    attributes: bpy.props.CollectionProperty(
        type=LMT51Attribute,
        name="Attributes",
        description="Collision attributes for each group"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_custom_properties_animation(
    "motion_se",
    ("re5",), is_secondary=True, display_name="Motion Sound Events")
@blender_registry.register_blender_prop
class MotionSECustomProperties(CustomPropsBase):
    event_id: bpy.props.IntVectorProperty(
        name="Event ID",
        size=32,
        default=[0] * 32,
        description="Collision group ID")
    attributes: bpy.props.CollectionProperty(
        type=LMT51Attribute,
        name="Attributes",
        description="Collision attributes for each group"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_blender_prop
class SeqInfoAttribute(CustomPropsBase):
    unk_00: bpy.props.IntProperty(name="Unk 00", default=0, options=set())
    unk_01: bpy.props.IntProperty(name="Unk 01", default=0, options=set())
    unk_02: bpy.props.IntProperty(name="Unk 02", default=0, options=set())


@blender_registry.register_blender_prop
class SeqInfo(CustomPropsBase):
    work: bpy.props.IntVectorProperty(
        name="Work",
        size=32,
        default=[0] * 32,
    )
    attributes: bpy.props.CollectionProperty(
        type=SeqInfoAttribute,
        name="Attributes"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_custom_properties_animation(
    "sequence_infos",
    ("re0", "re1", "rev1", "rev2", "re6",), is_secondary=True, display_name="Sequence Infos")
@blender_registry.register_blender_prop
class SequenceInfoProperties(CustomPropsBase):
    sequence_info: bpy.props.CollectionProperty(
        type=SeqInfo,
        name="Sequence Info"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_blender_prop
class KeyBlock(CustomPropsBase):
    unk_00: bpy.props.IntProperty(
        name="Unk 00",
        default=0
    )
    unk_01: bpy.props.IntProperty(
        name="Unk 01",
        default=0
    )
    unk_02: bpy.props.FloatProperty(
        name="Unk 02",
        default=0
    )
    unk_03: bpy.props.FloatProperty(
        name="Unk 03",
        default=0
    )
    unk_04: bpy.props.FloatProperty(
        name="Unk 04",
        default=0
    )


@blender_registry.register_blender_prop
class KeyInfo(CustomPropsBase):
    type: bpy.props.IntProperty(
        name="Type", default=0, options=set())
    work: bpy.props.IntProperty(
        name="Work", default=0, options=set())
    attr: bpy.props.IntProperty(
        name="Attr", default=0, options=set())
    keyframe_blocks: bpy.props.CollectionProperty(
        type=KeyBlock
    )


@blender_registry.register_custom_properties_animation(
    "keyframe_infos",
    ("re0", "re1", "rev1", "rev2", "re6",), is_secondary=True, display_name="Keyframe Infos")
@blender_registry.register_blender_prop
class KeyframeInfoProperties(CustomPropsBase):
    keyframe_info: bpy.props.CollectionProperty(
        type=KeyInfo,
        name="Keyframe Info"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_blender_prop
class LMT51Track(CustomPropsBase):
    buffer_type: bpy.props.IntProperty(
        name="Buffer Type",
        default=0,
        options=set(),
        description="Type of buffer used for this track")
    usage: bpy.props.IntProperty(
        name="Usage",
        default=0,
        options=set(),
        description="Track type")
    joint_type: bpy.props.IntProperty(
        name="Joint Type",
        default=0,
        options=set())
    bone_index: bpy.props.IntProperty(
        name="Bone Index",
        default=0,
        options=set(),
        description="Animation index of the bone in the armature")
    weight: bpy.props.FloatProperty(
        name="Weight",
        default=1.0,
        options=set(),
        description="Weight of the track, used for blending")
    reference_data: bpy.props.FloatVectorProperty(
        name="Reference Data",
        size=4,
        default=(0.0, 0.0, 0.0, 1.0),
        options=set(),
        description="Reference data for the track, used for blending"
    )
    raw_data: bpy.props.StringProperty(
        name="Raw Data",
        description="Raw binary data for this track",
        subtype='BYTE_STRING'
    )


@blender_registry.register_blender_prop
class FrameBounds(CustomPropsBase):
    addin: bpy.props.FloatVectorProperty(
        name="AddIn",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        options=set(),
    )
    offset: bpy.props.FloatVectorProperty(
        name="Offset",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        options=set(),
    )


@blender_registry.register_blender_prop
class LMT67Track(CustomPropsBase):
    buffer_type: bpy.props.IntProperty(
        name="Buffer Type",
        default=0,
        options=set(),
        description="Type of buffer used for this track")
    usage: bpy.props.IntProperty(
        name="Usage",
        default=0,
        options=set(),
        description="Track type")
    joint_type: bpy.props.IntProperty(
        name="Joint Type",
        default=0,
        options=set())
    bone_index: bpy.props.IntProperty(
        name="Bone Index",
        default=0,
        options=set(),
        description="Animation index of the bone in the armature")
    weight: bpy.props.FloatProperty(
        name="Weight",
        default=1.0,
        options=set(),
        description="Weight of the track, used for blending")
    reference_data: bpy.props.FloatVectorProperty(
        name="Reference Data",
        size=4,
        default=(0.0, 0.0, 0.0, 1.0),
        options=set(),
        description="Reference data for the track, used for blending"
    )
    raw_data: bpy.props.StringProperty(
        name="Raw Data",
        description="Raw binary data for this track",
        subtype='BYTE_STRING'
    )
    track_bounds: bpy.props.CollectionProperty(
        type=FrameBounds,
        name="Frame Bounds",
    )


@blender_registry.register_custom_properties_animation(
    "tracks",
    ("re5",), is_secondary=True, display_name="Animation Tracks")
@blender_registry.register_blender_prop
class AnimTrackCustomProperties(CustomPropsBase):
    tracks: bpy.props.CollectionProperty(
        type=LMT51Track,
        name="Tracks",
        description="Animation tracks for the LMT file"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_custom_properties_animation(
    "tracks",
    ("re0", "re1", "rev1", "rev2", "re6",), is_secondary=True, display_name="Animation Tracks")
@blender_registry.register_blender_prop
class AnimTrack67CustomProperties(CustomPropsBase):
    tracks: bpy.props.CollectionProperty(
        type=LMT67Track,
        name="Tracks",
        description="Animation tracks for the LMT file"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",
        description="Allows to select an item from the collection",
        default=0
    )
