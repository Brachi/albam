import pytest

from albam import register, unregister


def pytest_sessionstart():
    register()


def pytest_sessionfinish():
    unregister()


def pytest_addoption(parser):
    parser.addoption(
        "--game-dir",
        action="append",
        help="Format: <app-id>::<value>: either a local game install root (recursively "
        "scanned for .arc files via MTFW_FS), or the literal 'r2://' to explicitly source "
        "that app-id from R2 instead (bucket/prefix/credentials resolved from env vars - "
        "see .env.example; never inferred from a missing local path). Used by "
        "tests/mtfw/*.py's hash-driven, catalog-verified local round-trip tests. Can be "
        "passed multiple times.",
    )


def pytest_configure(config):
    # Validate eagerly, once, at startup - not from within a fixture, where a
    # malformed value would otherwise only surface once each parametrized
    # test actually runs it, as one raw traceback per test instead of a
    # single clear message before anything even starts.
    for app_id_and_dir in config.getoption("game_dir") or []:
        parts = app_id_and_dir.split("::")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise pytest.UsageError(
                f"--game-dir={app_id_and_dir!r} is malformed: expected exactly one "
                f"'::' separator between a non-empty app-id and a non-empty directory, "
                f"e.g. --game-dir=re5::/path/to/game (a single ':' is not the separator)"
            )
