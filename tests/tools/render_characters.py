"""Renders every character model an app can import, one PNG per character.

A visual counterpart to tests/tools/mod_import_sweep.py: the sweep says an import
raised no exception, this says whether what came out looks like the
character. Geometry that imports "successfully" with a flipped normal, a
missing texture or a collapsed skeleton is obvious in a render and invisible
in a pass/fail count.

Runs against the `bpy` pip package in .venv (Python 3.13, Blender 5.2), the
same interpreter pytest uses - not the real Blender application.

Usage:
    python tests/tools/render_characters.py <app-id> <game-root> [--pattern REGEX]
                                      [--suffix NAME] [--limit N]
                                      [--resolution WIDTHxHEIGHT] [--jobs N]

Example:

    python tests/tools/render_characters.py umvc3 "/path/to/UMVC3" --suffix baseline

Writes tests/data/<app-id>/<model>[_<suffix>].png. Pass --suffix to keep
a before/after pair side by side while working on shading.

Rendering is spread over --jobs worker processes. One process per worker is
the only way to parallelise this: bpy drives a single global Blender session,
so two characters cannot be in flight inside one interpreter.
"""
import argparse
import functools
import gc
import math
import os
import re
import subprocess
import sys

import bpy
from mathutils import Vector

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Script-mode execution puts this file's own dir at sys.path[0] instead of
# the repo root, which can let a stale/partial "albam" dir elsewhere on
# sys.path shadow the real package as an empty namespace package.
sys.path.insert(0, REPO_ROOT)
OUTPUT_ROOT = os.path.join(REPO_ROOT, "tests", "data")

# Default: a game's own playable character models, one per character. Most MT
# Framework titles lay these out as chr/<Name>/model/1p/<Name>.mod.
DEFAULT_PATTERN = r"^/chr/[^/]+/model/1p/[^/]+\.mod$"
# RE4 UHD has no whole-game filesystem to walk (see albam/engines/cie/fs.py),
# so its models are reached by mounting archives one at a time, and its
# pattern matches archive paths rather than model paths. Narrow it to one
# content folder to render just that folder's models.
CIE_APP_ID = "re4uhd"
CIE_DEFAULT_PATTERN = r"\.udas\.lfs$"


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                       bpy.data.lights, bpy.data.armatures, bpy.data.cameras):
        for block in list(collection):
            collection.remove(block)
    gc.collect()


def _world_points(max_points=20000):
    """World-space vertices of every mesh object, thinned to a bounded sample.

    Framing on vertices rather than on each object's bounding box matters for
    a character standing diagonally to the camera: the box corners stick out
    into empty space and cost a good part of the frame."""
    points = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        vertices = obj.data.vertices
        stride = max(1, len(vertices) // max_points)
        matrix = obj.matrix_world
        points.extend(matrix @ v.co for v in vertices[::stride])
    if not points:
        raise RuntimeError("no mesh geometry to frame")
    return points


def _setup_three_point_lighting(key=2.5, fill=0.9, rim=1.4):
    """Sun lamps, so strength is distance-independent and needs no re-tuning
    per character scale: key front-left-high, fill front-right-low (soft, no
    strong second shadow), rim behind-high for silhouette separation."""
    def add_sun(name, strength, rotation_euler):
        light_data = bpy.data.lights.new(name=name, type="SUN")
        light_data.energy = strength
        light_data.angle = math.radians(15)  # soft-ish shadows, not a pinpoint sun
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        light_obj.rotation_euler = rotation_euler
        bpy.context.collection.objects.link(light_obj)

    add_sun("Key", key, (math.radians(55), 0, math.radians(-35)))
    add_sun("Fill", fill, (math.radians(75), 0, math.radians(50)))
    add_sun("Rim", rim, (math.radians(140), 0, math.radians(160)))

    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.05, 0.05, 0.06, 1.0)
        background.inputs["Strength"].default_value = 1.0


