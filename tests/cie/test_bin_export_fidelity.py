"""What a RE4 UHD model must not lose when it is exported unedited.

tests/cie/test_bin_serialization.py round-trips a model imported under the
best conditions: its textures resolve, and it is the model that brought its
armature into the scene. These are the two cases either side of that, both
of which quietly wrote a worse file than the one that came in:

- a model whose textures could not be found still carries its materials'
  texture references, so they have to survive an export that has no image
  nodes to read them off;
- a model bound to an armature it shares with the rest of its archive has to
  export its own bone table, not the whole shared rig's.
"""
import json
import os
import shutil

import bpy
import pytest

from albam.lib import fs_registry
from tests.cie.lfs_paths import resolve_archive_hashes
from tests.cie.test_bin_serialization import _is_mesh_bin, _texture_slots

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "bin_export_fidelity_hashes.json")
with open(DATASET_PATH) as f:
    EXPORT_FIDELITY_DATASET = json.load(f)

NO_TEXTURE = 0xFF
NO_PARENT = 0xFF


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in EXPORT_FIDELITY_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in EXPORT_FIDELITY_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - see
    tests/cie/test_lfs_fs.py, same check. CI-safe."""
    for entry in EXPORT_FIDELITY_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        assert entry["archive_path_hash"] in catalog, (
            f"{entry['archive_path_hash']!r} is not in {catalog_path!r}"
        )


@pytest.fixture
def _clean_scene():
    # vfs, exported and bpy.data are session-scoped state: register() runs
    # once per pytest session, so a test that leaves objects or roots behind
    # changes what the next one sees.
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    bpy.context.scene.albam.vfs.file_list.clear()
    bpy.context.scene.albam.exported.file_list.clear()
    fs_registry.clear()


@pytest.fixture
def _forget_texture_packs():
    """A session with no texture pack found yet.

    Packs and the directories they were found in are remembered for the whole
    Blender session (see albam/engines/cie/textures.py), so a pack an earlier
    test resolved would keep resolving here and the archive being somewhere
    unhelpful would prove nothing.
    """
    from albam.engines.cie import textures

    packs = dict(textures._PACK_CACHE)
    directories = list(textures._PACK_DIRECTORIES)
    textures._PACK_CACHE.clear()
    textures._PACK_DIRECTORIES.clear()
    yield
    textures._PACK_CACHE.clear()
    textures._PACK_CACHE.update(packs)
    textures._PACK_DIRECTORIES[:] = directories


def _mesh_models(vfs, root):
    return [vf for vf in vfs.file_list
            if vf.tree_node.root_id == root.name and not vf.is_root and
            vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]


def _export(bl_object, vfile, original_bytes, app_id):
    from albam.registry import blender_registry

    bl_object.albam_asset.app_id = app_id
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = vfile.display_name
    bl_object.albam_asset.original_bytes = original_bytes
    vfiles = blender_registry.export_registry[(app_id, "bin")](bl_object)
    assert len(vfiles) == 1
    return vfiles[0].data_bytes


def _image_nodes(bl_object):
    """Every texture node of the model's materials that holds an image."""
    meshes = [o for o in bl_object.children_recursive if o.type == "MESH"]
    if bl_object.type == "MESH":
        meshes.append(bl_object)
    return [node
            for o in meshes for slot in o.material_slots if slot.material
            for node in slot.material.node_tree.nodes
            if getattr(node, "image", None) is not None]


