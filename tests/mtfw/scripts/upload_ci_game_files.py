"""
Uploads to R2 exactly the game files an app_id's CI run needs - the .arc
archives (and loose files) backing the committed dataset hashes - and
nothing else.

A full game install is far too large to mirror, and most of it is never
read: the committed datasets reference a few dozen files out of ~60k-100k
catalog entries. This resolves that reference set against a local install
and uploads only the archives that actually back it, under the same
"<bucket>/<app_id>/<game-root-relative path>" layout MTFW_FS.from_s3()
expects (see .env.example and albam/engines/mtfw/arc_fs.py).

Only app_ids the CI workflow actually passes a --game-dir for are
uploadable. Uploading data for an app_id CI never mounts would cost bucket
space and egress to back tests that skip anyway, so this refuses and says
which flag is missing rather than uploading dead weight - the workflow is
the source of truth for what CI runs, not this script's own list.

Credentials come from env/.env exactly as the tests read them (see
tests/mtfw/r2_config.py); no credential is ever taken from a CLI flag.

This is a real maintainer/owner-run tool, not part of CI or routine test
runs - same as generate_catalog.py alongside it.

Usage:
    python tests/mtfw/scripts/upload_ci_game_files.py --app-id re5 \
        --game-root "/path/to/Resident Evil 5" [--dry-run]

Note on completeness: whole .arc archives are uploaded, so a referenced
file's siblings (a .mod's .mrl, its textures) come along automatically when
they live in the same archive - which is the usual layout. A test needing a
file from an archive nothing in the datasets references would still fail to
resolve it; that surfaces as a test failure naming the missing path, and
the fix is to add that file's hash to the relevant dataset and re-run this.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "mtfw", "datasets")
DEFAULT_WORKFLOW = os.path.join(_REPO_ROOT, ".github", "workflows", "tests.yml")

sys.path.insert(0, _REPO_ROOT)

from tests.mtfw.r2_config import r2_credentials  # noqa: E402
from tests.mtfw.scripts.catalog_paths import resolve_hashes  # noqa: E402

# albam.engines.* is imported lazily, inside resolve_upload_set(): importing
# albam pulls in bpy, and everything before resolution - the CI gate, the
# dataset and catalog checks, --help - is plain JSON/text work that has no
# reason to need Blender installed. It also keeps the "CI does not run this
# app_id" refusal usable from any interpreter.

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


def dataset_hashes_for(app_id):
    """{path_hash: [dataset file names]} for every committed dataset entry
    belonging to app_id.

    The dataset file names come along so the report can say what a given
    file is needed *for* - useful when deciding whether a large archive is
    worth uploading.
    """
    hashes = {}
    for path in sorted(glob.glob(os.path.join(DATASETS_DIR, "*_hashes.json"))):
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
    path = os.path.join(DATASETS_DIR, f"{app_id}_catalog.json")
    if not os.path.isfile(path):
        raise SystemExit(
            f"no catalog for app_id={app_id!r} at {path} - generate one first:\n"
            f"    python tests/mtfw/scripts/generate_catalog.py {app_id} <game-root>"
        )
    with open(path) as f:
        return {e["path_hash"]: e for e in json.load(f)}


# A .mod's material library sits beside it under one of these suffixes, and
# its textures are named without an extension - both mirrored from the
# importer (_infer_mrl in material.py, build_blender_textures in texture.py).
# Keep them in step: a model whose .mrl or textures live in an archive
# nothing uploaded imports with empty image nodes rather than failing
# outright, which is exactly what test_mod_import_textures_are_resolved
# caught for all 59 umvc3 characters.
MRL_SUFFIXES = (".mrl", "_0.mrl", "_1.mrl", "_2.mrl", "_3.mrl")
TEXTURE_EXTENSIONS = (".tex", ".rtex")


def _first_existing(game_fs, candidates):
    for candidate in candidates:
        if game_fs.exists(candidate):
            return candidate
    return None


def mod_dependencies(game_fs, app_id, mod_path):
    """(paths, unresolved) for the .mrl and textures `mod_path` needs.

    Resolution follows the importer exactly rather than guessing at a
    naming convention: the .mrl by suffix, then every texture_path it
    lists, .tex first and .rtex second. `unresolved` names the texture
    paths this install has no file for - not fatal (the importer itself
    only warns), but worth reporting, since an upload can't include what
    isn't there.
    """
    from albam.engines.mtfw.structs.mrl import Mrl
    from albam.lib.kaitai_utils import parse

    base = mod_path[:-len(".mod")] if mod_path.lower().endswith(".mod") else mod_path
    mrl_path = _first_existing(game_fs, [base + suffix for suffix in MRL_SUFFIXES])
    if mrl_path is None:
        return set(), set()

    paths = {mrl_path}
    unresolved = set()
    try:
        with game_fs.openbin(mrl_path) as f:
            mrl = parse(Mrl, f.read(), app_id)
    except Exception as e:
        # A .mrl this tool can't parse is a real gap, but not one to abort
        # a whole upload over - report it as unresolved and carry on.
        return paths, {f"{mrl_path} (unparsed: {e})"}

    for texture in mrl.textures:
        texture_path = getattr(texture, "texture_path", None)
        if not texture_path:
            continue
        normalized = "/" + texture_path.replace("\\", "/").lstrip("/")
        found = _first_existing(game_fs, [normalized + ext for ext in TEXTURE_EXTENSIONS])
        if found:
            paths.add(found)
        else:
            unresolved.add(texture_path)
    return paths, unresolved


def resolve_upload_set(game_root, app_id, hashes):
    """{absolute local path: game-root-relative key suffix} for the files
    backing `hashes`.

    An archived hash contributes the whole .arc that holds it (many hashes
    usually collapse onto one archive); a loose hash contributes the file
    itself. Resolution is forward-only - hashes are matched by walking the
    install and hashing what's there, never by turning a hash back into a
    path - so a hash that doesn't correspond to this install fails loudly
    via resolve_hashes rather than silently uploading the wrong thing.
    """
    try:
        from albam.engines.mtfw.arc_fs import MTFW_FS
    except ImportError as e:
        # albam imports bpy at package level, so this tool needs the same
        # environment the tests run in. Worth naming outright: the traceback
        # alone points at albam/__init__.py and reads like a repo problem.
        raise SystemExit(
            f"cannot import albam ({e}) - run this with the same interpreter as the "
            f"test suite, e.g. .venv/bin/python with bpy installed"
        )

    game_fs = MTFW_FS(game_root)
    resolved = resolve_hashes(game_fs, hashes)

    # A .mod alone isn't importable: its .mrl and every texture that .mrl
    # names have to be reachable too, and they routinely live in other
    # archives. Expand before mapping to archives so those come along.
    wanted = set(resolved.values())
    unresolved = set()
    for virtual_path in sorted(resolved.values()):
        if not virtual_path.lower().endswith(".mod"):
            continue
        deps, missing = mod_dependencies(game_fs, app_id, virtual_path)
        wanted |= deps
        unresolved |= missing

    uploads = {}
    for virtual_path in sorted(wanted):
        absolute = game_fs.origin_absolute_path(virtual_path)
        if absolute is None:
            # Loose file: no owning archive, so the file itself is what CI
            # needs. MTFW_FS mounts loose files from an OSFS rooted at
            # game_root, so the virtual path is already the relative one.
            absolute = os.path.join(game_root, virtual_path.lstrip("/"))
        relative = os.path.relpath(absolute, game_root).replace(os.sep, "/")
        uploads[absolute] = relative

    if unresolved:
        print(f"  {len(unresolved)} texture path(s) named by a .mrl are not in this "
              f"install - the importer only warns about these, so they are left out:")
        for path in sorted(unresolved)[:10]:
            print(f"    {path}")
        if len(unresolved) > 10:
            print(f"    ... and {len(unresolved) - 10} more")

    print(f"  {len(resolved)} referenced file(s) pulled in {len(wanted) - len(resolved)} "
          f"dependency file(s) (.mrl + textures)")
    return uploads, resolved


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
