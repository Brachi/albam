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
        help="Format: <app-id>::<value>[::<path-list>]: <value> is either a local game "
        "install root (recursively scanned for .arc files via MTFW_FS), or the literal "
        "'r2://' to explicitly source that app-id from R2 instead (bucket/prefix/"
        "credentials resolved from env vars - see .env.example; never inferred from a "
        "missing local path). The optional third segment is reng-only (a .pak's file "
        "entries carry only hashes, not paths, so an external candidate-path list is "
        "required - see albam/engines/reng/pak_fs.py's module docstring): a local path, "
        "or 'r2://<key>' to fetch it from the same shared bucket instead, where <key> is "
        "the key it was uploaded under, relative to the app's own R2 prefix. MTFW apps "
        "ignore a third segment if given. Used by tests/mtfw/*.py and tests/reng/*.py's "
        "hash-driven, catalog-verified local round-trip tests. Can be passed multiple "
        "times.",
    )


def pytest_configure(config):
    # Validate eagerly, once, at startup - not from within a fixture, where a
    # malformed value would otherwise only surface once each parametrized
    # test actually runs it, as one raw traceback per test instead of a
    # single clear message before anything even starts.
    for app_id_and_dir in config.getoption("game_dir") or []:
        parts = app_id_and_dir.split("::")
        if len(parts) not in (2, 3) or not all(parts):
            raise pytest.UsageError(
                f"--game-dir={app_id_and_dir!r} is malformed: expected a non-empty "
                f"app-id and a non-empty value, joined by '::', with an optional third "
                f"'::'-joined non-empty segment (reng's path-list - see --help), e.g. "
                f"--game-dir=re5::/path/to/game or --game-dir=re3::/path/to/re3::"
                f"/path/to/list.txt (a single ':' is not the separator)"
            )
