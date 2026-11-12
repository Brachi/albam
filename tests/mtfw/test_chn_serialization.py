"""Round-trip paired RE5 MOD and CHN files through Blender's import/export path."""

import json
import os

import bpy
import pytest

from albam.engines.mtfw.structs.chn import Chn
from tests.mtfw.conftest import import_export, import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes


SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "chn_serialization_hashes.json")

with open(SERIALIZATION_DATASET_PATH) as f:
    SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    argnames = ("local_app_id", "local_mod_path_hash", "local_chn_path_hash")
    if all(name in metafunc.fixturenames for name in argnames):
        argvalues = [
            (entry["app_id"], entry["mod_path_hash"], entry["chn_path_hash"])
            for entry in SERIALIZATION_DATASET
        ]
        ids = [f"{entry['app_id']}-{entry['chn_path_hash']}" for entry in SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """Every paired MOD and CHN hash must belong to its app's committed catalog."""
    for entry in SERIALIZATION_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {item["path_hash"] for item in json.load(f)}
        for key in ("mod_path_hash", "chn_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}"
            )


@pytest.fixture(scope="session")
def chn_export_local(game_fs_root, local_app_id, local_mod_path_hash, local_chn_path_hash):
    bpy.context.scene.albam.apps.app_selected = local_app_id

    paths = resolve_hashes(game_fs_root, {local_mod_path_hash, local_chn_path_hash})
    mod_path = paths[local_mod_path_hash].lstrip("/")
    chn_path = paths[local_chn_path_hash].lstrip("/")

    import_vfile(local_app_id, mod_path)
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == "ARMATURE"
    bpy.context.scene.albam.import_options_chain.armature = armature

    vfile_chn = import_export(local_app_id, chn_path)
    exported_vfile = bpy.context.scene.albam.exported.select_vfile(local_app_id, chn_path)
    assert exported_vfile

    source_chn = Chn.from_bytes(vfile_chn.get_bytes())
    source_chn._read()
    assert source_chn.chain_infos
    for chain_info in source_chn.chain_infos:
        chain_ids = [joint.ref_joint_no for joint in chain_info.joints]
        assert chain_info.chain_type in (1, 2)
        assert all(
            joint.col_shape in (1, 2) and joint.node_num <= 8
            for joint in chain_info.joints
        )
        assert len(chain_ids) == len(set(chain_ids))
        if len(chain_ids) > 1:
            assert all(0 <= anim_id <= 0xFF for anim_id in chain_ids)
    assert any(len(chain_info.joints) >
               1 for chain_info in source_chn.chain_infos)

    exported_chn = Chn.from_bytes(exported_vfile.get_bytes())
    exported_chn._read()
    return source_chn, exported_chn


@pytest.fixture(scope="session")
def chn_imported_local(chn_export_local):
    return chn_export_local[0]


@pytest.fixture(scope="session")
def chn_exported_local(chn_export_local):
    return chn_export_local[1]


def test_export_header(chn_imported_local, chn_exported_local):
    source_chn = chn_imported_local
    exported_chn = chn_exported_local

    assert source_chn.magic == exported_chn.magic
    assert source_chn.version == exported_chn.version
    assert source_chn.num_chain_infos == exported_chn.num_chain_infos
    assert source_chn.reserve == exported_chn.reserve
    assert source_chn.data_size == exported_chn.data_size
    assert len(source_chn.chain_infos) == len(exported_chn.chain_infos)

    for source_chain, exported_chain in zip(source_chn.chain_infos, exported_chn.chain_infos):
        assert source_chain.num_joints == exported_chain.num_joints
        assert source_chain.chain_type == exported_chain.chain_type
        assert source_chain.grav_scaler == pytest.approx(exported_chain.grav_scaler)
        assert source_chain.time_scaler == pytest.approx(exported_chain.time_scaler)
        assert source_chain.dump_scaler == pytest.approx(exported_chain.dump_scaler)


def test_export_joint_info(chn_imported_local, chn_exported_local):
    source_chn = chn_imported_local
    exported_chn = chn_exported_local

    for source_chain, exported_chain in zip(source_chn.chain_infos, exported_chn.chain_infos):
        source_joints = source_chain.joints
        exported_joints = exported_chain.joints
        assert len(source_joints) == len(exported_joints)

        for index, (source_joint, exported_joint) in enumerate(zip(source_joints, exported_joints)):
            for field in ("x", "y", "z"):
                assert getattr(source_joint.min_angle, field) == pytest.approx(
                    getattr(exported_joint.min_angle, field))
                assert getattr(source_joint.max_angle, field) == pytest.approx(
                    getattr(exported_joint.max_angle, field))
            for field in (
                    "attr", "spring_coef", "dumping_coef", "mass", "restrict_flag",
                    "col_shape", "col_radius", "air_regist", "friction", "soft_coef",
                    "bend_regist"):
                assert getattr(source_joint, field) == pytest.approx(
                    getattr(exported_joint, field))

            expected_neighbors = []
            if index > 0:
                expected_neighbors.append(source_joints[index - 1].ref_joint_no)
            if index + 1 < len(source_joints):
                expected_neighbors.append(source_joints[index + 1].ref_joint_no)

            assert exported_joint.ref_joint_no == source_joint.ref_joint_no
            assert exported_joint.node_num == len(expected_neighbors)
            assert exported_joint.node_joint_no[:exported_joint.node_num] == expected_neighbors
            assert exported_joint.node_joint_no[exported_joint.node_num:] == (
                [0] * (8 - exported_joint.node_num))
