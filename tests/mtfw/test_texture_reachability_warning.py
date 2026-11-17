"""Albam writes whatever relative_path an image has into the MRL and adds
new textures to the model's own arc, but never checked whether the game
could actually find that path anywhere (#372). Renaming a texture's path
to dodge the duplicate-path check (#368) without a .tex ever landing at
the new name reads back fine in Blender and fails only in the game - a
crash or an endless load in RE6 campaign, which cost one user about two
hours in #support before anyone realized why.

Everything here is synthetic - no real game data needed: _serialize_arc
builds a throwaway .arc on disk, and FakeVFile stands in for the handful
of attributes update_arc actually reads off a vfile (relative_path,
extension, app_id, get_bytes()), the same stand-in test_arc_compression.py
uses for the archive-writer tests.
"""
import bpy
import pytest
from fs.memoryfs import MemoryFS

import albam.engines.mtfw.archive as archive_mod
from albam.engines.mtfw import EXTENSION_TO_FILE_ID
from albam.engines.mtfw.archive import (
    _get_file_entry,
    _serialize_arc,
    _warn_about_unreachable_textures,
    update_arc,
)

ARC_VERSION_ZLIB = 7


class FakeVFile:
    """The four things update_arc asks a vfile for."""

    def __init__(self, relative_path, data=b"", app_id="re1"):
        self.relative_path = relative_path
        self.extension = relative_path.rsplit(".", 1)[-1]
        self.app_id = app_id
        self._data = data

    def get_bytes(self):
        return self._data


class FakeFileEntry:
    """The two things _warn_about_unreachable_textures asks an exported
    arc entry for."""

    def __init__(self, file_path, file_type):
        self.file_path = file_path
        self.file_type = file_type


def _arc_with_one_dummy_entry(path):
    """Writes a minimal but valid .arc to `path`: _serialize_arc sizes its
    output stream from num_files * 80 with no allowance for the 8 byte
    header itself, so an archive of zero entries has no room to even write
    that header - one placeholder entry, irrelevant to every test here, is
    the smallest input that round-trips.
    """
    dummy = _get_file_entry(FakeVFile("chr\\dummy.tex", data=b"placeholder"), ARC_VERSION_ZLIB)
    path.write_bytes(_serialize_arc({"chr\\dummy.tex": dummy}, ARC_VERSION_ZLIB))


@pytest.fixture
def recorded_warnings(monkeypatch):
    """Swaps in a spy for show_message_box everywhere archive.py calls it,
    rather than letting the real one try to pop up a window during tests."""
    warnings = []
    monkeypatch.setattr(archive_mod, "show_message_box",
                        lambda message, **kwargs: warnings.append(message))
    return warnings


def test_warns_about_a_path_that_is_neither_in_the_arc_nor_mounted_anywhere(recorded_warnings):
    _warn_about_unreachable_textures(
        "re1", {"chr\\pl\\pl00\\pl_vtf5"}, exported={}, arc_version=ARC_VERSION_ZLIB)

    assert len(recorded_warnings) == 1
    message = recorded_warnings[0]
    assert "pl_vtf5.tex" in message
    assert "isn't in any loaded arc" in message


def test_quiet_when_the_path_is_already_among_the_arc_s_own_entries(recorded_warnings):
    exported = {
        "chr\\pl\\pl00\\pl_vtf5.tex": FakeFileEntry(
            "chr\\pl\\pl00\\pl_vtf5", EXTENSION_TO_FILE_ID["tex"]),
    }

    _warn_about_unreachable_textures(
        "re1", {"chr\\pl\\pl00\\pl_vtf5"}, exported, ARC_VERSION_ZLIB)

    assert recorded_warnings == []


def test_quiet_when_the_path_matches_case_and_separator_insensitively(recorded_warnings):
    """Mirrors _normalize_texture_key's own normalization (backslash,
    lowercase) - a path referenced with different casing or separators than
    the arc entry's own spelling still has to resolve as the same texture."""
    exported = {
        "chr/pl/pl00/PL_VTF5.tex": FakeFileEntry(
            "chr/pl/pl00/PL_VTF5", EXTENSION_TO_FILE_ID["tex"]),
    }

    _warn_about_unreachable_textures(
        "re1", {"chr\\pl\\pl00\\pl_vtf5"}, exported, ARC_VERSION_ZLIB)

    assert recorded_warnings == []


@pytest.fixture
def mounted_texture_root():
    """Mounts a texture under a throwaway VFS root via the real add_fs_root
    API - any arc the VFS has loaded, not just the one being written - and
    unmounts it again afterward so no test leaks state into the shared
    session's scene.
    """
    mem_fs = MemoryFS()
    mem_fs.makedirs("/chr/pl/pl00", recreate=True)
    mem_fs.writebytes("/chr/pl/pl00/pl_vtf5.tex", b"fake dds bytes")
    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_fs_root("re1", mem_fs, display_name="test-372-mounted-texture")
    try:
        yield
    finally:
        vfs._remove_root(root.name)


def test_quiet_when_the_path_is_mounted_in_a_different_loaded_root(
        recorded_warnings, mounted_texture_root):
    _warn_about_unreachable_textures(
        "re1", {"chr\\pl\\pl00\\pl_vtf5"}, exported={}, arc_version=ARC_VERSION_ZLIB)

    assert recorded_warnings == []


