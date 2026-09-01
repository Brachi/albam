"""
LfsFS against real .lfs archives: mounting one, listing it, and reading
every file back out - the same path the VFS takes when "Add Files" mounts an
archive (see albam/engines/cie/archive.py).
"""
import json
import os

import pytest

from tests.cie.lfs_paths import resolve_archive_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified archives
# (see test_dataset_hashes_are_in_catalog below), same pattern as
# tests/reng/test_mesh_parsing.py. One small archive per payload layout
# LfsFS has to handle: a container that names its entries' extensions
# (.udas, .dat), one that doesn't (.pack, both plain and .pack.yz2), one
# whose entries carry nested paths (.evd), and single-file archives.
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
LFS_PARSING_DATASET_PATH = os.path.join(DATASETS_DIR, "lfs_parsing_hashes.json")
with open(LFS_PARSING_DATASET_PATH) as f:
    LFS_PARSING_DATASET = json.load(f)

# Payload extensions that hold more than one file (see albam.engines.cie.fs).
CONTAINER_EXTENSIONS = {".udas", ".dat", ".pack", ".evd"}


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in LFS_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['payload_extension'].lstrip('.')}-{d['archive_path_hash']}"
               for d in LFS_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by LFS_PARSING_DATASET must be in that app_id's committed catalog, so this
    file only ever exercises real, unmodified, hash-verified game files.
    CI-safe: reads two committed JSON files, no real install needed.
    """
    for entry in LFS_PARSING_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        catalogued = catalog.get(entry["archive_path_hash"])
        assert catalogued is not None, (
            f"{entry['archive_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )
        assert catalogued["payload_extension"] == entry["payload_extension"], (
            f"{entry['archive_path_hash']!r} is a {catalogued['payload_extension']!r} archive, "
            f"not {entry['payload_extension']!r}"
        )


@pytest.fixture(scope="session")
def local_payload_extension(local_archive_path_hash):
    """The dataset's own payload extension for this archive - a fixture
    rather than a third parametrized argument, so tests that don't care about
    it don't have to take it."""
    return next(d["payload_extension"] for d in LFS_PARSING_DATASET
                if d["archive_path_hash"] == local_archive_path_hash)


@pytest.fixture(scope="session")
def lfs_fs(game_root, local_archive_path_hash):
    from albam.engines.cie.fs import LfsFS

    path = resolve_archive_hashes(game_root, {local_archive_path_hash})[local_archive_path_hash]
    fs = LfsFS(path)
    yield fs
    fs.close()


def test_archive_is_readable(lfs_fs):
    """Every listed file reads back at the size getinfo() reports.

    Not every entry has content: a .dat's file table has fixed-size slots, and
    an unused one is a real, zero-length entry with no extension (LfsFS names
    those "<stem>_NNN.null"). They stay listed rather than being dropped, so
    the numbering keeps matching the container's own.
    """
    paths = list(lfs_fs.walk.files())
    assert paths, "archive should expose at least one file"
    assert len(set(paths)) == len(paths), "file paths should be unique"

    sizes = []
    for path in paths:
        data = lfs_fs.readbytes(path)
        assert len(data) == lfs_fs.getinfo(path, namespaces=["details"]).size
        sizes.append(len(data))
    assert any(sizes), "archive should hold at least one non-empty file"


def test_payload_is_read_as_its_extension_says(lfs_fs, local_payload_extension):
    """The archive holds what its name says it does: a container splits into
    entries, anything else is one file named after the archive itself."""
    assert lfs_fs.payload_extension == local_payload_extension
    assert lfs_fs.container_error is None, (
        f"{lfs_fs.payload_extension} container failed to parse: {lfs_fs.container_error}"
    )

    paths = list(lfs_fs.walk.files())
    if local_payload_extension in CONTAINER_EXTENSIONS:
        assert len(paths) > 1, "a container archive in this dataset should hold several files"
    else:
        assert paths == [f"/{os.path.basename(lfs_fs.lfs_path).split('.')[0]}"
                         f"{local_payload_extension}"]


def test_unnamed_entries_are_numbered_in_container_order(lfs_fs, local_payload_extension):
    """udas/dat/pack entries have no names of their own, so LfsFS numbers them
    - and the numbering has to follow the container's own order, since that is
    the only thing a .tpl's texture index can refer to (see textures.py)."""
    if local_payload_extension not in CONTAINER_EXTENSIONS - {".evd"}:
        pytest.skip(f"a {local_payload_extension} archive has nothing to number "
                    f"(its entries are named, or it holds a single file)")

    stem = os.path.basename(lfs_fs.lfs_path).split(".")[0]
    indices = []
    for name in lfs_fs.listdir("/"):
        assert name.startswith(f"{stem}_"), f"{name} is not numbered after its archive"
        indices.append(int(name[len(stem) + 1:].split(".")[0]))
    assert indices == list(range(len(indices)))


def test_missing_file_raises(lfs_fs):
    from fs.errors import ResourceNotFound

    with pytest.raises(ResourceNotFound):
        lfs_fs.readbytes("/not-a-file-in-here.bin")


def test_read_only(lfs_fs):
    from fs.errors import ResourceReadOnly

    with pytest.raises(ResourceReadOnly):
        lfs_fs.openbin(next(iter(lfs_fs.walk.files())), mode="w")
