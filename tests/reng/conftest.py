import os

import pytest

# Gitignored plaintext community path list (never real game bytes, never
# committed itself - see albam/engines/reng/archive.py's RE3_PATH_LIST for
# the same hardcoded-for-now rationale). PakFS needs it to resolve any
# virtual path at all, since a .pak's own file entries carry only
# murmurhash3 hashes, not path strings.
_PATH_LIST_BY_APP = {
    "re3": os.path.join(os.path.dirname(__file__), "..", "data", "re3", "RE3Z_RT_STM_Release.list"),
}

# app_id -> the PakFS instance already constructed this session - built once
# per app_id (constructing PakFS re-reads + re-hashes the whole path list
# against the pak's header, not something to repeat per test).
_PAK_FS_INSTANCES = {}


@pytest.fixture(scope="session")
def pak_fs_root(local_app_id):
    """
    Builds (once per session, cached) a PakFS for local_app_id from a real
    .pak path supplied via ALBAM_TEST_<APP_ID>_PAK_PATH (e.g.
    ALBAM_TEST_RE3_PAK_PATH) - no --game-dir-style CLI option yet, matching
    reng's current re3-only, hardcoded-path-list scope. Skips cleanly when
    unset or the file doesn't exist, same convention as
    tests/mtfw/test_arc_fs.py's GAME_ROOT env var.
    """
    from albam.engines.reng.pak_fs import PakFS

    if local_app_id not in _PAK_FS_INSTANCES:
        path_list_path = _PATH_LIST_BY_APP.get(local_app_id)
        if path_list_path is None:
            pytest.skip(f"No path list configured for app_id={local_app_id!r} in tests/reng/conftest.py")

        env_var = f"ALBAM_TEST_{local_app_id.upper()}_PAK_PATH"
        pak_path = os.environ.get(env_var, "")
        if not pak_path or not os.path.isfile(pak_path):
            pytest.skip(f"{env_var} not set or file not found - point it at a real {local_app_id} .pak")

        _PAK_FS_INSTANCES[local_app_id] = PakFS(pak_path, path_list_path)

    return _PAK_FS_INSTANCES[local_app_id]
