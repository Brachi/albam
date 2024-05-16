from pprint import pprint

import pytest

from albam.engines.mtfw.structs.mrl import Mrl
from albam.engines.mtfw.material import MRL_BLEND_STATE_STR


def _get_error(mrl_imported, mrl_exported):
    src_mrl = mrl_imported
    dst_mrl = mrl_exported
    num_missing_materials = len(src_mrl.materials) - len(dst_mrl.materials)
    num_missing_textures = len(src_mrl.textures) - len(dst_mrl.textures)
    error_no_padding = (
        src_mrl.ofs_resources_calculated_no_padding - dst_mrl.ofs_resources_calculated_no_padding)
    expected_diff = (
        num_missing_materials * src_mrl.materials[0].size_ +
        num_missing_textures * src_mrl.textures[0].size_)

    assert expected_diff == error_no_padding

    return error_no_padding, num_missing_materials, num_missing_textures



def test_top_level(mrl_imported, mrl_exported):
    src_mrl = mrl_imported
    dst_mrl = mrl_exported

    error, num_missing_materials, num_missing_textures = _get_error(src_mrl, dst_mrl)

    assert src_mrl.id_magic == dst_mrl.id_magic
    assert src_mrl.version == dst_mrl.version
    assert src_mrl.num_textures == dst_mrl.num_textures + num_missing_textures
    assert src_mrl.num_materials == dst_mrl.num_materials + num_missing_materials
    assert src_mrl.unk_01 == dst_mrl.unk_01
    assert src_mrl.ofs_textures == dst_mrl.ofs_textures
    assert src_mrl.ofs_materials == dst_mrl.ofs_materials + error
    assert (src_mrl.ofs_resources_calculated_no_padding ==
            dst_mrl.ofs_resources_calculated_no_padding + error)


def test_textures(mrl_imported, mrl_exported, subtests):
    # Some textures are not exported
    src_mrl = mrl_imported
    dst_mrl = mrl_exported
    for i, dst_texture in enumerate(dst_mrl.textures):
        src_texture = [t for t in src_mrl.textures if t.texture_path == dst_texture.texture_path][0]
        with subtests.test(texture_index=i):
            assert dst_texture.type_hash == src_texture.type_hash
            assert dst_texture.unk_02 == src_texture.unk_02
            assert dst_texture.unk_03 == src_texture.unk_03
            assert dst_texture.texture_path == src_texture.texture_path
            assert dst_texture.filler == src_texture.filler


@pytest.mark.xfail()
def test_offsets(mrl_imported, mrl_exported, subtests):
    # TODO: try to export materials in order and get accumulated error
    # that way we can pontentially tests all offsets for float buffers
    src_mrl = mrl_imported
    dst_mrl = mrl_exported

    for mi, mat in enumerate(src_mrl.materials):
        if mi > len(dst_mrl.materials):
            continue
        with subtests.test(material_index=mi):
            assert mat.name_hash_crcjam32 == dst_mrl.materials[mi].name_hash_crcjam32


def test_materials(mrl_imported, mrl_exported, subtests):
    src_mrl = mrl_imported
    src_hashes = [m.name_hash_crcjam32 for m in src_mrl.materials]
    dst_mrl = mrl_exported

    error, num_missing_materials, num_missing_textures = _get_error(src_mrl, dst_mrl)

    for i, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[src_hashes.index(dst_material.name_hash_crcjam32)]

        with subtests.test(material_index=i):
            assert src_material.type_hash == dst_material.type_hash
            assert src_material.name_hash_crcjam32 == dst_material.name_hash_crcjam32
            assert src_material.blend_state_hash == dst_material.blend_state_hash
            assert src_material.depth_stencil_state_hash == dst_material.depth_stencil_state_hash
            assert src_material.rasterizer_state_hash == dst_material.rasterizer_state_hash
            assert src_material.unused == dst_material.unused
            assert src_material.material_info_flags == dst_material.material_info_flags
            assert src_material.unk_nulls == dst_material.unk_nulls
            assert src_material.num_resources == dst_material.num_resources
            assert src_material.cmd_buffer_size == dst_material.cmd_buffer_size

        with subtests.test(material_hash=src_material.name_hash_crcjam32):
            if error:
                pytest.xfail(reason="Difference in offset expected due to missing materials")
            # assert src_material.anim_data_size == dst_material.anim_data_size
            # assert src_material.ofs_anim_data == dst_material.ofs_anim_data


def test_resources(mrl_imported, mrl_exported, subtests):
    src_mrl = mrl_imported
    src_hashes = [m.name_hash_crcjam32 for m in src_mrl.materials]
    dst_mrl = mrl_exported

    for mi, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[src_hashes.index(dst_material.name_hash_crcjam32)]
        src_resources = [r for r in src_material.resources]
        dst_resources = [r for r in dst_material.resources]
        src_resource_names = [r.shader_object_hash.name for r in src_resources]
        dst_resource_names = [r.shader_object_hash.name for r in dst_resources]
        src_resources_sorted = sorted(src_resources, key=lambda r: r.shader_object_hash.name)
        dst_resources_sorted = sorted(dst_resources, key=lambda r: r.shader_object_hash.name)
        print_me = sorted(src_resource_names)

        same_num_resources = src_resource_names == dst_resource_names

        with subtests.test(material_hash=src_material.name_hash_crcjam32):
            assert src_resource_names == dst_resource_names

        if not same_num_resources:
            # no point in comparing resources if we start with having a different
            # amount. This will just add noise in test failures
            continue

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


@pytest.mark.parametrize("float_buffer_name", ["globals", "cbmaterial"])
def test_resource_float_buffer(mrl_imported, mrl_exported, subtests, float_buffer_name):
    src_mrl = mrl_imported
    src_hashes = [m.name_hash_crcjam32 for m in src_mrl.materials]
    dst_mrl = mrl_exported
    Mrl = mrl_imported.__class__

    for mi, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[src_hashes.index(dst_material.name_hash_crcjam32)]
        src_shader_object = [r for r in src_material.resources
                             if r.shader_object_hash == getattr(Mrl.ShaderObjectHash, float_buffer_name)]
        dst_shader_object = [r for r in dst_material.resources
                             if r.shader_object_hash == getattr(Mrl.ShaderObjectHash, float_buffer_name)]
        # TODO: ignore buffers not present
        src_float_buffer = src_shader_object[0].float_buffer.app_specific
        dst_float_buffer = dst_shader_object[0].float_buffer.app_specific

        assert len(src_float_buffer.__dict__.keys()) == len(dst_float_buffer.__dict__.keys())
        for attr_name, attr_value in dst_float_buffer.__dict__.items():
            if attr_name.startswith("_"):
                continue
            with subtests.test(material_index=mi, float_buffer=float_buffer_name, attribute=attr_name):
                assert getattr(src_float_buffer, attr_name) == attr_value
