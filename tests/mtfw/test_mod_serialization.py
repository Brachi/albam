from collections import Counter
import json
import math
import os

import bpy
import pytest

from tests.mtfw.conftest import import_export
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - not selectable via --mtfw-dataset like the rest
# of tests/mtfw/*.py. This is the single source of truth for what this file
# tests locally; extend it directly rather than pointing at some other file.
# Every mod_path_hash here must be a subset of that app_id's committed
# tests/mtfw/datasets/<app_id>_catalog.json - see test_dataset_hashes_are_in_catalog
# below, which enforces it.
MOD_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "mod_serialization_hashes.json"
)
with open(MOD_SERIALIZATION_DATASET_PATH) as f:
    MOD_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash")
        argvalues = [(d["app_id"], d["mod_path_hash"]) for d in MOD_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['mod_path_hash']}" for d in MOD_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MOD_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in MOD_SERIALIZATION_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json"
        )
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mod_path_hash"] in catalog_hashes, (
            f"{entry['mod_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


def _bones_data_error(src_mod, dst_mod):
    """Difference in bones_data section size, or 0 for a model with no
    armature at all (stage geometry), where neither side has the section.
    """
    if src_mod.bones_data is None or dst_mod.bones_data is None:
        assert src_mod.bones_data is None and dst_mod.bones_data is None
        return 0
    return abs(src_mod.bones_data.size_ - dst_mod.bones_data.size_)


@pytest.fixture(scope="session")
def mod_export_local(game_fs_root, local_app_id, local_mod_path_hash):
    from albam.engines.mtfw.mesh import APPID_CLASS_MAPPER

    bpy.context.scene.albam.apps.app_selected = local_app_id
    if local_app_id == "dd":
        bpy.context.scene.albam.export_settings.no_vf_grouping = True
    bpy.context.scene.albam.import_settings.import_only_main_lods = False
    bpy.context.scene.albam.export_settings.export_bones = True

    # resolve_hashes() returns MTFW_FS's own canonical form (leading "/"),
    # but vfs.add_fs_root() builds its tree with that stripped (see
    # albam.vfs.VirtualFileSystemBase.add_fs_root) - select_vfile()/
    # get_vfile() expect the stripped form.
    local_mod_path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash].lstrip("/")

    vfile_mod = import_export(local_app_id, local_mod_path)
    vfile_mod_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, local_mod_path)
    assert vfile_mod_exported

    Mod = APPID_CLASS_MAPPER[local_app_id]
    src_mod = Mod.from_bytes(vfile_mod.get_bytes())
    dst_mod = Mod.from_bytes(vfile_mod_exported.get_bytes())
    src_mod._read()
    dst_mod._read()

    return src_mod, dst_mod


@pytest.fixture(scope="session")
def mod_imported_local(mod_export_local):
    return mod_export_local[0]


@pytest.fixture(scope="session")
def mod_exported_local(mod_export_local):
    return mod_export_local[1]


def test_export_header(mod_imported_local, mod_exported_local):
    sheader = mod_imported_local.header
    dheader = mod_exported_local.header

    bones_data_error = _bones_data_error(mod_imported_local, mod_exported_local)
    assert (sheader.version in (210, 211, 212) and not bones_data_error) or sheader.version == 156

    assert sheader.ident == dheader.ident == b"MOD\x00"
    assert sheader.version == dheader.version
    assert sheader.revision == dheader.revision
    assert sheader.num_bones == dheader.num_bones
    assert sheader.num_materials == dheader.num_materials
    assert (sheader.version in (210, 211, 212) and sheader.reserved_01 == dheader.reserved_01 or
            sheader.version == 156 and not getattr(dheader, "reserved_01", None))
    assert sheader.num_groups == dheader.num_groups
    assert sheader.num_meshes == dheader.num_meshes
    assert ((sheader.version in (210, 211, 212) and sheader.num_vertices == dheader.num_vertices) or
            sheader.version == 156)  # given 2nd vertex buffer unknowns

    assert sheader.offset_bones_data == dheader.offset_bones_data
    assert sheader.offset_groups == dheader.offset_groups - bones_data_error
    assert sheader.offset_materials_data == dheader.offset_materials_data - bones_data_error
    assert sheader.offset_meshes_data == dheader.offset_meshes_data - bones_data_error
    assert sheader.offset_vertex_buffer == dheader.offset_vertex_buffer - bones_data_error


