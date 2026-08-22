import ctypes
import io
import json
import os

import bpy
import pytest
from kaitaistruct import KaitaiStream

from tests.mtfw.scripts.catalog_paths import resolve_hashes
from tests.reng.conftest import reng_import

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# import, same set as test_mesh_parsing.py's dataset (see
# test_dataset_hashes_are_in_catalog below) but its own file, matching this
# project's one-dataset-per-test-concern convention (see tests/mtfw/).
#
# Full by default (every entry below) - importing pulls in materials/
# textures per file, so it's much slower than parsing-only tests (~2min for
# 16 files vs ~20s just parsing them). --reng-mesh-import-dataset=quick runs
# only the entries marked "quick": true - a small, still category-diverse
# subset (character+bones, weapon, building terrain, the no-main-model-tree
# occlusion mesh, a static prop), for a fast local dev loop.
MESH_IMPORT_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "mesh_import_hashes.json")
with open(MESH_IMPORT_DATASET_PATH) as f:
    MESH_IMPORT_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mesh_path_hash" in metafunc.fixturenames):
        dataset = MESH_IMPORT_DATASET
        if metafunc.config.getoption("reng_mesh_import_dataset") == "quick":
            dataset = [d for d in MESH_IMPORT_DATASET if d.get("quick")]

        argnames = ("local_app_id", "local_mesh_path_hash")
        argvalues = [(d["app_id"], d["mesh_path_hash"]) for d in dataset]
        ids = [f"{d['app_id']}-{d['mesh_path_hash']}" for d in dataset]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MESH_IMPORT_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no real .pak needed.
    """
    for entry in MESH_IMPORT_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mesh_path_hash"] in catalog_hashes, (
            f"{entry['mesh_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


def _expected_submesh_vertex_counts(re_mesh, sub_meshes):
    """A submesh's real vertex count isn't stored anywhere in the format -
    it's the number of *unique* values in its slice of the index buffer,
    same technique build_blender_mesh (albam/engines/reng/mesh.py) uses to
    build the actual Blender mesh. Assumes 16-bit indices, same as that
    function - true for every file in this dataset
    (model_info.has_32bit_index_buffer == 0).
    """
    index_buffer = re_mesh.buffers_data.index_buffer
    counts = []
    for sub_mesh in sub_meshes:
        index_offset = sub_mesh.pos_index_buffer * 2
        indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(index_buffer, index_offset)
        counts.append(len(set(indices)))
    return counts


@pytest.fixture(scope="session")
def imported_mesh(reng_vfs_root, local_app_id, local_mesh_path_hash):
    from albam.engines.reng.structs.reengine_mesh import ReengineMesh

    path = resolve_hashes(reng_vfs_root, {local_mesh_path_hash})[local_mesh_path_hash].lstrip("/")

    # bpy.data.objects.new(..., ...) as build_blender_mesh does gives every
    # submesh object the same literal name ("TMP", auto-disambiguated by
    # Blender) - nothing usable to look imported objects up by name, so a
    # before/after diff is the only way to find what this import created.
    before = set(bpy.data.objects.keys())
    vfile = reng_import(local_app_id, path)
    new_objects = [bpy.data.objects[name] for name in bpy.data.objects.keys() if name not in before]
    mesh_objects = [ob for ob in new_objects if ob.type == "MESH"]

    re_mesh = ReengineMesh(KaitaiStream(io.BytesIO(vfile.get_bytes())))
    re_mesh._read()

    return re_mesh, mesh_objects


def test_mesh_import(imported_mesh):
    re_mesh, mesh_objects = imported_mesh

    if re_mesh.model_info is None:
        # No main model tree (e.g. an occlusion-culling mesh, see
        # RESULTS.md) - build_blender_model only ever builds the main
        # model tree, so this legitimately imports zero mesh objects
        # rather than crashing.
        assert mesh_objects == []
        return

    lod_group = re_mesh.model_info.lod_group_offsets[0].lod_group
    sub_meshes = [sub_mesh for mg in lod_group.mesh_groups for sub_mesh in mg.mesh_group.meshes]

    assert len(mesh_objects) == len(sub_meshes)
    assert len(mesh_objects) > 0

    expected_vertex_counts = sorted(_expected_submesh_vertex_counts(re_mesh, sub_meshes))
    actual_vertex_counts = sorted(len(ob.data.vertices) for ob in mesh_objects)
    assert actual_vertex_counts == expected_vertex_counts
    assert sum(actual_vertex_counts) > 0
