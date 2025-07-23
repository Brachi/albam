import os
import io
import json

import bpy
import pytest


MTFW_DATASET = []


def pytest_generate_tests(metafunc):
    global MTFW_DATASET
    mtfw_dataset_path = metafunc.config.getoption("mtfw_dataset")
    if mtfw_dataset_path and not MTFW_DATASET:
        # if loading multiple times will generate multiple
        # tests even with scope=session. We want only one
        # import-export per item in the dataset
        with open(mtfw_dataset_path) as f:
            MTFW_DATASET = json.load(f)

    if ("app_id" in metafunc.fixturenames and
            "mod_path" in metafunc.fixturenames and
            "mrl_path" in metafunc.fixturenames):
        argnames = ("app_id", "mod_path", "mrl_path")
        argvalues = []
        for data_dict in MTFW_DATASET:
            app_id = data_dict["app_id"]
            mod_path = data_dict["mod_path"]
            mrl_path = data_dict["mrl_path"]
            argvalues.append((app_id, mod_path, mrl_path))
        metafunc.parametrize(argnames, argvalues, scope="session")

    elif "parsed_mod_from_arc" in metafunc.fixturenames:
        _generate_tests_from_arcs("mod", metafunc, "parsed_mod_from_arc")
    elif "parsed_mrl_from_arc" in metafunc.fixturenames:
        _generate_tests_from_arcs("mrl", metafunc, "parsed_mrl_from_arc")
    elif "parsed_lmt_from_arc" in metafunc.fixturenames:
        _generate_tests_from_arcs("lmt", metafunc, "parsed_lmt_from_arc")
    elif "parsed_tex_from_arc" in metafunc.fixturenames:
        _generate_tests_from_arcs("tex", metafunc, "parsed_tex_from_arc")


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
        files = [{'name': name} for name in os.listdir(arc_dir) if name.endswith(".arc")]
        bpy.ops.albam.add_files(directory=arc_dir, files=files)


@pytest.fixture(scope="session")
def mod_export(loaded_arcs, app_id, mod_path, mrl_path):
    from albam.engines.mtfw.mesh import APPID_CLASS_MAPPER
    from albam.engines.mtfw.structs.mrl import Mrl
    from kaitaistruct import KaitaiStream

    bpy.context.scene.albam.apps.app_selected = app_id
    if app_id == "dd":
        bpy.context.scene.albam.export_settings.no_vf_grouping = True
    bpy.context.scene.albam.import_settings.import_only_main_lods = False

    vfile_mod = bpy.context.scene.albam.vfs.select_vfile(app_id, mod_path)
    vfile_mrl = bpy.context.scene.albam.vfs.get_vfile(app_id, mrl_path) if mrl_path else None
    assert vfile_mod and ((mrl_path and vfile_mrl) or (not mrl_path and not vfile_mrl))

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}

    vfile_mod_exported = bpy.context.scene.albam.exported.select_vfile(app_id, mod_path)
    try:
        vfile_mrl_exported = (bpy.context.scene.albam.exported.get_vfile(app_id, mrl_path)
                              if mrl_path else None)
    except KeyError:
        mrl_path = mrl_path.replace("_0.mrl", ".mrl")
        vfile_mrl_exported = (bpy.context.scene.albam.exported.get_vfile(app_id, mrl_path)
                              if mrl_path else None)

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
    mrl = mod_export[2]
    if not mrl:
        pytest.skip("No mrl available")
    else:
        return mrl


@pytest.fixture(scope="session")
def mrl_exported(mod_export):
    mrl = mod_export[3]
    if not mrl:
        pytest.skip("No mrl available")
    else:
        return mrl


@pytest.fixture
def parsed_mrl_from_arc(request, scope="session"):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found

    # TODO: cache, avoid duplicating mrls for each test
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
def parsed_mod_from_arc(request):
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
def parsed_tex_from_arc(request):
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


@pytest.fixture
def parsed_lmt_from_arc(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.structs.lmt import Lmt

    arc = request.param[0]
    file_entry = request.param[1]

    src_bytes = arc.get_file(file_entry.file_path, file_entry.file_type)

    parsed = Lmt.from_bytes(src_bytes)
    parsed._read()
    parsed._arc_name = os.path.basename(arc.file_path)
    parsed._file_path = file_entry.file_path

    return parsed


ARC_DIRS = None


def _generate_tests_from_arcs(file_extension, metafunc, fixturename):
    """
    Generate one parsed object for file_extension, based on provided arcs.
    Defer decompression and parsing to test-run time, not
    collection time.
    It requires a fixture named after the extension
    """
    global ARC_DIRS
    arc_dirs = metafunc.config.getoption("arcdir")
    if not arc_dirs:
        pytest.skip("No arc directory supplied")
        return

    if arc_dirs and not ARC_DIRS:
        # if loading multiple times will generate multiple
        # tests even with scope=session. We want only one
        # import-export per item in the dataset
        ARC_DIRS = arc_dirs

    total_parsed_files = []
    total_test_ids = []

    for arc_dir in ARC_DIRS:
        app_id, arc_dir = arc_dir.split("::")
        ARC_FILES = [
            os.path.join(root, f)
            for root, _, files in os.walk(arc_dir)
            for f in files
            if f.endswith(".arc")
        ]

        if not ARC_FILES:
            raise ValueError(f"No files ending in .arc found in {arc_dir}")
        parsed_files, ids = _files_per_arc(file_extension, ARC_FILES, app_id)
        total_parsed_files.extend(parsed_files)
        total_test_ids.extend(ids)
    metafunc.parametrize(fixturename, total_parsed_files, indirect=True, ids=total_test_ids)


def _files_per_arc(file_extension, arc_paths, app_id):
    # importing here to avoid errors in test collection.
    # Since collection happens before calling register() in `pytest_sessionstart`
    # sys.path is not modified to include albam_vendor, so the vendored dep kaitaistruct
    # is not found when needed.
    from albam.engines.mtfw.archive import ArcWrapper
    final = []
    ids = []
    failed_arcs = []
    for arc_path in arc_paths:
        arc_name = os.path.basename(arc_path)
        try:
            arc = ArcWrapper(arc_path)
        except OSError as err:  # TODO: skip/xfail
            if err.errno == 24:
                raise RuntimeError("Exceeded open file limits. Try running `ulimit -S -n 4096`")
        except Exception:
            failed_arcs.append(arc_path)
            continue

        file_entries = arc.get_file_entries_by_extension(file_extension)
        if not file_entries:
            del arc
            continue
        for fe in file_entries:
            final.append((arc, fe, app_id))
            ids.append("::".join((arc_name, f"{fe.file_path}.{file_extension}")))
    if failed_arcs:
        print(f"failed to load the following arc files: {failed_arcs}")

    return final, ids
