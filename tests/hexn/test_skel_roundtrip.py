import json
import os

# Reuses test_skel_parsing.py's own committed dataset - same files, same
# catalog verification, different assertion (byte-exact identity
# round-trip instead of structural sanity). See
# albam.engines.hexn.skel_roundtrip's module docstring: verified 100%
# byte-exact against the full local dataset of real
# dlc/pack1/Characters/skel/*.ssg files, not just this committed sample.
SKEL_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "skel_hashes.json")
with open(SKEL_DATASET_PATH) as f:
    SKEL_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if "local_app_id" in metafunc.fixturenames and "local_skel_path_hash" in metafunc.fixturenames:
        argnames = ("local_app_id", "local_skel_path_hash")
        argvalues = [(d["app_id"], d["skel_path_hash"]) for d in SKEL_DATASET]
        ids = [f"{d['app_id']}-{d['skel_path_hash']}" for d in SKEL_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_skel_identity_roundtrip(game_fs_root, hash_to_path, local_app_id, local_skel_path_hash):
    from albam.engines.hexn.skel_roundtrip import identity_roundtrip

    path = hash_to_path[local_skel_path_hash]
    skel_bytes = game_fs_root.readbytes(path)

    assert identity_roundtrip(skel_bytes) == skel_bytes
