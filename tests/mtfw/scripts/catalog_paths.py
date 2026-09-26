"""
Portable path identities for the hashed dataset catalog (see the design
discussion this branch started from - no plain-text game asset paths get
committed, only hashes of them).

MTFW_FS.origin_of() already returns an .arc's identity relative to
game_root (see arc_fs.py) - it never bakes in wherever the game happens to
sit on *this* disk. The remaining normalization for hashing is the same one
every other identity here needs: case-folding, since a real filesystem
entry's casing can vary between two legitimate installs of the same game
(e.g. across Windows/Linux, or a case-insensitive filesystem) even though
the underlying game data is identical. hash_virtual_path() covers that for
any already-relative identity, origin_of()'s included.

to_portable_relative_path()/hash_relative_path() are kept for the one case
that still starts from an absolute path: hashing MTFW_FS.origin_absolute_path()'s
result directly, without going through origin_of() first.

File paths themselves (both archived and loose) don't have the absolute-path
problem either: MTFW_FS's own virtual path space is already relative to
itself, never to a host filesystem location - an archived file's path comes
straight from the .arc's internal file table (game data, not a filesystem
artifact), and a loose file's path is already relative to game_root because
OSFS(game_root) is rooted there. Both still go through
normalize_virtual_path() for the same case-folding reason as above.
"""
import hashlib
import os

# Truncated sha256, not the full 64-char digest: this isn't a security
# boundary (path structures are already discoverable via modding community
# resources; the point is licensing-conscious storage + a legitimate-owner
# filter, not secrecy), and a full digest per entry would bloat a
# 100k+-entry catalog for no real benefit. 64 bits keeps collision risk
# astronomically low at that scale.
HASH_LENGTH = 16


def to_portable_relative_path(absolute_path, game_root):
    """
    Convert an absolute filesystem path into a stable identity string
    relative to game_root: forward-slash separators regardless of host OS,
    and lowercased - defensive against two legitimate installs of the same
    game differing only in path casing (e.g. across Windows/Linux, or a
    filesystem that normalizes case), so the same real install produces the
    same string, and therefore the same hash, everywhere.

    absolute_path must be a path actually under game_root (e.g. ArcFS.arc_path
    from an MTFW_FS(game_root) instance) - raises ValueError otherwise,
    rather than silently hashing something meaningless like "../../etc".
    """
    relative = os.path.relpath(absolute_path, game_root)
    if relative.startswith(".."):
        raise ValueError(f"{absolute_path!r} is not inside game_root {game_root!r}")
    return relative.replace(os.sep, "/").lower()


def normalize_virtual_path(path):
    """
    Normalize an already-portable MTFW_FS virtual path (e.g. from
    game_fs.walk.files(), leading "/") for hashing: strip the leading
    slash and lowercase, matching to_portable_relative_path's
    normalization for .arc identities - see module docstring for why.
    """
    return path.lstrip("/").lower()


def hash_identity(identity):
    """
    identity is expected to already be a portable, normalized string -
    either from to_portable_relative_path() (an .arc's own on-disk
    identity) or normalize_virtual_path() (an MTFW_FS virtual path).
    """
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return digest[:HASH_LENGTH]


def hash_relative_path(absolute_path, game_root):
    return hash_identity(to_portable_relative_path(absolute_path, game_root))


def hash_virtual_path(path):
    return hash_identity(normalize_virtual_path(path))


def resolve_hashes(game_fs, target_hashes):
    """
    Walk game_fs once, hashing every virtual path, and return {hash: path}
    for exactly the requested target_hashes. Forward match only - a hash is
    never turned back into a path any other way (see module docstring/
    generate_catalog.py, which uses the same technique). Raises KeyError
    naming whichever target hashes weren't found (missing/moved locally, or
    just the wrong hash/app_id) rather than returning a partial map silently -
    tests resolving a committed hash should fail loudly, not skip quietly.
    """
    target_hashes = set(target_hashes)
    found = {}
    for path in game_fs.walk.files():
        h = hash_virtual_path(path)
        if h in target_hashes:
            # First hit wins - a real install ships the same tree under
            # several casings, and the hash is over the lowercased path,
            # so a hash can match more than one file. Overwriting would
            # make the answer depend on how many other hashes were asked
            # for in the same call (the walk stops once they're all found).
            found.setdefault(h, path)
            if len(found) == len(target_hashes):
                break
    missing = target_hashes - found.keys()
    if missing:
        raise KeyError(f"hash(es) not found in this game install: {sorted(missing)}")
    return found


def index_by_hash(game_fs):
    """
    Walk game_fs once and return {hash: path} for *every* file in it - the
    whole-tree counterpart of resolve_hashes(), for a caller that resolves
    hashes repeatedly (e.g. a session-scoped fixture serving many
    parametrized tests) rather than once for a known set.

    Same forward-match-only rule as resolve_hashes: a hash is never turned
    back into a path any other way, this just keeps the result of the walk
    instead of throwing it away. Missing hashes surface as a plain KeyError
    on lookup, since there's no requested set to name them against here.

    First hit wins, exactly as resolve_hashes' own early exit does. That
    is not academic: a hash is over the lowercased path, and a real
    install ships the same tree under several casings - on one, 1937
    hashes cover more than one path, and some of those pairs are files of
    genuinely different sizes. Letting the last hit win would hand a test
    a different file than the one its hash was catalogued from.
    """
    index = {}
    for path in game_fs.walk.files():
        index.setdefault(hash_virtual_path(path), path)
    return index
