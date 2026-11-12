"""Round-trip a catalogued RE5 CCL file through Blender's import/export path."""

import json
import os

import bpy
import pytest

from albam.engines.mtfw.structs.ccl_156 import Ccl156
from tests.mtfw.conftest import import_export, import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes


SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "ccl_serialization_hashes.json")

with open(SERIALIZATION_DATASET_PATH) as f:
    SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    argnames = ("local_app_id", "local_mod_path_hash", "local_ccl_path_hash")
    if all(name in metafunc.fixturenames for name in argnames):
        argvalues = [
            (entry["app_id"], entry["mod_path_hash"], entry["ccl_path_hash"])
            for entry in SERIALIZATION_DATASET
        ]
        ids = [f"{entry['app_id']}-{entry['ccl_path_hash']}" for entry in SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """Every paired MOD and CCL hash must belong to its app's committed catalog."""
    for entry in SERIALIZATION_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {item["path_hash"] for item in json.load(f)}
        for key in ("mod_path_hash", "ccl_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}"
            )


@pytest.fixture(scope="session")
def ccl_export_local(game_fs_root, local_app_id, local_mod_path_hash, local_ccl_path_hash):
    bpy.context.scene.albam.apps.app_selected = local_app_id

    paths = resolve_hashes(game_fs_root, {local_mod_path_hash, local_ccl_path_hash})
    mod_path = paths[local_mod_path_hash].lstrip("/")
    ccl_path = paths[local_ccl_path_hash].lstrip("/")

    import_vfile(local_app_id, mod_path)
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == "ARMATURE"
    bpy.context.scene.albam.import_options_chain.armature = armature

    vfile_ccl = import_export(local_app_id, ccl_path)
    exported_vfile = bpy.context.scene.albam.exported.select_vfile(local_app_id, ccl_path)
    assert exported_vfile

    source_ccl = Ccl156.from_bytes(vfile_ccl.get_bytes())
    source_ccl._read()
    exported_ccl = Ccl156.from_bytes(exported_vfile.get_bytes())
    exported_ccl._read()
    return source_ccl, exported_ccl


@pytest.fixture(scope="session")
def ccl_imported_local(ccl_export_local):
    return ccl_export_local[0]


@pytest.fixture(scope="session")
def ccl_exported_local(ccl_export_local):
    return ccl_export_local[1]


def test_export_header(ccl_imported_local, ccl_exported_local):
    source_ccl = ccl_imported_local
    exported_ccl = ccl_exported_local

    assert source_ccl.magic == exported_ccl.magic
    assert source_ccl.version == exported_ccl.version
    assert source_ccl.num_col_infos == exported_ccl.num_col_infos
    assert source_ccl.data_size == exported_ccl.data_size
    assert len(source_ccl.col_infos) == len(exported_ccl.col_infos)


def test_export_col_infos(ccl_imported_local, ccl_exported_local):
    source_records = ccl_imported_local.col_infos
    exported_records = ccl_exported_local.col_infos
    assert len(source_records) == len(exported_records)

    for source_record, exported_record in zip(source_records, exported_records):
        for field in ("attr", "ref_joint_no", "pair_joint_no", "shape", "id"):
            assert getattr(source_record, field) == getattr(exported_record, field)
        for field in ("position", "extent", "angle"):
            for axis in ("x", "y", "z"):
                assert getattr(getattr(source_record, field), axis) == pytest.approx(
                    getattr(getattr(exported_record, field), axis))
        assert source_record.radius == pytest.approx(exported_record.radius)
