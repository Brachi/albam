import os

import pytest

from albam.mtframework import Mod210
from albam.utils import get_offset
from tests.conftest import SAMPLES_DIR


@pytest.fixture(scope='module')
def mod_re1hd_samples():
    samples_dir = pytest.config.getoption('--dirmod') or os.path.join(SAMPLES_DIR, 're1hd/mod')
    if not os.path.isdir(samples_dir):
        return []
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]


@pytest.fixture(scope='module', params=mod_re1hd_samples())
def mod210(request):
    mod210 = Mod210(file_path=request.param)
    assert mod210.id_magic == b'MOD'
    assert mod210.version == 210
    return mod210


def test_mod210_id_magic(mod210):
    assert mod210.id_magic == b'MOD'


def test_mod210_version(mod210):
    assert mod210.version == 210


def test_mod210_version_rev(mod210):
    assert mod210.version_rev == 0


def test_mod210_bone_count(mod210):
    assert mod210.bone_count >= 0


def test_mod210_mesh_count(mod210):
    assert mod210.mesh_count >= 0


def test_mod210_material_count(mod210):
    assert mod210.material_count >= 0


def test_mod210_vertex_count(mod210):
    assert mod210.vertex_count >= 0
    # assert mod210.vertex_count == len(mod210.vertex_buffer) // 32


def test_mod210_face_count(mod210):
    pass
    # assert mod210.face_count >= 0
    # assert mod210.face_count == len(mod210.index_buffer) + 1
    # assert mod210.face_count == sum(m.face_count for m in mod210.meshes_array)


def test_mod210_edge_count(mod210):
    assert mod210.edge_count >= 0


def test_mod210_vertex_buffer_size(mod210):
    assert mod210.vertex_buffer_size >= 0
    # assert mod210.vertex_buffer_size == mod210.vertex_count * 32
    # assert mod210.vertex_buffer_size == sum(m.vertex_count for m in mod210.meshes_array) * 32


def test_mod210_vertex_buffer_2_size(mod210):
    assert mod210.vertex_buffer_2_size >= 0


def test_mod210_group_count(mod210):
    assert mod210.group_count >= 1


def test_mod210_bones_array_offset(mod210):
    if mod210.bone_count:
        assert mod210.bones_array_offset >= get_offset(mod210, 'bones_array')
    else:
        assert mod210.bones_array_offset == 0


def test_mod210_group_offset(mod210):
    assert mod210.group_offset > 0


def test_mod210_meshes_array_offset(mod210):
    assert mod210.meshes_array_offset >= 0


def test_mod210_vertex_buffer_offset(mod210):
    pass


def test_mod210_vertex_buffer_2_offset(mod210):
    pass


def test_mod210_index_buffer_offset(mod210):
    pass


def test_mod210_reserverd_01(mod210):
    pass


def test_mod210_reserved_02(mod210):
    pass


def test_mod210_sphere_x(mod210):
    pass


def test_mod210_sphere_y(mod210):
    pass


def test_mod210_sphere_z(mod210):
    pass


def test_mod210_sphere_w(mod210):
    pass


def test_mod210_box_min_x(mod210):
    pass


def test_mod210_box_min_y(mod210):
    pass


def test_mod210_box_min_z(mod210):
    pass


def test_mod210_box_min_w(mod210):
    pass


def test_mod210_box_max_x(mod210):
    pass


def test_mod210_box_max_y(mod210):
    pass


def test_mod210_box_max_z(mod210):
    pass


def test_mod210_box_max_w(mod210):
    pass


def test_mod210_unk_01(mod210):
    pass


def test_mod210_unk_02(mod210):
    pass


def test_mod210_unk_03(mod210):
    pass


def test_mod210_unk_04(mod210):
    pass


def test_mod210_unk_05(mod210):
    pass


def test_mod210_unk_06(mod210):
    pass


def test_mod210_unk_07(mod210):
    pass


def test_mod210_bones_array(mod210):
    if mod210.bone_count:
        assert len(mod210.bones_array) == mod210.bone_count
        assert get_offset(mod210, 'bones_array') == mod210.bones_array_offset
    else:
        assert mod210.bones_array_offset == 0


def test_mod210_group_data_array(mod210):
    assert get_offset(mod210, 'group_data_array') == mod210.group_offset


def test_mod210_materials_data_array(mod210):
    assert get_offset(mod210, 'materials_data_array') == mod210.materials_data_offset


def test_mod210_meshes_array(mod210):
    assert get_offset(mod210, 'meshes_array') == mod210.meshes_array_offset


def test_mod210_vertex_buffer(mod210):
    assert len(mod210.vertex_buffer) == mod210.vertex_buffer_size
    assert get_offset(mod210, 'vertex_buffer') == mod210.vertex_buffer_offset


def test_mod210_vertex_buffer_2(mod210):
    assert len(mod210.vertex_buffer_2) == mod210.vertex_buffer_2_size
    if mod210.vertex_buffer_2_size:
        assert get_offset(mod210, 'vertex_buffer_2') == mod210.vertex_buffer_offset + mod210.vertex_buffer_2_size


def test_mod210_index_buffer(mod210):
    assert len(mod210.index_buffer) == mod210.face_count
    assert get_offset(mod210, 'index_buffer') == mod210.index_buffer_offset
    # assert get_offset(mod210, 'index_buffer') + mod210.face_count * 2 + len(mod210.file_padding) == mod210.file_size
