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
import json
import os

import bpy
import pytest

from tests.mtfw.conftest import R2_PROTOCOL_PREFIX, _game_dirs
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


def action_fcurves(action):
    """Every fcurve an action holds, whichever Blender version made it.

    The flat Action.fcurves shortcut is gone from 5.0 on - the same removal
    this file exists to catch - so reading it directly here would break the
    test exactly where it broke the code.
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
    return result, armature, actions


def test_lmt_import_succeeds(lmt_imported_local):
    result, _armature, _actions = lmt_imported_local
    assert result == {"FINISHED"}


def test_lmt_import_creates_actions(lmt_imported_local):
    _result, armature, actions = lmt_imported_local
    assert actions, "importing the .lmt created no actions"
    assert armature.animation_data is not None


def test_lmt_import_actions_have_keyframes(lmt_imported_local):
    """Without this, an import that swallowed the error and produced empty
    actions would still pass the two tests above.
    """
    _result, _armature, actions = lmt_imported_local
    for action in actions:
        fcurves = action_fcurves(action)
        assert fcurves, f"{action.name} has no fcurves"
        for fcurve in fcurves:
            assert len(fcurve.keyframe_points), f"{action.name}/{fcurve.data_path} has no keyframes"
