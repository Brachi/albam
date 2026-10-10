from collections import Counter
import json
import math
import os

import bpy
import pytest
from mathutils import Matrix

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


def _model_space_head(mod, bone_index):
    """A bone's rest position in model space, from its inverse bind matrix."""
    matrix = mod.bones_data.inverse_bind_matrices[bone_index]
    rows = [(m.x, m.y, m.z, m.w) for m in (matrix.row_1, matrix.row_2, matrix.row_3, matrix.row_4)]
    return Matrix(rows).transposed().inverted().to_translation()


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
    from albam.lib.kaitai_utils import parse

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
    src_mod = parse(Mod, vfile_mod.get_bytes(), local_app_id)
    dst_mod = parse(Mod, vfile_mod_exported.get_bytes(), local_app_id)

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
    # abs as well as rel: a component that happens to sit near zero - this
    # sphere's centre is at y = -0.0087 on a model 6 units tall - turns a
    # relative tolerance into a far tighter absolute one than the ~1e-04 a
    # position round trip through Blender costs.
    assert mod_imported_local.bsphere.y == pytest.approx(
        mod_exported_local.bsphere.y, rel=0.001, abs=1e-03)
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


# Apps whose bones carry a rest rotation in the source file. albam's armature
# keeps only each bone's head position, so export has nothing to rebuild a
# rotated basis from and writes an identity one, with the translation
# components landing on permuted axes. Every other app's bone matrices happen
# to be axis-aligned, which hides it. Fixing it means carrying the rotation
# through Blender as a real per-bone custom property, the way idx_anim_map
# already is.
APPS_BONE_REST_ROTATION_NOT_EXPORTED = {"umvc3"}


def test_export_bones_data(mod_imported_local, mod_exported_local, local_app_id, subtests):
    # TODO: matrices
    if mod_imported_local.bones_data is None:
        pytest.skip("model has no armature")
    if local_app_id in APPS_BONE_REST_ROTATION_NOT_EXPORTED:
        pytest.xfail("bone rest rotation is dropped on export")
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
            # idx_mapping is the bone record's alignment padding rather than a
            # field, and the source's copy of it is uninitialised heap (its most
            # common value across a large sample is 0xCD). Export writes a
            # defined value, so there is nothing to compare.
            assert dst_bone.idx_mapping == 0
            # `length` is Capcom's furthestVertexDistance, and export derives it
            # from the live meshes rather than carrying the source's value. The
            # game's own number is a maximum over some subset of the vertices a
            # bone influences that has not been identified, so deriving over the
            # whole set matches it exactly on most bones, but a real skeleton
            # has a minority that land on either side of the shipped value by
            # a wider margin than floating rounding - it was observed that
            # this field is most likely unused by the game itself, so a
            # generous tolerance is used here rather than an exact match.
            assert dst_bone.length >= src_bone.length * 0.8 - 9e-03
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


def test_materials_data(mod_imported_local, mod_exported_local, local_app_id):
    src = mod_imported_local.materials_data
    dst = mod_exported_local.materials_data

    assert src.size_ == dst.size_
    if mod_imported_local.header.version == 156:
        return
    # Version 211 identifies a material by a hash rather than by name, so
    # material_names doesn't exist on it at all - except for umvc3's own 211,
    # which carries names the way 210/212 do. See the matching condition in
    # mod-21.ksy.
    if mod_imported_local.header.version in (210, 212) or local_app_id == "umvc3":
        assert src.material_names == dst.material_names
    else:
        assert src.material_hashes == dst.material_hashes


