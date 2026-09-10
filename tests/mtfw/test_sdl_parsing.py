import json
import os
import pytest
from albam.engines.mtfw.structs.sdl_156 import Sdl156

from tests.mtfw.scripts.catalog_paths import resolve_hashes

PROP_TYPES = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 14, 15, 20, 21, 22, 28, 34, 35, 36, 40, 55, 57, 58]

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
SDL_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "sdl_parsing_hashes.json")
with open(SDL_PARSING_DATASET_PATH) as f:
    SDL_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_sdl_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_sdl_path_hash")
        argvalues = [(d["app_id"], d["sdl_path_hash"]) for d in SDL_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['sdl_path_hash']}" for d in SDL_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by TEX_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in SDL_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["sdl_path_hash"] in catalog_hashes, (
            f"{entry['sdl_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_sdl(game_fs_root, local_sdl_path_hash):
    path = resolve_hashes(game_fs_root, {local_sdl_path_hash})[local_sdl_path_hash]
    sdl_bytes = game_fs_root.readbytes(path)

    parsed = Sdl156.from_bytes(sdl_bytes)
    parsed._read()
    return {"parsed": parsed,
            "path": path
            }


def test_parsed_sdl_version(parsed_sdl):
    assert parsed_sdl["parsed"].header.version == 17


def test_parsed_sdl_type(parsed_sdl):
    path = parsed_sdl["path"]
    for i, track in enumerate(parsed_sdl["parsed"].tracks):
        assert track.prop_type in PROP_TYPES, (f"the error at the track {i} file {path}")