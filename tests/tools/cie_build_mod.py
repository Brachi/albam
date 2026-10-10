"""Build a modded RE4UHD archive, checking the exporter against the original
before trusting it with an edit.

The check is the point. Importing a model and exporting it again proves
nothing on its own: albam reads its own output, so a file it writes wrongly
still comes back looking right. Three archives that crashed or deformed the
game passed exactly that kind of test. What catches those is comparing a
**no-edit re-export against the bytes the archive shipped with** - bone
table, texture slots, material count, geometry - which is ground truth albam
had no hand in.

A model that fails keeps its original bytes rather than going into the
archive unverified: a model albam cannot reproduce is one whose skinning or
textures would be wrong in game, and nothing about the Blender scene shows
that.

Maintainer/owner tool, not part of CI: it needs a real game install.

Usage (from the repo root, with a bpy-enabled interpreter):

    python tests/tools/cie_build_mod.py <source-archive> <out-dir> [scale]

Writes B_stored.udas.lfs (every model re-exported, no edits) and
C_stored.udas.lfs (every model scaled about the origin), the second holding
only the models the check passed.
"""
import os
import struct
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)
# Kept before bpy sees it: importing bpy parses sys.argv itself.
ARGV = sys.argv[1:]
sys.argv = ["build_mod"]

import bpy  # noqa: E402
import albam  # noqa: E402

albam.register()

from albam.engines.cie.archive import _read_payload, _rebuild_udas  # noqa: E402
from albam.engines.cie.fs import LfsFS  # noqa: E402
from albam.engines.cie.lfs_decompress import xcompress_compress_re4hd  # noqa: E402
from albam.engines.cie.mesh import AUTO_TPL  # noqa: E402
from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin  # noqa: E402
from albam.lib import fs_registry  # noqa: E402
from albam.registry import blender_registry  # noqa: E402

APP = "re4uhd"
MESH_FLAG = 0x80000000


def is_mesh(data):
    return len(data) >= 0x24 and bool(
        struct.unpack_from("<I", data, 0x20)[0] & MESH_FLAG)


def describe(data):
    """The parts of a model that a faithful re-export must reproduce."""
    parsed = Re4UhdBin.from_bytes(data)
    parsed._read()
    return {
        "bones": [(b.bone_id, b.parent) for b in parsed.bones],
        "slots": [(m.diffuse_map, m.bump_map, m.opacity_map,
                   m.generic_specular_map, m.custom_specular_map, m.material_flag)
                  for m in parsed.materials],
        "triangles": sum(m.face_index.num_triangles for m in parsed.materials),
        "materials": parsed.header.num_materials,
    }


def entry_index(path):
    return int(path.rsplit("_", 1)[1].split(".")[0])


def export_all(archive, scale=None):
    """{entry index: exported bytes} for every mesh model in `archive`."""
    vfs = bpy.context.scene.albam.vfs
    vfs.file_list.clear()
    bpy.context.scene.albam.exported.file_list.clear()
    fs_registry.clear()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    bpy.context.scene.albam.apps.app_selected = APP

    root = vfs.add_real_file(APP, archive)
    children = [vf for vf in vfs.file_list
                if vf.tree_node.root_id == root.name and not vf.is_root]
    models = [vf for vf in children
              if vf.display_name.lower().endswith(".bin") and is_mesh(vf.get_bytes())]

    exported = {}
    scaled = set()
    for vfile in models:
        vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
        bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
        original = vfile.get_bytes()
        bl_object = import_one(vfile, original)
        if scale is not None:
            mesh = [o for o in bl_object.children_recursive if o.type == "MESH"][0].data
            # Guard against scaling a mesh twice: with a shared armature the
            # object handed back can own more than its own mesh.
            if mesh.name in scaled:
                raise SystemExit(f"would scale {mesh.name} twice - aborting")
            scaled.add(mesh.name)
            for vertex in mesh.vertices:
                vertex.co = vertex.co * scale
            mesh.update()
        exported[vfile.display_name] = blender_registry.export_registry[
            (APP, "bin")](bl_object)[0].data_bytes
    return exported


def import_one(vfile, original):
    bl_object = blender_registry.import_registry[(APP, "bin")](vfile, bpy.context)
    bl_object.albam_asset.app_id = APP
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = vfile.display_name
    bl_object.albam_asset.original_bytes = original
    return bl_object


def pack(archive, replacements, out_path):
    fs = LfsFS(archive)
    merged = {p.lstrip("/"): fs.readbytes(p) for p in fs.walk.files()}
    fs.close()
    merged.update(replacements)
    payload, _extension = _read_payload(archive)
    with open(out_path, "wb") as f:
        f.write(xcompress_compress_re4hd(_rebuild_udas(payload, merged)))
    return os.path.getsize(out_path)


def main():
    archive = ARGV[0]
    out_dir = ARGV[1] if len(ARGV) > 1 else "."
    scale = float(ARGV[2]) if len(ARGV) > 2 else 1.6
    os.makedirs(out_dir, exist_ok=True)

    fs = LfsFS(archive)
    originals = {entry_index(p): fs.readbytes(p) for p in fs.walk.files()
                 if p.endswith(".bin") and is_mesh(fs.readbytes(p))}
    fs.close()
    print(f"{len(originals)} mesh models in {os.path.basename(archive)}")

    plain = export_all(archive)
    size = pack(archive, plain, os.path.join(out_dir, "B_stored.udas.lfs"))
    print(f"B_stored {size} bytes")

    failures = []
    faithful = set()
    for name, data in plain.items():
        index = entry_index(name)
        want, got = describe(originals[index]), describe(data)
        bad = [f for f in ("bones", "slots", "materials") if want[f] != got[f]]
        if bad:
            failures.extend((index, f, want[f], got[f]) for f in bad)
        else:
            faithful.add(name)
    print(f"\nGATE: no-edit re-export vs original, {len(originals)} models")
    by_field = {}
    for _index, field, _w, _g in failures:
        by_field[field] = by_field.get(field, 0) + 1
    for field in ("bones", "slots", "materials"):
        bad = by_field.get(field, 0)
        print(f"  {field:10} {len(originals) - bad}/{len(originals)} reproduced"
              f"{'' if not bad else '   <-- FAILED'}")
    if failures:
        for index, field, want, got in failures[:3]:
            print(f"    model {index} {field}: want {str(want)[:70]}")
            print(f"    model {index} {field}: got  {str(got)[:70]}")
    if not faithful:
        print("\nnothing re-exported faithfully - refusing to build")
        return 1

    # Only models the gate passed are replaced. One albam cannot reproduce
    # keeps its original bytes rather than going into the archive unverified:
    # a model that fails here is one whose skinning would be wrong in game,
    # and there is no way to see that from Blender.
    skipped = sorted(entry_index(n) for n in plain if n not in faithful)
    if skipped:
        print(f"\nkeeping the original bytes for {len(skipped)} model(s): {skipped}")

    edited = {k: v for k, v in export_all(archive, scale=scale).items()
              if k in faithful}
    size = pack(archive, edited, os.path.join(out_dir, "C_stored.udas.lfs"))
    print(f"\nC_stored {size} bytes (every model scaled {scale}x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
