from collections import namedtuple
from difflib import SequenceMatcher
from itertools import chain
import os
import subprocess
from tempfile import TemporaryDirectory, gettempdir

import pytest

from albam.mtframework import Mod156, Arc, KNOWN_ARC_BLENDER_CRASH, Tex112
from albam.utils import get_offset
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

from albam import register

logging.basicConfig(filename='{log_filepath}', level=logging.DEBUG)
logging.debug('Importing {import_arc_filepath}')

try:
    register()
except ValueError:  # The addon is already installed in blender.
    pass

try:
    start = time.time()
    logging.debug('Importing {import_arc_filepath}')

    file_path = '{import_arc_filepath}'
    bpy.ops.albam_import.item(files=[{{'name': file_path}}], unpack_dir='{import_unpack_dir}')

    logging.debug('Import time: {{}} seconds [{import_arc_filepath}])'.format(round(time.time() - start, 2)))
except Exception:
    logging.exception('IMPORT failed: {import_arc_filepath}')
    sys.exit(1)
time.sleep(4)
try:
    imported_name = os.path.basename('{import_arc_filepath}')
    start = time.time()
    bpy.context.scene.albam_item_to_export = imported_name
    bpy.ops.albam_export.item(filepath='{export_arc_filepath}')
    logging.debug('Export time: {{}} seconds [{import_arc_filepath}]'.format(round(time.time() - start, 2)))
except Exception:
    logging.exception('EXPORT failed: {import_arc_filepath}')
    sys.exit(1)
"""


def is_close(a, b):
    return abs(a) - abs(b) < 0.001

UnpackedData = namedtuple('UnpackedData', ('mods_original', 'textures_original',
                                           'mods_exported', 'textures_exported'))


@pytest.fixture(scope='module', params=arc_re5_samples())
def unpacked_data(request, tmpdir_factory):
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
                print(line)
        try:
            os.unlink(export_arc_filepath)
            os.unlink(script_filepath)
        except FileNotFoundError:
            pass
        raise

    export_unpack_dir = TemporaryDirectory()
    arc = Arc(export_arc_filepath)
    arc.unpack(export_unpack_dir.name)

    mod_files_original = [os.path.join(root, f) for root, _, files in os.walk(import_unpack_dir.name)
                          for f in files if f.endswith('.mod')]
    mod_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_unpack_dir.name)
                          for f in files if f.endswith('.mod')]

    tex_files_original = [os.path.join(root, f) for root, _, files in os.walk(import_unpack_dir.name)
                          for f in files if f.endswith('.tex')]

    tex_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_unpack_dir.name)
                          for f in files if f.endswith('.tex')]

    mod_files_original = sorted(mod_files_original, key=os.path.basename)
    mod_files_exported = sorted(mod_files_exported, key=os.path.basename)
    tex_files_original = sorted(tex_files_original, key=os.path.basename)
    tex_files_exported = sorted(tex_files_exported, key=os.path.basename)
    tex_files_original = [Tex112(fp) for fp in tex_files_original]
    tex_files_exported = [Tex112(fp) for fp in tex_files_exported]
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
    return UnpackedData(mods_original=mod_objects_original,
                        mods_exported=mod_objects_exported,
                        textures_original=tex_files_original,
                        textures_exported=tex_files_exported)


def test_mod156_import_export_export_id_magic(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.id_magic == mod_exported.id_magic


def test_mod156_import_export_version(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.version == mod_exported.version


def test_mod156_import_export_version_rev(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.version_rev == mod_exported.version_rev


def test_mod156_import_export_bone_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.bone_count == mod_exported.bone_count


def test_mod156_import_export_mesh_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.mesh_count == mod_exported.mesh_count


def test_mod156_import_export_material_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.material_count == mod_exported.material_count


def test_mod156_import_export_vertex_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.vertex_count - mod_exported.vertex_count < EXPECTED_MAX_MISSING_VERTICES


def test_mod156_import_export_face_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        # Expecting some differences in faces generated with the export algorithm
        difference = abs(mod_original.face_count - mod_exported.face_count)
        ratio = difference / mod_original.face_count
        assert ratio < EXPECTED_MAX_INDICES_COUNT_RATIO


@pytest.mark.xfail
def test_mod156_import_export_edge_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.edge_count == mod_exported.edge_count


def test_mod156_import_export_vertex_buffer_size(unpacked_data):
    # TODO: see comment in _get_vertex_array_from_vertex_buffer
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert (mod_original.vertex_buffer_size - mod_exported.vertex_buffer_size) // 32 < EXPECTED_MAX_MISSING_VERTICES


def test_mod156_import_export_vertex_buffer_2_size(unpacked_data):
    """Since uses saved mod data"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.vertex_buffer_2_size == mod_exported.vertex_buffer_2_size


