import ctypes
import os

import pytest

from albam.engines.mtframework import Arc, Mod156
from albam.lib.structure import get_offset, get_size
from tests.test_mtframework_arc import ARC_FILES


@pytest.fixture(scope='module', params=ARC_FILES)
def mod156(request, tmpdir_factory):
    arc_file = request.param
    base_temp = tmpdir_factory.mktemp(os.path.basename(arc_file).replace('.arc', '-arc'))
    out = str(base_temp)
    arc = Arc(file_path=arc_file)
    arc.unpack(out)

    mod_files = [os.path.join(root, f) for root, _, files in os.walk(out)
                 for f in files if f.endswith('.mod')]
    mods = [Mod156(mod_file) for mod_file in mod_files]
    # TODO: test all mods in the arc in a simple way.
    # maybe it's worth to wait until parametrized fixtures
    # https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html
    biggest_mod = max(mods, key=lambda m: ctypes.sizeof(m))
    return biggest_mod


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
    assert mod156.vertex_buffer_2_size
    assert mod156.group_count
    assert mod156.group_offset
    assert mod156.unk_01
    assert mod156.unk_02
    assert mod156.unk_03
    assert mod156.unk_04


def test_conditional_fields(mod156):
    assert bool(mod156.bone_count) == bool(mod156.bones_array_offset)
    assert bool(mod156.bone_count) == bool(mod156.bone_palette_count)
    assert bool(mod156.texture_count) == bool(mod156.textures_array)
    assert bool(mod156.texture_count) == bool(mod156.textures_array_offset)
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
