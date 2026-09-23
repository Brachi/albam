"""_calculate_vertex_group_weight_bound must agree with what the exporter
actually writes for a vertex - see issue #253.

The bug: the filter tested a vertex's raw vertex-group weight, while the
exporter (_process_weights_for_export) normalizes a vertex's kept
influences and then floors any surviving one to at least 1/255
(`round(w * 255) or 1`). Two weights that are both far below one
quantization step - the residue Blender's "Normalize All" leaves behind -
can normalize each other up into a real exported byte while each raw value
still rounds to 0, so the filter dropped a vertex the exporter kept.

The mod-21 half-float formats encode weights differently again, so the
filter mirrors whichever branch `_export_vertices` will take and then
reads the result back the way `_get_weights` does. There a normalized
weight below 1/510 really does serialize to 0 and its bone is unskinned,
while the final slot - which every one of those formats reconstructs from
the remainder rather than a written field - is skinned whenever that
remainder is positive.

Not reachable through an import/export round trip: importer-derived
weights come from the file's already-quantized values, so none of them
round to zero raw. It only shows up on weights authored/edited directly in
Blender, which is why these tests build their vertex groups directly
(no game data needed) instead of round-tripping a file.
"""

from contextlib import contextmanager

import bpy
import pytest

from albam.engines.mtfw.mesh import (
    _bones_with_exported_weight,
    _calculate_weight_bounds,
    _encode_half_float_weight_slots,
    _process_weights_for_export,
    _reconstruct_half_float_weights,
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


@contextmanager
def _rig(bone_names):
    """An armature with one bone per name, plus a 1-vertex mesh with a
    matching vertex group per bone and an ARMATURE modifier wiring them
    together - everything
    get_bone_indices_and_weights_per_vertex/get_mesh_vertex_groups need.
    """
    armature_data = bpy.data.armatures.new("weight_bound_rig")
    armature = bpy.data.objects.new("weight_bound_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous_active = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for i, bone_name in enumerate(bone_names):
            bone = armature_data.edit_bones.new(bone_name)
            bone.head = (float(i), 0.0, 0.0)
            bone.tail = (float(i), 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")

        mesh_data = bpy.data.meshes.new("weight_bound_mesh")
        mesh_data.from_pydata([(0.5, 0.0, 0.0)], [], [])
        mesh_data.update()
        mesh_obj = bpy.data.objects.new("weight_bound_mesh", mesh_data)
        bpy.context.scene.collection.objects.link(mesh_obj)
        for bone_name in bone_names:
            mesh_obj.vertex_groups.new(name=bone_name)
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


@pytest.fixture
def weight_bound_rig():
    with _rig(["A", "B"]) as rig:
        yield rig


@pytest.fixture
def weight_bound_rig_4():
    with _rig(["A", "B", "C", "D"]) as rig:
        yield rig


@pytest.fixture
def weight_bound_rig_8():
    with _rig(["A", "B", "C", "D", "E", "F", "G", "H"]) as rig:
        yield rig


def _bound_bone_ids(armature, mesh_obj, max_bones_per_vertex=4, half_float=False):
    meshes_data = _FakeMeshesData()
    weight_bounds = _calculate_weight_bounds(
        armature, mesh_obj, Mod156, meshes_data, max_bones_per_vertex, half_float)
    return {wb.bone_id for wb in weight_bounds}


def _processed_weights(mesh_obj, max_bones_per_vertex=4, half_float=False):
    weights_per_vertex = get_bone_indices_and_weights_per_vertex(mesh_obj)
    processed = _process_weights_for_export(
        weights_per_vertex, max_bones_per_vertex=max_bones_per_vertex, half_float=half_float)
    (vertex_index, influences), = processed.items()
    return influences


def _exported_weight(mesh_obj, bone_index, max_bones_per_vertex=4):
    return dict(_processed_weights(mesh_obj, max_bones_per_vertex)).get(bone_index)


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


def test_third_row_used_to_slip_past_the_filter():
    """Direct check of the arithmetic issue #253 flags as the dangerous
    case: both raw weights are below one quantization step, so the old
    raw-weight test excluded B while normalization pushed it up to a
    substantial 109/255 in the exported data.
    """
    influence_list = [("A", 0.002), ("B", 0.0015)]
    quantized = dict(_process_weights_for_export(
        {0: influence_list}, max_bones_per_vertex=4, half_float=False)[0])

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


# One 8-influence vertex: A..D are ordinary, E..H are the residue weights.
# Ranked by weight it fills all eight slots of an 8-weight mod-21 format,
# so it exercises both ways that format can leave a bone unskinned:
# E lands in a slot serialized as round(w * 255) and its normalized weight
# (0.001) is below 1/510, so a literal 0 goes into the file; H lands in the
# eighth slot, whose remainder comes back negative once the seven written
# slots are quantized.
HALF_FLOAT_RAW_WEIGHTS = {
    "A": 0.5, "B": 0.3, "C": 0.19, "D": 0.005,
    "E": 0.001, "F": 0.0009, "G": 0.0008, "H": 0.0007,
}


def test_half_float_unskinned_weights_are_not_counted(weight_bound_rig_8):
    """The byte path floors every kept influence to at least 1/255, but the
    mod-21 half-float path does not: a weight that serializes as 0, and a
    final-slot remainder that comes back negative, leave their bones
    unskinned in the exported file, so neither may get a weight bound.
    """
    armature, mesh_obj = weight_bound_rig_8
    for name, weight in HALF_FLOAT_RAW_WEIGHTS.items():
        mesh_obj.vertex_groups[name].add([0], weight, "REPLACE")

    weights_data = _processed_weights(mesh_obj, max_bones_per_vertex=8, half_float=True)
    weight_values = [w for _, w in weights_data]
    _, packed_weights, _ = _encode_half_float_weight_slots(weight_values, 8)
    reconstructed = _reconstruct_half_float_weights(weight_values, 8)

    bones = [armature.pose.bones.find(name) for name in "ABCDEFGH"]
    # the influences rank in A..H order, so each bone lands in its own slot
    assert [bone for bone, _ in weights_data] == bones
    assert packed_weights[2] == 1  # D
    assert packed_weights[3] == 0  # E, a literal zero goes into the file
    assert reconstructed[4] == 0.0  # so the game reads E as unweighted
    assert reconstructed[7] < 0  # and H's remainder is not a real influence

    bound_ids = _bound_bone_ids(
        armature, mesh_obj, max_bones_per_vertex=8, half_float=True)
    assert set(bones) - bound_ids == {bones[4], bones[7]}  # E and H


def test_half_float_and_byte_paths_disagree_for_the_same_vertex():
    """The same vertex, exported by the two branches: the byte path's
    `or 1` floor keeps every influence skinned, the half-float path leaves
    two of them unskinned. The filter has to follow whichever branch the
    format actually takes rather than always assuming the byte one.
    """
    influence_list = list(HALF_FLOAT_RAW_WEIGHTS.items())

    byte_bones = _bones_with_exported_weight(influence_list, 8, half_float=False)
    half_float_bones = _bones_with_exported_weight(influence_list, 8, half_float=True)

    assert byte_bones == set("ABCDEFGH")
    assert byte_bones - half_float_bones == {"E", "H"}


# Every mod-21 half-float format derives its *last* slot from the remainder
# instead of a written field (see _get_weights), so a bone that only ever
# lands in that slot is still skinned in the exported file and still needs a
# weight bound. A blanket "the last slot is never written, so it never
# counts" rule silently deletes the 4th influence on 0x14D40020, the default
# skinned format, and the 2nd influence on every 2-weight format.
FULL_VERTEX_PER_FORMAT = [
    pytest.param(1, {"A": 1.0}, id="1wt"),
    pytest.param(2, {"A": 0.6, "B": 0.4}, id="2wt"),
    pytest.param(4, {"A": 0.4, "B": 0.3, "C": 0.2, "D": 0.1}, id="4wt-default-skinned"),
    pytest.param(8, dict.fromkeys("ABCDEFGH", 0.125), id="8wt"),
]


@pytest.mark.parametrize("max_bones_per_vertex, raw_weights", FULL_VERTEX_PER_FORMAT)
def test_half_float_remainder_slot_is_still_skinned(max_bones_per_vertex, raw_weights):
    """A vertex whose influences exactly fill its format: every bone,
    including the one in the reconstructed final slot, is skinned in the
    exported file, so every one of them counts.
    """
    influence_list = list(raw_weights.items())

    reconstructed = _reconstruct_half_float_weights(
        [w for _, w in _process_weights_for_export(
            {0: influence_list}, max_bones_per_vertex, half_float=True)[0]],
        max_bones_per_vertex,
    )
    assert len(reconstructed) == max_bones_per_vertex
    assert all(w > 0 for w in reconstructed)
    assert sum(reconstructed) == pytest.approx(1.0, abs=1e-3)

    assert _bones_with_exported_weight(
        influence_list, max_bones_per_vertex, half_float=True) == set(raw_weights)


def test_fourth_influence_on_the_default_skinned_format_gets_a_bound(weight_bound_rig_4):
    """The findings trace end to end: on 0x14D40020's 4-weight half-float
    layout the game reconstructs D as 1 - w1 - w2 - w3 = 0.1, so a bone
    that is only ever a 4th influence is genuinely skinned and must get a
    weight bound.
    """
    armature, mesh_obj = weight_bound_rig_4
    for name, weight in {"A": 0.4, "B": 0.3, "C": 0.2, "D": 0.1}.items():
        mesh_obj.vertex_groups[name].add([0], weight, "REPLACE")

    weights_data = _processed_weights(mesh_obj, max_bones_per_vertex=4, half_float=True)
    reconstructed = _reconstruct_half_float_weights([w for _, w in weights_data], 4)
    assert reconstructed[3] == pytest.approx(0.1, abs=1e-3)

    bound_ids = _bound_bone_ids(
        armature, mesh_obj, max_bones_per_vertex=4, half_float=True)
    assert bound_ids == {armature.pose.bones.find(name) for name in "ABCD"}
