"""Imports a .mod and then a .lmt onto its armature, through the real
Blender operators.

Nothing else covers importing a .lmt at all: test_lmt_parsing.py stops at
parsing the bytes. That gap let Blender 4.4's move of an action's fcurves
and groups behind its layers and slots - and 5.0's removal of the flat
Action.fcurves/Action.groups shortcuts - break load_lmt() for every app,
on the very Blender the tests run against, without a single test noticing.

Each file is mounted from its own single .arc (add_fs_root() on one ArcFS,
the mechanism the UI's "Add Files" action uses for a standalone .arc)
rather than from a whole-game MTFW_FS root, since that is how someone hits
this in practice.

Deliberately doesn't use the shared game_fs_root fixture: VFS node ids are
app_id::relative_path only, not scoped per mounted root, so mounting the
whole game root under the same app_id these two files' own .arcs get
mounted under would create ambiguous duplicate entries for the very same
paths. local_game_fs below builds its own private MTFW_FS purely to
resolve hashes to real paths - it is never itself added to the VFS.
"""
import contextlib
import json
import os

import bpy
import pytest

from tests.mtfw.conftest import R2_PROTOCOL_PREFIX, _game_dirs, action_fcurves
from tests.mtfw.r2_config import resolve_r2_source
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# import (see test_dataset_hashes_are_in_catalog below). Extend this
# directly to add more.
LMT_IMPORT_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "lmt_import_hashes.json"
)
with open(LMT_IMPORT_DATASET_PATH) as f:
    LMT_IMPORT_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames and
            "local_lmt_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash", "local_lmt_path_hash")
        argvalues = [
            (d["app_id"], d["mod_path_hash"], d["lmt_path_hash"])
            for d in LMT_IMPORT_DATASET
        ]
        ids = [f"{d['app_id']}-{d['lmt_path_hash']}" for d in LMT_IMPORT_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by LMT_IMPORT_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in LMT_IMPORT_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        for key in ("mod_path_hash", "lmt_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}"
            )


@pytest.fixture(scope="session")
def local_game_fs(pytestconfig, local_app_id):
    """A bare MTFW_FS, used only to resolve this file's committed hashes to
    real virtual paths and to each path's containing .arc on disk (via
    origin_absolute_path()) - never mounted into the VFS itself (see the
    module docstring for why).
    """
    from albam.engines.mtfw.arc_fs import MTFW_FS

    value = _game_dirs(pytestconfig).get(local_app_id)
    if not value:
        pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")
    elif value.startswith(R2_PROTOCOL_PREFIX):
        r2_kwargs = resolve_r2_source(value)
        if r2_kwargs is None:
            pytest.skip(
                f"--game-dir={local_app_id}::{value} requested but R2 isn't configured"
            )
        return MTFW_FS.from_s3(**r2_kwargs)
    elif not os.path.isdir(value):
        pytest.skip(f"--game-dir={local_app_id}::{value} does not exist")
    return MTFW_FS(value)


@pytest.fixture(scope="session")
def lmt_imported_local(local_game_fs, local_app_id, local_mod_path_hash, local_lmt_path_hash):
    bpy.context.scene.albam.apps.app_selected = local_app_id
    vfs = bpy.context.scene.albam.vfs

    resolved = resolve_hashes(local_game_fs, {local_mod_path_hash, local_lmt_path_hash})
    mod_path = resolved[local_mod_path_hash]
    lmt_path = resolved[local_lmt_path_hash]
    # The ArcFS each file already lives in, rather than building a new one
    # from a path: MTFW_FS opens its archives with a backend-appropriate
    # opener, so reusing the instance keeps this working over S3/R2 as well
    # as local disk - and CI only ever runs with an r2:// game dir.
    mod_arc = local_game_fs._owning_arc_fs(mod_path)
    lmt_arc = local_game_fs._owning_arc_fs(lmt_path)
    assert mod_arc, "expected the .mod to live packed inside an .arc, not loose"
    assert lmt_arc, "expected the .lmt to live packed inside an .arc, not loose"

    # Two separate single-.arc roots under the same app_id, which is safe
    # only because these two files' internal paths don't collide.
    vfs.add_fs_root(local_app_id, mod_arc, display_name="single-arc-mod")
    assert vfs.select_vfile(local_app_id, mod_path.lstrip("/"))
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}

    # exportable.file_list accumulates across every import in the session -
    # take the entry just created, not "the first armature in the scene".
    latest = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest].bl_object
    assert armature and armature.type == "ARMATURE"
    bpy.context.scene.albam.import_options_lmt.armature = armature

    vfs.add_fs_root(local_app_id, lmt_arc, display_name="single-arc-lmt")
    assert vfs.select_vfile(local_app_id, lmt_path.lstrip("/"))
    # The regression itself: on Blender 4.4+ this raised
    # "AttributeError: 'Action' object has no attribute 'groups'", which the
    # operator surfaces as a RuntimeError.
    result = bpy.ops.albam.import_vfile()

    # load_lmt() names every action it creates after the armature it was
    # applied to, and never assigns them, so that prefix is the only handle.
    actions = [a for a in bpy.data.actions if a.name.startswith(f"{armature.name}.")]
    latest = len(bpy.context.scene.albam.exportable.file_list) - 1
    lmt_bl_object = bpy.context.scene.albam.exportable.file_list[latest].bl_object
    yield result, armature, actions, lmt_bl_object

    # Unmount both roots again. The VFS lives in Blender's scene data, which
    # is process-global and outlives this fixture, while local_game_fs (and
    # with it the ArcFS instances mounted above) is dropped when this param
    # group tears down - leaving roots behind whose filesystem is closed.
    # Node ids are app_id::relative_path only, so any later test selecting
    # these same paths would resolve to one of those dead roots and fail with
    # fs.errors.FilesystemClosed.
    for display_name in ("single-arc-lmt", "single-arc-mod"):
        root_id = f"{local_app_id}::{display_name}"
        index = vfs.file_list.find(root_id)
        if index == -1:
            continue
        vfs.file_list_selected_index = index
        bpy.ops.albam.remove_imported()


