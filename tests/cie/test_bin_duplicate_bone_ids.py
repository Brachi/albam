"""A RE4UHD bone table may name the same bone id twice.

The scene has one bone per id and no way to hold a second: the weights name
a bone by id, so do the vertex groups named after them, and so does
animation retargeting. Import used to make a second bone anyway, which
Blender uniquified to "5.001" - a bone nothing meant - and export wrote one
entry per bone, so a table of five entries came back as four. The repeats
are carried on the mesh instead, in the order the table had them (see
albam/engines/cie/mesh.py, BONE_IDS_PROPERTY).

Most of this is checked against a model built here rather than a shipped
one: no dataset a CI run can reach holds a model with a repeated id (see
tests/cie/synthetic_bin.py). The last test does check shipped models, and
needs --game-dir.
"""
import json
import os

import bpy
from mathutils import Vector
import pytest

from albam.lib import fs_registry
from tests.conftest import close_new_fs_roots, remove_new_vfs_roots, vfs_root_names
from tests.cie.lfs_paths import resolve_archive_hashes
from tests.cie.synthetic_bin import bone_table, build_mesh_bin
from tests.cie.test_bin_serialization import _is_mesh_bin

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
with open(os.path.join(DATASETS_DIR, "bin_export_fidelity_hashes.json")) as f:
    EXPORT_FIDELITY_DATASET = json.load(f)

APP_ID = "re4uhd"
NO_PARENT = 0xFF

# Bone 2 twice, with a different parent and a different offset each time -
# the two things a repeat can disagree with its twin about. Bone 3 hangs off
# it, so a table that dropped one of them would still have to name it.
BONES = [
    (0, NO_PARENT, 0.0, 0.0, 0.0),
    (1, 0, 0.0, 100.0, 0.0),
    (2, 1, 0.0, 100.0, 0.0),
    (2, 0, 50.0, 0.0, 0.0),
    (3, 2, 0.0, 100.0, 0.0),
]
# Bone 1 is in the table but nothing is weighted to it, which is what makes
# the recorded ids rather than the weights the thing the table comes from.
WEIGHTS = [((0, 0, 0), (100, 0, 0), 1), ((2, 0, 0), (100, 0, 0), 1)]
WEIGHT_INDICES = [0, 0, 1, 1]


