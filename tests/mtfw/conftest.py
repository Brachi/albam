import os

import pytest


class FileWrapper:
    def __init__(self, file_path):
        self.name = os.path.basename(file_path)


@pytest.fixture
def lmt(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.structs.lmt import Lmt

    arc = request.param[0]
    file_entry = request.param[1]

    src_bytes = arc.get_file(file_entry.file_path, file_entry.file_type)

    parsed = Lmt.from_bytes(src_bytes)
    parsed._arc_name = os.path.basename(arc.file_path)
    parsed._file_path = file_entry.file_path

    return parsed


@pytest.fixture
def mrl(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.structs.mrl import Mrl
    arc = request.param[0]
    mrl_file_entry = request.param[1]

    mrl_bytes = arc.get_file(mrl_file_entry.file_path, mrl_file_entry.file_type)
    parsed_mrl = Mrl.from_bytes(mrl_bytes)
    parsed_mrl._read()
    parsed_mrl._arc_name = os.path.basename(arc.file_path)
    parsed_mrl._mrl_path = mrl_file_entry.file_path
    parsed_mrl._num_bytes = len(mrl_bytes)

    return parsed_mrl


@pytest.fixture
def mod(request):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.mesh import MOD_CLASS_MAPPER

    arc = request.param[0]
    file_entry = request.param[1]

    src_bytes = arc.get_file(file_entry.file_path, file_entry.file_type)
    mod_version = src_bytes[4]
    ModCls = MOD_CLASS_MAPPER[mod_version]

    parsed = ModCls.from_bytes(src_bytes)
    parsed._read()
    parsed._arc_name = os.path.basename(arc.file_path)
    parsed._src_bytes = src_bytes
    parsed._file_path = file_entry.file_path

    return parsed


@pytest.fixture
def tex(request):
    # FIXME: unify 112 with 157 or get app_id from config and decide here

    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.structs.tex_157 import Tex157
    arc = request.param[0]
    tex_file_entry = request.param[1]

    tex_bytes = arc.get_file(tex_file_entry.file_path, tex_file_entry.file_type)
    parsed_tex = Tex157.from_bytes(tex_bytes)
    parsed_tex._read()
    parsed_tex._arc_name = os.path.basename(arc.file_path)
    parsed_tex._mrl_path = tex_file_entry.file_path
    parsed_tex._num_bytes = len(tex_bytes)

    return parsed_tex
