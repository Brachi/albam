"""
Generates tests/reng/datasets/<app_id>_catalog.json: a hashed catalog of
every candidate path PakFS actually matched in a real .pak (see
albam/engines/reng/pak_fs.py). No plain-text game asset paths get committed
- only sha256-truncated hashes, reusing the same hashing primitives as
tests/mtfw/scripts/catalog_paths.py (fully generic, nothing mtfw-specific in
them - see that module for the full rationale).

This is a real maintainer/owner-run tool, not part of CI or routine test
runs.

Usage:
    python tests/reng/scripts/generate_catalog.py <app-id> <pak-path> <path-list-path>

Example:
    python tests/reng/scripts/generate_catalog.py re3 \\
        "/path/to/RE3/re_chunk_000.pak" tests/data/re3/RE3Z_RT_STM_Release.list
"""
import argparse
import json
import os
import sys
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "reng", "datasets")

sys.path.insert(0, _REPO_ROOT)

from albam.engines.reng.pak_fs import PakFS  # noqa: E402
from tests.mtfw.scripts.catalog_paths import hash_virtual_path  # noqa: E402

# extension's first dot-segment (before the format-version numeric suffix,
# e.g. "mesh.2109108288" -> "mesh") -> tag name. Extension-only, same
# trust-the-extension caveat as tests/mtfw/scripts/generate_catalog.py.
TAG_CHECKS = {
    "mesh": "mesh",
    "tex": "texture",
}


def detect_tags(path):
    name = path.rsplit("/", 1)[-1]
    first_ext = name.split(".", 1)[-1].split(".", 1)[0].lower() if "." in name else ""
    tag = TAG_CHECKS.get(first_ext)
    return [tag] if tag else []


def generate_catalog(pak_path, path_list_path, progress_every=5000):
    pak_fs = PakFS(pak_path, path_list_path)
    entries = []

    paths = list(pak_fs.walk.files())
    pak_identity_hash = hash_virtual_path(os.path.basename(pak_path))
    for i, path in enumerate(paths):
        if progress_every and i and i % progress_every == 0:
            print(f"  ...{i}/{len(paths)}", file=sys.stderr)

        # Everything PakFS exposes comes from the one .pak - "archived" is
        # always true here (no loose-file overlay, unlike MTFW_FS), so
        # archive_hash just identifies the pak itself, not a specific one of
        # many like MTFW's per-.arc archive_hash does.
        entries.append({
            "path_hash": hash_virtual_path(path),
            "archived": True,
            "archive_hash": pak_identity_hash,
            "tags": detect_tags(path),
        })

    entries.sort(key=lambda e: e["path_hash"])
    return entries


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_id")
    parser.add_argument("pak_path")
    parser.add_argument("path_list_path")
    parser.add_argument(
        "-o", "--out", default=None,
        help="Output path (default: tests/reng/datasets/<app_id>_catalog.json)",
    )
    args = parser.parse_args()

    t0 = time.time()
    entries = generate_catalog(args.pak_path, args.path_list_path)
    elapsed = time.time() - t0

    out_path = args.out or os.path.join(DATASETS_DIR, f"{args.app_id}_catalog.json")
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    tagged_count = sum(1 for e in entries if e["tags"])
    print(f"wrote {out_path} in {elapsed:.1f}s")
    print(f"  total entries: {len(entries)}")
    print(f"  tagged: {tagged_count}")


if __name__ == "__main__":
    main()
