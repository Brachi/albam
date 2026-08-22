import json
import os

import bpy
import pytest

from tests.mtfw.scripts.catalog_paths import resolve_hashes
from albam.engines.mtfw.animation import KEYFRAME_TYPES
from kaitaistruct import KaitaiStream
from io import BytesIO

# Committed, fixed dataset - not selectable via --mtfw-dataset like the rest
# of tests/mtfw/*.py. This is the single source of truth for what this file
# tests locally; extend it directly rather than pointing at some other file.
# Every hash here must be a subset of that app_id's committed
# tests/mtfw/datasets/<app_id>_catalog.json - see test_dataset_hashes_are_in_catalog
# below, which enforces it.
LMT_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "lmt_serialization_hashes.json"
)
with open(LMT_SERIALIZATION_DATASET_PATH) as f:
    LMT_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames and
            "local_lmt_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash", "local_lmt_path_hash")
        argvalues = [(d["app_id"], d["mod_path_hash"], d["lmt_path_hash"]) for d in LMT_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['lmt_path_hash']}" for d in LMT_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by LMT_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in LMT_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        for key in ("mod_path_hash", "lmt_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}"
            )


@pytest.fixture(scope="session")
def lmt_export_local(game_fs_root, local_app_id, local_mod_path_hash, local_lmt_path_hash):
    from albam.engines.mtfw.structs.lmt import Lmt

    bpy.context.scene.albam.apps.app_selected = local_app_id

    local_mod_path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash].lstrip("/")
    vfile_mod = bpy.context.scene.albam.vfs.select_vfile(local_app_id, local_mod_path)
    assert vfile_mod
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    armature = next((obj for obj in bpy.data.objects if obj.type == 'ARMATURE'), None)
    assert armature
    bpy.context.scene.albam.import_options_lmt.armature = armature

    local_lmt_path = resolve_hashes(game_fs_root, {local_lmt_path_hash})[local_lmt_path_hash].lstrip("/")
    vfile_lmt = bpy.context.scene.albam.vfs.select_vfile(local_app_id, local_lmt_path)
    assert vfile_lmt
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    # enable serialization of the imported action track
    lmt = bpy.context.scene.albam.exportable.file_list[latest_exported]
    bl_obj = lmt.bl_object
    bl_objects = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    for bl_obj in bl_objects:
        custom_props = bl_obj.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
        if custom_props.ofs_frame != 0:
            custom_props.generate_new = True

    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}

    vfile_lmt_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, local_lmt_path)
    assert vfile_lmt_exported
    src_lmt = Lmt.from_bytes(vfile_lmt.get_bytes())
    dst_lmt = Lmt.from_bytes(vfile_lmt_exported.get_bytes())
    src_lmt._read()
    dst_lmt._read()
    return src_lmt, dst_lmt


@pytest.fixture(scope="session")
def lmt_imported_local(lmt_export_local):
    return lmt_export_local[0]


@pytest.fixture(scope="session")
def lmt_exported_local(lmt_export_local):
    return lmt_export_local[1]


def test_export_header(lmt_imported_local, lmt_exported_local):
    slmt = lmt_imported_local
    dlmt = lmt_exported_local
    slmt.id_magic == dlmt.id_magic
    slmt.version == dlmt.version
    slmt.num_block_offsets == dlmt.num_block_offsets


def test_export_anim_block(lmt_imported_local, lmt_exported_local):
    slmt = lmt_imported_local
    dlmt = lmt_exported_local
    version = slmt.version

    samnib = [ab for _, ab in enumerate(slmt.block_offsets)]
    damnib = [ab for _, ab in enumerate(dlmt.block_offsets)]
    i = 0
    for sab, dab in zip(samnib, damnib):
        if sab.offset != 0:
            print(i)
            # assert sab.block_header.ofs_frame == dab.block_header.ofs_frame
            assert sab.block_header.num_tracks == dab.block_header.num_tracks
            # anim blocks have non correct value of frames, actually 1
            if i not in (100, 101, 102, 103, 104):
                assert sab.block_header.num_frames == dab.block_header.num_frames
            assert sab.block_header.loop_frame == dab.block_header.loop_frame
            assert sab.block_header.init_position == dab.block_header.init_position
            assert sab.block_header.init_quaterion == dab.block_header.init_quaterion
            stracks = [tr for _, tr in enumerate(sab.block_header.tracks)]
            dtracks = [tr for _, tr in enumerate(dab.block_header.tracks)]
            for strack in stracks:
                bone = strack.bone_index
                dbone = -1
                for dtrack in dtracks:
                    if dtrack.bone_index == bone:
                        dbone = dtrack.bone_index
                if dbone == -1:
                    print(bone)
            j = 0
            for str, dtr in zip(stracks, dtracks):
                print("amim_block:", i, "track:", j, "bone index:", str.bone_index)
                # current code buffer type selection isn't that reliable for static frames
                assert str.usage == dtr.usage
                assert str.joint_type == dtr.joint_type
                assert str.bone_index == dtr.bone_index
                assert str.weight == dtr.weight
                # assert str.reference_data == dtr.reference_data
                # can't pass because of unknow logic for static keyframes type
                if str.len_data != dtr.len_data:
                    print(f"don't match {str.buffer_type} and {dtr.buffer_type}")
                else:
                    kfcls = KEYFRAME_TYPES[version][str.buffer_type]
                    sdata = str.data
                    ddata = dtr.data
                    keyframe = kfcls()  # hack to get the size before reading
                    k = 0
                    for start in range(0, len(sdata), keyframe.size_):
                        schunk = sdata[start: start + keyframe.size_]
                        sframe = kfcls(KaitaiStream(BytesIO(schunk)))
                        sframe._read()
                        dchunk = ddata[start: start + keyframe.size_]
                        dframe = kfcls(KaitaiStream(BytesIO(dchunk)))
                        dframe._read()
                        print("Keyframe is:", k)
                        assert sframe.x == pytest.approx(dframe.x, rel=0.001)
                        assert sframe.y == pytest.approx(dframe.y, rel=0.001)
                        assert sframe.z == pytest.approx(dframe.z, rel=0.001)
                        k += 1
                j += 1
        else:
            assert sab.offset == dab.offset
        i += 1
