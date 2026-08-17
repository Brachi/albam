import os
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

    elif ("app_id" in metafunc.fixturenames and
          "sbc_path" in metafunc.fixturenames):
        argnames = ("app_id", "sbc_path")
        argvalues = [(d["app_id"], d["sbc_path"]) for d in MTFW_DATASET]
        metafunc.parametrize(argnames, argvalues, scope="session")

    elif ("app_id" in metafunc.fixturenames and
          "nav_path" in metafunc.fixturenames):
        argnames = ("app_id", "nav_path")
        argvalues = [(d["app_id"], d["nav_path"]) for d in MTFW_DATASET]
        metafunc.parametrize(argnames, argvalues, scope="session")


# --- MTFW_FS-based fixtures (shared across the hash-driven, --game-dir/R2
# tests migrating off the --arcdir/ArcWrapper fixtures below) ---

R2_PROTOCOL_PREFIX = "r2://"

# app_id -> the MTFW_FS instance already mounted as a VFS root this session -
# add_fs_root() must only run once per app_id (it always creates a new root;
# node ids are app_id::relative_path only, not scoped per-root, so adding
# the same game folder twice would create ambiguous duplicate entries).
_GAME_FS_INSTANCES = {}


def _game_dirs(pytestconfig):
    # Already validated (well-formed "<app-id>::<value>", once, at startup)
    # by tests/conftest.py's pytest_configure - see there. <value> is either
    # a local directory path, or the literal "r2://" sentinel selecting the
    # R2 backend explicitly (see tests.mtfw.r2_config.r2_kwargs_for_app) -
    # never inferred from whether a local path happens to exist.
    parsed = {}
    for app_id_and_dir in pytestconfig.getoption("game_dir") or []:
        app_id, value = app_id_and_dir.split("::")
        parsed[app_id] = value
    return parsed


@pytest.fixture(scope="session")
def game_fs_root(pytestconfig, local_app_id):
    """
    Mounts a VFS root for local_app_id via MTFW_FS (once per session, cached
    in _GAME_FS_INSTANCES) - the same mechanism "Add Folder" uses in the UI
    for a whole game install, unlike --arcdir's flat directory of loose .arc
    dumps. Returns the MTFW_FS instance itself, so callers can
    resolve_hashes() against the exact same tree that got mounted into the
    VFS.

    The source is explicit in --game-dir's value, never inferred: a plain
    path mounts a local install (skips if it doesn't exist); the literal
    "r2://" mounts R2 instead, resolving bucket/prefix/credentials from env
    vars (see tests.mtfw.r2_config.r2_kwargs_for_app - this is what lets CI
    exercise these tests without a full local game install, passing
    --game-dir=<app>::r2:// with credentials supplied separately via
    secrets, never on the command line). No --game-dir at all for this
    app_id skips outright - no implicit fallback either way.

    Scanning + flattening a full local game install's tree can take a while
    (a real RE5 install has ~1200 archives) - that cost is paid once per
    app_id per session, not per test.
    """
    from albam.engines.mtfw.arc_fs import MTFW_FS
    from tests.mtfw.r2_config import r2_kwargs_for_app

    if local_app_id not in _GAME_FS_INSTANCES:
        value = _game_dirs(pytestconfig).get(local_app_id)
        if not value:
            pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")
        elif value == R2_PROTOCOL_PREFIX:
            r2_kwargs = r2_kwargs_for_app(local_app_id)
            if r2_kwargs is None:
                pytest.skip(
                    f"--game-dir={local_app_id}::r2:// requested but R2 isn't configured "
                    f"(missing s3 extras or credentials - see .env.example)"
                )
            game_fs = MTFW_FS.from_s3(**r2_kwargs)
        elif not os.path.isdir(value):
            pytest.skip(f"--game-dir={local_app_id}::{value} does not exist")
        else:
            game_fs = MTFW_FS(value)

        bpy.context.scene.albam.apps.app_selected = local_app_id
        vfs = bpy.context.scene.albam.vfs
        vfs.add_fs_root(local_app_id, game_fs, display_name=f"{local_app_id}-local")
        _GAME_FS_INSTANCES[local_app_id] = game_fs

    return _GAME_FS_INSTANCES[local_app_id]


def import_export(local_app_id, local_path):
    """Select local_path (already resolved from a committed hash, and
    already mounted into the VFS via game_fs_root) and run it through the
    real Blender import_vfile()/export() operators - the shared
    "select, import, export" step every *_local round-trip fixture needs.
    Returns the source vfile; callers fetch whatever exported vfile(s) they
    need afterward from bpy.context.scene.albam.exported, since what comes
    out varies (a straight copy for a standalone file, but also an
    accompanying .mrl alongside a mod).
    """
    vfs = bpy.context.scene.albam.vfs
    try:
        vfile = vfs.select_vfile(local_app_id, local_path)
    except KeyError:
        pytest.skip(f"{local_path!r} not found under --game-dir for app_id={local_app_id!r}")

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}
    return vfile


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
def sbc_export(loaded_arcs, app_id, sbc_path):
    from albam.engines.mtfw.collision import APPID_SBC_CLASS_MAPPER
    if not sbc_path:
        pytest.skip("No sbc available")
    bpy.context.scene.albam.apps.app_selected = app_id
    vfile_sbc = bpy.context.scene.albam.vfs.select_vfile(app_id, sbc_path)
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}

    vfile_sbc_exported = bpy.context.scene.albam.exported.select_vfile(app_id, sbc_path)
    assert vfile_sbc_exported
    Sbc = APPID_SBC_CLASS_MAPPER[app_id]
    src_sbc = Sbc.from_bytes(vfile_sbc.get_bytes())
    dst_sbc = Sbc.from_bytes(vfile_sbc_exported.get_bytes())
    src_sbc._read()
    dst_sbc._read()
    return src_sbc, dst_sbc


@pytest.fixture(scope="session")
def sbc_imported(sbc_export):
    sbc = sbc_export[0]
    if not sbc:
        pytest.skip("No imported sbc available")
    else:
        return sbc


@pytest.fixture(scope="session")
def sbc_exported(sbc_export):
    sbc = sbc_export[1]
    if not sbc:
        pytest.skip("No exported sbc available")
    else:
        return sbc


@pytest.fixture(scope="session")
def nav_export(loaded_arcs, app_id, nav_path):
    if not nav_path:
        pytest.skip("No nav available")
    bpy.context.scene.albam.apps.app_selected = app_id
    vfile_nav = bpy.context.scene.albam.vfs.select_vfile(app_id, nav_path)
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}

    vfile_nav_exported = bpy.context.scene.albam.exported.select_vfile(app_id, nav_path)
    assert vfile_nav_exported
    from albam.engines.mtfw.structs.nav_156 import Nav156
    src_nav = Nav156.from_bytes(vfile_nav.get_bytes())
    dst_nav = Nav156.from_bytes(vfile_nav_exported.get_bytes())
    src_nav._read()
    dst_nav._read()
    return src_nav, dst_nav


@pytest.fixture(scope="session")
def nav_imported(nav_export):
    nav = nav_export[0]
    if not nav:
        pytest.skip("No imported nav available")
    else:
        return nav


@pytest.fixture(scope="session")
def nav_exported(nav_export):
    nav = nav_export[1]
    if not nav:
        pytest.skip("No exported nav available")
    else:
        return nav


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
