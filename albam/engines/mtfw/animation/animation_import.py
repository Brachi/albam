"""Reading a .lmt into Blender.

One action per animation block, the bones a track needs but the .mod did not
provide, and the control rig for the limbs whose middle joint the file leaves
to a solver.
"""
import contextlib
from io import BytesIO

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix, Quaternion, Vector

from ....registry import blender_registry
from ..structs.lmt import Lmt
from .keyframes import LMTKeyFrames, LMTKeyframeBounds, TRANSLATION_USAGES, USAGE


HACKY_BONE_INDEX_IK_FOOT_RIGHT = 19
HACKY_BONE_INDEX_IK_FOOT_LEFT = 23

# A limb is not stored as a finished pose. A track whose joint_type is one of
# these marks the root of a chain: the joint at root+1 is keyed by no track at
# all, and the joint this many places past the root carries a position channel
# which is the goal the chain is solved towards. The value says how long the
# chain is, not which limb it is - 42 is a biped's leg and 49 its arm, but a
# quadruped marks fore limbs 43 and hind limbs 42 - so neither the joint_type
# nor the bone id names a body part. Verified over every re5 character: 35422
# chains, none of them keying the joint at root+1.
CHAIN_TARGET_OFFSET = {37: 2, 38: 2, 42: 3, 43: 3, 44: 3, 48: 2, 49: 2}
CHAIN_TARGET_PROP = "mtfw.chain_target"
BLOCK_INDEX_PROP = "mtfw.lmt_block_index"
CHAIN_LENGTH_PROP = "mtfw.chain_length"  # joints the solver owns, plus the target
ROOT_MOTION_BONE_ID = 255
ROOT_MOTION_BONE_NAME = 'root_motion'
ROOT_BONE_NAME = '0'


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


