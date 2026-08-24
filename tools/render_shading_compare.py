"""
Renders partygirl.edgemodel and hunk.edgemodel (RE:ORC, app_id "reorc") under a
plain 3-point light rig, for before/after comparisons while working on
albam/engines/hexn/material.py's shading.

Runs against the `bpy` pip package in .venv (Python 3.13, Blender 5.2), same
as pytest - not the real Blender application. Source data is the small local
.ssg pair at tests/data/orc/{partygirl,hunk}.ssg (real game data, gitignored,
already present on disk - see tests/data/orc/).

Usage:
    .venv/bin/python tools/render_shading_compare.py before
    .venv/bin/python tools/render_shading_compare.py after <description>

`before` always writes tools/renders/<model>_before.png (the fixed baseline,
never overwritten past the first run). `after` runs are numbered
sequentially so the whole fix history stays on disk and browsable in order:
tools/renders/<model>_after-<NNN>-<description>.png, where <NNN> is one past
the highest sequence number already present in tools/renders/ (shared across
both models for a given run, so partygirl/hunk from the same invocation get
matching numbers).
"""
import math
import os
import re
import sys

import bpy
from mathutils import Vector

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Script-mode execution puts this file's own dir at sys.path[0] instead of
# the repo root, which can let a stale/partial "albam" dir elsewhere on
# sys.path (e.g. a concurrent `pip install` from another process sharing
# this venv) shadow the real package as an empty namespace package.
sys.path.insert(0, REPO_ROOT)
GAME_DATA_DIR = os.path.join(REPO_ROOT, "tests", "data", "orc")
OUTPUT_DIR = os.path.join(REPO_ROOT, "tools", "renders")

APP_ID = "reorc"
MODELS = {
    "partygirl": "dlc/pack1/characters/partygirl/models/partygirl.edgemodel",
    "hunk": "dlc/pack1/characters/hunk/models/hunk.edgemodel",
}


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block_collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.lights):
        for block in list(block_collection):
            block_collection.remove(block)


def _mount_vfs():
    from albam.engines.hexn.fs import HexnFS

    bpy.context.scene.albam.apps.app_selected = APP_ID
    vfs = bpy.context.scene.albam.vfs
    game_fs = HexnFS(GAME_DATA_DIR)
    vfs.add_fs_root(APP_ID, game_fs, display_name="orc-local")
    return vfs


def _import_model(vfs, relative_path):
    vfs.select_vfile(APP_ID, relative_path)
    result = bpy.ops.albam.import_vfile()
    if result != {"FINISHED"}:
        raise RuntimeError(f"Import failed for {relative_path!r}: {result}")
    return bpy.context.selected_objects


def _bounding_box_world():
    """World-space bounding box (min, max) across every mesh object in the scene."""
    corners = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            corners.append(obj.matrix_world @ Vector(corner))
    if not corners:
        raise RuntimeError("No mesh objects found to frame")
    xs, ys, zs = zip(*corners)
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def _setup_three_point_lighting(target, key_strength=2.5, fill_strength=0.9, rim_strength=1.4):
    """Gentle 3-point rig using Sun lamps (distance-independent strength, so it
    doesn't need re-tuning per character scale). Key at front-left-above, fill
    at front-right (soft, low), rim from behind-above for silhouette separation.
    """
    def _add_sun(name, strength, rotation_euler):
        light_data = bpy.data.lights.new(name=name, type="SUN")
        light_data.energy = strength
        light_data.angle = math.radians(15)  # soft-ish shadows, not a pinpoint sun
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        light_obj.rotation_euler = rotation_euler
        bpy.context.collection.objects.link(light_obj)
        return light_obj

    # Rotations are aim directions expressed as euler angles (sun lamps only
    # care about orientation, not position) - roughly: key from front-left-high,
    # fill from front-right-low (softer, no strong shadow read), rim from
    # behind-high for a subtle edge light.
    _add_sun("Key", key_strength, (math.radians(55), 0, math.radians(-35)))
    _add_sun("Fill", fill_strength, (math.radians(75), 0, math.radians(50)))
    _add_sun("Rim", rim_strength, (math.radians(140), 0, math.radians(160)))

    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.05, 0.05, 0.06, 1.0)
        bg.inputs["Strength"].default_value = 1.0


def _setup_camera(bbox_min, bbox_max, fov_deg=40):
    center = (bbox_min + bbox_max) / 2
    dimensions = bbox_max - bbox_min
    height = dimensions.z
    radius = max(dimensions.x, dimensions.y, height) / 2

    fov = math.radians(fov_deg)
    distance = (height / 2) / math.tan(fov / 2) * 1.35  # headroom so the whole character fits
    distance = max(distance, radius * 2.2)

    # Slightly elevated 3/4-ish front view - common "character showcase" angle.
    azimuth = math.radians(-25)
    elevation = math.radians(12)
    cam_offset = Vector((
        math.sin(azimuth) * math.cos(elevation),
        -math.cos(azimuth) * math.cos(elevation),
        math.sin(elevation),
    )) * distance
    cam_location = center + cam_offset

    cam_data = bpy.data.cameras.new("RenderCamera")
    cam_data.lens_unit = "FOV"
    cam_data.angle = fov
    cam_obj = bpy.data.objects.new("RenderCamera", cam_data)
    cam_obj.location = cam_location
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    direction = center - cam_location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    return cam_obj


def _render(output_path, resolution=(1024, 1536)):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


_AFTER_SEQ_RE = re.compile(r"_after-(\d+)-")


def _next_after_sequence():
    """One past the highest after-<NNN>- sequence number already on disk, so
    a whole fix history stays browsable in order instead of each run
    overwriting the last."""
    max_seq = 0
    if os.path.isdir(OUTPUT_DIR):
        for name in os.listdir(OUTPUT_DIR):
            match = _AFTER_SEQ_RE.search(name)
            if match:
                max_seq = max(max_seq, int(match.group(1)))
    return max_seq + 1


def _slugify(description):
    return re.sub(r"[^a-z0-9]+", "_", description.strip().lower()).strip("_")


def render_model(vfs, model_name, relative_path, filename_stem):
    _clear_scene()
    _import_model(vfs, relative_path)
    bbox_min, bbox_max = _bounding_box_world()
    _setup_three_point_lighting(target=(bbox_min + bbox_max) / 2)
    _setup_camera(bbox_min, bbox_max)

    output_path = os.path.join(OUTPUT_DIR, f"{model_name}_{filename_stem}.png")
    _render(output_path)
    return output_path


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("before", "after"):
        print(__doc__)
        sys.exit(1)
    stage = sys.argv[1]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if stage == "before":
        filename_stem = "before"
    else:
        if len(sys.argv) < 3:
            print("after requires a <description>, e.g.:\n"
                  "  .venv/bin/python tools/render_shading_compare.py after roughness")
            sys.exit(1)
        filename_stem = f"after-{_next_after_sequence():03d}-{_slugify(sys.argv[2])}"

    from albam import register
    register()

    vfs = _mount_vfs()

    for model_name, relative_path in MODELS.items():
        path = render_model(vfs, model_name, relative_path, filename_stem)
        print(f"Rendered {model_name} ({stage}): {path}")


if __name__ == "__main__":
    main()
