import os
import tempfile

import bpy
import pytest

R2_PROTOCOL_PREFIX = "r2://"

# app_id -> the ReenFS instance already mounted this session.
_REEN_FS_INSTANCES = {}

# app_id -> already mounted into bpy's VFS this session (see reng_vfs_root).
_REEN_VFS_MOUNTED = set()


def pytest_addoption(parser):
    parser.addoption(
        "--reng-mesh-import-dataset",
        choices=["full", "quick"],
        default="full",
        help="Which tier of tests/reng/datasets/mesh_import_hashes.json to run "
        "(see test_mesh_import.py) - 'full' (default) is every committed entry; "
        "'quick' is the small, category-diverse subset marked \"quick\": true in "
        "that same file, for a fast local dev loop (importing pulls in materials/"
        "textures per file, so it's much slower than parsing-only tests).",
    )


def _reen_game_dirs(pytestconfig):
    # Reuses the shared --game-dir option (see tests/conftest.py) - reng's
    # values carry an optional extra `::<path-list-source>` segment MTFW's
    # own values don't need: a .pak's file entries carry only hashes, not
    # paths, so an external candidate-path list is required to resolve
    # anything at all (see albam/engines/reng/pak_fs.py's module docstring).
    # Already validated (2 or 3 non-empty `::`-separated parts) by
    # tests/conftest.py's pytest_configure.
    parsed = {}
    for entry in pytestconfig.getoption("game_dir") or []:
        parts = entry.split("::")
        app_id, game_root = parts[0], parts[1]
        path_list_source = parts[2] if len(parts) > 2 else None
        parsed[app_id] = (game_root, path_list_source)
    return parsed


def _resolve_path_list(path_list_source, game_r2_kwargs):
    """A real local path for path_list_source - downloaded from R2 to a
    temp file if it starts with "r2://<key>" (a plain full GET, not
    Range requests - path-lists are only a few MB).

    game_r2_kwargs is the game root's own already-resolved R2 bucket/
    prefix/credentials (see resolve_r2_source), reused as-is: a key is
    only meaningful relative to a specific bucket/prefix, and there's no
    env-derived fallback if the game root wasn't R2-sourced (None here).

    Returns None if unresolvable - callers should skip.
    """
    if not path_list_source.startswith(R2_PROTOCOL_PREFIX):
        if os.path.isfile(path_list_source):
            return path_list_source
        return None

    key_suffix = path_list_source[len(R2_PROTOCOL_PREFIX):]
    if not key_suffix or game_r2_kwargs is None:
        return None

    from albam.lib.s3 import build_s3_client

    r2_kwargs = game_r2_kwargs
    client = build_s3_client(
        endpoint_url=r2_kwargs["endpoint_url"],
        aws_access_key_id=r2_kwargs["aws_access_key_id"],
        aws_secret_access_key=r2_kwargs["aws_secret_access_key"],
    )
    key = f"{r2_kwargs['prefix']}/{key_suffix}" if r2_kwargs["prefix"] else key_suffix
    try:
        response = client.get_object(Bucket=r2_kwargs["bucket"], Key=key)
    except Exception:
        return None

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(response["Body"].read())
        return tmp.name


@pytest.fixture(scope="session")
def pak_fs_root(pytestconfig, local_app_id):
    """
    Builds (once per session, cached) a ReenFS for local_app_id - the same
    mechanism "Add Folder" uses in the UI - from
    --game-dir=<app-id>::<game-root>::<path-list-source> (reng's required
    third segment on top of MTFW's --game-dir). Each of <game-root>/
    <path-list-source> is a local path or "r2://..." (see
    tests.mtfw.r2_config.resolve_r2_source and _resolve_path_list for the
    R2 details - path-list r2:// only works when the game root is
    R2-sourced too). Skips cleanly when no --game-dir was given, the third
    segment is missing, or anything fails to resolve.
    """
    from albam.engines.reng.pak_fs import ReenFS
    from tests.mtfw.r2_config import resolve_r2_source

    if local_app_id not in _REEN_FS_INSTANCES:
        game_dirs = _reen_game_dirs(pytestconfig)
        if local_app_id not in game_dirs:
            pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")

        game_root, path_list_source = game_dirs[local_app_id]
        if path_list_source is None:
            pytest.skip(
                f"--game-dir={local_app_id}::{game_root} has no third (path-list) "
                f"segment - reng needs --game-dir={local_app_id}::{game_root}::<path-list>"
            )

        game_r2_kwargs = None
        if game_root.startswith(R2_PROTOCOL_PREFIX):
            game_r2_kwargs = resolve_r2_source(game_root)
            if game_r2_kwargs is None:
                pytest.skip(
                    f"--game-dir={local_app_id}::{game_root}::... requested but R2 isn't "
                    f"configured (empty bucket, missing s3 extras, or missing credentials - "
                    f"see .env.example)"
                )

        path_list_path = _resolve_path_list(path_list_source, game_r2_kwargs)
        if path_list_path is None:
            pytest.skip(
                f"--game-dir={local_app_id}::...::{path_list_source} - path list "
                f"not found/resolvable"
            )

        if game_r2_kwargs is not None:
            reen_fs = ReenFS.from_s3(path_list_path=path_list_path, **game_r2_kwargs)
        elif not os.path.isdir(game_root):
            pytest.skip(f"--game-dir={local_app_id}::{game_root}::... does not exist")
        else:
            reen_fs = ReenFS(game_root, path_list_path)

        _REEN_FS_INSTANCES[local_app_id] = reen_fs

    return _REEN_FS_INSTANCES[local_app_id]


@pytest.fixture(scope="session")
def reng_vfs_root(local_app_id, pak_fs_root):
    """
    Mount pak_fs_root (this app_id's already-resolved ReenFS/PakFS) into
    bpy's VFS, once per session per app_id - the same mechanism
    tests/mtfw/conftest.py's game_fs_root uses for MTFW_FS. Needed for
    tests that go through the real import_vfile() operator, unlike
    test_mesh_parsing.py which reads bytes straight off pak_fs_root and
    never touches the VFS at all.
    """
    if local_app_id not in _REEN_VFS_MOUNTED:
        bpy.context.scene.albam.apps.app_selected = local_app_id
        bpy.context.scene.albam.vfs.add_fs_root(
            local_app_id, pak_fs_root, display_name=f"{local_app_id}-local"
        )
        _REEN_VFS_MOUNTED.add(local_app_id)
    return pak_fs_root


def reng_import(local_app_id, local_path):
    """
    Select local_path (already mounted via reng_vfs_root) and run it
    through the real import_vfile() operator. Import-only counterpart of
    tests/mtfw/conftest.py's import_export() - only .mesh has an export
    function registered so far (see albam/engines/reng/mesh.py), nothing
    else in reng does, so this is what most reng tests still want.
    """
    vfs = bpy.context.scene.albam.vfs
    try:
        vfile = vfs.select_vfile(local_app_id, local_path)
    except KeyError:
        pytest.skip(f"{local_path!r} not found under --game-dir for app_id={local_app_id!r}")
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    return vfile


def reng_import_export(local_app_id, local_path):
    """
    Same as reng_import(), then also runs the freshly-imported object
    through the real export() operator - the reng counterpart of
    tests/mtfw/conftest.py's import_export(), for the one reng format
    (.mesh) that has an export function registered. Returns the source
    vfile; callers fetch the exported one from
    bpy.context.scene.albam.exported afterward, same as mtfw's version.
    """
    vfile = reng_import(local_app_id, local_path)
    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()
    assert result == {"FINISHED"}
    return vfile
