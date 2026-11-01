"""Preconditions export checks before writing, instead of letting the pack
call fail raw (#369): a mesh's own bone count, the u2 vertex count and
vertex-index fields of each mesh, and a UV value too large for the
half-float format each slot packs into.
"""
from types import SimpleNamespace

import bpy
import pytest

from tests.mtfw.conftest import clear_scene, import_vfile
from tests.mtfw.scripts.catalog_paths import resolve_hashes

RE5_MODEL_HASH = "5d45d4682b062d49"


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

    armature_data = bpy.data.armatures.new("rig")
    armature = bpy.data.objects.new("rig", armature_data)
    mesh_data = bpy.data.meshes.new("mesh")
    mesh_ob = bpy.data.objects.new("mesh", mesh_data)
    previous_active = bpy.context.view_layer.objects.active
    try:
        bpy.context.scene.collection.objects.link(armature)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for i in range(33):
            edit_bone = armature_data.edit_bones.new(str(i))
            edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.context.scene.collection.objects.link(mesh_ob)
        mesh_data.vertices.add(33)
        mesh_data.update()
        for i in range(33):
            vg = mesh_ob.vertex_groups.new(name=str(i))
            vg.add([i], 1.0, 'REPLACE')

        src_mod = SimpleNamespace(header=SimpleNamespace(version=153))
        with pytest.raises(AlbamCheckFailure, match="too many bones"):
            _create_bone_palettes(src_mod, armature, [mesh_ob])
    finally:
        if armature.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(mesh_ob, do_unlink=True)
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.meshes.remove(mesh_data)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous_active


@pytest.fixture
def re5_model(game_fs_root):
    """A real re5 model, imported fresh and dropped again afterwards, along
    with the export setting the vertex-count tests change."""
    export_settings = bpy.context.scene.albam.export_settings
    no_vf_grouping = export_settings.no_vf_grouping
    local_path = resolve_hashes(game_fs_root, {RE5_MODEL_HASH})[RE5_MODEL_HASH].lstrip("/")
    try:
        import_vfile("re5", local_path)
        yield bpy.context.scene.albam.exportable.file_list[-1].bl_object
    finally:
        export_settings.no_vf_grouping = no_vf_grouping
        clear_scene()


def _pad_to_vertex_count(bl_mesh, count):
    """Add loose vertices to bl_mesh until it exports exactly `count`
    vertices. Export keeps vertices no triangle references, so each one
    adds exactly one exported vertex. They get the first vertex's main
    bone, since export refuses unweighted vertices on a skinned model."""
    from albam.engines.mtfw.mesh import _build_export_vertex_table

    missing = count - _build_export_vertex_table(bl_mesh).count
    assert missing >= 0
    first_new = len(bl_mesh.data.vertices)
    bl_mesh.data.vertices.add(missing)
    bl_mesh.data.update()
    group_index = bl_mesh.data.vertices[0].groups[0].group
    bl_mesh.vertex_groups[group_index].add(
        range(first_new, first_new + missing), 1.0, 'REPLACE')


def _meshes(bl_object):
    return [c for c in bl_object.children_recursive if c.type == "MESH"]


def test_export_accepts_meshes_whose_vertices_add_up_past_the_u2_limit_in_separate_blocks(re5_model):
    """With "Don't group meshes by vertex format" on, every mesh starts its
    own vertex block at index 0, so only each mesh's own count is limited:
    two meshes summing past 65535 export fine.

    Calls export_mod directly rather than going through the real
    bpy.ops.albam.export() operator (see import_vfile's own docstring for
    why: that operator wraps any exception into a plain RuntimeError).
    """
    from albam.engines.mtfw.mesh import export_mod

    bpy.context.scene.albam.export_settings.no_vf_grouping = True
    first, second = _meshes(re5_model)[:2]
    _pad_to_vertex_count(first, 40000)
    _pad_to_vertex_count(second, 40000)

    export_mod(re5_model)


