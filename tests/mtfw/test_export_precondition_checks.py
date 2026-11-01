"""Preconditions export checks before writing, instead of letting the pack
call fail raw (#369): a mesh's own bone count, the running vertex-index
total every mesh sharing a vertex block adds to, and a UV value too large
for the half-float format each slot packs into.
"""
from types import SimpleNamespace

import bpy
import pytest

from tests.mtfw.conftest import import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes


@pytest.fixture(scope="session")
def local_app_id():
    return "re5"


def test_export_refuses_a_mesh_influenced_by_more_than_32_bones():
    """Synthetic: no game data needed. A mesh whose vertex groups reference
    more than MAX_BONE_PALETTE_SIZE distinct bones can't fit in one bone
    palette no matter how palettes are split, so this is a hard limit on
    the mesh itself, not the grouping logic below it.
    """
    from albam.engines.mtfw.mesh import _create_bone_palettes
    from albam.exceptions import AlbamCheckFailure

    created = []
    try:
        armature_data = bpy.data.armatures.new("rig")
        armature = bpy.data.objects.new("rig", armature_data)
        bpy.context.scene.collection.objects.link(armature)
        created.append(armature)

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for i in range(33):
            edit_bone = armature_data.edit_bones.new(str(i))
            edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")

        mesh_data = bpy.data.meshes.new("mesh")
        mesh_ob = bpy.data.objects.new("mesh", mesh_data)
        bpy.context.scene.collection.objects.link(mesh_ob)
        created.append(mesh_ob)
        mesh_data.vertices.add(33)
        mesh_data.update()
        for i in range(33):
            vg = mesh_ob.vertex_groups.new(name=str(i))
            vg.add([i], 1.0, 'REPLACE')

        src_mod = SimpleNamespace(header=SimpleNamespace(version=153))
        with pytest.raises(AlbamCheckFailure, match="too many bones"):
            _create_bone_palettes(src_mod, armature, [mesh_ob])
    finally:
        for obj in reversed(created):
            bpy.data.objects.remove(obj, do_unlink=True)


def test_export_refuses_a_mesh_whose_vertex_index_overflows_the_format(game_fs_root, monkeypatch):
    """A real re5 mesh, with the real limit (MAX_MESH_LAST_INDEX, a u2 on
    every mod version this export path handles) monkeypatched down so any
    mesh trips it - the point here is that _serialize_meshes_data catches
    this itself rather than letting Kaitai's write_u2le raise a bare
    struct.error with no indication of which mesh or why.

    Calls export_mod directly rather than going through the real
    bpy.ops.albam.export() operator (see import_vfile's own docstring for
    why: that operator wraps any exception into a plain RuntimeError, same
    as every other operator's error handling - precise enough for a user,
    not for asserting on the specific AlbamCheckFailure here).
    """
    import albam.engines.mtfw.mesh as mesh_mod
    from albam.exceptions import AlbamCheckFailure

    monkeypatch.setattr(mesh_mod, "MAX_MESH_LAST_INDEX", 2)

    local_path = resolve_hashes(game_fs_root, {"5d45d4682b062d49"})["5d45d4682b062d49"].lstrip("/")
    import_vfile("re5", local_path)
    bl_object = bpy.context.scene.albam.exportable.file_list[-1].bl_object

    with pytest.raises(AlbamCheckFailure, match="too many vertices"):
        mesh_mod.export_mod(bl_object)


@pytest.mark.parametrize("uv_x, uv_y", [
    (70000.0, 0.0),
    (0.0, -70000.0),  # _normalize_uv flips y, so a large negative overflows too
])
def test_normalize_uv_refuses_a_value_too_large_for_half_float(uv_x, uv_y):
    """Synthetic, no game data needed. 65520 is where pack('e', ...) itself
    starts raising OverflowError (measured: 65519 packs fine, 65520
    doesn't) - not a number worth hand-maintaining, so this exercises the
    real boundary rather than asserting a hardcoded one.
    """
    from albam.engines.mtfw.mesh import _normalize_uv
    from albam.exceptions import AlbamCheckFailure

    with pytest.raises(AlbamCheckFailure, match="too large to export"):
        _normalize_uv(uv_x, uv_y)


def test_normalize_uv_accepts_ordinary_values():
    from albam.engines.mtfw.mesh import _normalize_uv

    assert _normalize_uv(0.5, 0.5) == (0.5, 0.5)
    # -0.0 is replaced with 0.0 (forbidden for half floats), and y is
    # flipped-then-offset for .dds (see the function's own docstring).
    assert _normalize_uv(-0.0, -0.0) == (0.0, 1.0)
