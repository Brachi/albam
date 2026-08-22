import os

import bpy
import pytest

R2_PROTOCOL_PREFIX = "r2://"

# app_id -> the HexnFS instance already mounted as a VFS root this session -
# add_fs_root() must only run once per app_id (it always creates a new root;
# node ids are app_id::relative_path only, not scoped per-root, so adding
# the same game folder twice would create ambiguous duplicate entries). See
# tests/mtfw/conftest.py's game_fs_root, which this mirrors.
_GAME_FS_INSTANCES = {}


def _game_dirs(pytestconfig):
    # Reuses the shared --game-dir option (see tests/conftest.py). A third
    # ("::"-joined) segment is reng-only and simply ignored here, same as
    # tests/mtfw/conftest.py.
    parsed = {}
    for app_id_and_dir in pytestconfig.getoption("game_dir") or []:
        app_id, value, *_reng_only = app_id_and_dir.split("::")
        parsed[app_id] = value
    return parsed


@pytest.fixture(scope="session")
def game_fs_root(pytestconfig, local_app_id):
    """
    Mounts a VFS root for local_app_id via HexnFS (once per session, cached
    in _GAME_FS_INSTANCES) - the same mechanism "Add Folder" uses in the UI
    for a whole game install/folder. Returns the HexnFS instance itself, so
    callers can resolve_hashes() against the exact same tree that got
    mounted into the VFS.

    Source is explicit in --game-dir's value, never inferred: a local
    directory path. No --game-dir for this app_id skips outright; HexnFS
    has no S3/R2 backend (unlike MTFW_FS/ReenFS), so an "r2://" value skips
    with a clear message instead of failing.
    """
    from albam.engines.hexn.fs import HexnFS

    if local_app_id not in _GAME_FS_INSTANCES:
        value = _game_dirs(pytestconfig).get(local_app_id)
        if not value:
            pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")
        elif value.startswith(R2_PROTOCOL_PREFIX):
            pytest.skip(f"--game-dir={local_app_id}::{value}: HexnFS has no S3/R2 backend")
        elif not os.path.isdir(value):
            pytest.skip(f"--game-dir={local_app_id}::{value} does not exist")
        else:
            game_fs = HexnFS(value)

        bpy.context.scene.albam.apps.app_selected = local_app_id
        vfs = bpy.context.scene.albam.vfs
        vfs.add_fs_root(local_app_id, game_fs, display_name=f"{local_app_id}-local")
        _GAME_FS_INSTANCES[local_app_id] = game_fs

    return _GAME_FS_INSTANCES[local_app_id]
