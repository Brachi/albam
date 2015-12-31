from ctypes import sizeof
from hashlib import sha1
import os

import pytest

from albam.mtframework import Arc, Tex112, Mod156, KNOWN_ARC_FAILS
from albam.mtframework.blender import _get_indices_array
from albam.utils import get_offset, get_size
from albam.image_formats.dds import DDSHeader
from tests.conftest import (arc_re5_samples, mod_re5_samples, tex_re5_samples,
                            dds_samples)


slow = pytest.mark.skipif(not pytest.config.getoption('--runslow'),
                          reason='Slow test, needs "--runslow" to run')


@pytest.mark.parametrize("arc_file", arc_re5_samples())
def test_arc_unpack_re5(tmpdir, arc_file):
    if arc_file.endswith(KNOWN_ARC_FAILS):
        pytest.xfail()
    arc = Arc(file_path=arc_file)
    out = os.path.join(str(tmpdir), 'extraced_ard')

    arc.unpack(out)

    files = {os.path.join(root, f) for root, _, files in os.walk(out)
             for f in files}
    expected_sizes = sorted([f.size for f in arc.file_entries if f.size])
    files_sizes = sorted([os.path.getsize(f) for f in files])

    assert os.path.isdir(out)
    assert arc.files_count == len(files)
    assert expected_sizes == files_sizes


@slow
@pytest.mark.parametrize('arc_file', arc_re5_samples())
def test_arc_from_dir_re5(tmpdir, arc_file):
    """
    get an arc file (ideally from the game), unpack it, repackit, unpack it again
    compare the 2 arc files and the 2 output folders
    """
    if arc_file.endswith(KNOWN_ARC_FAILS):
        pytest.xfail()
    arc_original = Arc(file_path=arc_file)
    arc_original_out = os.path.join(str(tmpdir), os.path.basename(arc_file).replace('.arc', ''))
    arc_original.unpack(arc_original_out)

    arc_from_dir = Arc.from_dir(arc_original_out)
    arc_from_dir_out = os.path.join(str(tmpdir), 'arc-from-dir.arc')
    with open(arc_from_dir_out, 'wb') as w:
        w.write(arc_from_dir)

    arc_from_arc_from_dir = Arc(file_path=arc_from_dir_out)
    arc_from_arc_from_dir_out = os.path.join(str(tmpdir), 'arc-from-arc-from-dir')
    arc_from_arc_from_dir.unpack(arc_from_arc_from_dir_out)

    files_extracted_1 = [f for _, _, files in os.walk(arc_original_out) for f in files]
    files_extracted_2 = [f for _, _, files in os.walk(arc_from_arc_from_dir_out) for f in files]

    # Assumming zlib default compression used in all original arc files.
    assert os.path.getsize(arc_file) == os.path.getsize(arc_from_dir_out)
    # The hashes would be different due to the file_paths ordering
    assert arc_original.files_count == arc_from_arc_from_dir.files_count
    assert files_extracted_1 == files_extracted_2
    assert arc_from_arc_from_dir.file_entries[0].offset == 32768


@pytest.mark.parametrize('tex_file', tex_re5_samples())
def test_tex112_to_dds(tmpdir, tex_file):
    tex = Tex112(file_path=tex_file)
    dds = tex.to_dds()
    tex_name = os.path.basename(tex_file)
    dds_name = tex_name.replace('.tex', '.dds')
    out = os.path.join(str(tmpdir), dds_name)

    with open(out, 'wb') as w:
        w.write(dds)

    assert dds.header.id_magic == b'DDS '
    assert os.path.getsize(out) == sizeof(DDSHeader) + len(tex.dds_data)


@pytest.mark.parametrize('tex_file', tex_re5_samples())
def test_tex112_calculate_mipmap_offsets(tex_file):
    tex = Tex112(file_path=tex_file)

    offsets_from_file = list(tex.mipmap_offsets)
    w = tex.width
    h = tex.height
    mc = tex.mipmap_count
    fmt = tex.compression_format
    fixed_size_of_header = 40  # mmm...
    start_offset = fixed_size_of_header + (mc * 4)
    calculated_offsets = tex.calculate_mipmap_offsets(mc, w, h, fmt, start_offset)

    assert offsets_from_file == calculated_offsets


@pytest.mark.parametrize('tex_file', tex_re5_samples())
def test_tex_112(tex_file, tmpdir):
    tex = Tex112(file_path=tex_file)
    out = os.path.join(str(tmpdir), 'test.tex')
    with open(out, 'wb') as w:
        w.write(tex)
    with open(tex_file, 'rb') as f, open(out, 'rb') as f2:
        s1 = sha1(f.read()).hexdigest()
        s2 = sha1(f2.read()).hexdigest()

    assert s1 == s2
    assert os.path.getsize(out) == os.path.getsize(tex_file)


