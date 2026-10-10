from bisect import bisect_right
import json
import os

import pytest
from albam.engines.mtfw.structs.sdl_156 import Sdl156

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


def test_sdl_data_block_boundaries_from_offsets(parsed_sdl):
    """Infer value-size candidates from each data block's next section offset."""
    sdl = parsed_sdl["parsed"]
    path = parsed_sdl["path"]
    section_offsets = sorted({
        sdl.header.ofs_names,
        *(
            offset
            for track in sdl.tracks
            for offset in (track.ofs_timing, track.ofs_data)
            if offset > 0
        ),
    })
    size_candidates_by_type = {}
    observations_by_type = {}

    for track_index, track in enumerate(sdl.tracks):
        if track.track_type <= 5 or track.num_frames == 0 or track.ofs_data == 0:
            continue

        data_end_index = bisect_right(section_offsets, track.ofs_data)
        data_end = (
            section_offsets[data_end_index]
            if data_end_index < len(section_offsets)
            else sdl.header.ofs_names
        )
        timing_end = track.ofs_timing + track.num_frames * 4
        data_size = data_end - track.ofs_data

        assert timing_end <= track.ofs_data, (
            f"track {track_index} ({track.name!r}, type {track.prop_type}) "
            f"timing ends at {timing_end}, after data begins at {track.ofs_data} "
            f"in {path}"
        )
        assert track.ofs_data < data_end <= sdl.header.ofs_names, (
            f"track {track_index} ({track.name!r}, type {track.prop_type}) "
            f"has invalid data boundary {track.ofs_data}:{data_end} "
            f"(ofs_names={sdl.header.ofs_names}) in {path}"
        )
        assert data_size % 4 == 0, (
            f"track {track_index} ({track.name!r}, type {track.prop_type}) "
            f"data block size {data_size} is not 4-byte aligned in {path}"
        )

        candidates = {
            value_size
            for value_size in range(1, data_size // track.num_frames + 2)
            if ((track.num_frames * value_size + 3) // 4) * 4 == data_size
        }
        observation = (
            f"track {track_index} {track.name!r}: "
            f"frames={track.num_frames}, data={track.ofs_data}:{data_end}, "
            f"block_size={data_size}, candidate_value_sizes={sorted(candidates)}"
        )
        assert candidates, f"No aligned value size fits {observation} in {path}"

        prop_type = track.prop_type
        if prop_type not in size_candidates_by_type:
            size_candidates_by_type[prop_type] = candidates
            observations_by_type[prop_type] = []
        else:
            size_candidates_by_type[prop_type] &= candidates
        observations_by_type[prop_type].append(observation)

    for prop_type, candidates in size_candidates_by_type.items():
        assert candidates, (
            f"Inconsistent measured data boundaries for property type {prop_type} "
            f"in {path}: {'; '.join(observations_by_type[prop_type])}"
        )