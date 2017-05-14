import os
from tempfile import mkdtemp
import shutil

import pytest

from albam.engines.mtframework import Arc, Mod156, Tex112
from albam.lib.misc import find_files
from tests.conftest import SAMPLES_DIR, albam_import_export

ARC_SAMPLES_DIR = os.path.join(SAMPLES_DIR, 're5/arc')
ARC_FILES = [os.path.join(root, f) for root, _, files in os.walk(ARC_SAMPLES_DIR)
             for f in files if f.endswith('.arc')]


CACHE_ARC = {}  # source arc dir: list of all files extracted in a temp dir
CACHE_FILE_ARC = {}
TEMP_DIRS_TO_DELETE = set()
TEMP_FILES_TO_DELETE = set()
ARC_FILES_EXPORTED = False


@pytest.fixture(scope='module')
def mod156(mod_file_from_arc):
    mod156 = Mod156(mod_file_from_arc)
    return mod156


@pytest.fixture(scope='module')
def tex112(tex_file_from_arc):
    tex112 = Tex112(tex_file_from_arc)
    return tex112


def pytest_generate_tests(metafunc):
    global ARC_FILES_EXPORTED

    if 'mod_file_from_arc' in metafunc.fixturenames:
        mod_files, ids = _get_files_from_arcs(extension='.mod', arc_path=metafunc.config.option.dirarc)
        metafunc.parametrize("mod_file_from_arc", mod_files, scope='module', ids=ids)
    elif 'tex_file_from_arc' in metafunc.fixturenames:
        tex_files, ids = _get_files_from_arcs(extension='.tex', arc_path=metafunc.config.option.dirarc)
        metafunc.parametrize("tex_file_from_arc", tex_files, scope='module', ids=ids)
    elif 'mod156_mesh' in metafunc.fixturenames:
        mod_files, ids = _get_files_from_arcs(extension='.mod', arc_path=metafunc.config.option.dirarc)
        meshes, ids = _get_array_members_from_files(mod_files, ids, Mod156, 'meshes_array')
        metafunc.parametrize("mod156_mesh", meshes, scope='module', ids=ids)
    elif 'mod156_bone' in metafunc.fixturenames:
        mod_files, ids = _get_files_from_arcs(extension='.mod', arc_path=metafunc.config.option.dirarc)
        meshes, ids = _get_array_members_from_files(mod_files, ids, Mod156, 'bones_array')
        metafunc.parametrize("mod156_bone", meshes, scope='module', ids=ids)
    elif 'mod156_original' and 'mod156_exported' in metafunc.fixturenames:
        exported_files = []
        blender_path = metafunc.config.getoption('blender')
        if not blender_path:
            pytest.skip('No blender bin path supplied')
        else:
            if not ARC_FILES_EXPORTED:
                albam_import_export(blender_path, ARC_FILES)
                ARC_FILES_EXPORTED = True
            exported_files = [f + '.exported' for f in ARC_FILES]

            mod_files_original, ids_exported = _get_files_from_arcs(extension='.mod', arc_list=ARC_FILES)
            mod_files_exported, ids_exported = _get_files_from_arcs(extension='.mod', arc_list=exported_files)

            mod_files = list(zip(mod_files_original, mod_files_exported))
            mods = [(Mod156(t[0]), Mod156(t[1])) for t in mod_files]
            TEMP_FILES_TO_DELETE.update(exported_files)

            metafunc.parametrize("mod156_original, mod156_exported", mods, scope='module', ids=ids_exported)


def pytest_sessionfinish(session, exitstatus):
    # TODO: try to use tempdir fixture from config?
    for temp_dir in TEMP_DIRS_TO_DELETE:
        shutil.rmtree(temp_dir)
    for temp_file in TEMP_FILES_TO_DELETE:
        os.remove(temp_file)


def _get_files_from_arcs(extension, arc_list=None, arc_path=None):
    if arc_path:
        arc_list = find_files(arc_path, '.arc')
    elif arc_list:
        arc_list = arc_list
    else:
        arc_list = ARC_FILES
    files = []
    ids = []
    for arc_file in arc_list:
        files_in_arc = CACHE_ARC.get(arc_file)
        if not files_in_arc:
            _unpack_arc_in_temp(arc_file)
        files_in_arc = CACHE_ARC[arc_file]
        found_files = [f for f in files_in_arc if f.endswith(extension)]
        files.extend(found_files)
        ids_for_files = ['{}-->{}'.format(os.path.basename(arc_file), os.path.basename(f)) for f in found_files]
        ids.extend(ids_for_files)

    return files, ids


def _get_array_members_from_files(files, file_ids, struct_class, array_name):
    """
    Given a list of <files>, and <file_ids> of the same length,
    iterate over files and parse them using <struct_class> creating an structure object
    Then iterate over structure_object.<array_name> and return a list of all the members,
    along with a list of ids appending '--><array_name>-<array_index> to each member

    the attribute '_parent_structure' is added to each array member containing the structure
    where it was taken from
    """
    assert len(files) == len(file_ids)

    structures = [struct_class(f) for f in files]
    structs_and_ids = [(array_member,
                        file_ids[structure_index] + '-->{}-{}'.format(array_name, array_index),
                        structure_index)
                       for structure_index, structure in enumerate(structures)
                       for array_index, array_member in enumerate(getattr(structure, array_name))]
    array_members = [t[0] for t in structs_and_ids]
    ids = [t[1] for t in structs_and_ids]

    for triplet in structs_and_ids:
        array_member = triplet[0]
        struct_index = triplet[2]
        array_member._parent_structure = structures[struct_index]

    return array_members, ids


def _unpack_arc_in_temp(arc_file):
    tmp_dirname = os.path.basename(arc_file).replace('.arc', '-arc')
    base_temp = mkdtemp(suffix=tmp_dirname, prefix='ALBAM_')
    TEMP_DIRS_TO_DELETE.add(base_temp)
    arc = Arc(file_path=arc_file)
    arc.unpack(base_temp)
    CACHE_ARC[arc_file] = find_files(base_temp)

    return base_temp
