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

    yield blender
    # TODO: see pytest_sessionfinish


def pytest_sessionfinish(session, exitstatus):
    # None of these work!!! No idea way. Tried both
    # doing ```coverage combine``` after the tests finishes does the job.
    # TODO: combine automatically and change .coveragerc back to its original state
    # Maybe see if coverage API could be improved to avoid using the coveragerc
    # to get the paths
    """
    option 1
    cmd = ('python3', '-m', 'coverage', 'combine')
    subprocess.check_call(cmd)
    """
    """
    option 2
    cov = coverage.Coverage()
    cov.combine()
    """


def assert_same_attributes(obj1, obj2, attr, binary=False, length=False):
    attr_1 = getattr(obj1, attr)
    attr_2 = getattr(obj2, attr)
    if binary:
        attr_1 = bytes(attr_1)
        attr_2 = bytes(attr_2)
    elif length:
        attr_1 = len(attr_1)
        attr_2 = len(attr_2)
    assert attr_1 == attr_2


def _get_blender_site_packages(blender_path):

    blender_dir = os.path.dirname(blender_path)
    dirs = [os.path.join(root, d) for root, dirs, _ in os.walk(blender_dir)
            for d in dirs if d == 'site-packages']

    blender_site_packages = dirs[0]

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
    albam_source_path = re.search('.*path= (.*)', output.decode('utf-8')).group(1)
    assert os.path.isdir(albam_source_path)

    return albam_source_path


def _create_coveragerc_for_blender(base_temp, albam_source_path):
    # TODO: check why coverals includes python/lib sources
    dst = base_temp.join('.coveragercblender')
    content = """[run]
branch = True
data_file = .coverage.blender
source = {}
omit = */python/lib/*
""".format(albam_source_path)
    dst.write(content)

    return str(dst)


PYTHON_TEMPLATE = """import os
import logging
import sys
import time
sys.path.append('{project_dir}')
import bpy

from albam import register

logging.basicConfig(filename='{log_filepath}', level=logging.DEBUG)
logging.debug('Importing {import_arc_filepath}')

try:
    register()
except ValueError:  # The addon is already installed in blender.
    pass

try:
    start = time.time()
    logging.debug('Importing {import_arc_filepath}')

    file_path = '{import_arc_filepath}'
    bpy.ops.albam_import.item(files=[{{'name': file_path}}], unpack_dir='{import_unpack_dir}')

    logging.debug('Import time: {{}} seconds [{import_arc_filepath}])'.format(round(time.time() - start, 2)))
except Exception:
    logging.exception('IMPORT failed: {import_arc_filepath}')
    sys.exit(1)
time.sleep(4)
try:
    imported_name = os.path.basename('{import_arc_filepath}')
    start = time.time()
    bpy.context.scene.albam_item_to_export = imported_name
    bpy.ops.albam_export.item(filepath='{export_arc_filepath}')
    logging.debug('Export time: {{}} seconds [{import_arc_filepath}]'.format(round(time.time() - start, 2)))
except Exception:
    logging.exception('EXPORT failed: {import_arc_filepath}')
    sys.exit(1)
"""