def test_lmt_import_succeeds(lmt_imported_local):
    result, _armature, _actions, _lmt_object = lmt_imported_local
    assert result == {"FINISHED"}


def test_lmt_import_creates_actions(lmt_imported_local):
    _result, armature, actions, _lmt_object = lmt_imported_local
    assert actions, "importing the .lmt created no actions"
    assert armature.animation_data is not None


def test_lmt_import_actions_have_keyframes(lmt_imported_local):
    """Without this, an import that swallowed the error and produced empty
    actions would still pass the two tests above.
    """
    _result, _armature, actions, _lmt_object = lmt_imported_local
    for action in actions:
        fcurves = action_fcurves(action)
        assert fcurves, f"{action.name} has no fcurves"
        for fcurve in fcurves:
            assert len(fcurve.keyframe_points), f"{action.name}/{fcurve.data_path} has no keyframes"


def test_block_order_is_recorded_not_read_off_the_scene(lmt_imported_local):
    """Which slot of the file a block sits in is its identity.

    An empty slot has to stay empty and every offset in the header is written
    by position, so getting the order wrong does not produce a slightly wrong
    file - it produces one whose blocks are all in the wrong place. Export used
    to take that order from `children_recursive`, which matches only because a
    first import happens to name the objects in block order; import the same
    .lmt again in one session and Blender renumbers the duplicates, the names
    stop lining up, and the order silently changes.
    """
    from albam.engines.mtfw.animation import BLOCK_INDEX_PROP, _lmt_blocks

    _result, _armature, _actions, lmt_object = lmt_imported_local
    blocks = _lmt_blocks(lmt_object)
    assert blocks, "the .lmt produced no blocks"

    recorded = [block.get(BLOCK_INDEX_PROP) for block in blocks]
    assert None not in recorded, "a block carries no index to order it by"
    assert recorded == list(range(len(blocks))), (
        f"blocks are not in file order: {recorded[:8]}...")

    # The names are what used to carry the order, so breaking them must not
    # change it. Reversed, so name order and block order disagree everywhere.
    original_names = [block.name for block in blocks]
    try:
        for position, block in enumerate(blocks):
            block.name = f"scrambled.{len(blocks) - position:04d}"
        after = [block.get(BLOCK_INDEX_PROP) for block in _lmt_blocks(lmt_object)]
        assert after == recorded, "renaming the objects reordered the blocks"
    finally:
        for block, name in zip(blocks, original_names):
            block.name = name


@contextlib.contextmanager
def _pose_restored(armature):
    """Put the armature's pose back exactly as it was found.

    Assigning an action makes Blender write the evaluated values into the pose
    bones themselves, and taking the action away again does not undo that - the
    armature keeps the last frame it was on. Root motion moves a character
    metres from the origin, so a test that animates one and walks away leaves
    every later test measuring that pose instead of the rest one.
    """
    from mathutils import Matrix

    animation_data = armature.animation_data
    previous_action = animation_data and animation_data.action
    previous_pose = {pb.name: pb.matrix_basis.copy() for pb in armature.pose.bones}
    previous_frame = bpy.context.scene.frame_current
    try:
        yield
    finally:
        if armature.animation_data is not None:
            armature.animation_data.action = previous_action
        for pose_bone in armature.pose.bones:
            pose_bone.matrix_basis = previous_pose.get(pose_bone.name, Matrix.Identity(4))
        bpy.context.scene.frame_set(previous_frame)


def _root_motion_track_angle(action, armature):
    """How far and about what the root motion bone turns, from its own keys.

    The axis comes back in the engine's frame, the one the track is written
    against.
    """
    import math

    from mathutils import Quaternion

    from albam.engines.mtfw.animation import ROOT_MOTION_BONE_NAME

    components = {}
    for fcurve in action_fcurves(action):
        if not fcurve.data_path.endswith("].rotation_quaternion"):
            continue
        if fcurve.data_path.split('"')[1] != ROOT_MOTION_BONE_NAME:
            continue
        components[fcurve.array_index] = fcurve
    if len(components) != 4:
        return None, None, None
    frames = sorted({key.co[0] for key in components[0].keyframe_points})
    if len(frames) < 2:
        return None, None, None
    first, last = (
        Quaternion([components[i].evaluate(f) for i in range(4)]).normalized()
        for f in (frames[0], frames[-1])
    )
    net = last @ first.inverted()
    angle = math.degrees(net.angle)
    return (360 - angle if angle > 180 else angle,
            net.axis.normalized(),
            (int(frames[0]), int(frames[-1])))


