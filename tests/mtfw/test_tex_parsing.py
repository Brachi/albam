import json
import os

import pytest

from albam.engines.mtfw.texture import (
    TEX_FORMAT_MAPPER,
    TEX_VERSION,
    Tex157,
    Tex112
)
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
TEX_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "tex_parsing_hashes.json")
with open(TEX_PARSING_DATASET_PATH) as f:
    TEX_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_tex_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_tex_path_hash")
        argvalues = [(d["app_id"], d["tex_path_hash"]) for d in TEX_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['tex_path_hash']}" for d in TEX_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by TEX_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in TEX_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["tex_path_hash"] in catalog_hashes, (
            f"{entry['tex_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_tex(game_fs_root, local_app_id, local_tex_path_hash):
    from albam.engines.mtfw.texture import APPID_TEXCLS_MAP

    path = resolve_hashes(game_fs_root, {local_tex_path_hash})[local_tex_path_hash]
    tex_bytes = game_fs_root.readbytes(path)
    Tex = APPID_TEXCLS_MAP[local_app_id]

    parsed = Tex.from_bytes(tex_bytes)
    parsed._read()
    return parsed


ACCEPTABLE_SIZES = {2 ** n for n in range(2, 12)}  # min:8; max:2048
ACCEPTABLE_SIZES.add(360)
ACCEPTABLE_SIZES.add(384)
ACCEPTABLE_SIZES.add(640)
ACCEPTABLE_SIZES.add(720)
ACCEPTABLE_SIZES.add(768)
ACCEPTABLE_SIZES.add(1280)
ACCEPTABLE_SIZES.add(1920)
ACCEPTABLE_SIZES.add(1080)
TEX_TYPES_157 = {0x2, 0x3, 0x6}
TEX_ATTR_157 = {0x0}
UNK = {0, 32, 160}
TEX_PREBIAS_157 = {0, 1, 2}


def test_parse_tex(parsed_tex):
    tex = parsed_tex
    # assert tex.width in ACCEPTABLE_SIZES
    # assert tex.height in ACCEPTABLE_SIZES
    assert tex.num_images in (1, 6)  # XXX FAILS sometimes
    assert tex.compression_format in TEX_FORMAT_MAPPER  # TODO: rename compression_format
    assert 0 < tex.num_mipmaps_per_image <= 13  # XXX FAILS sometimes

    if type(tex) is Tex157:
        assert tex.version in TEX_VERSION.values()
        assert tex.unk in UNK
        assert tex.attr == 0
        assert tex.prebias in TEX_PREBIAS_157
        assert tex.type in TEX_TYPES_157  # 2D-3D-Cube
        assert tex.depth in {1, 32}  # 32 for no mipmaps
    elif type(tex) is Tex112:
        assert tex.padding == 0  # not 0 only in modded files probably because of the old parser
        assert tex.attr == 0  # enum for FILLMARGIN, GRAYSCALE, NUKI, DITHER, RGBIENCODED, not used for PC RE5
        assert tex.depend_screen == 0
        assert tex.render_target == 0