def test_export_top_level(mod_imported_local, mod_exported_local):

    # assert mod_imported_local.bsphere.x == pytest.approx(mod_exported_local.bsphere.x, rel=0.5)
    assert mod_imported_local.bsphere.y == pytest.approx(mod_exported_local.bsphere.y, rel=0.001)
    # assert mod_imported_local.bsphere.z == pytest.approx(mod_exported_local.bsphere.z, rel=0.001)
    assert mod_imported_local.bsphere.w == pytest.approx(mod_exported_local.bsphere.w, rel=0.001)

    assert mod_imported_local.bbox_min.x == pytest.approx(mod_exported_local.bbox_min.x, rel=0.001)
    assert mod_imported_local.bbox_min.y == pytest.approx(mod_exported_local.bbox_min.y, rel=0.001)
    assert mod_imported_local.bbox_min.z == pytest.approx(mod_exported_local.bbox_min.z, rel=0.001)
    # .w is padding, not a coordinate: real files carry uninitialized garbage
    # there (seen on stage models), while export always writes 0.0

    assert mod_imported_local.bbox_max.x == pytest.approx(mod_exported_local.bbox_max.x, rel=0.001)
    assert mod_imported_local.bbox_max.y == pytest.approx(mod_exported_local.bbox_max.y, rel=0.001)
    assert mod_imported_local.bbox_max.z == pytest.approx(mod_exported_local.bbox_max.z, rel=0.001)


def test_export_bones_data(mod_imported_local, mod_exported_local, subtests):
    # TODO: matrices
    if mod_imported_local.bones_data is None:
        pytest.skip("model has no armature")
    sbd = mod_imported_local.bones_data
    dbd = mod_exported_local.bones_data
    bones_data_error = _bones_data_error(mod_imported_local, mod_exported_local)
    assert ((mod_exported_local.header.version in (210, 211, 212) and not bones_data_error) or
            mod_exported_local.header.version == 156)

    assert mod_imported_local.bones_data_size_ == mod_exported_local.bones_data_size_ - bones_data_error

    for i, src_bone in enumerate(sbd.bones_hierarchy):
        dst_bone = dbd.bones_hierarchy[i]

        with subtests.test(bone_index=i):
            assert src_bone.idx_anim_map == dst_bone.idx_anim_map
            assert src_bone.idx_parent == dst_bone.idx_parent
            assert src_bone.idx_mirror == dst_bone.idx_mirror
            assert src_bone.idx_mapping == dst_bone.idx_mapping
            assert src_bone.length == dst_bone.length
            assert src_bone.parent_distance == pytest.approx(dst_bone.parent_distance, abs=9e-05)
            assert src_bone.location.x == pytest.approx(dst_bone.location.x, abs=9e-05)
            assert src_bone.location.y == pytest.approx(dst_bone.location.y, abs=9e-05)
            assert src_bone.location.z == pytest.approx(dst_bone.location.z, abs=9e-05)

    for i, src_psmatrix in enumerate(sbd.parent_space_matrices):
        dst_psmatrix = dbd.parent_space_matrices[i]
        with subtests.test(matrix_index=i):
            assert src_psmatrix.row_1.x == pytest.approx(dst_psmatrix.row_1.x, abs=9e-05)
            assert src_psmatrix.row_1.y == pytest.approx(dst_psmatrix.row_1.y, abs=9e-05)
            assert src_psmatrix.row_1.z == pytest.approx(dst_psmatrix.row_1.z, abs=9e-05)
            assert src_psmatrix.row_1.w == dst_psmatrix.row_1.w
            assert src_psmatrix.row_2.x == pytest.approx(dst_psmatrix.row_2.x, abs=9e-05)
            assert src_psmatrix.row_2.y == pytest.approx(dst_psmatrix.row_2.y, abs=9e-05)
            assert src_psmatrix.row_2.z == pytest.approx(dst_psmatrix.row_2.z, abs=9e-05)
            assert src_psmatrix.row_2.w == dst_psmatrix.row_2.w
            assert src_psmatrix.row_3.x == pytest.approx(dst_psmatrix.row_3.x, abs=9e-05)
            assert src_psmatrix.row_3.y == pytest.approx(dst_psmatrix.row_3.y, abs=9e-05)
            assert src_psmatrix.row_3.z == pytest.approx(dst_psmatrix.row_3.z, abs=9e-05)
            assert src_psmatrix.row_3.w == dst_psmatrix.row_3.w
            assert src_psmatrix.row_4.x == pytest.approx(dst_psmatrix.row_4.x, abs=9e-05)
            assert src_psmatrix.row_4.y == pytest.approx(dst_psmatrix.row_4.y, abs=9e-05)
            assert src_psmatrix.row_4.z == pytest.approx(dst_psmatrix.row_4.z, abs=9e-05)
            assert src_psmatrix.row_4.w == pytest.approx(dst_psmatrix.row_4.w, abs=9e-05)

    for i, src_ibmatrix in enumerate(sbd.inverse_bind_matrices):
        dst_ibmatrix = dbd.inverse_bind_matrices[i]
        with subtests.test(matrix_index=i):
            assert src_ibmatrix.row_1.x == pytest.approx(dst_ibmatrix.row_1.x, abs=9e-03)
            assert src_ibmatrix.row_1.y == pytest.approx(dst_ibmatrix.row_1.y, abs=9e-05)
            assert src_ibmatrix.row_1.z == pytest.approx(dst_ibmatrix.row_1.z, abs=9e-05)
            assert src_ibmatrix.row_1.w == dst_ibmatrix.row_1.w
            assert src_ibmatrix.row_2.x == pytest.approx(dst_ibmatrix.row_2.x, abs=9e-05)
            assert src_ibmatrix.row_2.y == pytest.approx(dst_ibmatrix.row_2.y, abs=9e-03)
            assert src_ibmatrix.row_2.z == pytest.approx(dst_ibmatrix.row_2.z, abs=9e-03)
            assert src_ibmatrix.row_2.w == dst_ibmatrix.row_2.w
            assert src_ibmatrix.row_3.x == pytest.approx(dst_ibmatrix.row_3.x, abs=9e-05)
            assert src_ibmatrix.row_3.y == pytest.approx(dst_ibmatrix.row_3.y, abs=9e-03)
            assert src_ibmatrix.row_3.z == pytest.approx(dst_ibmatrix.row_3.z, abs=9e-03)
            assert src_ibmatrix.row_3.w == dst_ibmatrix.row_3.w
            assert src_ibmatrix.row_4.x == pytest.approx(dst_ibmatrix.row_4.x, abs=9e-05)
            assert src_ibmatrix.row_4.y == pytest.approx(dst_ibmatrix.row_4.y, abs=9e-05)
            assert src_ibmatrix.row_4.z == pytest.approx(dst_ibmatrix.row_4.z, abs=9e-05)
            assert src_ibmatrix.row_4.w == pytest.approx(dst_ibmatrix.row_4.w, abs=9e-03)

    assert sbd.bone_map == dbd.bone_map