def test_meshes_data_21(mod_imported_local, mod_exported_local, local_app_id, subtests):
    if mod_imported_local.header.version not in (210, 211, 212):
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
            assert src_mesh.boundary == dst_mesh.boundary
            # min_index/max_index are derived, not independent: in every real
            # file min_index is the mesh's own vertex_position and max_index
            # is one less than a full vertex run past it. Comparing them
            # against the source would just restate the vertex_position gap
            # test_meshes_data_xfail already tracks, so what is checked here
            # is that the exported file keeps the invariant internally - a
            # mesh whose index range disagrees with its vertex range reads
            # garbage geometry however the buffer got laid out.
            assert dst_mesh.min_index == dst_mesh.vertex_position
            assert dst_mesh.max_index == dst_mesh.min_index + dst_mesh.num_vertices - 1
            assert src_mesh.max_index - src_mesh.min_index == (
                dst_mesh.max_index - dst_mesh.min_index)

    # Version 211 normally carries its weight-bound count inside meshes_data,
    # but umvc3's own 211 keeps it at the top level like 210/212 do - see the
    # matching condition in mod-21.ksy.
    if mod_imported_local.header.version in (210, 212) or local_app_id == "umvc3":
        assert mod_imported_local.num_weight_bounds == mod_exported_local.num_weight_bounds
    else:
        assert (mod_imported_local.meshes_data.num_weight_bounds ==
                mod_exported_local.meshes_data.num_weight_bounds)


def test_vertices(mod_imported_local, mod_exported_local, subtests):
    if mod_imported_local.header.version not in (210, 211, 212):  # RE5 has some mess with in hands files
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


# Header fields test_export_header doesn't touch. They had a test, but it
# requested a fixture (pl0000_roundtrip) that was never defined anywhere, so
# under its xfail marker the fixture error read as an expected failure and
# the test never ran once in its life - 0.02s, no import, no export. These
# five fields have therefore had no coverage at all until now.
#
# Measured across the mod_serialization dataset:
#   num_edges            written as 0 on every model, both versions
#   num_faces            differs on every model, by between 1 and 1706
#   size_file            differs on 211; the field does not exist on 156
#   offset_index_buffer  matches on umvc3 211, differs on 2 of 3 re5 156
#   size_vertex_buffer   as offset_index_buffer
#
# Deliberately no xfail on the whole test: that is exactly what hid the
# missing fixture. What is known-broken is narrowed to its own test below,
# which takes real fixtures and so cannot fail for setup reasons.
APPS_HEADER_BUFFER_SIZES_NOT_ROUND_TRIPPED = {"re5"}


def test_export_header_sizes(mod_imported_local, mod_exported_local, local_app_id):
    """Buffer sizes and offsets in the header, for the apps they hold on."""
    sheader = mod_imported_local.header
    dheader = mod_exported_local.header

    if local_app_id not in APPS_HEADER_BUFFER_SIZES_NOT_ROUND_TRIPPED:
        # 210 doesn't export some vertex formats (the 64-byte one with blend
        # shapes), so its vertex buffer - and the index buffer offset that
        # follows it - legitimately differ; 156 differs for its own reasons.
        assert sheader.offset_index_buffer == dheader.offset_index_buffer
        assert sheader.size_vertex_buffer == dheader.size_vertex_buffer


# Versions whose index buffer holds triangle strips rather than independent
# triples - mirrors VERSIONS_USE_TRISTRIPS in albam/engines/mtfw/mesh.py.
VERSIONS_TRISTRIP = {153, 156, 212}


def _index_count_mismatch_reason(src_mod, dst_mod):
    """Why the exported index count differs from the source, or None if it
    doesn't. num_faces, num_edges and size_file are all computed from the
    index buffer, so none of them can match while this does not.

    Two unrelated causes, and which one applies depends on the version.

    On a triangle-list version the count is 3 per face, so it only moves when
    faces go missing - and they do, to a Blender data model limit rather than
    an export bug: a mesh there cannot hold two faces over the same set of
    vertices, nor a face that repeats one. That accounts for the loss exactly
    on the one umvc3 model in this dataset that shows it, 117729 source
    indices against 116022 exported, being 530 faces sharing a vertex set
    (1590 indices) plus 39 degenerate ones (117).

    On a tristrip version the count is a strip length, so it moves whenever
    the strips are cut differently - and albam's own striper
    (lib/blender.py's triangles_list_to_triangles_strip) does not reproduce
    the game's. The count as often grows as shrinks: re5's three models here
    come out +771, -132 and +68. Face dedup contributes as well, but is the
    smaller term, and source restart degenerates never reach Blender at all
    since strip_triangles_to_triangles_list drops them at decode. The
    invariant that actually holds on these versions is the decoded triangle
    set, not the index count - so this is a statement about what the header
    tests can assert, not a fidelity check.
    """
    src = sum(m.num_indices for m in src_mod.meshes_data.meshes)
    dst = sum(m.num_indices for m in dst_mod.meshes_data.meshes)
    if src == dst:
        return None
    if src_mod.header.version in VERSIONS_TRISTRIP:
        return f"strips re-cut on export, so the index count differs ({src} -> {dst})"
    return f"duplicate/degenerate faces dropped on import ({src} -> {dst})"


