"""Which slot of the file each .lmt block is, kept across a .blend.

A block's position is its identity: an empty slot has to stay empty and every
offset in the header is written by position. Import records it as an albam
custom property and export sorts on it, because the order cannot be read back
off the scene. See _lmt_blocks.

All synthetic: these build the object trees directly, no game data needed.
"""

import bpy
import pytest

from albam.exceptions import AlbamCheckFailure


def _new_empty(name, created, parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    created.append(ob)
    return ob


def _new_lmt(name, num_blocks, created):
    """A synthetic, fully-formed .lmt root with num_blocks real blocks,
    stamped the way load_lmt stamps them."""
    from albam.engines.mtfw.animation.animation_import import set_block_index

    root = _new_empty(name, created)
    blocks = []
    for i in range(num_blocks):
        block = _new_empty(f"{name}.{i:04d}", created, parent=root)
        block.albam_lmt_block_owner = root
        set_block_index(block, "re5", i)
        blocks.append(block)
    return root, blocks


def test_block_order_survives_names_that_stop_sorting_in_block_order():
    """Tree order is name order, and names are compared as text.

    Blender keeps `bpy.data.objects` sorted by name, so `children_recursive`
    gives blocks in name order, and re-importing renames the duplicates. Three
    imports of a 256 block file stay in order by luck: the 4th is numbered from
    `.1000`, which sorts before the `.771` of the one before it, and every one
    of its blocks lands 229 slots early. Export reads the recorded index rather
    than the tree, so it does not care.
    """
    from albam.engines.mtfw.animation import _lmt_blocks, get_block_index
    from albam.engines.mtfw.animation.animation_import import set_block_index

    created = []

    def build():
        root = bpy.data.objects.new("anim", None)
        bpy.context.scene.collection.objects.link(root)
        created.append(root)
        for i in range(256):
            block = bpy.data.objects.new(f"anim.{i:04d}", None)
            block.parent = root
            bpy.context.scene.collection.objects.link(block)
            created.append(block)
            set_block_index(block, "re5", i)
        return root

    try:
        roots = [build() for _ in range(4)]
        fourth = roots[-1]

        tree_order = [get_block_index(b, "re5") for b in fourth.children_recursive]
        assert tree_order != list(range(256)), (
            "expected the 4th import's names to stop sorting in block order; "
            "if Blender's numbering changed, this test is no longer measuring anything"
        )
        assert [get_block_index(b, "re5") for b in _lmt_blocks(fourth, "re5")] == list(range(256))
    finally:
        for obj in reversed(created):
            bpy.data.objects.remove(obj, do_unlink=True)


def test_lmt_blocks_excludes_an_empty_load_lmt_never_stamped():
    """Case 1 (#295): any EMPTY parented under a .lmt root - a gizmo, a
    reference point, anything a user put there - is not one of its blocks
    just because it sits underneath it. BLOCK_INDEX_PROP defaults to 0, so
    without this check it would take block 0's slot.
    """
    from albam.engines.mtfw.animation import _lmt_blocks, get_block_index

    created = []
    try:
        root, blocks = _new_lmt("pl00", 4, created)
        foreign = _new_empty("gizmo", created, parent=root)

        result = _lmt_blocks(root, "re5")

        assert foreign not in result
        assert [get_block_index(b, "re5") for b in result] == [0, 1, 2, 3]
    finally:
        for obj in reversed(created):
            bpy.data.objects.remove(obj, do_unlink=True)


def test_lmt_blocks_excludes_blocks_from_a_different_import():
    """Cases 2 and 3 (#295): a block that does carry a recorded index is
    still not this .lmt's just because the Outliner lets it end up
    parented here - a descendant block (case 2, a second .lmt's root
    dragged under the first) and a direct-child block with an index that
    collides with a real one (case 3, a single block dragged directly
    onto the first .lmt's root) both have to be excluded by ownership,
    since neither is caught by descent or by index presence.
    """
    from albam.engines.mtfw.animation import _lmt_blocks, get_block_index

    created = []
    try:
        root, blocks = _new_lmt("pl00", 5, created)

        other_root, other_blocks = _new_lmt("pl00action", 5, created)
        other_root.parent = root  # case 2

        single, _ = _new_lmt("pl00action2", 5, created)
        single.children[3].parent = root  # case 3 - collides with blocks[3]

        result = _lmt_blocks(root, "re5")

        assert all(b not in result for b in other_blocks)
        assert single.children[3] not in result
        assert [get_block_index(b, "re5") for b in result] == [0, 1, 2, 3, 4]
    finally:
        for obj in reversed(created):
            bpy.data.objects.remove(obj, do_unlink=True)


def test_lmt_blocks_keeps_a_block_with_no_owner_recorded():
    """A .blend saved before #295 has no albam_lmt_block_owner on any
    block at all - export must still treat them as belonging to their
    parent rather than suddenly counting zero blocks.
    """
    from albam.engines.mtfw.animation import _lmt_blocks
    from albam.engines.mtfw.animation.animation_import import set_block_index

    created = []
    try:
        root = _new_empty("legacy", created)
        block = _new_empty("legacy.0000", created, parent=root)
        set_block_index(block, "re5", 0)

        assert block.albam_lmt_block_owner is None
        assert _lmt_blocks(root, "re5") == [block]
    finally:
        for obj in reversed(created):
            bpy.data.objects.remove(obj, do_unlink=True)


def test_lmt_blocks_rejects_two_blocks_at_the_same_index():
    """A real, correctly-owned duplicate - e.g. a Shift+D duplicate of a
    block empty in Blender - has to fail loudly rather than export with
    one slot silently doubled and another left empty.
    """
    from albam.engines.mtfw.animation import _lmt_blocks
    from albam.engines.mtfw.animation.animation_import import set_block_index

    created = []
    try:
        root, blocks = _new_lmt("pl00", 2, created)
        dup = _new_empty("pl00.0000.001", created, parent=root)
        dup.albam_lmt_block_owner = root
        set_block_index(dup, "re5", 0)

        with pytest.raises(AlbamCheckFailure):
            _lmt_blocks(root, "re5")
    finally:
        for obj in reversed(created):
            bpy.data.objects.remove(obj, do_unlink=True)
