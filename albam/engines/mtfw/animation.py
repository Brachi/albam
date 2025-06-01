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

        tracks = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)["tracks"]
        for track_index, track in enumerate(block.block_header.tracks):
            # Custom attributes for a track
            item = tracks.tracks.add()
            item.buffer_type = track.buffer_type
            item.usage = track.usage
            item.joint_type = track.joint_type
            item.bone_index = track.bone_index
            item.weight = track.weight
            item.reference_data = track.reference_data
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

        col_events = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)["col_events"]
        motion_se = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)["motion_se"]
        # col_events.group_id[1] = 225
        for attr_index, attribute in enumerate(block.block_header.collision_events.attributes):
            item = col_events.attributes.add()
            item.group = attribute.group
            item.frame = attribute.frame
        for i, event_id in enumerate(block.block_header.collision_events.event_id):
            col_events.event_id[i] = event_id

        for attr_index, attribute in enumerate(block.block_header.motion_sound_effects.attributes):
            item = motion_se.attributes.add()
            item.group = attribute.group
            item.frame = attribute.frame
        for i, event_id in enumerate(block.block_header.motion_sound_effects.event_id):
            motion_se.event_id[i] = event_id

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


def _pre_serialize_offset(dst_lmt, num_anim_blocks):
    block_offsets = []
    for i in range(num_anim_blocks):
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        block_offset.offset = 0
    return block_offsets


def _serialize_motion_headers(dst_lmt, app_id, block_offsets, bl_objects):
    motion_headers = []
    for i, bl_obj in enumerate(bl_objects):
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)

        if custom_props.ofs_frame != 0:
            anim_header = dst_lmt.BlockHeader51(
                _parent=block_offset, _root=dst_lmt)
            anim_header.tracks__to_write = False
            anim_header.ofs_frame = 0
            anim_header.num_tracks = 0
            anim_header.num_frames = custom_props.num_frames
            anim_header.loop_frame = custom_props.loop_frame
            anim_header.init_position = custom_props.init_position
            anim_header.filler = 0
            anim_header.init_quaterion = custom_props.init_quaterion

            second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)

            col_events = second_props["col_events"]
            col_attributes = []
            dst_collision_events = dst_lmt.EventCollision(_parent=anim_header, _root=dst_lmt)
            dst_collision_events.attributes__to_write = False
            dst_collision_events.event_id = col_events.event_id
            col_events_attr = getattr(col_events, "attributes")
            dst_collision_events.num_events = len(col_events_attr)
            dst_collision_events.ofs_events = 0

            for attr in col_events_attr:
                dst_col_attr = dst_lmt.Attr(_parent=dst_collision_events, _root=dst_lmt)
                dst_col_attr.group = attr.group
                dst_col_attr.frame = attr.frame
                col_attributes.append(dst_col_attr)

            motion_se = second_props["motion_se"]
            motion_se_attributes = []
            dst_motion_sound_effects = dst_lmt.MotionSe(_parent=anim_header, _root=dst_lmt)
            motion_se_attr = getattr(motion_se, "attributes")
            for attr in motion_se_attr:
                dst_mot_attr = dst_lmt.Attr(_parent=dst_motion_sound_effects, _root=dst_lmt)
                dst_mot_attr.group = attr.group
                dst_mot_attr.frame = attr.frame
                motion_se_attributes.append(dst_mot_attr)

            tracks = getattr(second_props["tracks"], "tracks")
            tracks_headers = []
            tracks_data = []
            for track in tracks:
                dst_track = dst_lmt.Track51(_parent=anim_header, _root=dst_lmt)
                dst_track.buffer_type = track.buffer_type
                dst_track.usage = track.usage
                dst_track.joint_type = track.joint_type
                dst_track.bone_index = track.bone_index
                dst_track.weight = track.weight
                dst_track.len_data = len(track.raw_data)
                dst_track.ofs_data = 0
                tracks_headers.append(dst_track)
                tracks_data.append(track.raw_data)
    return motion_headers


