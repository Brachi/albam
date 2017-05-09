import os

import pytest

from albam.engines.mtframework import Arc, Mod156
from albam.lib.structure import get_offset, get_size
from tests.test_mtframework_arc import ARC_FILES


@pytest.fixture(scope='module', params=ARC_FILES)
def mods_from_arc(request, tmpdir_factory):
    arc_file = request.param
    base_temp = tmpdir_factory.mktemp(os.path.basename(arc_file).replace('.arc', '-arc'))
    out = str(base_temp)
    arc = Arc(file_path=arc_file)
    arc.unpack(out)

    mod_files = [os.path.join(root, f) for root, _, files in os.walk(out)
                 for f in files if f.endswith('.mod')]
    mods = [Mod156(mod_file) for mod_file in mod_files]
    return mods


def test_constant_fields(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.id_magic == b'MOD'
        assert mod.version == 156
        assert mod.version_rev == 1
        assert mod.reserved_01 == 0
        assert mod.reserved_02 == 0
        assert mod.reserved_03 == 0


def test_mandatory_fields(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.mesh_count
        assert mod.material_count
        assert mod.vertex_count
        assert mod.face_count
        assert mod.edge_count
        assert mod.vertex_buffer_size
        assert mod.vertex_buffer_2_size
        assert mod.group_count
        assert mod.group_offset
        assert mod.unk_01
        assert mod.unk_02
        assert mod.unk_03
        assert mod.unk_04


def test_conditional_fields(mods_from_arc):
    for mod in mods_from_arc:
        assert bool(mod.bone_count) == bool(mod.bones_array_offset)
        assert bool(mod.bone_count) == bool(mod.bone_palette_count)
        assert bool(mod.texture_count) == bool(mod.textures_array)
        assert bool(mod.texture_count) == bool(mod.textures_array_offset)
        assert bool(mod.unk_08) == bool(mod.unk_12)


def test_offset_fields(mods_from_arc):
    for mod in mods_from_arc:
        assert not mod.bone_count or get_offset(mod, 'bones_array') == mod.bones_array_offset
        assert not mod.texture_count or mod.textures_array_offset > get_offset(mod, 'group_data_array')
        assert mod.meshes_array_offset == get_offset(mod, 'meshes_array')
        assert get_offset(mod, 'meshes_array_2') == get_offset(mod, 'meshes_array') + get_size(mod, 'meshes_array')
        assert get_offset(mod, 'vertex_buffer') == mod.vertex_buffer_offset
        assert get_offset(mod, 'index_buffer') == mod.index_buffer_offset


def test_size_fields(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.bone_count == len(mod.bones_array)
        assert mod.mesh_count == len(mod.meshes_array)
        assert mod.material_count == len(mod.materials_data_array)
        assert mod.texture_count == len(mod.textures_array)
        assert mod.bone_palette_count == len(mod.bone_palette_array)


def test_mod_vertex_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.vertex_count == len(mod.vertex_buffer) // 32


def test_mod_face_count(mods_from_arc):
    for mod in mods_from_arc:
        assert mod.face_count == len(mod.index_buffer) + 1
        # assert mod.face_count == sum(m.face_count for m in mod.meshes_array)
