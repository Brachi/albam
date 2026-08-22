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
SBC_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "sbc_serialization_hashes.json"
)
with open(SBC_SERIALIZATION_DATASET_PATH) as f:
    SBC_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_sbc_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_sbc_path_hash")
        argvalues = [(d["app_id"], d["sbc_path_hash"]) for d in SBC_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['sbc_path_hash']}" for d in SBC_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by SBC_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in SBC_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["sbc_path_hash"] in catalog_hashes, (
            f"{entry['sbc_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def sbc_export_local(game_fs_root, local_app_id, local_sbc_path_hash):
    from albam.engines.mtfw.collision import APPID_SBC_CLASS_MAPPER

    bpy.context.scene.albam.apps.app_selected = local_app_id

    local_sbc_path = resolve_hashes(game_fs_root, {local_sbc_path_hash})[local_sbc_path_hash].lstrip("/")
    vfile_sbc = import_export(local_app_id, local_sbc_path)
    vfile_sbc_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, local_sbc_path)
    assert vfile_sbc_exported

    Sbc = APPID_SBC_CLASS_MAPPER[local_app_id]
    src_sbc = Sbc.from_bytes(vfile_sbc.get_bytes())
    dst_sbc = Sbc.from_bytes(vfile_sbc_exported.get_bytes())
    src_sbc._read()
    dst_sbc._read()
    return src_sbc, dst_sbc


@pytest.fixture(scope="session")
def sbc_imported_local(sbc_export_local):
    return sbc_export_local[0]


@pytest.fixture(scope="session")
def sbc_exported_local(sbc_export_local):
    return sbc_export_local[1]


def test_export_header(sbc_imported_local, sbc_exported_local):
    sbc_version = 255 if sbc_imported_local.header.indent == b"SBC\xFF" else 49
    sheader = sbc_imported_local.header
    dheader = sbc_exported_local.header
    assert sheader.indent == dheader.indent
    assert sheader.num_objects == dheader.num_objects
    assert sheader.num_faces == dheader.num_faces
    assert sheader.num_vertices == dheader.num_vertices
    if sbc_version == 49:
        assert sheader.version == dheader.version
        assert sheader.num_boxes == dheader.num_boxes
    elif sbc_version == 255:
        assert sheader.unk_00 == dheader.unk_00
        assert sheader.num_stages == dheader.num_stages
        # assert sheader.num_pairs == dheader.num_pairs
    assert sheader.bounding_box.min[0] == pytest.approx(dheader.bounding_box.min[0], rel=0.001)
    assert sheader.bounding_box.min[1] == pytest.approx(dheader.bounding_box.min[1], rel=0.001)
    assert sheader.bounding_box.min[2] == pytest.approx(dheader.bounding_box.min[2], rel=0.001)
    assert sheader.bounding_box.max[0] == pytest.approx(dheader.bounding_box.max[0], rel=0.001)
    assert sheader.bounding_box.max[1] == pytest.approx(dheader.bounding_box.max[1], rel=0.001)
    assert sheader.bounding_box.max[2] == pytest.approx(dheader.bounding_box.max[2], rel=0.001)


def test_export_infos(sbc_imported_local, sbc_exported_local):
    sbc_version = 255 if sbc_imported_local.header.indent == b"SBC\xFF" else 49
    sinfos = sbc_imported_local.sbc_info
    dinfos = sbc_exported_local.sbc_info
    assert len(sinfos) == len(dinfos)
    i = 0
    for sinfo, dinfo in zip(sinfos, dinfos):
        if sbc_version == 255:
            assert sinfo.num_faces == dinfo.num_faces
            assert sinfo.num_vertices == dinfo.num_vertices
        print("info id:", i)
        assert sinfo.index_id == dinfo.index_id  # probably an id for scripting
        assert sinfo.bounding_box.min[0] == pytest.approx(dinfo.bounding_box.min[0], rel=0.001)
        assert sinfo.bounding_box.min[1] == pytest.approx(dinfo.bounding_box.min[1], rel=0.001)
        assert sinfo.bounding_box.min[2] == pytest.approx(dinfo.bounding_box.min[2], rel=0.001)
        assert sinfo.bounding_box.max[0] == pytest.approx(dinfo.bounding_box.max[0], rel=0.001)
        assert sinfo.bounding_box.max[1] == pytest.approx(dinfo.bounding_box.max[1], rel=0.001)
        assert sinfo.bounding_box.max[2] == pytest.approx(dinfo.bounding_box.max[2], rel=0.001)
        i += 1


def test_export_nodes(sbc_imported_local, sbc_exported_local):
    sbc_version = 255 if sbc_imported_local.header.indent == b"SBC\xFF" else 49
    if sbc_version == 255:
        sbvhc = sbc_imported_local.sbc_bvhc
        dbvhc = sbc_exported_local.sbc_bvhc
        for sbhv, dbvh in zip(sbvhc, dbvhc):
            assert sbhv.soh == dbvh.soh
            # assert sbhv.num_nodes == dbvh.num_nodes


def test_export_faces(sbc_imported_local, sbc_exported_local):
    sbc_version = 255 if sbc_imported_local.header.indent == b"SBC\xFF" else 49
    sfaces = sbc_imported_local.faces
    dfaces = sbc_exported_local.faces
    assert len(sfaces) == len(dfaces)
    for sface, dface in zip(sfaces, dfaces):
        assert sface.vert[0] == dface.vert[0]
        assert sface.vert[1] == dface.vert[1]
        assert sface.vert[2] == dface.vert[2]
        assert sface.type == dface.type
        if sbc_version == 49:
            assert sface.unk_00 == dface.unk_00  # probably junk
            assert sface.unk_01 == dface.unk_01  # probably junk
            assert sface.runtime_attr == dface.runtime_attr
            assert sface.special_attr == dface.special_attr  # 0 in re5
            assert sface.surface_attr == dface.surface_attr  # 0 in re5
        elif sbc_version == 255:
            assert sface.normal[0] == pytest.approx(dface.normal[0], abs=0.001)  # precision error in re6
            assert sface.normal[1] == pytest.approx(dface.normal[1], abs=0.001)
            assert sface.normal[2] == pytest.approx(dface.normal[2], abs=0.001)
            # assert sface.adjacent[0] == dface.adjacent[0]
            # assert sface.adjacent[1] == dface.adjacent[1]
            # assert sface.adjacent[2] == dface.adjacent[2]


def test_export_vertices(sbc_imported_local, sbc_exported_local):
    sverts = sbc_imported_local.vertices
    dverts = sbc_exported_local.vertices
    assert len(sverts) == len(dverts)
    for svert, dvert in zip(sverts, dverts):
        assert svert.x == pytest.approx(dvert.x, rel=0.001)
        assert svert.y == pytest.approx(dvert.y, rel=0.001)
        assert svert.z == pytest.approx(dvert.z, rel=0.001)
        assert svert.w == pytest.approx(dvert.w, rel=0.001)
        assert svert.w == 0
