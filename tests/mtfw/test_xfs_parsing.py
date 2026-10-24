import os
import json
import pytest

from albam.engines.mtfw.structs.xfs import Xfs
from albam.engines.mtfw.config_assets import from_xfs
from tests.mtfw.scripts.catalog_paths import resolve_hashes


LOT_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "lot_parsing_hashes.json")
with open(LOT_PARSING_DATASET_PATH) as f:
    LOT_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_lot_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_lot_path_hash")
        argvalues = [(d["app_id"], d["lot_path_hash"]) for d in LOT_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['lot_path_hash']}" for d in LOT_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by TEX_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in LOT_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["lot_path_hash"] in catalog_hashes, (
            f"{entry['lot_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_lot(game_fs_root, local_lot_path_hash):
    path = resolve_hashes(game_fs_root, {local_lot_path_hash})[local_lot_path_hash]
    lot_bytes = game_fs_root.readbytes(path)

    parsed = Xfs.from_bytes(lot_bytes)
    parsed._read()
    return parsed


def test_xfs_lot_imports_real_sample(parsed_lot, local_app_id):
    xfs = parsed_lot

    xml = from_xfs(xfs, "lot", local_app_id)
    root = xml.getroot()

    assert root.tag == "root"
    assert root.get("extension") == "lot"
    root_class = root.find("./class")
    assert root_class is not None
    assert root_class.get("class_index") == "0"
    # XFS stores the root body directly; object indexes belong only to
    # nested ObjectRef values.
    assert "object_index" not in root_class.attrib

    class_defs = root.findall("./_xfs_metadata/class_def")
    assert len(class_defs) == xfs.header.num_class_defs
    assert [int(class_def.get("index")) for class_def in class_defs] == list(
        range(xfs.header.num_class_defs)
    )
