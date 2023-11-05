from albam import register, unregister
from tests.mtfw import (
    _generate_tests_arc_file_path,
    _generate_tests_from_arcs,
)


def pytest_addoption(parser):
    # TODO: use apps enum
    parser.addoption(
        "--arcdir",
        action="append",
        help="Format: <app-id>::<dir>: Directory to look for arc files "
        "to test with the app-id provieded. Can be passed multiple times",
    )


def pytest_sessionstart():
    register()


def pytest_sessionfinish():
    unregister()


def pytest_generate_tests(metafunc):
    if "arc_file" in metafunc.fixturenames:
        _generate_tests_arc_file_path(metafunc)
    if "lmt" in metafunc.fixturenames:
        _generate_tests_from_arcs("lmt", metafunc)
    if "mod" in metafunc.fixturenames:
        _generate_tests_from_arcs("mod", metafunc)
    if "mrl" in metafunc.fixturenames:
        _generate_tests_from_arcs("mrl", metafunc)
    if "tex" in metafunc.fixturenames:
        _generate_tests_from_arcs("tex", metafunc)
