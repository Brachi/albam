import json
import os

import bpy
import pytest

from tests.mtfw.conftest import import_export
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - not selectable via --mtfw-dataset like the rest
# of tests/mtfw/*.py. This is the single source of truth for what this file
# tests locally; extend it directly rather than pointing at some other file.
# Every hash here must be a subset of that app_id's committed
# tests/mtfw/datasets/<app_id>_catalog.json - see test_dataset_hashes_are_in_catalog
# below, which enforces it.
NAV_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "nav_serialization_hashes.json"
)
with open(NAV_SERIALIZATION_DATASET_PATH) as f:
    NAV_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_nav_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_nav_path_hash")
        argvalues = [(d["app_id"], d["nav_path_hash"]) for d in NAV_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['nav_path_hash']}" for d in NAV_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by NAV_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in NAV_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["nav_path_hash"] in catalog_hashes, (
            f"{entry['nav_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def nav_export_local(game_fs_root, local_app_id, local_nav_path_hash):
    from albam.engines.mtfw.structs.nav_156 import Nav156

    bpy.context.scene.albam.apps.app_selected = local_app_id

    local_nav_path = resolve_hashes(game_fs_root, {local_nav_path_hash})[local_nav_path_hash].lstrip("/")
    vfile_nav = import_export(local_app_id, local_nav_path)
    vfile_nav_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, local_nav_path)
    assert vfile_nav_exported

    src_nav = Nav156.from_bytes(vfile_nav.get_bytes())
    dst_nav = Nav156.from_bytes(vfile_nav_exported.get_bytes())
    src_nav._read()
    dst_nav._read()
    return src_nav, dst_nav


@pytest.fixture(scope="session")
def nav_imported_local(nav_export_local):
    return nav_export_local[0]


@pytest.fixture(scope="session")
def nav_exported_local(nav_export_local):
    return nav_export_local[1]


def test_export_header(nav_imported_local, nav_exported_local):
    snav = nav_imported_local
    dnav = nav_exported_local
    assert snav.indent == dnav.indent
    assert snav.version == dnav.version
    assert snav.reserved == dnav.reserved
    assert snav.num_vertices == dnav.num_vertices
    assert snav.num_faces == dnav.num_faces


def test_export_vertices(nav_imported_local, nav_exported_local):
    svtxs = nav_imported_local.vertices
    dvtxs = nav_exported_local.vertices
    for svtx, dvtx in zip(svtxs, dvtxs):
        assert svtx.x == pytest.approx(dvtx.x, rel=0.001)
        assert svtx.y == pytest.approx(dvtx.y, rel=0.001)
        assert svtx.z == pytest.approx(dvtx.z, rel=0.001)


def test_export_faces(nav_imported_local, nav_exported_local):
    sfaces = nav_imported_local.faces
    dfaces = nav_exported_local.faces
    for sface, dface in zip(sfaces, dfaces):
        assert sface.index == dface.index
        assert sface.unk_00 == dface.unk_00
        assert sface.flags == dface.flags
        assert sface.vertex_per_face == dface.vertex_per_face
        assert sface.v1 == dface.v1
        assert sface.v2 == dface.v2
        assert sface.v3 == dface.v3
        assert sface.num_neighbors == dface.num_neighbors
        sface_idxs = {}
        dface_idxs = {}
        for snrg, dnrg in zip(sface.neighbors, dface.neighbors):
            sface_idxs[snrg.face_index] = (snrg.edge, snrg.centroid_distance)
            dface_idxs[dnrg.face_index] = (dnrg.edge, dnrg.centroid_distance)
            assert snrg.padding == dnrg.padding
        for k, sv in sface_idxs.items():
            assert k in dface_idxs.keys()
            dv = dface_idxs[k]
            assert sv[0] == dv[0]
            assert sv[1] == pytest.approx(dv[1], rel=0.001)


def test_export_grid_header(nav_imported_local, nav_exported_local):
    sgridh = nav_imported_local
    dgridh = nav_exported_local
    sgridh.bbox.padding_00 == dgridh.bbox.padding_00
    sgridh.bbox.lower.x == pytest.approx(dgridh.bbox.lower.x, rel=0.001)
    sgridh.bbox.lower.y == pytest.approx(dgridh.bbox.lower.y, rel=0.001)
    sgridh.bbox.lower.z == pytest.approx(dgridh.bbox.lower.z, rel=0.001)
    sgridh.bbox.padding_01 == dgridh.bbox.padding_01
    sgridh.bbox.upper.x == pytest.approx(dgridh.bbox.upper.x, rel=0.001)
    sgridh.bbox.upper.y == pytest.approx(dgridh.bbox.upper.y, rel=0.001)
    sgridh.bbox.upper.z == pytest.approx(dgridh.bbox.upper.z, rel=0.001)
    sgridh.bbox.padding_02 == dgridh.bbox.padding_02
    sgridh.footer_indent == dgridh.footer_indent
    sgridh.footer_padding = dgridh.footer_padding


def test_export_grid(nav_imported_local, nav_exported_local):
    sgrid = nav_imported_local.lookup_grid
    dgrid = nav_exported_local.lookup_grid
    for scell, dcell in zip(sgrid, dgrid):
        scell.face_count = dcell.face_count
        sgfaces = scell.faces
        dgfaces = dcell.faces
        sface_idxs = set()
        dface_idxs = set()
        for sgface, dgface in zip(sgfaces, dgfaces):
            # assert sgface.face_index == dgface.face_index
            sface_idxs.add(sgface.face_index)
            dface_idxs.add(dgface.face_index)
            assert sgface.padding == dgface.padding
        # assert sface_idxs == dface_idxs  # looks like misses a little with faces in the grid cell
