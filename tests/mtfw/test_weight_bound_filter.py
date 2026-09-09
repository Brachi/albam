"""_calculate_vertex_group_weight_bound must agree with what the exporter
actually writes for a vertex - see issue #253.

The bug: the filter tested a vertex's raw vertex-group weight, while the
exporter (_process_weights_for_export) normalizes a vertex's kept
influences and then floors any surviving one to at least 1/255
(`round(w * 255) or 1`). Two weights that are both far below one
quantization step - the residue Blender's "Normalize All" leaves behind -
can normalize each other up into a real exported byte while each raw value
still rounds to 0, so the filter dropped a vertex the exporter kept.

Not reachable through an import/export round trip: importer-derived
weights come from the file's already-quantized values, so none of them
round to zero raw. It only shows up on weights authored/edited directly in
Blender, which is why these tests build their vertex groups directly
(no game data needed) instead of round-tripping a file.
"""

import bpy
import pytest

from albam.engines.mtfw.mesh import (
    _calculate_weight_bounds,
    _normalize_and_quantize_weights,
    _process_weights_for_export,
)
from albam.engines.mtfw.structs.mod_156 import Mod156
from albam.lib.blender import get_bone_indices_and_weights_per_vertex


class _FakeMeshesData:
    """Stand-in for the real MeshesData kaitai struct.

    _calculate_vertex_group_weight_bound only needs something with a
    `_root` a WeightBound (and its children) can be built and _check()ed
    against consistently - it never touches file I/O, so no real Mod156
    instance is required.
    """

    def __init__(self):
        self._root = self


@pytest.fixture
def weight_bound_rig():
    """A 2-bone armature ("A", "B") plus a 1-vertex mesh weighted to both,
    with an ARMATURE modifier wiring them together - everything
    get_bone_indices_and_weights_per_vertex/get_mesh_vertex_groups need.
    """
    armature_data = bpy.data.armatures.new("weight_bound_rig")
    armature = bpy.data.objects.new("weight_bound_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous_active = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        bone_a = armature_data.edit_bones.new("A")
        bone_a.head = (0.0, 0.0, 0.0)
        bone_a.tail = (0.0, 0.0, 0.1)
        bone_b = armature_data.edit_bones.new("B")
        bone_b.head = (1.0, 0.0, 0.0)
        bone_b.tail = (1.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")

        mesh_data = bpy.data.meshes.new("weight_bound_mesh")
        mesh_data.from_pydata([(0.5, 0.0, 0.0)], [], [])
        mesh_data.update()
        mesh_obj = bpy.data.objects.new("weight_bound_mesh", mesh_data)
        bpy.context.scene.collection.objects.link(mesh_obj)
        mesh_obj.vertex_groups.new(name="A")
        mesh_obj.vertex_groups.new(name="B")
        modifier = mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
        modifier.object = armature

        yield armature, mesh_obj
    finally:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(mesh_obj, do_unlink=True)
        bpy.data.meshes.remove(mesh_data)
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous_active


def _bound_bone_ids(armature, mesh_obj, max_bones_per_vertex=4):
    meshes_data = _FakeMeshesData()
    weight_bounds = _calculate_weight_bounds(
        armature, mesh_obj, Mod156, meshes_data, max_bones_per_vertex)
    return {wb.bone_id for wb in weight_bounds}


def _exported_weight(mesh_obj, bone_index, max_bones_per_vertex=4):
    weights_per_vertex = get_bone_indices_and_weights_per_vertex(mesh_obj)
    processed = _process_weights_for_export(
        weights_per_vertex, max_bones_per_vertex=max_bones_per_vertex, half_float=False)
    (vertex_index, influences), = processed.items()
    by_bone = dict(influences)
    return by_bone.get(bone_index)


# raw weights on the vertex -> weight B actually exports at (table in #253)
TABLE_ROWS = [
    pytest.param({"A": 0.9, "B": 0.001}, 1, id="A0.9-B0.001"),
    pytest.param({"A": 0.99998, "B": 0.00002}, 1, id="A0.99998-B0.00002"),
    pytest.param({"A": 0.002, "B": 0.0015}, 109, id="A0.002-B0.0015"),
]


@pytest.mark.parametrize("raw_weights, expected_b_export", TABLE_ROWS)
def test_filter_agrees_with_export_for_weights_below_one_quantization_step(
    weight_bound_rig, raw_weights, expected_b_export,
):
    armature, mesh_obj = weight_bound_rig
    for name, weight in raw_weights.items():
        mesh_obj.vertex_groups[name].add([0], weight, "REPLACE")

    bone_index_b = armature.pose.bones.find("B")
    assert _exported_weight(mesh_obj, bone_index_b) == expected_b_export

    # The exported vertex data skins this vertex to B at a non-zero weight
    # in every row (the "or 1" floor guarantees it once B survives the
    # max_bones_per_vertex truncation, which it does here - only 2
    # influences). The filter must count it towards B's bound exactly when
    # that happens, not when B's *raw* weight alone happens to round to 0.
    assert bone_index_b in _bound_bone_ids(armature, mesh_obj)


def test_third_row_used_to_slip_past_the_filter(weight_bound_rig):
    """Direct check of the arithmetic issue #253 flags as the dangerous
    case: both raw weights are below one quantization step, so the old
    raw-weight test excluded B while normalization pushed it up to a
    substantial 109/255 in the exported data.
    """
    influence_list = [("A", 0.002), ("B", 0.0015)]
    quantized = dict(_normalize_and_quantize_weights(influence_list, max_bones_per_vertex=4))

    assert quantized["B"] == 109
    # a raw-weight test at the export quantization step would have dropped it
    assert round(0.0015 * 255) == 0


def test_ordinary_vertex_is_unaffected(weight_bound_rig):
    """A normal, well-formed vertex (weights well above one quantization
    step) must be included in both bones' bounds, same as before the fix.
    """
    armature, mesh_obj = weight_bound_rig
    mesh_obj.vertex_groups["A"].add([0], 0.7, "REPLACE")
    mesh_obj.vertex_groups["B"].add([0], 0.3, "REPLACE")

    bone_index_a = armature.pose.bones.find("A")
    bone_index_b = armature.pose.bones.find("B")

    # both influences are well above one quantization step (1/255), so
    # neither the "or 1" floor nor the excess correction hides anything
    assert _exported_weight(mesh_obj, bone_index_a) > 1
    assert _exported_weight(mesh_obj, bone_index_b) > 1

    bound_ids = _bound_bone_ids(armature, mesh_obj)
    assert bone_index_a in bound_ids
    assert bone_index_b in bound_ids
