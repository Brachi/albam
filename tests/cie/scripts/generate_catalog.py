"""
Generates tests/cie/datasets/re4uhd_catalog.json: a hashed catalog of every
.lfs archive in a local RE4 UHD install. No plain-text game asset paths get
committed - only sha256-truncated hashes (see
tests/mtfw/scripts/catalog_paths.py for the full rationale, whose hashing
this reuses).

Unlike MT Framework's and RE Engine's catalogs, this one lists archives
rather than the files inside them: an .lfs's file table lives inside its
compressed stream, so cataloguing contents would mean decompressing all
~4500 archives of an install (see albam/engines/cie/fs.py).

This is a real maintainer/owner-run tool, not part of CI or routine test
runs.

Usage:
    python tests/cie/scripts/generate_catalog.py <app-id> <game-root>

Example:
    python tests/cie/scripts/generate_catalog.py re4uhd "/path/to/Resident Evil 4"
"""
import argparse
import json
import os
import sys
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "cie", "datasets")

sys.path.insert(0, _REPO_ROOT)

from albam.engines.cie.fs import split_archive_name  # noqa: E402
from tests.cie.lfs_paths import find_lfs_archives  # noqa: E402
from tests.mtfw.scripts.catalog_paths import hash_identity  # noqa: E402


def generate_catalog(game_root):
    entries = [
        {
            "path_hash": hash_identity(relative_path),
            # What decides how the archive's decompressed bytes are read
            # (see albam/engines/cie/fs.py). Not a game asset path, so it's
            # committable as-is, and it's what a dataset is picked for
            # coverage by.
            "payload_extension": split_archive_name(os.path.basename(relative_path))[1],
        }
        for relative_path, _absolute_path in find_lfs_archives(game_root)
    ]
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
        help="Output path (default: tests/cie/datasets/<app_id>_catalog.json)",
    )
    args = parser.parse_args()

    t0 = time.time()
    entries = generate_catalog(args.game_root)
    elapsed = time.time() - t0

    out_path = args.out or os.path.join(DATASETS_DIR, f"{args.app_id}_catalog.json")
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    print(f"wrote {out_path} in {elapsed:.1f}s")
    print(f"  total archives: {len(entries)}")


if __name__ == "__main__":
    main()
