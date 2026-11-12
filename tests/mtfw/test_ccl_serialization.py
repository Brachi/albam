"""Round-trip a catalogued RE5 CCL file through Blender's import/export path."""

import json
import math
import os

import bpy
import pytest

from albam.engines.mtfw.bone import set_anim_retarget
from albam.engines.mtfw.structs.ccl_156 import Ccl156
from tests.mtfw.conftest import import_export
from tests.mtfw.scripts.catalog_paths import hash_virtual_path


APP_ID = "re5"
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "datasets", "re5_catalog.json")


def pytest_generate_tests(metafunc):
    if "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", [APP_ID], ids=[APP_ID], scope="session")


def _catalogued_ccl_paths(game_fs_root):
    with open(CATALOG_PATH) as f:
        catalog_hashes = {item["path_hash"] for item in json.load(f)}
    return sorted(
        path for path in game_fs_root.walk.files()
        if path.lower().endswith(".ccl") and hash_virtual_path(path) in catalog_hashes
    )


def _make_armature(anim_ids):
    armature_data = bpy.data.armatures.new("ccl_serialization_armature_data")
    armature = bpy.data.objects.new("ccl_serialization_armature", armature_data)
    bpy.context.collection.objects.link(armature)

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    previous_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    for index, anim_id in enumerate(anim_ids):
        bone = armature_data.edit_bones.new(f"joint_{anim_id}")
        bone.head = (index * 0.02, 0.0, 0.0)
        bone.tail = (index * 0.02, 0.0, 0.1)
    bpy.ops.object.mode_set(mode="OBJECT")

    for anim_id in anim_ids:
        set_anim_retarget(armature.pose.bones[f"joint_{anim_id}"], APP_ID, str(anim_id))
    bpy.context.view_layer.objects.active = previous_active
    return armature


@pytest.fixture(scope="session")
def ccl_export_local(game_fs_root, local_app_id):
    bpy.context.scene.albam.apps.app_selected = local_app_id
    vfs = bpy.context.scene.albam.vfs

    selected = None
    for ccl_path in _catalogued_ccl_paths(game_fs_root):
        vfile = vfs.select_vfile(local_app_id, ccl_path.lstrip("/"))
        source_ccl = Ccl156.from_bytes(vfile.get_bytes())
        source_ccl._read()
        if not source_ccl.col_infos:
            continue
        if any(
                int(record.shape) not in (0, 1, 2, 3)
                or not math.isfinite(record.radius)
                or record.radius < 0.0
                for record in source_ccl.col_infos):
            continue
        selected = ccl_path, source_ccl
        break
    if selected is None:
        pytest.skip("No catalogued .ccl file with exportable records is present in this RE5 install")
    ccl_path, source_ccl = selected
    ccl_path = ccl_path.lstrip("/")

    anim_ids = sorted({record.ref_joint_no for record in source_ccl.col_infos})
    armature = _make_armature(anim_ids)
    bpy.context.scene.albam.import_options_chain.armature = armature

    import_export(local_app_id, ccl_path)
    exported_vfile = bpy.context.scene.albam.exported.select_vfile(local_app_id, ccl_path)
    assert exported_vfile

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
