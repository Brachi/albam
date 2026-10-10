"""Which local files back a RE:ORC (reorc) app_id's committed dataset hashes.

The engine half of tests/scripts/upload_ci_game_files.py, alongside
tests/mtfw/upload_source.py and tests/cie/upload_source.py. The dependency
expansion here (a model's skeleton, its .matb, and that .matb's textures)
mirrors tests/hexn/scripts/make_test_install.py's own referenced_paths() -
the local-install-shrinking counterpart of this same problem - rather than
duplicating a second copy of that logic from scratch.

albam.engines.* is imported lazily, inside the functions that need it: it
pulls in bpy, and the uploader's decision layer has no reason to need
Blender installed.
"""
import os

APP_IDS = ("reorc",)

_HERE = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(_HERE, "datasets")
CATALOG_COMMAND = "python tests/hexn/scripts/generate_catalog.py {app_id} <game-root>"


def _referenced_paths(game_fs, index, virtual_paths):
    """The extra virtual paths an import of `virtual_paths` reaches for:
    every .matb an .edgemodel names, every texture those .matb name (see
    albam.engines.hexn.material), and the skeleton inferred from the
    .edgemodel's own stem (see albam.engines.hexn.skeleton). Without these
    an uploaded subset parses fine but can't import anything.

    References are resolved through `index` by hash rather than used as
    paths directly, since a reference's casing doesn't have to match the
    file table's. Returns (paths found, references that resolved to
    nothing) - unresolved ones are reported rather than silently dropped,
    same as material.build_blender_materials's own tolerate-absence
    convention, since an upload can't include what isn't there.
    """
    from tests.mtfw.scripts.catalog_paths import hash_virtual_path
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel
    from albam.engines.hexn.structs.hexane_matb import HexaneMatb

    def resolve(reference):
        return index.get(hash_virtual_path(reference))

    unresolved = set()
    extra = set()
    for virtual_path in virtual_paths:
        if not virtual_path.lower().endswith(".edgemodel"):
            continue
        edgemodel = HexaneEdgemodel.from_bytes(game_fs.readbytes(virtual_path))
        edgemodel._read()

        # Same tails albam.engines.hexn.skeleton._find_skel_vfile looks
        # for - every pack has its own skel directory, so only the tail is
        # predictable, not the directory or the extension.
        stem = os.path.splitext(os.path.basename(virtual_path))[0].lower()
        tails = (f"/skel/{stem}.ssg", f"/skel/{stem}")
        extra |= {p for p in index.values() if p.lower().endswith(tails)}

        for mesh_header in edgemodel.meshes_header:
            material = resolve(mesh_header.materials.first_material)
            if material is None:
                unresolved.add(mesh_header.materials.first_material)
                continue
            extra.add(material)
            matb = HexaneMatb.from_bytes(game_fs.readbytes(material))
            matb._read()
            for texture in matb.shader.textures:
                resolved = resolve(texture)
                if resolved:
                    extra.add(resolved)
                else:
                    unresolved.add(texture)
    return extra, unresolved


def resolve_upload_set(game_root, app_id, hashes):
    """{absolute local path: game-root-relative key suffix} for the
    archives (and loose files) backing `hashes`, and the {hash: virtual
    path} they resolved to.

    An archived hash contributes the whole .ssg that holds it - HexnFS has
    no whole-file random access into one otherwise (see fs.py's SsgFS
    doc), so nothing short of the whole archive is ever uploadable. A
    loose hash contributes the file itself.
    """
    from tests.mtfw.scripts.catalog_paths import index_by_hash, resolve_hashes

    try:
        from albam.engines.hexn.fs import HexnFS
    except ImportError as e:
        # albam imports bpy at package level, so this tool needs the same
        # environment the tests run in. Worth naming outright: the traceback
        # alone points at albam/__init__.py and reads like a repo problem.
        raise SystemExit(
            f"cannot import albam ({e}) - run this with the same interpreter as the "
            f"test suite, e.g. .venv/bin/python with bpy installed"
        )

    game_fs = HexnFS(game_root)
    index = index_by_hash(game_fs)
    resolved = resolve_hashes(game_fs, hashes)

    wanted = set(resolved.values())
    referenced, unresolved = _referenced_paths(game_fs, index, wanted)
    wanted |= referenced

    uploads = {}
    for virtual_path in sorted(wanted):
        origin = game_fs.origin_of(virtual_path)
        relative = origin if origin is not None else virtual_path.lstrip("/")
        absolute = os.path.join(game_root, relative.replace("/", os.sep))
        uploads[absolute] = relative

    if unresolved:
        print(f"  {len(unresolved)} material/texture path(s) named by an .edgemodel/.matb are not "
              f"in this install - the importer only warns about these, so they are left out:")
        for path in sorted(unresolved)[:10]:
            print(f"    {path}")
        if len(unresolved) > 10:
            print(f"    ... and {len(unresolved) - 10} more")

    print(f"  {len(resolved)} referenced file(s) pulled in {len(wanted) - len(resolved)} "
          f"dependency file(s) (skeleton + .matb + textures)")
    return uploads, resolved
