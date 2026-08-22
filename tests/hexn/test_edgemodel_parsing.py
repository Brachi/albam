import json
import os

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
EDGEMODEL_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "edgemodel_parsing_hashes.json")
with open(EDGEMODEL_PARSING_DATASET_PATH) as f:
    EDGEMODEL_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_edgemodel_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_edgemodel_path_hash")
        argvalues = [(d["app_id"], d["edgemodel_path_hash"]) for d in EDGEMODEL_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['edgemodel_path_hash']}" for d in EDGEMODEL_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by EDGEMODEL_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in EDGEMODEL_PARSING_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["edgemodel_path_hash"] in catalog_hashes, (
            f"{entry['edgemodel_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


def test_parse_edgemodel(game_fs_root, local_app_id, local_edgemodel_path_hash):
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel

    path = resolve_hashes(game_fs_root, {local_edgemodel_path_hash})[local_edgemodel_path_hash]
    edgemodel_bytes = game_fs_root.readbytes(path)

    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    edgemodel._read()

    assert edgemodel.header.id_magic == b"FM6S"
    assert edgemodel.header.num_meshes > 0
    assert len(edgemodel.meshes_header) == edgemodel.header.num_meshes

    main_lods = [mh for mh in edgemodel.meshes_header if mh.lod == 0]
    assert main_lods, "expected at least one lod-0 mesh"

    for mesh_header in main_lods:
        mesh = mesh_header.mesh
        assert mesh.num_vertices > 0
        assert mesh.num_indices > 0
        assert mesh.num_indices % 3 == 0
        assert len(mesh.buffer_vertices) == mesh.size_buffer_vertices
        assert len(mesh.buffer_indices) == mesh.size_buffer_indices
        assert mesh_header.materials.first_material
