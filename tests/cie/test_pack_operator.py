"""bpy.ops.albam.pack, driven end to end for RE4UHD.

Never exercised by the suite before: ALBAM_OT_Pack's own _execute is marked
`# pragma: no cover` (see albam/blender_ui/export_panel.py), which is where a
defect was found by review rather than by any test. A script exists that
drives the same chain against a whole archive (tests/tools/cie_build_mod.py),
but it needs a real game install and is not part of CI.
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
DATASET_PATH = os.path.join(DATASETS_DIR, "bin_serialization_hashes.json")
with open(DATASET_PATH) as f:
    PACK_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in PACK_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in PACK_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


@pytest.fixture
def _clean_scene():
    before = fs_registry.keys()
    before_roots = vfs_root_names()
    # Not every test in this session cleans up after itself here: some drive
    # bpy.ops.albam.import_vfile() directly and leave stale entries in
    # "exportable" behind (see test_bin_serialization.py). Starting from a
    # clean list is what lets this test assert on its own import by count
    # rather than by some fragile "last added" bookkeeping.
    bpy.context.scene.albam.exportable.file_list.clear()
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    remove_new_vfs_roots(before_roots)
    bpy.context.scene.albam.exported.file_list.clear()
    bpy.context.scene.albam.exportable.file_list.clear()
    close_new_fs_roots(before)


def _exported_root_names():
    return {vf.name for vf in bpy.context.scene.albam.exported.file_list if vf.is_root}


def test_pack_operator_repacks_a_udas_archive(game_root, local_app_id,
                                              local_archive_path_hash, _clean_scene, tmp_path):
    """The whole chain bpy.ops.albam.pack drives: import a model through the
    real import operator (so it lands in the "exportable" list the way a user
    driving the UI would produce it), export it, then repack the archive it
    came from - and the resulting file mounts with the exported bytes in
    place of the original entry.
    """
    from albam.engines.cie.mesh import AUTO_TPL

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)

    models = [vf for vf in vfs.file_list
              if vf.tree_node.root_id == root.name and not vf.is_root and
              vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]
    assert models, "this archive should hold a mesh .bin"
    vfile = models[0]

    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    assert bpy.ops.albam.import_vfile() == {"FINISHED"}

    exportable = bpy.context.scene.albam.exportable
    assert len(exportable.file_list) == 1, "the import should have made one object exportable"
    exportable.file_list_selected_index = 0

    exported_roots_before = _exported_root_names()
    assert bpy.ops.albam.export() == {"FINISHED"}
    new_root_name = next(iter(_exported_root_names() - exported_roots_before))

    exported = bpy.context.scene.albam.exported
    exported_vfile = exported.select_vfile(local_app_id, vfile.display_name)
    assert exported_vfile, "the exported file should be findable in the export VFS"
    exported_bytes = exported_vfile.get_bytes()
    # ALBAM_OT_Pack.poll needs the export *root* selected, not the file
    # select_vfile just left selected.
    exported.file_list_selected_index = exported.file_list.find(new_root_name)

    # ALBAM_OT_Pack.poll requires the *archive* root selected on the import
    # side, not the .bin file that was picked to start the import above.
    vfs.file_list_selected_index = vfs.file_list.find(root.name)
    assert bpy.ops.albam.pack.poll(), (
        "pack should be available: an archive is selected on the import side "
        "and a root is selected on the export side"
    )

    # Same basename as the source archive: LfsFS numbers a container's
    # entries after the mounted file's own stem (see albam.engines.cie.fs),
    # so a differently-named output would compare against differently-named
    # entries below for no reason connected to the rebuild itself.
    out_path = tmp_path / os.path.basename(archive_path)
    result = bpy.ops.albam.pack(filepath=str(out_path))
    assert result == {"FINISHED"}
    assert out_path.exists() and out_path.stat().st_size > 0

    from albam.engines.cie.fs import LfsFS

    original = LfsFS(archive_path)
    try:
        before = {p.lstrip("/"): original.readbytes(p) for p in original.walk.files()}
    finally:
        original.close()

    repacked = LfsFS(str(out_path))
    try:
        after = {p.lstrip("/"): repacked.readbytes(p) for p in repacked.walk.files()}
    finally:
        repacked.close()

    assert after.keys() == before.keys(), "repacking should not add or drop entries"
    assert after[vfile.display_name] == exported_bytes, (
        "the repacked archive should hold the freshly exported bytes for this entry"
    )
    unchanged = {k: v for k, v in before.items() if k != vfile.display_name}
    assert {k: after[k] for k in unchanged} == unchanged, (
        "every other entry should have survived the rebuild untouched"
    )
