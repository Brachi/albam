# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineMdf(KaitaiStruct):
    def __init__(self, mdf_version, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self.mdf_version = mdf_version
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x44\x46\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x44\x46\x00", self.id_magic, self._io, u"/seq/0")
        self.unk_01 = self._io.read_u2le()
        self.num_materials = self._io.read_u2le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.materials = []
        for i in range(self.num_materials):
            self.materials.append(ReengineMdf.Material(self._io, self, self._root))


    class TextureHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_texture_type = self._io.read_u8le()
            self.hash_utf16 = self._io.read_u4le()
            self.hash_ascii = self._io.read_u4le()
            self.ofs_texture_path = self._io.read_u8le()
            if self._root.mdf_version >= 13:
                self.unk_01 = self._io.read_u8le()


        @property
        def texture_type_raw(self):
            if hasattr(self, '_m_texture_type_raw'):
                return self._m_texture_type_raw

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_type)
            self._m_texture_type_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_texture_type_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_texture_type_raw', None)

        @property
        def texture_path_raw(self):
            if hasattr(self, '_m_texture_path_raw'):
                return self._m_texture_path_raw

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_path)
            self._m_texture_path_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_texture_path_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_texture_path_raw', None)

        @property
        def texture_type(self):
            if hasattr(self, '_m_texture_type'):
                return self._m_texture_type

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_type)
            self._m_texture_type = (self._io.read_bytes(((len(self.texture_type_raw) * 2) - 2))).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_texture_type', None)

        @property
        def texture_path(self):
            if hasattr(self, '_m_texture_path'):
                return self._m_texture_path

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_path)
            self._m_texture_path = (self._io.read_bytes(((len(self.texture_path_raw) * 2) - 2))).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_texture_path', None)


    class PropertiesHeader10(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_name = self._io.read_u8le()
            self.name_hash_utf16 = self._io.read_u4le()
            self.name_hash_ascii = self._io.read_u4le()
            self.num_params = self._io.read_u4le()
            self.ofs_prop = self._io.read_u4le()

        @property
        def name_raw(self):
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_name_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_name_raw', None)

        @property
        def params(self):
            if hasattr(self, '_m_params'):
                return self._m_params

            _pos = self._io.pos()
            self._io.seek((self._parent.ofs_properties + self.ofs_prop))
            self._m_params = []
            for i in range(self.num_params):
                self._m_params.append(self._io.read_f4le())

            self._io.seek(_pos)
            return getattr(self, '_m_params', None)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name = (self._io.read_bytes(((len(self.name_raw) * 2) - 2))).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    class PropertiesHeader13(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_name = self._io.read_u8le()
            self.name_hash_utf16 = self._io.read_u4le()
            self.name_hash_ascii = self._io.read_u4le()
            self.ofs_prop = self._io.read_u4le()
            self.num_params = self._io.read_u4le()

        @property
        def name_raw(self):
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_name_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_name_raw', None)

        @property
        def params(self):
            if hasattr(self, '_m_params'):
                return self._m_params

            _pos = self._io.pos()
            self._io.seek((self._parent.ofs_properties + self.ofs_prop))
            self._m_params = []
            for i in range(self.num_params):
                self._m_params.append(self._io.read_f4le())

            self._io.seek(_pos)
            return getattr(self, '_m_params', None)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name = (self._io.read_bytes(((len(self.name_raw) * 2) - 2))).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    class AlphaFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.base_two_side_enable = self._io.read_bits_int_be(1) != 0
            self.base_alpha_test_enable = self._io.read_bits_int_be(1) != 0
            self.shadow_cast_disable = self._io.read_bits_int_be(1) != 0
            self.vertex_shader_used = self._io.read_bits_int_be(1) != 0
            self.emissive_used = self._io.read_bits_int_be(1) != 0
            self.tessellation_enable = self._io.read_bits_int_be(1) != 0
            self.enable_ignore_depth = self._io.read_bits_int_be(1) != 0
            self.alpha_mask_used = self._io.read_bits_int_be(1) != 0
            self.forced_two_side_enable = self._io.read_bits_int_be(1) != 0
            self.two_side_enable = self._io.read_bits_int_be(1) != 0
            self.tess_factor = self._io.read_bits_int_be(6)
            self.phong_factor = self._io.read_bits_int_be(1) != 0
            self.rough_transparent_enable = self._io.read_bits_int_be(1) != 0
            self.forced_alpha_test_enable = self._io.read_bits_int_be(1) != 0
            self.alpha_test_enable = self._io.read_bits_int_be(1) != 0
            self.sss_profile_used = self._io.read_bits_int_be(1) != 0
            self.enable_stencil_priority = self._io.read_bits_int_be(1) != 0
            self.require_dual_quaternion = self._io.read_bits_int_be(1) != 0
            self.pixel_depth_offset_used = self._io.read_bits_int_be(1) != 0
            self.no_ray_tracing = self._io.read_bits_int_be(1) != 0
            self.unk_01 = self._io.read_bits_int_be(7)


    class Material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_material_name = self._io.read_u8le()
            self.hash = self._io.read_u4le()
            self.size_properties = self._io.read_u4le()
            self.num_properties_headers = self._io.read_u4le()
            self.num_textures = self._io.read_u4le()
            if self._root.mdf_version >= 19:
                self.unk_01 = self._io.read_u8le()

            self.material_shading_type = self._io.read_u4le()
            self.alpha_flags = ReengineMdf.AlphaFlags(self._io, self, self._root)
            self.ofs_properties_headers = self._io.read_u8le()
            self.ofs_texture_headers = self._io.read_u8le()
            if self._root.mdf_version >= 19:
                self.ofs_first_material_name = self._io.read_u8le()

            self.ofs_properties = self._io.read_u8le()
            self.ofs_master_material_path = self._io.read_u8le()

        @property
        def master_material_path(self):
            if hasattr(self, '_m_master_material_path'):
                return self._m_master_material_path

            _pos = self._io.pos()
            self._io.seek(self.ofs_master_material_path)
            self._m_master_material_path = (self._io.read_bytes(((len(self.master_material_path_raw) * 2) - 2))).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_master_material_path', None)

        @property
        def properties_headers(self):
            if hasattr(self, '_m_properties_headers'):
                return self._m_properties_headers

            _pos = self._io.pos()
            self._io.seek(self.ofs_properties_headers)
            self._m_properties_headers = []
            for i in range(self.num_properties_headers):
                _on = self._root.mdf_version
                if _on == 10:
                    self._m_properties_headers.append(ReengineMdf.PropertiesHeader10(self._io, self, self._root))
                elif _on == 13:
                    self._m_properties_headers.append(ReengineMdf.PropertiesHeader13(self._io, self, self._root))
                elif _on == 21:
                    self._m_properties_headers.append(ReengineMdf.PropertiesHeader13(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_properties_headers', None)

        @property
        def master_material_path_raw(self):
            if hasattr(self, '_m_master_material_path_raw'):
                return self._m_master_material_path_raw

            _pos = self._io.pos()
            self._io.seek(self.ofs_master_material_path)
            self._m_master_material_path_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_master_material_path_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_master_material_path_raw', None)

        @property
        def textures(self):
            if hasattr(self, '_m_textures'):
                return self._m_textures

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_headers)
            self._m_textures = []
            for i in range(self.num_textures):
                self._m_textures.append(ReengineMdf.TextureHeader(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_textures', None)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek(self.ofs_material_name)
            self._m_name = (self._io.read_bytes(((len(self.name_raw) * 2) - 2))).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @property
        def name_raw(self):
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            _pos = self._io.pos()
            self._io.seek(self.ofs_material_name)
            self._m_name_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_name_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_name_raw', None)



