import io
import json
import os

import pytest
from kaitaistruct import KaitaiStream

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below), same pattern as
# tests/mtfw/test_mod_parsing.py - extend this directly to add more.
MESH_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "mesh_parsing_hashes.json")
with open(MESH_PARSING_DATASET_PATH) as f:
    MESH_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mesh_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mesh_path_hash")
        argvalues = [(d["app_id"], d["mesh_path_hash"]) for d in MESH_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['mesh_path_hash']}" for d in MESH_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MESH_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no real .pak needed.
    """
    for entry in MESH_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mesh_path_hash"] in catalog_hashes, (
            f"{entry['mesh_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_mesh(pak_fs_root, local_mesh_path_hash):
    from albam.engines.reng.structs.reengine_mesh import ReengineMesh

    path = resolve_hashes(pak_fs_root, {local_mesh_path_hash})[local_mesh_path_hash]
    src_bytes = pak_fs_root.readbytes(path)

    parsed = ReengineMesh(KaitaiStream(io.BytesIO(src_bytes)))
    parsed._read()
    return parsed, src_bytes


def test_mesh(parsed_mesh):
    mesh, src_bytes = parsed_mesh

    assert mesh.id_magic == b"MESH"
    assert mesh.file_size == len(src_bytes)

    if mesh.model_info is None:
        # Buffers-only variant (e.g. occlusion-culling meshes): no
        # model/mesh-group tree, header.offset_data == 0 - see RESULTS.md.
        assert mesh.header.offset_data == 0
        assert mesh.buffers_data.size_vertex_buffer > 0
        return

    model = mesh.model_info.model_offsets[0].model
    assert model.num_mesh_groups == len(model.mesh_groups)
    assert model.num_mesh_groups > 0

    total_sub_meshes = sum(len(mg.mesh_group.meshes) for mg in model.mesh_groups)
    assert total_sub_meshes > 0
