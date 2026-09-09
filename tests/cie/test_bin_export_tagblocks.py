"""RE4UHD morphs, bone pairs and the symmetry table round-trip through export.

Regression coverage for issue #266: all three blocks used to be read on
import and dropped on export - offsets left at 0, flags cleared, the model
losing them entirely. See albam/engines/cie/mesh.py (_serialize_morphs,
_serialize_bone_pairs, _serialize_symmetry) and structs/re4-uhd-bin.ksy.
"""
import json
import os

import bpy
import pytest

from albam.lib import fs_registry
from tests.conftest import close_new_fs_roots, remove_new_vfs_roots, vfs_root_names
from tests.cie.lfs_paths import resolve_archive_hashes
from tests.cie.test_bin_serialization import _is_mesh_bin

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


def test_morphs_round_trip_through_export(game_root, local_app_id, local_archive_path_hash,
                                          _clean_scene):
    """A morph-carrying model keeps a morph block after export, and every
    entry id it writes is a valid corner index - the format question issue
    #266 raised (see report.md item 1: the framing needed no import fix,
    so this exercises only the writer)."""
    entry = next(d for d in TAGBLOCKS_DATASET if d["archive_path_hash"] == local_archive_path_hash)
    if "morphs" not in entry["carries"]:
        pytest.skip("this archive carries no morphs")

    from albam.registry import blender_registry
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    bl_object, parsed = _import_first_model_carrying(
        game_root, local_app_id, local_archive_path_hash, "morphs")
    bl_mesh_ob = bl_object if bl_object.type == "MESH" else next(
        child for child in bl_object.children_recursive if child.type == "MESH")
    assert bl_mesh_ob.data.shape_keys is not None
    assert len(bl_mesh_ob.data.shape_keys.key_blocks) > 1, "Basis plus at least one morph"

    export_function = blender_registry.export_registry[(local_app_id, "bin")]
    vfiles = export_function(bl_object)
    reparsed = Re4UhdBin.from_bytes(vfiles[0].data_bytes)
    reparsed._read()

    assert reparsed.morphs is not None
    assert reparsed.header.offset_morphs > 0
    assert reparsed.morphs.num_morph_groups == len(reparsed.morphs.morph_groups)
    for group in reparsed.morphs.morph_groups:
        assert group.count == len(group.body.vertices)
        for vertex in group.body.vertices:
            assert 0 <= vertex.id < reparsed.header.num_vertices


def test_bone_pairs_round_trip_through_export(game_root, local_app_id, local_archive_path_hash,
                                              _clean_scene):
    """The DBL_JNT block survives an unedited round trip for every line whose
    bones are still present (see report.md item 3)."""
    entry = next(d for d in TAGBLOCKS_DATASET if d["archive_path_hash"] == local_archive_path_hash)
    if "bone_pairs" not in entry["carries"]:
        pytest.skip("this archive carries no bone pairs")

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

    original = {(l.helper_bone_id, l.bone_a_id, l.bone_b_id, l.percent)
                for l in parsed.bone_pairs.line}
    exported = {(l.helper_bone_id, l.bone_a_id, l.bone_b_id, l.percent)
                for l in reparsed.bone_pairs.line}
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
    big-endian as report.md item 4 established, for every bone still
    written."""
    entry = next(d for d in TAGBLOCKS_DATASET if d["archive_path_hash"] == local_archive_path_hash)
    if "symmetry" not in entry["carries"]:
        pytest.skip("this archive carries no symmetry table")

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
