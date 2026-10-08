"""Which local files back an RE4UHD app_id's committed dataset hashes.

The engine half of tests/scripts/upload_ci_game_files.py, alongside
tests/mtfw/upload_source.py. Two things differ from MT Framework's:

- A dataset hash names a whole archive, not a file inside one (an .lfs keeps
  its file table inside its compressed stream - see albam/engines/cie/fs.py),
  so there is no archive to map a resolved path back onto.
- The dependency a model needs is its texture pack, which lives in a
  separate archive found beside the model's own rather than inside it. That
  lookup is a directory scan the importer does at import time, so a pack no
  upload included costs those models their textures with nothing failing
  outright - the same trap .mrl files are for MT Framework.

albam.engines.* is imported lazily, inside the functions that need it: it
pulls in bpy, and the uploader's decision layer has no reason to need
Blender installed.
"""
import os

APP_IDS = ("re4uhd",)

_HERE = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(_HERE, "datasets")
CATALOG_COMMAND = "python tests/cie/scripts/generate_catalog.py {app_id} <game-root>"


def _pack_ids(archive_path):
    """Every texture pack id named by a .tpl inside one archive.

    Read from the .tpl entries themselves rather than from the models: a
    material addresses a texture by a slot index into its .tpl, and only the
    .tpl carries the pack the texture actually lives in.
    """
    from albam.engines.cie.fs import LfsFS
    from albam.engines.cie.structs.tpl import Tpl

    found = set()
    try:
        archive_fs = LfsFS(archive_path)
    except Exception:
        # A container variant albam cannot list yet (the big-endian ones)
        # simply contributes no dependencies - it is still uploaded itself.
        return found
    try:
        for path in archive_fs.walk.files():
            if not path.lower().endswith(".tpl"):
                continue
            try:
                tpl = Tpl.from_bytes(archive_fs.readbytes(path))
                tpl._read()
                for entry in tpl.tpl_entries:
                    found.add(f"{entry.image_data.ids.pack_id:08x}")
            except Exception:
                # Same rationale as the importer, which only warns about a
                # .tpl it cannot read: one bad entry is not worth aborting
                # a whole upload over.
                continue
    finally:
        archive_fs.close()
    return found


def _pack_archives(archive_path, pack_ids):
    """The pack files `pack_ids` resolve to next to `archive_path`, exactly
    where the importer looks for them, and the ids nothing was found for."""
    from albam.engines.cie.textures import _find_pack_in

    content_dir = os.path.dirname(os.path.dirname(archive_path))
    found, unresolved = set(), set()
    for pack_id in sorted(pack_ids):
        pack_path = _find_pack_in(content_dir, pack_id)
        if pack_path:
            found.add(pack_path)
        else:
            unresolved.add(pack_id)
    return found, unresolved


def resolve_upload_set(game_root, app_id, hashes):
    """{absolute local path: game-root-relative key suffix} for the archives
    backing `hashes`, and the {hash: absolute path} they resolved to.

    Resolution is forward-only, by hashing every archive found under
    game_root: a hash this install has no archive for raises rather than
    quietly uploading something else.
    """
    from tests.cie.lfs_paths import resolve_archive_hashes

    resolved = resolve_archive_hashes(game_root, hashes)

    wanted = set(resolved.values())
    unresolved = set()
    for archive_path in sorted(resolved.values()):
        packs, missing = _pack_archives(archive_path, _pack_ids(archive_path))
        wanted |= packs
        unresolved |= missing

    uploads = {path: os.path.relpath(path, game_root).replace(os.sep, "/")
               for path in sorted(wanted)}

    if unresolved:
        print(f"  {len(unresolved)} texture pack(s) named by a .tpl are not in this "
              f"install - the importer only warns about these, so they are left out:")
        for pack_id in sorted(unresolved):
            print(f"    {pack_id}")

    print(f"  {len(resolved)} referenced archive(s) pulled in {len(wanted) - len(resolved)} "
          f"dependency archive(s) (texture packs)")
    return uploads, resolved
