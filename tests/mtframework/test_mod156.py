from albam.lib.structure import get_offset, get_size


def test_constant_fields(mod156):
    assert mod156.id_magic == b'MOD'
    assert mod156.version == 156
    assert mod156.version_rev == 1
    assert mod156.reserved_01 == 0
    assert mod156.reserved_02 == 0
    assert mod156.reserved_03 == 0


def test_mandatory_fields(mod156):
    assert mod156.mesh_count
    assert mod156.material_count
    assert mod156.vertex_count
    assert mod156.face_count
    assert mod156.edge_count
    assert mod156.vertex_buffer_size
    assert mod156.group_count
    assert mod156.group_offset
    assert mod156.unk_01
    assert mod156.unk_02


def test_conditional_fields(mod156):
    assert bool(mod156.bone_count) == bool(mod156.bones_array_offset)
    assert bool(mod156.bone_count) == bool(mod156.bone_palette_count)
    assert bool(mod156.texture_count) == bool(mod156.textures_array)
    assert bool(mod156.texture_count) == bool(mod156.textures_array_offset) or \
        bool(mod156.textures_array_offset) == bool(mod156.materials_data_array)
    assert bool(mod156.unk_08) == bool(mod156.unk_12)


def test_offset_fields(mod156):
    assert not mod156.bone_count or get_offset(mod156, 'bones_array') == mod156.bones_array_offset
    assert not mod156.texture_count or mod156.textures_array_offset > get_offset(mod156, 'group_data_array')
    assert mod156.meshes_array_offset == get_offset(mod156, 'meshes_array')
    assert get_offset(mod156, 'meshes_array_2') == get_offset(mod156, 'meshes_array') + get_size(mod156, 'meshes_array')
    assert get_offset(mod156, 'vertex_buffer') == mod156.vertex_buffer_offset
    assert get_offset(mod156, 'index_buffer') == mod156.index_buffer_offset


def test_size_fields(mod156):
    assert mod156.bone_count == len(mod156.bones_array)
    assert mod156.mesh_count == len(mod156.meshes_array)
    assert mod156.material_count == len(mod156.materials_data_array)
    assert mod156.texture_count == len(mod156.textures_array)
    assert mod156.bone_palette_count == len(mod156.bone_palette_array)
    assert mod156.vertex_count == len(mod156.vertex_buffer) // 32
    assert mod156.face_count == len(mod156.index_buffer) + 1


def test_mesh_constant_fields(mod156_mesh):
    assert mod156_mesh.constant == 1
    assert mod156_mesh.vertex_stride == 32


def test_mesh_enum_fields(mod156_mesh):
    assert mod156_mesh.level_of_detail in (0, 1, 2, 3, 252, 254, 255)
    assert mod156_mesh.vertex_format in (0, 1, 2, 3, 4, 5, 6, 7)


def test_mesh_mandatory_fields(mod156_mesh):
    assert mod156_mesh.constant
    assert mod156_mesh.level_of_detail
    assert mod156_mesh.vertex_stride
    assert mod156_mesh.vertex_count
    assert mod156_mesh.vertex_index_end
    assert mod156_mesh.face_count
    assert mod156_mesh.vertex_group_count
