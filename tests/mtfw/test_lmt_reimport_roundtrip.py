"""
Proves a full LMT round trip through the real Blender import/export
operator stack, not just Kaitai-level byte parsing:

  1. Import a character model + a single-frame pose animation.
  2. Hand-edit a handful of bones' rotation_quaternion keyframes on the
     already-imported action - large, arbitrary values, no attempt at
     anatomical plausibility, just something big and easy to verify.
  3. Export the edited pose back to .lmt bytes via bpy.ops.albam.export().
  4. Stage those bytes as a real file under a fresh, single-file OSFS root
     and reimport them via bpy.ops.albam.import_vfile() - the actual import
     operator, not by parsing the bytes - onto a second, independently imported
     instance of the same character.
  5. Compare the reimported pose's bone rotations against the edited values.

test_lmt_custom_animation.py already proves an edited keyframe survives
export by parsing the exported bytes directly; this
file closes the remaining gap of proving those bytes also come back in
through the real VFS + import operator and produce a matching pose on an
independent armature.

Reuses test_lmt_single_arc_import.py's dataset and single-.arc mounting
approach (rather than the whole-game MTFW_FS root every other LMT test
mounts via game_fs_root) since it needs the same two files' actual
containing .arcs mounted individually, plus a private local_game_fs used
only to resolve hashes - never itself added to the VFS.
"""
import json
import os
from math import radians

import bpy
import pytest
from mathutils import Euler, Quaternion

from tests.mtfw.conftest import R2_PROTOCOL_PREFIX, _game_dirs, action_fcurves
from tests.mtfw.r2_config import resolve_r2_source
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Same committed dataset as test_lmt_single_arc_import.py - one re5
# model + pose pair, hash-only, verified against the app_id's catalog by
# test_dataset_hashes_are_in_catalog below.
LMT_SINGLE_ARC_IMPORT_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "lmt_single_arc_import_hashes.json"
)
with open(LMT_SINGLE_ARC_IMPORT_DATASET_PATH) as f:
    LMT_SINGLE_ARC_IMPORT_DATASET = json.load(f)

# MT Framework's shared numeric anim-bone ids (see animation.py's
# _create_bone_mapping docstring) that this dataset's pose already animates
# rotation_quaternion on - happen to land on the spine, the neck, and both
# upper arms. Values are arbitrary Euler angles, picked only to be large and
# obviously different from the resting pose.
EDITED_BONES_AND_EULERS = {
    "2": (radians(60), radians(20), 0),
    "6": (radians(-40), 0, radians(30)),
    "50": (0, radians(100), 0),
    "77": (0, radians(-100), 0),
}


