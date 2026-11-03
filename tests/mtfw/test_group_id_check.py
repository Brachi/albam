import pytest

import bpy

from albam.engines.mtfw.mesh import export_mod
from tests.mtfw.conftest import clear_scene, import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes


# Same pl00 model lmt_serialization_hashes.json and others already use -
# a real, committed re5 .mod with an armature and a real groups table.
RE5_MOD_PATH_HASH = "5d45d4682b062d49"


def _import_and_get_bl_obj(game_fs_root, local_app_id):
    clear_scene()
    bpy.context.scene.albam.apps.app_selected = local_app_id
    local_mod_path = resolve_hashes(game_fs_root, {RE5_MOD_PATH_HASH})[RE5_MOD_PATH_HASH].lstrip("/")
    import_vfile(local_app_id, local_mod_path)
    exportable = bpy.context.scene.albam.exportable
    latest = len(exportable.file_list) - 1
    return exportable.file_list[latest].bl_object


@pytest.mark.parametrize("local_app_id", ["re5"], scope="session")
def test_group_id_mismatch_warns(game_fs_root, local_app_id):
    """#375: a mesh whose Group ID isn't one of the model's own groups
    should warn, listing the IDs that are actually available - not raise,
    since the format allows a mesh to legitimately use an unusual one.
    """
    bl_obj = _import_and_get_bl_obj(game_fs_root, local_app_id)
    bl_mesh = next(c for c in bl_obj.children_recursive if c.type == "MESH")
    custom_properties = bl_mesh.data.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
    custom_properties.idx_group = 0xDEAD  # not a real group id on any shipped model

    with pytest.warns(UserWarning, match=r"Group ID 57005"):
        export_mod(bl_obj)


@pytest.mark.parametrize("local_app_id", ["re5"], scope="session")
def test_group_id_match_does_not_warn(game_fs_root, local_app_id, recwarn):
    """Baseline for the test above: an unmodified re5 model's own Group IDs
    already agree with its groups table, so exporting it as-is must not
    warn.
    """
    bl_obj = _import_and_get_bl_obj(game_fs_root, local_app_id)
    export_mod(bl_obj)

    assert not [w for w in recwarn.list if issubclass(w.category, UserWarning)]


@pytest.mark.parametrize("local_app_id", ["re5"], scope="session")
def test_group_id_mismatch_does_not_block_export(game_fs_root, local_app_id):
    """The check is a warning, not a hard failure (#375's suggested
    direction) - export through the real operator must still finish.
    """
    bl_obj = _import_and_get_bl_obj(game_fs_root, local_app_id)
    bl_mesh = next(c for c in bl_obj.children_recursive if c.type == "MESH")
    custom_properties = bl_mesh.data.albam_custom_properties.get_custom_properties_for_appid(local_app_id)
    custom_properties.idx_group = 0xDEAD

    exportable = bpy.context.scene.albam.exportable
    exportable.file_list_selected_index = len(exportable.file_list) - 1
    result = bpy.ops.albam.export()

    assert result == {"FINISHED"}
