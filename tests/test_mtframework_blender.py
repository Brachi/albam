import ntpath
import os
import subprocess

import pytest

from albam.mtframework.blender import (
    _get_vertex_array_from_vertex_buffer,
    _get_indices_array,
    _import_vertices,
    _vertices_export_locations,
    _vertices_import_locations,
)
from albam.mtframework import Mod156
from albam.utils import strip_triangles_to_triangles_list, chunks
from albam.mtframework import KNOWN_ARC_FAILS, KNOWN_ARC_BLENDER_CRASH, KNOWN_ARC_BLENDER_HANGS
from tests.conftest import arc_re5_samples, mod_re5_samples


@pytest.mark.parametrize('mod_file', mod_re5_samples())
def test_vertex_functions(mod_file):
    mod = Mod156(file_path=mod_file)
    box_width = abs(mod.box_min_x) + abs(mod.box_max_x)
    box_height = abs(mod.box_min_y) + abs(mod.box_max_y)
    box_length = abs(mod.box_min_z) + abs(mod.box_max_z)

    for mesh in mod.meshes_array:
        vertices_array = _get_vertex_array_from_vertex_buffer(mod, mesh)
        for vf in vertices_array:
            original = (vf.position_x, vf.position_y, vf.position_z)
            imported = _vertices_import_locations(vf, box_width, box_height, box_length)
            exported = _vertices_export_locations(imported, box_width, box_height, box_length)
            assert exported == original

        indices_array = _get_indices_array(mod, mesh)
        imported_vertices = _import_vertices(mod, mesh)
        triangles_list = strip_triangles_to_triangles_list(indices_array)
        assert imported_vertices
        assert triangles_list


