"""Which local files back an MT Framework app_id's committed dataset hashes.

The engine half of tests/scripts/upload_ci_game_files.py: everything here
knows about .arc archives, .mrl material libraries and MTFW_FS, and nothing
here knows about R2, the CI gate or what an upload costs.

albam.engines.* is imported lazily, inside the functions that need it:
importing albam pulls in bpy, and the uploader's whole decision layer - the
CI gate, the dataset and catalog checks, --help - is plain JSON work with no
reason to need Blender installed.
"""
import os

APP_IDS = ("re0", "re1", "re5", "re6", "rev1", "rev2", "dd", "dmc4", "umvc3")

_HERE = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(_HERE, "datasets")
CATALOG_COMMAND = "python tests/mtfw/scripts/generate_catalog.py {app_id} <game-root>"

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
    backing `hashes`, and the {hash: virtual path} they resolved to.

    An archived hash contributes the whole .arc that holds it (many hashes
    usually collapse onto one archive); a loose hash contributes the file
    itself. Resolution is forward-only - hashes are matched by walking the
    install and hashing what's there, never by turning a hash back into a
    path - so a hash that doesn't correspond to this install fails loudly
    via resolve_hashes rather than silently uploading the wrong thing.
    """
    from tests.mtfw.scripts.catalog_paths import resolve_hashes

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
