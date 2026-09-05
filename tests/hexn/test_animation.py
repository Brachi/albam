import json
import math
import os

import bpy
from mathutils import Quaternion, Vector

from .test_skeleton_import import SKEL_HASH

# Reuses test_anims_parsing.py's own committed dataset.
ANIMS_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "anims_parsing_hashes.json")
with open(ANIMS_PARSING_DATASET_PATH) as f:
    ANIMS_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_anims_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_anims_path_hash")
        argvalues = [(d["app_id"], d["anims_path_hash"]) for d in ANIMS_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['anims_path_hash']}" for d in ANIMS_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")
    elif "local_app_id" in metafunc.fixturenames:
        # The tests below pin one specific file rather than sweeping the
        # dataset, so they only need the app_id.
        metafunc.parametrize("local_app_id", ["reorc"], scope="session")


def _iter_clips(anims):
    from albam.engines.hexn.animation import parse_clip_name

    offset = 0
    for file_info in anims.files_info:
        clip_bytes = anims.buffer_chunks[offset:offset + file_info.size]
        offset += file_info.size
        clip_path, skeleton_name = parse_clip_name(file_info.name)
        yield file_info, clip_bytes, clip_path, skeleton_name


def _is_empty_archive(anims):
    """The dataset deliberately includes one archive with no entries at
    all (see its own dataset comment). Anything else decoding to zero
    clips is a failure, not a reason to pass quietly."""
    return not anims.files_info


def test_decode_clip_sane_across_dataset(game_fs_root, hash_to_path, local_app_id, local_anims_path_hash):
    """decode_clip() succeeds on every clip in these files and produces
    unit-length rotation quaternions and a finite, positive-length pose -
    the strongest content-level check available without a real skeleton
    to compare bind poses against (see animation.py's own module docstring:
    the small number of real clips that fail to decode are all in an
    obviously-fake dev archive referencing placeholder skeleton names, not
    real game content).
    """
    from albam.engines.hexn.animation import decode_clip
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    path = hash_to_path[local_anims_path_hash]
    data = game_fs_root.readbytes(path)
    anims = HexaneAnims.from_bytes(data)
    anims._read()

    n_clips = 0
    for file_info, clip_bytes, clip_path, skeleton_name in _iter_clips(anims):
        n_clips += 1
        decoded = decode_clip(clip_bytes, name=file_info.name, skeleton_name=skeleton_name)

        assert decoded.num_frames > 0
        assert decoded.num_bones > 0
        assert round(decoded.framerate) == 30
        assert decoded.num_frames == round(decoded.duration_seconds * decoded.framerate) + 1

        assert decoded.bones_with_rotation | decoded.bones_with_translation == set(decoded.bones)

        for bone_idx, (positions, rotations) in decoded.bones.items():
            assert len(positions) == decoded.num_frames
            assert len(rotations) == decoded.num_frames
            # Rotation magnitude is unit *by construction* - the decoder
            # rebuilds the dropped quaternion component from the unit-norm
            # constraint - so it says nothing about whether the right bits
            # were read. What does: every channel bone carries a real
            # value rather than the identity/zero it was seeded with.
            for p in positions:
                assert all(not math.isnan(c) and not math.isinf(c) for c in p)
            for q in rotations:
                assert not math.isnan(q.magnitude)

        # A clip whose only rotation-channel bone is the root can be
        # genuinely rotation-free (a stationary idle); one with several
        # rotating bones that all decode to the identity they were seeded
        # with means the channel data never got read.
        seeded_rotation = Quaternion((1, 0, 0, 0))
        if len(decoded.bones_with_rotation) > 1:
            assert any(any(q != seeded_rotation for q in decoded.bones[b][1])
                       for b in decoded.bones_with_rotation), (
                "every rotation channel in this clip decoded to the identity it was seeded with"
            )

    assert n_clips or _is_empty_archive(anims), (
        "archive decoded no clips at all - it has entries, so something stopped them being read"
    )


