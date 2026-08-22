"""
Generates tests/hexn/datasets/<app_id>_catalog.json: a hashed catalog of
every file in a local RE:ORC install (loose + packed) via HexnFS. No
plain-text game asset paths get committed - only sha256-truncated hashes,
reusing the same hashing primitives as tests/mtfw/scripts/catalog_paths.py
(fully generic, nothing mtfw-specific in them - see that module for the
full rationale).

This is a real maintainer/owner-run tool, not part of CI or routine test
runs.

Usage:
    python tests/hexn/scripts/generate_catalog.py <app-id> <game-root>

Example:
    python tests/hexn/scripts/generate_catalog.py reorc \\
        "/path/to/Resident Evil Operation Raccoon City"
"""
import argparse
import json
import os
import sys
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
_VENDOR_DIR = os.path.join(_REPO_ROOT, "albam", "albam_vendor")
DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "hexn", "datasets")

# kaitaistruct (needed transitively by albam.engines.hexn.fs) only lives in
# albam's vendored copy, same as everywhere else in the codebase that
# imports engine modules outside of register()'s own sys.path setup.
sys.path.insert(0, _VENDOR_DIR)
sys.path.insert(0, _REPO_ROOT)

from albam.engines.hexn.fs import HexnFS  # noqa: E402
from tests.mtfw.scripts.catalog_paths import hash_virtual_path  # noqa: E402

# extension -> tag name. Extension-only for this iteration, same
# trust-the-extension caveat as tests/mtfw/scripts/generate_catalog.py.
TAG_CHECKS = {
    "edgemodel": "mesh",
    "matb": "material",
}


def detect_tags(path):
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    tag = TAG_CHECKS.get(ext)
    return [tag] if tag else []


def generate_catalog(game_root, progress_every=5000):
    game_fs = HexnFS(game_root)
    entries = []

    paths = list(game_fs.walk.files())
    for i, path in enumerate(paths):
        if progress_every and i and i % progress_every == 0:
            print(f"  ...{i}/{len(paths)}", file=sys.stderr)

        origin = game_fs.origin_of(path)
        entries.append({
            "path_hash": hash_virtual_path(path),
            "archived": origin is not None,
            "archive_hash": hash_virtual_path(origin) if origin else None,
            "tags": detect_tags(path),
        })

    entries.sort(key=lambda e: e["path_hash"])
    return entries, game_fs.failed_ssgs


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument(
        "-o", "--out", default=None,
        help="Output path (default: tests/hexn/datasets/<app_id>_catalog.json)",
    )
    args = parser.parse_args()

    t0 = time.time()
    entries, failed_ssgs = generate_catalog(args.game_root)
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
    if failed_ssgs:
        print(f"  failed to parse ({len(failed_ssgs)} .ssg, skipped):")
        for path, exc in failed_ssgs:
            print(f"    {os.path.basename(path)}: {exc}")


if __name__ == "__main__":
    main()