@pytest.mark.parametrize('dds_path_1', dds_samples())
def test_tex_from_dds(dds_path_1, tmpdir):
    tex_1 = Tex112.from_dds(file_path=dds_path_1)
    tex_1_name = os.path.basename(dds_path_1).replace('.dds', '.tex')
    tex_1_path = os.path.join(str(tmpdir), tex_1_name)

    with open(tex_1_path, 'wb') as w:
        w.write(tex_1)

    tex_2 = Tex112(file_path=tex_1_path)
    tex_2_name = tex_1_name.replace('.tex', '1.tex')
    tex_2_path = os.path.join(str(tmpdir), tex_2_name)

    with open(tex_2_path, 'wb') as w2:
        w2.write(tex_2)

    with open(tex_1_path, 'rb') as w, open(tex_2_path, 'rb') as w2:
        c1 = w.read()
        c2 = w2.read()

    assert sha1(c1).hexdigest() == sha1(c2).hexdigest()


@pytest.mark.parametrize('mod_path', mod_re5_samples())
def test_mod_load(mod_path, tmpdir, mod_debug_csv_writer, modmesh_debug_csv_writer, pytestconfig):
    mod = Mod156(file_path=mod_path)
    out = os.path.join(str(tmpdir), 'copy-of-{}'.format(os.path.basename(mod_path)))

    # Debugging
    # TODO: this should be a separate script
    if pytestconfig.getoption('csvoutmod'):
        writer = mod_debug_csv_writer.get('ob')
        headers_written = mod_debug_csv_writer['headers_written']
        if not headers_written:
            writer.writerow(['file'] + [f[0] for f in mod._fields_])
            mod_debug_csv_writer['headers_written'] = True
        values = [getattr(mod, field_name[0]) for field_name in mod._fields_]
        writer.writerow([os.path.basename(mod_path)] + values)

    if pytestconfig.getoption('csvoutmodmesh'):
        writer = modmesh_debug_csv_writer.get('ob')
        headers_written = modmesh_debug_csv_writer['headers_written']
        if not headers_written:
            writer.writerow(['file', 'index'] + [f[0] for f in mod.meshes_array[0]._fields_])
            modmesh_debug_csv_writer['headers_written'] = True
        meshes = mod.meshes_array
        for i, mesh in enumerate(meshes):
            values = [getattr(mesh, field_name[0]) for field_name in mesh._fields_]
            writer.writerow([os.path.basename(mod_path), i] + values)

    with open(out, 'wb') as w:
        w.write(mod)

    with open(mod_path, 'rb') as w, open(out, 'rb') as w2:
        c1 = w.read()
        c2 = w2.read()

    assert sha1(c1).hexdigest() == sha1(c2).hexdigest()
    assert mod.id_magic == b'MOD'
    if mod.bone_count:
        assert mod.bones_array_offset == get_offset(mod, 'bones_array')
        assert len(mod.bones_array) >= 1
        assert len(mod.bone_palette_array) >= 1
    else:
        assert not mod.bones_array_offset
        assert len(mod.bones_array) == 0
        assert len(mod.bone_palette_array) == 0

    meshes_face_count_sum = sum(mesh.face_count for mesh in mod.meshes_array)
    indices_arrays = (_get_indices_array(mod, mod.meshes_array[i]) for i in range(len(mod.meshes_array)))
    assert meshes_face_count_sum == sum(len(indices) for indices in indices_arrays)
    assert mod.vertex_count == sum(mesh.vertex_count for mesh in mod.meshes_array)
    # TODO: this below fails! research needed
    # assert mod.face_count == sum(mesh.face_count for mesh in mod.meshes_array)
    if mod.texture_count:
        assert mod.textures_array_offset == get_offset(mod, 'textures_array')
        assert get_offset(mod, 'materials_data_array') == mod.textures_array_offset + get_size(mod, 'textures_array')
    else:
        assert get_offset(mod, 'materials_data_array') == mod.textures_array_offset
    assert mod.group_offset == get_offset(mod, 'group_data_array')
    assert mod.meshes_array_offset == get_offset(mod, 'meshes_array')
    assert mod.vertex_buffer_offset == get_offset(mod, 'vertex_buffer')
    assert sizeof(mod) == os.path.getsize(mod_path) == os.path.getsize(out)
