from ctypes import sizeof
from hashlib import sha1
import os

import pytest

from albam.mtframework import Tex112
from albam.image_formats.dds import DDSHeader
from tests.conftest import SAMPLES_DIR


@pytest.fixture(scope='module')
def tex_re5_samples():
    samples_dir = pytest.config.getoption('--dirtex') or os.path.join(SAMPLES_DIR, 're5/tex')
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]


@pytest.fixture(scope='module')
def dds_samples():
    samples_dir = pytest.config.getoption('--dirtex') or os.path.join(SAMPLES_DIR, 'dds')
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]


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