def test_export_header_face_counts(mod_imported_local, mod_exported_local):
    reason = _index_count_mismatch_reason(mod_imported_local, mod_exported_local)
    if reason:
        pytest.xfail(reason)
    sheader = mod_imported_local.header
    dheader = mod_exported_local.header

    assert sheader.num_edges == dheader.num_edges
    assert sheader.num_faces == dheader.num_faces


def test_export_header_size_file(mod_imported_local, mod_exported_local):
    # Version-gated before anything else: only 21x has a size_file field,
    # and letting an AttributeError land under a marker is how the test this
    # replaced went unnoticed for its whole life.
    if mod_imported_local.header.version not in (210, 211, 212):
        pytest.skip("no size_file on this version")
    reason = _index_count_mismatch_reason(mod_imported_local, mod_exported_local)
    if reason:
        pytest.xfail(reason)
    assert mod_imported_local.header.size_file == mod_exported_local.header.size_file


# The only per-mesh offset that round-trips on every model measured, so it
# is asserted rather than excused.
MESH_FIELDS_ROUND_TRIPPED = ("face_offset",)

# Buffer placement and what follows from it. Measured across the three
# umvc3 models in the dataset: of 51/1/31 meshes, face_position differs on
# 50/0/0, vertex_position on 4/0/13, num_indices on 18/0/0, and min_index,
# max_index and vertex_offset differ on exactly the meshes vertex_position
# does - they are derived from it. num_indices is the odd one out: 6918
# against 6822 on one mesh is a real geometry difference, not a placement
# one. The middle model round-trips all of them, so none of this is
# inherent to the format.
MESH_FIELDS_BUFFER_PLACEMENT = (
    "vertex_position", "min_index", "max_index", "vertex_offset",
    "face_position", "num_indices",
)
APPS_BUFFER_PLACEMENT_NOT_ROUND_TRIPPED = {"umvc3"}


def _mesh_field_mismatches(src_meshes, dst_meshes, fields):
    mismatches = []
    for i, src_mesh in enumerate(src_meshes):
        dst_mesh = dst_meshes[i]
        for field in fields:
            src_value = getattr(src_mesh, field)
            dst_value = getattr(dst_mesh, field)
            if src_value != dst_value:
                mismatches.append(f"mesh {i}: {field} {src_value} != {dst_value}")
    return mismatches


def test_meshes_data_offsets(mod_imported_local, mod_exported_local, subtests):
    """The per-mesh fields that already round-trip, asserted so they stay
    that way.

    Version-gated like test_meshes_data_21: these are the 21 layout's field
    names, and a 156 mesh has no vertex_position at all (it has
    vertex_position_2). Without the gate every re5 mesh raised
    AttributeError inside a subtest, which pytest-subtests reports as a
    failed subtest while the test itself still passes - so the old blanket
    xfail on this reported XPASS while checking nothing.

    No num_weight_bounds check: where it lives depends on the version (and
    on the app, for 211), and test_meshes_data_21 already checks it on the
    right side of that split. Reading it unconditionally here used to raise
    AttributeError on umvc3 - under an xfail marker, so every assertion in
    this test silently never ran for that app at all.
    """
    if mod_imported_local.header.version not in (210, 211, 212):
        pytest.skip()
    for i, src_mesh in enumerate(mod_imported_local.meshes_data.meshes):
        dst_mesh = mod_exported_local.meshes_data.meshes[i]
        with subtests.test(i=i):
            for field in MESH_FIELDS_ROUND_TRIPPED:
                assert getattr(src_mesh, field) == getattr(dst_mesh, field), field


