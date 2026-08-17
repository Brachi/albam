"""
Shared R2 credential/config resolution for real-Cloudflare-R2-backed tests
(test_arc_fs_r2.py, test_mod_serialization.py's local round-trip tests) -
see .env.example for the expected keys.

One shared bucket for every app_id; each app_id's game root lives under a
prefix equal to the app_id itself (e.g. re5's game root is
s3://<bucket>/re5/..., mirroring the real game's own folder structure from
there down).
"""
import os


def r2_kwargs_for_app(app_id):
    """
    MTFW_FS.from_s3() kwargs for app_id, or None if R2 isn't usable (the
    optional s3 extras aren't installed, or credentials aren't configured) -
    callers should treat None as "skip cleanly".
    """
    try:
        import boto3  # noqa: F401
        from dotenv import load_dotenv
    except ImportError:
        return None

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(repo_root, ".env"))

    required = ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME")
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
        bucket=values["R2_BUCKET_NAME"],
        prefix=app_id,
        endpoint_url=f"https://{values['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=values["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=values["R2_SECRET_ACCESS_KEY"],
    )
