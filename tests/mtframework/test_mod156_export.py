from tests.conftest import assert_same_attributes


def test_inmutable_fields(mod156_original, mod156_exported):
    assert_same_attributes(mod156_original, mod156_exported, 'id_magic')
    assert_same_attributes(mod156_original, mod156_exported, 'version')
    assert_same_attributes(mod156_original, mod156_exported, 'version_rev')
    assert_same_attributes(mod156_original, mod156_exported, 'reserved_01')
    assert_same_attributes(mod156_original, mod156_exported, 'reserved_02')
    assert_same_attributes(mod156_original, mod156_exported, 'reserved_03')
    assert_same_attributes(mod156_original, mod156_exported, 'mesh_count')
    assert_same_attributes(mod156_original, mod156_exported, 'material_count')
    assert_same_attributes(mod156_original, mod156_exported, 'vertex_count')
    assert_same_attributes(mod156_original, mod156_exported, 'face_count')
    assert_same_attributes(mod156_original, mod156_exported, 'edge_count')
    assert_same_attributes(mod156_original, mod156_exported, 'group_count')
    assert_same_attributes(mod156_original, mod156_exported, 'texture_count')
    assert_same_attributes(mod156_original, mod156_exported, 'bone_count')