def _skeleton_root_bone(armature):
    for bone in armature.data.bones:
        if str(bone.get("mtfw.anim_retarget")) == "0":
            return bone.name
    raise AssertionError("the armature carries no bone mapped to anim id 0")


def test_root_motion_turns_the_character_about_the_vertical(lmt_imported_local):
    """Root motion is a whole-character transform, rotation included.

    Two ways this has gone wrong, and one measurement rules out both. Bind the
    rotation to nothing and a block that spins the character around plays as a
    twist in place - he ends the block facing the way he started. Bind it in
    the wrong frame and he turns about the wrong axis, and a block that should
    turn him on the spot lays him on his face instead.

    So the character's own rotation is compared against the track's, carried
    over by the same (x, y, z) -> (x, -z, y) mapping a position takes. Not
    against vertical: most of these are turns on the spot, but a small number
    of blocks across the game really do turn the character about a horizontal
    axis, and a test that assumed otherwise would be asserting something the
    format does not promise.

    Both mistakes are only visible in armature space. The bone the track is
    keyed on is created pointing +Z, so its own rest orientation already
    carries the engine's axes into Blender's - which makes the value read
    straight off the fcurve the one place where neither shows up.
    """
    import math

    from mathutils import Vector

    _result, armature, actions, _lmt_object = lmt_imported_local
    root_bone = _skeleton_root_bone(armature)

    turning = []
    for action in actions:
        angle, axis, frames = _root_motion_track_angle(action, armature)
        if angle is not None and angle > 5:
            # the engine's axes into Blender's, the same mapping a position takes
            turning.append((action, angle, Vector((axis.x, -axis.z, axis.y)), frames))
    if not turning:
        pytest.skip("no block of this .lmt turns the root motion bone")

    with _pose_restored(armature):
        for action, expected, expected_axis, (first, last) in turning:
            if armature.animation_data is None:
                armature.animation_data_create()
            armature.animation_data.action = action
            slots = getattr(action, "slots", None)
            if slots:
                armature.animation_data.action_slot = slots[0]

            poses = []
            for frame in (first, last):
                bpy.context.scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                evaluated = armature.evaluated_get(depsgraph)
                poses.append(evaluated.pose.bones[root_bone].matrix.to_quaternion())

            net = poses[1] @ poses[0].inverted()
            angle = math.degrees(net.angle)
            angle = 360 - angle if angle > 180 else angle
            axis = net.axis.normalized()

            assert abs(angle - expected) < 1.0, (
                f"{action.name}: the root motion track turns {expected:.1f} deg but the "
                f"character turns {angle:.1f} deg"
            )
            # abs(): at exactly 180 degrees the sign of an axis is arbitrary
            assert abs(axis.dot(expected_axis)) > 0.999, (
                f"{action.name}: the character turns about "
                f"({axis.x:+.3f}, {axis.y:+.3f}, {axis.z:+.3f}), but the track names "
                f"({expected_axis.x:+.3f}, {expected_axis.y:+.3f}, {expected_axis.z:+.3f})"
            )


def test_root_motion_constraints_are_identities_at_rest(lmt_imported_local):
    """Adding the constraint must not move the rig on its own.

    CHILD_OF applies the target's transform relative to the inverse matrix it
    stores, so getting that matrix wrong doesn't fail loudly - it silently
    bakes the root motion bone's own rest orientation into every rig the
    moment the .lmt is imported, animated or not.
    """
    _result, armature, _actions, _lmt_object = lmt_imported_local

    constraints = [
        constraint
        for pose_bone in armature.pose.bones
        for constraint in pose_bone.constraints
        if constraint.type == "CHILD_OF"
    ]
    assert constraints, "nothing binds the rig to the root motion bone"

    from mathutils import Matrix

    with _pose_restored(armature):
        # Whatever the tests before this one left posed, measure from rest.
        if armature.animation_data is not None:
            armature.animation_data.action = None
        for pose_bone in armature.pose.bones:
            pose_bone.matrix_basis = Matrix.Identity(4)

        def evaluate():
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
            evaluated = armature.evaluated_get(depsgraph)
            return {pb.name: pb.matrix.copy() for pb in evaluated.pose.bones}

        live = evaluate()
        for constraint in constraints:
            constraint.mute = True
        try:
            muted = evaluate()
        finally:
            for constraint in constraints:
                constraint.mute = False

        worst = max((live[name].to_translation() - matrix.to_translation()).length
                    for name, matrix in muted.items())
        assert worst < 1e-5, f"the constraints move the rest pose by {worst * 100:.4f} cm"
