"""
Portable path identities for the hashed dataset catalog (see the design
discussion this branch started from - no plain-text game asset paths get
committed, only hashes of them).

The only thing that *isn't* already portable is an .arc's own on-disk
identity: MTFW_FS.origin_of() returns ArcFS.arc_path, which for a local
MTFW_FS(game_root) is an absolute filesystem path (built from os.walk() -
see arc_fs.find_arc_files()), so it necessarily bakes in wherever the game
happens to sit on *this* disk. Two legitimate owners of the same game would
get different absolute paths, and therefore different hashes, unless that
gets normalized to something relative to game_root first.

File paths themselves (both archived and loose) don't have this problem:
MTFW_FS's own virtual path space is already relative to itself, never to a
host filesystem location - an archived file's path comes straight from the
.arc's internal file table (game data, not a filesystem artifact), and a
loose file's path is already relative to game_root because OSFS(game_root)
is rooted there. Both still go through normalize_virtual_path() first
though: a loose file's *name* is a real filesystem entry, so its casing can
still vary the same way an .arc's own filename can (see
to_portable_relative_path) - lowercasing uniformly avoids having to treat
archived and loose paths differently.
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
