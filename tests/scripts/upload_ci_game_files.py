"""
Uploads to R2 exactly the game files an app_id's CI run needs - the archives
(and loose files) backing the committed dataset hashes - and nothing else.

A full game install is far too large to mirror, and most of it is never
read: the committed datasets reference a few dozen files out of ~60k-100k
catalog entries. This resolves that reference set against a local install
and uploads only the files that actually back it, under the same
"<bucket>/<app_id>/<game-root-relative path>" layout the tests mount from
(see .env.example).

Everything engine-specific - where the datasets live, how a hash becomes a
local file, and what else that file needs to be importable - is a
per-engine upload source module (tests/mtfw/upload_source.py,
tests/cie/upload_source.py). Adding an engine means adding one of those and
listing it in UPLOAD_SOURCES below; nothing else here changes.

Only app_ids the CI workflow actually passes a --game-dir for are
uploadable. Uploading data for an app_id CI never mounts would cost bucket
space and egress to back tests that skip anyway, so this refuses and says
which flag is missing rather than uploading dead weight - the workflow is
the source of truth for what CI runs, not this script's own list.

Credentials come from env/.env exactly as the tests read them (see
tests/mtfw/r2_config.py); no credential is ever taken from a CLI flag.

This is a real maintainer/owner-run tool, not part of CI or routine test
runs - same as the generate_catalog.py scripts beside each engine's tests.

Usage:
    python tests/scripts/upload_ci_game_files.py --app-id re5 \
        --game-root "/path/to/game" [--dry-run]

Note on completeness: whole archives are uploaded, so a referenced file's
siblings come along automatically when they live in the same archive - which
is the usual layout. A test needing a file from an archive nothing in the
datasets references would still fail to resolve it; that surfaces as a test
failure naming the missing path, and the fix is to add that file's hash to
the relevant dataset and re-run this.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", ".."))
DEFAULT_WORKFLOW = os.path.join(_REPO_ROOT, ".github", "workflows", "tests.yml")

sys.path.insert(0, _REPO_ROOT)

from tests.cie import upload_source as cie_source  # noqa: E402
from tests.hexn import upload_source as hexn_source  # noqa: E402
from tests.mtfw import upload_source as mtfw_source  # noqa: E402
from tests.mtfw.r2_config import r2_credentials  # noqa: E402

# The engines this can upload for. Each module says where its datasets live
# and how to turn a set of hashes into local files; neither imports albam at
# module level, so the gate below stays usable from any interpreter.
UPLOAD_SOURCES = (mtfw_source, cie_source, hexn_source)

# Matches the app-id in a `--game-dir=<app-id>::<value>` flag as written in
# the workflow. Only the app-id is wanted: the value there is a shell
# expression ("r2://\"$R2_BUCKET_NAME\"/re5"), not something to interpret.
GAME_DIR_APP_ID_RE = re.compile(r"--game-dir=([A-Za-z0-9_.-]+)::")

# Every dataset entry key that holds a path hash - mod_path_hash,
# mrl_path_hash, tex_path_hash and so on. Matching on the suffix rather than
# listing them keeps a newly added asset type working without a change here.
PATH_HASH_KEY_SUFFIX = "_path_hash"

# Object metadata key (S3 lowercases these and strips the x-amz-meta- prefix
# on the way back out) holding the sha256 of the bytes that were uploaded.
# Size alone can't answer "is the object still current": an .arc repacked
# from the same entries can keep its exact length, and a false skip is the
# one staleness the tests' ETag-validated cache cannot catch - nothing was
# re-uploaded, so no ETag changed, and CI keeps reading the old bytes with
# no signal at all. ETag would only work for single-part uploads (multipart
# ETags aren't a plain digest), and .arc files routinely exceed the 8MiB
# multipart threshold, so a checksum we write ourselves is the reliable one.
CHECKSUM_METADATA_KEY = "albam-sha256"

# S3's DeleteObjects caps a single request at 1000 keys.
DELETE_BATCH_SIZE = 1000


def ci_app_ids(workflow_path):
    """app_ids the workflow passes a --game-dir for.

    Read out of the raw file rather than the parsed YAML: the flags live
    inside a `run:` block, so YAML parsing would just hand back the same
    shell script text to regex anyway, and this keeps the script working if
    the step is ever restructured.
    """
    with open(workflow_path) as f:
        return set(GAME_DIR_APP_ID_RE.findall(f.read()))


def upload_source_for(app_id):
    """The engine module owning app_id, or None if no engine claims it."""
    for source in UPLOAD_SOURCES:
        if app_id in source.APP_IDS:
            return source
    return None


def dataset_hashes_for(app_id):
    """{path_hash: [dataset file names]} for every committed dataset entry
    belonging to app_id.

    The dataset file names come along so the report can say what a given
    file is needed *for* - useful when deciding whether a large archive is
    worth uploading.
    """
    source = upload_source_for(app_id)
    if source is None:
        return {}
    hashes = {}
    for path in sorted(glob.glob(os.path.join(source.DATASETS_DIR, "*_hashes.json"))):
        name = os.path.basename(path)
        with open(path) as f:
            entries = json.load(f)
        for entry in entries:
            if entry.get("app_id") != app_id:
                continue
            for key, value in entry.items():
                if key.endswith(PATH_HASH_KEY_SUFFIX):
                    hashes.setdefault(value, []).append(name)
    return hashes


def load_catalog(app_id):
    source = upload_source_for(app_id)
    path = os.path.join(source.DATASETS_DIR, f"{app_id}_catalog.json")
    if not os.path.isfile(path):
        raise SystemExit(
            f"no catalog for app_id={app_id!r} at {path} - generate one first:\n"
            f"    " + source.CATALOG_COMMAND.format(app_id=app_id)
        )
    with open(path) as f:
        return {e["path_hash"]: e for e in json.load(f)}


def resolve_upload_set(game_root, app_id, hashes):
    """{absolute local path: key suffix} for the files backing `hashes`, and
    what those hashes resolved to, from the engine that owns app_id."""
    return upload_source_for(app_id).resolve_upload_set(game_root, app_id, hashes)


def size_upload_set(game_root, app_id, hashes):
    """(sized, total_bytes, error) for the files backing `hashes`.

    `sized` is [(absolute path, key suffix, size)] largest first, and
    `error` is a human-readable reason when the set couldn't be resolved at
    all - a game root that isn't there, an interpreter without bpy, or a
    hash this install doesn't contain. Returning the reason rather than
    raising lets the caller decide whether it's fatal: it is when an upload
    was going to follow, but not when the run was only ever going to report
    what an unsupported app_id would cost.
    """
    try:
        from fs.errors import FSError
    except ImportError:
        # pyfilesystem comes in with albam; without it the albam import below
        # fails first anyway, so OSError alone is a fine stand-in here.
        FSError = OSError

    if not os.path.isdir(game_root):
        return [], 0, f"--game-root {game_root!r} is not a directory"

    print(f"resolving against {game_root} ...")
    try:
        uploads, _resolved = resolve_upload_set(game_root, app_id, hashes)
    except SystemExit as e:
        # resolve_upload_set raises this for a missing albam/bpy - the one
        # environmental failure that isn't about the install's contents.
        return [], 0, str(e)
    except KeyError as e:
        return [], 0, f"not found in this game install: {e}"
    except (OSError, FSError) as e:
        # Walking a game root that isn't one (or has unreadable subtrees)
        # surfaces here - pyfilesystem raises its own FSError hierarchy,
        # which is not an OSError subclass, so both are needed.
        return [], 0, f"cannot read {game_root!r}: {e}"

    sized = sorted(
        ((path, key, os.path.getsize(path)) for path, key in uploads.items()),
        key=lambda item: -item[2],
    )
    return sized, sum(size for _p, _k, size in sized), None


def file_checksum(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def remote_state(client, bucket, key):
    """(size, checksum or None) for an existing object, or None if absent.

    The checksum is None for anything uploaded before this tool wrote the
    metadata (or put there by other means), which the caller treats as
    "can only compare by size" rather than as a mismatch.
    """
    from botocore.exceptions import ClientError

    try:
        head = client.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            return None
        raise
    return head["ContentLength"], head.get("Metadata", {}).get(CHECKSUM_METADATA_KEY)


def existing_objects(client, bucket, prefix):
    """{key: size} already in the bucket under prefix, for skip-if-unchanged."""
    found = {}
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            found[obj["Key"]] = obj["Size"]
    return found


def human(num_bytes):
    for unit in ("B", "KiB", "MiB", "GiB"):
        if num_bytes < 1024 or unit == "GiB":
            return f"{num_bytes:.1f}{unit}" if unit != "B" else f"{num_bytes}B"
        num_bytes /= 1024


def main(argv=None):
    """argv is taken as a parameter (rather than read from sys.argv) so the
    decision layer above can be exercised directly from a test."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--app-id", required=True, help="e.g. re5")
    parser.add_argument("--game-root", required=True, help="local game install root")
    parser.add_argument(
        "--bucket", default=None,
        help="target bucket (default: $R2_BUCKET_NAME, same as the tests use)",
    )
    parser.add_argument(
        "--workflow", default=DEFAULT_WORKFLOW,
        help="workflow to read --game-dir app-ids from (default: .github/workflows/tests.yml)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="report what would be uploaded and deleted, then stop",
    )
    parser.add_argument(
        "--delete", action="store_true",
        help="also delete objects under <app_id>/ that no committed dataset hash "
             "resolves to (the bucket otherwise only grows as datasets change)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="re-upload every referenced file, skipping the unchanged check "
             "(also the way to give a pre-existing object a stored checksum)",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="skip the confirmation prompt",
    )
    args = parser.parse_args(argv)
    app_id = args.app_id
    allowed = ci_app_ids(args.workflow)
    in_ci = app_id in allowed

    hashes = dataset_hashes_for(app_id)
    if not hashes:
        print(f"NOTHING UPLOADED: no committed dataset entry references app_id={app_id!r}.",
              file=sys.stderr)
        return 2

    # Same invariant test_dataset_hashes_are_in_catalog enforces in the suite:
    # a dataset hash outside the catalog means the dataset and the catalog
    # disagree, and uploading against it would bake that in.
    catalog = load_catalog(app_id)
    missing = sorted(h for h in hashes if h not in catalog)
    if missing:
        print(f"NOTHING UPLOADED: {len(missing)} dataset hash(es) for {app_id!r} are not in "
              f"its catalog: {missing}", file=sys.stderr)
        return 2

    print(f"{app_id}: {len(hashes)} referenced file(s) across "
          f"{len({n for names in hashes.values() for n in names})} dataset(s)")

    # Sizing runs before the CI gate, and its failures are only fatal when
    # the upload could actually have gone ahead. For an app_id CI doesn't
    # run, the size is the whole point of the report - "this is what
    # enabling it would cost" - so a game root that can't be resolved
    # against downgrades to an unsized refusal instead of an error.
    sized, total, sizing_error = size_upload_set(args.game_root, app_id, hashes)
    if sizing_error and in_ci:
        sys.stdout.flush()  # keep the report above ahead of this, as in the refusal below
        print(f"NOTHING UPLOADED: {sizing_error}", file=sys.stderr)
        return 2
    if sizing_error:
        print(f"  (upload size unknown: {sizing_error})")
    else:
        print(f"\n{len(sized)} file(s) back those {len(hashes)} hashes, "
              f"{human(total)} total:")
        for _path, key, size in sized:
            print(f"  {human(size):>9}  {key}")

    if not in_ci:
        size_note = (
            f"  {human(total)} across {len(sized)} file(s) would be uploaded if it did.\n"
            if not sizing_error else "  The upload size could not be computed.\n"
        )
        # The report above goes to stdout and this goes to stderr; without a
        # flush the two arrive out of order whenever stdout is a pipe.
        sys.stdout.flush()
        print(
            f"\nNOTHING UPLOADED: CI does not run app_id={app_id!r}.\n\n"
            f"  {os.path.relpath(args.workflow, _REPO_ROOT)} passes --game-dir for: "
            f"{', '.join(sorted(allowed)) or '(none)'}\n"
            f"{size_note}\n"
            f"Every {app_id} test skips in CI, so uploading its game data would cost\n"
            f"bucket space and egress to back tests that never run. To make {app_id}\n"
            f"uploadable, add it to the pytest command in that workflow first:\n\n"
            f"    --game-dir={app_id}::r2://\"$R2_BUCKET_NAME\"/{app_id}\n\n"
            f"then re-run this script.",
            file=sys.stderr,
        )
        return 2

    if args.dry_run and not args.delete:
        # Stop before credentials: sizing an upload is useful on its own, and
        # asking for R2 config to answer "how big is this" would be noise.
        # --delete has to list the bucket, so it goes the long way round.
        print("\n--dry-run: nothing uploaded")
        return 0

    creds = r2_credentials()
    if creds is None:
        print("\nNOTHING UPLOADED: R2 is not configured (missing s3 extras or credentials) - "
              "see .env.example", file=sys.stderr)
        return 2
    bucket = args.bucket or os.environ.get("R2_BUCKET_NAME", "").strip()
    if not bucket:
        print("\nNOTHING UPLOADED: no bucket - pass --bucket or set R2_BUCKET_NAME",
              file=sys.stderr)
        return 2

    import boto3

    client = boto3.client("s3", region_name="auto", **creds)
    desired = {f"{app_id}/{key}": (path, size) for path, key, size in sized}

    pending = []
    verified = 0
    assumed = 0
    for full_key, (path, size) in desired.items():
        if args.force:
            pending.append((path, full_key, size))
            continue
        state = remote_state(client, bucket, full_key)
        if state is None:
            pending.append((path, full_key, size))
            continue
        remote_size, remote_digest = state
        if remote_digest is None:
            # Uploaded before this tool recorded checksums (or by other
            # means): size is all there is to compare, so a same-size object
            # is skipped without ever having been verified. --force is the
            # way to replace one and give it a checksum for next time.
            if remote_size == size:
                assumed += 1
                continue
        elif remote_digest == file_checksum(path):
            verified += 1
            continue
        pending.append((path, full_key, size))

    if verified:
        print(f"\n{verified} unchanged (checksum verified)")
    if assumed:
        print(f"{assumed} assumed unchanged (same size, no stored checksum - "
              f"--force replaces them)")

    stale = []
    if args.delete:
        # Only safe because the desired set was fully resolved: sizing
        # failures are fatal for an app_id CI runs (checked above), so this
        # can never be reached with a partial set that would make live
        # objects look stale.
        stale = sorted(
            ((key, size) for key, size in existing_objects(client, bucket, f"{app_id}/").items()
             if key not in desired),
            key=lambda item: -item[1],
        )
        if stale:
            stale_bytes = sum(size for _k, size in stale)
            print(f"\n{len(stale)} stale object(s) under {app_id}/, {human(stale_bytes)} "
                  f"- no committed dataset hash resolves to them:")
            for key, size in stale:
                print(f"  {human(size):>9}  {key}")
        else:
            print(f"\nno stale objects under {app_id}/")

    if not pending and not stale:
        print("\nnothing to do")
        return 0

    pending_bytes = sum(size for _p, _k, size in pending)
    if pending:
        print(f"\nuploading {len(pending)} file(s), {human(pending_bytes)} "
              f"to s3://{bucket}/{app_id}/")
    if stale:
        print(f"deleting {len(stale)} object(s) from s3://{bucket}/{app_id}/")

    if args.dry_run:
        print("\n--dry-run: nothing uploaded or deleted")
        return 0
    if not args.yes:
        if input("proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            print("aborted, nothing uploaded or deleted")
            return 1

    for i, (path, full_key, size) in enumerate(pending, 1):
        print(f"  [{i}/{len(pending)}] {human(size):>9}  {full_key}")
        client.upload_file(
            path, bucket, full_key,
            ExtraArgs={"Metadata": {CHECKSUM_METADATA_KEY: file_checksum(path)}},
        )

    for i in range(0, len(stale), DELETE_BATCH_SIZE):
        batch = stale[i:i + DELETE_BATCH_SIZE]
        client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": key} for key, _size in batch]},
        )
        print(f"  deleted {len(batch)} object(s)")

    if pending:
        print(f"\nuploaded {len(pending)} file(s), {human(pending_bytes)}")
    if stale:
        print(f"deleted {len(stale)} stale object(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
