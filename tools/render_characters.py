"""Renders every character model an app can import, one PNG per character.

A visual counterpart to tools/mod_import_sweep.py: the sweep says an import
raised no exception, this says whether what came out looks like the
character. Geometry that imports "successfully" with a flipped normal, a
missing texture or a collapsed skeleton is obvious in a render and invisible
in a pass/fail count.

Runs against the `bpy` pip package in .venv (Python 3.13, Blender 5.2), the
same interpreter pytest uses - not the real Blender application.

Usage:
    python tools/render_characters.py <app-id> <game-root> [--pattern REGEX]
                                      [--suffix NAME] [--limit N]

Example:

    python tools/render_characters.py umvc3 "/path/to/UMVC3" --suffix baseline

Writes tools/renders/<app-id>/<model>[_<suffix>].png. Pass --suffix to keep
a before/after pair side by side while working on shading.
"""
import argparse
import gc
import math
import os
import re
import sys

import bpy
from mathutils import Vector

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Script-mode execution puts this file's own dir at sys.path[0] instead of
# the repo root, which can let a stale/partial "albam" dir elsewhere on
# sys.path shadow the real package as an empty namespace package.
sys.path.insert(0, REPO_ROOT)
OUTPUT_ROOT = os.path.join(REPO_ROOT, "tools", "renders")

# Default: a game's own playable character models, one per character. Most MT
# Framework titles lay these out as chr/<Name>/model/1p/<Name>.mod.
DEFAULT_PATTERN = r"^/chr/[^/]+/model/1p/[^/]+\.mod$"


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                       bpy.data.lights, bpy.data.armatures, bpy.data.cameras):
        for block in list(collection):
            collection.remove(block)
    gc.collect()


def _bounding_box_world():
    """World-space bounding box (min, max) across every mesh object."""
    corners = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            corners.append(obj.matrix_world @ Vector(corner))
    if not corners:
        raise RuntimeError("no mesh objects to frame")
    xs, ys, zs = zip(*corners)
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


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


def _setup_camera(bbox_min, bbox_max, fov_deg=40):
    center = (bbox_min + bbox_max) / 2
    dimensions = bbox_max - bbox_min
    radius = max(dimensions.x, dimensions.y, dimensions.z) / 2

    fov = math.radians(fov_deg)
    distance = (dimensions.z / 2) / math.tan(fov / 2) * 1.35  # headroom
    distance = max(distance, radius * 2.2)

    # Slightly elevated 3/4 front view - the usual character showcase angle.
    azimuth, elevation = math.radians(-25), math.radians(12)
    cam_location = center + Vector((
        math.sin(azimuth) * math.cos(elevation),
        -math.cos(azimuth) * math.cos(elevation),
        math.sin(elevation),
    )) * distance

    cam_data = bpy.data.cameras.new("RenderCamera")
    cam_data.lens_unit = "FOV"
    cam_data.angle = fov
    cam_obj = bpy.data.objects.new("RenderCamera", cam_data)
    cam_obj.location = cam_location
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_obj.rotation_euler = (center - cam_location).to_track_quat("-Z", "Y").to_euler()


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


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
    parser.add_argument("--suffix", default=None,
                        help="appended to each filename, to keep runs side by side")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    import albam
    albam.register()
    from albam.engines.mtfw.arc_fs import MTFW_FS

    out_dir = os.path.join(OUTPUT_ROOT, args.app_id)
    os.makedirs(out_dir, exist_ok=True)

    game_fs = MTFW_FS(args.game_root)
    rx = re.compile(args.pattern, re.IGNORECASE)
    paths = sorted(p for p in game_fs.walk.files()
                   if p.lower().endswith(".mod") and rx.match(p))
    if args.limit:
        paths = paths[:args.limit]
    print(f"{len(paths)} models", file=sys.stderr)

    bpy.context.scene.albam.apps.app_selected = args.app_id
    bpy.context.scene.albam.import_settings.import_only_main_lods = True
    vfs = bpy.context.scene.albam.vfs
    vfs.add_fs_root(args.app_id, game_fs, display_name=f"{args.app_id}-render")

    rendered, failed = [], []
    for i, path in enumerate(paths, 1):
        name = _model_name(path)
        suffix = f"_{args.suffix}" if args.suffix else ""
        output_path = os.path.join(out_dir, f"{name}{suffix}.png")
        print(f"[{i}/{len(paths)}] {name}", file=sys.stderr)
        _clear_scene()
        try:
            # add_fs_root() strips the leading "/" when building its tree
            vfile = vfs.select_vfile(args.app_id, path.lstrip("/"))
            if vfile is None:
                raise KeyError(path)
            result = bpy.ops.albam.import_vfile()
            if result != {"FINISHED"}:
                raise RuntimeError(f"import_vfile returned {result}")
            bbox_min, bbox_max = _bounding_box_world()
            _setup_three_point_lighting()
            _setup_camera(bbox_min, bbox_max)
            _render(output_path)
            rendered.append(output_path)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))

    print(f"\nrendered {len(rendered)}/{len(paths)} into {out_dir}")
    for name, error in failed:
        print(f"  FAILED {name}: {error}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
