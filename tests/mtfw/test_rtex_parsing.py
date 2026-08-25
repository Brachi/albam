import json
import os

import pytest

from albam.engines.mtfw.texture import TEX_FORMAT_MAPPER, TEX_VERSION
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
RTEX_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "rtex_parsing_hashes.json")
with open(RTEX_PARSING_DATASET_PATH) as f:
    RTEX_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_rtex_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_rtex_path_hash")
        argvalues = [(d["app_id"], d["rtex_path_hash"]) for d in RTEX_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['rtex_path_hash']}" for d in RTEX_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by RTEX_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in RTEX_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["rtex_path_hash"] in catalog_hashes, (
            f"{entry['rtex_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_rtex(game_fs_root, local_app_id, local_rtex_path_hash):
    from albam.engines.mtfw.texture import APPID_RTEXCLS_MAP

    path = resolve_hashes(game_fs_root, {local_rtex_path_hash})[local_rtex_path_hash]
    rtex_bytes = game_fs_root.readbytes(path)
    Rtex = APPID_RTEXCLS_MAP[local_app_id]

    parsed = Rtex.from_bytes(rtex_bytes)
    parsed._read()
    return parsed


def test_parse_rtex(parsed_rtex):
    rtex = parsed_rtex
    rtex_version = rtex.version
    type_attr = "texture_type" if rtex_version == 112 else "type"
    if getattr(rtex, type_attr) == 6:
        assert rtex.num_images == 6
    assert rtex.num_images in (1, 6)
    assert rtex.compression_format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
    if rtex_version != 112:
        assert rtex.version in TEX_VERSION.values()
