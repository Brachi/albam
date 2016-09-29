import os
from pathlib import Path
import subprocess
import shutil

import pytest

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')
ALBAM_ROOT_DIR = Path(__file__).parent.parent
ALBAM_MODULE_DIR = ALBAM_ROOT_DIR / 'albam'


def pytest_addoption(parser):
    parser.addoption('--dirtex', help='Specified a custom folder for tex files (Re5)')
    parser.addoption('--dirarc', help='Specified a custom folder for arc files (Re5)')
    parser.addoption('--arcregex', help='Regex that will be applied while searching for arc files')
    parser.addoption('--blender', help='Path to Blender executable for performing functional tests')


@pytest.fixture(scope='session')
def setup_blender(tmpdir_factory):
    """Setups blender to be able to run tests inside of it:
    * Installs albam as an addon, with the current code, overwriting existing installs
    * Adds a sitecustomize.py file to be used by coverage if it's being used outside
    * cleanups everythings after done
    """
    blender = pytest.config.getoption('blender')
    if not blender:
        pytest.skip('No blender bin path supplied')
    assert os.path.isfile(blender)

    # install albam
    zip_path = str(tmpdir_factory.getbasetemp().join('albam'))  # '.zip' is already appended
    shutil.make_archive(zip_path, 'zip', str(ALBAM_ROOT_DIR), str(ALBAM_MODULE_DIR.parts[-1]))

    script = """
import bpy
import sys
try:
    bpy.ops.wm.addon_install(overwrite=True, filepath='{}')
except:
    sys.exit(1)
sys.exit()
""".format(zip_path + '.zip')
    script_file = tmpdir_factory.getbasetemp().join('script_install_albam.py')
    script_file.write(script)
    cmd = '{} --background --python {}'.format(blender, script_file)

    subprocess.check_output(cmd, shell=True)

    # check if coverage is being run

    return blender
