import json
import os

# Committed, fixed dataset - explicit, hash-only, catalog-verified skel
# files to parse (see test_dataset_hashes_are_in_catalog below). A mix of
# humans, a creature, a large-gap outlier, a zombie-type character, and a
# case where the .edgemodel's own directory name differs from its
# stem/skel name (its skeleton stays at skel/<stem>.ssg regardless - see
# skeleton.py's infer_skeleton_vfile).
SKEL_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "skel_hashes.json")
with open(SKEL_DATASET_PATH) as f:
    SKEL_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if "local_app_id" in metafunc.fixturenames and "local_skel_path_hash" in metafunc.fixturenames:
        argnames = ("local_app_id", "local_skel_path_hash")
        argvalues = [(d["app_id"], d["skel_path_hash"]) for d in SKEL_DATASET]
        ids = [f"{d['app_id']}-{d['skel_path_hash']}" for d in SKEL_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")
    elif "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", ["reorc"], scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by SKEL_DATASET must be a subset of that app_id's committed catalog, so
    this file only ever exercises real, unmodified, hash-verified game
    files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in SKEL_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["skel_path_hash"] in catalog_hashes, (
            f"{entry['skel_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


def test_parse_skel(game_fs_root, hash_to_path, local_app_id, local_skel_path_hash):
    from albam.engines.hexn.structs.hexane_skel import HexaneSkel

    path = hash_to_path[local_skel_path_hash]
    skel_bytes = game_fs_root.readbytes(path)

    skel = HexaneSkel.from_bytes(skel_bytes)
    skel._read()

    assert skel.tag == b"20SE"
    assert skel.node_count > 0
    assert len(skel.hierarchy) == skel.node_count
    assert len(skel.local_transforms) == skel.node_count
    assert len(skel.names) == skel.node_count
    assert len(skel.parents) == skel.node_count

    # `parents` is a well-formed tree: node 0 is its only root, and every
    # other entry points strictly backwards (see skel.ksy's `parents` doc) -
    # both relied on by skeleton.py's single-forward-pass world-transform
    # composition, and the difference between a coherent bind pose and a
    # scrambled one.
    roots = [i for i, parent in enumerate(skel.parents) if parent == 0xffff]
    assert roots == [0]
    for i, parent in enumerate(skel.parents):
        if i:
            assert parent < i

    # Names are unique-ish real bone names, not empty/garbage.
    assert all(skel.names)
    assert len(set(skel.names)) == len(skel.names)

    # Local transform quaternions/homogeneous coordinates are well-formed.
    for transform in skel.local_transforms:
        rot = transform.rotation
        length = (rot.x ** 2 + rot.y ** 2 + rot.z ** 2 + rot.w ** 2) ** 0.5
        assert 0.9 < length < 1.1
        assert transform.position.w == 1.0
        assert transform.scale.w == 1.0