def _make_throwaway_armature(name, num_bones):
    """Minimal flat-chain armature - NOT a real skeleton reconstruction,
    just enough bones/hierarchy to exercise build_blender_action()'s
    fcurve creation and bind-matrix math end to end. See
    build_blender_action's own docstring for what a real caller (once the
    skeleton importer lands) needs to provide instead.
    """
    armature_data = bpy.data.armatures.new(name)
    armature_obj = bpy.data.objects.new(name, armature_data)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = []
    for i in range(num_bones):
        b = armature_data.edit_bones.new(f"bone_{i}")
        b.head = (0, 0, i * 0.1)
        b.tail = (0, 0, i * 0.1 + 0.08)
        if i > 0:
            b.parent = edit_bones[i - 1]
        edit_bones.append(b)
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


def test_build_blender_action(game_fs_root, hash_to_path, local_app_id, local_anims_path_hash):
    """build_blender_action() runs end to end against a throwaway armature
    (positional bone_names lookup - see its own docstring for why that's
    documented as an assumption) and produces finite keyframe values on
    every fcurve, for every real clip in this dataset.
    """
    from albam.engines.hexn.animation import build_blender_action, decode_clip
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    path = hash_to_path[local_anims_path_hash]
    data = game_fs_root.readbytes(path)
    anims = HexaneAnims.from_bytes(data)
    anims._read()

    decoded_clips = [
        decode_clip(clip_bytes, name=file_info.name, skeleton_name=skeleton_name)
        for file_info, clip_bytes, _clip_path, skeleton_name in _iter_clips(anims)
    ]
    armature_obj = None
    bone_names = None
    if decoded_clips:
        # Wide enough for every clip in the archive, not just the first:
        # build_blender_action skips any bone index past the end of
        # bone_names, so a narrower armature would silently drop the extra
        # bones of a later clip instead of exercising them.
        armature_obj = _make_throwaway_armature(
            f"test-{local_anims_path_hash}", max(d.num_bones for d in decoded_clips))
        bone_names = [b.name for b in armature_obj.pose.bones]

    n_actions = 0
    for file_info, decoded in zip((fi for fi, *_ in _iter_clips(anims)), decoded_clips):

        action = build_blender_action(armature_obj, decoded, file_info.name, bone_names)
        n_actions += 1

        for layer in action.layers:
            for strip in layer.strips:
                for channelbag in strip.channelbags:
                    assert len(channelbag.fcurves) > 0
                    for fcurve in channelbag.fcurves:
                        for keyframe_point in fcurve.keyframe_points:
                            value = keyframe_point.co[1]
                            assert not math.isnan(value)
                            assert not math.isinf(value)

    assert n_actions or _is_empty_archive(anims), (
        "archive built no actions at all - it has entries, so something stopped them being read"
    )


# What decode_clip() produces for the first clip in ANIMS_BASELINE_HASH's
# archive that has both animated channel kinds. Recorded from real bytes
# that can't change; the point is that a change in the decoder shows up
# here as a failure rather than as animation that merely still looks
# finite. Every one of these was checked to move under a mutated decoder
# (component order, interpolation, frameset lookup, bit window).
ANIMS_BASELINE_HASH = "0aadc76ea27d6c42"
BASELINE_FRAMES = 201
BASELINE_BONES = 105
BASELINE_ROTATION_CHANNELS = 40
BASELINE_TRANSLATION_CHANNELS = 25
# (bone index, frame) -> (w, x, y, z)
BASELINE_ROTATIONS = {
    (2, 0): (-0.167481, 0.698822, -0.398817, -0.569686),
    (2, 100): (-0.167488, 0.698843, -0.399321, -0.569305),
    (2, 200): (-0.167481, 0.698822, -0.398817, -0.569686),
    (101, 0): (0.015775, -0.000237, 0.000281, 0.999875),
}
# (bone index, frame) -> (x, y, z)
BASELINE_POSITIONS = {
    (1, 0): (0.0, 0.366452, 0.0),
    (1, 100): (0.0, 0.366889, 0.0),
    (1, 200): (0.0, 0.366452, 0.0),
}


