import concurrent.futures
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
TEMP_DIRS_TO_DELETE = set()
TEMP_FILES_TO_DELETE = set()
ARC_FILES_EXPORTED = False


def _get_files_from_arcs(extension, arc_list=None, arc_path=None):
    use_concurrency = False  # experimental
    if arc_path:
        arc_list = find_files(arc_path, '.arc')
    elif arc_list:
        arc_list = arc_list
    else:
        arc_list = ARC_FILES
    to_export = [arc_file for arc_file in arc_list if arc_file not in CACHE_ARC]
    if to_export and use_concurrency:
        concurrent_unpack(arc_list, CACHE_ARC, extension)
    elif to_export and not use_concurrency:
        for arc_file in to_export:
            _unpack_arc_in_temp(arc_file, CACHE_ARC)

    files, ids = _get_files_and_ids(extension, arc_list)
    return files, ids


def _get_files_and_ids(extension, arc_list):
    files = []
    ids = []
    for arc_file in arc_list:
        files_in_arc = CACHE_ARC.get(arc_file)
        if not files_in_arc:
            print('arc_file missing, skipping', arc_file)
            continue
        found_files = [f for f in files_in_arc if f.endswith(extension)]
        files.extend(found_files)
        ids_for_files = ['{}-->{}'.format(os.path.basename(arc_file), os.path.basename(f)) for f in found_files]
        ids.extend(ids_for_files)
    return files, ids


def concurrent_unpack(arc_list, cache_arc, extension):

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_extracted = {executor.submit(_unpack_arc_in_temp, arc_file, CACHE_ARC) for arc_file in arc_list}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_extracted)):
            future.result()


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


def _unpack_arc_in_temp(arc_file, arc_cache):
    tmp_dirname = os.path.basename(arc_file).replace('.arc', '-arc')
    base_temp = mkdtemp(suffix=tmp_dirname, prefix='ALBAM_')
    TEMP_DIRS_TO_DELETE.add(base_temp)
    try:
        arc = Arc(file_path=arc_file)
    except Exception:
        print('error unpacking', arc_file)
        return
    arc.unpack(base_temp)
    arc_cache[arc_file] = find_files(base_temp)
