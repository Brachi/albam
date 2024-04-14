import os
import io

import bpy
import pytest

TMP_DATASET = [
    {
        "app_id": "re0",
        "mod_path": "model/em/em02/em02.mod",
        "mrl_path": "model/em/em02/em02.mrl",
    },
    {
        "app_id": "re1",
        "mod_path": "model/pl/pl00/pl00.mod",
        "mrl_path": "model/pl/pl00/pl00.mrl",
    },
    {
        "app_id": "re5",
        "mod_path": "pawn/pl/pl00/model/pl0000.mod",
        "mrl_path": None,
    },
    {
        "app_id": "rev1",
        "mod_path": "model/chara/pl/pl1000/pl1000.mod",
        "mrl_path": "model/chara/pl/pl1000/pl1000.mrl",
    },
    {
        "app_id": "rev2",
        "mod_path": "data/chara/pl/pl2200_N/model/pl2200.mod",
        "mrl_path": "data/chara/pl/pl2200_N/model/pl2200.mrl",
    },
]


class FileWrapper:
    def __init__(self, file_path):
        self.name = os.path.basename(file_path)


@pytest.fixture(scope="session")
def loaded_arcs(pytestconfig):
    """
    Loads all the arcs found in the config option --arcdir
    with the corresponding app-id to the vfs.
    Equivalent to selecting an app, clicking "Add files"
    and selecting all files ending in .arc in a directory
    """
    # TODO: recursive walk in directories
    arc_dirs = pytestconfig.getoption("arcdir")
    if not arc_dirs:
        pytest.skip("No arc directory or app_id supplied")
        return

    for app_id_and_arc_dir in arc_dirs:
        app_id, arc_dir = app_id_and_arc_dir.split("::")
        bpy.context.scene.albam.apps.app_selected = app_id
        files = [{'name': name} for name in os.listdir(arc_dir)]
        bpy.ops.albam.add_files(directory=arc_dir, files=files)


@pytest.fixture(scope="session")
def mod_export(loaded_arcs):
    from albam.engines.mtfw.mesh import APPID_CLASS_MAPPER
    from albam.engines.mtfw.structs.mrl import Mrl
    from kaitaistruct import KaitaiStream

    dataset = TMP_DATASET[4]  # FIXME: un-hardcode
    app_id = dataset["app_id"]
    mod_path = dataset["mod_path"]
    mrl_path = dataset["mrl_path"]

    bpy.context.scene.albam.apps.app_selected = app_id
    bpy.context.scene.albam.import_settings.import_only_main_lods = False

    vfile_mod = bpy.context.scene.albam.vfs.select_vfile(app_id, mod_path)
    vfile_mrl = bpy.context.scene.albam.vfs.get_vfile(app_id, mrl_path) if mrl_path else None
    assert vfile_mod and ((mrl_path and vfile_mrl) or (not mrl_path and not vfile_mrl))

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}

    vfile_mod_exported = bpy.context.scene.albam.exported.select_vfile(app_id, mod_path)
    vfile_mrl_exported = bpy.context.scene.albam.exported.get_vfile(app_id, mrl_path) if mrl_path else None
    assert vfile_mod_exported and (
        (mrl_path and vfile_mrl_exported) or
        (not mrl_path and not vfile_mrl_exported))

    Mod = APPID_CLASS_MAPPER[app_id]
    src_mod = Mod.from_bytes(vfile_mod.get_bytes())
    dst_mod = Mod.from_bytes(vfile_mod_exported.get_bytes())
    src_mod._read()
    dst_mod._read()

    src_mrl = Mrl(app_id, KaitaiStream(io.BytesIO(vfile_mrl.get_bytes()))) if mrl_path else None
    dst_mrl = Mrl(app_id, KaitaiStream(io.BytesIO(vfile_mrl_exported.get_bytes()))) if mrl_path else None
    if mrl_path:
        src_mrl._read()
        dst_mrl._read()
    return src_mod, dst_mod, src_mrl, dst_mrl


@pytest.fixture(scope="session")
def mod_imported(mod_export):
    return mod_export[0]


@pytest.fixture(scope="session")
def mod_exported(mod_export):
    return mod_export[1]


@pytest.fixture(scope="session")
def mrl_imported(mod_export):
    return mod_export[2]


@pytest.fixture(scope="session")
def mrl_exported(mod_export):
    return mod_export[3]


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
    from kaitaistruct import KaitaiStream
    arc = request.param[0]
    mrl_file_entry = request.param[1]
    app_id = request.param[2]

    mrl_bytes = arc.get_file(mrl_file_entry.file_path, mrl_file_entry.file_type)
    parsed_mrl = Mrl(app_id, KaitaiStream(io.BytesIO(mrl_bytes)))
    parsed_mrl.app_id = app_id
    parsed_mrl._read()
    parsed_mrl._arc_name = os.path.basename(arc.file_path)
    parsed_mrl._mrl_path = mrl_file_entry.file_path
    parsed_mrl._num_bytes = len(mrl_bytes)

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
    parsed._read()
    parsed._arc_name = os.path.basename(arc.file_path)
    parsed._src_bytes = src_bytes
    parsed._file_path = file_entry.file_path

    return parsed


@pytest.fixture
def tex(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.texture import APPID_TEXCLS_MAP
    arc = request.param[0]
    tex_file_entry = request.param[1]
    app_id = request.param[2]
    Tex = APPID_TEXCLS_MAP[app_id]

    tex_bytes = arc.get_file(tex_file_entry.file_path, tex_file_entry.file_type)
    parsed_tex = Tex.from_bytes(tex_bytes)
    parsed_tex._read()
    parsed_tex._arc_name = os.path.basename(arc.file_path)
    parsed_tex._mrl_path = tex_file_entry.file_path
    parsed_tex._num_bytes = len(tex_bytes)

    return parsed_tex