def test_export_refuses_a_mesh_sharing_a_block_past_the_u2_limit(re5_model):
    """Grouped by vertex format, a mesh's last index is the running total of
    the block it shares, so two meshes of one format summing past 65535
    can't be addressed, and the error points at the setting that fixes it."""
    from albam.engines.mtfw.mesh import _build_export_vertex_table, export_mod
    from albam.exceptions import AlbamCheckFailure

    bpy.context.scene.albam.export_settings.no_vf_grouping = False
    meshes = _meshes(re5_model)
    vtypes = [m.material_slots[0].material.albam_custom_properties
              .get_custom_properties_for_appid("re5").vtype for m in meshes]
    first, second = meshes[:2]
    # the same vertex format back to back, so both land in one block
    assert vtypes[0] == vtypes[1]
    _pad_to_vertex_count(first, 40000)
    _pad_to_vertex_count(second, 40000)
    assert _build_export_vertex_table(second).count == 40000

    with pytest.raises(AlbamCheckFailure, match="too many vertices") as excinfo:
        export_mod(re5_model)
    assert second.name in excinfo.value.message
    assert "Don't group meshes by vertex format" in excinfo.value.solution


def test_export_refuses_a_single_mesh_of_65536_vertices(re5_model):
    """A mesh of exactly 65536 vertices at the start of its block ends at
    index 65535, which fits, but its own num_vertices (also a u2) doesn't."""
    from albam.engines.mtfw.mesh import export_mod
    from albam.exceptions import AlbamCheckFailure

    bpy.context.scene.albam.export_settings.no_vf_grouping = True
    mesh = _meshes(re5_model)[0]
    _pad_to_vertex_count(mesh, 65536)

    with pytest.raises(AlbamCheckFailure, match="too many vertices") as excinfo:
        export_mod(re5_model)
    assert mesh.name in excinfo.value.message


@pytest.fixture
def uv_mesh():
    """A synthetic one-triangle mesh with two UV maps, the second named so
    the error can be checked for it."""
    mesh_data = bpy.data.meshes.new("uv_mesh")
    mesh_data.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    mesh_data.uv_layers.new(name="first")
    mesh_data.uv_layers.new(name="second")
    mesh_ob = bpy.data.objects.new("uv_mesh", mesh_data)
    try:
        yield mesh_ob
    finally:
        bpy.data.objects.remove(mesh_ob, do_unlink=True)
        bpy.data.meshes.remove(mesh_data)


def _set_uv(mesh_ob, layer_index, u, v):
    for loop_uv in mesh_ob.data.uv_layers[layer_index].data:
        loop_uv.uv = (0.5, 0.5)
    mesh_ob.data.uv_layers[layer_index].data[0].uv = (u, v)


@pytest.mark.parametrize("u, v", [
    (70000.0, 0.5),
    (0.5, -70000.0),
    # v is stored flipped as 1 - v, so this overflows as 65520 even though
    # v itself would pack
    (0.5, -65519.0),
])
def test_export_refuses_a_uv_too_large_for_half_float(uv_mesh, u, v):
    """65520 is where pack('e', ...) starts raising OverflowError (the
    largest finite half float is 65504; values in between round down)."""
    from albam.engines.mtfw.mesh import _build_export_vertex_table, _check_uv_range
    from albam.exceptions import AlbamCheckFailure

    _set_uv(uv_mesh, 1, u, v)
    vertex_table = _build_export_vertex_table(uv_mesh)

    _check_uv_range(uv_mesh, vertex_table, 0)
    with pytest.raises(AlbamCheckFailure, match="too large to export") as excinfo:
        _check_uv_range(uv_mesh, vertex_table, 1)
    assert "uv_mesh" in excinfo.value.message
    assert "'second'" in excinfo.value.details


@pytest.mark.parametrize("u, v", [
    (65519.0, 0.5),
    # flipped to -65519
    (0.5, 65520.0),
])
def test_export_accepts_a_uv_that_rounds_into_half_float(uv_mesh, u, v):
    from albam.engines.mtfw.mesh import _build_export_vertex_table, _check_uv_range

    _set_uv(uv_mesh, 0, u, v)
    _check_uv_range(uv_mesh, _build_export_vertex_table(uv_mesh), 0)


def test_normalize_uv_flips_v_and_drops_negative_zero():
    from albam.engines.mtfw.mesh import _normalize_uv

    assert _normalize_uv(0.5, 0.5) == (0.5, 0.5)
    # -0.0 is replaced with 0.0 (forbidden for half floats), and y is
    # flipped-then-offset for .dds (see the function's own docstring).
    assert _normalize_uv(-0.0, -0.0) == (0.0, 1.0)
