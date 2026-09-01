import io
import json
import os

import pytest

from albam.engines.mtfw.structs.mrl import Mrl
from albam.engines.mtfw.material import (
    MRL_BLEND_STATE_STR,
    MRL_DEPTH_STENCIL_STATE_STR,
    MRL_RASTERIZER_STATE_STR,
    MRL_MATERIAL_TYPE_STR,
)
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below). Extend this directly
# to add more.
MRL_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "mrl_parsing_hashes.json")
with open(MRL_PARSING_DATASET_PATH) as f:
    MRL_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mrl_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mrl_path_hash")
        argvalues = [(d["app_id"], d["mrl_path_hash"]) for d in MRL_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['mrl_path_hash']}" for d in MRL_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MRL_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in MRL_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mrl_path_hash"] in catalog_hashes, (
            f"{entry['mrl_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_mrl(game_fs_root, local_app_id, local_mrl_path_hash):
    from kaitaistruct import KaitaiStream

    path = resolve_hashes(game_fs_root, {local_mrl_path_hash})[local_mrl_path_hash]
    mrl_bytes = game_fs_root.readbytes(path)
    parsed = Mrl(local_app_id, KaitaiStream(io.BytesIO(mrl_bytes)))
    parsed.app_id = local_app_id
    parsed._read()
    return parsed


KNOWN_CONSTANT_BUFFERS = {
    "re0": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.globals,
    },
    "re1": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.cbdistortion,
        Mrl.ShaderObjectHash.cbdistortionrefract,
        Mrl.ShaderObjectHash.globals,
    },
    "rev1": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.cbdistortion,
        Mrl.ShaderObjectHash.cbdistortionrefract,
        Mrl.ShaderObjectHash.globals,
    },
    "rev2": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.cbbalphaclip,
        Mrl.ShaderObjectHash.cbdistortion,
        Mrl.ShaderObjectHash.cbcolormask,
        Mrl.ShaderObjectHash.cbdistortionrefract,
        Mrl.ShaderObjectHash.cbvertexdisplacement,
        Mrl.ShaderObjectHash.cbvertexdisplacement2,
        Mrl.ShaderObjectHash.cbvertexdisplacement3,
        Mrl.ShaderObjectHash.cbvertexdispmaskuv,
        Mrl.ShaderObjectHash.globals,
    },
    "re6": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.cbbalphaclip,
        Mrl.ShaderObjectHash.cbdistortion,
        Mrl.ShaderObjectHash.cbcolormask,
        Mrl.ShaderObjectHash.cbdistortionrefract,
        Mrl.ShaderObjectHash.cbvertexdisplacement,
        Mrl.ShaderObjectHash.cbvertexdisplacement2,
        Mrl.ShaderObjectHash.cbvertexdisplacement3,
        Mrl.ShaderObjectHash.cbvertexdispmaskuv,
        Mrl.ShaderObjectHash.globals,
    },
    "dd": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.cbdistortion,
        Mrl.ShaderObjectHash.cbdistortionrefract,
        Mrl.ShaderObjectHash.cbddmaterialparam,
        Mrl.ShaderObjectHash.cboutlineex,
        Mrl.ShaderObjectHash.cbappclipplane,
        Mrl.ShaderObjectHash.cbappreflect,
        Mrl.ShaderObjectHash.cbappreflectshadowlight,
        Mrl.ShaderObjectHash.cbburncommon,
        Mrl.ShaderObjectHash.cbburnemission,
        Mrl.ShaderObjectHash.cbddmaterialparaminnercorrect,
        Mrl.ShaderObjectHash.cbspecularblend,
        Mrl.ShaderObjectHash.cbuvrotationoffset,
        Mrl.ShaderObjectHash.globals,
    },
    "umvc3": {
        Mrl.ShaderObjectHash.cbmaterial,
        Mrl.ShaderObjectHash.cbdiffusecolorcorect,
        Mrl.ShaderObjectHash.cbhalflambert,
        Mrl.ShaderObjectHash.cbindirectuser,
        Mrl.ShaderObjectHash.cbtoon2,
        Mrl.ShaderObjectHash.globals,
    },
}


def test_materials(parsed_mrl, subtests):

    for material in parsed_mrl.materials:
        with subtests.test(material_hash=material.name_hash_crcjam32):
            assert material.blend_state_hash >> 12 in MRL_BLEND_STATE_STR
            assert material.depth_stencil_state_hash >> 12 in MRL_DEPTH_STENCIL_STATE_STR
            assert material.rasterizer_state_hash >> 12 in MRL_RASTERIZER_STATE_STR
            assert material.type_hash in MRL_MATERIAL_TYPE_STR


def test_global_resources_mandatory(parsed_mrl):
    """
    Test that every material has to include a $Globals shader object
    if it contains resources
    """
    for m in parsed_mrl.materials:
        raw_hashes = {r.shader_object_hash for r in m.resources}
        for h in raw_hashes:
            if not getattr(h, "value", None):
                print(h)
                assert False
        hashes = {r.shader_object_hash.value for r in m.resources}
        assert not hashes or Mrl.ShaderObjectHash.globals.value in hashes
        assert not hashes or Mrl.ShaderObjectHash.cbmaterial.value in hashes


def test_known_constant_buffers(parsed_mrl, subtests):
    for mat_idx, mat in enumerate(parsed_mrl.materials):
        for r_idx, res in enumerate(mat.resources):
            if not res.cmd_type == Mrl.CmdType.set_constant_buffer:
                continue
            with subtests.test(material_index=mat_idx, resource_index=r_idx):
                assert res.shader_object_hash in KNOWN_CONSTANT_BUFFERS[parsed_mrl.app_id]
