import os

import bpy
import pytest


R2_PROTOCOL_PREFIX = "r2://"

# app_id -> the MTFW_FS instance already mounted as a VFS root this session -
# add_fs_root() must only run once per app_id (it always creates a new root;
# node ids are app_id::relative_path only, not scoped per-root, so adding
# the same game folder twice would create ambiguous duplicate entries).
_GAME_FS_INSTANCES = {}


def _game_dirs(pytestconfig):
    # Already validated (well-formed "<app-id>::<value>[::<extra>]", once, at
    # startup) by tests/conftest.py's pytest_configure - see there. <value>
    # is either a local directory path, or an explicit
    # "r2://<bucket>/<prefix>" value (see tests.mtfw.r2_config.resolve_r2_source)
    # selecting the R2 backend - never inferred from whether a local path
    # happens to exist. A third segment is reng-only (its own path-list -
    # see tests/reng/conftest.py) and simply ignored here.
    parsed = {}
    for app_id_and_dir in pytestconfig.getoption("game_dir") or []:
        app_id, value, *_reng_only = app_id_and_dir.split("::")
        parsed[app_id] = value
    return parsed


@pytest.fixture(scope="session")
def game_fs_root(pytestconfig, local_app_id):
    """
    Mounts a VFS root for local_app_id via MTFW_FS (once per session, cached
    in _GAME_FS_INSTANCES) - the same mechanism "Add Folder" uses in the UI
    for a whole game install. Returns the MTFW_FS instance itself, so
    callers can resolve_hashes() against the exact same tree that got
    mounted into the VFS.

    Source is explicit in --game-dir's value, never inferred: a local path,
    or an explicit "r2://<bucket>/<prefix>" (see
    tests.mtfw.r2_config.resolve_r2_source for the R2/CI details). No
    --game-dir for this app_id skips outright.

    Scanning + flattening a full local game install's tree can take a while
    (a real RE5 install has ~1200 archives) - that cost is paid once per
    app_id per session, not per test.
    """
    from albam.engines.mtfw.arc_fs import MTFW_FS
    from tests.mtfw.r2_config import resolve_r2_source

    if local_app_id not in _GAME_FS_INSTANCES:
        value = _game_dirs(pytestconfig).get(local_app_id)
        if not value:
            pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")
        elif value.startswith(R2_PROTOCOL_PREFIX):
            r2_kwargs = resolve_r2_source(value)
            if r2_kwargs is None:
                pytest.skip(
                    f"--game-dir={local_app_id}::{value} requested but R2 isn't configured "
                    f"(empty bucket, missing s3 extras, or missing credentials - see "
                    f".env.example)"
                )
            game_fs = MTFW_FS.from_s3(**r2_kwargs)
        elif not os.path.isdir(value):
            pytest.skip(f"--game-dir={local_app_id}::{value} does not exist")
        else:
            game_fs = MTFW_FS(value)

        bpy.context.scene.albam.apps.app_selected = local_app_id
        vfs = bpy.context.scene.albam.vfs
        vfs.add_fs_root(local_app_id, game_fs, display_name=f"{local_app_id}-local")
        _GAME_FS_INSTANCES[local_app_id] = game_fs

    return _GAME_FS_INSTANCES[local_app_id]


def import_export(local_app_id, local_path):
    """Select local_path (already resolved from a committed hash, and
    already mounted into the VFS via game_fs_root) and run it through the
    real Blender import_vfile()/export() operators - the shared
    "select, import, export" step every *_local round-trip fixture needs.
    Returns the source vfile; callers fetch whatever exported vfile(s) they
    need afterward from bpy.context.scene.albam.exported, since what comes
    out varies (a straight copy for a standalone file, but also an
    accompanying .mrl alongside a mod).
    """
    vfs = bpy.context.scene.albam.vfs
    try:
        vfile = vfs.select_vfile(local_app_id, local_path)
    except KeyError:
        pytest.skip(f"{local_path!r} not found under --game-dir for app_id={local_app_id!r}")

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}
    return vfile


def import_vfile(local_app_id, local_path):
    """Select local_path (already resolved from a committed hash, and
    already mounted into the VFS via game_fs_root) and run it through the
    real Blender import_vfile() operator.

    The import-only half of import_export() above, for the tests that only
    care about what a file turns into in Blender - most notably apps albam
    can import but not yet export.
    """
    vfs = bpy.context.scene.albam.vfs
    try:
        vfile = vfs.select_vfile(local_app_id, local_path)
    except KeyError:
        pytest.skip(f"{local_path!r} not found under --game-dir for app_id={local_app_id!r}")

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    return vfile


def clear_scene():
    """Drops everything a previous import left behind.

    Imports accumulate in bpy.data otherwise, so a per-model assertion like
    "this model built some materials" would really be reading the sum of
    every model imported before it - and a whole game's worth of models in
    one session would exhaust memory. Deleting objects only unlinks the
    meshes/images they used; orphans_purge is what actually frees them.
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)
