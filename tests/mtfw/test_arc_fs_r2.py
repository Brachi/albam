"""
MTFW_FS.from_s3() against a real Cloudflare R2 bucket, using credentials
from a local .env file (see arc_fs prototyping session / README for the
expected keys: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
R2_BUCKET_NAME, optionally R2_PREFIX). Skipped entirely if that .env isn't
present/complete, so this never runs (or needs credentials) on another
machine or in CI.
"""
import os

import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("dotenv")
pytest.importorskip("smart_open")

from dotenv import load_dotenv  # noqa: E402

from albam.engines.mtfw.arc_fs import MTFW_FS  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(REPO, ".env"))

REQUIRED_ENV = ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME")
_missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]

pytestmark = pytest.mark.skipif(
    bool(_missing), reason=f"real R2 .env not configured (missing: {_missing})"
)

# known to exist in this account's bucket as of the arc_fs prototyping
# session - adjust here if the bucket's contents change.
SAMPLE_PATH = "/effect/tex/0011/tx0011_BM.tex"
SAMPLE_ARC_SUFFIX = "uPl02JillCos3.arc"


def _r2_kwargs():
    return dict(
        bucket=os.environ["R2_BUCKET_NAME"],
        prefix=os.environ.get("R2_PREFIX", ""),
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )


@pytest.fixture(scope="module")
def game_fs():
    return MTFW_FS.from_s3(**_r2_kwargs())


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
    assert data[:3] == b"TEX"

    origin = game_fs.origin_of(SAMPLE_PATH)
    assert origin is not None and origin.endswith(SAMPLE_ARC_SUFFIX)


def test_real_r2_reads_are_bounded_not_full_downloads(get_object_calls):
    game_fs = MTFW_FS.from_s3(**_r2_kwargs())

    # every request so far (construction: one header+table fetch per arc)
    # must be a bounded range, never open-ended to EOF
    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)

    get_object_calls.clear()  # isolate the read below from construction's calls
    data = game_fs.readbytes(SAMPLE_PATH)
    assert data[:3] == b"TEX"

    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)
    # sanity: total fetched shouldn't be wildly larger than what was read
    total_fetched = sum(cl for _r, cl in get_object_calls)
    assert total_fetched < 10 * len(data)
