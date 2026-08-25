import io
import json
import os

# Reuses test_anims_parsing.py's own committed dataset - same files, same
# catalog verification, different assertion (byte-exact identity round-trip
# instead of structural sanity). The container is modeled in
# structs/anims.ksy and each entry's own bytes are carried whole inside
# buffer_chunks, so a clip's internal layout doesn't have to be understood
# to reproduce the archive exactly.
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


def identity_roundtrip(data):
    """Parse `data` and write it back out. The dev/test archives with a
    corrupt size_chunks_info (see structs/anims.ksy) raise in `_read()`
    rather than reaching the write - none is in this dataset.
    """
    from kaitaistruct import KaitaiStream

    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    parsed = HexaneAnims.from_bytes(data)
    parsed._read()
    parsed._fetch_instances()

    stream = KaitaiStream(io.BytesIO(bytearray(len(data))))
    parsed._write(stream)
    return stream.to_byte_array()


def test_anims_identity_roundtrip(game_fs_root, hash_to_path, local_app_id, local_anims_path_hash):
    path = hash_to_path[local_anims_path_hash]
    anims_bytes = game_fs_root.readbytes(path)

    assert identity_roundtrip(anims_bytes) == anims_bytes