# re5 only, which is what main registered before any of this. Version 67 - re0,
# re1, re6, rev1, rev2, dd - reads without complaint and was briefly seen to
# work, but nothing has ever covered it, and 67 differs from 51 everywhere it
# was measured: joint_type is 0 on all 168607 of re1's tracks, position
# channels sit on 82 child bones where 51 uses two, and the blocks are laid out
# differently. Parked rather than rejected.
@blender_registry.register_import_function(app_id="re5", extension='lmt', albam_asset_type="ANIMATION")
def load_lmt(vfile, context):
    app_id = vfile.app_id
    lmt_bytes = vfile.get_bytes()
    lmt = Lmt(KaitaiStream(BytesIO(lmt_bytes)))
    lmt._read()
    lmt_ver = lmt.version
    armature = context.scene.albam.import_options_lmt.armature
    mapping = _create_bone_mapping(armature)

    # DEBUG_BLOCK = 2
    DEBUG_BLOCK = None
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(bl_object_name, None)
    # A chain is declared per block, but the constraint that serves it lives on
    # the rig for good. Remember both so every action can say whether its chains
    # are active - see _key_chain_influence.
    chain_constraints = {}
    block_chains = []

    for block_index, block in enumerate(lmt.block_offsets):
        anim_object_name = f"{vfile.display_name}.{str(block_index).zfill(4)}"
        anim_object = bpy.data.objects.new(anim_object_name, None)
        anim_object.parent = bl_object
        # Which slot of the file this block is. The name carries it too, but
        # Blender renumbers duplicate names, so it stops matching as soon as
        # the same .lmt is imported twice in one session - see _lmt_blocks.
        anim_object[BLOCK_INDEX_PROP] = block_index
        if block.offset == 0:
            continue
        if DEBUG_BLOCK is not None and DEBUG_BLOCK != block_index:
            continue
        armature.animation_data_create()
        name = f"{armature.name}.{vfile.display_name}.{str(block_index).zfill(4)}"
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        channels = _get_action_channels(action, armature)

        tracks = anim_object.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
            "tracks"]
        chains = _find_chains(block.block_header.tracks, lmt_ver)
        # Workaround for cases when same bone index has more than 3 anim tracks
        last_usage = {}
        duplicated_bids = {}
        for track_index, track in enumerate(block.block_header.tracks):
            if duplicated_bids.get(track.bone_index, None) is None:
                duplicated_bids[track.bone_index] = 0

            # Custom attributes for a track
            item = tracks.tracks.add()
            item.copy_custom_properties_from(track)
            item.raw_data = track.data
            bounds = None
            keyframes = LMTKeyFrames()
            if lmt_ver > 51:  # parked with version 67 import; see load_lmt
                bounds_body = track.bounds
                if bounds_body:
                    b_item = item.track_bounds.add()
                    b_item.copy_custom_properties_from(track.bounds)
                    bounds = LMTKeyframeBounds(track.bounds)
                    keyframes.bounds = bounds

            try:
                lu = last_usage[track.bone_index][-1]
                if lu >= track.usage:
                    duplicated_bids[track.bone_index] += 1
                last_usage[track.bone_index].append(track.usage)
            except KeyError:
                last_usage[track.bone_index] = [track.usage]

            if duplicated_bids[track.bone_index] == 0:
                key = str(track.bone_index)
            else:
                key = str(track.bone_index) + "_" + str(duplicated_bids[track.bone_index])
            bone_index = mapping.get(key)

            # Set motion root bone
            if bone_index is None and track.bone_index == ROOT_MOTION_BONE_ID:
                bone_index = _get_or_create_root_motion_bone(armature, mapping)

            # Restore IK. Driven by the chain the block declares, not by a
            # fixed pair of bone ids: an arm, and every limb of a quadruped,
            # needs exactly the same treatment as a biped's feet.
            is_chain_goal = track.bone_index in chains and bone_index is not None
            if is_chain_goal:
                bone_index = _get_or_create_ik_bone(
                    armature, track.bone_index, bone_index, mapping, chains[track.bone_index],
                    chain_constraints)

            # LMT references service(?) bones absent in the imported armature
            if bone_index is None:
                bone_index = _create_missing_bones(armature,
                                                   track.bone_index,
                                                   key,
                                                   mapping)
            if track.joint_type != 0:
                action[f"{USAGE.get(track.usage)}_{key}"] = track.joint_type

            action[f"rd_{USAGE.get(track.usage)}_{key}"] = str(track.reference_data)

            track_type = USAGE[track.usage]
            keyframes.track_type = USAGE[track.usage]
            if track.len_data > 0:
                keyframes.decode_framedata(lmt_ver, track.buffer_type, track.data)
            else:
                frame = None
                rd = track.reference_data
                if track_type == "location":
                    frame = Vector((rd[0] / 100, rd[1] / 100, rd[2] / 100))
                elif track_type == "rotation_quaternion":
                    frame = Quaternion((rd[3], rd[1], rd[2], rd[0]))
                elif track_type == "scale":
                    frame = Vector((rd[0], rd[1], rd[2]))
                keyframes.decoded_frames.append(frame)
            if not keyframes.decoded_frames:
                continue

            if track.usage == 4 or (track.usage == 1 and armature.data.bones[bone_index].parent):
                keyframes.decoded_frames = _parent_space_to_local_translation(
                    keyframes.decoded_frames, armature, bone_index)

            # temporary hack for the root bone
            if track.usage == 1 and track.bone_index == 0 and armature.data.bones[bone_index].parent is None:
                keyframes.decoded_frames = _parent_space_to_local_translation(
                    keyframes.decoded_frames, armature, bone_index)

            if is_chain_goal and track.usage in TRANSLATION_USAGES:
                keyframes.decoded_frames = [
                    None if f is None else f - _rest_head_in_bone_space(armature, bone_index)
                    for f in keyframes.decoded_frames
                ]

            err = _create_blender_action(
                action, keyframes, bone_index, track_type, block_index, track_index, channels)
            if err:
                continue
        block_chains.append((channels, set(chains)))

        # building custom attributes of lmt metadata
        custom_properties = anim_object.albam_custom_properties.get_custom_properties_for_appid(
            app_id)
        custom_properties.copy_custom_properties_from(block.block_header)
        custom_properties.action = action
        anim_props = anim_object.albam_custom_properties
        if lmt_ver < 67:
            col_events = anim_props.get_custom_properties_secondary_for_appid(app_id)[
                "col_events"]
            col_events.copy_custom_properties_from(block.block_header.collision_events)
            for attr_index, attribute in enumerate(block.block_header.collision_events.attributes):
                item = col_events.attributes.add()
                item.copy_custom_properties_from(attribute)

            motion_se = anim_props.get_custom_properties_secondary_for_appid(app_id)[
                "motion_se"]
            motion_se.copy_custom_properties_from(block.block_header.motion_sound_effects)
            for attr_index, attribute in enumerate(block.block_header.motion_sound_effects.attributes):
                item = motion_se.attributes.add()
                item.copy_custom_properties_from(attribute)
        else:
            seq_infos = anim_props.get_custom_properties_secondary_for_appid(app_id)[
                "sequence_infos"]
            # seq_info.copy_custom_properties_from(block.block_header.sequence_infos)
            for s_index, s_info in enumerate(block.block_header.sequence_infos):
                item = seq_infos.sequence_info.add()
                item.copy_custom_properties_from(s_info)
                for attr_index, s_attr in enumerate(s_info.attributes):
                    a_item = item.attributes.add()
                    a_item.copy_custom_properties_from(s_attr)

            keyframe_infos = anim_props.get_custom_properties_secondary_for_appid(app_id)[
                "keyframe_infos"]
            if len(block.block_header.key_infos) > 0:
                for k_index, k_info in enumerate(block.block_header.key_infos):
                    item = keyframe_infos.keyframe_info.add()
                    item.copy_custom_properties_from(k_info)
                    for kb_index, k_block in enumerate(k_info.keyframe_blocks):
                        k_item = item.keyframe_blocks.add()
                        k_item.copy_custom_properties_from(k_block)

    _key_chain_influence(block_chains, chain_constraints)
    return bl_object


