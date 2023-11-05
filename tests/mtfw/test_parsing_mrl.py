from albam.engines.mtfw.structs.mrl import Mrl


def test_global_resources_mandatory(mrl):
    """
    Test that every material has to include a $Globals shader object
    if it contains resources
    """
    for m in mrl.materials:
        hashes = {r.shader_object_hash.value for r in m.resources}
        assert not hashes or Mrl.ShaderObjectHash.globals.value in hashes
        assert not hashes or Mrl.ShaderObjectHash.cbmaterial.value in hashes
