import os
import time

import pytest

from albam.engines.mtfw.arc_fs import MTFW_FS

APP_ID = "re5"
R2_PROTOCOL_PREFIX = "r2://"

# Sourced from --game-dir=re5::<value> like the rest of tests/mtfw (see
# tests/mtfw/conftest.py's game_fs_root), so CI's r2:// curated subset runs
# this too. Its own MTFW_FS rather than the session-scoped game_fs_root:
# several tests here assert the lazy index has *not* been built yet, which a
# shared instance other test files may already have walked can't promise.
# Every test holds for any re5 source, a local install or the R2 subset.

# Present in every re5 source: the R2 subset carries its archive too (see
# test_arc_fs_r2.py's SAMPLE_PATH).
PACKED_PATH = "pawn/pl/pl00/model/pl0000.mod"
PACKED_DIR = "/pawn/pl/pl00/model"
LOOSE_PATH = "re5dx9.exe"  # a real file sitting directly under a full install's root

# origin_of() answers before the index exists, kept for the same question after.
_ORIGINS_BEFORE_INDEX = {}


def _re5_game_dir(pytestconfig):
    # Already validated by tests/conftest.py's pytest_configure.
    for entry in pytestconfig.getoption("game_dir") or []:
        app_id, value, *_reng_only = entry.split("::")
        if app_id == APP_ID:
            return value
    return None


@pytest.fixture(scope="module")
def game_fs(pytestconfig):
    from tests.mtfw.r2_config import resolve_r2_source

    value = _re5_game_dir(pytestconfig)
    if not value:
        pytest.skip(f"No --game-dir supplied for app_id={APP_ID!r}")
    if value.startswith(R2_PROTOCOL_PREFIX):
        r2_kwargs = resolve_r2_source(value)
        if r2_kwargs is None:
            pytest.skip(
                f"--game-dir={APP_ID}::{value} requested but R2 isn't configured "
                f"(empty bucket, missing s3 extras, or missing credentials - see .env.example)"
            )
        return MTFW_FS.from_s3(**r2_kwargs)
    if not os.path.isdir(value):
        pytest.skip(f"--game-dir={APP_ID}::{value} does not exist")
    return MTFW_FS(value)


def test_index_is_not_built_by_point_lookups(game_fs):
    assert game_fs._owner is None

    assert game_fs.exists(PACKED_PATH)
    assert game_fs._owner is None, "exists() should not trigger the lazy index"

    game_fs.readbytes(PACKED_PATH)
    assert game_fs._owner is None, "readbytes() should not trigger the lazy index"

    game_fs.getinfo(PACKED_PATH, namespaces=["details"])
    assert game_fs._owner is None, "getinfo() should not trigger the lazy index"


def test_origin_of_before_index_built(game_fs):
    assert game_fs._owner is None

    origin = game_fs.origin_of(PACKED_PATH)
    _ORIGINS_BEFORE_INDEX[PACKED_PATH] = origin
    assert origin is not None and origin.endswith(".arc")
    assert not os.path.isabs(origin), "origin_of() should return a game-root-relative path"
    assert game_fs._owner is None, "origin_of() should not trigger the lazy index"

    assert game_fs.origin_of(LOOSE_PATH) is None
    assert game_fs.origin_of("nope/does/not/exist.foo") is None
    assert game_fs._owner is None


def test_listdir_builds_and_caches_the_index(game_fs):
    game_fs.listdir(PACKED_DIR)
    assert game_fs._owner is not None
    owner_before = game_fs._owner
    game_fs.listdir(PACKED_DIR)
    assert game_fs._owner is owner_before, "index should be built once, then reused"


def test_walk_matches_and_is_fast_after_first_call(game_fs):
    t0 = time.time()
    first = sorted(game_fs.walk.files())
    first_duration = time.time() - t0

    t0 = time.time()
    second = sorted(game_fs.walk.files())
    second_duration = time.time() - t0

    assert first == second
    assert "/" + PACKED_PATH in first
    if game_fs._s3_prefix is None:
        assert len(first) > 40000  # sanity: this is a whole game install
    # second call reuses the cached index; generously bounded to avoid
    # flaking on slow CI, but should be an order of magnitude faster than
    # the ~70s the unindexed MultiFS fan-out took for this same walk.
    assert second_duration < max(first_duration / 3, 5)


def test_missing_path_raises(game_fs):
    from fs.errors import ResourceNotFound

    with pytest.raises(ResourceNotFound):
        game_fs.readbytes("/this/does/not/exist.foo")


def test_origin_of_after_index_built_matches_pre_index_result(game_fs):
    assert game_fs._owner is not None  # built by earlier tests in this module
    assert game_fs.origin_of(PACKED_PATH) == _ORIGINS_BEFORE_INDEX[PACKED_PATH]
    assert game_fs.origin_of(LOOSE_PATH) is None
    assert game_fs.origin_of("nope/does/not/exist.foo") is None
