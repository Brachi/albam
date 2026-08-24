"""
Blender import correctness test for RE:ORC skeletons (see
albam.engines.hexn.skeleton.build_blender_skeleton and structs/skel.ksy).

Drives a real bpy.ops.albam.import_vfile() import (through the actual
registry/VFS/UI operator stack, not a direct function call) and asserts on
the resulting Armature: bone count, root/hierarchy shape, and rest-pose
sanity. Scope note (see the task this was built for): .edgemodel has no
export function yet, so a full import->edit->export->reimport round trip
through the mesh pipeline isn't possible - this only exercises the import
side, plus skel_roundtrip.py's separate raw byte-level format round trip.

Reuses a small quadruped creature's .edgemodel hash from
test_edgemodel_parsing.py's own dataset rather than adding a new one -
its matching skeleton file is also already in this file's own
skel_hashes.json dataset, so importing this one .edgemodel exercises the
full real path-inference chain (skeleton.py's infer_skeleton_vfile()) end
to end, not just a directly-constructed HexaneSkel.
"""
import bpy

from tests.mtfw.scripts.catalog_paths import resolve_hashes

EDGEMODEL_HASH = "f8716a4c39cf84d2"
SKEL_HASH = "d9aaf6d76616ee3c"
EXPECTED_NODE_COUNT = 88
EXPECTED_ROOT_NAMES = {"skel_root", "hips", "hips_nobind", "leftupleg"}


def pytest_generate_tests(metafunc):
    if "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", ["reorc"], scope="session")


def test_import_builds_armature_matching_skel_file(game_fs_root, local_app_id):
    from albam.engines.hexn.structs.hexane_skel import HexaneSkel

    # Independently confirm both hashes resolve under this install/dataset,
    # and that the skel file's own node_count/hierarchy match what the
    # import is expected to produce below - so this test fails loudly if
    # the *fixture* data ever drifts, not just the import code.
    paths = resolve_hashes(game_fs_root, {EDGEMODEL_HASH, SKEL_HASH})
    skel_bytes = game_fs_root.readbytes(paths[SKEL_HASH])
    skel = HexaneSkel.from_bytes(skel_bytes)
    skel._read()
    assert skel.node_count == EXPECTED_NODE_COUNT
    expected_roots = {skel.names[i] for i, node in enumerate(skel.hierarchy) if node.is_root}
    assert expected_roots == EXPECTED_ROOT_NAMES

    vfs = bpy.context.scene.albam.vfs
    # resolve_hashes()/game_fs.walk.files() return a leading-slash virtual
    # path; VirtualFileSystemBase.select_vfile() builds its lookup key via
    # PureWindowsPath(relative_path).parts, where a leading "/" becomes its
    # own bogus "\\" part - strip it first (mirrors how e.g. material.py's
    # own mesh_header.materials.first_material is already leading-slash-free).
    vfs.select_vfile(local_app_id, paths[EDGEMODEL_HASH].lstrip("/"))
    before = set(bpy.data.objects)

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    imported = [ob for ob in bpy.data.objects if ob not in before]
    armatures = [ob for ob in imported if ob.type == "ARMATURE"]
    assert len(armatures) == 1, f"expected exactly one imported Armature, got {armatures}"
    armature_ob = armatures[0]

    bones = armature_ob.data.bones
    assert len(bones) == EXPECTED_NODE_COUNT

    root_bones = [b for b in bones if b.parent is None]
    assert {b.name for b in root_bones} == EXPECTED_ROOT_NAMES

    # Every non-root bone's parent must itself be one of this armature's own
    # bones (i.e. the whole hierarchy is internally consistent, no dangling
    # references) - and every bone name must be unique (Blender would
    # otherwise have silently deduped a real collision with a ".001" suffix).
    bone_names = [b.name for b in bones]
    assert len(set(bone_names)) == len(bone_names)
    for bone in bones:
        if bone.parent is not None:
            assert bone.parent.name in bone_names

    # Rest-pose sanity: non-degenerate (not every bone collapsed to the
    # same point) and roughly creature-scale (a small quadruped -
    # smaller than a human but not toy-sized or building-sized).
    heads = [tuple(b.head_local) for b in bones]
    assert len(set(heads)) > 1, "every bone landed on the exact same head position"
    ys = [h[2] for h in heads]  # Blender Z is the game's Y-up "vertical" axis after conversion
    span = max(ys) - min(ys)
    assert 0.1 < span < 10.0, f"implausible vertical bone span for a small quadruped creature: {span}"

    # Mesh objects parented to the armature, deforming via a real ARMATURE
    # modifier with vertex groups renamed to real bone names (not raw
    # indices) - see mesh.py/_build_weights().
    mesh_obs = [ob for ob in imported if ob.type == "MESH"]
    assert mesh_obs
    deforming = [
        ob for ob in mesh_obs
        if any(mod.type == "ARMATURE" and mod.object == armature_ob for mod in ob.modifiers)
    ]
    assert deforming, "expected at least one mesh with an ARMATURE modifier pointing at the imported skeleton"
    for ob in deforming:
        assert ob.parent == armature_ob
        assert ob.vertex_groups
        for vg in ob.vertex_groups:
            assert vg.name in bone_names, f"vertex group {vg.name!r} doesn't match any real bone name"