@pytest.fixture
def _clean_scene():
    # vfs, exported and bpy.data are session-scoped state: register() runs
    # once per pytest session, so a test that leaves objects or roots behind
    # changes what the next one sees.
    before = fs_registry.keys()
    before_roots = vfs_root_names()
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    remove_new_vfs_roots(before_roots)
    bpy.context.scene.albam.exported.file_list.clear()
    close_new_fs_roots(before)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in EXPORT_FIDELITY_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in EXPORT_FIDELITY_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def _import_bin(tmp_path, bin_bytes, name="repeated_bone_id.bin"):
    """Import `bin_bytes` the way the add-on does, and return its object.

    Through a directory root rather than a mounted .lfs: the importer reads
    its bytes off a VirtualFile either way, and building an archive around
    one model would only be testing the archive.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    path = tmp_path / name
    path.write_bytes(bin_bytes)

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = APP_ID
    vfs.add_real_file(APP_ID, str(tmp_path))
    vfile = next(vf for vf in vfs.file_list if vf.display_name == name)
    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL

    bl_object = blender_registry.import_registry[(APP_ID, "bin")](vfile, bpy.context)
    bl_object.albam_asset.app_id = APP_ID
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = name
    bl_object.albam_asset.original_bytes = bin_bytes
    return bl_object


def _export(bl_object):
    from albam.registry import blender_registry

    vfiles = blender_registry.export_registry[(APP_ID, "bin")](bl_object)
    assert len(vfiles) == 1
    return vfiles[0].data_bytes


def _mesh_of(bl_object):
    return next(o for o in bl_object.children_recursive if o.type == "MESH")


def _armature_of(bl_object):
    if bl_object.type == "ARMATURE":
        return bl_object
    return _mesh_of(bl_object).modifiers["Armature"].object


def _identities(table):
    return [(bone_id, parent) for bone_id, parent, _offset in table]


def _offsets(table):
    """Every entry's offset, flattened - pytest.approx compares a flat
    sequence of numbers, not a sequence of tuples."""
    return [coordinate for _bone_id, _parent, offset in table for coordinate in offset]


def test_a_repeated_bone_id_is_written_back(tmp_path, _clean_scene):
    """Both entries come back, each with what it came in with.

    Import made one bone per table entry and export wrote one entry per bone,
    so the repeat vanished on the way out - and the entry that survived was
    written with the other one's offset, since the armature bone had taken
    its position from whichever entry came last.
    """
    original = build_mesh_bin(BONES, WEIGHTS, WEIGHT_INDICES)
    exported = _export(_import_bin(tmp_path, original))

    assert _identities(bone_table(exported)) == _identities(bone_table(original))
    assert _offsets(bone_table(exported)) == pytest.approx(_offsets(bone_table(original)))


def test_a_table_without_repeats_is_unchanged(tmp_path, _clean_scene):
    """The control: carrying the repeats must not move anything else.

    Every entry of a table with no repeat is written from the armature bone
    it stands for, exactly as before, so a model the old code round-tripped
    has to come out the same way.
    """
    bones = [entry for entry in BONES if entry[:2] != (2, 0)]
    original = build_mesh_bin(bones, WEIGHTS, WEIGHT_INDICES)
    exported = _export(_import_bin(tmp_path, original))

    assert _identities(bone_table(exported)) == _identities(bone_table(original))
    assert _offsets(bone_table(exported)) == pytest.approx(_offsets(bone_table(original)))


@pytest.mark.parametrize("swapped", [False, True])
def test_repeated_entries_keep_the_order_they_came_in(tmp_path, swapped, _clean_scene):
    """Not just the count of them.

    The table is written in bone id order, which puts two entries sharing an
    id next to each other and says nothing about which of the two comes
    first. That order is the model's, so writing the pair back the other way
    round would be as wrong as dropping one: it is what tells the two
    entries apart.
    """
    bones = list(BONES)
    if swapped:
        bones[2], bones[3] = bones[3], bones[2]
    original = build_mesh_bin(bones, WEIGHTS, WEIGHT_INDICES)
    exported = _export(_import_bin(tmp_path, original))

    repeats = [(parent, offset) for bone_id, parent, offset in bone_table(exported)
               if bone_id == 2]
    assert [parent for parent, _offset in repeats] == ([0, 1] if swapped else [1, 0])
    flattened = [coordinate for _parent, offset in repeats for coordinate in offset]
    assert flattened == pytest.approx(
        [50.0, 0.0, 0.0, 0.0, 100.0, 0.0] if swapped
        else [0.0, 100.0, 0.0, 50.0, 0.0, 0.0])


def test_the_armature_gets_one_bone_per_id(tmp_path, _clean_scene):
    """A repeat has nowhere in the scene to go.

    Blender uniquifies a name already taken, so a second bone for id 2 came
    in as "2.001" - a bone no weight, vertex group or retargeted animation
    can name, sitting in the armature looking like part of the skeleton.
    """
    bl_object = _import_bin(tmp_path, build_mesh_bin(BONES, WEIGHTS, WEIGHT_INDICES))

    names = {bone.name for bone in _armature_of(bl_object).data.bones}
    assert names == {"0", "1", "2", "3"}
    assert {group.name for group in _mesh_of(bl_object).vertex_groups} == {"0", "2"}


def test_moving_the_bone_moves_the_entry_it_stands_for(tmp_path, _clean_scene):
    """The model stays editable, and only the repeat is carried verbatim.

    The armature bone stands for the first entry, so moving it is an edit the
    export sees. The second has no bone of its own to move and goes back as
    it came in, which is the only answer that does not invent a position for
    it.
    """
    bl_object = _import_bin(tmp_path, build_mesh_bin(BONES, WEIGHTS, WEIGHT_INDICES))
    armature = _armature_of(bl_object)

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    moved = armature.data.edit_bones["2"]
    moved.head = moved.head + Vector((0.0, 0.0, 0.5))
    moved.tail = moved.tail + Vector((0.0, 0.0, 0.5))
    bpy.ops.object.mode_set(mode="OBJECT")

    repeats = [(parent, offset) for bone_id, parent, offset
               in bone_table(_export(bl_object)) if bone_id == 2]
    assert len(repeats) == 2
    assert repeats[0][0] == 1 and repeats[1][0] == 0
    # 0.5 Blender metres is 500 of the millimetres the file counts in, and
    # the file's y is Blender's z.
    assert list(repeats[0][1]) == pytest.approx([0.0, 600.0, 0.0])
    assert list(repeats[1][1]) == pytest.approx([50.0, 0.0, 0.0])


def test_a_scene_saved_before_this_still_writes_every_entry(tmp_path, _clean_scene):
    """A .blend saved by an older albam comes back with the repeat.

    Such a scene has the ids and parents its model was imported with but no
    offsets, and an armature holding the "2.001" that import used to make.
    Both entries still have to be written, and the leftover bone must not
    become a bone of its own: read as its position in the armature it stood
    for some other id entirely.
    """
    from albam.engines.cie.mesh import BONE_OFFSETS_PROPERTY

    bl_object = _import_bin(tmp_path, build_mesh_bin(BONES, WEIGHTS, WEIGHT_INDICES))
    del _mesh_of(bl_object)[BONE_OFFSETS_PROPERTY]

    armature = _armature_of(bl_object)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    twin = armature.data.edit_bones["2"]
    leftover = armature.data.edit_bones.new("2")
    leftover.head, leftover.tail, leftover.parent = twin.head, twin.tail, twin.parent
    bpy.ops.object.mode_set(mode="OBJECT")
    assert "2.001" in armature.data.bones, "this is what the older importer left behind"

    assert _identities(bone_table(_export(bl_object))) == _identities(bone_table(
        build_mesh_bin(BONES, WEIGHTS, WEIGHT_INDICES)))


def test_shipped_models_with_a_repeated_bone_id_round_trip(
        game_root, local_app_id, local_archive_path_hash, _clean_scene):
    """The same thing, against whatever the game actually ships.

    Needs --game-dir. Every mesh model of the archive is imported and
    exported unedited, and the ones whose table repeats an id have to come
    back with that table entry for entry - which is the case
    tests/tools/cie_build_mod.py refuses to put in an archive.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)
    models = [vf for vf in vfs.file_list
              if vf.tree_node.root_id == root.name and not vf.is_root and
              vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]
    assert models, "this archive should hold a mesh .bin"

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL

    # Every model, in order, not only the ones with a repeat: import binds a
    # model to an armature another already brought in, and a repeated id has
    # to survive that too.
    repeated = []
    for vfile in models:
        vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
        original_bytes = vfile.get_bytes()
        bl_object = import_function(vfile, bpy.context)
        original = bone_table(original_bytes)
        ids = [bone_id for bone_id, _parent, _offset in original]
        if len(set(ids)) == len(ids):
            continue

        bl_object.albam_asset.app_id = local_app_id
        bl_object.albam_asset.extension = "bin"
        bl_object.albam_asset.relative_path = vfile.display_name
        bl_object.albam_asset.original_bytes = original_bytes
        exported = bone_table(_export(bl_object))
        assert _identities(exported) == _identities(original), (
            f"{vfile.display_name} did not write back the bone table it came with")

        # A repeat is written back verbatim, so it matches to the bit - unlike
        # an entry read off an armature bone, whose position has been through
        # Blender's floats and back.
        counted = {}
        for (bone_id, _parent, offset), (_id, _p, written) in zip(original, exported):
            occurrence = counted.get(bone_id, 0)
            counted[bone_id] = occurrence + 1
            if occurrence:
                assert written == offset, (
                    f"{vfile.display_name} moved a repeated entry for bone {bone_id}")
        repeated.append(vfile.display_name)

    if not repeated:
        pytest.skip(f"none of this archive's {len(models)} models repeats a bone id")