def _euler_to_positive_w_quat(euler_xyz):
    """
    re5/v51's single-frame rotation encoding (LMTKeyFrames.encode_framedata's
    kf_type=4 path, Lmt.Quat3Frame) stores only x/y/z and reconstructs w on
    decode as +sqrt(1 - x^2 - y^2 - z^2) (see LMTKeyFrames.restore_w). The
    encoder canonicalizes to that form itself (LMTKeyFrames.canonicalize),
    so a w < 0 rotation does survive - but it comes back as its negation,
    which the component-wise comparison below would read as a mismatch.
    Forcing w >= 0 up front keeps the expected values in the same form the
    round trip returns; q and -q are the same rotation, so nothing is lost.
    """
    quat = Euler(euler_xyz, "XYZ").to_quaternion()
    if quat.w < 0:
        quat = Quaternion((-quat.w, -quat.x, -quat.y, -quat.z))
    return quat


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames and
            "local_lmt_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash", "local_lmt_path_hash")
        argvalues = [
            (d["app_id"], d["mod_path_hash"], d["lmt_path_hash"])
            for d in LMT_SINGLE_ARC_IMPORT_DATASET
        ]
        ids = [f"{d['app_id']}-{d['lmt_path_hash']}" for d in LMT_SINGLE_ARC_IMPORT_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by LMT_SINGLE_ARC_IMPORT_DATASET must be a subset of that app_id's
    committed catalog, so this file only ever exercises real, unmodified,
    hash-verified game files. CI-safe: reads two committed JSON files, no
    --game-dir needed.
    """
    for entry in LMT_SINGLE_ARC_IMPORT_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        for key in ("mod_path_hash", "lmt_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}"
            )


@pytest.fixture(scope="session")
def local_game_fs(pytestconfig, local_app_id):
    """
    A bare MTFW_FS, used only to resolve this file's committed hashes to
    real virtual paths and to each path's containing .arc - never mounted
    into the VFS itself (see module docstring for why).
    """
    from albam.engines.mtfw.arc_fs import MTFW_FS

    value = _game_dirs(pytestconfig).get(local_app_id)
    if not value:
        pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")
    elif value.startswith(R2_PROTOCOL_PREFIX):
        r2_kwargs = resolve_r2_source(value)
        if r2_kwargs is None:
            pytest.skip(f"--game-dir={local_app_id}::{value} requested but R2 isn't configured")
        return MTFW_FS.from_s3(**r2_kwargs)
    elif not os.path.isdir(value):
        pytest.skip(f"--game-dir={local_app_id}::{value} does not exist")
    return MTFW_FS(value)


def _populated_block(bl_object, app_id):
    anim_blocks = [c for c in bl_object.children_recursive if c.type == "EMPTY"]
    populated = [
        block for block in anim_blocks
        if block.albam_custom_properties.get_custom_properties_for_appid(app_id).ofs_frame != 0
    ]
    assert len(populated) == 1, (
        f"expected exactly one populated animation block, got {len(populated)}"
    )
    return populated[0]


def test_reimport_through_import_operator(
    tmp_path, mount_vfs_root, local_game_fs, local_app_id,
    local_mod_path_hash, local_lmt_path_hash
):
    from albam.engines.mtfw.structs.lmt import Lmt
    from albam.lib.kaitai_utils import parse
    from fs.osfs import OSFS

    app_id = local_app_id
    bpy.context.scene.albam.apps.app_selected = app_id
    vfs = bpy.context.scene.albam.vfs

    resolved = resolve_hashes(local_game_fs, {local_mod_path_hash, local_lmt_path_hash})
    mod_virtual_path = resolved[local_mod_path_hash]
    lmt_virtual_path = resolved[local_lmt_path_hash]
    # The ArcFS each file already lives in, rather than building a new one
    # from an absolute path: MTFW_FS opens its archives with an opener that
    # matches whichever backend it was mounted from, so reusing the instance
    # keeps this working over S3/R2 as well as local disk.
    mod_arc_fs = local_game_fs._owning_arc_fs(mod_virtual_path)
    lmt_arc_fs = local_game_fs._owning_arc_fs(lmt_virtual_path)
    assert mod_arc_fs, "expected the .mod to live packed inside an .arc, not loose"
    assert lmt_arc_fs, "expected the .lmt to live packed inside an .arc, not loose"
    mod_rel_path = mod_virtual_path.lstrip("/")
    lmt_rel_path = lmt_virtual_path.lstrip("/")

    # --- Character A: import model + pose ---
    mount_vfs_root(app_id, mod_arc_fs, "roundtrip-mod")
    assert vfs.select_vfile(app_id, mod_rel_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_mod_a = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature_a = bpy.context.scene.albam.exportable.file_list[latest_mod_a].bl_object
    assert armature_a and armature_a.type == "ARMATURE"
    bpy.context.scene.albam.import_options_lmt.armature = armature_a

    mount_vfs_root(app_id, lmt_arc_fs, "roundtrip-lmt")
    assert vfs.select_vfile(app_id, lmt_rel_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_lmt_a = len(bpy.context.scene.albam.exportable.file_list) - 1
    lmt_entry_a = bpy.context.scene.albam.exportable.file_list[latest_lmt_a]
    lmt_bl_obj_a = lmt_entry_a.bl_object
    assert lmt_bl_obj_a

    block_a = _populated_block(lmt_bl_obj_a, app_id)
    custom_props_a = block_a.albam_custom_properties.get_custom_properties_for_appid(app_id)
    action_a = custom_props_a.action
    assert action_a and action_fcurves(action_a)

    # load_lmt() stops at animation_data_create() and never assigns the
    # action on any Blender version, so applying/editing the pose requires
    # this assignment by hand (see test_lmt_single_arc_import.py).
    armature_a.animation_data_create()
    armature_a.animation_data.action = action_a
    bpy.context.scene.frame_set(1)

    bone_names_with_rotation = {
        fc.data_path.split('"')[1] for fc in action_fcurves(action_a)
        if fc.data_path.startswith('pose.bones["') and "rotation_quaternion" in fc.data_path
    }

    # Hand-edit: set a large, obviously-different rotation on each target
    # bone, keyframed onto frame 1 of the same action _generate_track_from_action
    # will read on export (this dataset's pose is a single static frame -
    # see test_lmt_single_arc_import.py - so frame 1 is the only frame
    # there is).
    edited_quats = {}
    for bone_name, euler_xyz in EDITED_BONES_AND_EULERS.items():
        assert bone_name in bone_names_with_rotation, (
            f"bone {bone_name!r} has no existing rotation_quaternion fcurve on "
            f"{action_a.name!r} - dataset/skeleton assumption changed"
        )
        pose_bone = armature_a.pose.bones[bone_name]
        quat = _euler_to_positive_w_quat(euler_xyz)
        pose_bone.rotation_quaternion = quat
        pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=1)
        edited_quats[bone_name] = quat.copy()

    custom_props_a.generate_new = True
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_lmt_a
    assert bpy.ops.albam.export() == {"FINISHED"}

    vfile_lmt_exported = bpy.context.scene.albam.exported.select_vfile(app_id, lmt_rel_path)
    assert vfile_lmt_exported
    exported_bytes = vfile_lmt_exported.get_bytes()

    # Sanity check the exported bytes actually parse before trusting them for
    # a real reimport - a malformed export should fail loudly here, not
    # produce a confusing failure three steps later.
    from albam.engines.mtfw.animation import APPID_VERSION_MAPPER

    parsed = parse(Lmt, exported_bytes, app_id)
    assert parsed.version == APPID_VERSION_MAPPER[app_id]
    assert any(block.offset != 0 for block in parsed.block_offsets)

    # Stage the exported bytes as a real file under a fresh, single-file OSFS
    # root. Re-mounting either source .arc a second time under the same
    # app_id would collide (VFS node ids are app_id::relative_path only, not
    # scoped per mounted root - see add_fs_root's docstring), but a
    # brand-new root with a filename that doesn't exist anywhere else has no
    # such conflict.
    reimport_dir = tmp_path / "reimport"
    reimport_dir.mkdir()
    reimport_filename = "reimport_roundtrip.lmt"
    (reimport_dir / reimport_filename).write_bytes(exported_bytes)
    reimport_fs = OSFS(str(reimport_dir))
    mount_vfs_root(app_id, reimport_fs, "roundtrip-reimport-lmt")

    # --- Character B: a second, independent instance of the same .mod.
    # Reuses the mod vfile node already mounted for character A instead of
    # re-mounting its .arc (same collision reason as above) - Blender
    # auto-suffixes the new objects (Armature.001 etc.).
    assert vfs.select_vfile(app_id, mod_rel_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_mod_b = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature_b = bpy.context.scene.albam.exportable.file_list[latest_mod_b].bl_object
    assert armature_b and armature_b.type == "ARMATURE"
    assert armature_b is not armature_a

    # --- Reimport the exported .lmt through the real import operator, onto
    # character B.
    bpy.context.scene.albam.import_options_lmt.armature = armature_b
    assert vfs.select_vfile(app_id, reimport_filename)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_lmt_b = len(bpy.context.scene.albam.exportable.file_list) - 1
    lmt_entry_b = bpy.context.scene.albam.exportable.file_list[latest_lmt_b]
    lmt_bl_obj_b = lmt_entry_b.bl_object
    assert lmt_bl_obj_b

    block_b = _populated_block(lmt_bl_obj_b, app_id)
    custom_props_b = block_b.albam_custom_properties.get_custom_properties_for_appid(app_id)
    action_b = custom_props_b.action
    assert action_b and action_fcurves(action_b)

    armature_b.animation_data_create()
    armature_b.animation_data.action = action_b
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()

    # The actual proof: character B's reimported pose bones must carry the
    # same rotations hand-edited on character A, within the precision LMT's
    # on-disk encoding preserves (re5/v51's single-frame Quat3Frame format
    # stores plain, unquantized 32-bit floats for x/y/z - see
    # _euler_to_positive_w_quat's docstring - so this is a tight tolerance,
    # not a loose one hiding a real mismatch).
    TOLERANCE = 1e-3
    for bone_name, expected_quat in edited_quats.items():
        actual_quat = armature_b.pose.bones[bone_name].rotation_quaternion
        diffs = [abs(e - a) for e, a in zip(expected_quat, actual_quat)]
        assert max(diffs) < TOLERANCE, (
            f"bone {bone_name!r}: expected {tuple(expected_quat)}, "
            f"got {tuple(actual_quat)} (max diff {max(diffs)})"
        )
