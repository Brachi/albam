from albam import register, unregister


def pytest_sessionstart():
    register()


def pytest_sessionfinish():
    unregister()


def pytest_addoption(parser):
    # TODO: use apps enum
    parser.addoption(
        "--arcdir",
        action="append",
        help="Format: <app-id>::<dir>: Directory to look for arc files "
        "to test with the app-id provided. Can be passed multiple times",
    )
    parser.addoption(
        "--mtfw-dataset",
        action="store",
        help="Path to json file containing files to import. See tests/mtfw/datasets for examples"
    )
    parser.addoption(
        "--game-dir",
        action="append",
        help="Format: <app-id>::<dir>: Local game install root (recursively scanned for .arc "
        "files via MTFW_FS, not a flat directory of loose .arc dumps like --arcdir). Used by "
        "tests/mtfw/test_mod_serialization.py's local round-trip tests. Can be passed multiple "
        "times.",
    )
