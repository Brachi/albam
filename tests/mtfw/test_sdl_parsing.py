import json
import os
import xml.etree.ElementTree as ET
import pytest
from albam.engines.mtfw.config_assets import (
    _SDL_SERIALIZED_VALUE_SIZES,
    _sdl_to_xml,
    _sdl_xml_to_bytes,
)
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


def test_real_sdl_xml_serialization_roundtrip(parsed_sdl):
    original = parsed_sdl["parsed"]
    xml = _sdl_to_xml(original).getroot()

    serialized = Sdl156.from_bytes(_sdl_xml_to_bytes(xml))
    serialized._read()

    assert serialized.header.version == original.header.version
    assert serialized.header.frame_max == original.header.frame_max
    assert serialized.header.floor_frame == original.header.floor_frame
    assert len(serialized.tracks) == len(original.tracks)
    for source_track, exported_track in zip(original.tracks, serialized.tracks):
        assert exported_track.track_type == source_track.track_type
        assert exported_track.prop_type == source_track.prop_type
        assert exported_track.parent == source_track.parent
        assert exported_track.num_frames == source_track.num_frames
        assert exported_track.name == source_track.name
        assert [
            (frame.frame, frame.type) for frame in exported_track.timing_frames
        ] == [
            (frame.frame, frame.type) for frame in source_track.timing_frames
        ]

        if (
            source_track.track_type > 5
            and source_track.prop_type not in _SDL_SERIALIZED_VALUE_SIZES
        ):
            assert exported_track.ofs_data == 0
    assert ET.tostring(_sdl_to_xml(serialized).getroot()) == ET.tostring(xml)