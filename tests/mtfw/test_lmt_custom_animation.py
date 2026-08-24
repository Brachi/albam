import bpy

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Same pairs as lmt_serialization_hashes.json's re1/re5 pl00 entries - one
# per LMT version (re1=v67, re5=v51), since encode_framedata's static/normal
# paths differ by version and both need this probed independently.
DATASET = [
    {"app_id": "re1", "mod_path_hash": "d7e6d66be56bf3d3", "lmt_path_hash": "c0b58c74de2134de"},
    {"app_id": "re5", "mod_path_hash": "5d45d4682b062d49", "lmt_path_hash": "1cc34f3b754528ea"},
]


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames and
            "local_lmt_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash", "local_lmt_path_hash")
        argvalues = [(d["app_id"], d["mod_path_hash"], d["lmt_path_hash"]) for d in DATASET]
        ids = [d["app_id"] for d in DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_edited_keyframe_survives_export(
    game_fs_root, local_app_id, local_mod_path_hash, local_lmt_path_hash
):
    from albam.engines.mtfw.structs.lmt import Lmt

    bpy.context.scene.albam.apps.app_selected = local_app_id

    mod_path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash].lstrip("/")
    vfile_mod = bpy.context.scene.albam.vfs.select_vfile(local_app_id, mod_path)
    assert vfile_mod
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == 'ARMATURE'
    bpy.context.scene.albam.import_options_lmt.armature = armature

    lmt_path = resolve_hashes(game_fs_root, {local_lmt_path_hash})[local_lmt_path_hash].lstrip("/")
    vfile_lmt = bpy.context.scene.albam.vfs.select_vfile(local_app_id, lmt_path)
    assert vfile_lmt
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}

    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    lmt_asset = bpy.context.scene.albam.exportable.file_list[latest_exported]
    bl_obj = lmt_asset.bl_object
    bl_objects = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]

    # Pick the first block that actually has an action with a location fcurve
    # on some bone - that's the simplest, least ambiguous channel to hand-edit
    # and verify (encode_framedata's *100 scale factor is easy to invert).
    target_block = None
    target_fcurve = None
    for candidate in bl_objects:
        custom_props = candidate.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
        if custom_props.ofs_frame == 0 or not custom_props.action:
            continue
        action = custom_props.action
        if int(bpy.app.version_string[0]) >= 5:
            fcurves = action.layers[0].strips[0].channelbags[0].fcurves
        else:
            fcurves = action.fcurves
        for fcurve in fcurves:
            if fcurve.data_path.startswith('pose.bones["') and "location" in fcurve.data_path:
                target_block = candidate
                target_fcurve = fcurve
                break
        if target_block:
            break

    assert target_block is not None, "No block with a location fcurve found - can't probe an edit"

    custom_props = target_block.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
    bone_name = target_fcurve.data_path.split('"')[1]
    axis_index = target_fcurve.array_index

    # Hand-edit: bump every keyframe on this channel by a fixed, recognizable
    # delta (in Blender units; encode_framedata multiplies location by 100
    # before quantizing to the on-disk fixed-point format).
    DELTA = 0.05
    edited_values = []
    for kp in target_fcurve.keyframe_points:
        kp.co[1] += DELTA
        edited_values.append(kp.co[1])
    assert edited_values, "Location fcurve had no keyframes to edit"

    custom_props.generate_new = True

    assert bpy.ops.albam.export() == {"FINISHED"}

    vfile_lmt_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, lmt_path)
    assert vfile_lmt_exported
    dst_lmt = Lmt.from_bytes(vfile_lmt_exported.get_bytes())
    dst_lmt._read()

    block_index = bl_objects.index(target_block)
    dst_block = dst_lmt.block_offsets[block_index]
    assert dst_block.offset != 0

    # Locate the location track(s) by usage (1=local, 4=absolute)
    # among this block's tracks, matching how load_lmt() classified it.
    location_usages = {1, 4}
    matching = [t for t in dst_block.block_header.tracks if t.usage in location_usages]
    assert matching, "No location-usage track found in the exported block"

    # Decode every location track's frames and confirm at least one decoded
    # value matches an edited keyframe (within quantization tolerance) -
    # proving the edit propagated through _generate_track_from_action into
    # the actual exported bytes, not just that export "succeeded".
    from albam.engines.mtfw.animation import LMTKeyFrames

    found_match = False
    for track in matching:
        kf = LMTKeyFrames()
        kf.version = dst_lmt.version
        kf.track_type = "location"
        kf.decode_framedata(dst_lmt.version, track.buffer_type, track.data)
        decoded_axis_values = [f[axis_index] for f in kf.decoded_frames if f is not None]
        for expected in edited_values:
            if any(abs(v - expected) < 0.01 for v in decoded_axis_values):
                found_match = True
                break
        if found_match:
            break

    assert found_match, (
        f"None of the edited keyframe values {edited_values} (bone {bone_name!r}, "
        f"axis {axis_index}) were found in the exported LMT's decoded location tracks - "
        f"the hand-edit did not survive export"
    )
