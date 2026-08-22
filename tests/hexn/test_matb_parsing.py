import json
import os

import pytest

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Every .matb that
# successfully parsed in a full-game sweep of a real RE:ORC install is
# included (deduplicated to one entry per unique virtual path - the same
# real file gets embedded verbatim into many different .ssg archives, and
# only one copy is ever reachable through the VFS at a time) - see
# albam/engines/hexn/structs/matb.ksy's own header comment for what that
# sweep found and fixed.
MATB_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "matb_parsing_hashes.json")
with open(MATB_PARSING_DATASET_PATH) as f:
    MATB_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_matb_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_matb_path_hash")
        argvalues = [(d["app_id"], d["matb_path_hash"]) for d in MATB_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['matb_path_hash']}" for d in MATB_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MATB_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in MATB_PARSING_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["matb_path_hash"] in catalog_hashes, (
            f"{entry['matb_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def matb_hash_to_path(game_fs_root):
    """Resolves every hash this dataset needs in one single walk, instead of
    each parametrized test calling resolve_hashes() (and so walking the
    whole install) on its own - at thousands of entries, one-walk-per-test
    is prohibitively slow (each walk touches every archived + loose file in
    the install). resolve_hashes() is built for exactly this batched shape
    already; test_edgemodel_parsing.py just never needed it at its much
    smaller (5-entry) scale.
    """
    all_hashes = {d["matb_path_hash"] for d in MATB_PARSING_DATASET}
    return resolve_hashes(game_fs_root, all_hashes)


def test_parse_matb(game_fs_root, matb_hash_to_path, local_app_id, local_matb_path_hash):
    from albam.engines.hexn.structs.hexane_matb import HexaneMatb

    path = matb_hash_to_path[local_matb_path_hash]
    matb_bytes = game_fs_root.readbytes(path)

    matb = HexaneMatb.from_bytes(matb_bytes)
    matb._read()

    assert matb.id_magic == b"MAT"
    assert matb.version >= 1

    # header_size/ofs_params are stored explicitly in the file, not derived -
    # but on every real sample they satisfy this relationship exactly, so a
    # file that doesn't is a sign the format has drifted from what's modeled
    # here, not a well-formed-but-unusual file.
    assert matb.ofs_params == matb.header_size + 8 * matb.num_textures
    assert len(matb.extra_flags) == (matb.header_size - 24) // 4

    shader = matb.shader
    textures = shader.textures
    assert shader.shader
    assert len(textures) == matb.num_textures

    textures_table = matb.textures_table
    params_table = matb.params_table
    assert len(textures_table) == matb.num_textures
    assert len(params_table) == matb.num_params

    # Each texture_entry.ofs_path independently points at the exact same
    # string names_block/shader.textures decodes sequentially - verified
    # byte-exact on every sample in the sweep (0 mismatches).
    pos = matb.ofs_names + len(shader.shader.encode("ascii")) + 1
    for entry, texture_path in zip(textures_table, textures):
        assert entry.ofs_path == pos
        assert entry.path == texture_path
        pos += len(texture_path.encode("ascii")) + 1

    # The name/string block is the last thing in the file - no unmodeled
    # trailing bytes after the final texture path.
    assert pos == len(matb_bytes)
