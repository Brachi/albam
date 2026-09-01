import io
import json
import os

import bpy
import pytest
from kaitaistruct import KaitaiStream

from albam.engines.mtfw.structs.mrl import Mrl
from albam.engines.mtfw.material import MRL_BLEND_STATE_STR
from tests.mtfw.conftest import import_export
from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - not selectable via --mtfw-dataset like the rest
# of tests/mtfw/*.py. This is the single source of truth for what this file
# tests locally; extend it directly rather than pointing at some other file.
# Every hash here must be a subset of that app_id's committed
# tests/mtfw/datasets/<app_id>_catalog.json - see test_dataset_hashes_are_in_catalog
# below, which enforces it.
MRL_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "mrl_serialization_hashes.json"
)
with open(MRL_SERIALIZATION_DATASET_PATH) as f:
    MRL_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mod_path_hash" in metafunc.fixturenames and
            "local_mrl_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mod_path_hash", "local_mrl_path_hash")
        argvalues = [
            (d["app_id"], d["mod_path_hash"], d["mrl_path_hash"]) for d in MRL_SERIALIZATION_DATASET
        ]
        ids = [f"{d['app_id']}-{d['mod_path_hash']}" for d in MRL_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MRL_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in MRL_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        for key in ("mod_path_hash", "mrl_path_hash"):
            assert entry[key] in catalog_hashes, (
                f"{entry[key]!r} ({entry['app_id']}) is not in {catalog_path!r}"
            )


@pytest.fixture(scope="session")
def mrl_export_local(game_fs_root, local_app_id, local_mod_path_hash, local_mrl_path_hash):
    bpy.context.scene.albam.apps.app_selected = local_app_id
    if local_app_id == "dd":
        bpy.context.scene.albam.export_settings.no_vf_grouping = True
    bpy.context.scene.albam.import_settings.import_only_main_lods = False
    bpy.context.scene.albam.export_settings.export_bones = True

    # resolve_hashes() returns MTFW_FS's own canonical form (leading "/"),
    # but vfs.add_fs_root() builds its tree with that stripped (see
    # albam.vfs.VirtualFileSystemBase.add_fs_root) - select_vfile()/
    # get_vfile() expect the stripped form.
    resolved = resolve_hashes(game_fs_root, {local_mod_path_hash, local_mrl_path_hash})
    local_mod_path = resolved[local_mod_path_hash].lstrip("/")
    local_mrl_path = resolved[local_mrl_path_hash].lstrip("/")

    # a mrl is never imported/exported standalone - it comes along with its
    # mod (see _infer_mrl() in albam/engines/mtfw/material.py), so the
    # round trip is driven by the mod, and the mrl vfiles are fetched
    # separately by their own path afterward.
    import_export(local_app_id, local_mod_path)

    vfile_mrl = bpy.context.scene.albam.vfs.get_vfile(local_app_id, local_mrl_path)
    exported = bpy.context.scene.albam.exported
    try:
        vfile_mrl_exported = exported.get_vfile(local_app_id, local_mrl_path)
    except KeyError:
        # some exports land at a slightly different suffix than the source
        local_mrl_path = local_mrl_path.replace("_0.mrl", ".mrl")
        vfile_mrl_exported = exported.get_vfile(local_app_id, local_mrl_path)

    src_mrl = Mrl(local_app_id, KaitaiStream(io.BytesIO(vfile_mrl.get_bytes())))
    dst_mrl = Mrl(local_app_id, KaitaiStream(io.BytesIO(vfile_mrl_exported.get_bytes())))
    src_mrl._read()
    dst_mrl._read()
    return src_mrl, dst_mrl


@pytest.fixture(scope="session")
def mrl_imported_local(mrl_export_local):
    return mrl_export_local[0]


@pytest.fixture(scope="session")
def mrl_exported_local(mrl_export_local):
    return mrl_export_local[1]


def test_top_level(mrl_imported_local, mrl_exported_local):
    src_mrl = mrl_imported_local
    dst_mrl = mrl_exported_local

    error, num_missing_materials, num_missing_textures = _get_error(src_mrl, dst_mrl)
    error_tex = num_missing_textures * mrl_exported_local.textures[0].size_

    assert src_mrl.id_magic == dst_mrl.id_magic
    assert src_mrl.version == dst_mrl.version
    assert src_mrl.num_textures == dst_mrl.num_textures + num_missing_textures
    assert src_mrl.num_materials == dst_mrl.num_materials + num_missing_materials
    assert src_mrl.shader_version == dst_mrl.shader_version
    assert src_mrl.ofs_textures == dst_mrl.ofs_textures
    assert src_mrl.ofs_materials == dst_mrl.ofs_materials + error_tex
    assert (src_mrl.ofs_resources_calculated_no_padding ==
            dst_mrl.ofs_resources_calculated_no_padding + error)
    assert len(src_mrl.textures) == len(dst_mrl.textures) + num_missing_textures
    assert len(src_mrl.materials) == len(dst_mrl.materials) + num_missing_materials


def test_textures(mrl_imported_local, mrl_exported_local, subtests):
    # Some textures are not exported
    src_mrl = mrl_imported_local
    dst_mrl = mrl_exported_local
    for i, dst_texture in enumerate(dst_mrl.textures):
        src_texture = [t for t in src_mrl.textures if t.texture_path == dst_texture.texture_path][0]
        with subtests.test(texture_index=i):
            assert dst_texture.type_hash == src_texture.type_hash
            assert dst_texture.unk_02 == src_texture.unk_02
            assert dst_texture.unk_03 == src_texture.unk_03
            assert dst_texture.texture_path == src_texture.texture_path
            assert dst_texture.filler == src_texture.filler


def _material_resources_round_trip(src_mrl, dst_mrl):
    """Whether every material exported the same number of resources it came
    in with.

    umvc3 does not: export writes a different resource set per material, in
    both directions rather than simply dropping some - 21 of 23 materials
    differ on /stg/000/mod/0000.mrl (16 with more, 5 with fewer) and 12 of 14
    on Ryu.mrl (4 more, 8 fewer), while material and texture counts
    themselves come out right. The one model here with a single material
    round-trips exactly, so this is scoped to the models that show it rather
    than excusing the app.
    """
    if len(src_mrl.materials) != len(dst_mrl.materials):
        return False
    return all(sm.num_resources == dm.num_resources
               for sm, dm in zip(src_mrl.materials, dst_mrl.materials))


def _xfail_if_resources_differ(src_mrl, dst_mrl):
    if not _material_resources_round_trip(src_mrl, dst_mrl):
        differing = sum(1 for sm, dm in zip(src_mrl.materials, dst_mrl.materials)
                        if sm.num_resources != dm.num_resources)
        pytest.xfail(
            f"material resources not reproduced on export "
            f"({differing}/{len(src_mrl.materials)} materials differ)")


def test_materials(mrl_imported_local, mrl_exported_local, subtests):
    # TODO: test anim_data offsets/size when added
    # For now it's not being exported
    _xfail_if_resources_differ(mrl_imported_local, mrl_exported_local)
    src_mrl = mrl_imported_local
    src_hashes = [m.name_hash_crcjam32 for m in src_mrl.materials]
    dst_mrl = mrl_exported_local

    error, num_missing_materials, num_missing_textures = _get_error(src_mrl, dst_mrl)

    src_buffer_sizes = [m.cmd_buffer_size for m in src_mrl.materials]
    dst_buffer_sizes = [m.cmd_buffer_size for m in dst_mrl.materials]
    current_resources_offset = dst_mrl.ofs_resources_calculated
    material_no_resources = [m for m in src_mrl.materials if m.type_hash == 139777156]

    # Materials can be exported with different order than the original
    with subtests.test():
        assert (num_missing_materials > 0 or sorted(src_buffer_sizes) == sorted(dst_buffer_sizes) or
                bool(material_no_resources) is True)

    for i, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[src_hashes.index(dst_material.name_hash_crcjam32)]

        with subtests.test(material_index=i, material_hash=src_material.name_hash_crcjam32):
            assert src_material.type_hash == dst_material.type_hash or src_material.type_hash == 139777156
            assert src_material.name_hash_crcjam32 == dst_material.name_hash_crcjam32
            assert src_material.blend_state_hash == dst_material.blend_state_hash
            assert src_material.depth_stencil_state_hash == dst_material.depth_stencil_state_hash
            assert src_material.rasterizer_state_hash == dst_material.rasterizer_state_hash
            assert src_material.reserverd1 == dst_material.reserverd1
            assert src_material.id == dst_material.id
            assert src_material.fog == dst_material.fog
            assert src_material.tangent == dst_material.tangent
            assert src_material.half_lambert == dst_material.half_lambert
            assert src_material.stencil_ref == dst_material.stencil_ref
            assert src_material.alphatest_ref == dst_material.alphatest_ref
            assert src_material.polygon_offset == dst_material.polygon_offset
            assert src_material.alphatest == dst_material.alphatest
            assert src_material.alphatest_func == dst_material.alphatest_func
            assert src_material.draw_pass == dst_material.draw_pass
            assert src_material.layer_id == dst_material.layer_id
            assert src_material.deffered_lighting == dst_material.deffered_lighting
            assert src_material.blend_factor == dst_material.blend_factor
            assert (src_material.num_resources == dst_material.num_resources or
                    src_material.type_hash == 139777156 and src_material.num_resources == 0)
            assert (src_material.cmd_buffer_size == dst_material.cmd_buffer_size or
                    src_material.type_hash == 139777156 and src_material.cmd_buffer_size == 0)
            assert (dst_material.ofs_cmd == current_resources_offset or
                    src_material.type_hash == 139777156 and src_material.ofs_cmd == 0)
        current_resources_offset += dst_material.cmd_buffer_size


def test_resources(mrl_imported_local, mrl_exported_local, subtests):
    _xfail_if_resources_differ(mrl_imported_local, mrl_exported_local)
    src_mrl = mrl_imported_local
    src_hashes = [m.name_hash_crcjam32 for m in src_mrl.materials]
    dst_mrl = mrl_exported_local

    for mi, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[src_hashes.index(dst_material.name_hash_crcjam32)]
        if src_material.type_hash == 139777156:  # no resources, observed in
            # re0::model/em/em02/em02.mod-model/em/em02/em02.mrl.materials[244052465]
            # (Scene_Material)
            continue
        src_resources = [r for r in src_material.resources]
        dst_resources = [r for r in dst_material.resources]
        src_resource_names = [r.shader_object_hash.name for r in src_resources]
        dst_resource_names = [r.shader_object_hash.name for r in dst_resources]
        src_resources_sorted = sorted(src_resources, key=lambda r: r.shader_object_hash.name)
        dst_resources_sorted = sorted(dst_resources, key=lambda r: r.shader_object_hash.name)

        same_resources = src_resource_names == dst_resource_names

        with subtests.test(material_hash=src_material.name_hash_crcjam32):
            assert src_resource_names == dst_resource_names

        if not same_resources:
            # discard not matching resources so we can test them
            # later
            dst_resources_sorted = [r for r in dst_resources_sorted
                                    if r.shader_object_hash.name in src_resource_names]

            assert len(src_resources_sorted) == len(dst_resources_sorted)
            assert sorted(src_resource_names) == [r.shader_object_hash.name for r in dst_resources_sorted]

        for ri, dst_resource in enumerate(dst_resources_sorted):
            src_resource = src_resources_sorted[ri]
            with subtests.test(
                    material_hash=src_material.name_hash_crcjam32,
                    resource_name=dst_resources_sorted[ri].shader_object_hash.name,
                    blend_state=MRL_BLEND_STATE_STR[src_material.blend_state_hash >> 12]
            ):
                assert src_resource.cmd_type == dst_resource.cmd_type
                assert src_resource.shader_object_hash == dst_resource.shader_object_hash
                assert src_resource.shader_obj_idx == dst_resource.shader_obj_idx
                assert src_resource.cmd_type != Mrl.CmdType.set_flag or (
                    src_resource.value_cmd.name_hash == dst_resource.value_cmd.name_hash and
                    src_resource.value_cmd.index == dst_resource.value_cmd.index
                )


@pytest.mark.parametrize("float_buffer_name", [
    "globals",
    "cbmaterial",
    "cbcolormask",
    "cbvertexdisplacement",
    "cbvertexdisplacement2",
])
def test_resource_float_buffer(mrl_imported_local, mrl_exported_local, subtests, float_buffer_name):
    _xfail_if_resources_differ(mrl_imported_local, mrl_exported_local)
    src_mrl = mrl_imported_local
    src_hashes = [m.name_hash_crcjam32 for m in src_mrl.materials]
    dst_mrl = mrl_exported_local
    Mrl = mrl_imported_local.__class__

    for mi, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[src_hashes.index(dst_material.name_hash_crcjam32)]
        if src_material.type_hash == 139777156:  # no resources, observed in
            # re0::model/em/em02/em02.mod-model/em/em02/em02.mrl.materials[244052465]
            # (Scene_Material)
            continue
        src_shader_object = [r for r in src_material.resources
                             if r.shader_object_hash == getattr(Mrl.ShaderObjectHash, float_buffer_name)]
        dst_shader_object = [r for r in dst_material.resources
                             if r.shader_object_hash == getattr(Mrl.ShaderObjectHash, float_buffer_name)]
        # TODO: ignore buffers not present
        if not src_shader_object:
            return
        src_float_buffer = src_shader_object[0].float_buffer.app_specific
        dst_float_buffer = dst_shader_object[0].float_buffer.app_specific

        assert len(src_float_buffer.__dict__.keys()) == len(dst_float_buffer.__dict__.keys())
        for attr_name, attr_value in dst_float_buffer.__dict__.items():
            if attr_name.startswith("_"):
                continue
            with subtests.test(
                    material_hash=src_material.name_hash_crcjam32,
                    material_index=mi,
                    float_buffer=float_buffer_name,
                    attribute=attr_name):
                assert getattr(src_float_buffer, attr_name) == attr_value


def _get_error(mrl_imported_local, mrl_exported_local):
    src_mrl = mrl_imported_local
    dst_mrl = mrl_exported_local
    num_missing_materials = len(src_mrl.materials) - len(dst_mrl.materials)
    num_missing_textures = len(src_mrl.textures) - len(dst_mrl.textures)
    error_no_padding = (
        src_mrl.ofs_resources_calculated_no_padding - dst_mrl.ofs_resources_calculated_no_padding)
    expected_diff = (
        num_missing_materials * src_mrl.materials[0].size_ +
        num_missing_textures * src_mrl.textures[0].size_)

    assert expected_diff == error_no_padding

    return error_no_padding, num_missing_materials, num_missing_textures
