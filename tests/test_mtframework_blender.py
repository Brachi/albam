from difflib import SequenceMatcher
from itertools import chain

import pytest

from albam.mtframework.mod import Mesh156
from albam.utils import get_offset


EXPECTED_VERTEX_BUFFER_RATIO = 0.65
EXPECTED_MAX_INDICES_COUNT_RATIO = 0.17
EXPECTED_INDEX_BUFFER_RATIO = 0.65
EXPECTED_MAX_MISSING_VERTICES = 4000   # this is actually depending on the size of the model


def is_close(a, b):
    return abs(a) - abs(b) < 0.001


def test_mod156_import_export_export_id_magic(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.id_magic == mod_exported.id_magic


def test_mod156_import_export_version(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.version == mod_exported.version


def test_mod156_import_export_version_rev(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.version_rev == mod_exported.version_rev


def test_mod156_import_export_bone_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.bone_count == mod_exported.bone_count


def test_mod156_import_export_mesh_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.mesh_count == mod_exported.mesh_count


def test_mod156_import_export_material_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.material_count == mod_exported.material_count


def test_mod156_import_export_vertex_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.vertex_count - mod_exported.vertex_count < EXPECTED_MAX_MISSING_VERTICES


def test_mod156_import_export_face_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        # Expecting some differences in faces generated with the export algorithm
        difference = abs(mod_original.face_count - mod_exported.face_count)
        ratio = difference / mod_original.face_count
        assert ratio < EXPECTED_MAX_INDICES_COUNT_RATIO


@pytest.mark.xfail
def test_mod156_import_export_edge_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.edge_count == mod_exported.edge_count


def test_mod156_import_export_vertex_buffer_size(re5_unpacked_data):
    # TODO: see comment in _get_vertex_array_from_vertex_buffer
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert (mod_original.vertex_buffer_size - mod_exported.vertex_buffer_size) // 32 < EXPECTED_MAX_MISSING_VERTICES


def test_mod156_import_export_vertex_buffer_2_size(re5_unpacked_data):
    """Since uses saved mod data"""
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.vertex_buffer_2_size == mod_exported.vertex_buffer_2_size


def test_mod156_import_export_texture_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.texture_count == mod_exported.texture_count


def test_mod156_import_export_group_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.group_count == mod_exported.group_count


def test_mod156_import_export_bone_palettes_same_indices(re5_unpacked_data):
    """Bone palettes are exported using a greedy non optimized method, so
    the quantity so far differs, but it's equivalent. Here we only care that
    the exported bone palette has all the bone indices the original has"""
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        original = chain.from_iterable([bp.values[:] for bp in mod_original.bone_palette_array])
        exported = chain.from_iterable([bp.values[:] for bp in mod_exported.bone_palette_array])
        assert set(original) == set(exported)


def _assert_offsets(mod_original, mod_exported, offset_attr_name, attr_name):
        assert getattr(mod_original, offset_attr_name) in (0, get_offset(mod_original, attr_name))
        assert getattr(mod_exported, offset_attr_name) in (0, get_offset(mod_exported, attr_name))


def test_mod156_import_export_bones_array_offset(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'bones_array_offset', 'bones_array')


def test_mod156_import_export_group_offset(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'group_offset', 'group_data_array')


def test_mod156_import_export_textures_array_offset(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'textures_array_offset', 'textures_array')


def test_mod156_import_export_meshes_array_offset(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'meshes_array_offset', 'meshes_array')


def test_mod156_import_export_vertex_buffer_offset(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'vertex_buffer_offset', 'vertex_buffer')


def test_mod156_import_export_vertex_buffer_2_offset(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'vertex_buffer_2_offset', 'vertex_buffer_2')


def test_mod156_import_export_index_buffer_offset(re5_unpacked_data):
    '''Fails since vertex_buffer_2 is not included'''
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        _assert_offsets(mod_original, mod_exported, 'index_buffer_offset', 'index_buffer')


def test_mod156_import_export_reserved_01(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.reserved_01 == mod_exported.reserved_01


def test_mod156_import_export_reserved_02(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.reserved_02 == mod_exported.reserved_02


def test_mod156_import_export_sphere_x(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_x, mod_exported.sphere_x)


def test_mod156_import_export_sphere_y(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_y, mod_exported.sphere_y)


def test_mod156_import_export_z(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_z, mod_exported.sphere_z)


def test_mod156_import_export_sphere_w(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert is_close(mod_original.sphere_w, mod_exported.sphere_w)


@pytest.mark.parametrize('bbox_attr_name', ('box_min_x', 'box_min_y', 'box_min_z', 'box_min_w',
                                            'box_max_x', 'box_max_y', 'box_max_z', 'box_max_w'))
def test_mod156_import_export_bounding_box(re5_unpacked_data, bbox_attr_name):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        original_value = getattr(mod_original, bbox_attr_name)
        exported_value = getattr(mod_original, bbox_attr_name)

        # for some reason values don't always correspond to the vertices available
        # so accepting a difference of at most 5 units
        assert abs(original_value - exported_value) < 5


def test_mod156_import_export_box_unk_01(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_01 == mod_exported.unk_01


def test_mod156_import_export_box_unk_02(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_02 == mod_exported.unk_02


def test_mod156_import_export_box_unk_03(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_03 == mod_exported.unk_03


def test_mod156_import_export_box_unk_04(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_04 == mod_exported.unk_04


def test_mod156_import_export_box_unk_05(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_05 == mod_exported.unk_05


def test_mod156_import_export_box_unk_06(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_06 == mod_exported.unk_06


def test_mod156_import_export_box_unk_07(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_07 == mod_exported.unk_07


def test_mod156_import_export_box_unk_08(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_08 == mod_exported.unk_08


def test_mod156_import_export_box_unk_09(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_09 == mod_exported.unk_09


def test_mod156_import_export_box_unk_10(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_10 == mod_exported.unk_10


def test_mod156_import_export_box_unk_11(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.unk_11 == mod_exported.unk_11


def test_mod156_import_export_reserverd_03(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert mod_original.reserved_03 == mod_exported.reserved_03


def test_mod156_import_export_box_unk_12(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert bytes(mod_original.unk_12) == bytes(mod_exported.unk_12)


def test_mod156_import_export_bones_array(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert bytes(mod_original.bones_array) == bytes(mod_exported.bones_array)


def test_mod156_import_export_bones_unk_matrix_array(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert bytes(mod_original.bones_unk_matrix_array) == bytes(mod_exported.bones_unk_matrix_array)


def test_mod156_import_export_bones_world_transform_matrix_array(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert (bytes(mod_original.bones_world_transform_matrix_array) ==
                bytes(mod_exported.bones_world_transform_matrix_array))


def test_mod156_import_export_unk_13(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert bytes(mod_original.unk_13) == bytes(mod_exported.unk_13)


def test_mod156_import_export_textures_array(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        textures_original = {t[:] for t in mod_original.textures_array}
        textures_exported = {t[:] for t in mod_exported.textures_array}

        assert textures_original == textures_exported


def test_mod156_import_export_materials_data_array_length(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert len(mod_original.materials_data_array) == len(mod_exported.materials_data_array)


def test_mod156_import_export_materials_data_array_texture_paths(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        texture_paths_from_materials_original = {mod_original.textures_array[ti - 1][:]
                                                 for md in mod_original.materials_data_array
                                                 for ti in md.texture_indices}

        texture_paths_from_materials_exported = {mod_exported.textures_array[ti - 1][:]
                                                 for md in mod_exported.materials_data_array
                                                 for ti in md.texture_indices}
        assert texture_paths_from_materials_original == texture_paths_from_materials_exported


def test_mod156_import_export_materials_data_array_values(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
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


def test_mod156_import_export_meshes_array_length(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert len(mod_original.meshes_array) == len(mod_exported.meshes_array)


def test_mod156_import_export_meshes_array_group_index(re5_unpacked_data):
    """Mesh attribute is exported as null"""
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.group_index == 0


def test_mod156_import_export_meshes_array_material_index(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.material_index == mesh_exported.material_index


def test_mod156_import_export_meshes_array_level_of_detail(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.level_of_detail == mesh_exported.level_of_detail


@pytest.mark.parametrize('attr_name', (field[0] for field in Mesh156._fields_ if field[0].startswith('unk_')))
def test_mod156_import_export_meshes_unk_attributes(re5_unpacked_data, attr_name):
    """Exported as null"""
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert getattr(mesh_original, attr_name) == getattr(mesh_exported, attr_name)


@pytest.mark.xfail(reason="Need to figure out how to export vertex format in all cases")
def test_mod156_import_export_meshes_array_vertex_format(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_format == mesh_exported.vertex_format


def test_mod156_import_export_meshes_array_vertex_stride(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_stride == mesh_exported.vertex_stride


@pytest.mark.xfail(reason="Won't match in meshes that use index_start_1")
def test_mod156_import_export_meshes_array_vertex_count(re5_unpacked_data):
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.vertex_count == mesh_exported.vertex_count


@pytest.mark.xfail
def test_mod156_import_export_meshes_array_face_count(re5_unpacked_data):
    '''Won't match since triangle strip numbers could vary'''
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_original.face_count == mesh_exported.face_count


def test_mod156_import_export_meshes_array_vertex_group_count(re5_unpacked_data):
    """not sure if the attribute is 'vertex_group_count', but always exporting as 1"""
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        for i, mesh_original in enumerate(mod_original.meshes_array):
            mesh_exported = mod_exported.meshes_array[i]
            assert mesh_exported.vertex_group_count == 1

# TODO: Mesh156.bone_palette_index
# TODO: Mod156.meshes_array_2


def test_mod156_import_export_vertex_buffer_approximation(re5_unpacked_data):
    '''Is not expected that the buffer exported matches exactly the original,
    because of rounding errors and more, but right know especially since normals are to be added'''
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        seq = SequenceMatcher(None, bytes(mod_original.vertex_buffer), bytes(mod_exported.vertex_buffer))
        assert seq.quick_ratio() >= EXPECTED_VERTEX_BUFFER_RATIO


def test_mod156_import_export_vertex_buffer_2_approximation(re5_unpacked_data):
    """Since the export uses the saved mod data"""
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        assert bytes(mod_original.vertex_buffer_2) == bytes(mod_exported.vertex_buffer_2)


def test_mod156_import_export_index_buffer_approximation(re5_unpacked_data):
    '''Is not expected that the buffer exported matches exactly the original,
    because of rounding errors and more, but right know especially since normals are to be added'''
    for mod_original, mod_exported in zip(re5_unpacked_data.mods_original, re5_unpacked_data.mods_exported):
        seq = SequenceMatcher(None, bytes(mod_original), bytes(mod_exported))
        assert seq.quick_ratio() >= EXPECTED_INDEX_BUFFER_RATIO


def test_mod156_exported_textures_count(re5_unpacked_data):
    assert len(re5_unpacked_data.textures_original) == len(re5_unpacked_data.textures_exported)


# TODO: revision is not always 34
@pytest.mark.parametrize('attr_name', ('id_magic', 'version', 'mipmap_count',
                                       'unk_byte_1', 'unk_byte_2', 'unk_byte_3',
                                       'width', 'height', 'reserved_1', 'compression_format',
                                       'unk_float_1', 'unk_float_2', 'unk_float_3', 'unk_float_4'))
def test_mod156_exported_textures_attributes(re5_unpacked_data, attr_name):
    for tex_original, tex_exported in zip(re5_unpacked_data.textures_original, re5_unpacked_data.textures_exported):
        if 'effect' in tex_original._file_path:
            continue
        assert getattr(tex_original, attr_name) == getattr(tex_exported, attr_name)
