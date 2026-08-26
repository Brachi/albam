import contextlib

import bpy
import pytest

from tests.mtfw.conftest import action_fcurves
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


@contextlib.contextmanager
def _block_action_swapped(custom_props, action):
    """Export `action` for this block, then put the block back as it was.

    Blender's scene is process-global and outlives a test, so a block left
    pointing at one of the deliberately malformed actions below would follow
    into every later test that exports the same .lmt.
    """
    original_action = custom_props.action
    original_generate_new = custom_props.generate_new
    custom_props.action = action
    custom_props.generate_new = True
    try:
        yield
    finally:
        custom_props.action = original_action
        custom_props.generate_new = original_generate_new


@pytest.fixture(scope="module")
def imported_lmt_blocks(game_fs_root, local_app_id, local_mod_path_hash, local_lmt_path_hash):
    """Import the .mod and its .lmt once, and hand back the per-block empties
    export reads its actions from (the same setup the test above opens with).

    Module-scoped deliberately: every import adds another armature and
    another set of blocks to the process-global scene, and enough of those
    accumulating changes what a later whole-file export round trip produces.
    """
    app_id, mod_path_hash, lmt_path_hash = local_app_id, local_mod_path_hash, local_lmt_path_hash
    bpy.context.scene.albam.apps.app_selected = app_id

    mod_path = resolve_hashes(game_fs_root, {mod_path_hash})[mod_path_hash].lstrip("/")
    assert bpy.context.scene.albam.vfs.select_vfile(app_id, mod_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == 'ARMATURE'
    bpy.context.scene.albam.import_options_lmt.armature = armature

    lmt_path = resolve_hashes(game_fs_root, {lmt_path_hash})[lmt_path_hash].lstrip("/")
    assert bpy.context.scene.albam.vfs.select_vfile(app_id, lmt_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}

    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    bl_obj = bpy.context.scene.albam.exportable.file_list[latest_exported].bl_object
    return armature, lmt_path, [c for c in bl_obj.children_recursive if c.type == "EMPTY"]


def _first_block_with_location_action(bl_objects, app_id):
    """Reads fcurves through action_fcurves() rather than walking layers
    directly: this runs before the tests below decide whether slots apply at
    all, so it has to work on Blender versions that have no layers.
    """
    for candidate in bl_objects:
        custom_props = candidate.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.ofs_frame == 0 or not custom_props.action:
            continue
        action = custom_props.action
        for fcurve in action_fcurves(action):
            path = fcurve.data_path
            if path.startswith('pose.bones["') and "location" in path:
                return candidate, action, fcurve
    return None, None, None


def test_export_reads_the_armatures_channelbag_not_the_first(
    imported_lmt_blocks, local_app_id
):
    """An action can hold one channelbag per slot, in creation order, and the
    armature's is not necessarily the first.

    Export reaches its fcurves through a fixed layers[0].strips[0].channelbags[0],
    so for such an action it reads some other ID's channels - or, as here, an
    empty decoy - and silently writes an animation with none of the armature's
    keyframes in it. Silent, because nothing raises: the exported .lmt is
    well-formed and simply missing the animation.
    """
    from albam.engines.mtfw.structs.lmt import Lmt

    armature, lmt_path, bl_objects = imported_lmt_blocks
    target_block, action, fcurve = _first_block_with_location_action(bl_objects, local_app_id)
    if action is None:
        pytest.skip("No block with a location fcurve to rebuild")
    if hasattr(action, "fcurves"):
        pytest.skip("Blender exposes flat Action.fcurves here - slots don't apply")

    axis_index = fcurve.array_index
    expected_values = [kp.co[1] for kp in fcurve.keyframe_points]
    assert expected_values, "Location fcurve had no keyframes"

    # Same channels, but with an unrelated slot claiming index 0 - what you
    # get whenever the action was keyed on something else before the armature.
    rebuilt = bpy.data.actions.new(f"{action.name}.rebuilt")
    rebuilt.use_fake_user = True
    rebuilt.slots.new(id_type='OBJECT', name="Decoy")
    armature_slot = rebuilt.slots.new(id_type='OBJECT', name=armature.name)
    strip = rebuilt.layers.new("Layer").strips.new(type='KEYFRAME')
    strip.channelbag(rebuilt.slots[0], ensure=True)
    armature_channelbag = strip.channelbag(armature_slot, ensure=True)
    for src in action_fcurves(action):
        dst = armature_channelbag.fcurves.new(data_path=src.data_path, index=src.array_index)
        for kp in src.keyframe_points:
            dst.keyframe_points.add(1)
            dst.keyframe_points[-1].co = (kp.co[0], kp.co[1])
            dst.keyframe_points[-1].interpolation = 'LINEAR'
    assert strip.channelbags[0] != armature_channelbag, "decoy did not take index 0"

    custom_props = target_block.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
    with _block_action_swapped(custom_props, rebuilt):
        assert bpy.ops.albam.export() == {"FINISHED"}

    vfile_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, lmt_path)
    assert vfile_exported
    dst_lmt = Lmt.from_bytes(vfile_exported.get_bytes())
    dst_lmt._read()

    dst_block = dst_lmt.block_offsets[bl_objects.index(target_block)]
    assert dst_block.offset != 0
    matching = [t for t in dst_block.block_header.tracks if t.usage in {1, 4}]
    assert matching, "No location-usage track in the exported block"

    from albam.engines.mtfw.animation import LMTKeyFrames

    found = False
    for track in matching:
        kf = LMTKeyFrames()
        kf.version = dst_lmt.version
        kf.track_type = "location"
        kf.decode_framedata(dst_lmt.version, track.buffer_type, track.data)
        decoded = [f[axis_index] for f in kf.decoded_frames if f is not None]
        if any(any(abs(v - e) < 0.01 for v in decoded) for e in expected_values):
            found = True
            break

    assert found, (
        "None of the armature's location keyframes reached the exported .lmt - "
        "export read the channelbag at index 0 instead of the armature's"
    )


def test_export_action_without_layers_does_not_crash(imported_lmt_blocks, local_app_id):
    """A brand-new action has no layers at all, so the fixed
    layers[0].strips[0].channelbags[0] lookup raises IndexError instead of
    exporting an empty block.
    """
    armature, _lmt_path, bl_objects = imported_lmt_blocks
    target_block, action, _fcurve = _first_block_with_location_action(bl_objects, local_app_id)
    if action is None:
        pytest.skip("No block with an action to replace")
    if hasattr(action, "fcurves"):
        pytest.skip("Blender exposes flat Action.fcurves here - layers don't apply")

    empty_action = bpy.data.actions.new(f"{action.name}.empty")
    empty_action.use_fake_user = True
    assert len(empty_action.layers) == 0

    custom_props = target_block.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
    with _block_action_swapped(custom_props, empty_action):
        assert bpy.ops.albam.export() == {"FINISHED"}
