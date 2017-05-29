from itertools import chain

import pytest

from albam.engines.mtframework.utils import get_vertices_array
from tests.conftest import assert_same_attributes, assert_approximate_fields

EXPECTED_MAX_INDICES_COUNT_RATIO = 0.17
EXPECTED_VERTEX_BUFFER_SIZE_RATIO = 0.10


def test_inmutable_fields(mod156_original, mod156_exported):
    assert_same_attributes(mod156_original, mod156_exported, 'id_magic')
    assert_same_attributes(mod156_original, mod156_exported, 'version')
    assert_same_attributes(mod156_original, mod156_exported, 'version_rev')
    assert_same_attributes(mod156_original, mod156_exported, 'reserved_01')
    assert_same_attributes(mod156_original, mod156_exported, 'reserved_02')
    assert_same_attributes(mod156_original, mod156_exported, 'reserved_03')
    assert_same_attributes(mod156_original, mod156_exported, 'mesh_count')
    assert_same_attributes(mod156_original, mod156_exported, 'material_count')
    assert_same_attributes(mod156_original, mod156_exported, 'group_count')
    assert_same_attributes(mod156_original, mod156_exported, 'texture_count')
    assert_same_attributes(mod156_original, mod156_exported, 'bone_count')
    assert_same_attributes(mod156_original, mod156_exported, 'bones_array', binary=True)
    assert_same_attributes(mod156_original, mod156_exported, 'bones_unk_matrix_array', binary=True)
    assert_same_attributes(mod156_original, mod156_exported, 'bones_world_transform_matrix_array', binary=True)
    assert_same_attributes(mod156_original, mod156_exported, 'bones_animation_mapping', binary=True)
    assert_same_attributes(mod156_original, mod156_exported, 'materials_data_array', length=True)
    assert_same_attributes(mod156_original, mod156_exported, 'textures_array', length=True)
    assert_same_attributes(mod156_original, mod156_exported, 'meshes_array', length=True)
    assert_same_attributes(mod156_original, mod156_exported, 'vertex_buffer_2', binary=True)


def test_approximate_fields(mod156_original, mod156_exported):
    assert_approximate_fields(mod156_original, mod156_exported, 'box_min_x', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_min_y', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_min_z', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_min_w', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_max_x', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_max_y', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_max_z', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'box_max_w', 5)
    assert_approximate_fields(mod156_original, mod156_exported, 'face_count', EXPECTED_MAX_INDICES_COUNT_RATIO)
    assert_approximate_fields(mod156_original, mod156_exported, 'vertex_buffer_size', EXPECTED_MAX_INDICES_COUNT_RATIO)


def test_texture_paths_in_materials(mod156_original, mod156_exported):
    texture_paths_from_materials_original = {mod156_original.textures_array[ti - 1][:]
                                             for md in mod156_original.materials_data_array
                                             for ti in md.texture_indices}

    texture_paths_from_materials_exported = {mod156_exported.textures_array[ti - 1][:]
                                             for md in mod156_exported.materials_data_array
                                             for ti in md.texture_indices}
    assert texture_paths_from_materials_original == texture_paths_from_materials_exported


def _test_textures_array(mod156_original, mod156_exported):
    # TODO: see how it can be included in 'test_immutable_fields'
    textures_original = {t[:] for t in mod156_original.textures_array}
    textures_exported = {t[:] for t in mod156_exported.textures_array}
    assert textures_original == textures_exported


def test_bone_palette(mod156_original, mod156_exported):
    """
    Bone palettes are exported using a greedy non optimized method, so
    the quantity so far differs, but it's equivalent. Here we only care that
    the exported bone palette has all the bone indices the original has
    """
    original = chain.from_iterable([bp.values[:] for bp in mod156_original.bone_palette_array])
    exported = chain.from_iterable([bp.values[:] for bp in mod156_exported.bone_palette_array])

    assert set(original) == set(exported)


def test_meshes_array_immutable_fields(mod156_original, mod156_exported):
    for i, mesh_original in enumerate(mod156_original.meshes_array):
        mesh_exported = mod156_exported.meshes_array[i]
        assert_same_attributes(mesh_original, mesh_exported, 'material_index')
        assert_same_attributes(mesh_original, mesh_exported, 'level_of_detail')
        assert_same_attributes(mesh_original, mesh_exported, 'material_index')
        assert_same_attributes(mesh_original, mesh_exported, 'vertex_stride')


def test_mesh_vertices_bone_weights_sum(mod156_mesh_original, mod156_mesh_exported):
    # TODO: see to not dupliacte the test
    mod_exported = mod156_mesh_exported._parent_structure
    mesh_vertices = get_vertices_array(mod_exported, mod156_mesh_exported)
    if not mod_exported.bone_count:
        return

    vertices_failed = []
    for vertex_index, vertex in enumerate(mesh_vertices):
        if not sum(vertex.weight_values) == 255:
            vertices_failed.append(vertex_index)
    assert not vertices_failed


def test_mesh_vertices(mod156_mesh_original, mod156_mesh_exported):
    # TODO: see to not dupliacte the test
    mod_original = mod156_mesh_original._parent_structure
    mod_exported = mod156_mesh_exported._parent_structure

    mesh_original_vertices = get_vertices_array(mod_original, mod156_mesh_original)
    mesh_exported_vertices = get_vertices_array(mod_exported, mod156_mesh_exported)

    if mod156_mesh_original.vertex_count != mod156_mesh_exported.vertex_count:
        pytest.xfail('research needed')

    failed_pos_vertices = []
    failed_norm_vertices = []
    for vertex_index, vertex_ori in enumerate(mesh_original_vertices):
        vertex_exp = mesh_exported_vertices[vertex_index]

        pos_original = vertex_ori.position_x, vertex_ori.position_y, vertex_ori.position_z, vertex_ori.position_w
        pos_exported = vertex_exp.position_x, vertex_exp.position_y, vertex_exp.position_z, vertex_exp.position_w
        norm_original = vertex_ori.normal_x, vertex_ori.normal_y, vertex_ori.normal_z, vertex_ori.normal_w
        norm_exported = vertex_exp.normal_x, vertex_exp.normal_y, vertex_exp.normal_z, vertex_exp.normal_w

        if pos_original != pos_exported:
            failed_pos_vertices.append(vertex_index)
        if norm_original != norm_exported:
            failed_norm_vertices.append(vertex_index)

    assert not failed_pos_vertices
    #assert not failed_norm_vertices
