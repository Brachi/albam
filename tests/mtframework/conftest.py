import os
from tempfile import mkdtemp
import shutil

import pytest

from albam.engines.mtframework import Arc, Mod156, Tex112
from albam.lib.misc import find_files
from tests.conftest import SAMPLES_DIR

ARC_SAMPLES_DIR = os.path.join(SAMPLES_DIR, 're5/arc')
ARC_FILES = [os.path.join(root, f) for root, _, files in os.walk(ARC_SAMPLES_DIR)
             for f in files if f.endswith('.arc')]


CACHE_ARC = {}  # source arc dir: list of all files extracted in a temp dir
CACHE_FILE_ARC = {}
CACHE_TEMP_DIRS = set()


@pytest.fixture(scope='module')
def mod156(mod_file_from_arc):
    mod156 = Mod156(mod_file_from_arc)
    return mod156


@pytest.fixture(scope='module')
def tex112(tex_file_from_arc):
    tex112 = Tex112(tex_file_from_arc)
    return tex112


def pytest_generate_tests(metafunc):
    if 'mod_file_from_arc' in metafunc.fixturenames:
        mod_files = _get_files_from_arcs(extension='.mod', arc_path=metafunc.config.option.dirarc)
        mod_file_names = [os.path.basename(mf) for mf in mod_files]
        metafunc.parametrize("mod_file_from_arc", mod_files, scope='module', ids=mod_file_names)
    elif 'tex_file_from_arc' in metafunc.fixturenames:
        tex_files = _get_files_from_arcs(extension='.tex', arc_path=metafunc.config.option.dirarc)
        tex_file_names = [os.path.basename(tf) for tf in tex_files]
        metafunc.parametrize("tex_file_from_arc", tex_files, scope='module', ids=tex_file_names)
    elif 'mod156_original' and 'mod156_exported' in metafunc.fixturenames:
        mod_files = _get_files_from_arcs(extension='.mod', arc_path=metafunc.config.option.dirarc)
        mod_files = _import_export_blender(mod_files)
        metafunc.parametrize("mod156_original, mod156_exported", mod_files, scope='module')


def pytest_sessionfinish(session, exitstatus):
    # TODO: try to use tempdir fixture from config?
    for temp_dir in CACHE_TEMP_DIRS:
        shutil.rmtree(temp_dir)


def _get_files_from_arcs(extension, arc_path=None):
    if arc_path:
        arc_list = find_files(arc_path, '.arc')
    else:
        arc_list = ARC_FILES
    files = []
    for arc_file in arc_list:
        files_in_arc = CACHE_ARC.get(arc_file)
        if not files_in_arc:
            _unpack_arc_in_temp(arc_file)
        files_in_arc = CACHE_ARC[arc_file]
        found_files = [f for f in files_in_arc if f.endswith(extension)]
        files.extend(found_files)
    return files


def _unpack_arc_in_temp(arc_file):
    tmp_dirname = os.path.basename(arc_file).replace('.arc', '-arc')
    base_temp = mkdtemp(suffix=tmp_dirname, prefix='ALBAM_')
    CACHE_TEMP_DIRS.add(base_temp)
    arc = Arc(file_path=arc_file)
    arc.unpack(base_temp)
    CACHE_ARC[arc_file] = find_files(base_temp)

    return base_temp


def _import_export_blender(mod_files):
    out = []

    for mod_file in mod_files:
        result = (Mod156(mod_file), Mod156(mod_file))
        out.append(result)
    return out
