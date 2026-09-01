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
def parsed_lmt(game_fs_root, local_app_id, local_lmt_path_hash):
    from albam.engines.mtfw.structs.lmt import Lmt
    from albam.lib.kaitai_utils import parse

    path = resolve_hashes(game_fs_root, {local_lmt_path_hash})[local_lmt_path_hash]
    src_bytes = game_fs_root.readbytes(path)

    lmt = parse(Lmt, src_bytes, local_app_id)
    return lmt, src_bytes


SUPPORTED_LMT_VERSIONS = (51, 67)
MAX_BONE_INDEX = 255


def test_lmt(parsed_lmt):
    lmt, _ = parsed_lmt
    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)


def test_lmt_blocks_are_not_empty(parsed_lmt):
    """A .lmt whose offsets are read at the wrong width still parses, it just
    yields blocks that all look empty - which is silently indistinguishable
    from "this file has no animation" further up in the importer.
    """
    lmt, src_bytes = parsed_lmt
    blocks = [b for b in lmt.block_offsets if b.offset != 0]

    assert blocks, "every block offset is 0"
    for block in blocks:
        assert block.offset < len(src_bytes)

    animated = [b for b in blocks if b.block_header.num_tracks > 0]
    assert animated, "no block declares any track"


def test_lmt_tracks_point_inside_the_file(parsed_lmt):
    lmt, src_bytes = parsed_lmt
    num_tracks_with_data = 0

    for block in lmt.block_offsets:
        if block.offset == 0:
            continue
        header = block.block_header
        assert header.ofs_frame < len(src_bytes)
        for track in header.tracks:
            assert track.bone_index <= MAX_BONE_INDEX
            assert track.ofs_data + track.len_data <= len(src_bytes)
            if track.ofs_data and track.len_data:
                num_tracks_with_data += 1
                assert len(track.data) == track.len_data
            if lmt.version != 67:
                continue
            assert 0.0 <= track.weight <= 1.0
            if track.ofs_floats.ofs_buffer:
                assert track.ofs_floats.ofs_buffer < len(src_bytes)
                assert len(track.ofs_floats.body.unk_00) == 8

    assert num_tracks_with_data, "no track carries any keyframe data"
