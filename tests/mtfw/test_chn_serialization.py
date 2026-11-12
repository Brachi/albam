"""Round-trip a catalogued RE5 CHN file through Blender's import/export path."""

import json
import os

import bpy
import pytest

from albam.engines.mtfw.bone import set_anim_retarget
from albam.engines.mtfw.structs.chn import Chn
from tests.mtfw.conftest import import_export
from tests.mtfw.scripts.catalog_paths import hash_virtual_path


APP_ID = "re5"
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "datasets", "re5_catalog.json")


def pytest_generate_tests(metafunc):
    if "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", [APP_ID], ids=[APP_ID], scope="session")


def _catalogued_chn_paths(game_fs_root):
    with open(CATALOG_PATH) as f:
        catalog_hashes = {item["path_hash"] for item in json.load(f)}
    return sorted(
        path for path in game_fs_root.walk.files()
        if path.lower().endswith(".chn") and hash_virtual_path(path) in catalog_hashes
    )


def _make_armature(anim_ids):
    armature_data = bpy.data.armatures.new("chn_serialization_armature_data")
    armature = bpy.data.objects.new("chn_serialization_armature", armature_data)
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
def chn_export_local(game_fs_root, local_app_id):
    bpy.context.scene.albam.apps.app_selected = local_app_id
    vfs = bpy.context.scene.albam.vfs

    selected = None
    for chn_path in _catalogued_chn_paths(game_fs_root):
        vfile = vfs.select_vfile(local_app_id, chn_path.lstrip("/"))
        source_chn = Chn.from_bytes(vfile.get_bytes())
        source_chn._read()
        valid_chains = True
        for chain_info in source_chn.chain_infos:
            chain_ids = [joint.ref_joint_no for joint in chain_info.joints]
            if (chain_info.chain_type not in (1, 2)
                    or any(joint.col_shape not in (1, 2) or joint.node_num > 8
                           for joint in chain_info.joints)
                    or len(chain_ids) != len(set(chain_ids))
                    or (len(chain_ids) > 1
                        and any(not 0 <= anim_id <= 0xFF for anim_id in chain_ids))):
                valid_chains = False
                break
        has_linked_joints = any(
            len(chain_info.joints) > 1 for chain_info in source_chn.chain_infos)
        if valid_chains and has_linked_joints:
            selected = chn_path, source_chn
            break
    if selected is None:
        pytest.skip("No catalogued .chn file is present in this RE5 install")
    chn_path, source_chn = selected
    chn_path = chn_path.lstrip("/")

    anim_ids = sorted({
        joint.ref_joint_no
        for chain_info in source_chn.chain_infos
        for joint in chain_info.joints
    })
    armature = _make_armature(anim_ids)
    bpy.context.scene.albam.import_options_chain.armature = armature

    import_export(local_app_id, chn_path)
    exported_vfile = bpy.context.scene.albam.exported.select_vfile(local_app_id, chn_path)
    assert exported_vfile

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
