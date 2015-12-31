from albam.mtframework import Tex112
from tests.conftest import tex_re5_samples
import pytest

from albam.image_formats.dds import DDS


@pytest.mark.parametrize('tex_file', tex_re5_samples())
def test_tex_calculate_mipmap_count(tex_file):
    tex = Tex112(file_path=tex_file)

    mipmap_count_from_file = tex.mipmap_count
    mipmap_calculated = DDS.calculate_mipmap_count(tex.width, tex.height)

    # There might be cases where tex don't have mipmaps?
    assert mipmap_count_from_file == mipmap_calculated
