import json
import os

import pytest
from albam.engines.mtfw.structs.sdl_156 import Sdl156
from albam.engines.mtfw.config_assets import SDL_DATA_STRUCT_SIZES
from albam.lib.mt_classes import RV_MTPROPERTY_RE5

from tests.mtfw.scripts.catalog_paths import resolve_hashes

PROP_TYPES = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 14, 15, 20, 21, 22, 24, 28, 34, 35, 36, 40, 55, 57, 58]

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


def test_data_postion(parsed_sdl):
    for i, track in enumerate(parsed_sdl["parsed"].tracks):
        if track.track_type > 5 and track.num_frames > 0 and track.ofs_data:
            assert track.ofs_data % 16 == 0, (
                f"the data offset is not 16-byte aligned at track {i} "
                f"in {parsed_sdl['path']}"
            )


def test_sdl_data_block_boundaries_from_timing_frames(parsed_sdl):
    """Confirm data sizes only where a following timing block gives a boundary."""
    sdl = parsed_sdl["parsed"]
    path = parsed_sdl["path"]
    timing_offsets = sorted({track.ofs_timing for track in sdl.tracks if track.ofs_timing > 0})

    for track_index, track in enumerate(sdl.tracks):
        if track.track_type <= 5 or track.num_frames == 0 or track.ofs_data == 0:
            continue

        prop_type_name = RV_MTPROPERTY_RE5.get(track.prop_type)
        expected_size = SDL_DATA_STRUCT_SIZES.get(prop_type_name)
        if expected_size is None:
            continue

        following_timing_offsets = [offset for offset in timing_offsets if offset > track.ofs_data]
        if not following_timing_offsets:
            # A final data block cannot prove its size from a timing-frame boundary.
            continue

        data_end = following_timing_offsets[0]
        data_size = data_end - track.ofs_data
        if prop_type_name == "TYPE_BOOL":
            # Bool keys are byte-packed; 4 bytes in the size table includes
            # padding for one value. A list is padded only at its end.
            expected_block_size = (track.num_frames + 3) // 4 * 4
        else:
            expected_block_size = track.num_frames * expected_size

        timing_end = track.ofs_timing + track.num_frames * 4
        observation = (
            f"track {track_index} {track.name!r}: frames={track.num_frames}, "
            f"data={track.ofs_data}:{data_end}, block_size={data_size}, "
            f"expected_block_size={expected_block_size}"
        )
        assert timing_end <= track.ofs_data, (
            f"timing frames end at {timing_end}, after data begins at "
            f"{track.ofs_data} for {observation} in {path}"
        )
        assert track.ofs_data < data_end <= sdl.header.ofs_names, (
            f"invalid timing-frame data boundary for {observation} "
            f"(ofs_names={sdl.header.ofs_names}) in {path}"
        )
        assert data_size == expected_block_size, (
            f"SDL_DATA_STRUCT_SIZES[{prop_type_name!r}]={expected_size} with "
            f"{track.num_frames} frames implies {expected_block_size} bytes, "
            f"but got {data_size} for {observation} in {path}"
        )
