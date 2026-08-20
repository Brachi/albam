"""
MTFW_FS.from_s3() against a real Cloudflare R2 bucket, using credentials
from a local .env file (see .env.example for the expected keys). Skipped
entirely if R2 isn't configured for the "re5" app_id, so this never runs (or
needs credentials) on another machine, or in CI until the R2_* secrets are
added there (see .github/workflows/tests.yml).
"""
import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("dotenv")
pytest.importorskip("smart_open")

from albam.engines.mtfw.arc_fs import MTFW_FS  # noqa: E402
from tests.mtfw.r2_config import r2_kwargs_for_app  # noqa: E402

APP_ID = "re5"
_r2_kwargs = r2_kwargs_for_app(APP_ID)

pytestmark = pytest.mark.skipif(
    _r2_kwargs is None, reason=f"real R2 not configured for app_id={APP_ID!r} (see .env.example)"
)

# known to live in the real bucket under the "re5" prefix, mirroring the real
# game's own folder structure from there down (nativePC_MT/Image/Archive/...)
# - the same real content test_origin_arc_path.py's PACKED_PATH resolves to.
SAMPLE_PATH = "/pawn/pl/pl00/model/pl0000.mod"
SAMPLE_ARC_SUFFIX = "uPl00ChrisNormal.arc"


@pytest.fixture(scope="module")
def game_fs():
    return MTFW_FS.from_s3(**_r2_kwargs)


@pytest.fixture
def get_object_calls(monkeypatch):
    """Record (Range, ContentLength) for every get_object call made by any
    S3 client built while this fixture is active, including the one
    MTFW_FS.from_s3 constructs internally."""
    calls = []
    real_client_factory = boto3.client

    def spying_client_factory(*args, **kwargs):
        client = real_client_factory(*args, **kwargs)
        original_get_object = client.get_object

        def spy(**gkwargs):
            result = original_get_object(**gkwargs)
            calls.append((gkwargs.get("Range"), result["ContentLength"]))
            return result

        client.get_object = spy
        return client

    monkeypatch.setattr(boto3, "client", spying_client_factory)
    return calls


def test_real_r2_finds_arcs_without_errors(game_fs):
    assert game_fs.failed_arcs == []
    # at least one arc plus the default loose layer
    assert len(list(game_fs.iterate_fs())) >= 2


def test_real_r2_reads_real_content(game_fs):
    data = game_fs.readbytes(SAMPLE_PATH)
    assert data[:3] == b"MOD"

    origin = game_fs.origin_of(SAMPLE_PATH)
    assert origin is not None and origin.endswith(SAMPLE_ARC_SUFFIX)


def test_real_r2_reads_are_bounded_not_full_downloads(get_object_calls):
    game_fs = MTFW_FS.from_s3(**_r2_kwargs)

    # every request so far (construction: one header+table fetch per arc)
    # must be a bounded range, never open-ended to EOF
    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)

    get_object_calls.clear()  # isolate the read below from construction's calls
    data = game_fs.readbytes(SAMPLE_PATH)
    assert data[:3] == b"MOD"

    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)
    # sanity: total fetched shouldn't be wildly larger than what was read
    total_fetched = sum(cl for _r, cl in get_object_calls)
    assert total_fetched < 10 * len(data)
