"""
Builds a minimal stand-in for a real RE:ORC install: just the .ssg archives
(and loose files) that tests/hexn's committed hash datasets actually name,
copied into a new directory at their own relative paths, so it can be
passed to pytest as --game-dir=<app-id>::<out-dir> exactly like the real
thing.

Why: mounting a full install costs a HexnFS scan plus a walk of tens of
thousands of virtual paths before a single test runs, every session. A
dataset-sized install mounts in well under a second, and every hash still
resolves to the same virtual path (a packed file's path comes from its
archive's own file table, and a loose file's is relative to the game root -
neither depends on which other files sit next to it), so the tests are
running against the same real, unmodified game bytes either way.

This is a real maintainer/owner-run tool, not part of CI or routine test
runs - same as generate_catalog.py next to it.

Usage:
    python tests/hexn/scripts/make_test_install.py <app-id> <game-root> <out-dir>
"""
import argparse
import glob
import json
import os
import shutil
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
_VENDOR_DIR = os.path.join(_REPO_ROOT, "albam", "albam_vendor")
DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "hexn", "datasets")

# See generate_catalog.py for why the vendored kaitaistruct is added here.
sys.path.insert(0, _VENDOR_DIR)
sys.path.insert(0, _REPO_ROOT)

from albam.engines.hexn.fs import HexnFS  # noqa: E402
from tests.mtfw.scripts.catalog_paths import hash_virtual_path, index_by_hash  # noqa: E402


def dataset_hashes(app_id):
    """Every "*_path_hash" value for app_id across tests/hexn/datasets/
    *_hashes.json - i.e. exactly the files these tests can ask for."""
    hashes = set()
    for path in sorted(glob.glob(os.path.join(DATASETS_DIR, "*_hashes.json"))):
        with open(path) as f:
            for entry in json.load(f):
                if entry.get("app_id") != app_id:
                    continue
                hashes |= {v for k, v in entry.items() if k.endswith("path_hash")}
    return hashes


def referenced_paths(game_fs, index, virtual_paths):
    """The extra virtual paths an import of `virtual_paths` reaches for:
    every .matb an .edgemodel names, every texture those .matb name (see
    albam.engines.hexn.material), and the skeleton inferred from the
    .edgemodel's own stem (see albam.engines.hexn.skeleton). Without these
    a dataset-sized install parses fine but can't import anything.

    References are resolved through `index` by hash rather than used as
    paths directly, since a reference's casing doesn't have to match the
    file table's.
    """
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel
    from albam.engines.hexn.structs.hexane_matb import HexaneMatb

    def resolve(reference):
        return index.get(hash_virtual_path(reference))

    extra = set()
    for virtual_path in virtual_paths:
        if not virtual_path.lower().endswith(".edgemodel"):
            continue
        edgemodel = HexaneEdgemodel.from_bytes(game_fs.readbytes(virtual_path))
        edgemodel._read()

        stem = os.path.splitext(os.path.basename(virtual_path))[0]
        for candidate in (f"dlc/pack1/Characters/skel/{stem}.ssg", f"dlc/pack1/characters/skel/{stem}"):
            skeleton = resolve(candidate)
            if skeleton:
                extra.add(skeleton)

        for mesh_header in edgemodel.meshes_header:
            material = resolve(mesh_header.materials.first_material)
            if material is None:
                continue
            extra.add(material)
            matb = HexaneMatb.from_bytes(game_fs.readbytes(material))
            matb._read()
            for texture in matb.shader.textures:
                resolved = resolve(texture)
                if resolved:
                    extra.add(resolved)
    return extra


def sources_for(game_fs, game_root, virtual_paths):
    """{relative path -> absolute source path} for whatever has to be
    copied to make `virtual_paths` resolvable: the .ssg a packed file came
    from (see HexnFS.origin_of), or the loose file itself."""
    sources = {}
    for virtual_path in virtual_paths:
        origin = game_fs.origin_of(virtual_path)
        relative = origin if origin is not None else virtual_path.lstrip("/")
        sources[relative] = os.path.join(game_root, relative.replace("/", os.sep))
    return sources


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument("out_dir")
    args = parser.parse_args(argv)

    hashes = dataset_hashes(args.app_id)
    if not hashes:
        parser.error(f"no dataset hashes found for app_id={args.app_id!r} in {DATASETS_DIR}")

    print(f"mounting {args.game_root} ...")
    game_fs = HexnFS(args.game_root)
    index = index_by_hash(game_fs)
    missing = hashes - index.keys()
    if missing:
        parser.error(f"{len(missing)} dataset hash(es) not in this install: {sorted(missing)[:5]}")

    needed = {index[h] for h in hashes}
    needed |= referenced_paths(game_fs, index, needed)
    sources = sources_for(game_fs, args.game_root, needed)
    total = 0
    for relative, source in sorted(sources.items()):
        destination = os.path.join(args.out_dir, relative.replace("/", os.sep))
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copyfile(source, destination)
        total += os.path.getsize(destination)

    print(f"{len(hashes)} hashes (+{len(needed) - len(hashes)} referenced) -> {len(sources)} files, "
          f"{total / 1024 / 1024:.1f} MiB in {args.out_dir}")
    print(f'run the tests with --game-dir={args.app_id}::"{args.out_dir}"')


if __name__ == "__main__":
    main()
