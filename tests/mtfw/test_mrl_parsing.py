from albam.engines.mtfw.structs.mrl import Mrl
from albam.engines.mtfw.material import (
    MRL_BLEND_STATE_STR,
    MRL_DEPTH_STENCIL_STATE_STR,
    MRL_RASTERIZER_STATE_STR,
)


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
        Mrl.ShaderObjectHash.globals,
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
    },

}


def test_materials(parsed_mrl_from_arc, subtests):

    for material in parsed_mrl_from_arc.materials:
        with subtests.test(material_hash=material.name_hash_crcjam32):
            assert material.blend_state_hash >> 12 in MRL_BLEND_STATE_STR
            assert material.depth_stencil_state_hash >> 12 in MRL_DEPTH_STENCIL_STATE_STR
            assert material.rasterizer_state_hash >> 12 in MRL_RASTERIZER_STATE_STR


def test_global_resources_mandatory(parsed_mrl_from_arc):
    """
    Test that every material has to include a $Globals shader object
    if it contains resources
    """
    for m in parsed_mrl_from_arc.materials:
        raw_hashes = {r.shader_object_hash for r in m.resources}
        for h in raw_hashes:
            if not getattr(h, "value", None):
                print(h)
                assert False
        hashes = {r.shader_object_hash.value for r in m.resources}
        assert not hashes or Mrl.ShaderObjectHash.globals.value in hashes
        assert not hashes or Mrl.ShaderObjectHash.cbmaterial.value in hashes


def test_known_constant_buffers(parsed_mrl_from_arc, subtests):
    for mat_idx, mat in enumerate(parsed_mrl_from_arc.materials):
        for r_idx, res in enumerate(mat.resources):
            if not res.cmd_type == Mrl.CmdType.set_constant_buffer:
                continue
            with subtests.test(material_index=mat_idx, resource_index=r_idx):
                assert res.shader_object_hash in KNOWN_CONSTANT_BUFFERS[parsed_mrl_from_arc.app_id]
