import os

import pytest


def _cie_game_dirs(pytestconfig):
    # Reuses the shared --game-dir option (see tests/conftest.py). Local
    # directories only: an .lfs is read whole through
    # albam.engines.cie.fs.LfsFS, which has no S3-backed opener the way
    # ArcFS/SsgFS do, so an "r2://" value has nothing to resolve against here.
    parsed = {}
    for entry in pytestconfig.getoption("game_dir") or []:
        parts = entry.split("::")
        parsed[parts[0]] = parts[1]
    return parsed


@pytest.fixture(scope="session")
def game_root(pytestconfig, local_app_id):
    """
    The local game install root for local_app_id, from
    --game-dir=<app-id>::<game-root>. Unlike the other engines' equivalents
    this is a plain directory, not a mounted whole-game filesystem: there is
    no CieFS to mount (see albam/engines/cie/fs.py for why), so tests mount
    the individual archives their dataset names instead.

    Skips cleanly when no --game-dir was given for this app_id.
    """
    game_dirs = _cie_game_dirs(pytestconfig)
    if local_app_id not in game_dirs:
        pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")

    root = game_dirs[local_app_id]
    if not os.path.isdir(root):
        pytest.skip(f"--game-dir={local_app_id}::{root} does not exist")
    return root
