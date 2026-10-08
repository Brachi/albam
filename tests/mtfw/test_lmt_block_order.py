"""Which slot of the file each .lmt block is, kept across a .blend.

A block's position is its identity: an empty slot has to stay empty and every
offset in the header is written by position. Import records it as an albam
custom property and export sorts on it, because the order cannot be read back
off the scene. See _lmt_blocks.

All synthetic: these build the object trees directly, no game data needed.
"""

import bpy


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