def test_mod156_import_export_texture_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.texture_count == mod_exported.texture_count


def test_mod156_import_export_group_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.group_count == mod_exported.group_count


def test_mod156_import_export_bone_palettes_same_indices(unpacked_data):
    """Bone palettes are exported using a greedy non optimized method, so
    the quantity so far differs, but it's equivalent. Here we only care that
    the exported bone palette has all the bone indices the original has"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        original = chain.from_iterable([bp.values[:] for bp in mod_original.bone_palette_array])
        exported = chain.from_iterable([bp.values[:] for bp in mod_exported.bone_palette_array])
        assert set(original) == set(exported)


def _assert_offsets(mod_original, mod_exported, offset_attr_name, attr_name):
        assert getattr(mod_original, offset_attr_name) in (0, get_offset(mod_original, attr_name))
        assert getattr(mod_exported, offset_attr_name) in (0, get_offset(mod_exported, attr_name))


def test_mod156_import_export_bones_array_offset(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'bones_array_offset', 'bones_array')


def test_mod156_import_export_group_offset(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'group_offset', 'group_data_array')


def test_mod156_import_export_textures_array_offset(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'textures_array_offset', 'textures_array')


def test_mod156_import_export_meshes_array_offset(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'meshes_array_offset', 'meshes_array')


def test_mod156_import_export_vertex_buffer_offset(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'vertex_buffer_offset', 'vertex_buffer')


def test_mod156_import_export_vertex_buffer_2_offset(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'vertex_buffer_2_offset', 'vertex_buffer_2')


def test_mod156_import_export_index_buffer_offset(unpacked_data):
    '''Fails since vertex_buffer_2 is not included'''
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'index_buffer_offset', 'index_buffer')


def test_mod156_import_export_reserved_01(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.reserved_01 == mod_exported.reserved_01


def test_mod156_import_export_reserved_02(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.reserved_02 == mod_exported.reserved_02


def test_mod156_import_export_sphere_x(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_x, mod_exported.sphere_x)


def test_mod156_import_export_sphere_y(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_y, mod_exported.sphere_y)


def test_mod156_import_export_z(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_z, mod_exported.sphere_z)


def test_mod156_import_export_sphere_w(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_w, mod_exported.sphere_w)


def test_mod156_import_export_box_min_x(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_min_x, mod_exported.box_min_x)


def test_mod156_import_export_box_min_y(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_min_y, mod_exported.box_min_y)


def test_mod156_import_export_box_min_z(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_min_z, mod_exported.box_min_z)


def test_mod156_import_export_box_min_w(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_min_w, mod_exported.box_min_w)


def test_mod156_import_export_box_max_x(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_max_x, mod_exported.box_max_x)


def test_mod156_import_export_box_max_y(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_max_y, mod_exported.box_max_y)


def test_mod156_import_export_box_max_z(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_max_z, mod_exported.box_max_z)


def test_mod156_import_export_box_max_w(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert is_close(mod_original.box_max_w, mod_exported.box_max_w)


def test_mod156_import_export_box_unk_01(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_01 == mod_exported.unk_01


def test_mod156_import_export_box_unk_02(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_02 == mod_exported.unk_02


def test_mod156_import_export_box_unk_03(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_03 == mod_exported.unk_03


def test_mod156_import_export_box_unk_04(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_04 == mod_exported.unk_04


def test_mod156_import_export_box_unk_05(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_05 == mod_exported.unk_05


def test_mod156_import_export_box_unk_06(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_06 == mod_exported.unk_06


def test_mod156_import_export_box_unk_07(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_07 == mod_exported.unk_07


def test_mod156_import_export_box_unk_08(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_08 == mod_exported.unk_08


def test_mod156_import_export_box_unk_09(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_09 == mod_exported.unk_09


def test_mod156_import_export_box_unk_10(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_10 == mod_exported.unk_10


def test_mod156_import_export_box_unk_11(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.unk_11 == mod_exported.unk_11


def test_mod156_import_export_reserverd_03(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert mod_original.reserved_03 == mod_exported.reserved_03


def test_mod156_import_export_box_unk_12(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert bytes(mod_original.unk_12) == bytes(mod_exported.unk_12)


def test_mod156_import_export_bones_array(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert bytes(mod_original.bones_array) == bytes(mod_exported.bones_array)


def test_mod156_import_export_bones_unk_matrix_array(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert bytes(mod_original.bones_unk_matrix_array) == bytes(mod_exported.bones_unk_matrix_array)


def test_mod156_import_export_bones_world_transform_matrix_array(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert (bytes(mod_original.bones_world_transform_matrix_array) ==
                bytes(mod_exported.bones_world_transform_matrix_array))


def test_mod156_import_export_unk_13(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert bytes(mod_original.unk_13) == bytes(mod_exported.unk_13)


def test_mod156_import_export_textures_array(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        textures_original = {t[:] for t in mod_original.textures_array}
        textures_exported = {t[:] for t in mod_exported.textures_array}

        assert textures_original == textures_exported


def test_mod156_import_export_materials_data_array_length(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert len(mod_original.materials_data_array) == len(mod_exported.materials_data_array)


def test_mod156_import_export_materials_data_array_texture_paths(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        texture_paths_from_materials_original = {mod_original.textures_array[ti - 1][:]
                                                 for md in mod_original.materials_data_array
                                                 for ti in md.texture_indices}

        texture_paths_from_materials_exported = {mod_exported.textures_array[ti - 1][:]
                                                 for md in mod_exported.materials_data_array
                                                 for ti in md.texture_indices}
        assert texture_paths_from_materials_original == texture_paths_from_materials_exported


def test_mod156_import_export_materials_data_array_values(unpacked_data):
    print()
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, material_original in enumerate(mod_original.materials_data_array):
            material_exported = mod_exported.materials_data_array[i]
            for unk_index in range(1, 38):
                attr_name = 'unk_{}'.format(str(unk_index).zfill(2))
                assert getattr(material_original, attr_name) == getattr(material_exported, attr_name)
            assert material_original.texture_indices[:] == material_exported.texture_indices[:]

            # getting texture paths from texture_indices
            for tex_code, tex_index in enumerate(material_original.texture_indices):
                if not tex_index:
                    continue
                exported_tex_index = material_exported.texture_indices[tex_code]
                tex_path_original = mod_original.textures_array[tex_index - 1][:]
                tex_path_exported = mod_exported.textures_array[exported_tex_index - 1][:]
                assert tex_path_original == tex_path_exported


def test_mod156_import_export_meshes_array_length(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert len(mod_original.meshes_array) == len(mod_exported.meshes_array)


def test_mod156_import_export_meshes_array_group_index(unpacked_data):
    """Mesh attribute is exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.group_index == 0


