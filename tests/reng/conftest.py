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


def _resolve_path_list(app_id, path_list_source):
    """A real local path for path_list_source - downloaded from R2 to a
    temp file first if it starts with "r2://", e.g.
    "r2://RE3Z_RT_STM_Release.list" (the key it was uploaded under, relative
    to the app's own R2 prefix - explicit, not a fixed/assumed filename,
    since there's no single real-world naming convention for these
    community-published lists to rely on). Path-lists are small (a few MB):
    a plain full GET, not the Range-request machinery PakFS.from_s3/
    ReenFS.from_s3 use for the (possibly tens-of-GB) pak itself. Returns
    None if unresolvable - callers should skip.
    """
    if not path_list_source.startswith(R2_PROTOCOL_PREFIX):
        if os.path.isfile(path_list_source):
            return path_list_source
        return None

    key_suffix = path_list_source[len(R2_PROTOCOL_PREFIX):]
    if not key_suffix:
        return None

    from albam.lib.s3 import build_s3_client
    from tests.mtfw.r2_config import r2_kwargs_for_app

    r2_kwargs = r2_kwargs_for_app(app_id)
    if r2_kwargs is None:
        return None

    client = build_s3_client(
        endpoint_url=r2_kwargs["endpoint_url"],
        aws_access_key_id=r2_kwargs["aws_access_key_id"],
        aws_secret_access_key=r2_kwargs["aws_secret_access_key"],
    )
    key = f"{r2_kwargs['prefix']}/{key_suffix}"
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
    mechanism "Add Folder" uses in the UI for a whole RE Engine install -
    from --game-dir=<app-id>::<game-root>::<path-list-source>: the same
    --game-dir option MTFW uses (tests/conftest.py), extended with reng's
    required third segment. <game-root> is either a local path or the bare
    "r2://" sentinel (game-root discovery, same as MTFW's); <path-list-source>
    is either a local path or "r2://<key>" - the key it was uploaded under,
    relative to the app's own R2 prefix (explicit, since there's no fixed
    naming convention for these files to assume - see _resolve_path_list).
    Any combination works (e.g. pak from R2, path-list local, or vice
    versa). Skips cleanly when no --game-dir was given for this app_id, the
    third segment is missing, or anything fails to resolve.
    """
    from albam.engines.reng.pak_fs import ReenFS
    from tests.mtfw.r2_config import r2_kwargs_for_app

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

        path_list_path = _resolve_path_list(local_app_id, path_list_source)
        if path_list_path is None:
            pytest.skip(
                f"--game-dir={local_app_id}::...::{path_list_source} - path list "
                f"not found/resolvable"
            )

        if game_root == R2_PROTOCOL_PREFIX:
            r2_kwargs = r2_kwargs_for_app(local_app_id)
            if r2_kwargs is None:
                pytest.skip(
                    f"--game-dir={local_app_id}::r2://... requested but R2 isn't "
                    f"configured (missing s3 extras or credentials - see .env.example)"
                )
            reen_fs = ReenFS.from_s3(path_list_path=path_list_path, **r2_kwargs)
        elif not os.path.isdir(game_root):
            pytest.skip(f"--game-dir={local_app_id}::{game_root}::... does not exist")
        else:
            reen_fs = ReenFS(game_root, path_list_path)

        _REEN_FS_INSTANCES[local_app_id] = reen_fs

    return _REEN_FS_INSTANCES[local_app_id]
