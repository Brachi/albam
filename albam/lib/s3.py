"""
Shared S3/R2-compatible client + opener/filesystem helpers.

Used by both MT Framework's MTFW_FS.from_s3 (albam/engines/mtfw/arc_fs.py)
and RE Engine's PakFS.from_s3/ReenFS.from_s3 (albam/engines/reng/pak_fs.py)
- nothing engine-specific in any of these, so they live here instead of
being duplicated (or one engine importing the other's module).
"""
import io

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import DirectoryExpected, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.path import basename


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

    return boto3.client(
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
