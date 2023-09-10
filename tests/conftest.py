import os
import sys

import pytest

from albam import register, unregister
from tests.mtfw import (
    _generate_tests_arc_file_path,
    _generate_tests_from_arcs,
)


def pytest_addoption(parser):
    parser.addoption("--arcdir", help="Directory to look for arc files to test")


def pytest_sessionstart():
    register()


def pytest_sessionfinish():
    unregister()


def pytest_generate_tests(metafunc):
    if "arc_filepath" in metafunc.fixturenames:
        _generate_tests_arc_file_path(metafunc)
    if "lmt" in metafunc.fixturenames:
        _generate_tests_from_arcs("lmt", metafunc)
    if "mod" in metafunc.fixturenames:
        _generate_tests_from_arcs("mod", metafunc)
    if "mrl" in metafunc.fixturenames:
        _generate_tests_from_arcs("mrl", metafunc)
