import os

import bpy
import pytest

from albam.blender_ui.import_panel import (
    ALBAM_OT_AddFiles,
    ALBAM_OT_Import,
)


class FileWrapper:
    def __init__(self, file_path):
        self.name = os.path.basename(file_path)


@pytest.fixture
def loaded_mod_files(arc_filepath, scope="function"):
    directory = os.path.dirname(arc_filepath)
    ALBAM_OT_AddFiles._execute(bpy.context, directory, [FileWrapper(arc_filepath)])

    file_list = bpy.context.scene.albam.file_explorer.file_list

    mod_files = [f for f in file_list if f.name.endswith('.mod')]

    yield mod_files

    # TODO: cleanup, for memory
    """
    id_objs = {c.id_data for c in bl_container.children_recursive}
    id_objs.add(bl_container.id_data)
    bpy.data.batch_remove(id_objs)
    id_meshes = {m.id_data for m in bpy.data.meshes if m.users == 0}
    bpy.data.batch_remove(id_meshes)
    id_materials = {m.id_data for m in bpy.data.materials if m.users == 0}
    bpy.data.batch_remove(id_materials)
    id_images = {i.id_data for i in bpy.data.images if i.users == 0}
    bpy.data.batch_remove(id_images)
    id_armatures = {a.id_data for a in bpy.data.armatures if a.users == 0}
    bpy.data.batch_remove(id_armatures)
    del bl_container
    """


def test_import_mod(loaded_mod_files):

    for mod_file in loaded_mod_files:
        ALBAM_OT_Import._execute(mod_file, bpy.context)
        assert bpy.data.objects[mod_file.display_name]
