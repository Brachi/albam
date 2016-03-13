import ctypes
import os

import pytest

from albam.mtframework import Arc, Mod156
from albam.utils import get_offset, get_size
from tests.test_mtframework_arc import arc_re5_samples


@pytest.fixture(scope='module', params=arc_re5_samples())
def mods_from_arc(request, tmpdir_factory):
    arc_file = request.param
    base_temp = tmpdir_factory.mktemp(os.path.basename(arc_file).replace('.arc', '-arc'))
    out = str(base_temp)
    arc = Arc(file_path=arc_file)
    arc.unpack(out)

    mod_files = [os.path.join(root, f) for root, _, files in os.walk(out)
                 for f in files if f.endswith('.mod')]
    mods = [Mod156(mod_file) for mod_file in mod_files]
    for i, mod in enumerate(mods):
        assert ctypes.sizeof(mod) == os.path.getsize(mod_files[i])
    return mods


def test_mod_id_magic(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.id_magic == b'MOD'


def test_mod_version(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.version == 156


def test_mod_version_rev(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.version_rev == 1


def test_mod_bone_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.bone_count >= 0


def test_mod_mesh_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.mesh_count >= 0


def test_mod_material_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.material_count >= 0


def test_mod_vertex_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.vertex_count >= 0
        assert mod.vertex_count == len(mod.vertex_buffer) // 32


def test_mod_face_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.face_count >= 0
        assert mod.face_count == len(mod.index_buffer) + 1
        # assert mod.face_count == sum(m.face_count for m in mod.meshes_array)


def test_mod_edge_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.edge_count >= 0


def test_mod_vertex_buffer_size(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.vertex_buffer_size >= 0
        assert mod.vertex_buffer_size == mod.vertex_count * 32
        assert mod.vertex_buffer_size == sum(m.vertex_count for m in mod.meshes_array) * 32


def test_mod_vertex_buffer_2_size(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.vertex_buffer_2_size >= 0


def test_mod_texture_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.texture_count >= 0


def test_mod_group_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.group_count >= 1


def test_mod_bone_palette_count(mods_from_arc):
    for mod in mods_from_arc:
        if mod.bone_count:
            assert mod.bone_palette_count >= 1
        else:
            assert mod.bone_palette_count == 0


def test_mod_bones_array_offset(mods_from_arc):
    for mod in mods_from_arc:
        if mod.bone_count:
            assert mod.bones_array_offset >= get_offset(mod, 'unk_12')
        else:
            assert mod.bones_array_offset == 0


def test_mod_group_offset(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.group_offset > 0


def test_mod_textures_array_offset(mods_from_arc):
    for mod in mods_from_arc:
        if mod.texture_count or mod.material_count:
            assert mod.textures_array_offset > get_offset(mod, 'group_data_array')
        else:
            assert mod.textures_array_offset == 0


def test_mod_meshes_array_offset(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.meshes_array_offset >= 0


def test_mod_vertex_buffer_offset(mods_from_arc):
    pass


def test_mod_vertex_buffer_2_offset(mods_from_arc):
    pass


def test_mod_index_buffer_offset(mods_from_arc):
    pass


def test_mod_reserverd_01(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.reserved_01 == 0


def test_mod_reserved_02(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.reserved_02 == 0


def test_mod_sphere_x(mods_from_arc):
    for mod in mods_from_arc:
        pass


def test_mod_sphere_y(mods_from_arc):
    pass


def test_mod_sphere_z(mods_from_arc):
    pass


def test_mod_sphere_w(mods_from_arc):
    pass


def test_mod_box_min_x(mods_from_arc):
    pass


def test_mod_box_min_y(mods_from_arc):
    pass


def test_mod_box_min_z(mods_from_arc):
    pass


def test_mod_box_min_w(mods_from_arc):
    pass


def test_mod_box_max_x(mods_from_arc):
    pass


def test_mod_box_max_y(mods_from_arc):
    pass


def test_mod_box_max_z(mods_from_arc):
    pass


def test_mod_box_max_w(mods_from_arc):
    pass


def test_mod_unk_01(mods_from_arc):
    pass


def test_mod_unk_02(mods_from_arc):
    pass


def test_mod_unk_03(mods_from_arc):
    pass


def test_mod_unk_04(mods_from_arc):
    pass


def test_mod_unk_05(mods_from_arc):
    pass


def test_mod_unk_06(mods_from_arc):
    pass


def test_mod_unk_07(mods_from_arc):
    pass


def test_mod_unk_08(mods_from_arc):
    pass


def test_mod_unk_09(mods_from_arc):
    pass


def test_mod_unk_10(mods_from_arc):
    pass


def test_mod_unk_11(mods_from_arc):
    pass


def test_mod_reserved_03(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.reserved_03 == 0


def test_mod_unk_12(mods_from_arc):
    for mod in mods_from_arc:
        if mod.unk_08:
            assert mod.unk_12
        else:
            assert not mod.unk_12


def test_mod_bones_array(mods_from_arc):
    for mod in mods_from_arc:
        if mod.bone_count:
            assert len(mod.bones_array) == mod.bone_count
            assert get_offset(mod, 'bones_array') == mod.bones_array_offset
        else:
            assert mod.bones_array_offset == 0


def test_bones_unk_matrix_array(mods_from_arc):
    pass


def test_meshes_array_2(mods_from_arc):
    for mod in mods_from_arc:
        assert get_offset(mod, 'meshes_array_2') == get_offset(mod, 'meshes_array') + get_size(mod, 'meshes_array')
        assert get_offset(mod, 'vertex_buffer') == get_offset(mod, 'meshes_array_2') + get_size(mod, 'meshes_array_2')


def test_vertex_buffer(mods_from_arc):
    for mod in mods_from_arc:
        assert get_offset(mod, 'vertex_buffer') == mod.vertex_buffer_offset