def _setup_camera(points, resolution, fov_deg=40):
    xs, ys, zs = zip(*points)
    center = Vector((
        (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))

    fov = math.radians(fov_deg)
    # Blender's camera angle applies to the larger render dimension; the other
    # axis follows from the aspect ratio.
    width, height = resolution
    if width >= height:
        fov_x, fov_y = fov, 2 * math.atan(math.tan(fov / 2) * height / width)
    else:
        fov_y, fov_x = fov, 2 * math.atan(math.tan(fov / 2) * width / height)

    # Slightly elevated 3/4 front view - the usual character showcase angle.
    azimuth, elevation = math.radians(-25), math.radians(12)
    direction = Vector((
        math.sin(azimuth) * math.cos(elevation),
        -math.cos(azimuth) * math.cos(elevation),
        math.sin(elevation),
    ))
    rotation = direction.to_track_quat("Z", "Y").to_matrix()
    right, up = rotation.col[0], rotation.col[1]

    # Centre on the silhouette as the camera sees it, not on the world-space
    # box: an off-centre mid-point costs frame on one side and clips on the other.
    local_x = [(p - center).dot(right) for p in points]
    local_y = [(p - center).dot(up) for p in points]
    center = center + right * ((min(local_x) + max(local_x)) / 2)
    center = center + up * ((min(local_y) + max(local_y)) / 2)

    # For a point at camera-space (x, y, z) the camera must stand at least
    # z + |x| / tan(fov_x / 2) away for it to stay in frame (likewise for y),
    # so take the furthest demand any point makes.
    distance = 0.0
    for point in points:
        offset = point - center
        local = Vector((offset.dot(right), offset.dot(up), offset.dot(direction)))
        distance = max(
            distance,
            local.z + abs(local.x) / math.tan(fov_x / 2),
            local.z + abs(local.y) / math.tan(fov_y / 2),
        )
    distance = (distance or 1.0) * 1.06  # a little headroom

    cam_data = bpy.data.cameras.new("RenderCamera")
    cam_data.lens_unit = "FOV"
    cam_data.angle = fov
    cam_obj = bpy.data.objects.new("RenderCamera", cam_data)
    cam_obj.location = center + direction * distance
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_obj.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()


def _render(output_path, resolution=(1024, 1536)):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def _model_name(path):
    """The character's own name, from .../chr/<Name>/model/1p/<Name>.mod."""
    stem = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"[^A-Za-z0-9_-]+", "_", stem)


def _run_workers(args):
    """Re-run this script once per shard and wait for them all."""
    base = [sys.executable, os.path.abspath(__file__), args.app_id, args.game_root,
            "--pattern", args.pattern, "--resolution", args.resolution, "--jobs", "1"]
    if args.suffix:
        base += ["--suffix", args.suffix]
    if args.limit:
        base += ["--limit", str(args.limit)]

    workers = [subprocess.Popen(base + ["--shard", f"{index}/{args.jobs}"])
               for index in range(args.jobs)]
    return max(worker.wait() for worker in workers)


def _shard(items, shard):
    """The slice of `items` this worker owns.

    Round robin rather than contiguous blocks: neighbouring characters in a
    sorted listing tend to be alike in size, so a block hands one worker
    every heavy model and leaves another idle.
    """
    if not shard:
        return items
    index, total = (int(n) for n in shard.split("/"))
    return items[index::total]


def _mtfw_models(args, vfs):
    """(name, load) for every .mod matching --pattern in an MT Framework
    install, mounted as one game-wide filesystem."""
    from albam.engines.mtfw.arc_fs import MTFW_FS

    game_fs = MTFW_FS(args.game_root)
    rx = re.compile(args.pattern, re.IGNORECASE)
    paths = sorted(p for p in game_fs.walk.files()
                   if p.lower().endswith(".mod") and rx.match(p))
    if args.limit:
        paths = paths[:args.limit]
    paths = _shard(paths, args.shard)
    print(f"{len(paths)} models", file=sys.stderr)

    vfs.add_fs_root(args.app_id, game_fs, display_name=f"{args.app_id}-render")

    def load(path):
        # add_fs_root() strips the leading "/" when building its tree
        vfile = vfs.select_vfile(args.app_id, path.lstrip("/"))
        if vfile is None:
            raise KeyError(path)
        result = bpy.ops.albam.import_vfile()
        if result != {"FINISHED"}:
            raise RuntimeError(f"import_vfile returned {result}")

    for path in paths:
        yield _model_name(path), functools.partial(load, path)


