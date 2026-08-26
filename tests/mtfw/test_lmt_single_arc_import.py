"""
Imports a .mod and a .lmt each from its own individually-mounted single
.arc (ArcFS + add_fs_root() - the same mechanism the UI's "Add Files"
action uses for a standalone .arc), rather than the whole-game MTFW_FS root
every other LMT test mounts via game_fs_root (see tests/mtfw/conftest.py).
That single-.arc mount path is otherwise only exercised by
test_arc_fs.py-style tests, never through an LMT import - this file closes
that gap.

Deliberately doesn't depend on game_fs_root: VFS node ids are
app_id::relative_path only, not scoped per mounted root (see
game_fs_root's own docstring), so mounting the whole game root under the
same app_id these two files' own .arcs get mounted under would create
ambiguous duplicate entries for the very same paths. local_game_fs below
builds its own private MTFW_FS purely to resolve hashes to real paths - it
is never itself added to the VFS.
"""
import json
import os

import bpy
import pytest

from tests.mtfw.conftest import R2_PROTOCOL_PREFIX, _game_dirs
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - not selectable via --mtfw-dataset like the rest
# of tests/mtfw/*.py. Every hash here must be a subset of that app_id's
# committed tests/mtfw/datasets/<app_id>_catalog.json - see
# test_dataset_hashes_are_in_catalog below, which enforces it.
LMT_SINGLE_ARC_IMPORT_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "lmt_single_arc_import_hashes.json"
)
with open(LMT_SINGLE_ARC_IMPORT_DATASET_PATH) as f:
    LMT_SINGLE_ARC_IMPORT_DATASET = json.load(f)


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
    real virtual paths and each path's containing .arc's real absolute
    location on disk (via origin_absolute_path()) - never mounted into the
    VFS itself (see module docstring for why).
    """
    from albam.engines.mtfw.arc_fs import MTFW_FS

    value = _game_dirs(pytestconfig).get(local_app_id)
    if not value:
        pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")
    elif value.startswith(R2_PROTOCOL_PREFIX):
        pytest.skip(
            "test_lmt_single_arc_import needs a local game root - ArcFS opens a plain "
            "local file path, not an S3/R2 key"
        )
    elif not os.path.isdir(value):
        pytest.skip(f"--game-dir={local_app_id}::{value} does not exist")
    return MTFW_FS(value)


@pytest.fixture(scope="session")
def single_arc_import_local(local_game_fs, local_app_id, local_mod_path_hash, local_lmt_path_hash):
    from albam.engines.mtfw.arc_fs import ArcFS

    bpy.context.scene.albam.apps.app_selected = local_app_id
    vfs = bpy.context.scene.albam.vfs

    resolved = resolve_hashes(local_game_fs, {local_mod_path_hash, local_lmt_path_hash})
    mod_virtual_path = resolved[local_mod_path_hash]
    lmt_virtual_path = resolved[local_lmt_path_hash]
    mod_arc_abs_path = local_game_fs.origin_absolute_path(mod_virtual_path)
    lmt_arc_abs_path = local_game_fs.origin_absolute_path(lmt_virtual_path)
    assert mod_arc_abs_path, "expected the .mod to live packed inside an .arc, not loose on disk"
    assert lmt_arc_abs_path, "expected the .lmt to live packed inside an .arc, not loose on disk"

    # Two separate single-.arc roots under the same app_id - safe because
    # their internal paths (pawn/... vs id/figdata/...) don't collide.
    mod_arc_fs = ArcFS(mod_arc_abs_path)
    vfs.add_fs_root(local_app_id, mod_arc_fs, display_name="single-arc-mod")
    vfile_mod = vfs.select_vfile(local_app_id, mod_virtual_path.lstrip("/"))
    assert vfile_mod
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    # exportable.file_list accumulates across every import in this session -
    # grab the entry just created, not "the first armature in the scene".
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == 'ARMATURE'
    bpy.context.scene.albam.import_options_lmt.armature = armature

    lmt_arc_fs = ArcFS(lmt_arc_abs_path)
    vfs.add_fs_root(local_app_id, lmt_arc_fs, display_name="single-arc-lmt")
    vfile_lmt = vfs.select_vfile(local_app_id, lmt_virtual_path.lstrip("/"))
    assert vfile_lmt
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    latest_lmt = len(bpy.context.scene.albam.exportable.file_list) - 1
    lmt_entry = bpy.context.scene.albam.exportable.file_list[latest_lmt]
    return armature, lmt_entry


def test_single_frame_pose_action_applied(single_arc_import_local, local_app_id):
    """fig01.lmt is a static, single-frame pose, not a motion clip: exactly
    one of its animation blocks should actually carry data (the rest are
    placeholder empties - see load_lmt()'s `if block.offset == 0: continue`),
    and that one block's num_frames should be 1, with every one of its
    fcurves holding exactly one keyframe at frame 1 (_create_blender_action
    keys at frame_index + 1).

    load_lmt() only wires the action up as armature.animation_data.action
    for Blender 5+ (via _get_action_channels()) - on
    Blender 4.x it stops at animation_data_create() and leaves assigning
    the action up to the caller (see custom_props.action below), which is
    exactly what applying this pose for a render requires doing by hand.
    """
    armature, lmt_entry = single_arc_import_local
    bl_object = lmt_entry.bl_object
    assert bl_object

    anim_blocks = [c for c in bl_object.children_recursive if c.type == "EMPTY"]
    assert anim_blocks

    populated = []
    for block in anim_blocks:
        custom_props = block.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
        if custom_props.ofs_frame != 0 and custom_props.action:
            populated.append((block, custom_props))

    assert len(populated) == 1, (
        f"expected fig01.lmt (a single static pose) to produce exactly one populated "
        f"animation block out of {len(anim_blocks)}, got {len(populated)}"
    )
    _block, custom_props = populated[0]
    assert custom_props.num_frames == 1

    action = custom_props.action
    assert action.fcurves
    for fcurve in action.fcurves:
        assert len(fcurve.keyframe_points) == 1
        assert fcurve.keyframe_points[0].co[0] == 1

    # animation_data_create() is always called for a populated block (see
    # load_lmt()), independent of the channel container above.
    assert armature.animation_data is not None
