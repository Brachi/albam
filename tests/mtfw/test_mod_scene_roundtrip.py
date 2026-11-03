"""The .mod round trip with no Blender in it: file -> scene -> glb -> scene
-> file, on the same models test_mod_serialization runs through the
operators. It takes seconds per model, so it is where a format regression
shows up first, and it is what a game with no Blender shell yet can run.
"""
import json
import os

import numpy as np
import pytest

from albam.lib.gltf import read_glb, write_glb
from tests.mtfw.scripts.catalog_paths import resolve_hashes

DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "mod_serialization_hashes.json")
with open(DATASET_PATH) as f:
    DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames):
        argvalues = [(d["app_id"], d["mod_path_hash"]) for d in DATASET]
        ids = [f"{d['app_id']}-{d['mod_path_hash']}" for d in DATASET]
        metafunc.parametrize(("local_app_id", "local_mod_path_hash"), argvalues, ids=ids, scope="session")


@pytest.fixture(scope="session")
def scene_roundtrip(game_fs_root, local_app_id, local_mod_path_hash):
    from albam.engines.mtfw import mod_scene
    from albam.lib.kaitai_utils import parse

    path = resolve_hashes(game_fs_root, {local_mod_path_hash})[local_mod_path_hash]
    src_bytes = game_fs_root.readbytes(path)
    ModCls = mod_scene.MOD_CLASS_MAPPER[src_bytes[4]]
    src_mod = parse(ModCls, src_bytes, local_app_id)

    scene = mod_scene.mod_to_scene(local_app_id, src_mod, "model")
    scene = read_glb(write_glb(scene))
    dst_bytes = mod_scene.scene_to_mod(
        scene, src_mod, local_app_id, mod_scene.ExportSettings(),
        mod_scene.copy_materials_data(src_mod, local_app_id, "model"))
    return src_mod, parse(ModCls, dst_bytes, local_app_id)


def test_header_counts(scene_roundtrip):
    src, dst = scene_roundtrip
    for field in ("version", "num_bones", "num_meshes", "num_materials", "num_groups"):
        assert getattr(src.header, field) == getattr(dst.header, field), field
    if src.header.version not in (153, 156):
        # 153/156 count a second vertex stream the scene does not carry
        assert src.header.num_vertices == dst.header.num_vertices


def test_bounding_volumes(scene_roundtrip):
    """The bounds are recomputed from vertices that the file quantizes to
    1/32767 of the bounds themselves, so they can move by one step."""
    src, dst = scene_roundtrip
    for axis in "xyz":
        assert getattr(src.bbox_min, axis) == pytest.approx(getattr(dst.bbox_min, axis), rel=1e-3, abs=1e-2)
        assert getattr(src.bbox_max, axis) == pytest.approx(getattr(dst.bbox_max, axis), rel=1e-3, abs=1e-2)
    assert src.bsphere.w == pytest.approx(dst.bsphere.w, rel=1e-3)


def test_bones(scene_roundtrip):
    src, dst = scene_roundtrip
    if src.bones_data is None:
        assert dst.bones_data is None
        return
    assert src.bones_data.bone_map == dst.bones_data.bone_map
    for src_bone, dst_bone in zip(src.bones_data.bones_hierarchy, dst.bones_data.bones_hierarchy):
        assert (src_bone.idx_anim_map, src_bone.idx_parent, src_bone.idx_mirror) == (
            dst_bone.idx_anim_map, dst_bone.idx_parent, dst_bone.idx_mirror)
        for axis in "xyz":
            assert getattr(src_bone.location, axis) == pytest.approx(
                getattr(dst_bone.location, axis), abs=9e-5)
    for src_m, dst_m in zip(src.bones_data.parent_space_matrices, dst.bones_data.parent_space_matrices):
        for row in ("row_1", "row_2", "row_3", "row_4"):
            for axis in "xyzw":
                assert getattr(getattr(src_m, row), axis) == pytest.approx(
                    getattr(getattr(dst_m, row), axis), abs=9e-5)


def test_vertices(scene_roundtrip):
    """Every mesh keeps its vertex count and, vertex by vertex, its
    position, normal, first UV and weights: the scene has one vertex per
    file vertex, so the order survives too."""
    from albam.engines.mtfw import mod_scene

    src, dst = scene_roundtrip
    src_bbox = mod_scene._create_bbox_data(src)
    dst_bbox = mod_scene._create_bbox_data(dst)
    for src_mesh, dst_mesh in zip(src.meshes_data.meshes, dst.meshes_data.meshes):
        src_attrs, src_indices = mod_scene.decode_mesh(src.app_id, src, src_mesh, src_bbox)
        dst_attrs, dst_indices = mod_scene.decode_mesh(dst.app_id, dst, dst_mesh, dst_bbox)
        assert src_attrs["POSITION"].shape == dst_attrs["POSITION"].shape
        # positions are quantized to 1/32767 of the bbox on skinned meshes
        assert np.abs(src_attrs["POSITION"] - dst_attrs["POSITION"]).max() < 1e-4
        for name in ("NORMAL", "TEXCOORD_0", mod_scene.COLOR_ATTRIBUTE):
            if name in src_attrs:
                assert name in dst_attrs
                assert np.abs(src_attrs[name] - dst_attrs[name]).max() < 1e-2, name
        if "JOINTS_0" in src_attrs:
            for k in range(2):
                if f"JOINTS_{k}" not in src_attrs:
                    break
                for src_pairs, dst_pairs in zip(_influences(src_attrs, k), _influences(dst_attrs, k)):
                    assert [j for j, _ in src_pairs] == [j for j, _ in dst_pairs]
                    assert [w for _, w in src_pairs] == pytest.approx([w for _, w in dst_pairs], abs=0.02)


# Below this a weight is quantization residue: the mod-21 half-float formats
# derive their last slot from one minus the written ones, and after the
# written ones are rounded that remainder can come out a few thousandths
# where the file had nothing, landing on the padding bone.
WEIGHT_NOISE = 0.01


def _influences(attrs, k):
    joints = attrs[f"JOINTS_{k}"]
    weights = attrs[f"WEIGHTS_{k}"]
    return [
        sorted((int(j), float(w)) for j, w in zip(vj, vw) if w > WEIGHT_NOISE)
        for vj, vw in zip(joints, weights)
    ]
