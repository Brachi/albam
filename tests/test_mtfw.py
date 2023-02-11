import os

import bpy
import pytest

from albam.engines.mtfw.archive import import_arc


@pytest.fixture
def imported_arc(arc_filepath, scope="function"):
    bl_container = import_arc(arc_filepath)

    yield arc_filepath, bl_container

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


def test_import_arc(imported_arc):
    arc_filepath, bl_container = imported_arc

    assert bl_container.name == os.path.basename(arc_filepath)
