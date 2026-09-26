import io
import json
import os

# Reuses test_edgemodel_parsing.py's own committed dataset - same files,
# same catalog verification, different assertion (byte-exact identity
# round-trip instead of structural sanity). There's no export function yet
# (no Blender-driven bytes to compare against), but a well-formed
# .edgemodel comes back byte-identical from a plain parse-then-write.
# Every section these files exercise is modeled in structs/edgemodel.ksy;
# not every section of every file in the game is, so this dataset is
# deliberately curated rather than exhaustive.
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


def identity_roundtrip(data):
    """Parse `data` and write it back out."""
    from kaitaistruct import KaitaiStream

    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel

    parsed = HexaneEdgemodel.from_bytes(data)
    parsed._read()
    parsed._fetch_instances()

    stream = KaitaiStream(io.BytesIO(bytearray(len(data))))
    parsed._write(stream)
    return stream.to_byte_array()


def test_edgemodel_identity_roundtrip(game_fs_root, hash_to_path, local_app_id, local_edgemodel_path_hash):
    path = hash_to_path[local_edgemodel_path_hash]
    edgemodel_bytes = game_fs_root.readbytes(path)

    assert identity_roundtrip(edgemodel_bytes) == edgemodel_bytes
