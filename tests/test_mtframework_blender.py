from difflib import SequenceMatcher
import os
import subprocess

import pytest

from albam.mtframework import (KNOWN_ARC_FAILS, KNOWN_ARC_BLENDER_CRASH, KNOWN_ARC_BLENDER_HANGS,
                               Mod156, Arc)

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')
EXPECTED_VERTEX_BUFFER_RATIO = 0.65
EXPECTED_INDEX_BUFFER_RATIO = 0.65
EXPECTED_MAX_MISSING_VERTICES = 4000   # this is actually depending on the size of the model
PYTHON_TEMPLATE = """
import os
import sys
sys.path.append('{project_dir}')

import bpy

from albam.mtframework.blender_import import import_arc
from albam.mtframework.blender_export import export_arc
try:
    import_arc('{import_arc_filepath}', '{import_unpack_dir}')
    imported_name = os.path.basename('{import_arc_filepath}')
    exported_arc = export_arc(bpy.data.objects[imported_name])
    with open('{export_arc_filepath}', 'wb') as w:
        w.write(exported_arc)
    bpy.ops.wm.save_as_mainfile(filepath='{blend_file}')
except Exception as err:
    print(err)
    sys.exit(1)
"""


def is_close(a, b):
    return abs(a) - abs(b) < 0.001


@pytest.fixture(scope='session')
def arc_re5_samples(config=None):
    samples_dir = pytest.config.getoption('--dirarc') or os.path.join(SAMPLES_DIR, 're5/arc')
    return [os.path.join(root, f)
            for root, _, files in os.walk(samples_dir)
            for f in files if f.endswith('.arc')]


@pytest.fixture(scope='module', params=arc_re5_samples())
def mods_import_export(request, tmpdir_factory):
    blender = pytest.config.getoption('blender')
    if not blender:
        pytest.skip('No blender bin path supplied')

    import_arc_filepath = request.param
    arc_file_name = os.path.basename(import_arc_filepath).replace('.arc', '-arc')
    base_temp = tmpdir_factory.mktemp(arc_file_name)
    export_arc_filepath = os.path.join(str(base_temp), os.path.basename(import_arc_filepath) + 'exported')

    if import_arc_filepath.endswith(KNOWN_ARC_FAILS):
        pytest.xfail(reason='Malformed arc from the game')
    elif import_arc_filepath.endswith(KNOWN_ARC_BLENDER_CRASH):
        pytest.xfail(reason='Crash/segfault in blender: bug ALB-04')
    elif import_arc_filepath.endswith(KNOWN_ARC_BLENDER_HANGS):
        pytest.xfail(reason='Memory corruption in blender: bug ALB-04')
    elif import_arc_filepath.endswith('uPl03WeskerCos1.arc'):
        pytest.xfail(reason='Multiple mods export not supported yet')
    elif import_arc_filepath.endswith(('uPl02JillCos1.arc', 'uPl02JillCos4.arc')):
        pytest.xfail(reason='Strip triangles exported wrongly')
    elif import_arc_filepath.endswith('uPl01ShebaCos4.arc'):
        pytest.xfail(reason='Division by zero on bounding box')

    python_script_file_path = str(base_temp.join('test-script.py'))
    import_unpack_dir = str(base_temp.mkdir('import_unpack'))
    export_unpack_dir = str(base_temp.mkdir('export_unpack'))
    export_arc_filepath = os.path.join(str(base_temp), os.path.basename(import_arc_filepath)
                                       .replace('.arc', '-exported.arc'))
    # assuming that tests are run from the root project
    blend_file = str(base_temp.join(arc_file_name + '.blend'))
    project_dir = os.getcwd()

    python_script = PYTHON_TEMPLATE.format(project_dir=project_dir,
                                           import_arc_filepath=import_arc_filepath,
                                           export_arc_filepath=export_arc_filepath,
                                           import_unpack_dir=import_unpack_dir,
                                           export_unpack_dir=export_unpack_dir,
                                           blend_file=blend_file)

    with open(python_script_file_path, 'w') as w:
        w.write(python_script)

    args = '{} --background --python {}'.format(blender, python_script_file_path)
    try:
        subprocess.check_output((args,), shell=True)
    except subprocess.CalledProcessError as err:
        print(err.output)
        raise

    arc = Arc(export_arc_filepath)
    arc.unpack(export_unpack_dir)

    mod_files_original = [os.path.join(root, f) for root, _, files in os.walk(import_unpack_dir)
                          for f in files if f.endswith('.mod')]

    mod_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_unpack_dir)
                          for f in files if f.endswith('.mod')]

    mod_files_original = sorted(mod_files_original, key=os.path.basename)
    mod_files_exported = sorted(mod_files_exported, key=os.path.basename)

    return Mod156(file_path=mod_files_original[0]), Mod156(file_path=mod_files_exported[0])


