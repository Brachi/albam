"""
Shared R2 credential/config resolution for real-Cloudflare-R2-backed tests
(test_arc_fs_r2.py, test_origin_arc_path.py, scripts/test_catalog_paths.py,
test_mod_serialization.py's local round-trip tests, tests/reng's --game-dir
r2:// support) - see .env.example for the expected keys.

Credentials (R2_ACCOUNT_ID/R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY) always
come from env vars - never from a CLI flag or anything committed. Two ways
to get bucket/prefix, for two different callers:

- r2_kwargs_for_app(app_id): bucket=R2_BUCKET_NAME (env), prefix=app_id -
  for tests that hardcode a real app_id and need R2 config directly, with
  no --game-dir/CLI involved at all (test_arc_fs_r2.py and others above).
- resolve_r2_source(value): for --game-dir's own r2:// values specifically
  - always explicit ("r2://<bucket>/<prefix>", e.g. "r2://albam/re5"), no
  bare "r2://" that derives bucket/prefix from env/app_id itself. CI gets
  the same explicitness by interpolating a secret directly into the
  workflow's --game-dir value (${{ secrets.R2_BUCKET_NAME }}) rather than
  this resolving a bucket name from env on the CLI-parsing side.
"""
import os

R2_PROTOCOL_PREFIX = "r2://"


def r2_credentials():
    """endpoint_url/aws_access_key_id/aws_secret_access_key for
    *_FS.from_s3() - always sourced from env vars, or None if the optional
    s3 extras aren't installed or credentials aren't fully configured.
    """
    try:
        import boto3  # noqa: F401
        from dotenv import load_dotenv
    except ImportError:
        return None

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(repo_root, ".env"))

    required = ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
    # .strip(): a trailing newline in a GitHub Actions secret's value (an
    # easy copy-paste artifact) silently pollutes every signed request built
    # from it - botocore doesn't strip these itself, and the failure mode is
    # an opaque SignatureDoesNotMatch with no hint the credential itself is
    # the problem. Confirmed via a real CI traceback showing
    # api_params={'Bucket': '***\n', ...}.
    values = {k: os.environ.get(k, "").strip() for k in required}
    if not all(values.values()):
        return None

    return dict(
        endpoint_url=f"https://{values['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=values["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=values["R2_SECRET_ACCESS_KEY"],
    )


def r2_kwargs_for_app(app_id):
    """
    *_FS.from_s3() kwargs for app_id with bucket/prefix resolved entirely
    from env (bucket=R2_BUCKET_NAME, prefix=app_id), or None if R2 isn't
    usable. For tests that hardcode a real app_id directly (no --game-dir
    involved) - see module docstring. --game-dir's own r2:// parsing uses
    resolve_r2_source() instead, which never derives bucket/prefix from
    env/app_id on its own.
    """
    creds = r2_credentials()
    if creds is None:
        return None
    bucket = os.environ.get("R2_BUCKET_NAME", "").strip()
    if not bucket:
        return None
    return dict(bucket=bucket, prefix=app_id, **creds)


def resolve_r2_source(value):
    """
    Resolve an explicit --game-dir "r2://<bucket>/<prefix>" value into full
    *_FS.from_s3() kwargs, or None if unresolvable - an empty bucket (bare
    "r2://", or a CI secret that isn't configured yet and interpolated in
    as an empty string - both look identical here) or missing credentials.
    Callers treat None as "skip cleanly", same as any other R2-unavailable
    case - deliberately not a hard error, so CI without the R2 secrets
    configured keeps skipping instead of failing outright. `value` must
    start with R2_PROTOCOL_PREFIX.
    """
    assert value.startswith(R2_PROTOCOL_PREFIX)
    suffix = value[len(R2_PROTOCOL_PREFIX):]
    bucket, _sep, prefix = suffix.partition("/")
    # .strip(): same trailing-newline-in-a-secret defense as r2_credentials -
    # belt and suspenders on top of the CI-side stripping (see
    # .github/workflows/tests.yml), in case bucket ever reaches here
    # unstripped from some other caller.
    bucket = bucket.strip()
    prefix = prefix.strip()
    if not bucket:
        return None

    creds = r2_credentials()
    if creds is None:
        return None
    return dict(bucket=bucket, prefix=prefix, **creds)
