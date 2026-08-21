"""
Shared S3/R2-compatible client + opener/filesystem helpers.

Used by both MT Framework's MTFW_FS.from_s3 (albam/engines/mtfw/arc_fs.py)
and RE Engine's PakFS.from_s3/ReenFS.from_s3 (albam/engines/reng/pak_fs.py)
- nothing engine-specific in any of these, so they live here instead of
being duplicated (or one engine importing the other's module).
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import DirectoryExpected, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.path import basename


CACHE_DIR_ENV_VAR = "ALBAM_S3_CACHE_DIR"
CACHE_MAX_BYTES_ENV_VAR = "ALBAM_S3_CACHE_MAX_BYTES"
CACHE_MIN_FREE_BYTES_ENV_VAR = "ALBAM_S3_CACHE_MIN_FREE_BYTES"

# A full test suite against two games caches ~200MB, so 2GiB leaves room for
# several more without the cache ever being the thing that fills a disk.
DEFAULT_CACHE_MAX_BYTES = 2 * 1024 ** 3
# Refuse to grow the cache once the filesystem is this close to full,
# whatever the cache's own size. A convenience cache has no business being
# the reason a machine runs out of space.
DEFAULT_CACHE_MIN_FREE_BYTES = 2 * 1024 ** 3
# How much may be written between prunes. Pruning walks the cache, so it
# runs once when a client is built and then only after meaningful growth.
PRUNE_INTERVAL_BYTES = 256 * 1024 ** 2


def build_s3_client(
    *,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    endpoint_url=None,
    region_name="auto",
):
    """boto3 S3 client with the R2-compatibility fix already applied:
    botocore >=1.36 defaults to sending flexible-checksum headers (e.g.
    x-amz-checksum-crc32) on S3 requests - a documented source of
    SignatureDoesNotMatch against non-AWS S3-compatible providers like R2,
    which don't handle them the same way AWS does. Opting back out to the
    pre-1.36 behavior.

    Credential params default to None/"auto" and are forwarded straight to
    boto3.client("s3", ...) - leave them unset to fall back to boto3's
    normal credential resolution (env vars, ~/.aws/credentials, etc.)
    instead of passing secrets explicitly.
    """
    import boto3
    from botocore.config import Config

    client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        endpoint_url=endpoint_url,
        region_name=region_name,
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )
    cache_dir = resolve_cache_dir()
    if cache_dir:
        client = cache_get_object(client, cache_dir)
    return client


# get_object kwargs the cache knows how to key on. Anything else - a
# versioned read, a part number, SSE-C headers - bypasses the cache
# entirely rather than risking a hit that ignores the extra argument.
_CACHEABLE_GET_OBJECT_KWARGS = frozenset({"Bucket", "Key", "Range"})

# The only response fields anything downstream reads back: smart_open's
# Reader uses ContentLength/ContentRange/Body (plus ResponseMetadata,
# rebuilt below), S3LooseFS.openbin only Body. ETag is kept for debugging
# a cache entry by hand, not used.
_CACHED_RESPONSE_FIELDS = ("ContentLength", "ContentRange", "ETag", "ContentType")


def default_cache_dir():
    """Where the cache lives when nothing says otherwise: the platform's
    conventional cache location, which is the right place for data that can
    be deleted at any time without losing anything.
    """
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
        return os.path.join(base, "albam", "cache", "s3")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches/albam/s3")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, "albam", "s3")


def resolve_cache_dir():
    """The directory to cache into, or None for no caching.

    Unset means the platform default, so nobody has to opt in to get a
    working cache. Set to a path uses that path. Set to an empty string
    turns caching off - the one way to say "don't", since with a default in
    place unsetting the variable no longer means that.
    """
    configured = os.environ.get(CACHE_DIR_ENV_VAR)
    if configured is None:
        return default_cache_dir()
    configured = configured.strip()
    return configured or None


def _env_bytes(name, default):
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        print(f"{name}={raw!r} is not an integer number of bytes, using {default}")
        return default
    return max(0, value)


def _cache_entries(cache_dir):
    """(mtime, size, stem) for every complete entry, oldest first."""
    entries = []
    for root, _, files in os.walk(cache_dir):
        for name in files:
            if not name.endswith(".body"):
                continue
            body = os.path.join(root, name)
            meta = body[: -len(".body")] + ".json"
            try:
                size = os.path.getsize(body) + os.path.getsize(meta)
                mtime = os.path.getmtime(body)
            except OSError:
                continue  # vanished under us, or a half-written pair
            entries.append((mtime, size, body[: -len(".body")]))
    entries.sort()
    return entries


def prune_cache(cache_dir, max_bytes=None, min_free_bytes=None):
    """Evict least recently written entries until the cache fits under
    `max_bytes` and the filesystem has at least `min_free_bytes` free.

    Returns the number of bytes freed. Both limits matter: the absolute one
    bounds the cache on a machine with room to spare, and the free space one
    keeps it from being the last straw on a machine without.
    """
    max_bytes = DEFAULT_CACHE_MAX_BYTES if max_bytes is None else max_bytes
    min_free_bytes = DEFAULT_CACHE_MIN_FREE_BYTES if min_free_bytes is None else min_free_bytes

    entries = _cache_entries(cache_dir)
    total = sum(size for _, size, _ in entries)
    try:
        free = shutil.disk_usage(cache_dir).free
    except OSError:
        free = None

    freed = 0
    for _, size, stem in entries:
        over_size = total - freed > max_bytes
        low_disk = free is not None and (free + freed) < min_free_bytes
        if not (over_size or low_disk):
            break
        for path in (stem + ".body", stem + ".json"):
            try:
                os.unlink(path)
            except OSError:
                pass
        freed += size
    return freed


def _cache_entry_paths(cache_dir, kwargs):
    identity = json.dumps({k: kwargs[k] for k in sorted(kwargs)}, separators=(",", ":"))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    # two-level fanout: a full game root is tens of thousands of entries,
    # and a single flat directory that size is miserable to work with
    directory = os.path.join(cache_dir, digest[:2])
    return os.path.join(directory, digest[2:] + ".body"), os.path.join(directory, digest[2:] + ".json")


def _write_atomically(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_path, path)  # atomic, so a torn write is never read back
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def cache_get_object(client, cache_dir):
    """Wrap `client.get_object` with a content-addressed disk cache under
    `cache_dir`, keyed by (Bucket, Key, Range).

    This exists for development and test iteration, where the same handful
    of archives get re-fetched from scratch on every run - a full
    tests/mtfw/test_mod_serialization.py run pulls ~112MB in ~112 ranged
    requests, all of it identical to the run before. Nothing here helps end
    users, whose VFS reads local .arc files.

    Entries are validated by ETag before being served, once per object per
    process: the first cached range of a given key costs a head_object, and
    every other range of that same object rides on that answer. If the ETag
    moved, every cached range of that key is stale by definition, so the
    read falls through to the server and re-populates. That is worth the
    request - not caching at all is the only alternative that's also
    correct, and an object being re-uploaded under a name already in the
    cache is not hypothetical: the moto-backed tests recreate one bucket
    and key with different synthetic bytes in test after test, and without
    validation they get served each other's content.

    Ranges are cached as themselves rather than assembled into whole
    objects, so this stays correct for smart_open's chunked reads without
    ever materializing a 40MB archive to serve an 8 byte header read.
    """
    real_get_object = client.get_object
    live_etags = {}  # (bucket, key) -> ETag, one head_object per object per process
    max_bytes = _env_bytes(CACHE_MAX_BYTES_ENV_VAR, DEFAULT_CACHE_MAX_BYTES)
    min_free_bytes = _env_bytes(CACHE_MIN_FREE_BYTES_ENV_VAR, DEFAULT_CACHE_MIN_FREE_BYTES)
    written_since_prune = [0]

    def prune(force=False):
        if not force and written_since_prune[0] < PRUNE_INTERVAL_BYTES:
            return
        written_since_prune[0] = 0
        if os.path.isdir(cache_dir):
            prune_cache(cache_dir, max_bytes, min_free_bytes)

    def room_to_write(size):
        """Never write the entry that takes the filesystem below the floor.
        Checked per write because a single run can fetch hundreds of MB, and
        an entry refused now is just a cache miss later."""
        try:
            free = shutil.disk_usage(cache_dir if os.path.isdir(cache_dir) else ".").free
        except OSError:
            return True  # can't tell: behave as before rather than refuse
        return free - size >= min_free_bytes

    prune(force=True)

    def current_etag(bucket, key):
        identity = (bucket, key)
        if identity not in live_etags:
            try:
                live_etags[identity] = client.head_object(Bucket=bucket, Key=key).get("ETag")
            except Exception:
                live_etags[identity] = None  # can't tell: treat every entry as stale
        return live_etags[identity]

    def get_object(**kwargs):
        if not _CACHEABLE_GET_OBJECT_KWARGS.issuperset(kwargs):
            return real_get_object(**kwargs)

        body_path, meta_path = _cache_entry_paths(cache_dir, kwargs)
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            with open(body_path, "rb") as f:
                body = f.read()
        except (OSError, ValueError):
            pass  # miss, or an unreadable/half-written entry: just re-fetch
        else:
            etag = meta.get("ETag")
            if etag is not None and etag == current_etag(kwargs["Bucket"], kwargs["Key"]):
                return _cached_response(meta, body)

        response = real_get_object(**kwargs)
        body = response["Body"].read()
        if room_to_write(len(body)):
            meta = {k: response[k] for k in _CACHED_RESPONSE_FIELDS if k in response}
            _write_atomically(body_path, body)
            _write_atomically(meta_path, json.dumps(meta).encode("utf-8"))
            written_since_prune[0] += len(body)
            prune()
        response["Body"] = io.BytesIO(body)  # already consumed above
        return response

    client.get_object = get_object
    return client


def _cached_response(meta, body):
    return {
        **meta,
        "Body": io.BytesIO(body),
        # smart_open reads both of these off every response
        "ResponseMetadata": {
            "HTTPStatusCode": 206 if "ContentRange" in meta else 200,
            "RetryAttempts": 0,
        },
    }


def s3_opener(client, bucket, range_chunk_size=1024 * 1024):
    """Build an `opener(key) -> file-like` backed by an S3-compatible
    bucket (R2 works here too - just point `client` at R2's endpoint).
    Uses smart_open so seek()/read() become real HTTP Range requests
    instead of downloading the whole (possibly huge) file: `defer_seek=True`
    means opening the file doesn't even issue a request until the first
    read.

    range_chunk_size matters more than it looks: smart_open's default
    (`None`) issues an *open-ended* Range request (`bytes=N-`) whose
    Content-Length covers everything from N to EOF - i.e. reading 8 bytes
    from the start of a 40MB file asks the server for the full remaining
    40MB (confirmed against real fixture .arc files, not just guessed).
    Setting range_chunk_size bounds every underlying GET to that span;
    reads larger than one chunk transparently issue more (still bounded)
    requests. 1MiB is a reasonable default - large enough that a typical
    archive header/file-table fits in one request, small enough that
    reading one entry only costs a handful of requests instead of one that
    could be tens of MB.
    """
    import smart_open

    def opener(key):
        return smart_open.open(
            f"s3://{bucket}/{key}",
            "rb",
            transport_params={
                "client": client,
                "defer_seek": True,
                "range_chunk_size": range_chunk_size,
            },
        )

    return opener


class S3LooseFS(FS):
    """Read-only view of every object under `prefix` in an S3-compatible
    bucket as a plain filesystem - the S3/R2 equivalent of a local
    OSFS(game_root) layer for loose/unpacked files sitting directly in a
    real game install. Shared as the loose-file layer for both
    MTFW_FS.from_s3 and ReenFS.from_s3.

    Assumes the bucket mirrors a real game root exactly: no explicit
    directory-marker objects, and everything under `prefix` (archives
    themselves included) is legitimately part of the game data.
    """

    def __init__(self, client, bucket, prefix=""):
        super().__init__()
        self.client = client
        self.bucket = bucket
        self.prefix = prefix.strip("/")

    def __repr__(self):
        return f"S3LooseFS({self.bucket!r}, prefix={self.prefix!r})"

    def _key(self, path):
        _path = self.validatepath(path).strip("/")
        if self.prefix:
            return f"{self.prefix}/{_path}" if _path else self.prefix
        return _path

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()

        if _path == "/":
            return Info({"basic": {"name": "", "is_dir": True}})

        key = self._key(_path)
        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception:
            head = None

        if head is not None:
            raw_info = {"basic": {"name": basename(_path), "is_dir": False}}
            if "details" in namespaces:
                raw_info["details"] = {"type": int(ResourceType.file), "size": head["ContentLength"]}
            return Info(raw_info)

        # not a real object at this exact key - does anything live "under" it?
        resp = self.client.list_objects_v2(Bucket=self.bucket, Prefix=key + "/", MaxKeys=1)
        if resp.get("KeyCount", 0) > 0:
            raw_info = {"basic": {"name": basename(_path), "is_dir": True}}
            if "details" in namespaces:
                raw_info["details"] = {"type": int(ResourceType.directory), "size": 0}
            return Info(raw_info)

        raise ResourceNotFound(path)

    def listdir(self, path):
        return [info.name for info in self.scandir(path)]

    def scandir(self, path, namespaces=None, page=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()

        if not self.getinfo(_path).is_dir:
            raise DirectoryExpected(path)

        key_prefix = self._key(_path)
        if key_prefix and not key_prefix.endswith("/"):
            key_prefix += "/"

        entries = []
        paginator = self.client.get_paginator("list_objects_v2")
        for result in paginator.paginate(Bucket=self.bucket, Prefix=key_prefix, Delimiter="/"):
            for common_prefix in result.get("CommonPrefixes", ()):
                name = common_prefix["Prefix"][len(key_prefix):].rstrip("/")
                if name:
                    entries.append(Info({"basic": {"name": name, "is_dir": True}}))
            for obj in result.get("Contents", ()):
                name = obj["Key"][len(key_prefix):]
                if name:
                    raw_info = {"basic": {"name": name, "is_dir": False}}
                    if "details" in namespaces:
                        raw_info["details"] = {"type": int(ResourceType.file), "size": obj["Size"]}
                    entries.append(Info(raw_info))

        if page is not None:
            start, end = page
            entries = entries[start:end]
        return iter(entries)

    def openbin(self, path, mode="r", buffering=-1, **options):
        self.check()
        if "w" in mode or "+" in mode or "a" in mode:
            raise ResourceReadOnly(path)

        _path = self.validatepath(path)
        key = self._key(_path)
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except Exception:
            raise ResourceNotFound(path)
        return io.BytesIO(response["Body"].read())

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)
