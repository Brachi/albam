"""
Finding and identifying .lfs archives in a local RE4 UHD install.

The identity of one archive here is its path relative to the game root,
forward-slashed and lowercased, hashed the same way every other engine's
test dataset hashes its own identities (see
tests/mtfw/scripts/catalog_paths.py) - archives rather than the files inside
them, because listing an .lfs's contents means decompressing the whole
archive (see albam/engines/cie/fs.py).
"""
import os

from tests.mtfw.scripts.catalog_paths import hash_identity, to_portable_relative_path


def find_lfs_archives(game_root):
    """Every .lfs under game_root as (identity, absolute path) pairs, sorted
    by identity. The identity is lowercased (see to_portable_relative_path),
    so the real path is carried alongside rather than rebuilt from it - on a
    case-sensitive filesystem the two don't have to match.
    """
    found = []
    for current_dir, _dirs, files in os.walk(game_root):
        for name in files:
            if name.lower().endswith(".lfs"):
                absolute_path = os.path.join(current_dir, name)
                found.append((to_portable_relative_path(absolute_path, game_root), absolute_path))
    return sorted(found)


def resolve_archive_hashes(game_root, target_hashes):
    """{hash: absolute .lfs path} for exactly target_hashes, by hashing every
    archive found under game_root - the same forward-match-only approach as
    tests.mtfw.scripts.catalog_paths.resolve_hashes, and raising KeyError
    naming whichever hashes weren't found rather than skipping quietly.
    """
    target_hashes = set(target_hashes)
    found = {}
    for identity, absolute_path in find_lfs_archives(game_root):
        h = hash_identity(identity)
        if h in target_hashes:
            found[h] = absolute_path
            if len(found) == len(target_hashes):
                break
    missing = target_hashes - found.keys()
    if missing:
        raise KeyError(f"hash(es) not found in this game install: {sorted(missing)}")
    return found