def test_mod156_import_export_export_id_magic(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.id_magic == mod_exported.id_magic


def test_mod156_import_export_version(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.version == mod_exported.version


def test_mod156_import_export_version_rev(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.version_rev == mod_exported.version_rev


def test_mod156_import_export_bone_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.bone_count == mod_exported.bone_count


def test_mod156_import_export_mesh_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.mesh_count == mod_exported.mesh_count


def test_mod156_import_export_material_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.material_count == mod_exported.material_count


def test_mod156_import_export_vertex_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    # TODO: see comment in _get_vertex_array_from_vertex_buffer assert
    mod_original.vertex_count == mod_exported.vertex_count


def test_mod156_import_export_face_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    # Expecting some differences in faces generated with the export algorithm
    EXPECTED_AVERAGE_EXTRA_INDICES = 20
    assert (abs(mod_original.face_count - mod_exported.face_count) <
            mod_original.mesh_count * EXPECTED_AVERAGE_EXTRA_INDICES)


@pytest.mark.xfail
def test_mod156_import_export_edge_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.edge_count == mod_exported.edge_count


def test_mod156_import_export_vertex_buffer_size(mods_import_export):
    mod_original, mod_exported = mods_import_export
    # TODO: see comment in _get_vertex_array_from_vertex_buffer
    assert (mod_original.vertex_buffer_size - mod_exported.vertex_buffer_size) // 32 < EXPECTED_MAX_MISSING_VERTICES


@pytest.mark.xfail
def test_mod156_import_export_vertex_buffer_2_size(mods_import_export):
    mod_original, mod_exported = mods_import_export
    # TODO: see comment in _get_vertex_array_from_vertex_buffer
    assert mod_original.vertex_buffer_2_size == mod_exported.vertex_buffer_2_size


def test_mod156_import_export_texture_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.texture_count == mod_exported.texture_count


def test_mod156_import_export_group_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.group_count == mod_exported.group_count


def test_mod156_import_export_bone_palette_count(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.bone_palette_count == mod_exported.bone_palette_count


def test_mod156_import_export_bones_array_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.bones_array_offset == mod_exported.bones_array_offset


def test_mod156_import_export_group_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.group_offset == mod_exported.group_offset


def test_mod156_import_export_textures_array_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.textures_array_offset == mod_exported.textures_array_offset


def test_mod156_import_export_meshes_array_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.meshes_array_offset == mod_exported.meshes_array_offset


def test_mod156_import_export_vertex_buffer_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.vertex_buffer_offset == mod_exported.vertex_buffer_offset


@pytest.mark.xfail
def test_mod156_import_export_vertex_buffer_2_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.vertex_buffer_2_offset == mod_exported.vertex_buffer_2_offset


@pytest.mark.xfail
def test_mod156_import_export_index_buffer_offset(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.index_buffer_offset == mod_exported.index_buffer_offset


def test_mod156_import_export_reserved_01(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.reserved_01 == mod_exported.reserved_01


def test_mod156_import_export_reserved_02(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.reserved_02 == mod_exported.reserved_02


def test_mod156_import_export_sphere_x(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.sphere_x, mod_exported.sphere_x)


def test_mod156_import_export_sphere_y(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.sphere_y, mod_exported.sphere_y)


def test_mod156_import_export_z(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.sphere_z, mod_exported.sphere_z)


def test_mod156_import_export_sphere_w(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.sphere_w, mod_exported.sphere_w)


def test_mod156_import_export_box_min_x(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_min_x, mod_exported.box_min_x)


def test_mod156_import_export_box_min_y(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_min_y, mod_exported.box_min_y)


def test_mod156_import_export_box_min_z(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_min_z, mod_exported.box_min_z)


def test_mod156_import_export_box_min_w(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_min_w, mod_exported.box_min_w)


def test_mod156_import_export_box_max_x(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_max_x, mod_exported.box_max_x)


def test_mod156_import_export_box_max_y(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_max_y, mod_exported.box_max_y)


def test_mod156_import_export_box_max_z(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_max_z, mod_exported.box_max_z)


def test_mod156_import_export_box_max_w(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert is_close(mod_original.box_max_w, mod_exported.box_max_w)


def test_mod156_import_export_box_unk_01(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_01 == mod_exported.unk_01


def test_mod156_import_export_box_unk_02(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_02 == mod_exported.unk_02


def test_mod156_import_export_box_unk_03(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_03 == mod_exported.unk_03


def test_mod156_import_export_box_unk_04(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_04 == mod_exported.unk_04


def test_mod156_import_export_box_unk_05(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_05 == mod_exported.unk_05


def test_mod156_import_export_box_unk_06(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_06 == mod_exported.unk_06


def test_mod156_import_export_box_unk_07(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_07 == mod_exported.unk_07


def test_mod156_import_export_box_unk_08(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_08 == mod_exported.unk_08


def test_mod156_import_export_box_unk_09(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_09 == mod_exported.unk_09


def test_mod156_import_export_box_unk_10(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_10 == mod_exported.unk_10


def test_mod156_import_export_box_unk_11(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.unk_11 == mod_exported.unk_11


def test_mod156_import_export_reserverd_03(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert mod_original.reserved_03 == mod_exported.reserved_03


def test_mod156_import_export_box_unk_12(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.unk_12) == bytes(mod_exported.unk_12)


def test_mod156_import_export_bones_array(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.bones_array) == bytes(mod_exported.bones_array)


def test_mod156_import_export_bones_unk_matrix_array(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.bones_unk_matrix_array) == bytes(mod_exported.bones_unk_matrix_array)


def test_mod156_import_export_bones_world_transform_matrix_array(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert (bytes(mod_original.bones_world_transform_matrix_array) ==
            bytes(mod_exported.bones_world_transform_matrix_array))


def test_mod156_import_export_unk_13(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.unk_13) == bytes(mod_exported.unk_13)


def test_mod156_import_export_bone_palette_array(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.bone_palette_array) == bytes(mod_exported.bone_palette_array)


def test_mod156_import_export_textures_array(mods_import_export):
    mod_original, mod_exported = mods_import_export
    textures_original = {t[:] for t in mod_original.textures_array}
    textures_exported = {t[:] for t in mod_exported.textures_array}

    assert textures_original == textures_exported


def test_mod156_import_export_materials_data_array_length(mods_import_export):
    mod_original, mod_exported = mods_import_export

    assert len(mod_original.materials_data_array) == len(mod_exported.materials_data_array)


def test_mod156_import_export_materials_data_array_texture_paths(mods_import_export):
    mod_original, mod_exported = mods_import_export
    texture_paths_from_materials_original = {mod_original.textures_array[ti - 1][:]
                                             for md in mod_original.materials_data_array for ti in md.texture_indices}

    texture_paths_from_materials_exported = {mod_exported.textures_array[ti - 1][:]
                                             for md in mod_exported.materials_data_array for ti in md.texture_indices}
    assert texture_paths_from_materials_original == texture_paths_from_materials_exported


def test_mod156_import_export_meshes_array_length(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert len(mod_original.meshes_array) == len(mod_exported.meshes_array)


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_2(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.meshes_array_2) == bytes(mod_exported.meshes_array)


@pytest.mark.xfail
def test_mod156_import_export_vertex_buffer(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.vertex_buffer) == bytes(mod_exported.vertex_buffer)


def test_mod156_import_export_vertex_buffer_approximation(mods_import_export):
    mod_original, mod_exported = mods_import_export
    seq = SequenceMatcher(None, bytes(mod_original.vertex_buffer), bytes(mod_exported.vertex_buffer))

    assert seq.quick_ratio() >= EXPECTED_VERTEX_BUFFER_RATIO


@pytest.mark.xfail
def test_mod156_import_export_vertex_buffer_2(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.vertex_buffer_2) == bytes(mod_exported.vertex_buffer_2)


@pytest.mark.xfail
def test_mod156_import_export_index_buffer(mods_import_export):
    mod_original, mod_exported = mods_import_export
    assert bytes(mod_original.index_buffer) == bytes(mod_exported.index_buffer)


def test_mod156_import_export_index_buffer_approximation(mods_import_export):
    mod_original, mod_exported = mods_import_export
    seq = SequenceMatcher(None, bytes(mod_original), bytes(mod_exported))

    assert seq.quick_ratio() >= EXPECTED_INDEX_BUFFER_RATIO
