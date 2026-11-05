"""Writing a .lmt back out.

Turning actions into tracks, then laying the whole file out - every offset in
an .lmt header is absolute, so the sizes have to be known before a single byte
is written, which is what the two _calculate_offsets passes are for.
"""
from collections import Counter
from io import BytesIO

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Quaternion, Vector

from ....exceptions import AlbamCheckFailure
from ....registry import blender_registry
from ....vfs import VirtualFileData
from ..bone import get_anim_retarget, get_chain_target
from ..structs.lmt import Lmt
from .animation_import import (
    LMT_ASSET_TYPE,
    ROOT_MOTION_BONE_ID,
    _block_props,
    _create_bone_mapping,
    get_block_index,
    get_track_keys,
)
from .keyframes import (
    APPID_VERSION_MAPPER,
    ActionKey,
    BONE_TRACK_TYPES,
    BOUNDS_BUFF_TYPES,
    LMTKeyFrames,
)


def _local_space_to_parent_translation(frame, pose_bone, app_id):
    bone = pose_bone.bone
    anim_bone_id = get_anim_retarget(pose_bone, app_id).split("_")[0]

    if bone.parent is None:
        if anim_bone_id in ("0", "255") or anim_bone_id.startswith("254"):
            rest = bone.matrix_local.to_translation()
            lmt_rest = Vector((rest.x, rest.z, -rest.y))
            return frame + lmt_rest

    # A chain's goal was imported without a parent-space conversion, so it must
    # leave the same way. The bare ids are the fallback for rigs built before
    # the control bones were marked.
    if get_chain_target(pose_bone, app_id) or anim_bone_id in ("19", "23"):
        rest = bone.matrix_local.to_translation()
        return frame + Vector((rest.x, rest.z, -rest.y))

    global_pos = bone.matrix_local @ frame
    if bone.parent is not None:
        return bone.parent.matrix_local.inverted() @ global_pos
    return global_pos


# track type -> usage on an ordinary bone, and on the root motion bone
_TRACK_TYPE_USAGES = {
    "rotation_quaternion": (0, 3),
    "location": (1, 4),
    "scale": (2, 5),
}


def _block_custom_properties(bl_obj, app_id):
    return bl_obj.albam_custom_properties.get_custom_properties_for_appid(
        app_id, asset_type=LMT_ASSET_TYPE)


def _block_secondary_properties(bl_obj, app_id):
    return bl_obj.albam_custom_properties.get_custom_properties_secondary_for_appid(
        app_id, asset_type=LMT_ASSET_TYPE)


def _select_kf_usage(pose_bone, track_type, app_id):
    try:
        ordinary, motion_root = _TRACK_TYPE_USAGES[track_type]
    except KeyError:
        raise ValueError(f"Track type {track_type} isn't correct")
    is_mroot = get_anim_retarget(pose_bone, app_id) == str(ROOT_MOTION_BONE_ID)
    return motion_root if is_mroot else ordinary


def _block_length(action, fcurves, custom_props):
    """How many frames the block runs for.

    Import sets the action's manual frame range to the block's length, and
    that range is what decides it - it is the control a user retimes a clip
    with, and it is right where keyframes alone are not: a track that never
    changes carries a single keyframe however long the block runs, a static
    idle the engine holds for a couple of seconds.

    A .blend saved before #273 has no manual range and keeps the length in a
    `num_frames` property that is no longer registered but still stored, so
    that is read the way it always was: an action with real keyframes decides
    its own length, one without falls back to the stored value.
    """
    if action is not None and action.use_frame_range:
        return int(action.frame_range[1])
    stored = int(custom_props.get("num_frames", 0))
    if action is None:
        return stored
    if fcurves is None:
        # stored raw_data is written back as is, under the length it had
        return stored or int(action.frame_range[1])
    frames = {keyframe.co[0] for fcurve in fcurves for keyframe in fcurve.keyframe_points}
    if len(frames) > 1:
        return int(action.frame_range[1])
    return stored or int(action.frame_range[1])