def test_still_warns_when_the_mounted_texture_belongs_to_a_different_app(
        recorded_warnings, mounted_texture_root):
    """mounted_texture_root mounts under app_id "re1" - a model of a
    different game referencing the same-looking path is not actually the
    same texture, so it must not satisfy the check."""
    _warn_about_unreachable_textures(
        "re6", {"chr\\pl\\pl00\\pl_vtf5"}, exported={}, arc_version=ARC_VERSION_ZLIB)

    assert len(recorded_warnings) == 1


def test_quiet_when_a_mounted_texture_s_extension_is_upper_case(recorded_warnings):
    """A real game folder (MTFW_FS, not an .arc) mounts whatever case its
    files are actually named with on disk - vf.extension is read straight
    off that name, so a `.TEX` file must still satisfy the check rather
    than being silently filtered out by a case-sensitive comparison."""
    mem_fs = MemoryFS()
    mem_fs.makedirs("/chr/pl/pl00", recreate=True)
    mem_fs.writebytes("/chr/pl/pl00/pl_vtf5.TEX", b"fake dds bytes")
    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_fs_root("re1", mem_fs, display_name="test-372-upper-case-extension")
    try:
        _warn_about_unreachable_textures(
            "re1", {"chr\\pl\\pl00\\pl_vtf5"}, exported={}, arc_version=ARC_VERSION_ZLIB)
    finally:
        vfs._remove_root(root.name)

    assert recorded_warnings == []


def test_warning_lists_and_pluralizes_several_missing_paths(recorded_warnings):
    missing = {f"chr\\pl\\pl{i:02d}\\pl_vtf{i}" for i in range(10)}

    _warn_about_unreachable_textures("re1", missing, exported={}, arc_version=ARC_VERSION_ZLIB)

    assert len(recorded_warnings) == 1
    message = recorded_warnings[0]
    assert "aren't in any loaded arc" in message
    assert "..." in message


def test_quiet_when_nothing_is_referenced(recorded_warnings):
    _warn_about_unreachable_textures("re1", set(), exported={}, arc_version=ARC_VERSION_ZLIB)

    assert recorded_warnings == []


def test_update_arc_warns_about_a_texture_its_own_exported_mrl_references(
        recorded_warnings, monkeypatch, tmp_path):
    """The wiring end to end: update_arc gathers the paths an exported .mrl
    references and feeds them to the check - unconditionally, not only when
    remove_unused_textures is on (that option exists for a different,
    unrelated cleanup). _texture_paths_from_mrl is swapped in rather than
    writing out a real binary .mrl, which test_mrl_parsing.py already covers.
    """
    monkeypatch.setattr(archive_mod, "_texture_paths_from_mrl",
                        lambda data, app_id: {"chr\\pl\\pl00\\pl_vtf5"})

    arc_path = tmp_path / "test.arc"
    _arc_with_one_dummy_entry(arc_path)

    update_arc(str(arc_path), [FakeVFile("chr\\pl\\pl00\\pl00.mrl", app_id="re1")],
               remove_unused_textures=False)

    assert len(recorded_warnings) == 1
    assert "pl_vtf5.tex" in recorded_warnings[0]


def test_update_arc_stays_quiet_when_the_renamed_texture_is_part_of_the_same_export(
        recorded_warnings, monkeypatch, tmp_path):
    """The legitimate case the issue calls out explicitly: a texture that is
    new has the same shape as a dangling rename from here, and must not
    warn just because it wasn't in the arc before."""
    monkeypatch.setattr(archive_mod, "_texture_paths_from_mrl",
                        lambda data, app_id: {"chr\\pl\\pl00\\pl_vtf5"})

    arc_path = tmp_path / "test.arc"
    _arc_with_one_dummy_entry(arc_path)

    update_arc(str(arc_path), [
        FakeVFile("chr\\pl\\pl00\\pl00.mrl", app_id="re1"),
        FakeVFile("chr\\pl\\pl00\\pl_vtf5.tex", data=b"a real texture", app_id="re1"),
    ], remove_unused_textures=False)

    assert recorded_warnings == []


def test_update_arc_says_so_when_an_mrl_cannot_be_checked_at_all(
        recorded_warnings, monkeypatch, tmp_path):
    """_texture_paths_from_mrl returning None (unparseable) must not be read
    as "this file references nothing" - that would silently wave through
    exactly the dangling reference this feature exists to catch. It gets
    its own, differently-worded notice instead of a plain "reachable" check
    it was never actually able to run."""
    monkeypatch.setattr(archive_mod, "_texture_paths_from_mrl", lambda data, app_id: None)

    arc_path = tmp_path / "test.arc"
    _arc_with_one_dummy_entry(arc_path)

    update_arc(str(arc_path), [FakeVFile("chr\\pl\\pl00\\pl00.mrl", app_id="re1")],
               remove_unused_textures=False)

    assert len(recorded_warnings) == 1
    assert "pl00.mrl" in recorded_warnings[0]
    assert "failed to parse" in recorded_warnings[0]