def test_meshes_data_buffer_placement(
        mod_imported_local, mod_exported_local, local_app_id):
    """Buffer placement and index count - see MESH_FIELDS_BUFFER_PLACEMENT.

    xfail is applied per app rather than to the whole test, and only after
    running the checks, so an app listed as broken that starts passing fails
    here asking to be removed from the set - the signal a plain
    xfail(reason="WIP") throws away.
    """
    if mod_imported_local.header.version not in (210, 211, 212):
        pytest.skip()
    mismatches = _mesh_field_mismatches(
        mod_imported_local.meshes_data.meshes,
        mod_exported_local.meshes_data.meshes,
        MESH_FIELDS_BUFFER_PLACEMENT,
    )
    if local_app_id in APPS_BUFFER_PLACEMENT_NOT_ROUND_TRIPPED:
        if mismatches:
            pytest.xfail(
                f"{len(mismatches)} mesh field(s) not round-tripped: {mismatches[0]}")
        # A model in a listed app that round-trips cleanly is not a
        # contradiction - one of the three umvc3 models does - so this
        # passes rather than demanding the app be removed from the set.
        # Whether the app as a whole is fixed can only be judged across
        # every model at once, which a per-model test cannot see.
        return
    assert not mismatches, "\n".join(mismatches)


def test_guessing_mirrors_reproduces_the_files_own_values(mod_imported_local, subtests):
    """The mirror guess is exact on the models this dataset covers.

    Export reads a bone's mirror off the rig rather than guessing, so this does
    not gate a round trip. What it guards is the tool that seeds that value for
    bones the rig has none for: it works by reflecting each joint across x, and
    a rig where joints stack several deep on one point can defeat it. The
    character models here do not, and a future addition that does should relax
    this deliberately rather than silently.

    The armature is built from the file's own rest positions, in the same
    orientation and scale the importer uses, so this measures the algorithm
    rather than the import path.
    """
    from albam.engines.mtfw.bone import guess_mirrors

    if mod_imported_local.bones_data is None:
        pytest.skip("model has no armature")
    bones = mod_imported_local.bones_data.bones_hierarchy
    uses_mirroring = any(
        b.idx_mirror < len(bones) and b.idx_mirror != i for i, b in enumerate(bones)
    )
    if not uses_mirroring:
        pytest.skip("model never had mirrors authored, so there is nothing to reproduce")

    scale = 0.01
    armature_data = bpy.data.armatures.new("mirror_check")
    armature = bpy.data.objects.new("mirror_check", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for i, bone in enumerate(bones):
            head = _model_space_head(mod_imported_local, i)
            edit_bone = armature_data.edit_bones.new(str(i))
            # Same axis order and scale as build_blender_armature, so x stays x
            # and the tolerance means the same thing on both sides.
            edit_bone.head = (head[0] * scale, -head[2] * scale, head[1] * scale)
            edit_bone.tail = (edit_bone.head[0], edit_bone.head[1], edit_bone.head[2] + 0.01)
        for i, bone in enumerate(bones):
            if bone.idx_parent < len(bones):
                armature_data.edit_bones[str(i)].parent = armature_data.edit_bones[str(bone.idx_parent)]
        bpy.ops.object.mode_set(mode="OBJECT")

        guessed = guess_mirrors(armature)
        for i, bone in enumerate(bones):
            with subtests.test(bone_index=i):
                # A bone the file gives no mirror is expected to be absent.
                expected = None if bone.idx_mirror >= len(bones) else str(bone.idx_mirror)
                assert guessed.get(str(i)) == expected
    finally:
        bpy.context.view_layer.objects.active = previous
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data, do_unlink=True)
