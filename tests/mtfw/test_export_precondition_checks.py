"""Preconditions export checks before writing, instead of letting the pack
call fail raw (#369): a mesh's own bone count, the u2 vertex count and
vertex-index fields of each mesh, and a UV value too large for the
half-float format each slot packs into.
"""

import bpy
import pytest

from tests.mtfw.conftest import clear_scene, import_vfile, resolve_hashes_with_remount

RE5_MODEL_HASH = "5d45d4682b062d49"


@pytest.fixture(scope="session")
def local_app_id():
    return "re5"


def test_export_refuses_a_mesh_influenced_by_more_than_32_bones():
    """Synthetic: no game data needed. A mesh whose vertices are weighted to
    more than MAX_BONE_PALETTE_SIZE distinct bones can't fit in one bone
    palette no matter how palettes are split, so this is a hard limit on
    the mesh itself, not the grouping logic below it.
    """
    from albam.engines.mtfw.mod_scene import create_bone_palettes
    from albam.exceptions import AlbamCheckFailure

    with pytest.raises(AlbamCheckFailure, match="too many bones"):
        create_bone_palettes(153, [("mesh", set(range(33)))])


@pytest.fixture
def re5_model(pytestconfig, game_fs_root):
    """A real re5 model, imported fresh and dropped again afterwards, along
    with the export setting the vertex-count tests change."""
    export_settings = bpy.context.scene.albam.export_settings
    no_vf_grouping = export_settings.no_vf_grouping
    local_path = resolve_hashes_with_remount(
        pytestconfig, "re5", game_fs_root, {RE5_MODEL_HASH}
    )[RE5_MODEL_HASH].lstrip("/")
    try:
        import_vfile("re5", local_path)
        yield bpy.context.scene.albam.exportable.file_list[-1].bl_object
    finally:
        export_settings.no_vf_grouping = no_vf_grouping
        clear_scene()


def _exported_vertex_count(bl_mesh):
    from albam.lib.gltf_blender import export_objects

    scene = export_objects([bl_mesh])
    return sum(p.vertex_count for m in scene.meshes for p in m.primitives)


def _pad_to_vertex_count(bl_mesh, count):
    """Add triangles of new vertices to bl_mesh until it exports exactly
    `count` vertices. A vertex no face references is dropped on the way
    through glTF, so every added vertex sits on a face; the faces share no
    attributes that differ between corners, so none of them splits. They
    get the first vertex's main bone, since export refuses unweighted
    vertices on a skinned model."""
    import bmesh

    missing = count - _exported_vertex_count(bl_mesh)
    assert missing >= 0
    first_new = len(bl_mesh.data.vertices)
    bm = bmesh.new()
    bm.from_mesh(bl_mesh.data)
    new_verts = [bm.verts.new((i * 0.001, 0.0, -10.0)) for i in range(missing)]
    for i in range(0, missing, 3):
        corners = new_verts[i:i + 3]
        # the remainder borrows from the previous face: a shared new vertex
        # has identical corners, so it still exports as one vertex
        while len(corners) < 3:
            corners.append(new_verts[i - 1 - (3 - len(corners))])
        bm.faces.new(corners)
    bm.to_mesh(bl_mesh.data)
    bm.free()
    bl_mesh.data.update()
    group_index = bl_mesh.data.vertices[0].groups[0].group
    bl_mesh.vertex_groups[group_index].add(
        range(first_new, first_new + missing), 1.0, 'REPLACE')
    assert _exported_vertex_count(bl_mesh) == count


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
    from albam.engines.mtfw.mesh import export_mod
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


def _uvs(u, v):
    """A one-triangle UV layer as the scene carries it: glTF flips v to
    1 - v, which is also the file's convention."""
    import numpy as np

    return np.array([(u, 1 - v), (0.5, 0.5), (0.5, 0.5)], dtype=np.float32)


@pytest.mark.parametrize("u, v", [
    (70000.0, 0.5),
    (0.5, -70000.0),
    # v is stored flipped as 1 - v, so this overflows as 65520 even though
    # v itself would pack
    (0.5, -65519.0),
])
def test_export_refuses_a_uv_too_large_for_half_float(u, v):
    """65520 is where pack('e', ...) starts raising OverflowError (the
    largest finite half float is 65504; values in between round down)."""
    from albam.engines.mtfw.mod_scene import _check_uv_range
    from albam.exceptions import AlbamCheckFailure

    _check_uv_range("uv_mesh", _uvs(0.5, 0.5), 0)
    with pytest.raises(AlbamCheckFailure, match="too large to export") as excinfo:
        _check_uv_range("uv_mesh", _uvs(u, v), 1)
    assert "uv_mesh" in excinfo.value.message
    assert "UV slot 2" in excinfo.value.details


@pytest.mark.parametrize("u, v", [
    (65519.0, 0.5),
    # flipped to -65519
    (0.5, 65520.0),
])
def test_export_accepts_a_uv_that_rounds_into_half_float(u, v):
    from albam.engines.mtfw.mod_scene import _check_uv_range

    _check_uv_range("uv_mesh", _uvs(u, v), 0)


def test_normalize_uv_flips_v_and_drops_negative_zero():
    from albam.engines.mtfw.mod_scene import _normalize_uv

    assert _normalize_uv(0.5, 0.5) == (0.5, 0.5)
    # -0.0 is replaced with 0.0 (forbidden for half floats), and y is
    # flipped-then-offset for .dds (see the function's own docstring).
    assert _normalize_uv(-0.0, -0.0) == (0.0, 1.0)
