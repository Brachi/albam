"""export_bin's face-corner ceiling: a clear, loud error rather than a
silently truncated file.

The format states both position and normal counts in a u2 (see
albam.engines.cie.mesh.MAX_VERTICES and structs/re4-uhd-bin.ksy), and the
format is non-indexed - one entry per face corner, not per Blender vertex -
so a mesh with enough triangles and no shared corners can exceed it. One
model in the game needs 79,959 corners against the 65,535 the format can
state (see the module docstring on GitHub issue #271); the next largest is
at 70% of the limit. That gap is real, but a model actually hitting it errors
here rather than writing a corrupt file, which is what this test pins down -
closing this as a wontfix rather than engineering around a single model
still needs that error to stay loud.

CI-safe: builds the oversized mesh directly, no game data needed.
"""
import bpy
import pytest

from albam.engines.cie.mesh import MAX_VERTICES, export_bin
from albam.exceptions import AlbamCheckFailure


def _disjoint_triangles_mesh(name, triangle_count):
    """A mesh of `triangle_count` triangles sharing no vertex, UV or normal
    with any other - so every corner the exporter walks is its own, and the
    corner count is exactly 3 * triangle_count (see mesh._collect_geometry's
    per-material corner deduplication, which this gives nothing to merge)."""
    vertices = []
    faces = []
    for i in range(triangle_count):
        base = len(vertices)
        vertices.extend([(i, 0.0, 0.0), (i, 1.0, 0.0), (i, 0.0, 1.0)])
        faces.append((base, base + 1, base + 2))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return mesh


@pytest.fixture
def _oversized_mesh_object():
    # One more triangle than fits: 3 corners each, none shareable.
    triangle_count = MAX_VERTICES // 3 + 1
    mesh = _disjoint_triangles_mesh("albam-test-oversized", triangle_count)
    bl_object = bpy.data.objects.new("albam-test-oversized", mesh)
    bpy.context.collection.objects.link(bl_object)
    bl_object.albam_asset.app_id = "re4uhd"
    yield bl_object
    bpy.data.objects.remove(bl_object, do_unlink=True)
    bpy.data.meshes.remove(mesh)


def test_export_bin_refuses_more_face_corners_than_the_format_can_state(
        _oversized_mesh_object):
    with pytest.raises(AlbamCheckFailure, match="too much geometry") as excinfo:
        export_bin(_oversized_mesh_object)
    assert str(MAX_VERTICES) in excinfo.value.details
