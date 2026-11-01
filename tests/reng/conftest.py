import os
import tempfile

import pytest

R2_PROTOCOL_PREFIX = "r2://"

# app_id -> the ReenFS instance already mounted this session.
_REEN_FS_INSTANCES = {}


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
