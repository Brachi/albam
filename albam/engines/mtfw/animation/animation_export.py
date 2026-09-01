"""Writing a .lmt back out.

Turning actions into tracks, then laying the whole file out - every offset in
an .lmt header is absolute, so the sizes have to be known before a single byte
is written, which is what the two _calculate_offsets passes are for.
"""
import ast
from io import BytesIO

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Quaternion, Vector

from ....registry import blender_registry
from ....vfs import VirtualFileData
from ..structs.lmt import Lmt
from .animation_import import BLOCK_INDEX_PROP, CHAIN_TARGET_PROP, _create_bone_mapping
from .keyframes import (
    APPID_VERSION_MAPPER,
    ActionKey,
    BONE_TRACK_TYPES,
    BOUNDS_BUFF_TYPES,
    LMTKeyFrames,
    USAGE,
)


def _local_space_to_parent_translation(frame, bone):
    anim_bone_id = bone.get("mtfw.anim_retarget", "").split("_")[0]

    if bone.parent is None:
        if anim_bone_id in ("0", "255") or anim_bone_id.startswith("254"):
            rest = bone.matrix_local.to_translation()
            lmt_rest = Vector((rest.x, rest.z, -rest.y))
            return frame + lmt_rest

    # A chain's goal was imported without a parent-space conversion, so it must
    # leave the same way. The bare ids are the fallback for rigs built before
    # the control bones were marked.
    if bone.get(CHAIN_TARGET_PROP) or anim_bone_id in ("19", "23"):
        rest = bone.matrix_local.to_translation()
        return frame + Vector((rest.x, rest.z, -rest.y))

    global_pos = bone.matrix_local @ frame
    if bone.parent is not None:
        return bone.parent.matrix_local.inverted() @ global_pos
    return global_pos


def _select_kf_usage(bone, track_type):
    is_mroot = bone.get('mtfw.anim_retarget', "-1") == "255"
    match track_type:
        case "rotation_quaternion":
            return 3 if is_mroot else 0
        case "location":
            return 4 if is_mroot else 1
        case "scale":
            return 5 if is_mroot else 2
        case _:
            raise ValueError(f"Track type {track_type} isn't correct")


def _block_length(action, fcurves, custom_props):
    """How many frames the block runs for.

    An action whose tracks never change carries a single keyframe, because one
    keyframe is all a constant needs - so its frame range reads 1 no matter how
    long the block actually runs. Blocks like that are ordinary: a static idle
    the engine holds for a couple of seconds. Taking the range there would
    write a 60 frame hold out as a single frame, leaving the pose right and the
    timing destroyed, so the length the block already declares is kept instead.

    An action with real keyframes is the authority on its own length, including
    when the intent is to shorten the block.
    """
    frames = {keyframe.co[0] for fcurve in fcurves for keyframe in fcurve.keyframe_points}
    if len(frames) > 1:
        return int(action.frame_range[1])
    return int(custom_props.num_frames) or int(action.frame_range[1])


