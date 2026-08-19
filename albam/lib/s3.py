"""
Shared S3/R2-compatible client + opener helpers.

Used by both MT Framework's MTFW_FS.from_s3 (albam/engines/mtfw/arc_fs.py)
and RE Engine's PakFS.from_s3 (albam/engines/reng/pak_fs.py) - nothing
engine-specific in either helper, so it lives here instead of being
duplicated (or one engine importing the other's module).
"""


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
