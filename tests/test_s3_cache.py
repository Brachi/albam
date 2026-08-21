"""
albam.lib.s3's disk cache, against a mocked S3 (moto) - no real bucket or
credentials needed, and no network. What it has to get right is narrow:
serve identical bytes on a hit, key ranges separately, never serve a hit
for a request it doesn't fully understand, and survive a corrupted entry.
"""
import os

import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("moto")

from moto import mock_aws  # noqa: E402

from albam.lib.s3 import (  # noqa: E402
    CACHE_DIR_ENV_VAR,
    build_s3_client,
    cache_get_object,
)

BUCKET = "albam-test"
KEY = "re5/some.arc"
CONTENT = bytes(range(256)) * 40  # 10KB, enough to range into meaningfully


class CountingClient:
    """Wraps a real (moto-backed) client, counting get_object and
    head_object calls so a cache hit is provable rather than inferred from
    timing. Everything else proxies straight through - the cache is allowed
    to use any part of the client, and a double that only implements what
    it happens to call today silently turns a real regression into a
    fallback path that still returns correct bytes.
    """

    def __init__(self, client):
        self._client = client
        self.calls = 0
        self.head_calls = 0

    def __getattr__(self, name):
        return getattr(self._client, name)

    def get_object(self, **kwargs):
        self.calls += 1
        return self._client.get_object(**kwargs)

    def head_object(self, **kwargs):
        self.head_calls += 1
        return self._client.head_object(**kwargs)


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        client.put_object(Bucket=BUCKET, Key=KEY, Body=CONTENT)
        yield client


@pytest.fixture
def counting(s3_client):
    return CountingClient(s3_client)


def test_second_read_is_served_from_disk(counting, tmp_path):
    cached = cache_get_object(counting, str(tmp_path))

    first = cached.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    assert counting.calls == 1
    assert first == CONTENT

    second = cached.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    assert counting.calls == 1, "second read should not reach the server"
    assert second == first
    assert counting.head_calls == 1, "the hit costs one ETag check, not a re-download"


def test_ranges_are_cached_separately(counting, tmp_path):
    cached = cache_get_object(counting, str(tmp_path))

    head = cached.get_object(Bucket=BUCKET, Key=KEY, Range="bytes=0-15")
    assert head["Body"].read() == CONTENT[:16]
    tail = cached.get_object(Bucket=BUCKET, Key=KEY, Range="bytes=16-31")
    assert tail["Body"].read() == CONTENT[16:32]
    assert counting.calls == 2

    # both come back from disk, each with its own bytes - a shared key would
    # silently serve one range's content for the other
    assert cached.get_object(Bucket=BUCKET, Key=KEY, Range="bytes=0-15")["Body"].read() == CONTENT[:16]
    assert cached.get_object(Bucket=BUCKET, Key=KEY, Range="bytes=16-31")["Body"].read() == CONTENT[16:32]
    assert counting.calls == 2
    assert counting.head_calls == 1, "one ETag check covers every range of the same object"


def test_ranged_response_keeps_the_fields_smart_open_reads(counting, tmp_path):
    cached = cache_get_object(counting, str(tmp_path))

    live = cached.get_object(Bucket=BUCKET, Key=KEY, Range="bytes=0-15")
    live_body = live["Body"].read()
    from_cache = cached.get_object(Bucket=BUCKET, Key=KEY, Range="bytes=0-15")

    assert from_cache["ContentLength"] == live["ContentLength"]
    assert from_cache["ContentRange"] == live["ContentRange"]
    assert from_cache["ResponseMetadata"]["HTTPStatusCode"] == 206
    assert from_cache["ResponseMetadata"]["RetryAttempts"] == 0
    assert from_cache["Body"].read() == live_body


def test_unknown_kwargs_bypass_the_cache(counting, tmp_path):
    """A request carrying an argument the key doesn't cover (here VersionId)
    must never be answered from an entry that ignored it."""
    cached = cache_get_object(counting, str(tmp_path))

    cached.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    assert counting.calls == 1

    cached.get_object(Bucket=BUCKET, Key=KEY, VersionId="null")["Body"].read()
    cached.get_object(Bucket=BUCKET, Key=KEY, VersionId="null")["Body"].read()
    assert counting.calls == 3, "versioned reads should go to the server every time"
    assert not any(name.endswith(".body") for _, _, files in os.walk(tmp_path) for name in files
                   if "VersionId" in name)


def test_corrupted_entry_falls_back_to_the_server(counting, tmp_path):
    cached = cache_get_object(counting, str(tmp_path))
    cached.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    assert counting.calls == 1

    for root, _, files in os.walk(tmp_path):
        for name in files:
            if name.endswith(".json"):
                with open(os.path.join(root, name), "w") as f:
                    f.write("{not json")

    assert cached.get_object(Bucket=BUCKET, Key=KEY)["Body"].read() == CONTENT
    assert counting.calls == 2


def test_build_s3_client_caches_only_when_the_env_var_is_set(monkeypatch, tmp_path):
    """Checked by what lands on disk rather than by inspecting the client:
    anything else that wraps get_object (a profiler, a request counter)
    would fool an attribute check into reporting the cache as enabled.
    """
    def read_once(client):
        client.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()

    def entries():
        return sorted(f for _, _, files in os.walk(tmp_path) for f in files)

    with mock_aws():
        boto3.client("s3", region_name="us-east-1").create_bucket(Bucket=BUCKET)
        boto3.client("s3", region_name="us-east-1").put_object(
            Bucket=BUCKET, Key=KEY, Body=CONTENT)

        monkeypatch.setenv(CACHE_DIR_ENV_VAR, str(tmp_path))
        read_once(build_s3_client(region_name="us-east-1"))
        assert entries(), "with the env var set, the read should be cached"

        before = entries()
        monkeypatch.delenv(CACHE_DIR_ENV_VAR, raising=False)
        read_once(build_s3_client(region_name="us-east-1"))
        assert entries() == before, "with no env var, nothing should be written"


def test_reuploaded_object_is_not_served_from_the_cache(counting, s3_client, tmp_path):
    """The staleness case the ETag check exists for, and not a hypothetical
    one: the moto-backed suites recreate one bucket and key with different
    bytes from test to test. A cache keyed on (bucket, key, range) alone
    hands the second run the first run's content.
    """
    replacement = CONTENT[::-1]

    first = cache_get_object(counting, str(tmp_path))
    assert first.get_object(Bucket=BUCKET, Key=KEY)["Body"].read() == CONTENT

    s3_client.put_object(Bucket=BUCKET, Key=KEY, Body=replacement)

    # a fresh wrapper, i.e. a later process against the same cache directory
    second = cache_get_object(CountingClient(s3_client), str(tmp_path))
    assert second.get_object(Bucket=BUCKET, Key=KEY)["Body"].read() == replacement
