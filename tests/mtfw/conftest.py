import os

import pytest

from albam.blender_ui.import_panel import (
    ALBAM_OT_AddFiles,
    ALBAM_OT_Import,
)


class FileWrapper:
    def __init__(self, file_path):
        self.name = os.path.basename(file_path)

@pytest.fixture
def lmt(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.structs.lmt import Lmt

    arc = request.param[0]
    file_entry = request.param[1]

    src_bytes = arc.get_file(file_entry.file_path, file_entry.file_type)

    parsed = Lmt.from_bytes(src_bytes)
    parsed._arc_name = os.path.basename(arc.file_path)
    parsed._file_path = file_entry.file_path

    return parsed


@pytest.fixture
def mrl(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.structs.mrl import Mrl
    arc = request.param[0]
    mrl_file_entry = request.param[1]

    mrl_bytes = arc.get_file(mrl_file_entry.file_path, mrl_file_entry.file_type)
    parsed_mrl = Mrl.from_bytes(mrl_bytes)
    parsed_mrl._arc_name = os.path.basename(arc.file_path)
    parsed_mrl._mrl_path = mrl_file_entry.file_path

    return parsed_mrl


@pytest.fixture
def mod(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.mesh import MOD_CLASS_MAPPER

    arc = request.param[0]
    file_entry = request.param[1]

    src_bytes = arc.get_file(file_entry.file_path, file_entry.file_type)
    mod_version = src_bytes[4]
    ModCls = MOD_CLASS_MAPPER[mod_version]

    parsed = ModCls.from_bytes(src_bytes)
    parsed._arc_name = os.path.basename(arc.file_path)
    parsed._file_path = file_entry.file_path

    return parsed


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
