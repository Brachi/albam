import os
import time
import zlib

import pytest

from albam.engines.mtfw.arc_fs import MTFW_FS

APP_ID = "re5"
R2_PROTOCOL_PREFIX = "r2://"

# Sourced from --game-dir=re5::<value> like the rest of tests/mtfw (see
# tests/mtfw/conftest.py's game_fs_root), so CI's r2:// curated subset runs
# this too. Its own MTFW_FS rather than the session-scoped game_fs_root:
# several tests here assert the lazy index has *not* been built yet, which a
# shared instance other test files may already have walked can't promise.
#
# The tests split two ways. Those taking `game_fs` hold for any re5 source,
# a local install or the R2 subset. Those taking `full_install_fs` assert
# facts about one whole local install - which archives fail to parse, how
# many entries a full walk finds, a loose .exe next to the archives, raw
# reads straight off disk - that the curated R2 subset (only the archives
# the committed datasets reference) can't answer, so they skip there.

# Known-bad archives in a full install: they use a container layout arc.ksy
# doesn't model (see MTFW_FS.failed_arcs). Asserted by name so a regression
# (more archives silently failing to parse) gets caught.
EXPECTED_FAILED_ARCS = {
    "s101.arc",
    "uOmS103ScrAdj.arc",
    "uOmf303.arc",
}

# A file known to live in multiple archives with the same relative path but
# different content (see the duplicate-content report from the arc_fs
# prototyping session) - useful as a stable point-lookup target. Full
# install only: the R2 subset doesn't carry its archives.
SAMPLE_PATH = "/sound/se/mt/se_mt0002.srq"

# Present in every re5 source: the R2 subset carries its archive too (see
# test_arc_fs_r2.py's SAMPLE_PATH).
PACKED_PATH = "pawn/pl/pl00/model/pl0000.mod"
PACKED_DIR = "/pawn/pl/pl00/model"
LOOSE_PATH = "re5dx9.exe"  # a real file sitting directly under a full install's root


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


@pytest.fixture
def full_install_fs(game_fs):
    if game_fs._s3_prefix is not None:
        pytest.skip(
            f"needs a full local {APP_ID} install: --game-dir={APP_ID} is an r2:// "
            f"curated subset, which can't answer whole-install assertions"
        )
    return game_fs


def test_construction_finds_arcs_and_skips_bad_ones(full_install_fs):
    game_fs = full_install_fs
    failed_names = {os.path.basename(p) for p, _e in game_fs.failed_arcs}
    assert failed_names == EXPECTED_FAILED_ARCS
    # +1 for the loose/"<loose>" OSFS layer added on top
    assert len(list(game_fs.iterate_fs())) > 1000


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


def test_point_lookup_matches_manual_decompression(full_install_fs):
    game_fs = full_install_fs
    owner_fs = game_fs._delegate(SAMPLE_PATH)
    assert owner_fs is not None

    # independent read path: raw seek/read on the arc file itself, bypassing
    # ArcFS/openbin entirely, using only the offset/zsize kaitai already
    # parsed for this entry.
    file_entry = owner_fs._entries[SAMPLE_PATH]
    with open(owner_fs.arc_path, "rb") as f:
        f.seek(file_entry.offset)
        raw = f.read(file_entry.zsize)
    expected = zlib.decompress(raw)

    assert game_fs.readbytes(SAMPLE_PATH) == expected


def test_missing_path_raises(game_fs):
    from fs.errors import ResourceNotFound

    with pytest.raises(ResourceNotFound):
        game_fs.readbytes("/this/does/not/exist.foo")


def test_origin_of_after_index_built_matches_pre_index_result(full_install_fs):
    game_fs = full_install_fs
    assert game_fs._owner is not None  # built by earlier tests in this module

    owner_arc_path = game_fs._owner[game_fs.validatepath(PACKED_PATH)].arc_path
    expected = os.path.relpath(owner_arc_path, game_fs.game_root).replace(os.sep, "/")
    assert game_fs.origin_of(PACKED_PATH) == expected
    assert game_fs.origin_of(LOOSE_PATH) is None
    assert game_fs.origin_of("nope/does/not/exist.foo") is None


def test_origin_absolute_path_is_openable_on_disk(full_install_fs):
    game_fs = full_install_fs
    absolute = game_fs.origin_absolute_path(PACKED_PATH)
    assert os.path.isabs(absolute)
    assert os.path.isfile(absolute)
    assert absolute == os.path.join(game_fs.game_root, game_fs.origin_of(PACKED_PATH))
    assert game_fs.origin_absolute_path(LOOSE_PATH) is None
