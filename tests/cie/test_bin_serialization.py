"""
Round-trip a real RE4 UHD model through the import and export functions:
import it, export it, import what came out, and check the model survived.

Unlike tests/cie/test_lfs_fs.py, which only reads, this drives the registry,
the VFS and the material and armature building the way an actual import and
export do - so it covers the parts a parsing test cannot reach.

What is compared, and what deliberately is not: triangles, materials and
bones have to match exactly, and so do every material's texture slots.
Vertex counts do not. The format shares no vertices between faces and export
writes each triangle as three corners of its own, so a model whose original
used triangle strips comes back with more vertices describing the same
surface (see albam/engines/cie/mesh.py).
"""
import json
import os

import bpy
import pytest

from albam.lib import fs_registry
from tests.cie.lfs_paths import resolve_archive_hashes

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "bin_serialization_hashes.json")
with open(DATASET_PATH) as f:
    BIN_SERIALIZATION_DATASET = json.load(f)

MESH_FLAG_OFFSET = 0x20
MESH_FLAG = 0x80000000


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in BIN_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in BIN_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - see
    tests/cie/test_lfs_fs.py, same check. CI-safe."""
    for entry in BIN_SERIALIZATION_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        assert entry["archive_path_hash"] in catalog, (
            f"{entry['archive_path_hash']!r} is not in {catalog_path!r}"
        )


@pytest.fixture
def _clean_scene():
    # vfs, exported and bpy.data are session-scoped state: register() runs
    # once per pytest session, so a test that leaves objects or roots behind
    # changes what the next one sees.
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    bpy.context.scene.albam.vfs.file_list.clear()
    bpy.context.scene.albam.exported.file_list.clear()
    fs_registry.clear()


def _is_mesh_bin(data):
    if len(data) < MESH_FLAG_OFFSET + 4:
        return False
    return bool(int.from_bytes(
        data[MESH_FLAG_OFFSET:MESH_FLAG_OFFSET + 4], "little") & MESH_FLAG)


def _model_state(bl_object):
    """What has to survive a round trip."""
    meshes = [o for o in bl_object.children_recursive if o.type == "MESH"]
    if bl_object.type == "MESH":
        meshes.append(bl_object)
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    materials = [slot.material for o in meshes for slot in o.material_slots if slot.material]
    return {
        "triangles": sum(len(polygon.vertices) - 2
                         for o in meshes for polygon in o.data.polygons),
        "materials": len(materials),
        "bones": len(armatures[0].data.bones) if armatures else 0,
        "vertices": sum(len(o.data.vertices) for o in meshes),
    }


def _texture_slots(bin_bytes):
    """Every material's texture indices, as the file stores them."""
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()
    return [(m.diffuse_map, m.bump_map, m.opacity_map,
             m.generic_specular_map, m.custom_specular_map, m.material_flag)
            for m in parsed.materials]


def test_bin_round_trips_through_export(game_root, local_app_id,
                                        local_archive_path_hash, _clean_scene):
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)

    models = [vf for vf in vfs.file_list
              if vf.tree_node.root_id == root.name and not vf.is_root and
              vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]
    assert models, "this archive should hold a mesh .bin"
    vfile = models[0]

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    export_function = blender_registry.export_registry[(local_app_id, "bin")]

    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    original_bytes = vfile.get_bytes()
    bl_object = import_function(vfile, bpy.context)
    before = _model_state(bl_object)
    assert before["triangles"] > 0

    bl_object.albam_asset.app_id = local_app_id
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = vfile.display_name
    bl_object.albam_asset.original_bytes = original_bytes
    vfiles = export_function(bl_object)
    assert len(vfiles) == 1
    exported_bytes = vfiles[0].data_bytes
    assert _is_mesh_bin(exported_bytes), "the exported file should read as a mesh"

    # Texture slots are rebuilt from the material's image nodes rather than
    # carried, so they are worth checking on their own: getting them wrong
    # still produces a valid file, just an untextured one.
    assert _texture_slots(exported_bytes) == _texture_slots(original_bytes)

    exported_vfs = bpy.context.scene.albam.exported
    exported_vfs.add_export_root(local_app_id, "serialization-test", vfiles)
    reimported = next(vf for vf in exported_vfs.file_list
                      if not vf.is_root and vf.display_name == vfile.display_name)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    bl_object = import_function(reimported, bpy.context)
    after = _model_state(bl_object)

    assert after["triangles"] == before["triangles"]
    assert after["materials"] == before["materials"]
    assert after["bones"] == before["bones"]