def _serialize_lmt_track(armature, tracks, mapping, app_id):
    keyframes = LMTKeyFrames()
    keyframes.version = APPID_VERSION_MAPPER[app_id]
    for bone_name, bone_tracks in tracks.items():
        location = {}
        rotation_quaternion = {}
        scale = {}
        bone = armature.data.bones.get(bone_name)
        bone_index = mapping.get(bone_name)
        for frame, action_key in bone_tracks.items():
            if action_key.location is not None:
                kf = action_key.location
                kf = _local_space_to_parent_translation(kf, bone)
                location[frame] = kf
            if action_key.rotation_quaternion is not None:
                rotation_quaternion[frame] = action_key.rotation_quaternion
            if action_key.scale is not None:
                scale[frame] = action_key.scale
        if rotation_quaternion:
            keyframes.track_type = "rotation_quaternion"
            rotation_sorted = {k: rotation_quaternion[k] for k in sorted(rotation_quaternion)}
            usage = _select_kf_usage(bone, "rotation_quaternion")
            if len(rotation_sorted) == 1 and keyframes.version != 51:
                # see encode_framedata(static=True): v67's single-frame quat
                # type id is taken by an unrelated vec3 format
                keyframes.encode_framedata(2, bone_index, rotation_sorted, usage, static=True)
            else:
                kf_type = 4 if len(rotation_sorted) == 1 else 6
                keyframes.encode_framedata(kf_type, bone_index, rotation_sorted, usage)
        if location:
            keyframes.track_type = "location"
            location_sorted = {k: location[k] for k in sorted(location)}
            usage = _select_kf_usage(bone, "location")
            kf_type = 2 if len(location_sorted) == 1 else 9
            keyframes.encode_framedata(kf_type, bone_index, location_sorted, usage)
        if scale:
            keyframes.track_type = "scale"
            scale_sorted = {k: scale[k] for k in sorted(scale)}
            kf_type = 2 if len(scale_sorted) == 1 else 9
            usage = _select_kf_usage(bone, "scale")
            keyframes.encode_framedata(kf_type, bone_index, scale_sorted, usage)
    return keyframes.encoded_frames


def _update_track_data(bl_obj, encoded_tracks, num_frames, joint_types, rd_stored, app_id):
    custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_props.num_frames = num_frames
    second_props = bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
    tracks_collection = getattr(second_props["tracks"], "tracks")
    tracks_collection.clear()
    for et in encoded_tracks:
        item = tracks_collection.add()
        item.buffer_type = et.buffer_type
        item.usage = et.usage
        item.bone_index = int(et.bone_index.split("_")[0])  # workaround for 254_ values
        item.joint_type = joint_types.get((USAGE[item.usage], str(et.bone_index)), 0)
        item.weight = 1.0
        ref_data = et.reference_data
        ref_data_stored = rd_stored.get((USAGE[item.usage], str(et.bone_index)), None)
        if ref_data_stored:  # and ref_data_stored != "[]":
            ref_data = ast.literal_eval(ref_data_stored)
        item.reference_data = ref_data
        item.raw_data = et.data


def _get_action_fcurves(action, armature):
    """Every fcurve `action` holds, whichever container it keeps them in.

    Blender 4.4 moved fcurves into one channelbag per slot and 5.0 removed
    the flat Action.fcurves shortcut. Slots are ordered by creation, so the
    armature's channelbag is not necessarily the first, and an action that
    has never been keyed has no layers at all - hence walking them all
    rather than indexing. Callers filter by data_path anyway, so channels
    belonging to another slot are ignored rather than mistaken for bones.
    """
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    return [
        fcurve
        for layer in action.layers
        for strip in layer.strips
        for channelbag in strip.channelbags
        for fcurve in channelbag.fcurves
    ]


