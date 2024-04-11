

def test_export_mrl_top_level(mrl_imported, mrl_exported):
    src_mrl = mrl_imported
    dst_mrl = mrl_exported

    assert src_mrl.id_magic == dst_mrl.id_magic
    assert src_mrl.version == dst_mrl.version
    assert src_mrl.num_materials == dst_mrl.num_materials
    # assert src_mrl.num_textures == dst_mrl.num_textures
    assert src_mrl.unk_01 == dst_mrl.unk_01
    assert src_mrl.ofs_textures == dst_mrl.ofs_textures
    # assert src_mrl.ofs_materials == dst_mrl.ofs_materials


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


def _test_materials(mrl_imported, mrl_exported, subtests):
    src_mrl = mrl_imported
    dst_mrl = mrl_exported

    for i, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[i]

        with subtests.test(material_index=i):
            assert src_material.type_hash == dst_material.type_hash
            # assert src_material.name_hash_crcjam32 == dst_material.name_hash_crcjam32
            # assert src_material.cmd_buffer_size == dst_material.cmd_buffer_size
            assert src_material.blend_state_hash == dst_material.blend_state_hash
            assert src_material.depth_stencil_state_hash == dst_material.depth_stencil_state_hash
            assert src_material.rasterizer_state_hash == dst_material.rasterizer_state_hash
            assert src_material.num_resources == dst_material.num_resources
            # assert src_material.unused == dst_material.unused
            assert src_material.material_info_flags == dst_material.material_info_flags
            assert src_material.unk_nulls == dst_material.unk_nulls
            # assert src_material.anim_data_size == dst_material.anim_data_size
            # assert src_material.ofs_cmd == dst_material.ofs_cmd
            # assert src_material.ofs_anim_data == dst_material.ofs_anim_data


def test_resource_names(mrl_imported, mrl_exported, subtests):
    src_mrl = mrl_imported
    dst_mrl = mrl_exported

    for mi, dst_material in enumerate(dst_mrl.materials):
        if mi != 1:
            continue
        src_material = src_mrl.materials[mi]
        src_resource_names = [r.shader_object_hash.name for r in src_material.resources]
        dst_resource_names = [r.shader_object_hash.name for r in dst_material.resources]

        with subtests.test(material_index=mi):
            assert sorted(src_resource_names) == sorted(dst_resource_names)
        break


def test_resources(mrl_imported, mrl_exported, subtests):
    src_mrl = mrl_imported
    dst_mrl = mrl_exported

    for mi, dst_material in enumerate(dst_mrl.materials):
        src_material = src_mrl.materials[mi]
        for ri, dst_resource in enumerate(dst_material.resources):
            src_resource = src_material.resources[ri]
            with subtests.test(material_index=mi, resource_index=ri):
                assert src_resource.cmd_type == dst_resource.cmd_type
