import os
import json
import pytest

from albam.engines.mtfw.structs.xfs import Xfs
from albam.engines.mtfw.config_assets import from_xfs
from tests.mtfw.scripts.catalog_paths import resolve_hashes


XFS_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "xfs_parsing_hashes.json"
)
with open(XFS_PARSING_DATASET_PATH) as f:
    XFS_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and "local_xfs_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_xfs_path_hash")
        argvalues = [(d["app_id"], d["xfs_path_hash"]) for d in XFS_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['xfs_path_hash']}" for d in XFS_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by TEX_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in XFS_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["xfs_path_hash"] in catalog_hashes, (
            f"{entry['xfs_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_xfs(game_fs_root, local_app_id, local_xfs_path_hash):
    path = resolve_hashes(game_fs_root, {local_xfs_path_hash})[local_xfs_path_hash]
    xfs_bytes = game_fs_root.readbytes(path)

    parsed = Xfs.from_bytes(xfs_bytes)
    parsed._read()
    return {"parsed": parsed, "path": path, "app_id": local_app_id}


def test_parsed_xfs_version(parsed_xfs):
    assert parsed_xfs["parsed"].header.version_major == 6
