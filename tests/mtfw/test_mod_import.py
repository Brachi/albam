"""Import a .mod through the real Blender operator stack and check what
came out.

The other *_serialization.py files drive import->export round trips and
compare bytes; this one stops at import and asserts on the Blender data
instead. That covers the apps albam can import but not yet export (umvc3),
and it catches the whole class of breakage - a missing material type, an
unmapped texture slot, a bad bone hierarchy - that a byte-level round trip
happily reproduces without ever building a usable model.
"""
import json
import os

import bpy
import pytest

from tests.mtfw.conftest import clear_scene, import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# import (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
MOD_IMPORT_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "mod_import_hashes.json")
with open(MOD_IMPORT_DATASET_PATH) as f:
    MOD_IMPORT_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash")
        argvalues = [(d["app_id"], d["mod_path_hash"]) for d in MOD_IMPORT_DATASET]
        ids = [f"{d['app_id']}-{d['mod_path_hash']}" for d in MOD_IMPORT_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MOD_IMPORT_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in MOD_IMPORT_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mod_path_hash"] in catalog_hashes, (
            f"{entry['mod_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="module")
def imported_mod(game_fs_root, local_app_id, local_mod_path_hash):
    """One import per model, into a scene emptied of the previous one, so
    every assertion below reads only this model's own data.

    Module-scoped rather than session-scoped: the parametrization is
    session-scoped (game_fs_root needs it to be), so pytest runs all of
    this file's tests for one model together and rebuilds the fixture when
    the model changes - each model is imported once, not once per test.
    """
    clear_scene()

    # resolve_hashes() returns MTFW_FS's own canonical form (leading "/"),
    # but vfs.add_fs_root() builds its tree with that stripped (see
    # albam.vfs.VirtualFileSystemBase.add_fs_root) - select_vfile()
    # expects the stripped form.
    path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash]
    bpy.context.scene.albam.import_settings.import_only_main_lods = False

    vfile = import_vfile(local_app_id, path.lstrip("/"))
    bl_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    bl_armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    yield vfile, bl_meshes, bl_armatures
    clear_scene()


def test_mod_import_builds_geometry(imported_mod):
    _vfile, bl_meshes, _bl_armatures = imported_mod

    assert bl_meshes, "import produced no mesh objects"
    for bl_mesh in bl_meshes:
        assert len(bl_mesh.data.vertices) > 0, f"{bl_mesh.name} has no vertices"
        assert len(bl_mesh.data.polygons) > 0, f"{bl_mesh.name} has no faces"
        # A degenerate face means the index buffer was misread - the model
        # still "imports", it just renders as nothing.
        assert all(len(set(p.vertices)) == len(p.vertices) for p in bl_mesh.data.polygons), (
            f"{bl_mesh.name} has faces with repeated vertices"
        )


def test_mod_import_builds_materials(imported_mod):
    """Every imported mesh must end up with a material driven by albam's own
    shader group. A material type or texture slot albam doesn't know about
    surfaces here rather than silently producing an untextured model.
    """
    from albam.engines.mtfw.material import MTFW_SHADER_NODEGROUP_NAME

    _vfile, bl_meshes, _bl_armatures = imported_mod

    for bl_mesh in bl_meshes:
        assert bl_mesh.data.materials, f"{bl_mesh.name} has no material"
        for bl_mat in bl_mesh.data.materials:
            group = bl_mat.node_tree.nodes.get("MTFrameworkGroup")
            assert group is not None, (
                f"{bl_mat.name} has no MTFrameworkGroup node"
            )
            assert group.node_tree.name == MTFW_SHADER_NODEGROUP_NAME


def test_mod_import_builds_skeleton(imported_mod):
    """A skinned model's armature must be complete and acyclic, and every
    vertex group must name a real bone - a mismatch there means the bone
    palette was misread and the model would deform into garbage.
    """
    _vfile, bl_meshes, bl_armatures = imported_mod

    if not bl_armatures:
        pytest.skip("model has no skeleton")
    assert len(bl_armatures) == 1
    bones = bl_armatures[0].data.bones
    assert len(bones) > 0

    for bone in bones:
        seen = set()
        parent = bone.parent
        while parent is not None:
            assert parent.name not in seen, f"cycle in the bone hierarchy at {bone.name}"
            seen.add(parent.name)
            parent = parent.parent

    bone_names = {b.name for b in bones}
    for bl_mesh in bl_meshes:
        unknown = {vg.name for vg in bl_mesh.vertex_groups} - bone_names
        assert not unknown, f"{bl_mesh.name} weighted to non-existent bones: {sorted(unknown)}"


def test_mod_import_textures_are_resolved(imported_mod):
    """Every image texture node albam wires up must actually carry an image.

    An empty node is how a texture that couldn't be found or decoded shows
    up - the import still "succeeds", but the model arrives untextured.
    """
    _vfile, bl_meshes, _bl_armatures = imported_mod

    missing = []
    for bl_mesh in bl_meshes:
        for bl_mat in bl_mesh.data.materials:
            for node in bl_mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is None:
                    missing.append(f"{bl_mat.name}/{node.name}")
    assert not missing, f"image nodes with no image: {sorted(set(missing))}"
