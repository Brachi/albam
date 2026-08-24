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
    elif "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", ["reorc"], scope="session")


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


# Real .edgemodel meshes use 11 distinct real vertex strides across a
# full-game sweep (12, 16, 24, 28, 32, 40, 44, 52, 56, 60, 64), only ~76%
# of meshes actually using 52 - build_blender_mesh() must read each mesh
# at its own real stride rather than a fixed one, since misreading at the
# wrong stride scrambles every vertex position past the first into an
# unrecognizable blob. Reuses this file's own vector.edgemodel hash
# (9b51865995033c55) rather than a new one - mesh_index 12 there has a
# real stride-12 vertex format (no UV/normal/color, just position), a
# convenient already-verified case.
VECTOR_EDGEMODEL_HASH = "9b51865995033c55"
STRIDE_12_MESH_INDEX = 12


def test_non_52_stride_produces_a_coherent_mesh(game_fs_root, local_app_id):
    import struct

    from albam.engines.hexn.mesh import build_blender_mesh
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel

    path = resolve_hashes(game_fs_root, {VECTOR_EDGEMODEL_HASH})[VECTOR_EDGEMODEL_HASH]
    edgemodel = HexaneEdgemodel.from_bytes(game_fs_root.readbytes(path))
    edgemodel._read()

    mesh_header = edgemodel.meshes_header[STRIDE_12_MESH_INDEX]
    mesh = mesh_header.mesh
    correct_stride = mesh.size_buffer_vertices // mesh.num_vertices
    assert correct_stride == 12

    # Doesn't crash: build_blender_mesh()'s UV read is guarded on has_uvs
    # rather than unconditionally reading a fixed offset (24/26) - this
    # stride (no room for UV data at all) would otherwise run
    # unpack_from() straight past the end of the buffer. Exercises that
    # guard directly (12 < 28).
    bl_object = build_blender_mesh(mesh_header, {})
    assert len(bl_object.data.vertices) == mesh.num_vertices

    # "How big is this mesh" isn't a stable thing to assert on (this one's
    # a real, human-sized body part, not a small prop), but consecutive
    # vertices in a real mesh's own buffer are typically close together
    # (shared triangles/strips) regardless of the model's overall size -
    # reading at the wrong stride destroys that locality by drifting out
    # of alignment with every vertex read. Compare directly instead of
    # against an absolute threshold.
    def mean_neighbor_distance(stride):
        # The "wrong" (52) stride reads past the real buffer well before
        # num_vertices - cap to whatever actually fits, at either stride.
        count = min(mesh.num_vertices, len(mesh.buffer_vertices) // stride)
        positions = [
            struct.unpack_from('fff', mesh.buffer_vertices, vi * stride)
            for vi in range(count)
        ]
        deltas = (
            sum((a - b) ** 2 for a, b in zip(p1, p2)) ** 0.5
            for p1, p2 in zip(positions, positions[1:])
        )
        return sum(deltas) / (count - 1)

    correct_distance = mean_neighbor_distance(correct_stride)
    wrong_distance = mean_neighbor_distance(52)
    assert correct_distance < wrong_distance / 10, (
        f"expected the correct stride ({correct_stride}) to produce much more spatially "
        f"coherent geometry than reading at stride 52 - got {correct_distance} vs {wrong_distance}"
    )
