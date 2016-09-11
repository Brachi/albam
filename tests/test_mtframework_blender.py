from difflib import SequenceMatcher
from itertools import chain
import os
import subprocess
from tempfile import TemporaryDirectory, gettempdir

import pytest

from albam.mtframework import Mod156, Arc, KNOWN_ARC_BLENDER_CRASH
from albam.utils import get_offset, get_size
from tests.test_mtframework_arc import arc_re5_samples

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')
EXPECTED_VERTEX_BUFFER_RATIO = 0.65
EXPECTED_MAX_INDICES_COUNT_RATIO = 0.17
EXPECTED_INDEX_BUFFER_RATIO = 0.65
EXPECTED_MAX_MISSING_VERTICES = 4000   # this is actually depending on the size of the model
PYTHON_TEMPLATE = """import os
import logging
import sys
import time
sys.path.append('{project_dir}')
import bpy

from albam.mtframework.blender_import import import_arc
from albam.mtframework.blender_export import export_arc
from albam import register

logging.basicConfig(filename='{log_filepath}', level=logging.DEBUG)

logging.debug('Importing {import_arc_filepath}')

# TODO: use the UI panels directly?
try:
    register()
except ValueError:  # The addon is installed in blender.
    pass

try:
    start = time.time()
    logging.debug('Importing {import_arc_filepath}')
    import_arc('{import_arc_filepath}', '{import_unpack_dir}', bpy.context.scene)
    logging.debug('Import time: {{}} seconds [{import_arc_filepath}])'.format(round(time.time() - start, 2)))
except Exception:
    logging.exception('IMPORT failed: {import_arc_filepath}')
    sys.exit(1)
time.sleep(4)
try:
    imported_name = os.path.basename('{import_arc_filepath}')
    start = time.time()
    exported_arc = export_arc(bpy.data.objects[imported_name])
    logging.debug('Export time: {{}} seconds [{import_arc_filepath}]'.format(round(time.time() - start, 2)))
    with open('{export_arc_filepath}', 'wb') as w:
        w.write(exported_arc)
except Exception:
    logging.exception('EXPORT failed: {import_arc_filepath}')
    sys.exit(1)
"""


def is_close(a, b):
    return abs(a) - abs(b) < 0.001


@pytest.fixture(scope='module', params=arc_re5_samples())
def mods_from_arc(request, tmpdir_factory):
    blender = pytest.config.getoption('blender')
    if not blender:
        pytest.skip('No blender bin path supplied')

    import_arc_filepath = request.param
    if import_arc_filepath.endswith(tuple(KNOWN_ARC_BLENDER_CRASH)):
        pytest.xfail('Known arc crashes blender')
    log_filepath = str(tmpdir_factory.getbasetemp().join('blender.log'))
    import_unpack_dir = TemporaryDirectory()
    export_arc_filepath = os.path.join(gettempdir(), os.path.basename(import_arc_filepath))
    script_filepath = os.path.join(gettempdir(), 'import_arc.py')

    with open(script_filepath, 'w') as w:
        w.write(PYTHON_TEMPLATE.format(project_dir=os.getcwd(),
                                       import_arc_filepath=import_arc_filepath,
                                       export_arc_filepath=export_arc_filepath,
                                       import_unpack_dir=import_unpack_dir.name,
                                       log_filepath=log_filepath))
    args = '{} -noaudio --background --python {}'.format(blender, script_filepath)
    try:
        subprocess.check_output((args,), shell=True)
    except subprocess.CalledProcessError:
        # the test will actually error here, if the import/export fails, since the file won't exist.
        # which is better, since pytest traceback to subprocess.check_output is pretty long and useless
        with open(log_filepath) as f:
            for line in f:
                print(line)   # XXX: should print only the last n lines
        os.unlink(export_arc_filepath)
        os.unlink(script_filepath)
        raise

    export_unpack_dir = TemporaryDirectory()
    arc = Arc(export_arc_filepath)
    arc.unpack(export_unpack_dir.name)

    mod_files_original = [os.path.join(root, f) for root, _, files in os.walk(import_unpack_dir.name)
                          for f in files if f.endswith('.mod')]
    mod_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_unpack_dir.name)
                          for f in files if f.endswith('.mod')]
    mod_files_original = sorted(mod_files_original, key=os.path.basename)
    mod_files_exported = sorted(mod_files_exported, key=os.path.basename)
    mod_objects_original = []
    mod_objects_exported = []
    if mod_files_original and mod_files_exported:
        os.unlink(export_arc_filepath)
        os.unlink(script_filepath)
        for i, mod_file_original in enumerate(mod_files_original):
            mod_original = Mod156(file_path=mod_file_original)
            mod_exported = Mod156(file_path=mod_files_exported[i])
            mod_objects_original.append(mod_original)
            mod_objects_exported.append(mod_exported)
    else:
        os.unlink(export_arc_filepath)
        os.unlink(script_filepath)
        pytest.skip('Arc contains no mod files')
    return mod_objects_original, mod_objects_exported


