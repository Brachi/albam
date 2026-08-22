"""
Generates tests/mtfw/datasets/<app_id>_catalog.json: a hashed catalog of
every file in a local game install (loose + archived) via MTFW_FS. No
plain-text game asset paths get committed - only sha256-truncated hashes
(see catalog_paths.py for the full rationale and the game-root-relative
identity problem this solves).

This is a real maintainer/owner-run tool, not part of CI or routine test
runs.

Usage:
    python tests/mtfw/scripts/generate_catalog.py <app-id> <game-root>

Example:
    python tests/mtfw/scripts/generate_catalog.py re5 "/path/to/Resident Evil 5"
"""
import argparse
import json
import os
import sys
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "mtfw", "datasets")

sys.path.insert(0, _REPO_ROOT)

from albam.engines.mtfw.arc_fs import MTFW_FS  # noqa: E402
from tests.mtfw.scripts.catalog_paths import hash_virtual_path  # noqa: E402

# extension -> tag name. Extension-only for this iteration - trusting a
# renamed/misidentified file's extension over its actual content. Reading
# every file to check id_magic (e.g. b"MOD\x00" for .mod) is the correct,
# more robust approach discussed, but decompressing all ~100k+ entries in a
# full game install to peek at a few header bytes made this impractically
# slow as a first pass; came back to it once this stops being a prototype.
# TODO: verify tags via id_magic (or other real header data) instead of
# trusting the extension alone.
TAG_CHECKS = {
    "mod": "mod",
}


def detect_tags(path):
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    tag = TAG_CHECKS.get(ext)
    return [tag] if tag else []


def generate_catalog(game_root, progress_every=5000):
    game_fs = MTFW_FS(game_root)
    entries = []

    paths = list(game_fs.walk.files())
    for i, path in enumerate(paths):
        if progress_every and i and i % progress_every == 0:
            print(f"  ...{i}/{len(paths)}", file=sys.stderr)

        # origin_of() already returns a game-root-relative identity (see
        # arc_fs.py) - only case-normalization is left to do, same as any
        # other portable identity here, hence hash_virtual_path over
        # hash_relative_path (which expects an absolute path).
        origin = game_fs.origin_of(path)
        entries.append({
            "path_hash": hash_virtual_path(path),
            "archived": origin is not None,
            "archive_hash": hash_virtual_path(origin) if origin else None,
            "tags": detect_tags(path),
        })

    entries.sort(key=lambda e: e["path_hash"])
    return entries


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument(
        "-o", "--out", default=None,
        help="Output path (default: tests/mtfw/datasets/<app_id>_catalog.json)",
    )
    args = parser.parse_args()

    t0 = time.time()
    entries = generate_catalog(args.game_root)
    elapsed = time.time() - t0

    out_path = args.out or os.path.join(DATASETS_DIR, f"{args.app_id}_catalog.json")
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    archived_count = sum(1 for e in entries if e["archived"])
    tagged_count = sum(1 for e in entries if e["tags"])
    print(f"wrote {out_path} in {elapsed:.1f}s")
    print(f"  total entries: {len(entries)}")
    print(f"  archived: {archived_count}, loose: {len(entries) - archived_count}")
    print(f"  tagged: {tagged_count}")


if __name__ == "__main__":
    main()
