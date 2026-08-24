import json
import math
import os

import bpy
import pytest

from tests.mtfw.scripts.catalog_paths import resolve_hashes

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


def _iter_clips(anims):
    from albam.engines.hexn.animation import parse_clip_name

    offset = 0
    for file_info in anims.files_info:
        clip_bytes = anims.buffer_chunks[offset:offset + file_info.size]
        offset += file_info.size
        clip_path, skeleton_name = parse_clip_name(file_info.name)
        yield file_info, clip_bytes, clip_path, skeleton_name


def test_decode_clip_sane_across_dataset(game_fs_root, local_app_id, local_anims_path_hash):
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

    path = resolve_hashes(game_fs_root, {local_anims_path_hash})[local_anims_path_hash]
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

        for bone_idx, (positions, rotations) in decoded.bones.items():
            assert len(positions) == decoded.num_frames
            assert len(rotations) == decoded.num_frames
            for q in rotations:
                assert not math.isnan(q.magnitude)
                assert 0.9 < q.magnitude < 1.2  # unit quaternion, some compression slack
            for p in positions:
                assert all(not math.isnan(c) and not math.isinf(c) for c in p)

    if n_clips == 0:
        pytest.skip("empty archive in the dataset - nothing to decode")


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


def test_build_blender_action(game_fs_root, local_app_id, local_anims_path_hash):
    """build_blender_action() runs end to end against a throwaway armature
    (positional bone_names lookup - see its own docstring for why that's
    documented as an assumption) and produces finite keyframe values on
    every fcurve, for every real clip in this dataset.
    """
    from albam.engines.hexn.animation import build_blender_action, decode_clip
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    path = resolve_hashes(game_fs_root, {local_anims_path_hash})[local_anims_path_hash]
    data = game_fs_root.readbytes(path)
    anims = HexaneAnims.from_bytes(data)
    anims._read()

    armature_obj = None
    bone_names = None
    n_actions = 0
    for file_info, clip_bytes, clip_path, skeleton_name in _iter_clips(anims):
        decoded = decode_clip(clip_bytes, name=file_info.name, skeleton_name=skeleton_name)
        if armature_obj is None:
            armature_obj = _make_throwaway_armature(
                f"test-{local_anims_path_hash}", decoded.num_bones)
            bone_names = [b.name for b in armature_obj.pose.bones]

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

    if n_actions == 0:
        pytest.skip("empty archive in the dataset - nothing to build")
