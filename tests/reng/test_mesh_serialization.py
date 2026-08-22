import ctypes
import io
import json
import os

import pytest
from kaitaistruct import KaitaiStream

from tests.mtfw.scripts.catalog_paths import resolve_hashes
from tests.reng.conftest import reng_import_export

# Committed, fixed dataset - a representative subset of mesh_import_hashes.json
# (see that dataset's categories in RESULTS.md): a skinned player character,
# a skinned weapon (bones move its parts, not the whole object), a skinned
# enemy with 8 LOD groups (only LOD 0 is ever imported/exported - the other
# 7 are the main regression check for "everything not touched stays
# identical"), a static prop and a static building/terrain mesh (both with
# no bones at all, so a fully byte-exact case).
MESH_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "mesh_serialization_hashes.json"
)
with open(MESH_SERIALIZATION_DATASET_PATH) as f:
    MESH_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mesh_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mesh_path_hash")
        argvalues = [(d["app_id"], d["mesh_path_hash"]) for d in MESH_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['mesh_path_hash']}" for d in MESH_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MESH_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no real .pak needed.
    """
    for entry in MESH_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mesh_path_hash"] in catalog_hashes, (
            f"{entry['mesh_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def mesh_export_local(reng_vfs_root, local_app_id, local_mesh_path_hash):
    from albam.engines.reng.structs.reengine_mesh import ReengineMesh

    local_mesh_path = resolve_hashes(reng_vfs_root, {local_mesh_path_hash})[local_mesh_path_hash].lstrip("/")

    vfile = reng_import_export(local_app_id, local_mesh_path)
    vfile_exported = bpy_context_exported_vfile(local_app_id, local_mesh_path)

    src_bytes = vfile.get_bytes()
    dst_bytes = vfile_exported.get_bytes()

    src_mesh = ReengineMesh(KaitaiStream(io.BytesIO(src_bytes)))
    src_mesh._read()
    dst_mesh = ReengineMesh(KaitaiStream(io.BytesIO(dst_bytes)))
    dst_mesh._read()

    return src_mesh, dst_mesh, src_bytes, dst_bytes


def bpy_context_exported_vfile(app_id, local_path):
    import bpy
    return bpy.context.scene.albam.exported.select_vfile(app_id, local_path)


def _sub_meshes(mesh):
    lod_group = mesh.model_info.lod_group_offsets[0].lod_group
    return [sm for mg in lod_group.mesh_groups for sm in mg.mesh_group.meshes]


def _decode_weight_pairs(mesh, sub_mesh, num_vertices, weight_acc, name_offset):
    vertex_buffer = mesh.buffers_data.vertex_buffer
    skin_offset = weight_acc.offset + sub_mesh.pos_vertex_buffer * weight_acc.size
    skin = ((ctypes.c_ubyte * 16) * num_vertices).from_buffer_copy(vertex_buffer, skin_offset)
    per_vertex = []
    for data in skin:
        joints = list(data[0:4]) + list(data[4:8])
        weights = list(data[8:12]) + list(data[12:16])
        pairs = set()
        for j, w in zip(joints, weights):
            if w:
                real_bone = mesh.bones_header.bone_maps[j]
                name = mesh.named_nodes[name_offset + real_bone].value
                pairs.add((name, w))
        per_vertex.append(pairs)
    return per_vertex


def test_export_structure_and_material_unchanged(mesh_export_local, subtests):
    """
    Everything about a submesh other than its raw vertex/index bytes
    (material_index, is_quad, vertex_buffer_index, index/vertex counts and
    positions) must come out exactly as it went in - export only ever
    patches buffer contents in place, never these structural fields.
    """
    src_mesh, dst_mesh, _, _ = mesh_export_local
    src_sub_meshes = _sub_meshes(src_mesh)
    dst_sub_meshes = _sub_meshes(dst_mesh)

    assert len(src_sub_meshes) == len(dst_sub_meshes)

    for i, (src_sm, dst_sm) in enumerate(zip(src_sub_meshes, dst_sub_meshes)):
        with subtests.test(sub_mesh=i):
            assert src_sm.material_index == dst_sm.material_index
            assert src_sm.is_quad == dst_sm.is_quad
            assert src_sm.vertex_buffer_index == dst_sm.vertex_buffer_index
            assert src_sm.num_indices == dst_sm.num_indices
            assert src_sm.pos_index_buffer == dst_sm.pos_index_buffer
            assert src_sm.pos_vertex_buffer == dst_sm.pos_vertex_buffer


def test_export_geometry_byte_exact(mesh_export_local, subtests):
    """
    position/UV/index bytes for every LOD-0 submesh must be byte-identical
    to the source: positions and indices are lossless by construction, and
    UV round-trips exactly through f16 (it was f16 to begin with).
    normal+tangent is deliberately NOT checked here - see
    test_export_normals_tangents_semantically_equal for why it's only
    semantically, not byte, exact (it's recomputed from the live mesh on
    every export, on purpose - this is a modding addon, an edit made in
    Blender has to actually reach the exported file).
    """
    src_mesh, dst_mesh, src_bytes, dst_bytes = mesh_export_local
    buffers = src_mesh.buffers_data
    pos_acc, _, uv_acc = buffers.primitive_accessors[0:3]
    vb = buffers.offset_vertex_buffer
    ib = buffers.offset_index_buffer

    for i, sub_mesh in enumerate(_sub_meshes(src_mesh)):
        index_buffer = buffers.index_buffer
        indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(
            index_buffer, sub_mesh.pos_index_buffer * 2
        )
        num_vertices = len(set(indices))

        with subtests.test(sub_mesh=i, region="position"):
            off = vb + pos_acc.offset + sub_mesh.pos_vertex_buffer * pos_acc.size
            size = num_vertices * pos_acc.size
            assert src_bytes[off:off + size] == dst_bytes[off:off + size]

        with subtests.test(sub_mesh=i, region="uv"):
            off = vb + uv_acc.offset + sub_mesh.pos_vertex_buffer * uv_acc.size
            size = num_vertices * uv_acc.size
            assert src_bytes[off:off + size] == dst_bytes[off:off + size]

        with subtests.test(sub_mesh=i, region="index"):
            off = ib + sub_mesh.pos_index_buffer * 2
            size = sub_mesh.num_indices * 2
            assert src_bytes[off:off + size] == dst_bytes[off:off + size]


def test_export_full_file_byte_exact_outside_lossy_regions(mesh_export_local):
    """
    The strongest fidelity check in this file: every byte in the exported
    file must match the source *except* inside a submesh's own skin-weight
    or normal/tangent byte ranges (see test_export_weights_semantically_equal
    and test_export_normals_tangents_semantically_equal for why those two
    regions are only semantically, not byte, exact - both are genuine,
    intentional trade-offs, not bugs). This exercises the whole export
    path at once - header, name tables, bone data (including the
    local/world bone matrices and shadow-mesh header mesh.ksy didn't
    model until this pass), every LOD level other than LOD 0, and the
    header offsets mesh.ksy still doesn't model at all (bone AABBs, blend
    shapes, normal-recalc data) that export restores from source rather
    than reconstructing - not just the handful of regions the other tests
    check individually.
    """
    src_mesh, _, src_bytes, dst_bytes = mesh_export_local
    assert len(src_bytes) == len(dst_bytes)

    lossy_ranges = []
    buffers = src_mesh.buffers_data
    _, nor_tan_acc, _ = buffers.primitive_accessors[0:3]
    weight_acc = next((a for a in buffers.primitive_accessors if a.primitive_type == 4), None)
    vb = buffers.offset_vertex_buffer
    for sub_mesh in _sub_meshes(src_mesh):
        index_buffer = buffers.index_buffer
        indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(
            index_buffer, sub_mesh.pos_index_buffer * 2
        )
        num_vertices = len(set(indices))

        off = vb + nor_tan_acc.offset + sub_mesh.pos_vertex_buffer * nor_tan_acc.size
        lossy_ranges.append((off, off + num_vertices * nor_tan_acc.size))

        if src_mesh.header.offset_bones and weight_acc:
            off = vb + weight_acc.offset + sub_mesh.pos_vertex_buffer * weight_acc.size
            lossy_ranges.append((off, off + num_vertices * weight_acc.size))

    unexpected_diffs = [
        i for i in range(len(src_bytes))
        if src_bytes[i] != dst_bytes[i] and not any(a <= i < b for a, b in lossy_ranges)
    ]
    assert unexpected_diffs == []


def _decode_re_vec3(a, b, c):
    return (a / 127, -c / 127, b / 127)


def _decode_nor_tan(mesh, sub_mesh, num_vertices, nor_tan_acc):
    vertex_buffer = mesh.buffers_data.vertex_buffer
    off = nor_tan_acc.offset + sub_mesh.pos_vertex_buffer * nor_tan_acc.size
    raw = ((ctypes.c_byte * 8) * num_vertices).from_buffer_copy(vertex_buffer, off)
    normals = [_decode_re_vec3(n[0], n[1], n[2]) for n in raw]
    tangents = [_decode_re_vec3(n[4], n[5], n[6]) for n in raw]
    signs = [n[7] / 127 for n in raw]
    return normals, tangents, signs


def test_export_normals_tangents_semantically_equal(mesh_export_local):
    """
    normal/tangent are recomputed from the live Blender mesh on every
    export (see _vertex_normals_tangents in mesh.py) rather than
    round-tripped byte-for-byte, on purpose - this is a modding addon, so
    an edit made in Blender (recalculating normals, reshaping geometry)
    has to actually reach the exported file. That means an *unmodified*
    round trip isn't byte-exact here either, for three real reasons:

    1. Byte index 3 of the 8-byte nor_tan block is a still-unidentified
       value (RESULTS.md), with no Blender-side equivalent at all - not
       recoverable from live geometry, a permanent precision loss.
    2. Blender's tangent generation (calc_tangents()/MikkTSpace) is a
       different algorithm than whatever the original art/export pipeline
       used - even geometrically-identical tangents can come out with a
       different sign or a slightly different direction, particularly at
       UV seams/mirrored islands or tiny/degenerate submeshes, where
       tangent-space generation is inherently under-determined regardless
       of algorithm. Measured directly against this dataset: per-file
       pooled average tangent alignment (dot product) never dropped below
       ~0.82, and per-file sign agreement never dropped below ~85% even on
       the single worst (tiny, 32-vertex) submesh - the thresholds below
       have real headroom under those measured worst cases, not arbitrary
       slack.
    3. int8 quantization (both normal and tangent are stored as
       signed-byte-over-127) means small floating-point differences
       between the two algorithms can legitimately round to
       adjacent-but-different byte values even where 1/2 don't apply.

    normal.xyz has none of the algorithm-choice ambiguity above (both
    sides derive it from the same quantized source, mediated only by
    Blender's own normal storage/rounding) so it's checked with a tight,
    quantization-only tolerance instead.
    """
    src_mesh, dst_mesh, _, _ = mesh_export_local
    buffers = src_mesh.buffers_data
    _, nor_tan_acc, _ = buffers.primitive_accessors[0:3]

    # 3 quantization steps (3/127 ~= 0.0236) - measured max observed delta
    # across the whole dataset is exactly one step (1/127); the extra
    # headroom absorbs float rounding at the boundary, not a real gap.
    NORMAL_TOLERANCE = 3 / 127

    total_vertices = 0
    tangent_dot_sum = 0.0
    sign_matches = 0

    for sub_mesh in _sub_meshes(src_mesh):
        index_buffer = buffers.index_buffer
        indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(index_buffer, sub_mesh.pos_index_buffer * 2)
        num_vertices = len(set(indices))

        src_n, src_t, src_s = _decode_nor_tan(src_mesh, sub_mesh, num_vertices, nor_tan_acc)
        dst_n, dst_t, dst_s = _decode_nor_tan(dst_mesh, sub_mesh, num_vertices, nor_tan_acc)

        for v in range(num_vertices):
            nd = max(abs(a - b) for a, b in zip(src_n[v], dst_n[v]))
            assert nd <= NORMAL_TOLERANCE, f"normal delta {nd} exceeds {NORMAL_TOLERANCE}"

            tangent_dot_sum += sum(a * b for a, b in zip(src_t[v], dst_t[v]))
            if (src_s[v] > 0) == (dst_s[v] > 0):
                sign_matches += 1
        total_vertices += num_vertices

    avg_tangent_dot = tangent_dot_sum / total_vertices
    sign_match_ratio = sign_matches / total_vertices
    assert avg_tangent_dot >= 0.75, f"average tangent alignment {avg_tangent_dot} too low"
    assert sign_match_ratio >= 0.8, f"bitangent-sign agreement {sign_match_ratio} too low"


def test_export_normal_edit_reaches_exported_file(reng_vfs_root):
    """
    The actual point of reworking this from a stashed-byte round trip to a
    live-mesh derivation: an edit made in Blender has to come out the
    other end. Flips every normal (bpy's flip_normals(), which also
    reverses face winding/index order) on a real imported mesh, exports
    it, and asserts the exported normal is now the *opposite* direction
    from the original file's normal - not a copy of it.
    """
    import bpy
    from albam.engines.reng.structs.reengine_mesh import ReengineMesh
    from tests.reng.conftest import reng_import

    # player_jill - a real skinned character file already in this dataset.
    mesh_hash = "094caac02ef9c93b"
    path = resolve_hashes(reng_vfs_root, {mesh_hash})[mesh_hash].lstrip("/")

    before = set(bpy.data.objects.keys())
    vfile = reng_import("re3", path)
    new_objects = [bpy.data.objects[name] for name in bpy.data.objects.keys() if name not in before]
    bl_object = next(ob for ob in new_objects if ob.parent is None)
    bl_mesh_ob = next(ob for ob in new_objects if ob.type == "MESH")

    bl_mesh_ob.data.flip_normals()

    from albam.engines.reng.mesh import export_reengine_mesh

    exported = export_reengine_mesh(bl_object)
    dst_bytes = exported[0].data_bytes

    src_bytes = vfile.get_bytes()
    src_mesh = ReengineMesh(KaitaiStream(io.BytesIO(src_bytes)))
    src_mesh._read()
    dst_mesh = ReengineMesh(KaitaiStream(io.BytesIO(dst_bytes)))
    dst_mesh._read()

    buffers = src_mesh.buffers_data
    _, nor_tan_acc, _ = buffers.primitive_accessors[0:3]
    sub_mesh = _sub_meshes(src_mesh)[0]
    index_buffer = buffers.index_buffer
    indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(index_buffer, sub_mesh.pos_index_buffer * 2)
    num_vertices = len(set(indices))

    src_n, _, _ = _decode_nor_tan(src_mesh, sub_mesh, num_vertices, nor_tan_acc)
    dst_n, _, _ = _decode_nor_tan(dst_mesh, sub_mesh, num_vertices, nor_tan_acc)

    dots = [sum(a * b for a, b in zip(s, d)) for s, d in zip(src_n, dst_n)]
    avg_dot = sum(dots) / len(dots)
    assert avg_dot <= -0.9, (
        f"exported normals should be ~opposite of the source after flip_normals() "
        f"(avg dot {avg_dot}), i.e. the edit reached the exported file"
    )


def test_export_weights_semantically_equal(mesh_export_local, subtests):
    """
    Which of the 8 joint/weight byte-slots a bone lands in isn't
    recoverable from a Blender vertex group (see _encode_vertex_weights in
    mesh.py) - so this is deliberately a semantic check (same set of
    (bone name, quantized weight) pairs per vertex), not a byte-exact one
    like test_export_geometry_byte_exact above.
    """
    src_mesh, dst_mesh, _, _ = mesh_export_local
    if not src_mesh.header.offset_bones:
        pytest.skip("this file has no bones/skin weights")

    buffers = src_mesh.buffers_data
    weight_acc = next(a for a in buffers.primitive_accessors if a.primitive_type == 4)
    name_offset = src_mesh.model_info.num_materials

    src_sub_meshes = _sub_meshes(src_mesh)
    dst_sub_meshes = _sub_meshes(dst_mesh)

    for i, (src_sm, dst_sm) in enumerate(zip(src_sub_meshes, dst_sub_meshes)):
        index_buffer = buffers.index_buffer
        indices = (ctypes.c_ushort * src_sm.num_indices).from_buffer_copy(index_buffer, src_sm.pos_index_buffer * 2)
        num_vertices = len(set(indices))

        src_weights = _decode_weight_pairs(src_mesh, src_sm, num_vertices, weight_acc, name_offset)
        dst_weights = _decode_weight_pairs(dst_mesh, dst_sm, num_vertices, weight_acc, name_offset)

        with subtests.test(sub_mesh=i):
            assert src_weights == dst_weights


@pytest.fixture(scope="session")
def local_app_id():
    return "re3"


def test_export_occlusion_mesh_not_supported(reng_vfs_root):
    """
    A mesh with no main model tree (header.offset_data == 0, e.g. an
    occlusion-culling mesh - see RESULTS.md) has nothing for export to
    patch - it should fail clearly rather than silently produce garbage
    or a copy of the source with nothing exported.
    """
    from albam.exceptions import AlbamCheckFailure
    from albam.engines.reng.mesh import export_reengine_mesh
    from tests.reng.conftest import reng_import

    occlusion_mesh_hash = "ea077b0c68d5007d"
    path = resolve_hashes(reng_vfs_root, {occlusion_mesh_hash})[occlusion_mesh_hash].lstrip("/")

    import bpy
    before = set(bpy.data.objects.keys())
    reng_import("re3", path)
    new_objects = [bpy.data.objects[name] for name in bpy.data.objects.keys() if name not in before]
    bl_object = next(ob for ob in new_objects if ob.parent is None)

    with pytest.raises(AlbamCheckFailure):
        export_reengine_mesh(bl_object)
