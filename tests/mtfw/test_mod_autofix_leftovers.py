import json
import os

import bpy
import pytest

from tests.mtfw.conftest import clear_scene, import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes


MOD_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "mod_serialization_hashes.json"
)
with open(MOD_SERIALIZATION_DATASET_PATH) as f:
    RE5_MOD_PATH_HASH = next(d["mod_path_hash"] for d in json.load(f) if d["app_id"] == "re5")


def _leave_stale_autofix_copy(bl_mesh):
    """What an autofix export that died before cleaning up leaves behind
    (e.g. #330 on 0.5.0, then the .blend saved): an AlbamTemp collection
    holding a copy of one of the model's meshes. copy() keeps the parent,
    so the copy is still a child of the exported object.
    """
    stale = bl_mesh.copy()
    stale.data = bl_mesh.data.copy()
    temp_collection = bpy.data.collections.new("AlbamTemp")
    bpy.context.scene.collection.children.link(temp_collection)
    temp_collection.objects.link(stale)
    return stale


@pytest.mark.parametrize("local_app_id", ["re5"], scope="session")
def test_autofix_export_survives_stale_albam_temp(game_fs_root, local_app_id):
    """#331: an AlbamTemp left by an earlier failed export must not break
    the next one. Its copies are children of the exported object, so they
    get collected as meshes to export, then deleted by the stale cleanup
    before being duplicated - ReferenceError: StructRNA of type Object has
    been removed.
    """
    clear_scene()
    bpy.context.scene.albam.apps.app_selected = local_app_id
    bpy.context.scene.albam.export_settings.export_autofix = True

    local_mod_path = resolve_hashes(game_fs_root, {RE5_MOD_PATH_HASH})[RE5_MOD_PATH_HASH].lstrip("/")
    import_vfile(local_app_id, local_mod_path)
    exportable = bpy.context.scene.albam.exportable
    latest = len(exportable.file_list) - 1
    bl_obj = exportable.file_list[latest].bl_object
    original_names = {c.name for c in bl_obj.children_recursive if c.type == "MESH"}

    stale = _leave_stale_autofix_copy(bpy.data.objects[sorted(original_names)[0]])
    assert stale.parent is not None and stale in bl_obj.children_recursive

    exportable.file_list_selected_index = latest
    try:
        result = bpy.ops.albam.export()
    finally:
        bpy.context.scene.albam.export_settings.export_autofix = False

    assert result == {"FINISHED"}
    assert "AlbamTemp" not in bpy.data.collections
    assert {c.name for c in bl_obj.children_recursive if c.type == "MESH"} == original_names


@pytest.mark.parametrize("local_app_id", ["re5"], scope="session")
def test_autofix_export_survives_excluded_albam_temp(game_fs_root, local_app_id):
    """#330: an existing AlbamTemp that is excluded from the view layer (the
    user unticked it in the outliner) must not be reused as is. Copies moved
    into it are not in the view layer, so apply_transform cannot select
    them - RuntimeError: Object ... cannot be selected because it is not in
    View Layer.
    """
    clear_scene()
    bpy.context.scene.albam.apps.app_selected = local_app_id
    bpy.context.scene.albam.export_settings.export_autofix = True

    local_mod_path = resolve_hashes(game_fs_root, {RE5_MOD_PATH_HASH})[RE5_MOD_PATH_HASH].lstrip("/")
    import_vfile(local_app_id, local_mod_path)
    exportable = bpy.context.scene.albam.exportable
    latest = len(exportable.file_list) - 1
    bl_obj = exportable.file_list[latest].bl_object
    original_names = {c.name for c in bl_obj.children_recursive if c.type == "MESH"}

    # Empty, so this exercises #330 alone rather than tripping #331 first.
    temp_collection = bpy.data.collections.new("AlbamTemp")
    bpy.context.scene.collection.children.link(temp_collection)
    bpy.context.view_layer.layer_collection.children["AlbamTemp"].exclude = True

    exportable.file_list_selected_index = latest
    try:
        result = bpy.ops.albam.export()
    finally:
        bpy.context.scene.albam.export_settings.export_autofix = False

    assert result == {"FINISHED"}
    assert "AlbamTemp" not in bpy.data.collections
    assert {c.name for c in bl_obj.children_recursive if c.type == "MESH"} == original_names
