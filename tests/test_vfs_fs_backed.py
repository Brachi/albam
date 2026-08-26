"""
Tests for the fs.base.FS-backed side of the VFS (albam/vfs.py's
add_fs_root/add_export_root, and albam/lib/fs_registry.py) added as part of
replacing VirtualFileSystem's Blender-property-only storage with a live FS
instance as the source of truth. Uses MemoryFS throughout - the mechanism
itself is engine-agnostic; MTFW_FS/ArcFS-specific integration is covered in
tests/mtfw/test_origin_arc_path.py.
"""
import bpy
import pytest
from fs.memoryfs import MemoryFS

from albam.lib import fs_registry
from albam.vfs import VirtualFileData


@pytest.fixture(autouse=True)
def _clean_vfs_state():
    # vfs/exported are session-scoped Blender state (register() runs once
    # per pytest session), so without this, roots added by one test would
    # collide by name with roots added by another - node ids are keyed by
    # app_id::relative_path only, not by which root added them.
    yield
    bpy.context.scene.albam.vfs.file_list.clear()
    bpy.context.scene.albam.exported.file_list.clear()
    fs_registry.clear()


def _sample_fs():
    fs_instance = MemoryFS()
    fs_instance.makedirs("model/pl/pl00")
    fs_instance.writebytes("/model/pl/pl00/pl00.mod", b"mod-bytes")
    fs_instance.writebytes("/model/pl/pl00/pl00.mrl", b"mrl-bytes")
    return fs_instance


def test_fs_registry_register_get_unregister():
    fs_instance = MemoryFS()
    key = fs_registry.register(fs_instance)

    assert fs_registry.get(key) is fs_instance

    fs_registry.unregister(key)
    with pytest.raises(KeyError):
        fs_registry.get(key)


def test_fs_registry_clear():
    key_a = fs_registry.register(MemoryFS())
    key_b = fs_registry.register(MemoryFS())

    fs_registry.clear()

    with pytest.raises(KeyError):
        fs_registry.get(key_a)
    with pytest.raises(KeyError):
        fs_registry.get(key_b)


def test_add_fs_root_builds_tree_and_reads_bytes():
    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_fs_root("re5", _sample_fs(), display_name="sample-root")

    # add_fs_root must return a live, correctly-populated reference, not the
    # pre-population one captured before file_list.add() calls that follow
    # can invalidate it (see the fix in albam/vfs.py).
    assert root.name == "re5::sample-root"
    assert root.fs_key
    assert root.is_root
    assert root.is_archive is False

    vfile_mod = vfs.select_vfile("re5", "model/pl/pl00/pl00.mod")
    assert vfile_mod.get_bytes() == b"mod-bytes"

    vfile_mrl = vfs.get_vfile("re5", "model/pl/pl00/pl00.mrl")
    assert vfile_mrl.get_bytes() == b"mrl-bytes"

    # intermediate directory nodes must exist too, for the tree UI - node ids
    # are app_id::relative_path, not prefixed by the root's own display name.
    dir_node = vfs.file_list["re5::model::pl::pl00"]
    assert dir_node.is_expandable


def test_add_fs_root_is_archive_flag():
    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_fs_root("re5", MemoryFS(), display_name="an.arc", is_archive=True)
    assert root.is_archive is True


def test_add_export_root_writes_and_reads_bytes():
    exported = bpy.context.scene.albam.exported
    vfiles = [
        VirtualFileData("re5", "model/pl/pl00/pl00.mod", data_bytes=b"exported-mod"),
        VirtualFileData("re5", "model/pl/pl00/pl00.mrl", data_bytes=b"exported-mrl"),
    ]

    root = exported.add_export_root("re5", "export-root", vfiles)

    assert root.name and root.fs_key

    vfile_mod = exported.select_vfile("re5", "model/pl/pl00/pl00.mod")
    assert vfile_mod.get_bytes() == b"exported-mod"

    vfile_mrl = exported.get_vfile("re5", "model/pl/pl00/pl00.mrl")
    assert vfile_mrl.get_bytes() == b"exported-mrl"