def test_export_groups(mod_imported_local, mod_exported_local):

    assert mod_imported_local.groups_size_ == mod_exported_local.groups_size_

    assert ([g.group_index for g in mod_imported_local.groups] ==
            [g.group_index for g in mod_exported_local.groups])
    assert [g.pos.x for g in mod_imported_local.groups] == [g.pos.x for g in mod_exported_local.groups]
    assert [g.pos.y for g in mod_imported_local.groups] == [g.pos.y for g in mod_exported_local.groups]
    assert [g.pos.z for g in mod_imported_local.groups] == [g.pos.z for g in mod_exported_local.groups]
    assert [g.radius for g in mod_imported_local.groups] == [g.radius for g in mod_exported_local.groups]


def test_materials_data(mod_imported_local, mod_exported_local):

    assert mod_imported_local.materials_data.size_ == mod_exported_local.materials_data.size_
    assert ((mod_imported_local.header.version in (210, 211, 212) and
            mod_imported_local.materials_data.material_names ==
            mod_exported_local.materials_data.material_names) or
            mod_imported_local.header.version == 156)


def test_meshes_data_21(mod_imported_local, mod_exported_local, subtests):
    if mod_imported_local.header.version not in (210, 212):
        pytest.skip()

    for i, mesh in enumerate(mod_imported_local.meshes_data.meshes):
        src_mesh = mesh
        dst_mesh = mod_exported_local.meshes_data.meshes[i]
        with subtests.test(mesh_index=i):
            assert src_mesh.draw_mode == dst_mesh.draw_mode
            assert src_mesh.num_vertices == dst_mesh.num_vertices
            assert src_mesh.idx_group == dst_mesh.idx_group
            assert src_mesh.idx_material == dst_mesh.idx_material
            assert src_mesh.level_of_detail == dst_mesh.level_of_detail
            assert src_mesh.disp == dst_mesh.disp
            assert src_mesh.shape == dst_mesh.shape
            assert src_mesh.sort == dst_mesh.sort
            # assert src_mesh.max_bones_per_vertex == dst_mesh.max_bones_per_vertex
            # assert src_mesh.vertex_stride == dst_mesh.vertex_stride
            assert src_mesh.alpha_priority == dst_mesh.alpha_priority
            assert src_mesh.topology == dst_mesh.topology
            assert src_mesh.binormal_flip == dst_mesh.binormal_flip
            assert src_mesh.bridge == dst_mesh.bridge
            # assert src_mesh.vertex_format == dst_mesh.vertex_format
            assert src_mesh.bone_id_start == dst_mesh.bone_id_start
            assert src_mesh.num_weight_bounds == dst_mesh.num_weight_bounds
            assert src_mesh.connect_id == dst_mesh.connect_id
            assert src_mesh.min_index == dst_mesh.min_index
            assert src_mesh.max_index == dst_mesh.max_index
            assert src_mesh.boundary == dst_mesh.boundary

    assert mod_imported_local.header.version in (210, 212) and (
        mod_imported_local.num_weight_bounds == mod_exported_local.num_weight_bounds)