def _generate_track_from_action(armature, bl_objects, app_id):
    mapping = _create_bone_mapping(armature)
    mapping = {value: key for key, value in mapping.items()}
    for bl_obj in bl_objects:
        tracks = {}  # bone_name -> frame -> ActionKey
        joint_types = {}
        reference_data = {}
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.generate_new and custom_props.action:
            action = custom_props.action
            fcurves = _get_action_fcurves(action, armature)
            num_frames = _block_length(action, fcurves, custom_props)
            for fcurve in fcurves:
                path = fcurve.data_path
                index = fcurve.array_index
                if path.startswith('pose.bones["'):
                    bone_name = path.split('"')[1]
                    if mapping.get(bone_name, None) is None:
                        continue
                    track_type = path.split(".")[-1]
                    if track_type not in BONE_TRACK_TYPES:
                        # an action also carries channels that are not a bone's
                        # transform - a chain constraint's influence, say - and
                        # none of them is a track
                        continue
                    joint_type = action.get(f"{track_type}_{mapping.get(bone_name)}", 0)
                    joint_types[(track_type, mapping.get(bone_name))] = joint_type

                    # A chain's control bone is retargeted "<id>_1", but its
                    # reference data was stored under the plain id the track
                    # came from, so ask for it under that.
                    rd_bone_id = mapping.get(bone_name)
                    if armature.data.bones[bone_name].get(CHAIN_TARGET_PROP):
                        rd_bone_id = rd_bone_id.split("_")[0]
                    elif bone_name == "IK_Foot.L":
                        rd_bone_id = "23"
                    elif bone_name == "IK_Foot.R":
                        rd_bone_id = "19"
                    ref_data = action.get(f"rd_{track_type}_{rd_bone_id}", None)
                    if ref_data:
                        reference_data[(track_type, rd_bone_id)] = ref_data
                    if tracks.get(bone_name) is None:
                        tracks[bone_name] = {}
                    for keyframe in fcurve.keyframe_points:
                        frame = keyframe.co[0]
                        if tracks[bone_name].get(frame) is None:
                            tracks[bone_name][frame] = ActionKey()
                        value = keyframe.co[1]
                        if "location" in path:
                            if getattr(tracks[bone_name][frame], "location", None) is None:
                                tracks[bone_name][frame].location = Vector((0.0, 0.0, 0.0))
                            tracks[bone_name][frame].location[index] = value
                        elif "scale" in path:
                            if getattr(tracks[bone_name][frame], "scale", None) is None:
                                tracks[bone_name][frame].scale = Vector((1.0, 1.0, 1.0))
                            tracks[bone_name][frame].scale[index] = value
                        elif "rotation_quaternion" in path:
                            if getattr(tracks[bone_name][frame], "rotation_quaternion", None) is None:
                                tracks[bone_name][frame].rotation_quaternion = Quaternion(
                                    (1.0, 0.0, 0.0, 0.0))
                            tracks[bone_name][frame].rotation_quaternion[index] = value
            track_attrs = _serialize_lmt_track(armature, tracks, mapping, app_id)
            _update_track_data(bl_obj, track_attrs, num_frames, joint_types, reference_data, app_id)


def _align(value, alignment):
    return (value + alignment - 1) & ~(alignment - 1)


def _calculate_offsets_lmt51(bl_objects, app_id):
    HEADER_SIZE = 8
    BLOCK_OFFSET_SIZE = 4
    MOTION_HEADER_SIZE = 192
    ATTR_SIZE = 8
    TRACK_SIZE = 32
    # The engine pads to this before each block header. Every header is 192
    # bytes, a multiple of it, so only the first one moves - the rest inherit
    # the alignment. The bytes skipped are already zero in the output buffer.
    BLOCK_HEADER_ALIGNMENT = 16

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

    headers_start = _align(HEADER_SIZE + block_offsets_table_size, BLOCK_HEADER_ALIGNMENT)
    cur_ofc_bloc_offsets = headers_start
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

    motion_body_start = headers_start + total_headers_size
    cur_frame_offset = motion_body_start

    for i in range(num_blocks):
        if motion_body_sizes[i] > 0:
            frame_offsets.append(cur_frame_offset)
            collision_attr_offsets.append(cur_frame_offset + tracks_headers_sizes[i] + tracks_data_sizes[i])
            motion_se_attr_offsets.append(cur_frame_offset + tracks_headers_sizes[i] + tracks_data_sizes[i] +
                                          collision_attr_sizes[i])

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

    final_size = headers_start + total_headers_size + sum(motion_body_sizes)
    return {
        "block_offsets": block_offsets,
        "frame_offsets": frame_offsets,
        "collision_attr_offsets": collision_attr_offsets,
        "motion_se_attr_offsets": motion_se_attr_offsets,
        "track_data_offsets": track_data_offsets,
        "final_size": final_size
    }


