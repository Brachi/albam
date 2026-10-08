"""
Regression tests for two archives mounted under the same name (#275: "2
archives with the same name drives the file explorer insane").

The user-visible report was about the *tree*: expanding one of the two
same-named roots also revealed the other one's children, while that other
root's own triangle still read as collapsed. Its cause is that a root vfile
is keyed by name in `vfs.file_list`, and a plain
`app_id::<display name>` key is not unique across two archives that share a
basename - so every child of the second root pointed its `tree_node.root_id`
back at the first, and the UIList's expansion cache (keyed by root id) held
one entry for what the user saw as two roots.
`VirtualFileSystemBase._unique_root_name` gives the second root a `#N`
suffix instead; `tests/test_vfs_fs_backed.py` covers the bytes half of that
(each root reads its own FS), and the tree half is covered here.

Node ids *below* a root are still `app_id::<path parts>` with no root in
them, which is deliberate (see `_unique_root_name`'s docstring) but leaves
anything that walks the tree by ancestor node id alone unable to tell the
two archives apart - covered here too, for the batch-import folder walk.
"""
import bpy
import pytest
from fs.memoryfs import MemoryFS

from albam.blender_ui.import_panel import (
    ALBAM_UL_VirtualFileSystemUIBase,
    folder_descendants,
)
from albam.lib import fs_registry
from albam.vfs import ALBAM_OT_VirtualFileSystemCollapseToggle
from tests.conftest import close_new_fs_roots, remove_new_vfs_roots, vfs_root_names

DUPLICATE_NAME = "uPl00ChrisNormal.arc"


@pytest.fixture(autouse=True)
def _clean_vfs_state():
    # Same session-scoped Blender state every other VFS test shares - see
    # tests/test_vfs_fs_backed.py's own fixture for why this diffs instead
    # of clearing. The UIList expansion cache is process-global class state
    # on the operator, so it needs resetting around each test too.
    before_roots = vfs_root_names()
    before_fs = fs_registry.keys()
    ALBAM_OT_VirtualFileSystemCollapseToggle.NODES_CACHE.clear()
    yield
    remove_new_vfs_roots(before_roots)
    close_new_fs_roots(before_fs)
    ALBAM_OT_VirtualFileSystemCollapseToggle.NODES_CACHE.clear()


class _FileTreeUI(ALBAM_UL_VirtualFileSystemUIBase):
    """The panel's UIList without Blender's UI around it.

    `filter_items` is what decides which rows the file tree shows, and it
    only needs `bitflag_filter_item` and the collapse operator class -
    neither of which requires a registered, drawn `bpy.types.UIList`.
    """
    collapse_toggle_operator_cls = ALBAM_OT_VirtualFileSystemCollapseToggle
    bitflag_filter_item = 1 << 30


def _archive_fs(marker):
    fs_instance = MemoryFS()
    for folder in ("effect", "pawn", "sound"):
        fs_instance.makedirs("/" + folder)
        fs_instance.writebytes(f"/{folder}/thing.mod", marker)
    return fs_instance


def _add_duplicate_named_roots():
    """Two archives with the same name, holding the same internal paths -
    the setup in the issue's screenshot. Returns both roots' unique ids."""
    vfs = bpy.context.scene.albam.vfs
    vfs.add_fs_root("re5", _archive_fs(b"first"), display_name=DUPLICATE_NAME, is_archive=True)
    vfs.add_fs_root("re5", _archive_fs(b"second"), display_name=DUPLICATE_NAME, is_archive=True)
    roots = [vf.name for vf in vfs.file_list if vf.is_root and vf.display_name == DUPLICATE_NAME]
    assert len(roots) == 2
    return roots


def _visible_rows(vfs, root_ids):
    """(display_name, root_id) of the rows the file tree would draw for
    `root_ids`, in tree order.

    Scoped to the roots under test on purpose: `vfs.file_list` is shared by
    the whole session, and other suites' session-scoped game_fs_root
    fixtures mount their own roots into it and never remove them (they run
    under CI's --game-dir), so the whole visible list is not this test's to
    assert on.
    """
    flags, _ = _FileTreeUI().filter_items(bpy.context, vfs, "file_list")
    rows = []
    for i, flag in enumerate(flags):
        if not flag:
            continue
        vfile = vfs.file_list[i]
        owner = vfile.name if vfile.is_root else vfile.tree_node.root_id
        if owner in root_ids:
            rows.append((vfile.display_name, vfile.tree_node.root_id))
    return rows


