"""update_lfs and _rebuild_udas: the archive writer's own coverage gaps.

_rebuild_udas was previously only ever exercised by substituting an entry for
itself (test_lfs_fs.test_repacking_an_archive_unchanged_preserves_every_entry),
which never resizes the DAT block and so never took the descriptor-shifting
path - the whole reason a rebuild has to touch the block table at all - nor
exercised update_lfs itself: neither its extension dispatch (.udas rebuild vs.
single-file-archive replacement vs. "not supported") nor archive_writer_registry
calling it, which is what bpy.ops.albam.pack actually drives.
"""
import json
import os

import pytest

from tests.cie.lfs_paths import resolve_archive_hashes

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "archive_update_hashes.json")
with open(DATASET_PATH) as f:
    ARCHIVE_UPDATE_DATASET = json.load(f)

BLOCK_TYPE_DAT = 0


class _FakeExportedFile:
    """A stand-in for the VirtualFile update_lfs actually receives.

    update_lfs only ever reads `display_name` and calls `get_bytes()` on what
    it is handed, so a plain object serves - a real VirtualFile is a bpy
    PropertyGroup, meant to live as an item of a registered VFS collection,
    not to be built standalone for a unit test.
    """

    def __init__(self, display_name, data):
        self.display_name = display_name
        self._data = data

    def get_bytes(self):
        return self._data


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in ARCHIVE_UPDATE_DATASET]
        ids = [f"{d['app_id']}-{d['payload_extension'].lstrip('.')}-{d['archive_path_hash']}"
               for d in ARCHIVE_UPDATE_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - see
    tests/cie/test_lfs_fs.py, same check. CI-safe."""
    for entry in ARCHIVE_UPDATE_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        assert entry["archive_path_hash"] in catalog, (
            f"{entry['archive_path_hash']!r} is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def local_payload_extension(local_archive_path_hash):
    return next(d["payload_extension"] for d in ARCHIVE_UPDATE_DATASET
                if d["archive_path_hash"] == local_archive_path_hash)


@pytest.fixture(scope="session")
def archive_path(game_root, local_archive_path_hash):
    return resolve_archive_hashes(game_root, {local_archive_path_hash})[local_archive_path_hash]


def test_rebuild_udas_shifts_blocks_after_a_resized_entry(
        archive_path, local_payload_extension, tmp_path):
    """The path test_repacking_an_archive_unchanged_preserves_every_entry
    cannot reach: substituting an entry for itself never changes the DAT
    block's size, so shift is always 0 there and comparing every block
    descriptor to the original - which that test does - is only a
    meaningful check in that one case. Resizing an entry here forces shift
    != 0, so a descriptor after the DAT block actually has to move.
    """
    if local_payload_extension != ".udas":
        pytest.skip("only .udas archives are rebuilt by _rebuild_udas")

    from albam.engines.cie.archive import _read_payload, _rebuild_udas
    from albam.engines.cie.fs import LfsFS, read_udas_block_table

    fs = LfsFS(archive_path)
    try:
        paths = list(fs.walk.files())
        target = paths[0].lstrip("/")
        before = {p.lstrip("/"): fs.readbytes(p) for p in paths}
    finally:
        fs.close()
    original_entry_bytes = before[target]

    payload, _extension = _read_payload(archive_path)
    original_blocks = read_udas_block_table(payload, "<")
    assert len(original_blocks) > 1, (
        "this archive should hold a block after the DAT one to exercise the shift"
    )
    dat_type, dat_size, data_offset = original_blocks[0]
    assert dat_type == BLOCK_TYPE_DAT

    # Bigger than the original by enough that it survives 16-byte entry
    # alignment and still changes the DAT block's overall size.
    resized_bytes = original_entry_bytes + b"\xAA" * 64
    rebuilt_payload = _rebuild_udas(payload, {target: resized_bytes})

    rebuilt_blocks = read_udas_block_table(rebuilt_payload, "<")
    assert len(rebuilt_blocks) == len(original_blocks)
    new_dat_type, new_dat_size, new_data_offset = rebuilt_blocks[0]
    assert new_dat_type == BLOCK_TYPE_DAT
    assert new_data_offset == data_offset, "the DAT block itself does not move"
    shift = new_dat_size - dat_size
    assert shift != 0, "the resize should have changed the DAT block's size"

    for (orig_type, _orig_size, orig_offset), (new_type, new_size, new_offset) in zip(
            original_blocks[1:], rebuilt_blocks[1:]):
        assert new_type == orig_type
        assert new_size == _orig_size, "only the DAT block's own size should change"
        expected_offset = orig_offset + shift if orig_offset > data_offset else orig_offset
        assert new_offset == expected_offset, (
            f"block {orig_type:#x} should have moved by {shift}, from {orig_offset} "
            f"to {expected_offset}, not {new_offset}"
        )

    # And the rebuilt archive still mounts and reads back correctly: the
    # resized entry comes back as what it was resized to, everything else
    # exactly as it shipped.
    from albam.engines.cie.lfs_decompress import xcompress_compress_re4hd

    archive_bytes = xcompress_compress_re4hd(rebuilt_payload)
    out_path = tmp_path / os.path.basename(archive_path)
    out_path.write_bytes(archive_bytes)
    rebuilt_fs = LfsFS(str(out_path))
    try:
        after = {p.lstrip("/"): rebuilt_fs.readbytes(p) for p in rebuilt_fs.walk.files()}
    finally:
        rebuilt_fs.close()

    assert after[target] == resized_bytes
    unchanged = {k: v for k, v in before.items() if k != target}
    assert {k: after[k] for k in unchanged} == unchanged


def test_update_lfs_rebuilds_a_udas_archive(archive_path, local_payload_extension, tmp_path):
    """update_lfs's own extension dispatch, on the branch that matters most:
    a .udas archive with one entry replaced comes back as a whole .lfs the
    game can load, with the replacement in place and everything else intact.
    """
    if local_payload_extension != ".udas":
        pytest.skip("only .udas archives take this branch of update_lfs")

    from albam.engines.cie.archive import update_lfs
    from albam.engines.cie.fs import LfsFS

    fs = LfsFS(archive_path)
    try:
        paths = list(fs.walk.files())
        target_path = paths[0]
        before = {p.lstrip("/"): fs.readbytes(p) for p in paths}
    finally:
        fs.close()

    replacement = before[target_path.lstrip("/")] + b"\xAA" * 16
    vfile = _FakeExportedFile(target_path.lstrip("/"), replacement)

    archive_bytes = update_lfs(archive_path, [vfile])

    out_path = tmp_path / os.path.basename(archive_path)
    out_path.write_bytes(archive_bytes)
    rebuilt_fs = LfsFS(str(out_path))
    try:
        after = {p.lstrip("/"): rebuilt_fs.readbytes(p) for p in rebuilt_fs.walk.files()}
    finally:
        rebuilt_fs.close()

    assert after[target_path.lstrip("/")] == replacement
    unchanged = {k: v for k, v in before.items() if k != target_path.lstrip("/")}
    assert {k: after[k] for k in unchanged} == unchanged


def test_update_lfs_replaces_a_single_file_archive_wholesale(
        archive_path, local_payload_extension, tmp_path):
    """A single-file .lfs (no container inside it) is replaced outright: the
    whole payload becomes the one exported file, not something rebuilt
    around a file table it never had.
    """
    if local_payload_extension in (".udas", ".dat", ".pack", ".evd"):
        pytest.skip("only a single-file archive takes this branch of update_lfs")

    from albam.engines.cie.archive import update_lfs
    from albam.engines.cie.fs import LfsFS

    fs = LfsFS(archive_path)
    try:
        paths = list(fs.walk.files())
        assert len(paths) == 1, "this dataset entry should be a single-file archive"
        display_name = paths[0].lstrip("/")
    finally:
        fs.close()

    replacement = b"\xBB" * 128
    vfile = _FakeExportedFile(display_name, replacement)

    archive_bytes = update_lfs(archive_path, [vfile])

    out_path = tmp_path / os.path.basename(archive_path)
    out_path.write_bytes(archive_bytes)
    rebuilt_fs = LfsFS(str(out_path))
    try:
        paths = list(rebuilt_fs.walk.files())
        assert paths == [f"/{display_name}"]
        assert rebuilt_fs.readbytes(paths[0]) == replacement
    finally:
        rebuilt_fs.close()


def test_update_lfs_refuses_a_container_it_cannot_rebuild(
        archive_path, local_payload_extension):
    """.dat/.pack/.evd containers have no rebuild support (only .udas does),
    so update_lfs says so plainly rather than silently doing nothing or
    corrupting the archive.
    """
    if local_payload_extension != ".dat":
        pytest.skip("only the .dat entry in this dataset exercises this branch")

    from albam.engines.cie.archive import update_lfs
    from albam.engines.cie.fs import LfsFS

    fs = LfsFS(archive_path)
    try:
        display_name = next(iter(fs.walk.files())).lstrip("/")
    finally:
        fs.close()

    vfile = _FakeExportedFile(display_name, b"\xCC" * 16)

    with pytest.raises(NotImplementedError, match="dat"):
        update_lfs(archive_path, [vfile])
