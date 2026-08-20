import os
import time
import zlib

import pytest

from albam.engines.mtfw.arc_fs import MTFW_FS

# TODO: hardcoded for now; parametrize / move to --arcdir-style pytest option
# once this stops being a prototype.
GAME_ROOT = os.environ.get("ALBAM_TEST_RE5_GAME_ROOT", "")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(GAME_ROOT), reason=f"RE5 install not found at {GAME_ROOT}"
)

# Known-bad archives in this specific install: they use a container layout
# arc.ksy doesn't model (see MTFW_FS.failed_arcs). Asserted by name so a
# regression (more archives silently failing to parse) gets caught.
EXPECTED_FAILED_ARCS = {
    "s101.arc",
    "uOmS103ScrAdj.arc",
    "uOmf303.arc",
}

# A file known to live in multiple archives with the same relative path but
# different content (see the duplicate-content report from the arc_fs
# prototyping session) - useful as a stable point-lookup target.
SAMPLE_PATH = "/sound/se/mt/se_mt0002.srq"

PACKED_PATH = "pawn/pl/pl00/model/pl0000.mod"
LOOSE_PATH = "re5dx9.exe"  # a real file sitting directly under GAME_ROOT


@pytest.fixture(scope="module")
def game_fs():
    return MTFW_FS(GAME_ROOT)


def test_construction_finds_arcs_and_skips_bad_ones(game_fs):
    failed_names = {os.path.basename(p) for p, _e in game_fs.failed_arcs}
    assert failed_names == EXPECTED_FAILED_ARCS
    # +1 for the loose/"<loose>" OSFS layer added on top
    assert len(list(game_fs.iterate_fs())) > 1000


def test_index_is_not_built_by_point_lookups(game_fs):
    assert game_fs._owner is None

    assert game_fs.exists(SAMPLE_PATH)
    assert game_fs._owner is None, "exists() should not trigger the lazy index"

    game_fs.readbytes(SAMPLE_PATH)
    assert game_fs._owner is None, "readbytes() should not trigger the lazy index"

    game_fs.getinfo(SAMPLE_PATH, namespaces=["details"])
    assert game_fs._owner is None, "getinfo() should not trigger the lazy index"


def test_origin_of_before_index_built(game_fs):
    assert game_fs._owner is None

    origin = game_fs.origin_of(PACKED_PATH)
    assert origin is not None and origin.endswith(".arc")
    assert game_fs._owner is None, "origin_of() should not trigger the lazy index"

    assert game_fs.origin_of(LOOSE_PATH) is None
    assert game_fs.origin_of("nope/does/not/exist.foo") is None
    assert game_fs._owner is None


def test_listdir_builds_and_caches_the_index(game_fs):
    game_fs.listdir("/sound/se/mt")
    assert game_fs._owner is not None
    owner_before = game_fs._owner
    game_fs.listdir("/sound/se/mt")
    assert game_fs._owner is owner_before, "index should be built once, then reused"


def test_walk_matches_and_is_fast_after_first_call(game_fs):
    t0 = time.time()
    first = sorted(game_fs.walk.files())
    first_duration = time.time() - t0

    t0 = time.time()
    second = sorted(game_fs.walk.files())
    second_duration = time.time() - t0

    assert first == second
    assert len(first) > 40000  # sanity: this is a whole game install
    # second call reuses the cached index; generously bounded to avoid
    # flaking on slow CI, but should be an order of magnitude faster than
    # the ~70s the unindexed MultiFS fan-out took for this same walk.
    assert second_duration < max(first_duration / 3, 5)


def test_point_lookup_matches_manual_decompression(game_fs):
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


def test_origin_of_after_index_built_matches_pre_index_result(game_fs):
    assert game_fs._owner is not None  # built by earlier tests in this module

    assert game_fs.origin_of(PACKED_PATH) == game_fs._owner[game_fs.validatepath(PACKED_PATH)].arc_path
    assert game_fs.origin_of(LOOSE_PATH) is None
    assert game_fs.origin_of("nope/does/not/exist.foo") is None
