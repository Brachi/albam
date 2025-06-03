from ctypes import Structure, c_ulonglong
import io
import struct
from io import BytesIO
from albam.vfs import VirtualFileData

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix

from albam.registry import blender_registry
from .structs.lmt import Lmt


HACKY_BONE_INDEX_IK_FOOT_RIGHT = 19
HACKY_BONE_INDEX_IK_FOOT_LEFT = 23
HACKY_BONE_INDICES_IK_FOOT = {HACKY_BONE_INDEX_IK_FOOT_RIGHT, HACKY_BONE_INDEX_IK_FOOT_LEFT}
ROOT_UNK_BONE_ID = 254
ROOT_MOTION_BONE_ID = 255
ROOT_MOTION_BONE_NAME = 'root_motion'
ROOT_BONE_NAME = '0'


@blender_registry.register_import_function(app_id="re5", extension='lmt', file_category="ANIMATION")
def load_lmt(file_list_item, context):
    app_id = file_list_item.app_id
    lmt_bytes = file_list_item.get_bytes()
    lmt = Lmt(KaitaiStream(io.BytesIO(lmt_bytes)))
    lmt._read()
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

        custom_properties = anim_object.albam_custom_properties.get_custom_properties_for_appid(
            app_id)
        custom_properties.copy_custom_properties_from(block.block_header)
        custom_properties.action = action

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


# LMTVec3Frame T_VECTOR3_CONST = 0x2,
def decode_type_2(data):
    decoded_frames = []
    CHUNK_SIZE = 12

    for start in range(0, len(data), CHUNK_SIZE):
        chunk = data[start: start + CHUNK_SIZE]
        u = struct.unpack("fff", chunk)
        floats = (u[0] / 100, u[1] / 100, u[2] / 100)
        decoded_frames.append(floats)
    return decoded_frames


# LMTQuatFramev14 T_POLAR3KEY = 0x6,
def decode_type_6(data):
    decoded_frames = []

    for idx, start in enumerate(range(0, len(data), 8)):
        chunk = data[start: start + 8]
        frame = FrameQuat4_14()
        io.BytesIO(chunk).readinto(frame)

        decoded_frames.append((frame.w, frame.x, frame.y, frame.z))
        decoded_frames.extend([None] * (frame.duration - 1))

    return decoded_frames


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


def _pre_serialize_offset(dst_lmt, num_anim_blocks):
    block_offsets = []
    for i in range(num_anim_blocks):
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        block_offset.offset = 0
    return block_offsets


def _calculate_offsets(bl_objects, app_id):
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

            # Offset для кожного raw_data в треках
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
    return (
        block_offsets,
        frame_offsets,
        collision_attr_offsets,
        motion_se_attr_offsets,
        track_data_offsets,
        final_size
    )


@blender_registry.register_export_function(app_id="re5", extension="lmt")
def export_lmt(bl_obj):
    # export_settings = bpy.context.scene.albam.export_settings
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    vfiles = []
    print(f"Exporting LMT for {bl_obj.name} with app_id {app_id}")
    bl_objects = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    dst_lmt = Lmt()
    dst_lmt.id_magic = b"LMT\x00"
    dst_lmt.version = 51
    dst_lmt.num_block_offsets = len(bl_objects)
    block_offsets = _pre_serialize_offset(dst_lmt, len(bl_objects))

    ofc_block, ofc_frames, ofc_ce, ofc_mse, ofc_tr_data, final_size = _calculate_offsets(bl_objects, app_id)
    for i, bl_obj in enumerate(bl_objects):
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.ofs_frame != 0:
            second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
            col_events = second_props["col_events"]
            col_events_attr = getattr(col_events, "attributes")
            motion_se = second_props["motion_se"]
            motion_se_attr = getattr(motion_se, "attributes")
            tracks = getattr(second_props["tracks"], "tracks")

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