def _serialize_lmt_track(armature, tracks, mapping, app_id):
    keyframes = LMTKeyFrames()
    keyframes.version = APPID_VERSION_MAPPER[app_id]
    for bone_name, bone_tracks in tracks.items():
        location = {}
        rotation_quaternion = {}
        scale = {}
        pose_bone = armature.pose.bones.get(bone_name)
        bone_index = mapping.get(bone_name)
        for frame, action_key in bone_tracks.items():
            if action_key.location is not None:
                kf = action_key.location
                kf = _local_space_to_parent_translation(kf, pose_bone, app_id)
                location[frame] = kf
            if action_key.rotation_quaternion is not None:
                rotation_quaternion[frame] = action_key.rotation_quaternion
            if action_key.scale is not None:
                scale[frame] = action_key.scale
        if rotation_quaternion:
            keyframes.track_type = "rotation_quaternion"
            rotation_sorted = {k: rotation_quaternion[k] for k in sorted(rotation_quaternion)}
            usage = _select_kf_usage(pose_bone, "rotation_quaternion", app_id)
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
            usage = _select_kf_usage(pose_bone, "location", app_id)
            kf_type = 2 if len(location_sorted) == 1 else 9
            keyframes.encode_framedata(kf_type, bone_index, location_sorted, usage)
        if scale:
            keyframes.track_type = "scale"
            scale_sorted = {k: scale[k] for k in sorted(scale)}
            kf_type = 2 if len(scale_sorted) == 1 else 9
            usage = _select_kf_usage(pose_bone, "scale", app_id)
            keyframes.encode_framedata(kf_type, bone_index, scale_sorted, usage)
    return keyframes.encoded_frames


def _tracks_source_action(bl_obj, app_id):
    """The action a block's tracks were built from, or None if it has none.

    A .blend saved before source_action existed has none recorded, and there
    the block's own action stands in: import set both together, so it holds
    until the block is pointed at another action."""
    tracks_props = _block_secondary_properties(bl_obj, app_id)["tracks"]
    if not tracks_props.tracks:
        return None
    source = getattr(tracks_props, "source_action", None)
    return source if source is not None else _block_custom_properties(bl_obj, app_id).action


def _stored_track_data(tracks_collection):
    """(usage, key) -> (joint_type, reference_data) for a block's tracks.

    Keys are taken by position, as the file itself does, so a chain's control
    bone ("<id>_1") still finds the track it came from and a second export
    agrees with the first.
    """
    return {
        (item.usage, key): (item.joint_type, tuple(item.reference_data))
        for item, key in zip(
            tracks_collection,
            get_track_keys((item.bone_index, item.usage) for item in tracks_collection))
    }


def _stored_track_data_by_action(app_id):
    """Every block's stored track data, keyed by the action it was built from.

    Taken once, before any block is rebuilt, and across every .lmt in the
    scene: an action imported with one file can be given to a block of
    another. Where several blocks were built from the same action, the first
    by name wins, so the choice doesn't depend on export order.
    """
    by_action = {}
    for bl_obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if bl_obj.type != "EMPTY":
            continue
        tracks_collection = _block_tracks(bl_obj, app_id)
        if not tracks_collection:
            continue
        source = _tracks_source_action(bl_obj, app_id)
        if source is not None:
            by_action.setdefault(source.as_pointer(), _stored_track_data(tracks_collection))
    return by_action