def _calculate_offsets(bl_objects, app_id):
    HEADER_SIZE = 8
    BLOCK_OFFSET_SIZE = 4
    MOTION_HEADER_SIZE = 192
    ATTR_SIZE = 8
    TRACK_SIZE = 32
    block_offsets_table_size = len(bl_objects) * BLOCK_OFFSET_SIZE

    m_headers_size = 0
    motion_body_size = 0
    ofc_motion_body = []
    ofc_block_offsets = []
    ce_attr_size = []
    mse_attr_size = []
    tr_size = []
    rw_size = []
    ttraw_data = []

    cur_ofc_bloc_offsets = HEADER_SIZE + block_offsets_table_size
    for i, bl_obj in enumerate(bl_objects):
        ofc_ = 0
        traw_data = []
        motion_body_size = 0
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.ofs_frame != 0:
            ofc_ = cur_ofc_bloc_offsets
            cur_ofc_bloc_offsets += MOTION_HEADER_SIZE
            m_headers_size += MOTION_HEADER_SIZE

            second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
            tracks = getattr(second_props["tracks"], "tracks")
            t_size = len(tracks) * TRACK_SIZE

            raw_data_size = 0
            t_size = 0
            for track in tracks:
                raw_data_size += len(track.raw_data)
                traw_data.append(len(track.raw_data))
                t_size += TRACK_SIZE
            tr_size.append(t_size)
            rw_size.append(raw_data_size)

            col_events_attr = getattr(second_props["col_events"], "attributes")
            col_events_attr_size = len(col_events_attr) * ATTR_SIZE
            ce_attr_size.append(col_events_attr_size)
            motion_se_attr = getattr(second_props["motion_se"], "attributes")
            motion_se_attr_size = len(motion_se_attr) * ATTR_SIZE
            mse_attr_size.append(motion_se_attr_size)
            # frame_data_size = track_size + col_events_attr_size + motion_se_attr_size + raw_data_size
            motion_body_size = t_size + col_events_attr_size + motion_se_attr_size + raw_data_size
        else:
            ce_attr_size.append(0)
            mse_attr_size.append(0)
            tr_size.append(0)
            rw_size.append(0)
        ttraw_data.append(traw_data)
        ofc_block_offsets.append(ofc_)
        ofc_motion_body.append(motion_body_size)

    motion_body_start = HEADER_SIZE + block_offsets_table_size + m_headers_size
    cur_frame_offset = motion_body_start
    ofc_frames = []
    ofc_ce_attr = []
    ofc_mse_attr = []
    ofc_data_data = []
    for i, bl_obj in enumerate(bl_objects):
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.ofs_frame != 0:
            ofc_frames.append(cur_frame_offset)
            ofc_ce_attr.append(cur_frame_offset + tr_size[i] + rw_size[i])
            ofc_mse_attr.append(cur_frame_offset + tr_size[i] + rw_size[i] + ce_attr_size[i])
            ofc_data = []
            temp_size = 0
            for t in ttraw_data[i]:
                val = cur_frame_offset + tr_size[i] + temp_size
                ofc_data.append(val)
                temp_size += t
            ofc_data_data.append(ofc_data)
            cur_frame_offset += ofc_motion_body[i]
        else:
            ofc_frames.append(0)
            ofc_ce_attr.append(0)
            ofc_mse_attr.append(0)
            ofc_data_data.append([])

    return ofc_block_offsets, ofc_frames, ofc_ce_attr, ofc_mse_attr, ofc_data_data


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
    block_headers = []
    ofs = 8 + len(bl_objects) * 4

    test_serialization = _serialize_motion_headers(dst_lmt, app_id, block_offsets, bl_objects)
    ofc_block, ofc_frames, ofc_ce, ofc_mse, ofc_tr_data = _calculate_offsets(bl_objects, app_id)
    for bl_obj in bl_objects:
        block_offset = dst_lmt.BlockOffset(_parent=dst_lmt, _root=dst_lmt)
        # block_offset.block_header__to_write = False
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        body_size = 0
        if custom_props.ofs_frame != 0:
            anim_header = dst_lmt.BlockHeader51(
                _parent=block_offset, _root=dst_lmt)
            anim_header.tracks__to_write = False
            anim_header.ofs_frame = 0
            anim_header.num_tracks = 0
            anim_header.num_frames = custom_props.num_frames
            anim_header.loop_frame = custom_props.loop_frame
            anim_header.init_position = custom_props.init_position
            anim_header.filler = 0
            anim_header.init_quaterion = custom_props.init_quaterion
            body_size += 56

            collision_events = dst_lmt.EventCollision(_parent=anim_header, _root=dst_lmt)
            collision_events.event_id = [0] * 32
            collision_events.num_events = 0
            collision_events.ofs_events = 0
            collision_events.attributes__to_write = False

            """
            col_attributes = []
            col_attr = dst_lmt.Attr(_parent=collision_events, _root=dst_lmt)
            col_attr.group = 0
            col_attr.frame = 0
            col_attributes.append(col_attr)
            """

            anim_header.collision_events = collision_events
            body_size += 72

            motion_sound_effects = dst_lmt.MotionSe(_parent=anim_header, _root=dst_lmt)
            motion_sound_effects.event_id = [0] * 32
            motion_sound_effects.num_events = 0
            motion_sound_effects.ofs_events = 0
            motion_sound_effects.attributes__to_write = False
            anim_header.motion_sound_effects = motion_sound_effects
            body_size += 72

            anim_header._check()
            #block_offset.block_header = anim_header
            block_headers.append(anim_header)
            # block_offset.offset = ofs
        block_offset.offset = 0
        ofs += (4 + body_size)

        # block_offset.check()
        block_offsets.append(block_offset)

    dst_lmt.block_offsets = block_offsets
    final_size = ofs

    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_lmt._check()
    dst_lmt._write(stream)

    lmt_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
    vfiles.append(lmt_vf)
    return vfiles


@blender_registry.register_blender_type
class BaseCustomProps(bpy.types.PropertyGroup):
    """
    Base class for custom properties that are used in animations.
    This is used to ensure that the custom properties are registered
    and can be accessed from the animation data.
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
class LMT51AnimationCustomProperties(BaseCustomProps):
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
class LMT51Attribute(bpy.types.PropertyGroup):
    group: bpy.props.IntProperty(name="Group", default=0, options=set())
    frame: bpy.props.IntProperty(name="Frame", default=0, options=set())


@blender_registry.register_custom_properties_animation(
    "col_events",
    ("re5",), is_secondary=True, display_name="Collision Events")
@blender_registry.register_blender_prop
class ColEventsCustomProperties(bpy.types.PropertyGroup):
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
    attributes_index: bpy.props.IntProperty(default=0)


@blender_registry.register_custom_properties_animation(
    "motion_se",
    ("re5",), is_secondary=True, display_name="Motion Sound Events")
@blender_registry.register_blender_prop
class MotionSECustomProperties(bpy.types.PropertyGroup):
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
    attributes_index: bpy.props.IntProperty(default=0)


@blender_registry.register_blender_prop
class LMT51Track(bpy.types.PropertyGroup):
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
class AnimTrackCustomProperties(bpy.types.PropertyGroup):
    tracks: bpy.props.CollectionProperty(
        type=LMT51Track,
        name="Tracks",
        description="Animation tracks for the LMT file"
    )
    tracks_index: bpy.props.IntProperty(default=0)
