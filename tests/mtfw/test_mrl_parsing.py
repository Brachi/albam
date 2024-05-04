from albam.engines.mtfw.structs.mrl import Mrl

KNOWN_BLEND_STATE_STENSIL_HASH = [
    0x62b2d,  # BSSolid
    0x23baf,  # BSBlendAlpha
    0xd3b1d,  # BSAddAlpha
    0xc4064,  # BSRevSubAlpha
]

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
    }
}


def test_global_resources_mandatory(mrl_imported):
    """
    Test that every material has to include a $Globals shader object
    if it contains resources
    """
    for m in mrl_imported.materials:
        hashes = {r.shader_object_hash.value for r in m.resources}
        assert (m.blend_state_hash >> 12) in KNOWN_BLEND_STATE_STENSIL_HASH
        assert not hashes or Mrl.ShaderObjectHash.globals.value in hashes
        assert not hashes or Mrl.ShaderObjectHash.cbmaterial.value in hashes


def test_known_constant_buffers(mrl_imported, subtests):
    for mat_idx, mat in enumerate(mrl_imported.materials):
        for r_idx, res in enumerate(mat.resources):
            if not res.cmd_type == Mrl.CmdType.set_constant_buffer:
                continue
            with subtests.test(material_index=mat_idx, resource_index=r_idx):
                assert res.shader_object_hash in KNOWN_CONSTANT_BUFFERS[mrl_imported.app_id]
