import json
import os

import pytest

from albam.engines.mtfw.collision import KNOWN_RUNTIME_ATTR
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
SBC_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "sbc_parsing_hashes.json")
with open(SBC_PARSING_DATASET_PATH) as f:
    SBC_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_sbc_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_sbc_path_hash")
        argvalues = [(d["app_id"], d["sbc_path_hash"]) for d in SBC_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['sbc_path_hash']}" for d in SBC_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by SBC_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in SBC_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["sbc_path_hash"] in catalog_hashes, (
            f"{entry['sbc_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_sbc(game_fs_root, local_app_id, local_sbc_path_hash):
    from albam.engines.mtfw.collision import APPID_SBC_CLASS_MAPPER

    path = resolve_hashes(game_fs_root, {local_sbc_path_hash})[local_sbc_path_hash]
    sbc_bytes = game_fs_root.readbytes(path)
    SBC = APPID_SBC_CLASS_MAPPER[local_app_id]

    parsed_sbc = SBC.from_bytes(sbc_bytes)
    parsed_sbc._read()

    return parsed_sbc


SBC_MAGIC_ID = [49, 255]
KNOWN_NODE156_BIT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 15, 17, 19, 20, 21, 23, 29, 30, 31, 33,
                     45, 47, 53, 55, 61, 63, 64, 67, 69, 76, 127, 128, 129, 195,
                     200, 207, 216, 225, 227, 237, 239, 245, 255]

KNOWN_TYPE156 = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 8192, 16384, 32768, 131072,
                 524288, 1048576, 209715, 262144, 4194304, 2097152, 8388608, 67108864, 536870912,
                 134217728,]  # power of 2 flags ?

KNOWN_SBC_INFO156_ID = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 15, 17, 18, 19, 20, 21, 22, 23,
                        24, 25, 26, 27, 28, 29, 31, 30, 32, 33, 35, 34, 37, 307, 308, 309, 310, 311, 500, 501,
                        502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 4294967295]

KNOWN_SPECIAL_ATTR = [0]
KNOWN_SURFACE_ATTR = [0]

SBC21_VERSION = [2011120601,  # rev2
                 2010091000,  # re6
                 ]


def test_parsed_sbc(parsed_sbc):
    sbc = parsed_sbc
    magic = sbc.header.indent
    assert magic[3] in SBC_MAGIC_ID
    if magic[3] == 255:
        assert sbc.header.unk_00 in SBC21_VERSION
        for info in sbc.sbc_bvhc:
            assert info.num_nodes > 0
        assert sbc.bvh.num_nodes > 0
    elif magic[3] == 49:
        sbc_info = [info for info in sbc.sbc_info]
        assert sbc_info[0].start_nodes == sbc.header.num_objects_nodes
        for info in sbc_info:
            assert info.base == 0
            assert info.index_id in KNOWN_SBC_INFO156_ID
        for i, node in enumerate(sbc.nodes):
            if i < sbc.header.num_objects_nodes:
                # doesn't pass for s107h_sr1 s109h_scr s205h_eff s205h_scr s304h_scr s312h_scr s316h_eff
                # s316h_scr
                assert node.boxes[0].min[0] == sbc_info[i].vmin[0].x
                assert node.boxes[0].min[1] == sbc_info[i].vmin[0].y
                assert node.boxes[0].min[2] == sbc_info[i].vmin[0].z

                assert node.boxes[1].min[0] == sbc_info[i].vmin[1].x
                assert node.boxes[1].min[1] == sbc_info[i].vmin[1].y
                assert node.boxes[1].min[2] == sbc_info[i].vmin[1].z

                assert node.boxes[0].max[0] == sbc_info[i].vmax[0].x
                assert node.boxes[0].max[1] == sbc_info[i].vmax[0].y
                assert node.boxes[0].max[2] == sbc_info[i].vmax[0].z

                assert node.boxes[1].max[0] == sbc_info[i].vmax[1].x
                assert node.boxes[1].max[1] == sbc_info[i].vmax[1].y
                assert node.boxes[1].max[2] == sbc_info[i].vmax[1].z
                sbc_child0 = sbc_info[i].child_index[0]
                sbc_child1 = sbc_info[i].child_index[1]
                if sbc_child0:
                    assert node.child_index[0] == sbc_child0
                if sbc_child1:
                    assert node.child_index[1] == sbc_child1
        for face in sbc.faces:
            assert face.runtime_attr in KNOWN_RUNTIME_ATTR
            assert face.type in KNOWN_TYPE156
            assert face.special_attr in KNOWN_SPECIAL_ATTR
            assert face.surface_attr in KNOWN_SURFACE_ATTR
            assert face.unk_02 == 0