def test_texture_slots_survive_textures_not_resolving(
        game_root, local_app_id, local_archive_path_hash, tmp_path,
        _forget_texture_packs, _clean_scene):
    """Exporting a model whose textures were not found keeps its texture
    references.

    A model's textures live in a separate archive found beside its own, so an
    archive opened on its own - the normal case for someone working on a mod
    - imports untextured. Its materials still name their textures, and an
    export that reads only the image nodes it has in front of it used to
    write "no texture" over every one of them.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]
    # Away from the install, where nothing can find the texture packs. Named
    # after the test rather than copied under its own name: nothing about the
    # archive's own name is what makes this work.
    isolated = str(tmp_path / "unresolvable.udas.lfs")
    shutil.copyfile(archive_path, isolated)

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, isolated)
    models = _mesh_models(vfs, root)
    assert models, "this archive should hold a mesh .bin"

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL

    vfile = next((vf for vf in models
                  if any(slot != NO_TEXTURE
                         for slots in _texture_slots(vf.get_bytes()) for slot in slots[:5])),
                 None)
    if vfile is None:
        pytest.skip("no model in this archive references a texture")

    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    original_bytes = vfile.get_bytes()
    bl_object = import_function(vfile, bpy.context)

    assert not _image_nodes(bl_object), (
        "this test is about textures that could not be found, and these were")

    exported_bytes = _export(bl_object, vfile, original_bytes, local_app_id)
    assert _texture_slots(exported_bytes) == _texture_slots(original_bytes)


def test_texture_slot_follows_the_image_bound_to_it(
        game_root, local_app_id, local_archive_path_hash, _clean_scene):
    """Swapping a texture in Blender is still what gets written.

    The fallback above must not turn the stored index into the answer: an
    image actually bound to a material input outranks it, which is what makes
    changing a texture in Blender an edit an export can see.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)
    models = _mesh_models(vfs, root)
    assert models, "this archive should hold a mesh .bin"

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL

    swapped = None
    for vfile in models:
        vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
        original_bytes = vfile.get_bytes()
        bl_object = import_function(vfile, bpy.context)
        nodes = _image_nodes(bl_object)
        if nodes:
            swapped = (vfile, original_bytes, bl_object, nodes[0])
            break
    if swapped is None:
        pytest.skip("no model in this archive imported with textures")

    vfile, original_bytes, bl_object, node = swapped
    unedited = _texture_slots(_export(bl_object, vfile, original_bytes, local_app_id))
    written = {slot for slots in unedited for slot in slots[:5]}
    unused = next(i for i in range(NO_TEXTURE) if i not in written)

    # A new image rather than a different index on the imported one: images
    # are keyed by name in bpy.data and outlive the scene, so editing one
    # here would follow every later test in the session.
    replacement = bpy.data.images.new("albam-test-texture-swap", 4, 4)
    custom_properties = replacement.albam_custom_properties.get_custom_properties_for_appid(
        local_app_id)
    custom_properties.tpl_index = unused
    original_image = node.image
    try:
        node.image = replacement
        edited = _texture_slots(_export(bl_object, vfile, original_bytes, local_app_id))
    finally:
        node.image = original_image
        bpy.data.images.remove(replacement)

    assert edited != unedited, "binding another image should change the file"
    assert any(unused in slots[:5] for slots in edited), (
        "the slot the newly bound image names should be the one written")


def _bone_table(bin_bytes):
    """(bone ids in the order they are written, ids the weights name)."""
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()
    ids = [bone.bone_id for bone in parsed.bones]
    weighted = set()
    if ids:
        for weight in parsed.weights:
            weighted.update(weight.bone_ids[:weight.count])
    return ids, weighted


def test_model_sharing_an_armature_exports_its_own_bones(
        game_root, local_app_id, local_archive_path_hash, _clean_scene):
    """A model bound to a shared armature writes its own bone table.

    Import binds a model to an armature already brought in from the same
    archive that covers its bones, so a character's parts share one rig. The
    export then wrote every bone of that armature, so a model that had two
    bones came out with the whole character's table - and its weights, which
    name bones by id, no longer described the same skinning.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)
    models = _mesh_models(vfs, root)
    assert models, "this archive should hold a mesh .bin"

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL

    shared = None
    for vfile in models:
        vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
        original_bytes = vfile.get_bytes()
        bl_object = import_function(vfile, bpy.context)
        armature = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
        original_ids, weighted = _bone_table(original_bytes)
        if armature and original_ids and len(original_ids) < len(armature.data.bones):
            shared = (vfile, original_bytes, bl_object, armature, original_ids, weighted)
            break
    if shared is None:
        pytest.skip("no model in this archive reuses another's armature")

    vfile, original_bytes, bl_object, armature, original_ids, weighted = shared
    exported_bytes = _export(bl_object, vfile, original_bytes, local_app_id)
    exported_ids, _ = _bone_table(exported_bytes)

    assert exported_ids, "an exported skinned model should carry a bone table"
    assert len(exported_ids) < len(armature.data.bones), (
        "the shared armature's whole bone table was written, not this model's")
    assert set(exported_ids) <= set(original_ids), (
        "no bone should be written that the model did not have")
    assert weighted <= set(exported_ids), (
        "every bone the weights name has to be in the table")
    if len(set(original_ids)) == len(original_ids):
        assert exported_ids == sorted(original_ids), (
            "an unedited model should write back the bone table it came with")
    assert exported_ids == sorted(exported_ids), "the table is written in bone id order"
    # A bone names its parent by id, so a table that dropped one would leave
    # the bones under it unable to say where they hang from.
    parents = {bone_id: parent for bone_id, parent in _bone_parents(exported_bytes)}
    for bone_id, parent in parents.items():
        assert parent == NO_PARENT or parent == bone_id or parent in parents, (
            f"bone {bone_id} names a parent that is not in the table")


def _bone_parents(bin_bytes):
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()
    return [(bone.bone_id, bone.parent) for bone in parsed.bones]
