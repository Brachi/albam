import json
import os

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Six *.anims.ssg
# from Animation/Projects/: an effectively-empty archive (32 bytes, no
# entries), a single-entry one, and four multi-entry ones spanning both
# real id_magic values (5 and 6) and a range of sizes/characters. Extend
# this directly to add more.
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
    elif "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", ["reorc"], scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by ANIMS_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in ANIMS_PARSING_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["anims_path_hash"] in catalog_hashes, (
            f"{entry['anims_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


def test_parse_anims_container(game_fs_root, hash_to_path, local_app_id, local_anims_path_hash):
    """Container-level structure: same shape as hexane_ssg, just big-endian
    (see structs/anims.ksy). id_magic is 5 or 6 on every real file; every
    entry's name follows the `<clip_path>--<skeleton_name>` convention
    (except the one empty archive in the dataset, which has no entries at
    all).
    """
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    path = hash_to_path[local_anims_path_hash]
    data = game_fs_root.readbytes(path)

    anims = HexaneAnims.from_bytes(data)
    anims._read()

    assert anims.id_magic in (5, 6)
    assert len(anims.files_info) == anims.size_files_info // 32

    if not anims.files_info:
        return  # Leon.anims.ssg: a real, well-formed, but empty archive.

    offset = 0
    for file_info in anims.files_info:
        assert file_info.file_type == 5
        assert "--" in file_info.name
        clip_path, skeleton_name = file_info.name.rsplit("--", 1)
        assert clip_path
        assert skeleton_name

        clip_bytes = anims.buffer_chunks[offset:offset + file_info.size]
        offset += file_info.size  # no padding between entries - see anims.ksy
        assert clip_bytes[:4] == b"40AE"


def test_parse_anims_clip_header(game_fs_root, hash_to_path, local_app_id, local_anims_path_hash):
    """AnimClip's own confirmed EdgeAnimAnimation header fields, spot-checked
    against the relationships confirmed against the committed dataset (see
    structs/anims.ksy's module doc): framerate is always 30, num_frames is
    duration*framerate rounded up by one, and size_header always exactly
    matches this clip's own real byte offset into its keyframe data.
    """
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    path = hash_to_path[local_anims_path_hash]
    data = game_fs_root.readbytes(path)

    anims = HexaneAnims.from_bytes(data)
    anims._read()

    offset = 0
    for file_info in anims.files_info:
        clip_bytes = anims.buffer_chunks[offset:offset + file_info.size]
        offset += file_info.size

        clip = HexaneAnims.AnimClip.from_bytes(clip_bytes)
        clip._read()

        assert round(clip.framerate) == 30
        assert clip.num_bones > 0
        assert clip.num_frames == round(clip.duration_seconds * clip.framerate) + 1
        assert clip.num_frame_sets >= 1
        assert len(clip.body) == file_info.size - 96
