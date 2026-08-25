"""Import every .mod matching a pattern through the real Blender operator
stack, and report what succeeded, what failed and why.

Maintainer/owner tool, not part of CI: it needs a real game install, and a
full sweep is far too slow (and too memory-hungry) for a test run. The
committed import tests cover a curated subset of the same ground - this is
what you reach for when adding a new app, or checking a change against
every model a game ships.

Usage (from the repo root, with a bpy-enabled interpreter):

    python tools/mod_import_sweep.py <app-id> <game-root> [--pattern REGEX]
                                     [--limit N] [--out results.json]

Example:

    python tools/mod_import_sweep.py umvc3 "/path/to/UMVC3" \
        --pattern '^/chr/[^/]+/model/1p/[^/]+\\.mod$'
"""
import argparse
import gc
import json
import os
import re
import sys
import time
import traceback

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)


def _reset_scene(bpy):
    """Drops everything the previous import created.

    Imports accumulate otherwise, and a sweep over a few hundred models
    would both distort each model's stats and run the process out of
    memory. purge_orphans() is what actually frees the meshes/images -
    deleting objects only unlinks them.
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True,
                                       do_recursive=True)
    gc.collect()


def sweep(app_id, game_root, pattern, limit=None):
    import bpy
    import albam
    albam.register()

    from albam.engines.mtfw.arc_fs import MTFW_FS

    t0 = time.time()
    game_fs = MTFW_FS(game_root)
    paths = sorted(p for p in game_fs.walk.files() if p.lower().endswith(".mod"))
    if pattern:
        rx = re.compile(pattern, re.IGNORECASE)
        paths = [p for p in paths if rx.match(p)]
    if limit:
        paths = paths[:limit]
    print(f"mounted {game_root} in {time.time() - t0:.1f}s; {len(paths)} models",
          file=sys.stderr)

    bpy.context.scene.albam.apps.app_selected = app_id
    vfs = bpy.context.scene.albam.vfs
    vfs.add_fs_root(app_id, game_fs, display_name=f"{app_id}-sweep")

    results = []
    for i, path in enumerate(paths, 1):
        # add_fs_root() strips the leading "/" when building its tree
        vfs_path = path.lstrip("/")
        print(f"[{i}/{len(paths)}] {vfs_path}", file=sys.stderr)
        _reset_scene(bpy)
        entry = {"path": vfs_path, "ok": False}
        t = time.time()
        try:
            vfile = vfs.select_vfile(app_id, vfs_path)
            if vfile is None:
                raise KeyError(f"{vfs_path} not in the VFS tree")
            bpy.ops.albam.import_vfile()
            meshes = [o for o in bpy.data.objects if o.type == "MESH"]
            armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
            entry.update(
                ok=True,
                meshes=len(meshes),
                vertices=sum(len(o.data.vertices) for o in meshes),
                faces=sum(len(o.data.polygons) for o in meshes),
                bones=len(armatures[0].data.bones) if armatures else 0,
                materials=len(bpy.data.materials),
                images=len(bpy.data.images),
            )
        except Exception as e:
            entry.update(error=f"{type(e).__name__}: {e}",
                         traceback=traceback.format_exc())
        entry["seconds"] = round(time.time() - t, 2)
        results.append(entry)
    return results


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument("--pattern", default=None,
                        help="only sweep .mod paths matching this regex")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default=None, help="write full results as JSON")
    args = parser.parse_args()

    results = sweep(args.app_id, args.game_root, args.pattern, args.limit)

    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    print(f"\n{len(ok)}/{len(results)} imported")
    if bad:
        print("\nFAILURES:")
        for r in bad:
            print(f"  {r['path']}: {r['error']}")
        kinds = {}
        for r in bad:
            kinds[r["error"].split("\n")[0][:100]] = kinds.get(
                r["error"].split("\n")[0][:100], 0) + 1
        print("\nby kind:")
        for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print(f"  {v:4d}  {k}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=1)
        print(f"\nwrote {args.out}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
