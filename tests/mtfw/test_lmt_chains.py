"""A limb chain's goal is a position in model space, not an offset from rest.

An .lmt does not store a finished pose for a limb. A track on the chain's root
carries a `joint_type`, the joint just past the root is keyed by nothing at all,
and the joint at the end of the chain carries a position channel which is the
goal that missing joint is solved from.

That goal is the end joint's own position in model space. Reading it instead as
an offset from where that joint rests is nearly harmless for a foot, which
rests close to the origin, and catastrophic for a hand, which rests at chest
height: the goal lands a metre above the character's head, no arm can reach it,
and the solver just points the limb at it.

A three-joint chain pins the space down exactly. Only the middle joint's
rotation can move the end joint, so the distance from the middle joint to the
goal must equal the last rest segment, with no freedom anywhere. A goal in the
wrong space misses by most of a limb.
"""
import json
import os

import bpy
import pytest

from tests.mtfw.conftest import action_fcurves
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# pl00action.lmt is the one sampled file that declares three-joint chains - it
# carries them in 5 of its 111 blocks, on the arms.
DATASET = [
    {"app_id": "re5", "mod_path_hash": "5d45d4682b062d49", "lmt_path_hash": "1cc34f3b754528ea"},
]


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames and
            "local_lmt_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash", "local_lmt_path_hash")
        argvalues = [(d["app_id"], d["mod_path_hash"], d["lmt_path_hash"]) for d in DATASET]
        ids = [f"{d['app_id']}-{d['lmt_path_hash']}" for d in DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed. CI-safe."""
    for entry in DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        for key in ("mod_path_hash", "lmt_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}")


@pytest.fixture(scope="session")
def chain_rig(game_fs_root, local_app_id, local_mod_path_hash, local_lmt_path_hash):
    bpy.context.scene.albam.apps.app_selected = local_app_id
    resolved = resolve_hashes(game_fs_root, {local_mod_path_hash, local_lmt_path_hash})

    assert bpy.context.scene.albam.vfs.select_vfile(
        local_app_id, resolved[local_mod_path_hash].lstrip("/"))
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest].bl_object
    assert armature and armature.type == "ARMATURE"
    bpy.context.scene.albam.import_options_lmt.armature = armature

    assert bpy.context.scene.albam.vfs.select_vfile(
        local_app_id, resolved[local_lmt_path_hash].lstrip("/"))
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    actions = [a for a in bpy.data.actions if a.name.startswith(f"{armature.name}.")]
    assert actions
    return armature, actions


def test_chain_goal_is_the_joints_own_position(chain_rig):
    from albam.engines.mtfw.bone import get_anim_retarget, get_chain_length, get_chain_target

    armature, actions = chain_rig
    app_id = armature.albam_asset.app_id
    by_anim_id = {}
    for pose_bone in armature.pose.bones:
        anim_id = get_anim_retarget(pose_bone, app_id)
        if anim_id and "_" not in anim_id:
            by_anim_id[anim_id] = pose_bone.bone

    exact = []
    for control in armature.pose.bones:
        if not get_chain_target(control, app_id) or get_chain_length(control, app_id) != 2:
            continue  # only the exactly determined chains pin the space down
        target_id = int(get_anim_retarget(control, app_id).split("_")[0])
        middle, target = by_anim_id.get(str(target_id - 1)), by_anim_id.get(str(target_id))
        if middle is None or target is None:
            continue
        exact.append((control.name, middle.name,
                      (target.head_local - middle.head_local).length))
    assert exact, "expected this file to declare a three-joint chain"

    checked = 0
    for action in actions:
        keyed = {
            fcurve.data_path.split('"')[1]
            for fcurve in action_fcurves(action)
            if 'pose.bones["' in fcurve.data_path
        }
        if not any(name in keyed for name, _, _ in exact):
            continue  # this block declares no such chain
        armature.animation_data.action = action
        slots = getattr(action, "slots", None)
        if slots:
            armature.animation_data.action_slot = next(
                (s for s in slots if s.target_id_type == "OBJECT"), slots[0])
        frames = sorted({
            int(round(kp.co[0]))
            for fcurve in action_fcurves(action)
            for kp in fcurve.keyframe_points
        })
        for frame in frames:
            bpy.context.scene.frame_set(frame)
            evaluated = armature.evaluated_get(bpy.context.evaluated_depsgraph_get())
            for control_name, middle_name, segment in exact:
                if control_name not in keyed:
                    continue
                goal = evaluated.pose.bones[control_name].matrix.to_translation()
                middle = evaluated.pose.bones[middle_name].matrix.to_translation()
                assert (goal - middle).length == pytest.approx(segment, abs=1e-3), (
                    f"{action.name} frame {frame}: {control_name} sits "
                    f"{(goal - middle).length:.4f} from {middle_name}, but the joint "
                    f"it drives is fixed at {segment:.4f} - the goal is in the wrong space"
                )
                checked += 1
    assert checked, "no posed goal was measured"


@pytest.fixture(scope="session")
def reimported_actions(chain_rig, game_fs_root, local_app_id, local_lmt_path_hash):
    """The actions a second import of the same .lmt onto the same rig produces.

    Shuffling animations means loading more than one .lmt onto a character, and
    the control bones and their constraints survive the first import. What must
    survive with them is the bookkeeping that lets a later block say its chain
    is inactive.
    """
    armature, first_actions = chain_rig
    resolved = resolve_hashes(game_fs_root, {local_lmt_path_hash})
    bpy.context.scene.albam.import_options_lmt.armature = armature

    before = set(bpy.data.actions)
    assert bpy.context.scene.albam.vfs.select_vfile(
        local_app_id, resolved[local_lmt_path_hash].lstrip("/"))
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    return armature, [a for a in bpy.data.actions if a not in before]


def test_a_second_import_still_keys_its_chains(reimported_actions):
    """A constraint the rig already carries is still keyed off where unused.

    The constraint belongs to the rig for good, but the record of which
    constraint serves which chain is rebuilt per file. Lose it and the second
    file's actions key no influence at all, so every chain keeps solving
    towards a goal those blocks never move - the limb is dragged to the
    control bone's rest position for the whole animation.
    """
    armature, actions = reimported_actions
    assert actions, "expected the second import to create its own actions"

    influence_paths = {
        f'pose.bones["{bone.name}"].constraints["{constraint.name}"].influence'
        for bone in armature.pose.bones
        for constraint in bone.constraints
        if constraint.type == "IK"
    }
    assert influence_paths, "expected the rig to carry IK constraints"

    keyed = {
        fcurve.data_path
        for action in actions
        for fcurve in action_fcurves(action)
    }
    assert influence_paths & keyed, (
        "no action from the second import keys any chain's influence")
