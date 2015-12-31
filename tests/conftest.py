import csv
import os

import pytest


CSV_HEADERS_WRITTEN = False
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')


def pytest_addoption(parser):
    parser.addoption('--runslow', action='store_true', help='run slow tests')
    parser.addoption('--dirmod', help='Specified a custom folder for mod files (Re5)')
    parser.addoption('--dirtex', help='Specified a custom folder for tex files (Re5)')
    parser.addoption('--dirarc', help='Specified a custom folder for arc files (Re5)')
    parser.addoption('--blender', help='Path to Blender executable for performing functional tests')
    parser.addoption('--csvoutmod', help='')
    parser.addoption('--csvoutmodmesh', help='')


@pytest.fixture(scope='session')
def mod_debug_csv_writer(request, pytestconfig):
    out = pytestconfig.getoption('csvoutmod')
    if not out:
        return
    f = open(out, 'w')
    csv_writer = csv.writer(f)

    def tear_down():
        f.close()
    request.addfinalizer(tear_down)
    return {'ob': csv_writer, 'headers_written': CSV_HEADERS_WRITTEN}


@pytest.fixture(scope='session')
def modmesh_debug_csv_writer(request, pytestconfig):
    out = pytestconfig.getoption('csvoutmodmesh')
    if not out:
        return
    f = open(out, 'w')
    csv_writer = csv.writer(f)

    def tear_down():
        f.close()
    request.addfinalizer(tear_down)
    return {'ob': csv_writer, 'headers_written': CSV_HEADERS_WRITTEN}


@pytest.fixture(scope='session')
def arc_re5_samples(config=None):
    samples_dir = pytest.config.getoption('--dirarc') or os.path.join(SAMPLES_DIR, 're5/arc')
    return [os.path.join(root, f)
            for root, _, files in os.walk(samples_dir)
            for f in files if f.endswith('.arc')]


@pytest.fixture(scope='session')
def mod_re5_samples():
    samples_dir = pytest.config.getoption('--dirmod') or os.path.join(SAMPLES_DIR, 're5/mod')
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]


@pytest.fixture(scope='session')
def tex_re5_samples():
    samples_dir = pytest.config.getoption('--dirtex') or os.path.join(SAMPLES_DIR, 're5/tex')
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]


@pytest.fixture(scope='session')
def dds_samples():
    samples_dir = pytest.config.getoption('--dirtex') or os.path.join(SAMPLES_DIR, 'dds')
    return [os.path.join(samples_dir, f) for f in os.listdir(samples_dir)]