def _calculate_offsets_lmt67(bl_objects, app_id):
    """Where every part of a version 67 .lmt lands.

    Unreachable while .lmt registration is re5 only (see load_lmt and
    export_lmt). Kept because the parser still reads version 67 and the
    tests still parse it - only importing and exporting it are parked.
    """
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
        # only re5 can reach export_lmt, so this arm never runs today
        return _calculate_offsets_lmt67(bl_objects, app_id)


def _lmt_blocks(bl_obj):
    """This .lmt's blocks, in the order the file stores them.

    A block's position is what gives it its identity - an empty slot has to
    stay empty, and every offset in the header is written by position - but
    Blender's children are not kept in the order they were created, and the
    names that used to stand in for the index get renumbered as soon as the
    same .lmt is imported twice in one session. Sorting on the index recorded
    at import is the only thing that survives that. Objects from before it was
    recorded all sort equal, which a stable sort leaves exactly as it found
    them.
    """
    blocks = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    return sorted(blocks, key=lambda block: block.get(BLOCK_INDEX_PROP, 0))


# re5 only, deliberately. Writing a .lmt was built and measured against
# version 51, and nothing here has ever been checked against a version 67 game:
# 67 does not use the joint_type field at all, puts position channels where 51
# never does, and lays its blocks out differently. Offering an export that has
# never round-tripped is worse than offering none, since what it produces is a
# file the game will load.
@blender_registry.register_export_function(app_id="re5", extension="lmt")
def export_lmt(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    vfiles = []
    print(f"Exporting LMT for {bl_obj.name} with app_id {app_id}")
    bl_objects = _lmt_blocks(bl_obj)
    armature = bpy.context.scene.albam.import_options_lmt.armature
    dst_lmt = Lmt()
    dst_lmt.id_magic = b"LMT\x00"
    dst_lmt.version = APPID_VERSION_MAPPER[app_id]
    dst_lmt.num_block_offsets = len(bl_objects)
    block_offsets = []
    _generate_track_from_action(armature, bl_objects, app_id)
    lmt_offsets = _calculate_offsets(bl_objects, app_id)
    ofc_block = lmt_offsets["block_offsets"]
    final_size = lmt_offsets["final_size"]
    if APPID_VERSION_MAPPER[app_id] == 51:
        ofc_frames = lmt_offsets["frame_offsets"]
        ofc_ce = lmt_offsets["collision_attr_offsets"]
        ofc_mse = lmt_offsets["motion_se_attr_offsets"]
        ofc_tr_data = lmt_offsets["track_data_offsets"]
    else:
        ofc_track_headers = lmt_offsets["track_headers_offsets"]
        ofc_bounds = lmt_offsets["bounds_offsets"]
        ofc_tr_data = lmt_offsets["track_data_offsets"]
        ofc_sq_info = lmt_offsets["seq_info_offsets"]
        ofc_sq_info_attr = lmt_offsets["seq_info_attr_offsets"]
        ofc_kf_info = lmt_offsets["key_info_offsets"]
        ofc_kf_info_attr = lmt_offsets["key_info_attr_offsets"]
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
                    dst_col_attr._check()
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
                    motion_se_attr._check()
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
                    dst_track._check()
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
                        dst_si_attr._check()
                        si_attrs.append(dst_si_attr)
                    dst_seq_info.attributes = si_attrs
                    dst_seq_info._check()
                    dst_seq_infos.append(dst_seq_info)
                # Keyframe Info
                dst_kf_infos = []
                for j, kf_info in enumerate(kf_infos):
                    dst_kf_info = dst_lmt.KeyframeInfo(_parent=anim_header, _root=dst_lmt)
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
                        dst_k_attr._check()
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
        block_offset._check()
        block_offsets.append(block_offset)

    dst_lmt.block_offsets = block_offsets

    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_lmt._check()
    dst_lmt._write(stream)

    lmt_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
    vfiles.append(lmt_vf)
    return vfiles
