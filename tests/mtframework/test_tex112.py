from ctypes import sizeof
from hashlib import sha1
import os


from albam.image_formats.dds import DDS, DDSHeader
from albam.engines.mtframework import Tex112


def test_tex112_to_dds(tmpdir, tex112):
    dds = tex112.to_dds()

    out = tmpdir.join(os.path.basename(tex112._file_path).replace('.tex', '.dds'))
    with open(str(out), 'wb') as w:
        w.write(dds)

    assert dds.header.id_magic == b'DDS '
    assert out.size() == sizeof(DDSHeader) + len(tex112.dds_data)


def test_tex112_calculate_mipmap_offsets(tex112):
    offsets_from_file = list(tex112.mipmap_offsets)
    w = tex112.width
    h = tex112.height
    mc = tex112.mipmap_count
    fmt = tex112.compression_format
    fixed_size_of_header = 40  # mmm...
    start_offset = fixed_size_of_header + (mc * 4)
    calculated_offsets = tex112.calculate_mipmap_offsets(mc, w, h, fmt, start_offset)

    assert offsets_from_file == calculated_offsets


def test_tex_calculate_mipmap_count(tex112):
    mipmap_count_from_file = tex112.mipmap_count
    mipmap_calculated = DDS.calculate_mipmap_count(tex112.width, tex112.height)

    # There might be cases where tex don't have mipmaps?
    assert mipmap_count_from_file == mipmap_calculated


def test_tex_from_dds(tex112, tmpdir):
    dds = tex112.to_dds()

    out = str(tmpdir.join(os.path.basename(tex112._file_path).replace('.tex', '.dds')))
    with open(out, 'wb') as w:
        w.write(dds)

    tex_from_dds = Tex112.from_dds(file_path=out)
    out_2 = str(tmpdir.join(os.path.basename(tex112._file_path).replace('.tex', '.2.dds')))
    with open(out_2, 'wb') as w:
        w.write(tex_from_dds.to_dds())

    with open(out, 'rb') as f, open(out_2, 'rb') as f_2:
        c1 = f.read()
        c2 = f_2.read()

    assert sha1(c1).hexdigest() == sha1(c2).hexdigest()
