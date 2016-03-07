import os

import pytest

from albam.mtframework import Mod156
from albam.utils import get_offset
from tests.conftest import SAMPLES_DIR


@pytest.fixture(scope='module')
def mod_re5_samples():
    samples_dir = pytest.config.getoption('--dirmod') or os.path.join(SAMPLES_DIR, 're5/mod')
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]


@pytest.fixture(scope='module', params=mod_re5_samples())
def mod156(request):
    return Mod156(file_path=request.param)


def test_mod156_id_magic(mod156):
    assert mod156.id_magic == b'MOD'


def test_mod156_version(mod156):
    assert mod156.version == 156


def test_mod156_version_rev(mod156):
    assert mod156.version_rev == 1

def test_mod156_bone_count(mod156):
    assert mod156.bone_count >= 0


def test_mod156_bone_count(mod156):
    assert mod156.bone_count >= 0


def test_mod156_mesh_count(mod156):
    assert mod156.mesh_count >= 0


def test_mod156_material_count(mod156):
    assert mod156.material_count >= 0


def test_mod156_vertex_count(mod156):
    assert mod156.vertex_count >= 0
    assert mod156.vertex_count == len(mod156.vertex_buffer) // 32


def test_mod156_face_count(mod156):
    assert mod156.face_count >= 0
    assert mod156.face_count == len(mod156.index_buffer) + 1
    # assert mod156.face_count == sum(m.face_count for m in mod156.meshes_array)


def test_mod156_edge_count(mod156):
    assert mod156.edge_count >= 0


def test_mod156_vertex_buffer_size(mod156):
    assert mod156.vertex_buffer_size >= 0
    assert mod156.vertex_buffer_size == mod156.vertex_count * 32
    assert mod156.vertex_buffer_size == sum(m.vertex_count for m in mod156.meshes_array) * 32


def test_mod156_vertex_buffer_2_size(mod156):
    assert mod156.vertex_buffer_2_size >= 0


def test_mod156_texture_count(mod156):
    assert mod156.texture_count >= 0


def test_mod156_group_count(mod156):
    assert mod156.group_count >= 1


def test_mod156_bone_palette_count(mod156):
    if mod156.bone_count:
        assert mod156.bone_palette_count >= 1
    else:
        assert mod156.bone_palette_count == 0


def test_mod156_bones_array_offset(mod156):
    if mod156.bone_count:
        assert mod156.bones_array_offset >= get_offset(mod156, 'unk_12')
    else:
        assert mod156.bones_array_offset == 0


def test_mod156_group_offset(mod156):
    assert mod156.group_offset > 0


def test_mod156_textures_array_offset(mod156):
    if mod156.texture_count:
        assert mod156.textures_array_offset > get_offset(mod156, 'group_data_array')
    else:
        assert mod156.textures_array_offset == 0


def test_mod156_meshes_array_offset(mod156):
    assert mod156.meshes_array_offset >= 0


def test_mod156_vertex_buffer_offset(mod156):
    pass


def test_mod156_vertex_buffer_2_offset(mod156):
    pass


def test_mod156_index_buffer_offset(mod156):
    pass


def test_mod156_reserverd_01(mod156):
    pass


def test_mod156_reserved_02(mod156):
    pass


def test_mod156_sphere_x(mod156):
    pass


def test_mod156_sphere_y(mod156):
    pass


def test_mod156_sphere_z(mod156):
    pass


def test_mod156_sphere_z(mod156):
    pass


def test_mod156_box_min_x(mod156):
    pass


def test_mod156_box_min_y(mod156):
    pass


def test_mod156_box_min_z(mod156):
    pass


def test_mod156_box_min_w(mod156):
    assert mod156.box_min_w


def test_mod156_box_max_x(mod156):
    pass


def test_mod156_box_max_y(mod156):
    pass


def test_mod156_box_max_z(mod156):
    pass


def test_mod156_box_max_w(mod156):
    assert mod156.box_max_w


def test_mod156_unk_01(mod156):
    pass

def test_mod156_unk_02(mod156):
    pass


def test_mod156_unk_02(mod156):
    pass


def test_mod156_unk_03(mod156):
    pass


def test_mod156_unk_04(mod156):
    pass


def test_mod156_unk_05(mod156):
    pass


def test_mod156_unk_06(mod156):
    pass


def test_mod156_unk_07(mod156):
    pass


def test_mod156_unk_08(mod156):
    pass


def test_mod156_unk_09(mod156):
    pass


def test_mod156_unk_10(mod156):
    pass


def test_mod156_unk_11(mod156):
    pass


def test_mod156_reserved_03(mod156):
    assert mod156.reserved_03 == 0


def test_mod156_unk_12(mod156):
    if mod156.unk_08:
        assert mod156.unk_12
    else:
        assert not mod156.unk_12


def test_mod156_bones_array(mod156):
    if mod156.bone_count:
        assert len(mod156.bones_array) == mod156.bone_count
        assert get_offset(mod156, 'bones_array') == mod156.bones_array_offset
    else:
        assert mod156.bones_array_offset == 0


def test_bones_unk_matrix_array(mod156):
    pass
