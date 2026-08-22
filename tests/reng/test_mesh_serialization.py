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
    position/normal+tangent/UV/index bytes for every LOD-0 submesh must be
    byte-identical to the source: positions and indices are lossless by
    construction, UV round-trips exactly through f16 (it was f16 to begin
    with), and normal+tangent is read back from the raw bytes stashed at
    import time (see NOR_TAN_LO_ATTR/NOR_TAN_HI_ATTR in mesh.py) rather
    than recomputed - so none of these should ever differ for an
    unmodified re-export.
    """
    src_mesh, dst_mesh, src_bytes, dst_bytes = mesh_export_local
    buffers = src_mesh.buffers_data
    pos_acc, nor_tan_acc, uv_acc = buffers.primitive_accessors[0:3]
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

        with subtests.test(sub_mesh=i, region="nor_tan"):
            off = vb + nor_tan_acc.offset + sub_mesh.pos_vertex_buffer * nor_tan_acc.size
            size = num_vertices * nor_tan_acc.size
            assert src_bytes[off:off + size] == dst_bytes[off:off + size]

        with subtests.test(sub_mesh=i, region="uv"):
            off = vb + uv_acc.offset + sub_mesh.pos_vertex_buffer * uv_acc.size
            size = num_vertices * uv_acc.size
            assert src_bytes[off:off + size] == dst_bytes[off:off + size]

        with subtests.test(sub_mesh=i, region="index"):
            off = ib + sub_mesh.pos_index_buffer * 2
            size = sub_mesh.num_indices * 2
            assert src_bytes[off:off + size] == dst_bytes[off:off + size]


def test_export_full_file_byte_exact_outside_weights(mesh_export_local):
    """
    The strongest fidelity check in this file: every byte in the exported
    file must match the source *except* inside a submesh's own skin-weight
    byte range (see test_export_weights_semantically_equal for why that
    one region is only semantically, not byte, exact). This exercises the
    whole export path at once - header, name tables, bone data (including
    the local/world bone matrices mesh.ksy didn't model until this pass),
    every LOD level other than LOD 0, and the header offsets mesh.ksy
    still doesn't model at all (bone AABBs, and a shadow-mesh tree on
    some files) that export restores from source rather than
    reconstructing - not just the handful of regions the other tests
    check individually.
    """
    src_mesh, _, src_bytes, dst_bytes = mesh_export_local
    assert len(src_bytes) == len(dst_bytes)

    weight_ranges = []
    if src_mesh.header.offset_bones:
        buffers = src_mesh.buffers_data
        weight_acc = next((a for a in buffers.primitive_accessors if a.primitive_type == 4), None)
        if weight_acc:
            vb = buffers.offset_vertex_buffer
            for sub_mesh in _sub_meshes(src_mesh):
                index_buffer = buffers.index_buffer
                indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(
                    index_buffer, sub_mesh.pos_index_buffer * 2
                )
                num_vertices = len(set(indices))
                off = vb + weight_acc.offset + sub_mesh.pos_vertex_buffer * weight_acc.size
                weight_ranges.append((off, off + num_vertices * weight_acc.size))

    unexpected_diffs = [
        i for i in range(len(src_bytes))
        if src_bytes[i] != dst_bytes[i] and not any(a <= i < b for a, b in weight_ranges)
    ]
    assert unexpected_diffs == []


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
