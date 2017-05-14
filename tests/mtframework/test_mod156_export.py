from tests.conftest import assert_same_attributes, assert_approximate_fields

EXPECTED_MAX_INDICES_COUNT_RATIO = 0.17


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
    assert_same_attributes(mod156_original, mod156_exported, 'unk_13', binary=True)
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


