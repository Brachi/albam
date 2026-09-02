"""Round-trip every RE4UHD mesh .bin an archive holds: import, export,
re-import, and check the model survived.

The import sweep says a file parsed. This says albam can write one back that
it can read again, with the same triangles, materials and bones - the thing a
modding workflow depends on, and the part a parser test cannot reach.

What is compared, and what deliberately is not: triangle, material and bone
counts have to match exactly. Vertex counts do not, and are reported rather
than checked. Corners are shared along a triangle strip but never across a
UV seam or a shading split, and where a strip has to restart the two corners
it begins with are written again - so a re-imported model carries slightly
more vertices than the original while describing the same surface (see
albam/engines/cie/mesh.py).

Maintainer/owner tool, not part of CI: it needs a real game install, and
mounting archives means decompressing them.

Usage (from the repo root, with a bpy-enabled interpreter):

    python tests/tools/cie_export_sweep.py <game-root> [--pattern REGEX]
                                     [--limit N] [--out results.json]

--pattern matches an archive's path relative to the game root, so it is how
you narrow a run to one content folder.
"""
import argparse
import gc
import json
import os
import sys
import time
import traceback

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)

APP_ID = "re4uhd"
DEFAULT_PATTERN = r"\.udas\.lfs$"


def _reset_scene(bpy):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True,
                                       do_recursive=True)
    gc.collect()


def _model_stats(bpy, bl_object):
    meshes = [o for o in bl_object.children_recursive if o.type == "MESH"]
    if bl_object.type == "MESH":
        meshes.append(bl_object)
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    return {
        "vertices": sum(len(o.data.vertices) for o in meshes),
        "triangles": sum(len(polygon.vertices) - 2
                         for o in meshes for polygon in o.data.polygons),
        "materials": len({slot.material.name for o in meshes
                          for slot in o.material_slots if slot.material}),
        "bones": len(armatures[0].data.bones) if armatures else 0,
        "images": len([i for i in bpy.data.images if i.packed_file]),
    }


def sweep(game_root, pattern, limit=None):
    import bpy
    import albam
    albam.register()

    from albam.engines.cie.mesh import AUTO_TPL
    from albam.lib import fs_registry
    from albam.registry import blender_registry
    from tests.tools.cie_import_sweep import find_archives, is_mesh_bin

    archives = find_archives(game_root, pattern, limit)
    print(f"{len(archives)} archives to sweep", file=sys.stderr)

    bpy.context.scene.albam.apps.app_selected = APP_ID
    import_function = blender_registry.import_registry[(APP_ID, "bin")]
    export_function = blender_registry.export_registry[(APP_ID, "bin")]

    results = []
    for i, (relative, absolute_path) in enumerate(archives, 1):
        vfs = bpy.context.scene.albam.vfs
        vfs.file_list.clear()
        bpy.context.scene.albam.exported.file_list.clear()
        fs_registry.clear()
        try:
            root = vfs.add_real_file(APP_ID, absolute_path)
        except Exception as e:
            results.append({"archive": relative, "path": None, "ok": False,
                            "error": f"mount failed: {type(e).__name__}: {e}"})
            continue

        children = [vf for vf in vfs.file_list
                    if vf.tree_node.root_id == root.name and not vf.is_root]
        models = [vf for vf in children
                  if vf.display_name.lower().endswith(".bin") and is_mesh_bin(vf.get_bytes())]
        print(f"[{i}/{len(archives)}] {relative}: {len(models)} models", file=sys.stderr)

        for vfile in models:
            entry = {"archive": relative, "path": vfile.display_name, "ok": False}
            started = time.time()
            try:
                _reset_scene(bpy)
                vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
                bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
                original_bytes = vfile.get_bytes()
                bl_object = import_function(vfile, bpy.context)
                before = _model_stats(bpy, bl_object)

                bl_object.albam_asset.app_id = APP_ID
                bl_object.albam_asset.extension = "bin"
                bl_object.albam_asset.relative_path = vfile.display_name
                bl_object.albam_asset.original_bytes = original_bytes
                vfiles = export_function(bl_object)
                exported = vfiles[0].data_bytes

                exported_vfs = bpy.context.scene.albam.exported
                exported_vfs.file_list.clear()
                exported_vfs.add_export_root(APP_ID, f"roundtrip-{vfile.display_name}", vfiles)
                reimported_vfile = next(
                    vf for vf in exported_vfs.file_list
                    if not vf.is_root and vf.display_name == vfile.display_name)

                _reset_scene(bpy)
                bl_object = import_function(reimported_vfile, bpy.context)
                after = _model_stats(bpy, bl_object)

                mismatches = [key for key in ("triangles", "materials", "bones")
                              if before[key] != after[key]]
                entry.update(
                    ok=not mismatches,
                    mismatches=mismatches,
                    before=before,
                    after=after,
                    original_bytes=len(original_bytes),
                    exported_bytes=len(exported),
                )
                if mismatches:
                    entry["error"] = "round trip changed " + ", ".join(
                        f"{key} {before[key]}->{after[key]}" for key in mismatches)
            except Exception as e:
                entry.update(error=f"{type(e).__name__}: {e}",
                             traceback=traceback.format_exc())
            entry["seconds"] = round(time.time() - started, 2)
            results.append(entry)

        _reset_scene(bpy)
    return results


def summarize(results):
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    print(f"\n{len(ok)}/{len(results)} models round-tripped")
    if ok:
        grew = sum(r["exported_bytes"] for r in ok)
        was = sum(r["original_bytes"] for r in ok)
        print(f"  triangles: {sum(r['before']['triangles'] for r in ok)}, "
              f"bones: {sum(r['before']['bones'] for r in ok)}")
        print(f"  bytes: {was} in, {grew} out ({grew / was:.2f}x)")
    if bad:
        kinds = {}
        for r in bad:
            kind = r.get("error", "?").split("\n")[0][:110]
            kinds[kind] = kinds.get(kind, 0) + 1
        print("\nfailures by kind:")
        for kind, count in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print(f"  {count:4d}  {kind}")
    return bad


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("game_root")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
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
