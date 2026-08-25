import json
import os

# Reuses test_anims_parsing.py's own committed dataset - same files, same
# catalog verification, different assertion (byte-exact identity round-trip
# instead of structural sanity). See
# albam.engines.hexn.anims_roundtrip's module docstring.
ANIMS_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "anims_parsing_hashes.json")
with open(ANIMS_PARSING_DATASET_PATH) as f:
    ANIMS_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_anims_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_anims_path_hash")
        argvalues = [(d["app_id"], d["anims_path_hash"]) for d in ANIMS_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['anims_path_hash']}" for d in ANIMS_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_anims_identity_roundtrip(game_fs_root, hash_to_path, local_app_id, local_anims_path_hash):
    from albam.engines.hexn.anims_roundtrip import identity_roundtrip

    path = hash_to_path[local_anims_path_hash]
    anims_bytes = game_fs_root.readbytes(path)

    assert identity_roundtrip(anims_bytes) == anims_bytes