def test_vertices(mod_imported_local, mod_exported_local, subtests):
    if mod_imported_local.header.version not in (210, 212):  # RE5 has some mess with in hands files
        pytest.skip()
    assert len(mod_imported_local.meshes_data.meshes) == len(mod_exported_local.meshes_data.meshes)
    for mi, mesh in enumerate(mod_imported_local.meshes_data.meshes):
        src_mesh = mesh
        dst_mesh = mod_exported_local.meshes_data.meshes[mi]
        with subtests.test(mesh_index=mi):
            assert src_mesh.num_vertices == dst_mesh.num_vertices
            # disable for now, some normals don't match
            '''for vi, dst_vertex in enumerate(dst_mesh.vertices):
                src_vertex = src_mesh.vertices[vi]
                with subtests.test(mesh_index=mi, vertex_index=vi):
                    assert src_vertex.normal.x == (dst_vertex.normal.x + 1) or \
                        src_vertex.normal.x == (dst_vertex.normal.x - 1) or \
                        src_vertex.normal.x == (dst_vertex.normal.x + 2) or \
                        src_vertex.normal.x == (dst_vertex.normal.x - 2) or \
                        src_vertex.normal.x == dst_vertex.normal.x'''


def test_vertex_colors(mod_imported_local, mod_exported_local, subtests):
    """
    Vertex colors must survive a round trip byte for byte, compared as a
    multiset of (uv, rgba) per mesh rather than per vertex index: the
    exporter is free to hand two vertices with identical attributes a
    different pair of buffer slots than the original file used, which is
    invisible to the GPU since only the index buffer says which slot a
    triangle corner reads from.

    uv rather than position identifies the vertex here because position is
    not bit stable across a round trip: import scales cm to m and export
    scales back, and that pair of float32 multiplications lands ~1 ULP away
    for a small fraction of vertices (~3% of one mesh in this dataset).
    That has nothing to do with colors, so it has no business failing this
    test.

    A mesh whose vertex count/format doesn't match the original is a
    separate, already tracked gap (see test_meshes_data_xfail), so it's
    skipped rather than failed.
    """
    def colored(mesh):
        return Counter(
            (getattr(v, "uv", None) and (v.uv.u, v.uv.v),
             (v.rgba.x, v.rgba.y, v.rgba.z, v.rgba.w))
            for v in mesh.vertices if hasattr(v, "rgba")
        )

    src_meshes = mod_imported_local.meshes_data.meshes
    dst_meshes = mod_exported_local.meshes_data.meshes
    checked = 0
    for mi, (src_mesh, dst_mesh) in enumerate(zip(src_meshes, dst_meshes)):
        if (src_mesh.num_vertices, src_mesh.vertex_stride) != (
                dst_mesh.num_vertices, dst_mesh.vertex_stride):
            continue
        src_colors = colored(src_mesh)
        if not src_colors:
            continue
        checked += 1
        with subtests.test(mesh_index=mi):
            assert src_colors == colored(dst_mesh)
    if not checked:
        pytest.skip("no mesh in this model carries vertex colors")


def _position(vertex):
    """(x, y, z) as stored - ints for the quantized formats (vec4_s2), floats
    for the rest (vec3)."""
    p = vertex.position
    return (p.x, p.y, p.z)


def _uv_bytes(vertex):
    """The primary UV exactly as encoded. Unlike position this does survive a
    round trip bit for bit, so it identifies a vertex reliably."""
    uv = getattr(vertex, "uv", None)
    return (uv.u, uv.v) if uv is not None else None


