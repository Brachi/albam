import configparser
import os
from pathlib import Path
import re
import subprocess
import shutil

import coverage
import pytest

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')
ALBAM_ROOT_DIR = Path(__file__).parent.parent
ALBAM_MODULE_DIR = ALBAM_ROOT_DIR / 'albam'
COVERAGERC_FILE = ALBAM_ROOT_DIR / '.coveragerc'


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

    _install_albam_as_addon(tmpdir_factory.getbasetemp(), blender)
    blender_site_packages = _get_blender_site_packages(blender)
    albam_addon_source_path = _get_albam_addon_source_path(blender)
    _install_coverage(blender_site_packages)
    _setup_coverage_on_startup(blender_site_packages)
    blender_coveragerc = _create_coveragerc_for_blender(tmpdir_factory.getbasetemp(), albam_addon_source_path)

    os.environ['COVERAGE_PROCESS_START'] = blender_coveragerc

    _set_paths_in_coveragerc(albam_addon_source_path)
    yield blender
    # TODO: leave coveragerc like it was, after the session finishes


def _get_blender_site_packages(blender_path):

    blender_dir = os.path.dirname(blender_path)
    dirs = [os.path.join(root, d) for root, dirs, _ in os.walk(blender_dir)
            for d in dirs if d == 'site-packages']
    try:
        blender_site_packages = dirs[0]
    except IndexError:
        print('blender_path', blender_path)
        print('dirs', [os.path.join(root, d) for root, dirs, _ in os.walk(blender_dir)
                       for d in dirs])
        raise

    # another way, doesn't work on travis for now because of stderr messages
    '''
    expr = "import sys;print('path=', [f for f in sys.path if 'site-packages' in f][0])"
    cmd = '{} --background --python-expr "{}"'.format(blender_path, expr)
    output = subprocess.check_output(cmd, shell=True)
    blender_site_packages = re.match('path= (.*)', output.decode('utf-8')).group(1)
    assert os.path.isdir(blender_site_packages)
    '''

    return blender_site_packages


def _install_albam_as_addon(base_temp, blender_path):
    zip_path = str(base_temp.join('albam'))  # '.zip' is already appended
    shutil.make_archive(zip_path, 'zip', str(ALBAM_ROOT_DIR), str(ALBAM_MODULE_DIR.parts[-1]))

    script = """
import bpy
import sys
try:
    bpy.ops.wm.addon_install(overwrite=True, filepath='{}')
    bpy.ops.wm.addon_enable(module='albam')
except:
    sys.exit(1)
sys.exit()
""".format(zip_path + '.zip')
    script_file = base_temp.join('script_install_albam.py')
    script_file.write(script)
    cmd = '{} --background --python {}'.format(blender_path, script_file)

    subprocess.check_call(cmd, shell=True)


def _install_coverage(blender_site_packages_path):

    coverage_dir = os.path.dirname(coverage.__file__)
    dst = os.path.join(blender_site_packages_path, 'coverage')
    try:
        shutil.copytree(coverage_dir, dst)
    except FileExistsError:
        # coverage already installed
        pass


def _setup_coverage_on_startup(blender_site_packages_path):
    # for now, overwriting
    dst = os.path.join(blender_site_packages_path, 'sitecustomize.py')
    with open(dst, 'w') as w:
        w.write('import coverage\n')
        w.write('coverage.process_startup()\n')


def _get_albam_addon_source_path(blender_path):
    expr = "import albam,os;print('path=', os.path.dirname(albam.__file__))"
    cmd = '{} --background --python-expr "{}"'.format(blender_path, expr)
    output = subprocess.check_output(cmd, shell=True)
    albam_source_path = re.match('path= (.*)', output.decode('utf-8')).group(1)
    assert os.path.isdir(albam_source_path)

    return albam_source_path


def _create_coveragerc_for_blender(base_temp, albam_source_path):
    dst = base_temp.join('coveragercblender')
    content = """[run]
branch = True
data_file = .coverage.blender
source = {}
""".format(albam_source_path)
    dst.write(content)

    return str(dst)


def _set_paths_in_coveragerc(albam_addon_source_path):
    """adds [paths] to the current .coveragerc adding the source installed as addond,
    for combining both coverage files"""

    # XXX this is temporary until it's decided how albam is shipped
    # if multiple addons are installed, coverage will take all addons as missing
    # files
    albam_addon_source_path = os.path.dirname(albam_addon_source_path)

    config = configparser.ConfigParser()
    config.read([str(COVERAGERC_FILE)])
    try:
        config.add_section('paths')
    except configparser.DuplicateSectionError:
        pass
    config.set('paths', 'source', '.\n{}'.format(albam_addon_source_path))

    with open(str(COVERAGERC_FILE), 'w') as w:
        config.write(w)