def _create_blender_action(action, keyframes, bone_index, track_type, block_index, track_index, channels):
    data_path = f"pose.bones[\"{bone_index}\"].{track_type}"
    num_curv = 4 if track_type == "rotation_quaternion" else 3

    group_name = str(bone_index)
    group = channels.groups.get(group_name) or channels.groups.new(group_name)
    try:
        curves = [channels.fcurves.new(data_path=data_path, index=i) for i in range(num_curv)]
        for c in curves:
            c.group = group
    except RuntimeError as err:
        print('unknown error:', err, "Block index: {0}, Track index:{1}".format(
            block_index, track_index))
        return True
    for frame_index, frame_data in enumerate(keyframes.decoded_frames):
        if frame_data is None:
            continue
        for curve_idx, curve in enumerate(curves):
            curve.keyframe_points.add(1)
            curve.keyframe_points[-1].co = (frame_index + 1, frame_data[curve_idx])  # frame , value
            curve.keyframe_points[-1].interpolation = 'LINEAR'
    return False


def _key_chain_influence(block_chains, chain_constraints):
    """Switch each chain's constraint off in the blocks that do not declare it.

    The constraint is part of the rig and the chain is part of a block, so a
    constraint left at full influence keeps solving towards a control bone the
    current block never keys - it sits at its rest position and drags the limb
    to it. Keying influence per action makes the rig follow the data.
    """
    for channels, declared in block_chains:
        for target_bone_index, (owner, constraint_name) in chain_constraints.items():
            data_path = f'pose.bones["{owner}"].constraints["{constraint_name}"].influence'
            try:
                curve = channels.fcurves.new(data_path=data_path)
            except RuntimeError:
                continue
            curve.keyframe_points.add(1)
            curve.keyframe_points[-1].co = (1, 1.0 if target_bone_index in declared else 0.0)
            curve.keyframe_points[-1].interpolation = 'CONSTANT'


def _rest_head_in_bone_space(armature, bone_name):
    """The control bone's own rest position, in the space its location channel
    is measured in.

    A chain's goal is the joint's position in model space, not an offset from
    where that joint happens to rest. The control bone sits at the joint so it
    is usable as a handle, so its rest position has to come back out of the
    value - and back in again on export. A bone's rest rotation is what turns
    the file's Y-up vector into Blender's Z-up one, hence the swap.
    """
    rest = armature.data.bones[bone_name].matrix_local.to_translation()
    return Vector((rest.x, rest.z, -rest.y))


