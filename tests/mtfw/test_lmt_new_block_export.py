import bpy

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# The same pl00 pair other lmt tests use.
DATASET = [
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


def _first_used_block_with_action(bl_objects, app_id):
    for candidate in bl_objects:
        custom_props = candidate.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if custom_props.action:
            return candidate, custom_props.action
    return None, None


def test_a_block_created_rather_than_imported_exports(
    game_fs_root, local_app_id, local_mod_path_hash, local_lmt_path_hash
):
    """A block a user builds by hand - not one an import produced - never had
    anything stamp a real offset onto it.

    Under the old "is this slot used" test (`ofs_frame != 0`), that made it
    indistinguishable from a slot that really is empty: export wrote the
    block out as an empty slot no matter what action it held, silently, with
    no warning. See issue #272.
    """
    from albam.engines.mtfw.animation.animation_import import get_block_index, set_block_index
    from albam.engines.mtfw.structs.lmt import Lmt
    from albam.lib.kaitai_utils import parse

    bpy.context.scene.albam.apps.app_selected = local_app_id

    mod_path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash].lstrip("/")
    assert bpy.context.scene.albam.vfs.select_vfile(local_app_id, mod_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}
    latest_mod = len(bpy.context.scene.albam.exportable.file_list) - 1
    armature = bpy.context.scene.albam.exportable.file_list[latest_mod].bl_object
    assert armature and armature.type == 'ARMATURE'
    bpy.context.scene.albam.import_options_lmt.armature = armature

    lmt_path = resolve_hashes(game_fs_root, {local_lmt_path_hash})[local_lmt_path_hash].lstrip("/")
    assert bpy.context.scene.albam.vfs.select_vfile(local_app_id, lmt_path)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}

    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    lmt_asset = bpy.context.scene.albam.exportable.file_list[latest_exported]
    bl_obj = lmt_asset.bl_object
    bl_objects = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]

    source_block, source_action = _first_used_block_with_action(bl_objects, local_app_id)
    assert source_action is not None, "No imported block with an action to reuse"

    # Build a block the way a user does through the UI: a bare empty, given
    # an existing action and told to (re)generate its animation - never
    # imported, so it never had a stored offset or track count to begin with.
    new_block_index = max(get_block_index(b, local_app_id) for b in bl_objects) + 1
    new_block = bpy.data.objects.new(f"{bl_obj.name}.new_block", None)
    try:
        new_block.parent = bl_obj
        set_block_index(new_block, local_app_id, new_block_index)
        custom_props = new_block.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
        custom_props.generate_new = True
        custom_props.action = source_action

        assert bpy.ops.albam.export() == {"FINISHED"}

        vfile_lmt_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, lmt_path)
        assert vfile_lmt_exported
        dst_lmt = parse(Lmt, vfile_lmt_exported.get_bytes(), local_app_id)

        dst_block = dst_lmt.block_offsets[new_block_index]
        assert dst_block.offset != 0, (
            "a block created (not imported) and given an action was written out "
            "as an empty slot"
        )
        assert dst_block.block_header.num_tracks > 0
    finally:
        bpy.data.objects.remove(new_block)