def _index_of(vfs, root_id, display_name=None):
    """Position of a row in `file_list`, addressed the way the tree UI does.

    By position, not by `file_list[name]`: two same-named archives give
    their identically placed folders the identical node id, and Blender's
    CollectionProperty name lookup returns only the first match - which is
    the very thing these tests are about. The collapse operator takes the
    row's index for the same reason.
    """
    for i, vf in enumerate(vfs.file_list):
        if display_name is None:
            if vf.is_root and vf.name == root_id:
                return i
        elif vf.tree_node.root_id == root_id and vf.display_name == display_name:
            return i
    raise LookupError((root_id, display_name))


def _toggle(vfs, root_id, display_name=None):
    ALBAM_OT_VirtualFileSystemCollapseToggle.button_index = _index_of(
        vfs, root_id, display_name)
    ALBAM_OT_VirtualFileSystemCollapseToggle.execute(
        ALBAM_OT_VirtualFileSystemCollapseToggle, bpy.context
    )


def _child_of(vfs, root_id, display_name):
    return vfs.file_list[_index_of(vfs, root_id, display_name)]


def test_expanding_one_of_two_same_named_roots_leaves_the_other_collapsed():
    """The screenshot in #275: with both archives collapsed, expanding the
    second one listed the first one's children too, under a root still
    drawn as collapsed.
    """
    vfs = bpy.context.scene.albam.vfs
    root_a, root_b = _add_duplicate_named_roots()

    assert _visible_rows(vfs, (root_a, root_b)) == [
        (DUPLICATE_NAME, ""),
        (DUPLICATE_NAME, ""),
    ]

    _toggle(vfs, root_b)

    assert _visible_rows(vfs, (root_a, root_b)) == [
        (DUPLICATE_NAME, ""),
        (DUPLICATE_NAME, ""),
        ("effect", root_b),
        ("pawn", root_b),
        ("sound", root_b),
    ]
    # The tree state has to match the triangle each root is drawn with.
    assert vfs.file_list[root_a].is_expanded is False
    assert vfs.file_list[root_b].is_expanded is True


def test_same_named_roots_expand_their_own_subfolders_independently():
    """Deeper than the root row: two same-named archives hold the same
    internal paths, so their `effect` folders share a node id
    (`re5::effect`) - only `tree_node.root_id` tells them apart.
    """
    vfs = bpy.context.scene.albam.vfs
    root_a, root_b = _add_duplicate_named_roots()

    _toggle(vfs, root_a)
    _toggle(vfs, root_b)
    shared_node_id = _child_of(vfs, root_a, "effect").name
    assert shared_node_id == _child_of(vfs, root_b, "effect").name == "re5::effect"

    _toggle(vfs, root_b, "effect")

    visible = _visible_rows(vfs, (root_a, root_b))
    assert ("thing.mod", root_b) in visible
    assert ("thing.mod", root_a) not in visible


def test_folder_descendants_is_scoped_to_the_root_the_folder_belongs_to():
    """"Batch import folder" on the second archive's folder used to import
    the first archive's identically-placed files as well: it collected every
    vfile whose ancestors named the selected folder's node id, and that id
    is shared by both archives' copies of the folder.
    """
    vfs = bpy.context.scene.albam.vfs
    _, root_b = _add_duplicate_named_roots()

    picked = list(folder_descendants(vfs, _child_of(vfs, root_b, "pawn")))

    assert [vf.get_bytes() for vf in picked] == [b"second"]
    assert [vf.tree_node.root_id for vf in picked] == [root_b]


def test_folder_descendants_on_a_root_takes_only_that_root():
    """A root node keeps its own id in `name` and leaves `tree_node.root_id`
    empty, so it needs the other half of the scoping - "Batch import folder"
    accepts a root row too (it is expandable).
    """
    vfs = bpy.context.scene.albam.vfs
    root_a, _ = _add_duplicate_named_roots()

    picked = list(folder_descendants(vfs, vfs.file_list[root_a]))

    assert len(picked) == 3  # effect/pawn/sound, one .mod each
    assert {vf.get_bytes() for vf in picked} == {b"first"}
    assert {vf.tree_node.root_id for vf in picked} == {root_a}
