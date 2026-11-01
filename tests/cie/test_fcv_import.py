"""An RE4UHD motion (.fcv) bakes onto an imported armature the way the game
poses it (issue #268).

The one thing a literal reading of the keys gets wrong is the limbs: the
translation keyed on a leg chain's end joint is where the toe goes, in model
space, and the solver bends the leg to put it there (see
albam/engines/cie/animation.py and structs/re4-uhd-fcv.ksy). So the check is
that the baked toe lands on that point while the leg keeps its length.
"""
import json
import os

import bpy
import pytest
from mathutils import Matrix, Vector

from albam.lib import fs_registry
from tests.conftest import close_new_fs_roots, remove_new_vfs_roots, vfs_root_names
from tests.cie.lfs_paths import resolve_archive_hashes
from tests.cie.test_bin_serialization import _is_mesh_bin

# Committed, hash-only, catalog-verified archives, same pattern as the other
# cie datasets. Every entry has to be a character archive holding a model
# with a skeleton and motions with leg IK chains.
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "fcv_import_hashes.json")
with open(DATASET_PATH) as f:
    FCV_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in FCV_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in FCV_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed. CI-safe."""
    for entry in FCV_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        assert entry["archive_path_hash"] in catalog


@pytest.fixture
def _clean_scene():
    before = fs_registry.keys()
    before_roots = vfs_root_names()
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    remove_new_vfs_roots(before_roots)
    close_new_fs_roots(before)


def _leg_chain_motion(entries, parse):
    """The first motion with a leg chain (kind 0x20 without 0x80) whose
    end joint is keyed with a target, and no root rotation, so the target
    only has to be offset by the root's position to be in armature space."""
    for vfile in entries:
        try:
            fcv = parse(vfile.get_bytes())
        except Exception:
            continue
        kinds = {j.parts_no: j.info.kind for j in fcv.joints}
        if 0x40 in kinds.values() or fcv.max_frame < 10:
            continue
        for joint in fcv.joints:
            kind = joint.info.kind
            if kind != 0x01 and kind & 0x20 and not kind & 0x80:
                effector = joint.parts_no + 2
                target = next((j for j in fcv.joints
                               if j.parts_no == effector and j.info.kind & 0x04), None)
                if target is not None:
                    return vfile, fcv, joint.parts_no, target
    return None


def test_leg_ik_puts_the_toe_on_the_keyed_target(game_root, local_app_id, local_archive_path_hash,
                                                 _clean_scene):
    from albam.engines.cie.animation import (
        GAME_TO_BLENDER, KIND_ROOT_POSITION, _axes_value, _parse_fcv)
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]
    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)
    entries = [vf for vf in vfs.file_list
               if vf.tree_node.root_id == root.name and not vf.is_root]

    model = next(vf for vf in entries
                 if vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes()))
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    # Other test files in the same worker can leave armatures behind (an
    # MT Framework one shares no bone layout with this one), so take the
    # armature this import deforms its mesh with, and start it from rest.
    bpy.context.scene.albam.import_options_bin.shared_armature = None
    objects_before = set(bpy.data.objects)
    vfs.file_list_selected_index = vfs.file_list.find(model.name)
    blender_registry.import_registry[(local_app_id, "bin")](model, bpy.context)
    armatures = {m.object for ob in set(bpy.data.objects) - objects_before if ob.type == 'MESH'
                 for m in ob.modifiers if m.type == 'ARMATURE' and m.object is not None}
    assert len(armatures) == 1, [ob.name for ob in armatures]
    armature = armatures.pop()
    for pose_bone in armature.pose.bones:
        pose_bone.matrix_basis = Matrix.Identity(4)

    found = _leg_chain_motion([vf for vf in entries if vf.display_name.lower().endswith(".fcv")],
                              _parse_fcv)
    assert found, "this archive should hold a motion with a keyed leg chain"
    vfile, fcv, chain_root, target_joint = found
    root_position = next((j for j in fcv.joints if j.info.kind == KIND_ROOT_POSITION), None)

    bpy.context.scene.albam.import_options_fcv.armature = armature
    blender_registry.import_registry[(local_app_id, "fcv")](vfile, bpy.context)
    action = armature.animation_data.action
    assert action is not None and tuple(action.frame_range) == (1.0, fcv.max_frame + 1.0)

    bones = armature.pose.bones
    thigh, knee, ankle, toe = (bones[str(chain_root + i)] for i in range(4))
    rest_lengths = [(b.bone.head_local - b.parent.bone.head_local).length for b in (knee, ankle)]
    for frame in range(0, fcv.max_frame + 1, max(1, fcv.max_frame // 5)):
        bpy.context.scene.frame_set(frame + 1)
        offset = Vector()
        if root_position is not None:
            offset = _axes_value(root_position, frame) - _axes_value(root_position, 0)
        expected = GAME_TO_BLENDER @ Matrix.Translation(offset) @ _axes_value(target_joint, frame)
        assert (toe.head - expected).length < 1e-3, f"frame {frame}"
        lengths = [(b.head - b.parent.head).length for b in (knee, ankle)]
        assert lengths == pytest.approx(rest_lengths, abs=1e-4), f"frame {frame}"
