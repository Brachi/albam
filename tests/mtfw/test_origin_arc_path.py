"""
origin_arc_path() lets callers (Pack/Patch in export_panel.py) resolve which
.arc a given path came from without caring whether the VFS root behind it is
a single ArcFS-wrapped archive or a whole MTFW_FS game-folder root. Sourced
from the real R2 bucket (see tests/mtfw/r2_config.py) rather than a local
game install or committed sample data - tests/data/ is deliberately
gitignored (never commit real game asset bytes, even small ones), so there's
no local fixture to fall back to.
"""
import pytest

from albam.engines.mtfw.arc_fs import ArcFS, MTFW_FS, origin_arc_path
from tests.mtfw.r2_config import r2_kwargs_for_app

R2_KWARGS = r2_kwargs_for_app("re5")
pytestmark = pytest.mark.skipif(
    R2_KWARGS is None, reason="R2 not configured for app_id='re5' (see .env.example)"
)

# Known to live inside uPl00ChrisNormal.arc in the real bucket - not just any
# walked path, since walk.files() can also yield the .arc files themselves
# as raw loose entries (see MTFW_FS's <loose> layer).
PACKED_PATH = "/pawn/pl/pl00/model/pl0000.mod"
ARC_KEY = "re5/nativePC_MT/Image/Archive/uPl00ChrisNormal.arc"


@pytest.fixture(scope="module")
def game_fs():
    return MTFW_FS.from_s3(**R2_KWARGS)


def test_origin_arc_path_arcfs_ignores_the_path_argument(game_fs):
    fs_instance = game_fs.get_fs(ARC_KEY)
    assert isinstance(fs_instance, ArcFS)
    # ArcFS only ever backs a single archive - the path passed in shouldn't
    # matter, unlike MTFW_FS's per-path resolution below.
    assert origin_arc_path(fs_instance, "/anything/at/all") == ARC_KEY
    assert origin_arc_path(fs_instance, "/") == ARC_KEY


def test_origin_arc_path_mtfw_fs_resolves_per_path(game_fs):
    resolved = origin_arc_path(game_fs, PACKED_PATH)

    assert resolved == ARC_KEY


def test_origin_arc_path_mtfw_fs_loose_file_resolves_to_none(game_fs):
    # Nothing under the "re5" prefix at this exact path is a loose file
    # layered on top of the archives, so a path that isn't inside any
    # archive's own listing resolves to nothing owned by an ArcFS - exactly
    # the "not part of a packed archive" case Pack/Patch need to report
    # cleanly instead of proceeding.
    assert origin_arc_path(game_fs, "/does/not/exist.foo") is None


def test_origin_arc_path_unrelated_fs_returns_none():
    class NotAnArcFS:
        pass

    assert origin_arc_path(NotAnArcFS(), "/whatever") is None


def test_origin_of_returns_game_root_relative_path(game_fs):
    origin = game_fs.origin_of(PACKED_PATH)

    assert origin is not None
    assert origin == "nativePC_MT/Image/Archive/uPl00ChrisNormal.arc"


def test_origin_of_loose_file_resolves_to_none(game_fs):
    assert game_fs.origin_of("/does/not/exist.foo") is None


def test_origin_absolute_path_matches_origin_arc_path(game_fs):
    # origin_absolute_path() is what origin_arc_path() defers to for an
    # MTFW_FS - both must resolve to the same real, directly-openable key.
    assert game_fs.origin_absolute_path(PACKED_PATH) == ARC_KEY
    assert game_fs.origin_absolute_path(PACKED_PATH) == origin_arc_path(game_fs, PACKED_PATH)