def test_mod156_import_export_meshes_array_material_index(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.material_index == mesh_exported.material_index


def test_mod156_import_export_meshes_array_level_of_detail(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.level_of_detail == mesh_exported.level_of_detail


def test_mod156_import_export_meshes_array_unk_01(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            mesh_exported.unk_01 == 0


@pytest.mark.xfail(reason="Need to figure out how to export vertex format in all cases")
def test_mod156_import_export_meshes_array_vertex_format(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_format == mesh_exported.vertex_format


def test_mod156_import_export_meshes_array_vertex_stride(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_stride == mesh_exported.vertex_stride


def test_mod156_import_export_meshes_array_unk_02(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_02 == 0


def test_mod156_import_export_meshes_array_unk_03(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_03 == 0


def test_mod156_import_export_meshes_array_unk_04(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_04 == 0


@pytest.mark.xfail(reason="Won't match in meshes that use index_start_1")
def test_mod156_import_export_meshes_array_vertex_count(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_count == mesh_exported.vertex_count


def test_mod156_import_export_meshes_array_unk_05(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_05 == 0


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_face_count(unpacked_data):
    '''Won't match since triangle strip numbers could vary'''
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.face_count == mesh_exported.face_count


def test_mod156_import_export_meshes_array_unk_06(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_06 == 0


def test_mod156_import_export_meshes_array_unk_07(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_07 == 0


def test_mod156_import_export_meshes_array_vertex_group_count(unpacked_data):
    """not sure if the attribute is 'vertex_group_count', but always exporting as 1"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.vertex_group_count == 1


@pytest.mark.xfail(reason="not necessary, because heuristics")
def test_mod156_import_export_meshes_bone_palette_index(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.unk_07 == mesh_exported.unk_07


def test_mod156_import_export_meshes_array_unk_08(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_08 == 0


def test_mod156_import_export_meshes_array_unk_09(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_09 == 0


def test_mod156_import_export_meshes_array_unk_10(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_10 == 0


def test_mod156_import_export_meshes_array_unk_11(unpacked_data):
    """Exported as null"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.unk_11 == 0


# TODO: test exported harcoded data maybe?
@pytest.mark.xfail(reason="using hardcoded data")
def test_mod156_import_export_meshes_array_2(unpacked_data):
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert bytes(mod_original.meshes_array_2) == bytes(mod_exported.meshes_array_2)


def test_mod156_import_export_vertex_buffer_approximation(unpacked_data):
    '''Is not expected that the buffer exported matches exactly the original,
    because of rounding errors and more, but right know especially since normals are to be added'''
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        seq = SequenceMatcher(None, bytes(mod_original.vertex_buffer), bytes(mod_exported.vertex_buffer))
        assert seq.quick_ratio() >= EXPECTED_VERTEX_BUFFER_RATIO


def test_mod156_import_export_vertex_buffer_2_approximation(unpacked_data):
    """Since the export uses the saved mod data"""
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        assert bytes(mod_original.vertex_buffer_2) == bytes(mod_exported.vertex_buffer_2)


def test_mod156_import_export_index_buffer_approximation(unpacked_data):
    '''Is not expected that the buffer exported matches exactly the original,
    because of rounding errors and more, but right know especially since normals are to be added'''
    for mod_original, mod_exported in zip(unpacked_data.mods_original, unpacked_data.mods_exported):
        seq = SequenceMatcher(None, bytes(mod_original), bytes(mod_exported))
        assert seq.quick_ratio() >= EXPECTED_INDEX_BUFFER_RATIO


def test_mod156_exported_textures_count(unpacked_data):
    assert len(unpacked_data.textures_original) == len(unpacked_data.textures_exported)


# TODO: revision is not always 34
@pytest.mark.parametrize('attr_name', ('id_magic', 'version', 'mipmap_count',
                                       'unk_byte_1', 'unk_byte_2', 'unk_byte_3',
                                       'width', 'height', 'reserved_1', 'compression_format',
                                       'unk_float_1', 'unk_float_2', 'unk_float_3', 'unk_float_4'))
def test_mod156_exported_textures_attributes(unpacked_data, attr_name):
    for tex_original, tex_exported in zip(unpacked_data.textures_original, unpacked_data.textures_exported):
        if 'effect' in tex_original._file_path:
            continue
        assert getattr(tex_original, attr_name) == getattr(tex_exported, attr_name)
