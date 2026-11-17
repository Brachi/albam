"""
HexnFS.from_s3() against a mocked S3 (moto) - no real bucket/credentials or
real .ssg needed to validate the mechanism. Real Cloudflare R2 usage differs
only in which endpoint_url/credentials get passed to from_s3() (see its
docstring, and albam.lib.s3 which it shares with MTFW_FS.from_s3/
ReenFS.from_s3). Mirrors tests/mtfw/test_arc_fs_s3.py.

Like ArcFS/PakFS, construction only reads each .ssg's header and file
table. Unlike them, the first read of any file decompresses the archive's
whole body: an .ssg's "solid" compression (see albam/engines/hexn/fs.py's
module docstring) leaves no way to reach one file on its own.
"""
import os

import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("moto")
pytest.importorskip("smart_open")

from moto import mock_aws  # noqa: E402
from albam.lib.s3 import CACHE_DIR_ENV_VAR  # noqa: E402

from albam.engines.hexn.fs import HexnFS  # noqa: E402
from tests.hexn.test_ssg_fs import _build_ssg_bytes  # noqa: E402

BUCKET = "reorc-assets"
GAME_ROOT_PREFIX = "reorc"
MODELS_DIR = "some/pack/models/"
SAMPLE_PATH = "some/pack/models/sample_a/model.edgemodel"
OTHER_PATH = "some/pack/models/sample_b/model.edgemodel"

# Deliberately larger than s3_opener's 1MiB range_chunk_size, same reasoning
# as test_arc_fs_s3.py's SAMPLE_CONTENT - not load-bearing here (from_s3()
# downloads the whole object regardless, see module docstring), kept for
# parity/consistency with the other from_s3 test suites.
SAMPLE_CONTENT = b"EDGEMODEL-FAKE-CONTENT-FOR-MOCKED-S3-TESTS" + os.urandom(2 * 1024 * 1024)
OTHER_CONTENT = b"EDGEMODEL-OTHER-FAKE-CONTENT"

DUMMY_CREDS = dict(
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
    region_name="us-east-1",
)

FIXTURE_SSG_BYTES = {
    "sample_a.ssg": _build_ssg_bytes([(SAMPLE_PATH, SAMPLE_CONTENT)]),
    # content doesn't matter here - only used as a second, distinct .ssg for
    # count-based assertions.
    "sample_b.ssg": _build_ssg_bytes([(OTHER_PATH, OTHER_CONTENT)]),
}
FIXTURE_SSGS = tuple(FIXTURE_SSG_BYTES)


def _from_s3(**kwargs):
    kwargs = {**DUMMY_CREDS, **kwargs}
    return HexnFS.from_s3(bucket=BUCKET, prefix=GAME_ROOT_PREFIX, **kwargs)


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        for name, data in FIXTURE_SSG_BYTES.items():
            client.put_object(Bucket=BUCKET, Key=f"{GAME_ROOT_PREFIX}/{MODELS_DIR}{name}", Body=data)
        yield client


@pytest.fixture
def get_object_calls(s3_client, monkeypatch):
    """Record (Range, ContentLength) for every get_object call made by any
    S3 client built while this fixture is active - same technique as
    tests/mtfw/test_arc_fs_s3.py's fixture of the same name, since
    HexnFS.from_s3() also builds its client internally.
    """
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
    # The disk cache wraps get_object outside the spy, so a range an earlier
    # test already fetched would never reach it.
    monkeypatch.setenv(CACHE_DIR_ENV_VAR, "")
    return calls


def test_from_s3_loads_ssgs(s3_client):
    game_fs = _from_s3(include_loose=False)
    assert game_fs.failed_ssgs == []
    assert len(list(game_fs.iterate_fs())) == len(FIXTURE_SSGS)


def test_from_s3_includes_loose_layer_by_default(s3_client):
    game_fs = _from_s3()
    assert len(list(game_fs.iterate_fs())) == len(FIXTURE_SSGS) + 1


def test_from_s3_include_loose_false_disables_loose_layer(s3_client):
    loose_override = b"LOOSE-OVERRIDE-CONTENT"
    s3_client.put_object(Bucket=BUCKET, Key=f"{GAME_ROOT_PREFIX}/{SAMPLE_PATH}", Body=loose_override)

    game_fs = _from_s3(include_loose=False)
    # with no loose layer, the packed copy is all there is - loose_override
    # sitting in the bucket at that key is simply invisible
    assert game_fs.readbytes(SAMPLE_PATH) != loose_override
    assert game_fs.readbytes(SAMPLE_PATH) == SAMPLE_CONTENT


def test_from_s3_first_read_fetches_the_archive_and_later_reads_do_not(get_object_calls):
    """SsgFS decompresses an archive's whole body on its first read and keeps
    it until close(): solid compression means a single file can't be read
    on its own. Construction only reads the header and file table.
    """
    game_fs = _from_s3()
    get_object_calls.clear()  # isolate the reads below from construction's calls

    assert game_fs.readbytes(SAMPLE_PATH) == SAMPLE_CONTENT
    assert get_object_calls, "the first read has to fetch the compressed body"

    get_object_calls.clear()
    assert game_fs.readbytes(SAMPLE_PATH) == SAMPLE_CONTENT
    assert not get_object_calls


def test_from_s3_read_matches_local_reference(s3_client):
    game_fs = _from_s3()
    assert game_fs.readbytes(SAMPLE_PATH) == SAMPLE_CONTENT
    assert game_fs.readbytes(OTHER_PATH) == OTHER_CONTENT


def test_from_s3_origin_of(s3_client):
    game_fs = _from_s3()
    # relative to prefix (GAME_ROOT_PREFIX="reorc" here), not the bucket key
    # verbatim - see HexnFS.origin_of()'s docstring.
    assert game_fs.origin_of(SAMPLE_PATH) == MODELS_DIR + "sample_a.ssg"


def test_from_s3_loose_file_overrides_packed_content(s3_client):
    # a loose override lives at the path itself, not under the .ssg's own
    # prefix - same convention as a local unpacked/modded file under
    # game_root.
    loose_override = b"LOOSE-OVERRIDE-CONTENT"
    s3_client.put_object(Bucket=BUCKET, Key=f"{GAME_ROOT_PREFIX}/{SAMPLE_PATH}", Body=loose_override)

    game_fs = _from_s3()

    assert game_fs.readbytes(SAMPLE_PATH) == loose_override
    # not from an .ssg, so origin_of should say so
    assert game_fs.origin_of(SAMPLE_PATH) is None
