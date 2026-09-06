"""
"Add Files" tests for RE:ORC .ssg archives - i.e. mounting individual files
through albam.vfs.VirtualFileSystemBase.add_real_file() (the exact path the
UI's "Add Files" button takes, including fs_root_loader dispatch into
SsgFS), rather than the whole-game-folder mount tests/hexn/conftest.py's
game_fs_root fixture sets up for every other test here.

Self-contained: archive bytes are hand-built by tests/hexn/test_ssg_fs.py's
_build_ssg_bytes, no real game data needed (see that file's own docstring).
"""
import bpy
import pytest

from .test_ssg_fs import _build_ssg_bytes


@pytest.fixture
def added_roots():
    """The VFS is session state shared with every other test here (the
    game_fs_root fixture mounts its own root into it), so roots added by
    this file are removed again rather than left behind."""
    vfs = bpy.context.scene.albam.vfs
    before = len(vfs.file_list)
    yield vfs
    while len(vfs.file_list) > before:
        vfs.file_list.remove(len(vfs.file_list) - 1)


def test_add_files_two_ssgs_with_the_same_name_read_their_own_bytes(tmp_path, added_roots):
    """A character's mesh archive and its skeleton archive share a basename
    on a real install (Characters/<name>.ssg and Characters/skel/<name>.ssg),
    so adding both - which is what importing a skinned .edgemodel this way
    requires - used to leave every entry of the second one reading from the
    first archive's FS, failing with ResourceNotFound on import.
    """
    model_ssg = tmp_path / "dup.ssg"
    model_ssg.write_bytes(_build_ssg_bytes([("dup_addfiles/models/dup.edgemodel", b"MESH-BYTES")]))
    skel_dir = tmp_path / "skel"
    skel_dir.mkdir()
    skel_ssg = skel_dir / "dup.ssg"
    skel_ssg.write_bytes(_build_ssg_bytes([("dup_addfiles/skel/dup", b"SKEL-BYTES")]))

    vfs = added_roots
    vfs.add_real_file("reorc", str(model_ssg))
    vfs.add_real_file("reorc", str(skel_ssg))

    assert vfs.get_vfile("reorc", "dup_addfiles/models/dup.edgemodel").get_bytes() == b"MESH-BYTES"
    assert vfs.get_vfile("reorc", "dup_addfiles/skel/dup").get_bytes() == b"SKEL-BYTES"