def _find_chains(tracks, version):
    """{target bone id: how many joints the solver owns}, for one block.

    Only for version 51, where the chain convention was measured. Every one of
    re1's 168607 tracks carries joint_type 0, so version 67 either does not use
    the field or uses it for something else, and it puts position channels on
    82 different child bones where 51 uses them on two - so the reading that a
    position channel marks a chain's goal does not carry over either. Applying
    51's table there would be guessing.

    Read from the root track's joint_type rather than matched against bone ids,
    because the same value marks different limbs on different skeletons.
    """
    chains = {}
    if version != 51:
        return chains
    for track in tracks:
        offset = CHAIN_TARGET_OFFSET.get(track.joint_type)
        if offset is not None:
            chains[track.bone_index + offset] = offset
    return chains


def _create_bone_mapping(armature_obj):
    """Creates a dictionary: animation bone index -> bone name.

    The animation bone index isn't something Albam derives - it's
    .mod's own idx_anim_map field (structs/mod-*.ksy), copied verbatim onto
    each bone as the 'mtfw.anim_retarget' custom property in
    mesh.py:build_blender_armature(). MT Framework uses this to decouple a
    character's own skeleton (bone order/count is per-.mod, e.g. pl00 vs an
    enemy with a completely different hierarchy) from the numeric bone-id
    space .lmt tracks are keyed on, which is shared across the whole engine
    (root=0, root_motion=255, common IK/service ids, etc. - see the
    HACKY_BONE_INDEX_*/ROOT_*_ID constants above). An .lmt authored against
    one character's idx_anim_map layout plays back correctly against any
    other armature as long as this property is populated the same way, since
    load_lmt()/_generate_track_from_action() only ever address bones through
    this id, never through .mod's own per-file bone order.

    Note: 'mtfw.anim_retarget' is stored as a str (see the assignments
    below and in mesh.py), so the `== 0`/`== 0` comparisons just below are
    always False against the string "0" - the multiple-root-bone special
    case they guard is currently dead code, not a deliberately-skipped one.
    """
    bone_names = {}
    # find root bones, at least 2 can have the same 0 index
    root_bone_names = [b.name for idx, b in enumerate(
        armature_obj.data.bones) if b.get('mtfw.anim_retarget', None) == 0]
    for b_idx, mapped_bone in enumerate(armature_obj.data.bones):
        animation_bone_id = mapped_bone.get('mtfw.anim_retarget')
        if animation_bone_id is None:
            print(f"WARNING: {armature_obj.name}->{mapped_bone.name} doesn't contain a mapped bone")
            continue
        # ignore possible root_ground bone
        if animation_bone_id == 0 and len(root_bone_names) > 1:
            if mapped_bone.parent is None:
                continue
        if animation_bone_id in bone_names:
            print(f"WARNING: bone_id {b_idx} already mapped. TODO")
        bone_names[animation_bone_id] = mapped_bone.name
    return bone_names


@contextlib.contextmanager
def _armature_in_edit_mode(armature):
    """Edit mode on `armature`, and object mode again however the block ends.

    A bone can only be created in edit mode, which is modal and global - it
    acts on whatever happens to be active - so the armature has to be made
    active first. Restoring the mode in a finally matters: a raise in the
    middle would otherwise leave Blender in edit mode, where every later
    operator here fails.
    """
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    try:
        yield armature.data.edit_bones
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')


def _create_missing_bones(armature, bone_index, key, mapping):
    """A bone to hang a track on when the rig maps nothing to that anim id.

    The name Blender settles on is the one to return, not the one asked for.
    Bone names are unique, and a rig can already carry a bone *named* for a
    number that is some other bone's anim id - the two are separate spaces, a
    bone named "104" answering to anim id 77 is ordinary. Blender then makes
    the new bone "104.001", and returning the requested name instead hands the
    caller that unrelated existing bone: the track lands on it, overwriting
    whatever it was doing, and export reads it back as that bone's own id, so
    the original id disappears from the file and a duplicate takes its place.
    """
    with _armature_in_edit_mode(armature) as edit_bones:
        blender_bone = edit_bones.new(key)
        bone_name = blender_bone.name
        mapping[key] = bone_name
        blender_bone.tail[2] += 0.01
        blender_bone["mtfw.anim_retarget"] = key
    return bone_name


