import json
import os

# Reuses test_edgemodel_parsing.py's own committed dataset - same files,
# same catalog verification, different assertion (byte-exact identity
# round-trip instead of structural sanity). See
# albam.engines.hexn.edgemodel_roundtrip's module docstring: there's no
# export function yet (no Blender-driven bytes to compare against), but a
# well-formed .edgemodel should come back byte-identical from a plain
# parse-then-write - every field these 5 files exercise is modeled
# directly in the .ksy (not all sections are, for every possible file -
# see the module docstring for the ~28% of files elsewhere in the game
# that don't fully round-trip yet, and why).
EDGEMODEL_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "edgemodel_parsing_hashes.json")
with open(EDGEMODEL_PARSING_DATASET_PATH) as f:
    EDGEMODEL_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_edgemodel_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_edgemodel_path_hash")
        argvalues = [(d["app_id"], d["edgemodel_path_hash"]) for d in EDGEMODEL_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['edgemodel_path_hash']}" for d in EDGEMODEL_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_edgemodel_identity_roundtrip(game_fs_root, hash_to_path, local_app_id, local_edgemodel_path_hash):
    from albam.engines.hexn.edgemodel_roundtrip import identity_roundtrip

    path = hash_to_path[local_edgemodel_path_hash]
    edgemodel_bytes = game_fs_root.readbytes(path)

    assert identity_roundtrip(edgemodel_bytes) == edgemodel_bytes