@pytest.mark.skipif(not pytest.config.getoption('blender'), reason='no path to blender executable')
@pytest.mark.parametrize('arc_file', arc_re5_samples())
def test_arc_import_mod_export(arc_file, tmpdir):
    """
    Functional test that should be splitted once the code is finished
    """
    if arc_file.endswith(KNOWN_ARC_FAILS):
        pytest.xfail(reason='Malformed arc from the game')
    elif arc_file.endswith(KNOWN_ARC_BLENDER_CRASH):
        pytest.xfail(reason='Crash/segfault in blender: bug ALB-04')
    elif arc_file.endswith(KNOWN_ARC_BLENDER_HANGS):
        pytest.xfail(reason='Memory corruption in blender: bug ALB-04')
    elif arc_file.endswith('uPl03WeskerCos1.arc'):
        pytest.xfail(reason='Multiple mods export not supported yet')
    elif arc_file.endswith(('uPl02JillCos1.arc', 'uPl02JillCos4.arc')):
        pytest.xfail(reason='Strip triangles exported wrongly')
    elif arc_file.endswith('uPl01ShebaCos4.arc'):
        pytest.xfail(reason='Division by zero on bounding box')
    blender = pytest.config.getoption('blender')
    out = os.path.join(str(tmpdir), 'test-script.py')
    export_dir = os.path.join(str(tmpdir), 'albam_exported')
    extract_dir = os.path.join(str(tmpdir), 'albam_extracted')
    os.mkdir(export_dir)
    os.mkdir(extract_dir)
    # assuming that tests are run from the root project
    project_dir = os.getcwd()
    python_expr = """
import os
import sys
sys.path.append('{project_dir}')

import bpy

from albam.mtframework.blender import import_arc, create_mod156, Tex112
try:
    import_arc('{arc_file}', '{extract_dir}')
    imported_name = os.path.basename('{arc_file}')
    parent_arc = bpy.data.objects[imported_name]
    for child in parent_arc.children:
        mod_name = child.name
        mod, textures = create_mod156(child)
        with open(os.path.join('{export_dir}', mod_name), 'wb') as w:
            w.write(mod)
        for texture in textures:
            tex = Tex112.from_dds(file_path=texture.image.filepath)
            with open(os.path.join('{export_dir}', texture.name), 'wb') as w:
                w.write(tex)
    bpy.ops.wm.save_as_mainfile(filepath='{filepath}')
except Exception as err:
    print(err)
    sys.exit(1)


""".format(project_dir=project_dir, arc_file=arc_file,
           filepath=os.path.join(str(tmpdir), os.path.basename(arc_file) + '.blend'),
           export_dir=export_dir, extract_dir=extract_dir)

    with open(out, 'w') as w:
        w.write(python_expr)
    args = '{} --background --python {}'.format(blender, out)
    try:
        subprocess.check_output((args,), shell=True)
    except subprocess.CalledProcessError as err:
        print(err.output)
        raise

    mod_files_original = [os.path.join(root, f) for root, _, files in os.walk(extract_dir)
                          for f in files if f.endswith('.mod') and not f.startswith('exported')]

    mod_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_dir)
                          for f in files if f.endswith('.mod')]

    mod_files_original = sorted(mod_files_original, key=os.path.basename)
    mod_files_exported = sorted(mod_files_exported, key=os.path.basename)

    assert len(mod_files_exported) == len(mod_files_original)

    for i, mod_file in enumerate(mod_files_original):
        mod_original = Mod156(mod_file)
        mod_exported = Mod156(mod_files_exported[i])

        assert mod_original.id_magic == mod_exported.id_magic
        assert mod_original.version == mod_exported.version
        assert mod_original.bone_count == mod_exported.bone_count
        assert mod_original.mesh_count == mod_exported.mesh_count
        assert mod_original.material_count == mod_exported.material_count
        # TODO: see comment in _get_vertex_array_from_vertex_buffer assert
        # mod_original.vertex_count == mod_exported.vertex_count
        # TODO: assert mod_original.edge_count == mod_exported.edge_count
        # Expecting some differences in faces generated with the export algorithm
        EXPECTED_AVERAGE_EXTRA_INDICES = 20
        assert abs(mod_original.face_count - mod_exported.face_count) < mod_original.mesh_count * EXPECTED_AVERAGE_EXTRA_INDICES
        # TODO: see comment in _get_vertex_array_from_vertex_buffer
        # assert mod_original.vertex_buffer_size  == mod_exported.vertex_buffer_size
        # TODO: assert mod_original.texture_count == mod_exported.texture_count
        # TODO: assert mod_original.group_count == mod_exported.group_count
        # TODO: assert mod_original.bone_palette_count == mod_exported.bone_palette_count
        # TODO: will fail in some assert mod_original.bones_array_offset == mod_exported.bones_array_offset
        # TODO: assert mod_original.group_offset == mod_exported.group_offset
        # TODO: assert mod_original.textures_array_offset  == mod_exported.textures_array_offset
        # TODO: implement isclose
        """
        assert mod_original.meshes_array_offset == mod_exported.meshes_array_offset
        assert mod_original.vertex_buffer_offset == mod_exported.vertex_buffer_offset
        assert mod_original.vertex_buffer_2_offset == mod_exported.vertex_buffer_2_offset
        assert mod_original.index_buffer_offset == mod_exported.index_buffer_offset
        assert mod_original.reserved_01 == mod_exported.reserved_01
        assert mod_original.reserved_02 == mod_exported.reserved_02
        assert mod_original.sphere_x == mod_exported.sphere_x
        assert mod_original.sphere_y == mod_exported.sphere_y
        assert mod_original.sphere_z == mod_exported.sphere_z
        assert mod_original.sphere_w == mod_exported.sphere_w
        assert mod_original.box_min_x == mod_exported.box_min_x
        assert mod_original.box_min_y == mod_exported.box_min_y
        assert mod_original.box_min_z == mod_exported.box_min_z
        assert mod_original.box_min_w == mod_exported.box_min_w
        assert mod_original.box_max_x == mod_exported.box_max_x
        assert mod_original.box_max_y == mod_exported.box_max_y
        assert mod_original.box_max_z == mod_exported.box_max_z
        assert mod_original.box_max_w == mod_exported.box_max_w
        """
        assert mod_original.reserved_03 == mod_exported.reserved_03
        assert bytes(mod_original.bone_palette_count) == bytes(mod_exported.bone_palette_count)
        assert bytes(mod_original.bones_array) == bytes(mod_exported.bones_array)
        assert bytes(mod_original.bones_unk_matrix_array) == bytes(mod_exported.bones_unk_matrix_array)
        assert bytes(mod_original.bones_world_transform_matrix_array) == bytes(mod_exported.bones_world_transform_matrix_array)
        assert bytes(mod_original.unk_13) == bytes(mod_exported.unk_13)
        assert bytes(mod_original.bone_palette_array) == bytes(mod_exported.bone_palette_array)

        # TODO: when folder definition is supported, take out the os.path.basename
        textures_original = {ntpath.basename(t[:]).rstrip(b'\x00') for t in mod_original.textures_array}
        textures_exported = {t[:].rstrip(b'\x00') for t in mod_exported.textures_array}
        assert textures_original == textures_exported
        assert len(mod_original.materials_data_array) == len(mod_exported.materials_data_array)
        assert len(mod_original.meshes_array) == len(mod_exported.meshes_array)
        assert len(mod_original.textures_array) == len(mod_exported.textures_array)


        texture_paths_from_materials_original = {ntpath.basename(mod_original.textures_array[ti - 1][:].rstrip(b'\x00'))
                                                 for md in mod_original.materials_data_array for ti in md.texture_indices}

        texture_paths_from_materials_exported = {ntpath.basename(mod_exported.textures_array[ti - 1][:].rstrip(b'\x00'))
                                                 for md in mod_exported.materials_data_array for ti in md.texture_indices}
        assert texture_paths_from_materials_original == texture_paths_from_materials_exported

        failed_uvs_all = {}
        for mesh_index, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[mesh_index]

            tri_strips_original = _get_indices_array(mod_original, mesh_original)
            tri_strips_exported = _get_indices_array(mod_exported, mesh_exported)

            # the indices array won't be exactly the same in all cases, since heuristics may
            # differ in the algorithm applied
            # The faces are sorted for a TODO in the list to strips function that changes
            # faces directions in some cases
            tri_list_original = strip_triangles_to_triangles_list(tri_strips_original)
            tri_list_original = chunks(tri_list_original, 3)
            tri_list_original = {tuple(sorted(indices)) for indices in tri_list_original}

            tri_list_exported = strip_triangles_to_triangles_list(tri_strips_exported)
            tri_list_exported = chunks(tri_list_exported, 3)
            tri_list_exported = {tuple(sorted(indices)) for indices in tri_list_exported}

            assert len(tri_list_original) == len(tri_list_exported)
            assert tri_list_original == tri_list_exported

            vertices_array_original = _get_vertex_array_from_vertex_buffer(mod_original, mesh_original)
            vertices_array_exported = _get_vertex_array_from_vertex_buffer(mod_exported, mesh_exported)

            # This whole ugly loop could be replaced by one line comparing both vertex_buffer,
            # once the exporing functions take care of TODO bone indices, uvs and normals
            failed_uvs_count = 0
            failed_uvs = {}
            for vertex_index, v_original in enumerate(vertices_array_original):
                v_exported = vertices_array_exported[vertex_index]
                if mesh_original.vertex_format != 0:
                    assert v_original.position_x == v_exported.position_x
                    assert v_original.position_y == v_exported.position_y
                    assert v_original.position_z == v_exported.position_z
                else:
                    # floats, no rounding, Blender carries some presicion errors
                    # TODO: could use the math.isclose function in python 3.5
                    assert abs(v_original.position_x - v_exported.position_x) < 0.0001
                    assert abs(v_original.position_y - v_exported.position_y) < 0.0001
                    assert abs(v_original.position_z - v_exported.position_z) < 0.0001
                # TODO:
                # assert v_original.position_w == v_exported.position_w

                if v_original.uv_x != v_exported.uv_x:
                    failed_uvs_count += 1
                    failed_uvs[v_original.uv_x] = v_exported.uv_x
                    failed_uvs_all[v_original.uv_x] = v_exported.uv_x
                if v_original.uv_y != v_exported.uv_y:
                    failed_uvs_count += 1
                    failed_uvs[v_original.uv_y] = v_exported.uv_y
                    failed_uvs_all[v_original.uv_y] = v_exported.uv_y
                if mesh_original.vertex_format == 0:
                    continue

                # Check if weights were exported correctly
                # Add workrounds for weird cases (although maybe they should fail)
                weights_test = sorted(v_original.weight_values[:]) == sorted(v_exported.weight_values[:])
                bone_indices = v_original.bone_indices[:]
                if len(set(bone_indices)) != len(bone_indices):
                    # Weird case 1): there were duplicate bone indices
                    weights_test = True
                if weights_test is False:
                    # weird case 2): bone_indices not in the bone_palette array bounds
                    # ALB-19 was created to investigate this
                    bpi = mesh_original.bone_palette_index
                    bone_palette = mod_original.bone_palette_array[bpi]
                    new_bone_indices_1 = [bone_palette.values[bi] for bi in bone_indices if bi < bone_palette.unk_01]
                    new_bone_indices_2 = [mod_original.unk_13[bi] for bi in bone_indices if bi >= bone_palette.unk_01]
                    new_bone_indices = new_bone_indices_1 + new_bone_indices_2
                    if len(new_bone_indices) != len(set(new_bone_indices)):
                        weights_test = True
                if weights_test is False:
                    print('Mesh index {} Vertex index {} {}'.format(mesh_index, vertex_index, mod_file))
                    print('indices (original, exported)', v_original.bone_indices[:], v_exported.bone_indices[:])
                    print('weights (original, exported)', v_original.weight_values[:], v_exported.weight_values[:])
                assert weights_test
            if failed_uvs_count:
                print('mesh index {mesh_index} has {failed_uvs_count} failed uvs'
                      .format(mesh_index=mesh_index, failed_uvs_count=failed_uvs_count))
        if failed_uvs_all:
            print('Model has {uv_count} failed uvs: {total_failed_uvs}'
                  .format(uv_count=len(failed_uvs_all), total_failed_uvs=failed_uvs_all))
        assert len(failed_uvs_all) < 10
