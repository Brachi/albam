"""Import every RE4 UHD mesh .bin in a set of .lfs archives through the real
Blender operator stack, and report what succeeded, what failed and why.

The cie counterpart of tests/tools/mod_import_sweep.py. It differs in what it
sweeps over, because RE4 UHD has no whole-game filesystem to walk: an .lfs's
file table lives inside its compressed stream, so archives are mounted one at
a time (see albam/engines/cie/fs.py). This mounts each archive matching
--pattern, then imports every mesh .bin inside it.

Two RE4-specific wrinkles the mtfw sweep doesn't have:

- ".bin" is not a format, it's a file name. Cameras, lighting and collision
  data are all ".bin" too. is_mesh_bin() below tests the header flag that only
  a mesh sets, rather than importing everything and counting the crashes.
- The .bin importer needs a .tpl chosen for it (materials resolve their
  textures through one), so this picks the archive's first .tpl the way the
  UI's dropdown would.

Maintainer/owner tool, not part of CI: it needs a real game install, and
decompressing a few hundred archives is far too slow for a test run.

Usage (from the repo root, with a bpy-enabled interpreter):

    python tests/tools/cie_import_sweep.py <game-root> [--pattern REGEX]
                                     [--limit N] [--out results.json]

--pattern matches an archive's path relative to the game root, so it is how
you narrow a run to one content folder - characters, say - rather than every
container archive in the install.
"""
import argparse
import gc
import json
import os
import re
import struct
import sys
import time
import traceback

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)

APP_ID = "re4uhd"
# Every block container in the install. Models live in these; narrow with
# --pattern to sweep one folder's worth rather than all of them.
DEFAULT_PATTERN = r"\.udas\.lfs$"

# A mesh .bin always has this bit set in the flags word at 0x20. Camera,
# lighting and other ".bin" payloads don't, so it's what separates a model
# from a file that merely shares the extension.
MESH_FLAG = 0x80000000
MESH_FLAG_OFFSET = 0x20


def is_mesh_bin(data):
    if len(data) < MESH_FLAG_OFFSET + 4:
        return False
    (flags,) = struct.unpack_from("<I", data, MESH_FLAG_OFFSET)
    return bool(flags & MESH_FLAG)


def _reset_scene(bpy):
    """Drops everything the previous import created - see
    tests/tools/mod_import_sweep.py, same reasoning."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True,
                                       do_recursive=True)
    gc.collect()


def find_archives(game_root, pattern, limit=None):
    rx = re.compile(pattern, re.IGNORECASE)
    found = []
    for current_dir, _dirs, files in os.walk(game_root):
        for name in files:
            absolute_path = os.path.join(current_dir, name)
            relative = os.path.relpath(absolute_path, game_root).replace(os.sep, "/")
            if rx.search(relative):
                found.append((relative, absolute_path))
    found.sort()
    return found[:limit] if limit else found


def sweep(game_root, pattern, limit=None):
    import bpy
    import albam
    albam.register()

    archives = find_archives(game_root, pattern, limit)
    print(f"{len(archives)} archives to sweep", file=sys.stderr)

    bpy.context.scene.albam.apps.app_selected = APP_ID
    vfs = bpy.context.scene.albam.vfs

    results = []
    for i, (relative, absolute_path) in enumerate(archives, 1):
        t_mount = time.time()
        try:
            root = vfs.add_real_file(APP_ID, absolute_path)
        except Exception as e:
            results.append({"archive": relative, "path": None, "ok": False,
                            "error": f"mount failed: {type(e).__name__}: {e}",
                            "traceback": traceback.format_exc()})
            continue
        mount_seconds = round(time.time() - t_mount, 2)

        children = [vf for vf in vfs.file_list
                    if vf.tree_node.root_id == root.name and not vf.is_root]
        tpl = next((vf for vf in children if vf.display_name.lower().endswith(".tpl")), None)
        meshes = [vf for vf in children
                  if vf.display_name.lower().endswith(".bin") and is_mesh_bin(vf.get_bytes())]
        print(f"[{i}/{len(archives)}] {relative}: {len(meshes)} mesh bins, "
              f"tpl={tpl.display_name if tpl else None} ({mount_seconds}s)", file=sys.stderr)

        for vfile in meshes:
            _reset_scene(bpy)
            entry = {"archive": relative, "path": vfile.display_name, "ok": False,
                     "tpl": tpl.display_name if tpl else None,
                     "mount_seconds": mount_seconds}
            t = time.time()
            try:
                # Selection first: the .tpl dropdown's items are computed
                # from whatever is selected (see mesh._get_tpl_files_enum),
                # so assigning it before there's a selection has no valid
                # value to take.
                vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
                if tpl:
                    bpy.context.scene.albam.import_options_bin.tpl_file_id = tpl.name
                bl_object = _import_one(bpy, vfile)
                bl_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
                armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
                entry.update(
                    ok=True,
                    imported=bool(bl_object),
                    meshes=len(bl_meshes),
                    vertices=sum(len(o.data.vertices) for o in bl_meshes),
                    faces=sum(len(o.data.polygons) for o in bl_meshes),
                    bones=len(armatures[0].data.bones) if armatures else 0,
                    materials=len(bpy.data.materials),
                    images=len(bpy.data.images),
                )
            except Exception as e:
                entry.update(error=f"{type(e).__name__}: {e}",
                             traceback=traceback.format_exc())
            entry["seconds"] = round(time.time() - t, 2)
            results.append(entry)

        _reset_scene(bpy)
        vfs.file_list.clear()
    return results


def _import_one(bpy, vfile):
    """Calls the registered import function directly rather than
    bpy.ops.albam.import_vfile.

    The operator swallows the exception and reports "Import failed" (see
    ALBAM_OT_Import.execute), which is right for a UI but would turn every
    failure here into an indistinguishable {"CANCELLED"} with no traceback -
    and a sweep exists to tell failures apart.
    """
    from albam.registry import blender_registry

    import_function = blender_registry.import_registry[(vfile.app_id, vfile.extension)]
    return import_function(vfile, bpy.context)


def summarize(results):
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    archives = {r["archive"] for r in results}
    print(f"\n{len(ok)}/{len(results)} mesh .bin imported, across {len(archives)} archives")
    if ok:
        print(f"  vertices: {sum(r.get('vertices', 0) for r in ok)}, "
              f"bones: {sum(r.get('bones', 0) for r in ok)}, "
              f"images: {sum(r.get('images', 0) for r in ok)}")
    if bad:
        kinds = {}
        for r in bad:
            kind = r["error"].split("\n")[0][:110]
            kinds[kind] = kinds.get(kind, 0) + 1
        print("\nfailures by kind:")
        for kind, count in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print(f"  {count:4d}  {kind}")
    return bad


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("game_root")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN,
                        help="only sweep archives whose game-root-relative path matches "
                             f"this regex (default: {DEFAULT_PATTERN})")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default=None, help="write full results as JSON")
    args = parser.parse_args()

    results = sweep(args.game_root, args.pattern, args.limit)
    bad = summarize(results)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=1)
        print(f"\nwrote {args.out}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