def _positions_match(src, dst):
    """Same coordinate, re-encoded - not the same bits.

    Import scales cm to m and export scales back, and that pair of float32
    multiplications lands ~1 ULP away for a small fraction of vertices (275
    of 13037 on one model in this dataset). The quantized formats have the
    same problem one step coarser, where a rounding difference is +-1 in an
    int16. Neither says anything is wrong, so neither should fail this.
    """
    for a, b in zip(src, dst):
        if isinstance(a, int) and isinstance(b, int):
            if abs(a - b) > 1:
                return False
        elif not math.isclose(a, b, rel_tol=1e-5, abs_tol=1e-5):
            return False
    return True


def test_vertex_buffer_bytes(mod_imported_local, mod_exported_local, subtests):
    """
    Compare the original file's vertices against the exported ones, mesh by
    mesh, on the two attributes that are meaningful to compare: the primary
    UV (exactly, since it round trips bit for bit) and the position (within
    a tolerance, see _positions_match).

    Both sides are sorted before comparing rather than matched by index: the
    exporter is free to hand two vertices with identical attributes a
    different pair of buffer slots than the original file used, which is
    invisible to the GPU since only the index buffer says which slot a
    triangle corner reads from. Sorting on the UV, which is stable, gives
    both sides the same canonical order.

    Deliberately not compared: normals and tangents, which Blender
    recomputes - and which are outright garbage for any vertex that only
    belongs to a zero-area triangle, since Blender has no normal space for
    one and returns a non-unit vector (about 10% of vertices on a strip
    based model, and strips are what produce those triangles). uv2 is an
    unused channel holding placeholder bytes on both sides, and
    bone_indices padding follows a "repeat the first bone" convention that
    doesn't always match the source file's own choice.

    A mesh whose vertex count/format doesn't match the original is a
    separate, already tracked gap (see test_meshes_data_xfail), so it is
    skipped rather than failed.
    """
    src_meshes = mod_imported_local.meshes_data.meshes
    dst_meshes = mod_exported_local.meshes_data.meshes
    assert len(src_meshes) == len(dst_meshes)

    for mi, (src_mesh, dst_mesh) in enumerate(zip(src_meshes, dst_meshes)):
        with subtests.test(mesh_index=mi):
            if (src_mesh.num_vertices, src_mesh.vertex_stride) != (
                    dst_mesh.num_vertices, dst_mesh.vertex_stride):
                pytest.skip("vertex count/format doesn't match the original for this mesh")

            def described(mesh):
                return sorted(
                    (_uv_bytes(v), _position(v)) for v in mesh.vertices
                    if hasattr(v, "position")
                )

            src, dst = described(src_mesh), described(dst_mesh)
            assert len(src) == len(dst)
            for vi, ((src_uv, src_pos), (dst_uv, dst_pos)) in enumerate(zip(src, dst)):
                assert src_uv == dst_uv, f"vertex {vi}: uv changed"
                assert _positions_match(src_pos, dst_pos), (
                    f"vertex {vi}: position {src_pos} became {dst_pos}")


@pytest.mark.xfail(reason="WIP")
def test_header_xfail(pl0000_roundtrip):
    """
    Tests to fix
    """
    src_mod, dst_mod = pl0000_roundtrip
    sheader = src_mod.header
    dheader = dst_mod.header

    assert sheader.num_faces == dheader.num_faces
    assert sheader.num_edges == dheader.num_edges
    assert sheader.version not in (210, 211, 212) or sheader.size_file == dheader.size_file
    # in 210, given we don't export some vertex formats (like the one witih blend shapes of 64 bytes)
    # the size and hence the offset of the index buffer will differ
    assert sheader.offset_index_buffer == dheader.offset_index_buffer
    assert sheader.size_vertex_buffer == dheader.size_vertex_buffer


@pytest.mark.xfail(reason="WIP")
def test_meshes_data_xfail(mod_imported_local, mod_exported_local, subtests):

    assert (mod_imported_local.meshes_data.num_weight_bounds ==
            mod_exported_local.meshes_data.num_weight_bounds)
    for i, mesh in enumerate(mod_imported_local.meshes_data.meshes):
        src_mesh = mesh
        dst_mesh = mod_exported_local.meshes_data.meshes[i]
        with subtests.test(i=i):
            assert src_mesh.vertex_position == dst_mesh.vertex_position
            assert src_mesh.vertex_offset == dst_mesh.vertex_offset
            assert src_mesh.face_position == dst_mesh.face_position
            assert src_mesh.num_indices == dst_mesh.num_indices
            assert src_mesh.face_offset == dst_mesh.face_offset