def _cie_models(args, vfs):
    """(name, load) for every mesh .bin in the RE4 UHD archives matching
    --pattern.

    Sharding is by archive rather than by model: mounting one costs a full
    decompression (see albam/engines/cie/fs.py), so splitting a single
    archive's models across workers would pay that cost once per worker.

    Archives are mounted lazily, as the generator reaches them, and dropped
    afterwards - a worker's share of a character folder is more decompressed
    archive than is worth holding at once.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.lib import fs_registry
    from albam.registry import blender_registry
    from tests.tools.cie_import_sweep import find_archives, is_mesh_bin

    archives = find_archives(args.game_root, args.pattern, args.limit)
    archives = _shard(archives, args.shard)
    print(f"{len(archives)} archives", file=sys.stderr)

    def load(vfile):
        # Left on "Auto": the importer works out which .tpl a model's
        # materials address (see mesh.choose_tpl), which is what a user gets
        # by default too.
        vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
        bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
        import_function = blender_registry.import_registry[(vfile.app_id, vfile.extension)]
        import_function(vfile, bpy.context)

    for relative, absolute_path in archives:
        vfs.file_list.clear()
        fs_registry.clear()
        root = vfs.add_real_file(args.app_id, absolute_path)
        children = [vf for vf in vfs.file_list
                    if vf.tree_node.root_id == root.name and not vf.is_root]
        archive_name = os.path.basename(relative).split(".")[0]
        for vfile in children:
            if not vfile.display_name.lower().endswith(".bin"):
                continue
            if not is_mesh_bin(vfile.get_bytes()):
                continue
            name = f"{archive_name}_{os.path.splitext(vfile.display_name)[0]}"
            yield name, functools.partial(load, vfile)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument("--pattern", default=None,
                        help="model paths to render, or archive paths for "
                             f"{CIE_APP_ID} (defaults: {DEFAULT_PATTERN!r}, "
                             f"{CIE_DEFAULT_PATTERN!r})")
    parser.add_argument("--suffix", default=None,
                        help="appended to each filename, to keep runs side by side")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resolution", default="1024x1536",
                        help="WIDTHxHEIGHT, e.g. 640x960 for a quick low-res pass")
    parser.add_argument("--jobs", type=int, default=4,
                        help="worker processes to render with (default 4)")
    parser.add_argument("--shard", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.pattern is None:
        args.pattern = CIE_DEFAULT_PATTERN if args.app_id == CIE_APP_ID else DEFAULT_PATTERN

    if args.shard is None and args.jobs > 1:
        return _run_workers(args)

    import albam
    albam.register()

    out_dir = os.path.join(OUTPUT_ROOT, args.app_id)
    os.makedirs(out_dir, exist_ok=True)

    bpy.context.scene.albam.apps.app_selected = args.app_id
    bpy.context.scene.albam.import_settings.import_only_main_lods = True
    vfs = bpy.context.scene.albam.vfs

    source = _cie_models if args.app_id == CIE_APP_ID else _mtfw_models
    models = source(args, vfs)

    resolution = tuple(int(n) for n in args.resolution.lower().split("x"))

    rendered, failed = [], []
    for i, (name, load) in enumerate(models, 1):
        suffix = f"_{args.suffix}" if args.suffix else ""
        output_path = os.path.join(out_dir, f"{name}{suffix}.png")
        print(f"[{i}] {name}", file=sys.stderr)
        _clear_scene()
        try:
            load()
            # Cel-shaded models are built with inverted-hull outlines: a
            # black copy of the body, normals pointing inward, drawn with
            # front faces culled so only the silhouette shows. Rendered
            # unculled that hull simply swallows the model.
            for bl_material in bpy.data.materials:
                bl_material.use_backface_culling = True
            points = _world_points()
            _setup_three_point_lighting()
            _setup_camera(points, resolution)
            _render(output_path, resolution=resolution)
            rendered.append(output_path)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))

    print(f"\nrendered {len(rendered)}/{len(rendered) + len(failed)} into {out_dir}")
    for name, error in failed:
        print(f"  FAILED {name}: {error}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