def _update_track_data(bl_obj, encoded_tracks, action, app_id, stored_by_action):
    tracks_props = _block_secondary_properties(bl_obj, app_id)["tracks"]
    tracks_collection = getattr(tracks_props, "tracks")
    # joint_type and reference_data do not come out of an action, and tracks
    # are the only place they live, so each rebuilt track takes them from the
    # stored track it replaces: the one with the same usage and key, among
    # tracks built from this same action. The block's own, if they were;
    # otherwise another block's, which is how a block given an imported
    # action - a new one, or one that held another animation - keeps that
    # animation's chain markers instead of losing them or inheriting the
    # previous animation's.
    if _tracks_source_action(bl_obj, app_id) == action:
        stored = _stored_track_data(tracks_collection)
    else:
        stored = stored_by_action.get(action.as_pointer(), {})
    bone_indices = [int(et.idx_anim_map.split("_")[0]) for et in encoded_tracks]  # workaround for 254_ values
    keys = get_track_keys((bone_index, et.usage) for bone_index, et in zip(bone_indices, encoded_tracks))
    tracks_collection.clear()
    for et, bone_index, key in zip(encoded_tracks, bone_indices, keys):
        item = tracks_collection.add()
        item.buffer_type = et.buffer_type
        item.usage = et.usage
        item.bone_index = bone_index
        item.joint_type, item.reference_data = stored.get((et.usage, key), (0, et.reference_data))
        item.weight = 1.0
        item.raw_data = et.data
    tracks_props.source_action = action


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
    mapping = _create_bone_mapping(armature, app_id)
    mapping = {value: key for key, value in mapping.items()}
    lengths = {}  # bl_obj name -> num_frames, for the blocks regenerated here
    stored_by_action = _stored_track_data_by_action(app_id)
    for bl_obj in bl_objects:
        tracks = {}  # bone_name -> frame -> ActionKey
        custom_props = _block_custom_properties(bl_obj, app_id)
        if custom_props.generate_new and custom_props.action:
            action = custom_props.action
            fcurves = _get_action_fcurves(action, armature)
            lengths[bl_obj.name] = _block_length(action, fcurves, custom_props)
            if "num_frames" in custom_props:
                # a pre-#273 .blend: keep its stored length matching the
                # tracks regenerated here, for a later export of the raw data
                custom_props["num_frames"] = lengths[bl_obj.name]
            num_bone_channels = 0
            for fcurve in fcurves:
                path = fcurve.data_path
                index = fcurve.array_index
                if path.startswith('pose.bones["'):
                    bone_name = path.split('"')[1]
                    track_type = path.split(".")[-1]
                    if track_type not in BONE_TRACK_TYPES:
                        # an action also carries channels that are not a bone's
                        # transform - a chain constraint's influence, say - and
                        # none of them is a track
                        continue
                    num_bone_channels += 1
                    if mapping.get(bone_name, None) is None:
                        continue
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
            if num_bone_channels and not track_attrs:
                raise ValueError(
                    f"Exporting {bl_obj.name!r} resolved zero tracks: none of its action's "
                    f"bone names matched an Anim Retarget id on {armature.name!r}. Writing "
                    "this block out would silently produce num_tracks = 0 with a non-zero "
                    "ofs_frame - check the armature this .lmt was imported onto against the "
                    "bones the action actually keys."
                )
            _update_track_data(bl_obj, track_attrs, action, app_id, stored_by_action)
    return lengths


def _align(value, alignment):
    return (value + alignment - 1) & ~(alignment - 1)


def _block_tracks(bl_obj, app_id):
    """The block's tracks; a slot holds a real block iff this is non-empty.

    An .lmt is an index-addressed table of block slots, and an empty slot is
    a real thing a file can hold - there is no separate "is this slot used"
    bit anywhere, on disk or on the object. Measured over 400 RE5 .lmt files,
    8533 used blocks: none has zero tracks, so "this block has tracks" (set
    at import, or by _generate_track_from_action from a chosen action) is an
    exact stand-in, and unlike a stored flag it cannot go stale or be hand-set
    wrong - see issue #272.

    A block whose action keys bones the armature has no id for never gets
    here: _generate_track_from_action refuses it (#254) before its tracks are
    cleared. One whose action keys no bone at all comes out with no tracks and
    is written as an empty slot - the only thing a block without tracks can be.
    """
    second_props = _block_secondary_properties(bl_obj, app_id)
    return getattr(second_props["tracks"], "tracks")


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
        tracks = _block_tracks(bl_obj, app_id)
        if len(tracks) > 0:
            second_props = _block_secondary_properties(bl_obj, app_id)
            ofc = cur_ofc_bloc_offsets
            block_offsets.append(ofc)
            cur_ofc_bloc_offsets += MOTION_HEADER_SIZE
            total_headers_size += MOTION_HEADER_SIZE

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
        tracks = _block_tracks(bl_obj, app_id)
        if len(tracks) > 0:
            second_props = _block_secondary_properties(bl_obj, app_id)
            total_headers_size += MOTION_HEADER_SIZE

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
        tracks = _block_tracks(bl_obj, app_id)
        if len(tracks) > 0:
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
        tracks = _block_tracks(bl_obj, app_id)
        if len(tracks) > 0:
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