def test_add_export_root_defaults_missing_bytes_to_empty():
    exported = bpy.context.scene.albam.exported
    exported.add_export_root(
        "re5", "export-root-2", [VirtualFileData("re5", "empty.txt", data_bytes=None)]
    )

    vfile = exported.select_vfile("re5", "empty.txt")
    assert vfile.get_bytes() == b""


def test_reload_blend_file_reconnects_fs_roots(tmp_path):
    """
    add_fs_root() stashes the live FS instance in fs_registry - a plain
    in-process dict (see its module docstring) - and only a string key on
    the persisted VirtualFile.fs_key. That dict isn't part of the .blend
    file and doesn't survive a real restart: a fresh Blender process starts
    with fs_registry empty again, while VirtualFile.fs_key (restored from
    the file) still points at an entry that no longer exists. Reproduces
    the KeyError a user hits importing after reopening a saved .blend that
    had a folder/archive added to the VFS.
    """
    game_root = tmp_path / "game_root"
    (game_root / "model" / "pl" / "pl00").mkdir(parents=True)
    (game_root / "model" / "pl" / "pl00" / "pl00.mod").write_bytes(b"mod-bytes")

    vfs = bpy.context.scene.albam.vfs
    vfs.add_real_file("re5", str(game_root))
    vfile = vfs.select_vfile("re5", "model/pl/pl00/pl00.mod")
    assert vfile.get_bytes() == b"mod-bytes"

    blend_path = str(tmp_path / "save.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Simulate closing and reopening Blender: fs_registry is plain-Python,
    # in-process state that a fresh process starts up without, unlike
    # bpy.data (including VirtualFile.fs_key), which is restored from disk.
    fs_registry.clear()
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    vfs = bpy.context.scene.albam.vfs
    vfile = vfs.select_vfile("re5", "model/pl/pl00/pl00.mod")
    assert vfile.get_bytes() == b"mod-bytes"


def test_remove_root_unregisters_fs():
    from albam.vfs import ALBAM_OT_VirtualFileSystemRemoveRootVFile

    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_fs_root("re5", _sample_fs(), display_name="removable-root")
    key = root.fs_key
    assert fs_registry.get(key) is not None

    vfs.file_list_selected_index = vfs.file_list.find(root.name)
    ALBAM_OT_VirtualFileSystemRemoveRootVFile.execute(
        ALBAM_OT_VirtualFileSystemRemoveRootVFile, bpy.context
    )

    assert len(vfs.file_list) == 0
    with pytest.raises(KeyError):
        fs_registry.get(key)


def test_two_roots_sharing_a_display_name_each_read_their_own_fs():
    """Adding two same-named archives from different directories (e.g.
    "Add Files" on both Characters/<name>.ssg and Characters/skel/<name>.ssg)
    used to give both roots the identical file_list name, so every child of
    the second one resolved its root - and therefore its FS - back to the
    first, reading bytes from the wrong archive.
    """
    fs_a = MemoryFS()
    fs_a.makedirs("/only_in_a")
    fs_a.writebytes("/only_in_a/thing.mod", b"a-bytes")
    fs_b = MemoryFS()
    fs_b.makedirs("/only_in_b")
    fs_b.writebytes("/only_in_b/thing.mod", b"b-bytes")

    vfs = bpy.context.scene.albam.vfs
    root_a = vfs.add_fs_root("re5", fs_a, display_name="same.arc", is_archive=True)
    root_b = vfs.add_fs_root("re5", fs_b, display_name="same.arc", is_archive=True)

    # Re-fetched by name: file_list.add() calls during the second
    # add_fs_root can invalidate a reference taken before them (see the
    # comment in add_fs_root), and a stale one would pass these vacuously.
    name_a, name_b = root_a.name, root_b.name
    assert name_a != name_b
    root_a, root_b = vfs.file_list[name_a], vfs.file_list[name_b]

    # Distinct keys in file_list, but the same UI label - the disambiguation
    # is internal, the user still sees what they added.
    assert root_a.name == name_a and root_b.name == name_b
    assert root_a.display_name == root_b.display_name == "same.arc"
    assert root_a.fs_key != root_b.fs_key

    assert vfs.get_vfile("re5", "only_in_a/thing.mod").get_bytes() == b"a-bytes"
    assert vfs.get_vfile("re5", "only_in_b/thing.mod").get_bytes() == b"b-bytes"
