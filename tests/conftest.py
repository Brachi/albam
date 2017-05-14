import os
from pathlib import Path
import re
import subprocess
import shutil
import tempfile

import coverage


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')
ALBAM_ROOT_DIR = Path(__file__).parent.parent
ALBAM_MODULE_DIR = ALBAM_ROOT_DIR / 'albam'
COVERAGERC_FILE = ALBAM_ROOT_DIR / '.coveragerc'
TEMPLATE_PATH = ALBAM_ROOT_DIR / 'tests' / 'run_albam.template.py'
IS_BLENDER_SETUP = False
EXPORTED_CACHE = {}


def pytest_addoption(parser):
    parser.addoption('--dirarc', help='Specified a custom folder for arc files (RE5)')
    parser.addoption('--blender', help='Path to Blender executable for performing functional tests')


def albam_import_export(blender_path, files):
    _setup_blender(blender_path)
    temp_script = tempfile.NamedTemporaryFile()
    with open(str(TEMPLATE_PATH)) as f:
        python_template = f.read()
    with open(temp_script.name, 'w') as w:
        content = python_template.format(files=files)
        w.write(content)

    args = '{} -noaudio --background --python {}'.format(blender_path, temp_script.name)
    try:
        output = subprocess.check_output((args,), shell=True)
        print(output)
    except subprocess.CalledProcessError as exc:
        print('debug', exc.output)
        raise RuntimeError('Failed to execute blender. output: {}'.format(exc.output))


def _setup_blender(blender_path):
    """
    Setup blender to be able to run tests inside of it:
    * Install albam as an addon, with the current code, overwriting existing installs
    * Add a sitecustomize.py file to be used by coverage if it's being used outside
    """
    global IS_BLENDER_SETUP
    if IS_BLENDER_SETUP:
        return

    _install_albam_as_addon(blender_path)
    blender_site_packages = _get_blender_site_packages(blender_path)
    albam_addon_source_path = _get_albam_addon_source_path(blender_path)
    _install_coverage(blender_site_packages)
    _setup_coverage_on_startup(blender_site_packages)
    blender_coveragerc = _create_coveragerc_for_blender(albam_addon_source_path)

    os.environ['COVERAGE_PROCESS_START'] = blender_coveragerc
    IS_BLENDER_SETUP = True


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


def assert_approximate_fields(obj1, obj2, attr_name, max_ratio):
    attr_1 = getattr(obj1, attr_name)
    attr_2 = getattr(obj2, attr_name)
    difference = abs(attr_1 - attr_2)
    ratio = difference / obj1.face_count

    assert ratio < max_ratio


def _get_blender_site_packages(blender_path):

    blender_dir = os.path.dirname(blender_path)
    dirs = [os.path.join(root, d) for root, dirs, _ in os.walk(blender_dir)
            for d in dirs if d == 'site-packages']

    blender_site_packages = dirs[0]

    return blender_site_packages


def _install_albam_as_addon(blender_path):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'albam')
    os.mkdir(os.path.join(temp_dir, 'albam'))
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
    with tempfile.NamedTemporaryFile() as temp_file:
        with open(temp_file.name, 'w') as w:
            w.write(script)
        cmd = '{} --background --python {}'.format(blender_path, temp_file.name)

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


def _create_coveragerc_for_blender(albam_source_path):
    # TODO: check why coverals includes python/lib sources
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    content = """[run]
branch = True
data_file = .coverage.blender
source = {}
omit = */python/lib/*
""".format(albam_source_path)
    with open(temp_file.name, 'w') as w:
        w.write(content)

    return temp_file.name
