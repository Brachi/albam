import json
import math
import os

import bpy
import pytest

from tests.mtfw.scripts.catalog_paths import resolve_hashes
from albam.engines.mtfw.animation import USAGE, LMTKeyFrames, LMTKeyframeBounds

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
    from albam.lib.kaitai_utils import parse

    bpy.context.scene.albam.apps.app_selected = local_app_id

    local_mod_path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash].lstrip("/")
    vfile_mod = bpy.context.scene.albam.vfs.select_vfile(local_app_id, local_mod_path)
    assert vfile_mod
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    # Session-scoped: bpy.data.objects accumulates armatures from every
    # dataset entry run so far, so grabbing "the first armature" would pick
    # up a leftover from an earlier (app_id, mod) pair instead of the one
    # just imported. build_blender_model() returns the armature itself
    # (mesh.py's `bl_object = skeleton or ...`) and is exposed as the latest
    # exportable entry's bl_object, same as the lmt lookup just below.
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == 'ARMATURE'
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
    src_lmt = parse(Lmt, vfile_lmt.get_bytes(), local_app_id)
    dst_lmt = parse(Lmt, vfile_lmt_exported.get_bytes(), local_app_id)
    return src_lmt, dst_lmt


@pytest.fixture(scope="session")
def lmt_imported_local(lmt_export_local):
    return lmt_export_local[0]


@pytest.fixture(scope="session")
def lmt_exported_local(lmt_export_local):
    return lmt_export_local[1]


def test_export_header(lmt_imported_local, lmt_exported_local):
    """The file header survives a round trip.

    These were three bare comparisons whose results went nowhere, so the
    test passed whatever the exporter wrote.
    """
    slmt = lmt_imported_local
    dlmt = lmt_exported_local
    assert slmt.id_magic == dlmt.id_magic
    assert slmt.version == dlmt.version
    assert slmt.num_block_offsets == dlmt.num_block_offsets


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
            # A block whose tracks never change carries one keyframe however
            # long it runs, and its length used to be read off that, writing a
            # static hold out as a single frame. See _block_length().
            assert sab.block_header.num_frames == dab.block_header.num_frames
            assert sab.block_header.loop_frame == dab.block_header.loop_frame
            assert sab.block_header.init_position == dab.block_header.init_position
            assert sab.block_header.init_quaterion == dab.block_header.init_quaterion
            # The event tables - footstep sounds, collision triggers. Compared
            # by content: ofs_events is a file offset and moves whenever the
            # layout does, so it says nothing about whether the events survived.
            for table in ("collision_events", "motion_sound_effects"):
                sev = getattr(sab.block_header, table)
                dev = getattr(dab.block_header, table)
                assert (sev is None) == (dev is None), table + " appeared or vanished"
                if sev is None:
                    continue
                assert list(sev.event_id) == list(dev.event_id), table + " ids changed"
                assert sev.num_events == dev.num_events, table + " count changed"
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
                # Re-encoding a track shifts its fallback value in the last
                # decimals, so this is a tolerance rather than equality.
                assert list(str.reference_data) == pytest.approx(
                    list(dtr.reference_data), abs=1e-3)
                # A re-encoded track has a different length by definition -
                # the exporter picks the buffer type that fits the keyframes it
                # has, not the one the original used. Skipping the comparison
                # when the length differs skipped exactly the tracks whose
                # values had most room to drift, so the values are compared
                # whenever both sides carry data at all.
                if str.len_data and dtr.len_data:
                    # Compare fully decoded values (through the same
                    # dequantaize/to_quat/to_vec3 pipeline import uses), not
                    # raw struct fields - several buffer types (XwQuat/
                    # YwQuat/ZwQuat, the Quatized* family) store a quantized
                    # int subset of components (e.g. YwQuat has only y/w, no
                    # x/z at all) that only becomes a real x/y/z/w value
                    # after decoding.
                    skeyframes = LMTKeyFrames()
                    skeyframes.track_type = USAGE[str.usage]
                    if version > 51 and str.bounds:
                        skeyframes.bounds = LMTKeyframeBounds(str.bounds)
                    skeyframes.decode_framedata(version, str.buffer_type, str.data)

                    dkeyframes = LMTKeyFrames()
                    dkeyframes.track_type = USAGE[dtr.usage]
                    if version > 51 and dtr.bounds:
                        dkeyframes.bounds = LMTKeyframeBounds(dtr.bounds)
                    dkeyframes.decode_framedata(version, dtr.buffer_type, dtr.data)

                    skept = [f for f in skeyframes.decoded_frames if f is not None]
                    dkept = [f for f in dkeyframes.decoded_frames if f is not None]
                    assert len(skept) == len(dkept), (
                        "keyframe count changed: %d -> %d" % (len(skept), len(dkept)))
                    for k, (sframe, dframe) in enumerate(
                            zip(skeyframes.decoded_frames, dkeyframes.decoded_frames)):
                        print("Keyframe is:", k)
                        if sframe is None or dframe is None:
                            continue  # duration padding, not a real keyframe
                        if hasattr(sframe, "w"):
                            # Compare the rotation, not the components. A
                            # buffer type that stores only x/y/z rebuilds w as
                            # a positive square root, so a quaternion with a
                            # negative w comes back negated - and q and -q are
                            # the same rotation, which componentwise equality
                            # would call a failure.
                            drift = math.degrees(sframe.normalized().rotation_difference(
                                dframe.normalized()).angle)
                            # rotation_difference reports the negated case as a
                            # full turn rather than none, and a full turn is the
                            # identity
                            drift = min(drift, abs(360.0 - drift))
                            assert drift < 0.5, (
                                "rotation drifted %.4f deg" % drift)
                        else:
                            assert sframe.x == pytest.approx(dframe.x, rel=0.001)
                            assert sframe.y == pytest.approx(dframe.y, rel=0.001)
                            assert sframe.z == pytest.approx(dframe.z, rel=0.001)
                j += 1
        else:
            assert sab.offset == dab.offset
        i += 1