def _lmt_blocks(bl_obj, app_id):
    """This .lmt's blocks, in the order the file stores them.

    A block's position is what gives it its identity: an empty slot has to stay
    empty, and every offset in the header is written by position. That order
    cannot be read back off the scene. `children_recursive` is name order,
    because Blender keeps `bpy.data.objects` sorted by name, and names are
    compared as text while blocks are numbered. Re-importing renames the
    duplicates - the 4th import of a 256 block file in one session gets
    `.1000`, which sorts before the `.771` of the import before it - and a user
    is free to rename a block outright. Sorting on the index recorded at import
    is what survives both.

    Being parented under bl_obj is not the same claim as belonging to it
    (#295) - an empty from a different import, or a plain unrelated one,
    can end up here through ordinary Outliner tidying. Two checks instead
    of one:

    - block_index < 0 means load_lmt never stamped this empty at all, so
      it isn't one of this .lmt's blocks - any other object a user parented
      here, indexed or not.
    - albam_lmt_block_owner names the .lmt root this block was actually
      created under; a block whose owner is a *different* root is excluded
      even though it is indexed and even though it sits directly under
      bl_obj. A block imported before this property existed has no owner
      (None) and is kept, same as before - a .blend saved before the fix
      must keep exporting exactly as it did.
    """
    candidates = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    blocks = []
    for block in candidates:
        if _block_props(block, app_id).block_index < 0:
            continue
        owner = block.albam_lmt_block_owner
        if owner is not None and owner != bl_obj:
            continue
        blocks.append(block)

    counts = Counter(get_block_index(block, app_id) for block in blocks)
    duplicate_indexes = sorted(index for index, count in counts.items() if count > 1)
    if duplicate_indexes:
        raise AlbamCheckFailure(
            "Two blocks claim the same slot",
            f"{bl_obj.name!r} has more than one block recorded at index(es) "
            f"{duplicate_indexes}.",
            "Only one empty per recorded block index is supported - remove or "
            "re-import whichever one is the duplicate.",
        )

    return sorted(blocks, key=lambda block: get_block_index(block, app_id))


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
    bl_objects = _lmt_blocks(bl_obj, app_id)
    # The armature this .lmt was actually imported onto (#254), not whichever
    # one the import panel currently points at - that changes every time a
    # later import runs, while this asset stays tied to its own rig. Only a
    # scene saved before this property existed falls back to the panel.
    armature = bl_obj.albam_lmt_armature
    if armature is None and bl_obj.albam_lmt_armature_name:
        # Recorded, then deleted - the panel's rig may be another character's,
        # which is the silent renumbering #254 is about.
        raise ValueError(
            f"{bl_obj.name!r} was imported onto armature "
            f"{bl_obj.albam_lmt_armature_name!r}, which no longer exists. Re-import "
            "the .lmt onto the current rig, or point it at one from the Python console: "
            f"bpy.data.objects[{bl_obj.name!r}].albam_lmt_armature = bpy.data.objects['<armature>']"
        )
    if armature is None:
        armature = bpy.context.scene.albam.import_options_lmt.armature
    dst_lmt = Lmt(app_id)
    dst_lmt.id_magic = b"LMT\x00"
    dst_lmt.version = APPID_VERSION_MAPPER[app_id]
    dst_lmt.num_block_offsets = len(bl_objects)
    block_offsets = []
    lengths = _generate_track_from_action(armature, bl_objects, app_id)
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
        custom_props = _block_custom_properties(bl_obj, app_id)
        tracks = _block_tracks(bl_obj, app_id)
        if len(tracks) > 0:
            num_frames = lengths.get(bl_obj.name)
            if num_frames is None:
                num_frames = _block_length(custom_props.action, None, custom_props)
            second_props = _block_secondary_properties(bl_obj, app_id)
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
                anim_header.num_frames = num_frames
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
                    dst_track.idx_anim_map = track.bone_index
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
                anim_header.num_frames = num_frames
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
                    dst_track.idx_anim_map = track.bone_index
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