def test_mod156_import_export_export_id_magic(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.id_magic == mod_exported.id_magic


def test_mod156_import_export_version(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.version == mod_exported.version


def test_mod156_import_export_version_rev(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.version_rev == mod_exported.version_rev


def test_mod156_import_export_bone_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.bone_count == mod_exported.bone_count


def test_mod156_import_export_mesh_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.mesh_count == mod_exported.mesh_count


def test_mod156_import_export_material_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.material_count == mod_exported.material_count


@pytest.mark.skip
def test_mod156_import_export_vertex_count(mods_from_arc):
    # TODO: see comment in _get_vertex_array_from_vertex_buffer assert
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.vertex_count == mod_exported.vertex_count


def test_mod156_import_export_face_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        # Expecting some differences in faces generated with the export algorithm
        difference = abs(mod_original.face_count - mod_exported.face_count)
        ratio = difference / mod_original.face_count
        assert ratio < EXPECTED_MAX_INDICES_COUNT_RATIO


@pytest.mark.xfail
def test_mod156_import_export_edge_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.edge_count == mod_exported.edge_count


def test_mod156_import_export_vertex_buffer_size(mods_from_arc):
    # TODO: see comment in _get_vertex_array_from_vertex_buffer
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert (mod_original.vertex_buffer_size - mod_exported.vertex_buffer_size) // 32 < EXPECTED_MAX_MISSING_VERTICES


def test_mod156_import_export_vertex_buffer_2_size(mods_from_arc):
    """Since uses saved mod data"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.vertex_buffer_2_size == mod_exported.vertex_buffer_2_size


def test_mod156_import_export_texture_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.texture_count == mod_exported.texture_count


def test_mod156_import_export_group_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.group_count == mod_exported.group_count


def test_mod156_import_export_bone_palettes_same_indices(mods_from_arc):
    """Bone palettes are exported using a greedy non optimized method, so
    the quantity so far differs, but it's equivalent. Here we only care that
    the exported bone palette has all the bone indices the original has"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        original = chain.from_iterable([bp.values[:] for bp in mod_original.bone_palette_array])
        exported = chain.from_iterable([bp.values[:] for bp in mod_exported.bone_palette_array])
        assert set(original) == set(exported)


def _assert_offsets(mod_original, mod_exported, offset_attr_name, attr_name):
        assert getattr(mod_original, offset_attr_name) == get_offset(mod_original, attr_name)
        assert getattr(mod_exported, offset_attr_name) == get_offset(mod_exported, attr_name)


def test_mod156_import_export_bones_array_offset(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'bones_array_offset', 'bones_array')


def test_mod156_import_export_group_offset(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'group_offset', 'group_data_array')


def test_mod156_import_export_textures_array_offset(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'textures_array_offset', 'textures_array')


def test_mod156_import_export_meshes_array_offset(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'meshes_array_offset', 'meshes_array')


def test_mod156_import_export_vertex_buffer_offset(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'vertex_buffer_offset', 'vertex_buffer')


@pytest.mark.xfail
def test_mod156_import_export_vertex_buffer_2_offset(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'vertex_buffer_2_offset', 'vertex_2_buffer')


def test_mod156_import_export_index_buffer_offset(mods_from_arc):
    '''Fails since vertex_buffer_2 is not included'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        _assert_offsets(mod_original, mod_exported, 'index_buffer_offset', 'index_buffer')


def test_mod156_import_export_reserved_01(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.reserved_01 == mod_exported.reserved_01


def test_mod156_import_export_reserved_02(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.reserved_02 == mod_exported.reserved_02


def test_mod156_import_export_sphere_x(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.sphere_x, mod_exported.sphere_x)


def test_mod156_import_export_sphere_y(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.sphere_y, mod_exported.sphere_y)


def test_mod156_import_export_z(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.sphere_z, mod_exported.sphere_z)


def test_mod156_import_export_sphere_w(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.sphere_w, mod_exported.sphere_w)


def test_mod156_import_export_box_min_x(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_min_x, mod_exported.box_min_x)


def test_mod156_import_export_box_min_y(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_min_y, mod_exported.box_min_y)


def test_mod156_import_export_box_min_z(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_min_z, mod_exported.box_min_z)


def test_mod156_import_export_box_min_w(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_min_w, mod_exported.box_min_w)


def test_mod156_import_export_box_max_x(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_max_x, mod_exported.box_max_x)


def test_mod156_import_export_box_max_y(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_max_y, mod_exported.box_max_y)


def test_mod156_import_export_box_max_z(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_max_z, mod_exported.box_max_z)


def test_mod156_import_export_box_max_w(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert is_close(mod_original.box_max_w, mod_exported.box_max_w)


def test_mod156_import_export_box_unk_01(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_01 == mod_exported.unk_01


def test_mod156_import_export_box_unk_02(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_02 == mod_exported.unk_02


def test_mod156_import_export_box_unk_03(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_03 == mod_exported.unk_03


def test_mod156_import_export_box_unk_04(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_04 == mod_exported.unk_04


def test_mod156_import_export_box_unk_05(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_05 == mod_exported.unk_05


def test_mod156_import_export_box_unk_06(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_06 == mod_exported.unk_06


def test_mod156_import_export_box_unk_07(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_07 == mod_exported.unk_07


def test_mod156_import_export_box_unk_08(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_08 == mod_exported.unk_08


def test_mod156_import_export_box_unk_09(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_09 == mod_exported.unk_09


def test_mod156_import_export_box_unk_10(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_10 == mod_exported.unk_10


def test_mod156_import_export_box_unk_11(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.unk_11 == mod_exported.unk_11


def test_mod156_import_export_reserverd_03(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert mod_original.reserved_03 == mod_exported.reserved_03


def test_mod156_import_export_box_unk_12(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert bytes(mod_original.unk_12) == bytes(mod_exported.unk_12)


def test_mod156_import_export_bones_array(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert bytes(mod_original.bones_array) == bytes(mod_exported.bones_array)


def test_mod156_import_export_bones_unk_matrix_array(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert bytes(mod_original.bones_unk_matrix_array) == bytes(mod_exported.bones_unk_matrix_array)


def test_mod156_import_export_bones_world_transform_matrix_array(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert (bytes(mod_original.bones_world_transform_matrix_array) ==
                bytes(mod_exported.bones_world_transform_matrix_array))


def test_mod156_import_export_unk_13(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert bytes(mod_original.unk_13) == bytes(mod_exported.unk_13)


def test_mod156_import_export_textures_array(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        textures_original = {t[:] for t in mod_original.textures_array}
        textures_exported = {t[:] for t in mod_exported.textures_array}

        assert textures_original == textures_exported


def test_mod156_import_export_materials_data_array_length(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert len(mod_original.materials_data_array) == len(mod_exported.materials_data_array)


def test_mod156_import_export_materials_data_array_texture_paths(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        texture_paths_from_materials_original = {mod_original.textures_array[ti - 1][:]
                                                 for md in mod_original.materials_data_array
                                                 for ti in md.texture_indices}

        texture_paths_from_materials_exported = {mod_exported.textures_array[ti - 1][:]
                                                 for md in mod_exported.materials_data_array
                                                 for ti in md.texture_indices}
        assert texture_paths_from_materials_original == texture_paths_from_materials_exported


@pytest.mark.xfail(reason='Materials exported are hardcoded for now')
def test_mod156_import_export_materials_data_array_values(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, material_original in enumerate(mod_original.materials_data_array):
            material_exported = mod_exported.materials_data_array[i]
            assert material_original.unk_01 == material_exported.unk_01
            assert material_original.unk_02 == material_exported.unk_02
            assert material_original.unk_03 == material_exported.unk_03
            assert material_original.unk_04 == material_exported.unk_04
            assert material_original.unk_05 == material_exported.unk_05
            assert material_original.unk_06 == material_exported.unk_06
            assert material_original.unk_07[:] == material_exported.unk_07[:]


def test_mod156_import_export_meshes_array_length(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert len(mod_original.meshes_array) == len(mod_exported.meshes_array)


def test_mod156_import_export_meshes_array_group_index(mods_from_arc):
    """Mesh attribute is exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.group_index == 0


def test_mod156_import_export_meshes_array_material_index(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.material_index == mesh_exported.material_index


def test_mod156_import_export_meshes_array_level_of_detail(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.level_of_detail == mesh_exported.level_of_detail


def test_mod156_import_export_meshes_array_unk_01(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            mesh_exported.unk_01 == 0


@pytest.mark.xfail(reason="Need to figure out how to export vertex format in all cases")
def test_mod156_import_export_meshes_array_vertex_format(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_format == mesh_exported.vertex_format


def test_mod156_import_export_meshes_array_vertex_stride(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_stride == mesh_exported.vertex_stride


def test_mod156_import_export_meshes_array_unk_02(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_02 == 0


def test_mod156_import_export_meshes_array_unk_03(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_03 == 0


def test_mod156_import_export_meshes_array_unk_04(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_04 == 0


@pytest.mark.xfail(reason="Won't match in meshes that use index_start_1")
def test_mod156_import_export_meshes_array_vertex_count(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_count == mesh_exported.vertex_count


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_vertex_index_end(mods_from_arc):
    '''Won't match since no grouping is applied'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_index_end == mesh_exported.vertex_index_end


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_vertex_index_start_1(mods_from_arc):
    '''Won't match since no grouping is applied'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_index_start_1 == mesh_exported.vertex_index_start_1


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_vertex_offset(mods_from_arc):
    '''Won't match since no grouping is applied'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_offset == mesh_exported.vertex_offset


def test_mod156_import_export_meshes_array_unk_05(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_05 == 0


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_face_position(mods_from_arc):
    '''Won't match since no grouping is applied, plus triangle strip numbers could vary'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.face_position == mesh_exported.face_position


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_face_count(mods_from_arc):
    '''Won't match since triangle strip numbers could vary'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.face_count == mesh_exported.face_count


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_face_offset(mods_from_arc):
    '''Won't match since no grouping is applied, plus triangle strip numbers could vary'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.face_offset == mesh_exported.face_offset


def test_mod156_import_export_meshes_array_unk_06(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_06 == 0


def test_mod156_import_export_meshes_array_unk_07(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_07 == 0


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_vertex_index_start_22(mods_from_arc):
    '''Won't match since no grouping is applied'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_index_start_2 == mesh_exported.vertex_index_start_2


def test_mod156_import_export_meshes_array_vertex_group_count(mods_from_arc):
    """not sure if the attribute is 'vertex_group_count', but always exporting as 1"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.vertex_group_count == 1


@pytest.mark.xfail(reason="not necessary, because heuristics")
def test_mod156_import_export_meshes_bone_palette_index(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.unk_07 == mesh_exported.unk_07


def test_mod156_import_export_meshes_array_unk_08(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_08 == 0


def test_mod156_import_export_meshes_array_unk_09(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_09 == 0


def test_mod156_import_export_meshes_array_unk_10(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_10 == 0


def test_mod156_import_export_meshes_array_unk_11(mods_from_arc):
    """Exported as null"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_11 == 0


# TODO: test exported harcoded data maybe?
@pytest.mark.xfail(reason="using hardcoded data")
def test_mod156_import_export_meshes_array_2(mods_from_arc):
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert bytes(mod_original.meshes_array_2) == bytes(mod_exported.meshes_array_2)


def test_mod156_import_export_vertex_buffer_approximation(mods_from_arc):
    '''Is not expected that the buffer exported matches exactly the original,
    because of rounding errors and more, but right know especially since normals are to be added'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        seq = SequenceMatcher(None, bytes(mod_original.vertex_buffer), bytes(mod_exported.vertex_buffer))
        assert seq.quick_ratio() >= EXPECTED_VERTEX_BUFFER_RATIO


def test_mod156_import_export_vertex_buffer_2_approximation(mods_from_arc):
    """Since the export uses the saved mod data"""
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        assert bytes(mod_original.vertex_buffer_2) == bytes(mod_exported.vertex_buffer_2)


def test_mod156_import_export_index_buffer_approximation(mods_from_arc):
    '''Is not expected that the buffer exported matches exactly the original,
    because of rounding errors and more, but right know especially since normals are to be added'''
    for mod_original, mod_exported in zip(mods_from_arc[0], mods_from_arc[1]):
        seq = SequenceMatcher(None, bytes(mod_original), bytes(mod_exported))
        assert seq.quick_ratio() >= EXPECTED_INDEX_BUFFER_RATIO