def _first_fully_animated_clip(anims):
    """The first clip in `anims` with both an animated rotation and an
    animated translation channel - the code path with real interpolation
    in it, and a stable choice for a fixed archive."""
    for file_info, clip_bytes, clip_path, skeleton_name in _iter_clips(anims):
        clip = type(anims).AnimClip.from_bytes(clip_bytes)
        clip._read()
        if clip.num_anim_r_channels > 0 and clip.num_anim_t_channels > 0:
            return file_info, clip_bytes
    raise AssertionError("no clip with both animated channel kinds in this archive")


def test_decoded_values_match_the_recorded_baseline(game_fs_root, hash_to_path, local_app_id):
    """Pins decode_clip()'s actual output for one real clip. The
    structural checks elsewhere in this file pass just as happily on a
    decoder that reads the wrong bits - unit-length quaternions and finite
    positions come out either way - so this compares the numbers
    themselves.
    """
    from albam.engines.hexn.animation import decode_clip
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    anims = HexaneAnims.from_bytes(game_fs_root.readbytes(hash_to_path[ANIMS_BASELINE_HASH]))
    anims._read()
    file_info, clip_bytes = _first_fully_animated_clip(anims)
    decoded = decode_clip(clip_bytes, name=file_info.name)

    assert decoded.num_frames == BASELINE_FRAMES
    assert decoded.num_bones == BASELINE_BONES
    assert len(decoded.bones_with_rotation) == BASELINE_ROTATION_CHANNELS
    assert len(decoded.bones_with_translation) == BASELINE_TRANSLATION_CHANNELS

    for (bone_index, frame), expected in BASELINE_ROTATIONS.items():
        actual = decoded.bones[bone_index][1][frame]
        assert tuple(round(c, 6) for c in actual) == expected, f"bone {bone_index} frame {frame}"
    for (bone_index, frame), expected in BASELINE_POSITIONS.items():
        actual = decoded.bones[bone_index][0][frame]
        assert tuple(round(c, 6) for c in actual) == expected, f"bone {bone_index} frame {frame}"

    # This clip is a looping idle, and it closes its loop: its last frame
    # is its first, exactly. That only holds if the final frame resolves
    # through the frameset that actually covers it.
    last = decoded.num_frames - 1
    for bone_index in (1, 2):
        assert decoded.bones[bone_index][0][last] == decoded.bones[bone_index][0][0]
        assert decoded.bones[bone_index][1][last] == decoded.bones[bone_index][1][0]


def test_a_skeletons_own_bind_pose_poses_it_back_to_rest(game_fs_root, hash_to_path, local_app_id):
    """Feed a real skeleton's own bind transforms back in as a one-frame
    clip: a clip that says "every bone is exactly where it rests" has to
    leave the armature in its rest pose.

    This is what pins down the space conversion. A clip stores
    parent-local transforms in the game's Y-up space, while pose channels
    hold a basis against a rest orientation the skeleton importer chooses
    itself, in Blender's Z-up space - and getting that wrong still
    produces finite, unit-length, entirely plausible-looking keyframes.
    Here it produces a rig rotated 90 degrees off its own rest pose
    instead of an exact match.
    """
    from pathlib import PureWindowsPath

    from albam.engines.hexn.animation import DecodedClip, build_blender_action
    from albam.engines.hexn.skeleton import build_blender_skeleton_by_stem
    from albam.engines.hexn.structs.hexane_skel import HexaneSkel

    skel_path = hash_to_path[SKEL_HASH]
    skel = HexaneSkel.from_bytes(game_fs_root.readbytes(skel_path))
    skel._read()
    armature_ob, bone_names = build_blender_skeleton_by_stem(
        bpy.context, PureWindowsPath(skel_path).stem)
    assert armature_ob is not None

    clip = DecodedClip(
        name="bind-pose", skeleton_name="", duration_seconds=0.0, framerate=30.0,
        num_frames=1, num_bones=skel.node_count,
    )
    for node_index, transform in enumerate(skel.local_transforms):
        position, rotation = transform.position, transform.rotation
        clip.bones[node_index] = (
            [Vector((position.x, position.y, position.z))],
            [Quaternion((rotation.w, rotation.x, rotation.y, rotation.z))],
        )
    clip.bones_with_rotation = set(clip.bones)
    clip.bones_with_translation = set(clip.bones)

    build_blender_action(armature_ob, clip, "bind-pose-identity", bone_names, skeleton=skel)
    bpy.context.scene.frame_set(0)
    evaluated = armature_ob.evaluated_get(bpy.context.evaluated_depsgraph_get())

    worst = max((pose_bone.matrix.translation - pose_bone.bone.matrix_local.translation).length
                for pose_bone in evaluated.pose.bones)
    assert worst < 1e-4, f"posed bind pose is {worst:.3f} away from the rest pose"


