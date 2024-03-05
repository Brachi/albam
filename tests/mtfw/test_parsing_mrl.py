from albam.engines.mtfw.structs.mrl import Mrl

KNOWN_BLEND_STATE_STENSIL_HASH = [
    0x62b2d,  # BSSolid
    0x23baf,  # BSBlendAlpha
    0xd3b1d,  # BSAddAlpha
    0xc4064,  # BSRevSubAlpha
]


def test_global_resources_mandatory(mrl):
    """
    Test that every material has to include a $Globals shader object
    if it contains resources
    """
    for m in mrl.materials:
        hashes = {r.shader_object_hash.value for r in m.resources}
        assert (m.blend_state_hash >> 12) in KNOWN_BLEND_STATE_STENSIL_HASH
        assert not hashes or Mrl.ShaderObjectHash.globals.value in hashes
        assert not hashes or Mrl.ShaderObjectHash.cbmaterial.value in hashes
