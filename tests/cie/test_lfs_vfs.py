"""
Mounting a real .lfs through the VFS, the way "Add Files" does in the UI:
`add_real_file` dispatches on extension to the fs_root_loader registered in
albam/engines/cie/archive.py, so this exercises the registry, the FS and the
tree building together rather than LfsFS on its own.
"""
import json
import os

import bpy
import pytest

from albam.lib import fs_registry
from tests.cie.conftest import close_new_fs_roots
from tests.cie.lfs_paths import resolve_archive_hashes

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
with open(os.path.join(DATASETS_DIR, "lfs_parsing_hashes.json")) as f:
    LFS_PARSING_DATASET = json.load(f)

# One .udas: the layout an actual import starts from (a mesh .bin and its
# .tpl packed together), not every payload type - those are covered directly
# in test_lfs_fs.py, and each one mounted here would be a full decompression.
UDAS_ENTRY = next(d for d in LFS_PARSING_DATASET if d["payload_extension"] == ".udas")


@pytest.fixture(autouse=True)
def _clean_vfs_state():
    # Same session-scoped Blender state every other VFS test has to clean up
    # after itself - see tests/test_vfs_fs_backed.py.
    before = fs_registry.keys()
    yield
    bpy.context.scene.albam.vfs.file_list.clear()
    close_new_fs_roots(before)


@pytest.fixture(scope="session")
def local_app_id():
    return UDAS_ENTRY["app_id"]


def test_add_files_mounts_an_archive(game_root, local_app_id):
    archive_path = resolve_archive_hashes(
        game_root, {UDAS_ENTRY["archive_path_hash"]}
    )[UDAS_ENTRY["archive_path_hash"]]

    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_real_file(local_app_id, archive_path)

    assert root.is_root
    assert root.is_archive
    assert root.fs_key, "an fs_root_loader-backed root carries its fs_registry key"
    assert root.display_name == os.path.basename(archive_path)

    children = [vf for vf in vfs.file_list if vf.tree_node.root_id == root.name and not vf.is_root]
    assert children, "the archive's files should have been added to the tree"

    for vfile in children:
        assert vfile.get_bytes(), f"{vfile.display_name} read back empty through the VFS"


def test_teardown_leaves_other_suites_filesystems_open():
    """Cleaning up after a cie test must not close anyone else's FS.

    Session-scoped parametrization interleaves this suite with tests/mtfw,
    whose game_fs_root is a single session-scoped MTFW_FS every test in it
    shares. A teardown calling fs_registry.clear() closed that mid-run, and
    every mtfw test after the point where a cie block happened to land failed
    with FilesystemClosed - which is what adding one parametrized test here
    was enough to trigger. CI-safe: MemoryFS, no game data.
    """
    from fs.memoryfs import MemoryFS

    someone_elses = fs_registry.register(MemoryFS())
    before = fs_registry.keys()
    mine = fs_registry.register(MemoryFS())

    close_new_fs_roots(before)

    assert not fs_registry.get(someone_elses).isclosed(), (
        "a filesystem registered before the test was closed by its teardown")
    assert mine not in fs_registry.keys(), "the test's own root should be gone"
    fs_registry.unregister(someone_elses)