def _follow_root_motion(armature, bone_name, root_motion_bone):
    """Make one bone ride the root motion bone, rotation included.

    Root motion is a whole-character transform, so a bone that only copies its
    position turns nowhere: a block that spins the character around plays as a
    twist in place, and a chain's goal keeps reaching for the point it would
    have reached before the turn.

    CHILD_OF rather than a copy pair, for two reasons. It applies the target's
    transform as a delta from the target's own rest, which a world-space
    COPY_ROTATION does not - that copies the absolute rotation, root motion's
    90 degree rest orientation and all, and lays the character on its face.
    And it does it without making anything an actual child, which matters
    because both import and export decide how to convert a translation by
    asking whether a bone has a parent.

    The inverse matrix is what makes the delta a delta: at rest the constraint
    has to be an identity, or every rig gains root motion's rest orientation
    the moment the constraint is added.
    """
    pose_bone = armature.pose.bones[bone_name]
    constraint = pose_bone.constraints.new('CHILD_OF')
    constraint.target = armature
    constraint.subtarget = root_motion_bone
    constraint.inverse_matrix = armature.data.bones[root_motion_bone].matrix_local.inverted()


def _get_or_create_ik_bone(armature, track_bone_index, bone_index, mapping, chain_count,
                           chain_constraints):
    """A control bone carrying a chain's goal, with the chain constrained to it.

    The goal is a point in space rather than a rotation of the bone it belongs
    to, so it cannot live on the target bone itself: put there, it translates
    that bone away from its parent and drags the limb with it. `chain_count`
    reaches from the target back to the joint the file never keys.
    """
    if track_bone_index == HACKY_BONE_INDEX_IK_FOOT_RIGHT:
        bone_name = "IK_Foot.R"
    elif track_bone_index == HACKY_BONE_INDEX_IK_FOOT_LEFT:
        bone_name = "IK_Foot.L"
    else:
        bone_name = f"IK_Target.{track_bone_index}"
    # The control bone and its constraint outlive the import that made them,
    # but chain_constraints is rebuilt per file: a second .lmt on the same rig
    # has to find the existing constraint again, or none of its actions key
    # influence and every chain stays wherever the previous file left it.
    pose_bone = armature.pose.bones[mapping.get(str(track_bone_index))]
    constraint_name = f"chain.{track_bone_index}"
    if bone_name in armature.data.bones:
        if constraint_name in pose_bone.constraints:
            chain_constraints[track_bone_index] = (pose_bone.name, constraint_name)
        return bone_name

    with _armature_in_edit_mode(armature) as edit_bones:
        blender_bone = edit_bones.new(bone_name)
        blender_bone.head = edit_bones[bone_index].head
        blender_bone.tail = edit_bones[bone_index].tail
        blender_bone["mtfw.anim_retarget"] = str(track_bone_index) + "_1"
        # marks the bone as carrying a goal rather than a joint's own transform,
        # so export leaves its position channel alone exactly as import did
        blender_bone[CHAIN_TARGET_PROP] = True
        blender_bone[CHAIN_LENGTH_PROP] = chain_count

    # constrain the chain to the goal
    constraint = pose_bone.constraints.new('IK')
    constraint.name = constraint_name
    constraint.target = armature
    constraint.subtarget = bone_name
    constraint.chain_count = chain_count
    constraint.use_rotation = True
    chain_constraints[track_bone_index] = (pose_bone.name, constraint_name)

    root_motion_bone = _get_or_create_root_motion_bone(armature, mapping)
    _follow_root_motion(armature, bone_name, root_motion_bone)

    return bone_name


def _get_or_create_root_motion_bone(armature, mapping):
    bone_name = ROOT_MOTION_BONE_NAME
    if bone_name in armature.data.bones:
        return bone_name

    with _armature_in_edit_mode(armature) as edit_bones:
        blender_bone = edit_bones.new(bone_name)
        blender_bone.tail[2] += 0.01
        blender_bone["mtfw.anim_retarget"] = "255"

    root_bone_name = mapping.get(ROOT_BONE_NAME)
    if root_bone_name is None:
        raise ValueError(
            f"The armature has no bone for animation id {ROOT_BONE_NAME}, so root motion "
            "has nothing to move. Check the skeleton's mtfw.anim_retarget properties."
        )
    _follow_root_motion(armature, root_bone_name, bone_name)

    return bone_name


def _parent_space_to_local_translation(decoded_frames, armature, bone_index):
    '''
    LMT frames are usually stored in parent space, Blender uses local space
    This function does the conversion and switches Y/Z axis
    '''
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
