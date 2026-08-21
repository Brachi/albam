import json
import os

import pytest

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
LMT_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "lmt_parsing_hashes.json")
with open(LMT_PARSING_DATASET_PATH) as f:
    LMT_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_lmt_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_lmt_path_hash")
        argvalues = [(d["app_id"], d["lmt_path_hash"]) for d in LMT_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['lmt_path_hash']}" for d in LMT_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by LMT_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in LMT_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["lmt_path_hash"] in catalog_hashes, (
            f"{entry['lmt_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_lmt(game_fs_root, local_lmt_path_hash):
    from albam.engines.mtfw.structs.lmt import Lmt

    path = resolve_hashes(game_fs_root, {local_lmt_path_hash})[local_lmt_path_hash]
    src_bytes = game_fs_root.readbytes(path)

    lmt = Lmt.from_bytes(src_bytes)
    lmt._read()
    return lmt


SUPPORTED_LMT_VERSIONS = (51, 67)


def test_lmt(parsed_lmt):
    lmt = parsed_lmt
    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
