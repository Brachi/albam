"""
albam.lib.s3's disk cache, against a mocked S3 (moto) - no real bucket or
credentials needed, and no network. What it has to get right is narrow:
serve identical bytes on a hit, key ranges separately, never serve a hit
for a request it doesn't fully understand, and survive a corrupted entry.
"""
import os
import shutil
import sys

import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("moto")

from moto import mock_aws  # noqa: E402

from albam.lib.s3 import (  # noqa: E402
    CACHE_DIR_ENV_VAR,
    build_s3_client,
    cache_get_object,
    default_cache_dir,
    prune_cache,
    resolve_cache_dir,
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


def test_caching_is_on_by_default_and_lands_in_the_platform_cache_dir(monkeypatch, tmp_path):
    """Unset means the platform cache directory, not "off" - nobody should
    have to opt in to a cache that only ever saves work.
    """
    monkeypatch.delenv(CACHE_DIR_ENV_VAR, raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "platform", "linux")

    assert default_cache_dir() == str(tmp_path / "albam" / "s3")
    assert resolve_cache_dir() == default_cache_dir()

    with mock_aws():
        _seed_bucket()
        build_s3_client(region_name="us-east-1").get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    assert list((tmp_path / "albam" / "s3").iterdir()), "the default read should be cached"


def test_empty_env_var_turns_caching_off(monkeypatch, tmp_path):
    """The only way to say "don't cache", now that unset means the default."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setenv(CACHE_DIR_ENV_VAR, "")
    assert resolve_cache_dir() is None

    with mock_aws():
        _seed_bucket()
        build_s3_client(region_name="us-east-1").get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    assert not (tmp_path / "albam").exists()


def test_prune_evicts_oldest_first_until_under_the_size_limit(tmp_path):
    stems = _fill_cache(tmp_path, count=5, size=1000)
    freed = prune_cache(str(tmp_path), max_bytes=2500, min_free_bytes=0)

    surviving = {s for s in stems if os.path.exists(s + ".body")}
    assert freed >= 2000
    assert surviving == set(stems[-2:]), "the two most recently written should survive"
    # metadata goes with the body, never orphaned
    assert not any(os.path.exists(s + ".json") for s in stems if s not in surviving)


def test_prune_evicts_when_the_filesystem_is_nearly_full(tmp_path, monkeypatch):
    """The absolute limit alone isn't enough: a 2GiB cache is fine on a disk
    with room and a problem on one without."""
    stems = _fill_cache(tmp_path, count=4, size=1000)
    monkeypatch.setattr(shutil, "disk_usage", lambda _: _Usage(free=10))

    prune_cache(str(tmp_path), max_bytes=10 ** 9, min_free_bytes=3000)

    surviving = [s for s in stems if os.path.exists(s + ".body")]
    assert surviving == stems[-1:], (
        "low free space should evict even when far under max_bytes, oldest first")


def test_entries_are_not_written_when_that_would_fill_the_disk(monkeypatch, tmp_path):
    monkeypatch.setenv(CACHE_DIR_ENV_VAR, str(tmp_path))
    monkeypatch.setattr(shutil, "disk_usage", lambda _: _Usage(free=1))

    with mock_aws():
        _seed_bucket()
        body = build_s3_client(region_name="us-east-1").get_object(
            Bucket=BUCKET, Key=KEY)["Body"].read()

    assert body == CONTENT, "the read still succeeds, it just isn't cached"
    assert not any(f.endswith(".body") for _, _, files in os.walk(tmp_path) for f in files)


class _Usage:
    def __init__(self, free):
        self.total, self.used, self.free = free * 10, free * 9, free


def _seed_bucket():
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=BUCKET)
    client.put_object(Bucket=BUCKET, Key=KEY, Body=CONTENT)


def _fill_cache(tmp_path, count, size):
    """`count` complete entries, oldest first, one second apart so mtime
    ordering is unambiguous."""
    stems = []
    for i in range(count):
        stem = str(tmp_path / f"{i:02d}" / "entry")
        os.makedirs(os.path.dirname(stem), exist_ok=True)
        with open(stem + ".body", "wb") as f:
            f.write(b"x" * size)
        with open(stem + ".json", "w") as f:
            f.write("{}")
        os.utime(stem + ".body", (i, i))
        stems.append(stem)
    return stems
