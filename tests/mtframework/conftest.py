from collections import namedtuple
import ctypes
import os
from tempfile import TemporaryDirectory, gettempdir
import subprocess

import pytest

from albam.engines.mtframework import Arc, Mod156, KNOWN_ARC_BLENDER_CRASH, Tex112
from tests.conftest import SAMPLES_DIR, PYTHON_TEMPLATE

ARC_SAMPLES_DIR = os.path.join(SAMPLES_DIR, 're5/arc')
ARC_FILES = [os.path.join(root, f) for root, _, files in os.walk(ARC_SAMPLES_DIR)
             for f in files if f.endswith('.arc')]

RE5UnpackedData = namedtuple('RE5UnpackedData', ('mods_original', 'textures_original',
                                                 'mods_exported', 'textures_exported'))


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


@pytest.fixture(scope='module', params=ARC_FILES)
def re5_unpacked_data(request, tmpdir_factory, setup_blender):
    import_arc_filepath = request.param
    if import_arc_filepath.endswith(tuple(KNOWN_ARC_BLENDER_CRASH)):
        pytest.xfail('Known arc crashes blender')
    log_filepath = str(tmpdir_factory.getbasetemp().join('blender.log'))
    import_unpack_dir = TemporaryDirectory()
    export_arc_filepath = os.path.join(gettempdir(), os.path.basename(import_arc_filepath))
    script_filepath = os.path.join(gettempdir(), 'import_arc.py')

    with open(script_filepath, 'w') as w:
        w.write(PYTHON_TEMPLATE.format(project_dir=os.getcwd(),
                                       import_arc_filepath=import_arc_filepath,
                                       export_arc_filepath=export_arc_filepath,
                                       import_unpack_dir=import_unpack_dir.name,
                                       log_filepath=log_filepath))
    args = '{} -noaudio --background --python {}'.format(setup_blender, script_filepath)
    try:
        subprocess.check_output((args,), shell=True)
    except subprocess.CalledProcessError:
        # the test will actually error here, if the import/export fails, since the file won't exist.
        # which is better, since pytest traceback to subprocess.check_output is pretty long and useless
        with open(log_filepath) as f:
            for line in f:
                print(line)
        try:
            os.unlink(export_arc_filepath)
            os.unlink(script_filepath)
        except FileNotFoundError:
            pass
        raise

    export_unpack_dir = TemporaryDirectory()
    arc = Arc(export_arc_filepath)
    arc.unpack(export_unpack_dir.name)

    mod_files_original = [os.path.join(root, f) for root, _, files in os.walk(import_unpack_dir.name)
                          for f in files if f.endswith('.mod')]
    mod_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_unpack_dir.name)
                          for f in files if f.endswith('.mod')]

    tex_files_original = [os.path.join(root, f) for root, _, files in os.walk(import_unpack_dir.name)
                          for f in files if f.endswith('.tex')]

    tex_files_exported = [os.path.join(root, f) for root, _, files in os.walk(export_unpack_dir.name)
                          for f in files if f.endswith('.tex')]

    mod_files_original = sorted(mod_files_original, key=os.path.basename)
    mod_files_exported = sorted(mod_files_exported, key=os.path.basename)
    tex_files_original = sorted(tex_files_original, key=os.path.basename)
    tex_files_exported = sorted(tex_files_exported, key=os.path.basename)
    tex_files_original = [Tex112(fp) for fp in tex_files_original]
    tex_files_exported = [Tex112(fp) for fp in tex_files_exported]
    mod_objects_original = []
    mod_objects_exported = []
    if mod_files_original and mod_files_exported:
        os.unlink(export_arc_filepath)
        os.unlink(script_filepath)
        for i, mod_file_original in enumerate(mod_files_original):
            mod_original = Mod156(file_path=mod_file_original)
            mod_exported = Mod156(file_path=mod_files_exported[i])
            mod_objects_original.append(mod_original)
            mod_objects_exported.append(mod_exported)
    else:
        os.unlink(export_arc_filepath)
        os.unlink(script_filepath)
        pytest.skip('Arc contains no mod files')
    return RE5UnpackedData(mods_original=mod_objects_original,
                           mods_exported=mod_objects_exported,
                           textures_original=tex_files_original,
                           textures_exported=tex_files_exported)
