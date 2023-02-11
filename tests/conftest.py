import os

import pytest

from albam import register, unregister


def pytest_addoption(parser):
    parser.addoption("--arcdir", help="Directory to look for arc files to test")


def pytest_sessionstart():
    register()


def pytest_sessionfinish():
    unregister()


def pytest_generate_tests(metafunc):
    if "arc_filepath" in metafunc.fixturenames:
        arc_dir = metafunc.config.getoption("arcdir")
        if not arc_dir:
            pytest.skip("No arc directory supplied")
        else:
            ARC_FILES = [
                os.path.join(root, f)
                for root, _, files in os.walk(arc_dir)
                for f in files
                if f.endswith(".arc")
            ]
            arc_names = [os.path.basename(f) for f in ARC_FILES]
            metafunc.parametrize("arc_filepath", ARC_FILES, scope="module", ids=arc_names)
