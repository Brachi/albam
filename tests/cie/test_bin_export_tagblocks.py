"""RE4UHD morphs, bone pairs and the symmetry table round-trip through export.

Regression coverage for issue #266: all three blocks used to be read on
import and dropped on export - offsets left at 0, flags cleared, the model
losing them entirely. See albam/engines/cie/mesh.py (_serialize_morphs,
_serialize_bone_pairs, _serialize_symmetry) and structs/re4-uhd-bin.ksy.
"""
import json
import os

import bpy
import mathutils
import pytest

from albam.lib import fs_registry
from tests.conftest import close_new_fs_roots, remove_new_vfs_roots, vfs_root_names
from tests.cie.lfs_paths import resolve_archive_hashes
from tests.cie.test_bin_serialization import _is_mesh_bin

# Committed, hash-only, catalog-verified archives (see
# test_dataset_hashes_are_in_catalog), same pattern as the other cie
# datasets. Every entry has to carry both a DBL_JNT and a pXFlip table,
# which is what the two round-trip tests below mount it for.
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "bin_export_tagblocks_hashes.json")
with open(DATASET_PATH) as f:
    TAGBLOCKS_DATASET = json.load(f)

BIN_FLAG_BONEPAIRS = 0x00000100
BIN_FLAG_ADJACENCY = 0x00000200


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in TAGBLOCKS_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in TAGBLOCKS_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - see
    tests/cie/test_lfs_fs.py, same check. CI-safe."""
    for entry in TAGBLOCKS_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        assert entry["archive_path_hash"] in catalog, (
            f"{entry['archive_path_hash']!r} is not in {catalog_path!r}"
        )


@pytest.fixture
def _clean_scene():
    before = fs_registry.keys()
    before_roots = vfs_root_names()
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    remove_new_vfs_roots(before_roots)
    bpy.context.scene.albam.exported.file_list.clear()
    close_new_fs_roots(before)


def _import_first_model_carrying(game_root, local_app_id, archive_hash, block_attr):
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(game_root, {archive_hash})[archive_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)

    candidates = [vf for vf in vfs.file_list
                  if vf.tree_node.root_id == root.name and not vf.is_root and
                  vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]

    vfile = None
    original_bytes = None
    parsed = None
    for candidate in candidates:
        data = candidate.get_bytes()
        p = Re4UhdBin.from_bytes(data)
        p._read()
        if getattr(p, block_attr):
            vfile, original_bytes, parsed = candidate, data, p
            break
    assert vfile is not None, f"no model in this archive carries {block_attr!r}"

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    bl_object = import_function(vfile, bpy.context)

    bl_object.albam_asset.app_id = local_app_id
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = vfile.display_name
    bl_object.albam_asset.original_bytes = original_bytes
    return bl_object, parsed


def _mesh_child(bl_object):
    if bl_object.type == "MESH":
        return bl_object
    return next(child for child in bl_object.children_recursive if child.type == "MESH")


def test_morphs_are_written_from_shape_keys(game_root, local_app_id, local_archive_path_hash,
                                            _clean_scene):
    """Shape keys come back out as a morph block, framed the way the
    measurements recorded in the .ksy comments on morph_group and
    morph_group_body settled the format question issue #266 raised, with
    every delta decoding to the movement Blender held.

    The morphs are added here rather than imported from a morph-carrying
    game model: none of the archives the committed datasets name carries
    one, and export is the half #266 reports missing either way - the
    framing needed no import fix, so this exercises only the writer.
    """
    from albam.registry import blender_registry
    from albam.engines.cie.mesh import _yz_flip
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    bl_object, _parsed = _import_first_model_carrying(
        game_root, local_app_id, local_archive_path_hash, "bone_pairs")
    bl_mesh_ob = _mesh_child(bl_object)
    assert bl_mesh_ob.data.shape_keys is None, "this model is expected to carry no morphs"

    # Two moved vertices with distinct deltas, so the entries can be checked
    # against what moved rather than only against each other, and a key that
    # moves nothing after them.
    moved = {0: (0.01, 0.02, -0.03), 1: (-0.05, 0.008, 0.04)}
    bl_mesh_ob.shape_key_add(name="Basis", from_mix=False)
    shape_key = bl_mesh_ob.shape_key_add(name="000", from_mix=False)
    for vertex_index, (dx, dy, dz) in moved.items():
        shape_key.data[vertex_index].co.x += dx
        shape_key.data[vertex_index].co.y += dy
        shape_key.data[vertex_index].co.z += dz
    bl_mesh_ob.shape_key_add(name="001", from_mix=False)

    export_function = blender_registry.export_registry[(local_app_id, "bin")]
    vfiles = export_function(bl_object)
    reparsed = Re4UhdBin.from_bytes(vfiles[0].data_bytes)
    reparsed._read()

    assert reparsed.morphs is not None
    assert reparsed.header.offset_morphs > 0
    groups = reparsed.morphs.morph_groups
    assert reparsed.morphs.num_morph_groups == len(groups) == 2
    # The game addresses a morph by its group index, so a key that moves
    # nothing is still written - dropping it would renumber the keys after it.
    assert groups[1].count == 0
    assert groups[1].body.vertices == []
    assert groups[0].count == len(groups[0].body.vertices) > 0

    # Every entry addresses a corner of this model and decodes back to one of
    # the two movements applied above - the deltas are written per corner, and
    # a corner belongs to exactly one vertex (see _collect_geometry).
    extra_scale = 2 ** reparsed.header.vertex_scale
    world = bl_mesh_ob.matrix_world.to_3x3()
    expected = {tuple(round(c, 3) for c in (world @ mathutils.Vector(delta)))
                for delta in moved.values()}
    decoded = set()
    for vertex in groups[0].body.vertices:
        assert 0 <= vertex.id < reparsed.header.num_vertices
        position = _yz_flip(vertex.position.x, vertex.position.y, vertex.position.z)
        decoded.add(tuple(round(c / extra_scale, 3) for c in position))
    assert decoded == expected

    # The morph block is num_morph_groups (u4), the group table, then the
    # bodies - and nothing else may be laid out inside that span, or the
    # block that follows overwrites a morph the game is about to read.
    header = reparsed.header
    morph_body_size = 8 * sum(g.count for g in groups)
    morph_end = header.offset_morphs + 4 + 8 * len(groups) + morph_body_size
    following = [offset for offset in (
        header.offset_bones, header.offset_weights, header.offset_bonepairs,
        header.offset_adjacents, header.offset_vertex_position,
        header.offset_vertex_normals, header.offset_index_buffer,
        header.offset_index_buffer2, header.offset_vertex_colors,
        header.offset_vertex_texcoord, header.offset_materials)
        if offset > header.offset_morphs]
    assert morph_end <= min(following), (morph_end, min(following))


def test_bone_pairs_round_trip_through_export(game_root, local_app_id, local_archive_path_hash,
                                              _clean_scene):
    """The DBL_JNT block survives an unedited round trip for every line whose
    bones are still present - see the .ksy comment on pair_line."""
    from albam.registry import blender_registry
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    bl_object, parsed = _import_first_model_carrying(
        game_root, local_app_id, local_archive_path_hash, "bone_pairs")

    export_function = blender_registry.export_registry[(local_app_id, "bin")]
    vfiles = export_function(bl_object)
    reparsed = Re4UhdBin.from_bytes(vfiles[0].data_bytes)
    reparsed._read()

    assert reparsed.bone_pairs is not None
    assert reparsed.header.offset_bonepairs > 0
    assert reparsed.header.flags & BIN_FLAG_BONEPAIRS

    original = {(line.helper_bone_id, line.bone_a_id, line.bone_b_id, line.percent)
                for line in parsed.bone_pairs.line}
    exported = {(line.helper_bone_id, line.bone_a_id, line.bone_b_id, line.percent)
                for line in reparsed.bone_pairs.line}
    # Every line whose three bones the model's own table already had must
    # survive; a line naming a bone that table never carried to begin with
    # (a known RE4UHD partial-table quirk) has nothing in Blender to write
    # back and is dropped with a warning instead.
    own_ids = {bone.bone_id for bone in parsed.bones}
    kept_originals = {line for line in original if all(b in own_ids for b in line[:3])}
    assert kept_originals <= exported


def test_symmetry_round_trips_through_export(game_root, local_app_id, local_archive_path_hash,
                                             _clean_scene):
    """The pXFlip mirror table survives an unedited round trip, decoded
    big-endian as the .ksy comment on symmetry records, for every bone still
    written."""
    from albam.registry import blender_registry
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    bl_object, parsed = _import_first_model_carrying(
        game_root, local_app_id, local_archive_path_hash, "symmetry_table")

    export_function = blender_registry.export_registry[(local_app_id, "bin")]
    vfiles = export_function(bl_object)
    reparsed = Re4UhdBin.from_bytes(vfiles[0].data_bytes)
    reparsed._read()

    assert reparsed.symmetry_table is not None
    assert reparsed.header.offset_adjacents > 0
    assert reparsed.header.flags & BIN_FLAG_ADJACENCY
    assert reparsed.symmetry_table.num_bones == len(reparsed.bones)

    original = dict(zip((b.bone_id for b in parsed.bones), parsed.symmetry_table.mirror_bone_ids))
    exported = dict(zip((b.bone_id for b in reparsed.bones),
                        reparsed.symmetry_table.mirror_bone_ids))
    kept_ids = set(exported)
    for bone_id, mirror_id in original.items():
        if bone_id not in kept_ids:
            continue
        expected = mirror_id if mirror_id in kept_ids else -1
        assert exported[bone_id] == expected, (bone_id, mirror_id, exported[bone_id])
