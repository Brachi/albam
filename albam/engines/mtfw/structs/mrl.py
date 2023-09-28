# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mrl(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x52\x4C\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x52\x4C\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.num_materials = self._io.read_u4le()
        self.num_textures = self._io.read_u4le()
        self.unk_01 = self._io.read_u4le()
        self.ofs_textures = self._io.read_u4le()
        self.ofs_materials = self._io.read_u4le()
        self.textures = []
        for i in range(self.num_textures):
            self.textures.append(Mrl.TextureSlot(self._io, self, self._root))

        self.materials = []
        for i in range(self.num_materials):
            self.materials.append(Mrl.Material(self._io, self, self._root))


    class AnimSubEntry1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                self.values.append(Mrl.AnimType1(self._io, self, self._root))



    class StrCbBaAlphaClip(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_b_alpha_clip_threshold = self._io.read_f4le()
            self.f_b_blend_rate = self._io.read_f4le()
            self.f_b_blend_band = self._io.read_f4le()
            self.filler = self._io.read_f4le()


    class StrCbDistortion(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_distortion_factor = self._io.read_f4le()
            self.f_distortion_blend = self._io.read_f4le()
            self.filler = []
            for i in range(2):
                self.filler.append(self._io.read_f4le())



    class AnimSubEntry5(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())



    class CmdTexIdx(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tex_idx = self._io.read_u4le()


    class HashBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.index = self._io.read_bits_int_le(12)
            self.value = self._io.read_bits_int_le(20)


    class StrCbVtxDispEx(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_vtx_disp_ex_scale0 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale1 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale2 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale3 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale4 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale5 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale6 = self._io.read_f4le()
            self.f_vtx_disp_ex_scale7 = self._io.read_f4le()
            self.f_vtx_disp_ex_radius = self._io.read_f4le()
            self.f_vtx_disp_ex_rot_x = self._io.read_f4le()
            self.f_vtx_disp_ex_rot_y = self._io.read_f4le()
            self.f_vtx_disp_ex_rot_z = self._io.read_f4le()
            self.f_vtx_disp_ex_rot_origin_x = self._io.read_f4le()
            self.f_vtx_disp_ex_rot_origin_y = self._io.read_f4le()
            self.f_vtx_disp_ex_rot_origin_z = self._io.read_f4le()
            self.filler = self._io.read_f4le()


    class StrRev2CbGlobals(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_alpha_clip_threshold = self._io.read_f4le()
            self.f_albedo_color = []
            for i in range(3):
                self.f_albedo_color.append(self._io.read_f4le())

            self.f_albedo_blend_color = []
            for i in range(4):
                self.f_albedo_blend_color.append(self._io.read_f4le())

            self.f_detail_normal_power = self._io.read_f4le()
            self.f_detail_normal_uv_scale = self._io.read_f4le()
            self.f_detail_normal2_power = self._io.read_f4le()
            self.f_detail_normal2_uv_scale = self._io.read_f4le()
            self.f_primary_shift = self._io.read_f4le()
            self.f_secondary_shift = self._io.read_f4le()
            self.f_parallax_factor = self._io.read_f4le()
            self.f_parallax_self_occlusion = self._io.read_f4le()
            self.f_parallax_min_sample = self._io.read_f4le()
            self.f_parallax_max_sample = []
            for i in range(3):
                self.f_parallax_max_sample.append(self._io.read_f4le())

            self.f_light_map_color = []
            for i in range(4):
                self.f_light_map_color.append(self._io.read_f4le())

            self.f_thin_map_color = []
            for i in range(3):
                self.f_thin_map_color.append(self._io.read_f4le())

            self.f_thin_scattering = self._io.read_f4le()
            self.f_screen_uv_scale = []
            for i in range(2):
                self.f_screen_uv_scale.append(self._io.read_f4le())

            self.f_screen_uv_offset = []
            for i in range(2):
                self.f_screen_uv_offset.append(self._io.read_f4le())

            self.f_indirect_offset = []
            for i in range(2):
                self.f_indirect_offset.append(self._io.read_f4le())

            self.f_indirect_scale = []
            for i in range(2):
                self.f_indirect_scale.append(self._io.read_f4le())

            self.f_fresnel_schlick = self._io.read_f4le()
            self.f_fresnel_schlick_rgb = []
            for i in range(3):
                self.f_fresnel_schlick_rgb.append(self._io.read_f4le())

            self.f_specular_color = []
            for i in range(3):
                self.f_specular_color.append(self._io.read_f4le())

            self.f_shininess = self._io.read_f4le()
            self.f_emission_color = []
            for i in range(3):
                self.f_emission_color.append(self._io.read_f4le())

            self.f_emission_threshold = self._io.read_f4le()
            self.f_constant_color = []
            for i in range(4):
                self.f_constant_color.append(self._io.read_f4le())

            self.f_roughness = self._io.read_f4le()
            self.f_roughness_rgb = []
            for i in range(3):
                self.f_roughness_rgb.append(self._io.read_f4le())

            self.f_anisotoropic_direction = []
            for i in range(3):
                self.f_anisotoropic_direction.append(self._io.read_f4le())

            self.f_smoothness = self._io.read_f4le()
            self.f_anistropic_uv = []
            for i in range(2):
                self.f_anistropic_uv.append(self._io.read_f4le())

            self.f_primary_expo = self._io.read_f4le()
            self.f_secondary_expo = self._io.read_f4le()
            self.f_primary_color = []
            for i in range(4):
                self.f_primary_color.append(self._io.read_f4le())

            self.f_secondary_color = []
            for i in range(4):
                self.f_secondary_color.append(self._io.read_f4le())

            self.f_albedo_color2 = []
            for i in range(4):
                self.f_albedo_color2.append(self._io.read_f4le())

            self.f_specular_color2 = []
            for i in range(3):
                self.f_specular_color2.append(self._io.read_f4le())

            self.f_fresnel_schlick2 = self._io.read_f4le()
            self.f_shininess2 = []
            for i in range(4):
                self.f_shininess2.append(self._io.read_f4le())

            self.f_transparency_clip_threshold = []
            for i in range(4):
                self.f_transparency_clip_threshold.append(self._io.read_f4le())

            self.f_blend_uv = self._io.read_f4le()
            self.f_normal_power = []
            for i in range(3):
                self.f_normal_power.append(self._io.read_f4le())

            self.f_albedo_blend2_color = []
            for i in range(4):
                self.f_albedo_blend2_color.append(self._io.read_f4le())

            self.f_detail_normal_u_v_scale = []
            for i in range(2):
                self.f_detail_normal_u_v_scale.append(self._io.read_f4le())

            self.f_fresnel_legacy = []
            for i in range(2):
                self.f_fresnel_legacy.append(self._io.read_f4le())

            self.f_normal_mask_pow0 = []
            for i in range(4):
                self.f_normal_mask_pow0.append(self._io.read_f4le())

            self.f_normal_mask_pow1 = []
            for i in range(4):
                self.f_normal_mask_pow1.append(self._io.read_f4le())

            self.f_normal_mask_pow2 = []
            for i in range(4):
                self.f_normal_mask_pow2.append(self._io.read_f4le())

            self.f_texture_blend_rate = []
            for i in range(4):
                self.f_texture_blend_rate.append(self._io.read_f4le())

            self.f_texture_blend_color = []
            for i in range(4):
                self.f_texture_blend_color.append(self._io.read_f4le())



    class AnimInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk = self._io.read_bits_int_le(2)
            self.num_entry2 = self._io.read_bits_int_le(16)
            self.num_entry1 = self._io.read_bits_int_le(14)


    class StrCbVtxDispMaskUv(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_vertex_disp_mask_uv = []
            for i in range(8):
                self.f_vertex_disp_mask_uv.append(self._io.read_f4le())



    class AnimType4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = []
            for i in range(19):
                self.unk_01.append(self._io.read_f4le())



    class StrCbVtxDisplacement3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_vtx_disp_direction = []
            for i in range(3):
                self.f_vtx_disp_direction.append(self._io.read_f4le())

            self.filler = self._io.read_f4le()


    class CbUnk01(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(4):
                self.data.append(self._io.read_f4le())



    class CmdInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd_type = self._io.read_bits_int_le(4)
            self.unk = self._io.read_bits_int_le(16)
            self.shader_obj_idx = self._io.read_bits_int_le(12)


    class AnimOfs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_block = self._io.read_u4le()

        @property
        def anim_entries(self):
            if hasattr(self, '_m_anim_entries'):
                return self._m_anim_entries

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_anim_data + self.ofs_block))
            self._m_anim_entries = Mrl.AnimEntry(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_anim_entries', None)


    class AnimSubEntry0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                self.values.append(Mrl.AnimType0(self._io, self, self._root))



    class CbUnk02(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(24):
                self.data.append(self._io.read_f4le())



    class AnimSubEntry7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(36):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((24 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



    class ShdHash(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.shader_hash = self._io.read_u4le()


    class AnimType0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = self._io.read_f4le()


    class StrCbMaterial(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_diffuse_color = []
            for i in range(3):
                self.f_diffuse_color.append(self._io.read_f4le())

            self.f_transparency = self._io.read_f4le()
            self.f_reflective_color = []
            for i in range(3):
                self.f_reflective_color.append(self._io.read_f4le())

            self.f_transparency_volume = self._io.read_f4le()
            self.f_uv_transform = []
            for i in range(8):
                self.f_uv_transform.append(self._io.read_f4le())

            self.f_uv_transform2 = []
            for i in range(8):
                self.f_uv_transform2.append(self._io.read_f4le())

            self.f_uv_transform3 = []
            for i in range(8):
                self.f_uv_transform3.append(self._io.read_f4le())



    class TextureSlot(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type_hash = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            self.texture_path = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ascii")


    class BlockOffset(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofc_block = self._io.read_u4le()

        @property
        def body(self):
            if hasattr(self, '_m_body'):
                return self._m_body

            _pos = self._io.pos()
            self._io.seek((self._parent._parent._parent.ofs_base + self.ofc_block))
            self._m_body = Mrl.AnimSubEntry(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_body', None)


    class StrCbVtxDisplacement(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_vtx_disp_start = self._io.read_f4le()
            self.f_vtx_disp_scale = self._io.read_f4le()
            self.f_vtx_disp_inv_area = self._io.read_f4le()
            self.f_vtx_disp_rcn = self._io.read_f4le()
            self.f_vtx_disp_tilt_u = self._io.read_f4le()
            self.f_vtx_disp_tilt_v = self._io.read_f4le()
            self.filler = []
            for i in range(2):
                self.filler.append(self._io.read_f4le())



    class CmdOfsBuffer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_float_buff = self._io.read_u4le()


    class StrCbVtxDistortionRefract(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_distortion_refract = self._io.read_f4le()
            self.filler = []
            for i in range(3):
                self.filler.append(self._io.read_f4le())



    class AnimType6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_00 = []
            for i in range(2):
                self.unk_00.append(self._io.read_u4le())

            self.unk_01 = []
            for i in range(4):
                self.unk_01.append(self._io.read_f4le())



    class AnimDataInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_bits_int_le(4)
            self.unk_00 = self._io.read_bits_int_le(4)
            self.num_entry = self._io.read_bits_int_le(24)


    class CbUnk04(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(16):
                self.data.append(self._io.read_f4le())



    class AnimSubEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.shader_hash = self._io.read_u4le()
            self.info = Mrl.AnimDataInfo(self._io, self, self._root)
            _on = self.info.type
            if _on == 0:
                self.entry = Mrl.AnimSubEntry0(self._io, self, self._root)
            elif _on == 4:
                self.entry = Mrl.AnimSubEntry4(self._io, self, self._root)
            elif _on == 6:
                self.entry = Mrl.AnimSubEntry6(self._io, self, self._root)
            elif _on == 7:
                self.entry = Mrl.AnimSubEntry7(self._io, self, self._root)
            elif _on == 1:
                self.entry = Mrl.AnimSubEntry1(self._io, self, self._root)
            elif _on == 3:
                self.entry = Mrl.AnimSubEntry3(self._io, self, self._root)
            elif _on == 5:
                self.entry = Mrl.AnimSubEntry5(self._io, self, self._root)
            elif _on == 2:
                self.entry = Mrl.AnimSubEntry2(self._io, self, self._root)


    class AnimSubEntry4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                self.values.append(Mrl.AnimType4(self._io, self, self._root))

            self.hash = []
            for i in range(self._parent.info.num_entry):
                self.hash.append(self._io.read_u4le())



    class CbUnk03(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(8):
                self.data.append(self._io.read_f4le())



    class StrCbColorMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_color_mask_threshold = []
            for i in range(4):
                self.f_color_mask_threshold.append(self._io.read_f4le())

            self.f_color_mask_offset = []
            for i in range(4):
                self.f_color_mask_offset.append(self._io.read_f4le())

            self.f_clip_threshold = []
            for i in range(4):
                self.f_clip_threshold.append(self._io.read_f4le())

            self.f_color_mask_color = []
            for i in range(4):
                self.f_color_mask_color.append(self._io.read_f4le())

            self.f_color_mask2_threshold = []
            for i in range(4):
                self.f_color_mask2_threshold.append(self._io.read_f4le())

            self.f_color_mask2_color = []
            for i in range(4):
                self.f_color_mask2_color.append(self._io.read_f4le())



    class StrRehdCbGlobals(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_alpha_clip_threshold = self._io.read_f4le()
            self.f_albedo_color = []
            for i in range(3):
                self.f_albedo_color.append(self._io.read_f4le())

            self.f_albedo_blend_color = []
            for i in range(4):
                self.f_albedo_blend_color.append(self._io.read_f4le())

            self.f_detail_normal_power = self._io.read_f4le()
            self.f_detail_normal_uv_scale = self._io.read_f4le()
            self.f_detail_normal2_power = self._io.read_f4le()
            self.f_detail_normal2_uv_scale = self._io.read_f4le()
            self.f_primary_shift = self._io.read_f4le()
            self.f_secondary_shift = self._io.read_f4le()
            self.f_parallax_factor = self._io.read_f4le()
            self.f_parallax_self_occlusion = self._io.read_f4le()
            self.f_parallax_min_sample = self._io.read_f4le()
            self.f_parallax_max_sample = []
            for i in range(3):
                self.f_parallax_max_sample.append(self._io.read_f4le())

            self.f_light_map_color = []
            for i in range(4):
                self.f_light_map_color.append(self._io.read_f4le())

            self.f_thin_map_color = []
            for i in range(3):
                self.f_thin_map_color.append(self._io.read_f4le())

            self.f_thin_scattering = self._io.read_f4le()
            self.f_screen_uv_scale = []
            for i in range(2):
                self.f_screen_uv_scale.append(self._io.read_f4le())

            self.f_screen_uv_offset = []
            for i in range(2):
                self.f_screen_uv_offset.append(self._io.read_f4le())

            self.f_indirect_offset = []
            for i in range(2):
                self.f_indirect_offset.append(self._io.read_f4le())

            self.f_indirect_scale = []
            for i in range(2):
                self.f_indirect_scale.append(self._io.read_f4le())

            self.f_fresnel_schlick = self._io.read_f4le()
            self.f_fresnel_schlick_rgb = []
            for i in range(3):
                self.f_fresnel_schlick_rgb.append(self._io.read_f4le())

            self.f_specular_color = []
            for i in range(3):
                self.f_specular_color.append(self._io.read_f4le())

            self.f_shininess = self._io.read_f4le()
            self.f_emission_color = []
            for i in range(4):
                self.f_emission_color.append(self._io.read_f4le())

            self.f_constant_color = []
            for i in range(4):
                self.f_constant_color.append(self._io.read_f4le())

            self.f_roughness = self._io.read_f4le()
            self.f_roughness_rgb = []
            for i in range(3):
                self.f_roughness_rgb.append(self._io.read_f4le())

            self.f_anisotoropic_direction = []
            for i in range(3):
                self.f_anisotoropic_direction.append(self._io.read_f4le())

            self.f_smoothness = self._io.read_f4le()
            self.f_anistropic_uv = []
            for i in range(2):
                self.f_anistropic_uv.append(self._io.read_f4le())

            self.f_primary_expo = self._io.read_f4le()
            self.f_secondary_expo = self._io.read_f4le()
            self.f_primary_color = []
            for i in range(4):
                self.f_primary_color.append(self._io.read_f4le())

            self.f_secondary_color = []
            for i in range(4):
                self.f_secondary_color.append(self._io.read_f4le())



    class Material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type_hash = self._io.read_u4le()
            self.name_hash_crcjam32 = self._io.read_u4le()
            self.cmd_buffer_size = self._io.read_u4le()
            self.blend_state_hash = self._io.read_u4le()
            self.depth_stencil_state_hash = self._io.read_u4le()
            self.rasterizer_state_hash = self._io.read_u4le()
            self.cmd_list_info = Mrl.HashBlock(self._io, self, self._root)
            self.material_info_flags = []
            for i in range(4):
                self.material_info_flags.append(self._io.read_u1())

            self.unk_nulls = []
            for i in range(4):
                self.unk_nulls.append(self._io.read_u4le())

            self.anim_data_size = self._io.read_u4le()
            self.ofs_cmd = self._io.read_u4le()
            self.ofs_anim_data = self._io.read_u4le()

        @property
        def resources(self):
            if hasattr(self, '_m_resources'):
                return self._m_resources

            _pos = self._io.pos()
            self._io.seek(self.ofs_cmd)
            self._m_resources = []
            for i in range(self.cmd_list_info.index):
                self._m_resources.append(Mrl.ResourceBinding(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_resources', None)

        @property
        def anims(self):
            if hasattr(self, '_m_anims'):
                return self._m_anims

            if self.anim_data_size != 0:
                _pos = self._io.pos()
                self._io.seek(self.ofs_anim_data)
                self._m_anims = Mrl.AnimData(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_anims', None)


    class AnimType1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = []
            for i in range(4):
                self.unk_01.append(self._io.read_f4le())



    class AnimSubEntry6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                self.values.append(Mrl.AnimType6(self._io, self, self._root))



    class StrCbVtxDisplacement2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.f_vtx_disp_start2 = self._io.read_f4le()
            self.f_vtx_disp_scales = self._io.read_f4le()
            self.f_vtx_disp_inv_area2 = self._io.read_f4le()
            self.f_vtx_disp_rcn2 = self._io.read_f4le()


    class AnimData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entry_count = self._io.read_u4le()
            self.ofs_to_info = []
            for i in range(self.entry_count):
                self.ofs_to_info.append(Mrl.AnimOfs(self._io, self, self._root))


        @property
        def ofs_base(self):
            if hasattr(self, '_m_ofs_base'):
                return self._m_ofs_base

            self._m_ofs_base = self._parent.ofs_anim_data
            return getattr(self, '_m_ofs_base', None)


    class OfsBuff(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_const_buff = self._io.read_u4le()


    class CbSGlobals(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(84):
                self.data.append(self._io.read_f4le())



    class TexOffset(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.texture_id = self._io.read_u4le()


    class AnimEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.info = Mrl.AnimInfo(self._io, self, self._root)
            self.ofs_list_entry1 = self._io.read_u4le()
            self.unk_hash = self._io.read_u4le()
            self.ofs_entry2 = []
            for i in range(self.info.num_entry2):
                self.ofs_entry2.append(Mrl.BlockOffset(self._io, self, self._root))

            self.set_buff_hash = []
            for i in range(self.info.num_entry1):
                self.set_buff_hash.append(self._io.read_u4le())



    class ResourceBinding(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.info = Mrl.CmdInfo(self._io, self, self._root)
            _on = self.info.cmd_type
            if _on == 0:
                self.value_cmd = Mrl.HashBlock(self._io, self, self._root)
            elif _on == 4:
                self.value_cmd = Mrl.HashBlock(self._io, self, self._root)
            elif _on == 1:
                self.value_cmd = Mrl.CmdOfsBuffer(self._io, self, self._root)
            elif _on == 3:
                self.value_cmd = Mrl.CmdTexIdx(self._io, self, self._root)
            elif _on == 2:
                self.value_cmd = Mrl.HashBlock(self._io, self, self._root)
            self.shader_object_hash = self._io.read_u4le()

        @property
        def float_buffer(self):
            if hasattr(self, '_m_float_buffer'):
                return self._m_float_buffer

            if self.info.cmd_type == 1:
                _pos = self._io.pos()
                self._io.seek((self._parent.ofs_cmd + self.value_cmd.ofs_float_buff))
                _on = self.shader_object_hash
                if _on == 1862361870:
                    self._m_float_buffer = Mrl.CbUnk02(self._io, self, self._root)
                elif _on == 4023005735:
                    self._m_float_buffer = Mrl.StrCbDistortion(self._io, self, self._root)
                elif _on == 579346993:
                    self._m_float_buffer = Mrl.StrCbVtxDisplacement3(self._io, self, self._root)
                elif _on == 4023005730:
                    self._m_float_buffer = Mrl.StrCbDistortion(self._io, self, self._root)
                elif _on == 1820332537:
                    self._m_float_buffer = Mrl.StrCbMaterial(self._io, self, self._root)
                elif _on == 4023005728:
                    self._m_float_buffer = Mrl.StrCbDistortion(self._io, self, self._root)
                elif _on == 1642345011:
                    self._m_float_buffer = Mrl.StrCbVtxDispEx(self._io, self, self._root)
                elif _on == 2215727888:
                    self._m_float_buffer = Mrl.CbUnk03(self._io, self, self._root)
                elif _on == 2934141708:
                    self._m_float_buffer = Mrl.CbUnk01(self._io, self, self._root)
                elif _on == 1367425584:
                    self._m_float_buffer = Mrl.StrCbVtxDisplacement2(self._io, self, self._root)
                elif _on == 3297735201:
                    self._m_float_buffer = Mrl.CbUnk01(self._io, self, self._root)
                elif _on == 579347000:
                    self._m_float_buffer = Mrl.StrCbVtxDisplacement3(self._io, self, self._root)
                elif _on == 1640423997:
                    self._m_float_buffer = Mrl.StrCbVtxDispMaskUv(self._io, self, self._root)
                elif _on == 2066489676:
                    self._m_float_buffer = Mrl.CbSGlobals(self._io, self, self._root)
                elif _on == 3297735212:
                    self._m_float_buffer = Mrl.StrCbVtxDistortionRefract(self._io, self, self._root)
                elif _on == 356618799:
                    self._m_float_buffer = Mrl.StrCbVtxDisplacement(self._io, self, self._root)
                elif _on == 2066489689:
                    self._m_float_buffer = Mrl.StrRehdCbGlobals(self._io, self, self._root)
                elif _on == 356618806:
                    self._m_float_buffer = Mrl.StrCbVtxDisplacement(self._io, self, self._root)
                elif _on == 2066489695:
                    self._m_float_buffer = Mrl.StrRehdCbGlobals(self._io, self, self._root)
                elif _on == 2934141721:
                    self._m_float_buffer = Mrl.StrCbBaAlphaClip(self._io, self, self._root)
                elif _on == 1862361883:
                    self._m_float_buffer = Mrl.StrCbColorMask(self._io, self, self._root)
                elif _on == 1820332522:
                    self._m_float_buffer = Mrl.StrCbMaterial(self._io, self, self._root)
                elif _on == 3297735208:
                    self._m_float_buffer = Mrl.StrCbVtxDistortionRefract(self._io, self, self._root)
                elif _on == 2066489694:
                    self._m_float_buffer = Mrl.StrRev2CbGlobals(self._io, self, self._root)
                elif _on == 1820332542:
                    self._m_float_buffer = Mrl.StrCbMaterial(self._io, self, self._root)
                elif _on == 4023005739:
                    self._m_float_buffer = Mrl.StrCbDistortion(self._io, self, self._root)
                elif _on == 2066489685:
                    self._m_float_buffer = Mrl.StrRehdCbGlobals(self._io, self, self._root)
                elif _on == 3297735203:
                    self._m_float_buffer = Mrl.StrCbVtxDistortionRefract(self._io, self, self._root)
                elif _on == 1820332532:
                    self._m_float_buffer = Mrl.StrCbMaterial(self._io, self, self._root)
                elif _on == 1820332544:
                    self._m_float_buffer = Mrl.StrCbMaterial(self._io, self, self._root)
                elif _on == 1367425591:
                    self._m_float_buffer = Mrl.StrCbVtxDisplacement2(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_float_buffer', None)


    class AnimSubEntry3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(24):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((16 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



    class AnimSubEntry2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())