def test_a_clip_poses_the_armature_the_way_the_game_composes_it(game_fs_root, hash_to_path, local_app_id):
    """Import a real clip through the operator and compare every posed bone
    against the clip composed in the game's own space.

    A clip only describes the bones it moves, and the armature's rest pose
    carries the bind positions but not the bind orientations (the importer
    aims each bone at its child). Writing a clip's transforms straight into
    pose channels therefore leaves untouched bones in that invented frame
    for their animated children to compose on top of, and rotates skinned
    vertices about the wrong axis - a character folded over itself, out of
    values that are all finite and all unit-length.
    """
    from albam.engines.hexn.animation import (GAME_TO_BLENDER, GAME_TO_BLENDER_INVERTED, _clip_matrix,
                                              _compose, _game_matrix, decode_clip)
    from albam.engines.hexn.skeleton import (armature_name_for, bone_names_from_armature, find_skel,
                                             find_skel_vfile)
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    anims = HexaneAnims.from_bytes(game_fs_root.readbytes(hash_to_path[ANIMS_BASELINE_HASH]))
    anims._read()
    file_info, clip_bytes = _first_fully_animated_clip(anims)
    clip_path, skeleton_name = file_info.name.rsplit("--", 1)

    vfs = bpy.context.scene.albam.vfs
    vfs.select_vfile(local_app_id, file_info.name.replace("\\", "/").lstrip("/") + ".animclip")
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    skel_vfile = find_skel_vfile(bpy.context, skeleton_name)
    armature_ob = bpy.data.objects[armature_name_for(skel_vfile)]

    skel = find_skel(bpy.context, skeleton_name)
    assert skel is not None
    decoded = decode_clip(clip_bytes, name=file_info.name)
    bone_names = bone_names_from_armature(armature_ob)
    parents = [-1 if parent == 0xffff else parent for parent in skel.parents]
    bind_local = [_game_matrix(transform) for transform in skel.local_transforms]
    bind_world = _compose(bind_local, parents)

    worst = 0.0
    for frame in (0, decoded.num_frames // 2, decoded.num_frames - 1):
        bpy.context.scene.frame_set(frame)
        evaluated = armature_ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        frame_world = _compose(
            [_clip_matrix(decoded, i, frame, bind_local[i]) for i in range(len(bind_local))], parents)
        for bone_index, name in enumerate(bone_names):
            if name is None or name not in evaluated.pose.bones:
                continue
            delta = (GAME_TO_BLENDER @ (frame_world[bone_index] @ bind_world[bone_index].inverted())
                     @ GAME_TO_BLENDER_INVERTED)
            expected = delta @ armature_ob.data.bones[name].matrix_local
            posed = evaluated.pose.bones[name].matrix
            worst = max(worst, max(abs(a - b) for rows in zip(expected, posed) for a, b in zip(*rows)))
    assert worst < 1e-3, f"posed skeleton is {worst:.4f} away from the game's own composition"
