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


from albam.engines.mtfw.animation import USAGE
SUPPORTED_LMT_VERSIONS = (51, 67)
SUPPORTED_BUFFER_TYPES = [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
LOCATION = [1, 4]
ROTATION = [0, 3]
SCALE = [2, 5]
BOUNDS_BUFF_TYPES = [4, 5, 7, 11, 12, 13, 14, 15]
JOINT_TYPES = [0, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 42, 43, 44, 48, 49]
BONES_WITH_JOINT_TYPES = [16, 11, 20, 6, 254]  # 20: "thigh_l",
# re0 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re1 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# rev1 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13]
# rev2 [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]
# re 5[2, 4, 6, 9]
# re 6[1, 2, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15]


def test_lmt(parsed_lmt):
    lmt = parsed_lmt
    assert lmt.id_magic == b"LMT\x00"
    assert lmt.version in SUPPORTED_LMT_VERSIONS
    assert lmt.num_block_offsets == len(lmt.block_offsets)
    anim_blocks = {ab.block_header for ab in lmt.block_offsets if ab.offset != 0}

    for ab in anim_blocks:
        if lmt.version == 67:
            assert ab.seq_num == 4  # as 3 bit value probably constant
            if ab.kf_num > 0:
                assert ab.kf_num == 4
        tracks = getattr(ab, "tracks")
        for tr in tracks:
            assert tr.joint_type in JOINT_TYPES
            assert tr.buffer_type in SUPPORTED_BUFFER_TYPES
            if tr.buffer_type == 1:
                assert tr.usage in LOCATION or tr.usage in SCALE
                assert tr.len_data == 0
            elif tr.buffer_type == 2:
                if lmt.version == 51:
                    assert tr.usage in SCALE or tr.usage in LOCATION  # RE5
                else:
                    assert tr.usage in ROTATION
                    assert tr.len_data % 12 == 0
            elif tr.buffer_type == 3:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.len_data % 16 == 0
            elif tr.buffer_type == 4:
                if lmt.version == 51:
                    assert tr.usage in ROTATION  # RE5
                    assert tr.len_data % 12 == 0
                else:
                    assert tr.usage in SCALE or tr.usage in LOCATION
                    assert tr.ofs_bounds != 0
                    assert tr.len_data % 8 == 0
            elif tr.buffer_type == 5:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 6:
                assert tr.usage in ROTATION
                assert tr.len_data % 8 == 0
            elif tr.buffer_type == 7:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 9:
                assert tr.usage in SCALE or tr.usage in LOCATION
                assert tr.len_data % 16 == 0
            elif tr.buffer_type == 11:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 12:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 13:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 4 == 0
            elif tr.buffer_type == 14:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 6 == 0
            elif tr.buffer_type == 15:
                assert tr.usage in ROTATION
                assert tr.ofs_bounds != 0
                assert tr.len_data % 5 == 0


def is_strictly_increasing(lst):
    return all(lst[i] < lst[i + 1] for i in range(len(lst) - 1))


def test_joint(parsed_lmt):
    lmt = parsed_lmt
    anim_blocks = {ab.block_header for ab in lmt.block_offsets if ab.offset != 0}
    for ab in anim_blocks:
        assert ab.loop_frame in (-1, 0, 1)
        tracks = getattr(ab, "tracks")
        bones_joint_index = []
        seq = {}
        for track in tracks:
            # looks like 254 is some index for multiple service objects
            if track.bone_index == 254:
                # FAILED [fig29.arc::id\\figdata\\fig29\\fig29.lmt]
                # FAILED [uOma004_Collapse.arc::pawn\\om\\oma004\\motion\\oma004_pf.lmt]
                assert track.joint_type != 0
            if track.bone_index not in (254, 255):
                key = (track.bone_index, track.usage, track.joint_type)
                # assert key not in bones_joint_index
                bones_joint_index.append(key)
                if track.bone_index not in seq:
                    seq[track.bone_index] = [track.usage]
                else:
                    seq[track.bone_index].append(track.usage)
        for k, v in seq.items():
            if len(v) > 1:
                # looks like it's a sequence of usage per bone [rotation, translation, scale]
                assert is_strictly_increasing(v)


def test_joint_type_usage(parsed_lmt):
    lmt = parsed_lmt
    anim_blocks = {ab.block_header for ab in lmt.block_offsets if ab.offset != 0}
    for ab in anim_blocks:
        tracks = getattr(ab, "tracks")
        joint_types = {}
        for track in tracks:
            usage_str = USAGE.get(track.usage)
            cur_joint_type = joint_types.get((track.bone_index, usage_str), None)
            if cur_joint_type is None:
                joint_types[(track.bone_index, usage_str)] = track.joint_type
            else:
                assert cur_joint_type == joint_types[(track.bone_index, usage_str)]
                assert track.bone_index in (0, 254, 255)
                print(track.bone_index, usage_str)
