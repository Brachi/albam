from ctypes import sizeof
from hashlib import sha1
import os


from albam.image_formats.dds import DDS, DDSHeader
from albam.engines.mtframework import Tex112


def test_tex112_to_dds(tmpdir, re5_unpacked_data):
    for tex_original in re5_unpacked_data.textures_original:
        dds = tex_original.to_dds()

        out = tmpdir.join(os.path.basename(tex_original._file_path).replace('.tex', '.dds'))
        with open(str(out), 'wb') as w:
            w.write(dds)

        assert dds.header.id_magic == b'DDS '
        assert out.size() == sizeof(DDSHeader) + len(tex_original.dds_data)


def test_tex112_calculate_mipmap_offsets(re5_unpacked_data):
    for tex in re5_unpacked_data.textures_original:
        offsets_from_file = list(tex.mipmap_offsets)
        w = tex.width
        h = tex.height
        mc = tex.mipmap_count
        fmt = tex.compression_format
        fixed_size_of_header = 40  # mmm...
        start_offset = fixed_size_of_header + (mc * 4)
        calculated_offsets = tex.calculate_mipmap_offsets(mc, w, h, fmt, start_offset)

        assert offsets_from_file == calculated_offsets


def test_tex_calculate_mipmap_count(re5_unpacked_data):
    for tex in re5_unpacked_data.textures_original:

        mipmap_count_from_file = tex.mipmap_count
        mipmap_calculated = DDS.calculate_mipmap_count(tex.width, tex.height)

        # There might be cases where tex don't have mipmaps?
        assert mipmap_count_from_file == mipmap_calculated


def test_tex_from_dds(re5_unpacked_data, tmpdir):
    for tex_original in re5_unpacked_data.textures_original:
        dds = tex_original.to_dds()

        out = str(tmpdir.join(os.path.basename(tex_original._file_path).replace('.tex', '.dds')))
        with open(out, 'wb') as w:
            w.write(dds)

        tex_from_dds = Tex112.from_dds(file_path=out)
        out_2 = str(tmpdir.join(os.path.basename(tex_original._file_path).replace('.tex', '.2.dds')))
        with open(out_2, 'wb') as w:
            w.write(tex_from_dds.to_dds())

        with open(out, 'rb') as f, open(out_2, 'rb') as f_2:
            c1 = f.read()
            c2 = f_2.read()

        assert sha1(c1).hexdigest() == sha1(c2).hexdigest()
