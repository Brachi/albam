import json
import math
import os
import struct

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Reuses test_edgemodel_parsing.py's own committed, catalog-verified dataset
# (see its test_dataset_hashes_are_in_catalog) - same convention already
# used by test_material_layout.py for the same reason: no new hashes needed
# to cover a range of real meshes.
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
    for entry in EDGEMODEL_PARSING_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["edgemodel_path_hash"] in catalog_hashes, (
            f"{entry['edgemodel_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


def test_normals_are_unit_length_and_shading_is_smooth(
        game_fs_root, local_app_id, local_edgemodel_path_hash, subtests):
    """
    Regression check for build_blender_mesh() leaving imported meshes flat-
    shaded: normal is a plain float32 xyz at buffer_vertices offset 12 for
    any vertex_stride >= 24 (confirmed against real geometry - decoded
    vector is unit-length to float32 precision and aligns with the real
    triangle's geometric face normal on single-triangle/quad test props;
    not some packed/quantized format). Without polygons.foreach_set(
    "use_smooth", ...) before normals_split_custom_set_from_vertices(), the
    custom normal data is set but every polygon renders flat regardless
    (same class of bug already found and fixed in the mtfw engine this
    session). Imports real meshes and asserts both halves: the data is
    real unit vectors, and Blender is actually set up to use them.
    """
    from albam.engines.hexn.mesh import build_blender_mesh
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel

    path = resolve_hashes(game_fs_root, {local_edgemodel_path_hash})[local_edgemodel_path_hash]
    edgemodel_bytes = game_fs_root.readbytes(path)
    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    edgemodel._read()

    checked = 0
    for mi, mesh_header in enumerate(edgemodel.meshes_header):
        if mesh_header.lod != 0:
            continue
        mesh = mesh_header.mesh
        if mesh.num_vertices == 0:
            continue
        stride = mesh.size_buffer_vertices // mesh.num_vertices
        if stride < 24:
            continue
        with subtests.test(mesh_index=mi):
            bl_ob = build_blender_mesh(mesh_header, {})
            bl_mesh = bl_ob.data
            if not bl_mesh.polygons:
                continue
            checked += 1
            assert all(p.use_smooth for p in bl_mesh.polygons), (
                "expected every polygon to be marked smooth once normal data is present"
            )
            for vi in range(mesh.num_vertices):
                off = vi * stride
                nx, ny, nz = struct.unpack_from('fff', mesh.buffer_vertices, off + 12)
                mag = math.sqrt(nx * nx + ny * ny + nz * nz)
                assert mag == mag, f"mesh {mi} vertex {vi}: normal is NaN"
                assert abs(mag - 1.0) < 0.01, (
                    f"mesh {mi} vertex {vi}: expected a unit-length normal, got magnitude {mag}"
                )
    if not checked:
        import pytest
        pytest.skip("no lod-0 mesh in this model has a vertex_stride >= 24")


def test_tangent_orthogonal_to_normal(game_fs_root, local_app_id, local_edgemodel_path_hash, subtests):
    """
    Regression check for the confirmed vertex_stride == 52 tangent layout
    (buffer_vertices offset 28, a third float32 xyz right after position
    and normal - part of a real orthonormal TBN triad together with an
    unimported bitangent at offset 40, confirmed on real geometry: all
    three read back unit-length, mutually perpendicular to 6+ decimal
    places). A wrong offset/scale would fail either check below; this
    isn't confirmed for any other stride, so only stride == 52 is checked.
    """
    from albam.engines.hexn.mesh import build_blender_mesh
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel

    path = resolve_hashes(game_fs_root, {local_edgemodel_path_hash})[local_edgemodel_path_hash]
    edgemodel_bytes = game_fs_root.readbytes(path)
    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    edgemodel._read()

    checked = 0
    for mi, mesh_header in enumerate(edgemodel.meshes_header):
        if mesh_header.lod != 0:
            continue
        mesh = mesh_header.mesh
        if mesh.num_vertices == 0:
            continue
        stride = mesh.size_buffer_vertices // mesh.num_vertices
        if stride != 52:
            continue
        with subtests.test(mesh_index=mi):
            bl_ob = build_blender_mesh(mesh_header, {})
            bl_mesh = bl_ob.data
            assert 'tangent' in bl_mesh.attributes
            checked += 1
            tangent_attr = bl_mesh.attributes['tangent']
            for vi in range(mesh.num_vertices):
                off = vi * stride
                nx, ny, nz = struct.unpack_from('fff', mesh.buffer_vertices, off + 12)
                n_mag = math.sqrt(nx * nx + ny * ny + nz * nz)
                tx, ty, tz = tangent_attr.data[vi].vector
                t_mag = math.sqrt(tx * tx + ty * ty + tz * tz)
                assert abs(t_mag - 1.0) < 0.01, f"mesh {mi} vertex {vi}: tangent magnitude {t_mag}"
                dot = (nx * tx + ny * ty + nz * tz) / (n_mag * t_mag)
                assert abs(dot) < 0.05, (
                    f"mesh {mi} vertex {vi}: expected tangent roughly orthogonal to normal, "
                    f"got dot={dot}"
                )
    if not checked:
        import pytest
        pytest.skip("no lod-0 mesh in this model has vertex_stride == 52")
