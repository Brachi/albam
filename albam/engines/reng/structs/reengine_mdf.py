# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineMdf(ReadWriteKaitaiStruct):
    def __init__(self, mdf_version, _io=None, _parent=None, _root=None):
        super(ReengineMdf, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self.mdf_version = mdf_version

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
            _t_materials = ReengineMdf.Material(self._io, self, self._root)
            try:
                _t_materials._read()
            finally:
                self.materials.append(_t_materials)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.materials)):
            pass
            self.materials[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(ReengineMdf, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u2le(self.unk_01)
        self._io.write_u2le(self.num_materials)
        self._io.write_u4le(self.unk_02)
        self._io.write_u4le(self.unk_03)
        for i in range(len(self.materials)):
            pass
            self.materials[i]._write__seq(self._io)



    def _check(self):
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x4D\x44\x46\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x44\x46\x00", self.id_magic, None, u"/seq/0")
        if len(self.materials) != self.num_materials:
            raise kaitaistruct.ConsistencyError(u"materials", self.num_materials, len(self.materials))
        for i in range(len(self.materials)):
            pass
            if self.materials[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"materials", self._root, self.materials[i]._root)
            if self.materials[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"materials", self, self.materials[i]._parent)

        self._dirty = False

    class AlphaFlags(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMdf.AlphaFlags, self).__init__(_io)
            self._parent = _parent
            self._root = _root

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
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMdf.AlphaFlags, self)._write__seq(io)
            self._io.write_bits_int_be(1, int(self.base_two_side_enable))
            self._io.write_bits_int_be(1, int(self.base_alpha_test_enable))
            self._io.write_bits_int_be(1, int(self.shadow_cast_disable))
            self._io.write_bits_int_be(1, int(self.vertex_shader_used))
            self._io.write_bits_int_be(1, int(self.emissive_used))
            self._io.write_bits_int_be(1, int(self.tessellation_enable))
            self._io.write_bits_int_be(1, int(self.enable_ignore_depth))
            self._io.write_bits_int_be(1, int(self.alpha_mask_used))
            self._io.write_bits_int_be(1, int(self.forced_two_side_enable))
            self._io.write_bits_int_be(1, int(self.two_side_enable))
            self._io.write_bits_int_be(6, self.tess_factor)
            self._io.write_bits_int_be(1, int(self.phong_factor))
            self._io.write_bits_int_be(1, int(self.rough_transparent_enable))
            self._io.write_bits_int_be(1, int(self.forced_alpha_test_enable))
            self._io.write_bits_int_be(1, int(self.alpha_test_enable))
            self._io.write_bits_int_be(1, int(self.sss_profile_used))
            self._io.write_bits_int_be(1, int(self.enable_stencil_priority))
            self._io.write_bits_int_be(1, int(self.require_dual_quaternion))
            self._io.write_bits_int_be(1, int(self.pixel_depth_offset_used))
            self._io.write_bits_int_be(1, int(self.no_ray_tracing))
            self._io.write_bits_int_be(7, self.unk_01)


        def _check(self):
            self._dirty = False


    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMdf.Material, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_master_material_path = False
            self.master_material_path__enabled = True
            self._should_write_master_material_path_raw = False
            self.master_material_path_raw__enabled = True
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_name_raw = False
            self.name_raw__enabled = True
            self._should_write_properties_headers = False
            self.properties_headers__enabled = True
            self._should_write_textures = False
            self.textures__enabled = True

        def _read(self):
            self.ofs_material_name = self._io.read_u8le()
            self.hash = self._io.read_u4le()
            self.size_properties = self._io.read_u4le()
            self.num_properties_headers = self._io.read_u4le()
            self.num_textures = self._io.read_u4le()
            if self._root.mdf_version >= 19:
                pass
                self.unk_01 = self._io.read_u8le()

            self.material_shading_type = self._io.read_u4le()
            self.alpha_flags = ReengineMdf.AlphaFlags(self._io, self, self._root)
            self.alpha_flags._read()
            self.ofs_properties_headers = self._io.read_u8le()
            self.ofs_texture_headers = self._io.read_u8le()
            if self._root.mdf_version >= 19:
                pass
                self.ofs_first_material_name = self._io.read_u8le()

            self.ofs_properties = self._io.read_u8le()
            self.ofs_master_material_path = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.mdf_version >= 19:
                pass

            self.alpha_flags._fetch_instances()
            if self._root.mdf_version >= 19:
                pass

            _ = self.master_material_path
            if hasattr(self, '_m_master_material_path'):
                pass

            _ = self.master_material_path_raw
            if hasattr(self, '_m_master_material_path_raw'):
                pass
                for i in range(len(self._m_master_material_path_raw)):
                    pass


            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.name_raw
            if hasattr(self, '_m_name_raw'):
                pass
                for i in range(len(self._m_name_raw)):
                    pass


            _ = self.properties_headers
            if hasattr(self, '_m_properties_headers'):
                pass
                for i in range(len(self._m_properties_headers)):
                    pass
                    _on = self._root.mdf_version
                    if _on == 10:
                        pass
                        self._m_properties_headers[i]._fetch_instances()
                    elif _on == 13:
                        pass
                        self._m_properties_headers[i]._fetch_instances()
                    elif _on == 21:
                        pass
                        self._m_properties_headers[i]._fetch_instances()


            _ = self.textures
            if hasattr(self, '_m_textures'):
                pass
                for i in range(len(self._m_textures)):
                    pass
                    self._m_textures[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(ReengineMdf.Material, self)._write__seq(io)
            self._should_write_master_material_path = self.master_material_path__enabled
            self._should_write_master_material_path_raw = self.master_material_path_raw__enabled
            self._should_write_name = self.name__enabled
            self._should_write_name_raw = self.name_raw__enabled
            self._should_write_properties_headers = self.properties_headers__enabled
            self._should_write_textures = self.textures__enabled
            self._io.write_u8le(self.ofs_material_name)
            self._io.write_u4le(self.hash)
            self._io.write_u4le(self.size_properties)
            self._io.write_u4le(self.num_properties_headers)
            self._io.write_u4le(self.num_textures)
            if self._root.mdf_version >= 19:
                pass
                self._io.write_u8le(self.unk_01)

            self._io.write_u4le(self.material_shading_type)
            self.alpha_flags._write__seq(self._io)
            self._io.write_u8le(self.ofs_properties_headers)
            self._io.write_u8le(self.ofs_texture_headers)
            if self._root.mdf_version >= 19:
                pass
                self._io.write_u8le(self.ofs_first_material_name)

            self._io.write_u8le(self.ofs_properties)
            self._io.write_u8le(self.ofs_master_material_path)


        def _check(self):
            if self._root.mdf_version >= 19:
                pass

            if self.alpha_flags._root != self._root:
                raise kaitaistruct.ConsistencyError(u"alpha_flags", self._root, self.alpha_flags._root)
            if self.alpha_flags._parent != self:
                raise kaitaistruct.ConsistencyError(u"alpha_flags", self, self.alpha_flags._parent)
            if self._root.mdf_version >= 19:
                pass

            if self.master_material_path__enabled:
                pass

            if self.master_material_path_raw__enabled:
                pass
                if len(self._m_master_material_path_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"master_material_path_raw", 0, len(self._m_master_material_path_raw))
                for i in range(len(self._m_master_material_path_raw)):
                    pass
                    _ = self._m_master_material_path_raw[i]
                    if (_ == 0) != (i == len(self._m_master_material_path_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"master_material_path_raw", i == len(self._m_master_material_path_raw) - 1, _ == 0)


            if self.name__enabled:
                pass

            if self.name_raw__enabled:
                pass
                if len(self._m_name_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"name_raw", 0, len(self._m_name_raw))
                for i in range(len(self._m_name_raw)):
                    pass
                    _ = self._m_name_raw[i]
                    if (_ == 0) != (i == len(self._m_name_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"name_raw", i == len(self._m_name_raw) - 1, _ == 0)


            if self.properties_headers__enabled:
                pass
                if len(self._m_properties_headers) != self.num_properties_headers:
                    raise kaitaistruct.ConsistencyError(u"properties_headers", self.num_properties_headers, len(self._m_properties_headers))
                for i in range(len(self._m_properties_headers)):
                    pass
                    _on = self._root.mdf_version
                    if _on == 10:
                        pass
                        if self._m_properties_headers[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"properties_headers", self._root, self._m_properties_headers[i]._root)
                        if self._m_properties_headers[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"properties_headers", self, self._m_properties_headers[i]._parent)
                    elif _on == 13:
                        pass
                        if self._m_properties_headers[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"properties_headers", self._root, self._m_properties_headers[i]._root)
                        if self._m_properties_headers[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"properties_headers", self, self._m_properties_headers[i]._parent)
                    elif _on == 21:
                        pass
                        if self._m_properties_headers[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"properties_headers", self._root, self._m_properties_headers[i]._root)
                        if self._m_properties_headers[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"properties_headers", self, self._m_properties_headers[i]._parent)


            if self.textures__enabled:
                pass
                if len(self._m_textures) != self.num_textures:
                    raise kaitaistruct.ConsistencyError(u"textures", self.num_textures, len(self._m_textures))
                for i in range(len(self._m_textures)):
                    pass
                    if self._m_textures[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"textures", self._root, self._m_textures[i]._root)
                    if self._m_textures[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"textures", self, self._m_textures[i]._parent)


            self._dirty = False

        @property
        def master_material_path(self):
            if self._should_write_master_material_path:
                self._write_master_material_path()
            if hasattr(self, '_m_master_material_path'):
                return self._m_master_material_path

            if not self.master_material_path__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_master_material_path)
            self._m_master_material_path = (self._io.read_bytes(len(self.master_material_path_raw) * 2 - 2)).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_master_material_path', None)

        @master_material_path.setter
        def master_material_path(self, v):
            self._dirty = True
            self._m_master_material_path = v

        def _write_master_material_path(self):
            self._should_write_master_material_path = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_master_material_path)
            if len((self._m_master_material_path).encode(u"utf-16")) != len(self.master_material_path_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"master_material_path", len(self.master_material_path_raw) * 2 - 2, len((self._m_master_material_path).encode(u"utf-16")))
            self._io.write_bytes((self._m_master_material_path).encode(u"utf-16"))
            self._io.seek(_pos)

        @property
        def master_material_path_raw(self):
            if self._should_write_master_material_path_raw:
                self._write_master_material_path_raw()
            if hasattr(self, '_m_master_material_path_raw'):
                return self._m_master_material_path_raw

            if not self.master_material_path_raw__enabled:
                return None

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

        @master_material_path_raw.setter
        def master_material_path_raw(self, v):
            self._dirty = True
            self._m_master_material_path_raw = v

        def _write_master_material_path_raw(self):
            self._should_write_master_material_path_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_master_material_path)
            for i in range(len(self._m_master_material_path_raw)):
                pass
                self._io.write_u2le(self._m_master_material_path_raw[i])

            self._io.seek(_pos)

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_material_name)
            self._m_name = (self._io.read_bytes(len(self.name_raw) * 2 - 2)).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_material_name)
            if len((self._m_name).encode(u"utf-16")) != len(self.name_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"name", len(self.name_raw) * 2 - 2, len((self._m_name).encode(u"utf-16")))
            self._io.write_bytes((self._m_name).encode(u"utf-16"))
            self._io.seek(_pos)

        @property
        def name_raw(self):
            if self._should_write_name_raw:
                self._write_name_raw()
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            if not self.name_raw__enabled:
                return None

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

        @name_raw.setter
        def name_raw(self, v):
            self._dirty = True
            self._m_name_raw = v

        def _write_name_raw(self):
            self._should_write_name_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_material_name)
            for i in range(len(self._m_name_raw)):
                pass
                self._io.write_u2le(self._m_name_raw[i])

            self._io.seek(_pos)

        @property
        def properties_headers(self):
            if self._should_write_properties_headers:
                self._write_properties_headers()
            if hasattr(self, '_m_properties_headers'):
                return self._m_properties_headers

            if not self.properties_headers__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_properties_headers)
            self._m_properties_headers = []
            for i in range(self.num_properties_headers):
                _on = self._root.mdf_version
                if _on == 10:
                    pass
                    _t__m_properties_headers = ReengineMdf.PropertiesHeader10(self._io, self, self._root)
                    try:
                        _t__m_properties_headers._read()
                    finally:
                        self._m_properties_headers.append(_t__m_properties_headers)
                elif _on == 13:
                    pass
                    _t__m_properties_headers = ReengineMdf.PropertiesHeader13(self._io, self, self._root)
                    try:
                        _t__m_properties_headers._read()
                    finally:
                        self._m_properties_headers.append(_t__m_properties_headers)
                elif _on == 21:
                    pass
                    _t__m_properties_headers = ReengineMdf.PropertiesHeader13(self._io, self, self._root)
                    try:
                        _t__m_properties_headers._read()
                    finally:
                        self._m_properties_headers.append(_t__m_properties_headers)

            self._io.seek(_pos)
            return getattr(self, '_m_properties_headers', None)

        @properties_headers.setter
        def properties_headers(self, v):
            self._dirty = True
            self._m_properties_headers = v

        def _write_properties_headers(self):
            self._should_write_properties_headers = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_properties_headers)
            for i in range(len(self._m_properties_headers)):
                pass
                _on = self._root.mdf_version
                if _on == 10:
                    pass
                    self._m_properties_headers[i]._write__seq(self._io)
                elif _on == 13:
                    pass
                    self._m_properties_headers[i]._write__seq(self._io)
                elif _on == 21:
                    pass
                    self._m_properties_headers[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def textures(self):
            if self._should_write_textures:
                self._write_textures()
            if hasattr(self, '_m_textures'):
                return self._m_textures

            if not self.textures__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_headers)
            self._m_textures = []
            for i in range(self.num_textures):
                _t__m_textures = ReengineMdf.TextureHeader(self._io, self, self._root)
                try:
                    _t__m_textures._read()
                finally:
                    self._m_textures.append(_t__m_textures)

            self._io.seek(_pos)
            return getattr(self, '_m_textures', None)

        @textures.setter
        def textures(self, v):
            self._dirty = True
            self._m_textures = v

        def _write_textures(self):
            self._should_write_textures = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_headers)
            for i in range(len(self._m_textures)):
                pass
                self._m_textures[i]._write__seq(self._io)

            self._io.seek(_pos)


    class PropertiesHeader10(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMdf.PropertiesHeader10, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_name_raw = False
            self.name_raw__enabled = True
            self._should_write_params = False
            self.params__enabled = True

        def _read(self):
            self.ofs_name = self._io.read_u8le()
            self.name_hash_utf16 = self._io.read_u4le()
            self.name_hash_ascii = self._io.read_u4le()
            self.num_params = self._io.read_u4le()
            self.ofs_prop = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.name_raw
            if hasattr(self, '_m_name_raw'):
                pass
                for i in range(len(self._m_name_raw)):
                    pass


            _ = self.params
            if hasattr(self, '_m_params'):
                pass
                for i in range(len(self._m_params)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMdf.PropertiesHeader10, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._should_write_name_raw = self.name_raw__enabled
            self._should_write_params = self.params__enabled
            self._io.write_u8le(self.ofs_name)
            self._io.write_u4le(self.name_hash_utf16)
            self._io.write_u4le(self.name_hash_ascii)
            self._io.write_u4le(self.num_params)
            self._io.write_u4le(self.ofs_prop)


        def _check(self):
            if self.name__enabled:
                pass

            if self.name_raw__enabled:
                pass
                if len(self._m_name_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"name_raw", 0, len(self._m_name_raw))
                for i in range(len(self._m_name_raw)):
                    pass
                    _ = self._m_name_raw[i]
                    if (_ == 0) != (i == len(self._m_name_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"name_raw", i == len(self._m_name_raw) - 1, _ == 0)


            if self.params__enabled:
                pass
                if len(self._m_params) != self.num_params:
                    raise kaitaistruct.ConsistencyError(u"params", self.num_params, len(self._m_params))
                for i in range(len(self._m_params)):
                    pass


            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name = (self._io.read_bytes(len(self.name_raw) * 2 - 2)).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            if len((self._m_name).encode(u"utf-16")) != len(self.name_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"name", len(self.name_raw) * 2 - 2, len((self._m_name).encode(u"utf-16")))
            self._io.write_bytes((self._m_name).encode(u"utf-16"))
            self._io.seek(_pos)

        @property
        def name_raw(self):
            if self._should_write_name_raw:
                self._write_name_raw()
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            if not self.name_raw__enabled:
                return None

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

        @name_raw.setter
        def name_raw(self, v):
            self._dirty = True
            self._m_name_raw = v

        def _write_name_raw(self):
            self._should_write_name_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            for i in range(len(self._m_name_raw)):
                pass
                self._io.write_u2le(self._m_name_raw[i])

            self._io.seek(_pos)

        @property
        def params(self):
            if self._should_write_params:
                self._write_params()
            if hasattr(self, '_m_params'):
                return self._m_params

            if not self.params__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._parent.ofs_properties + self.ofs_prop)
            self._m_params = []
            for i in range(self.num_params):
                self._m_params.append(self._io.read_f4le())

            self._io.seek(_pos)
            return getattr(self, '_m_params', None)

        @params.setter
        def params(self, v):
            self._dirty = True
            self._m_params = v

        def _write_params(self):
            self._should_write_params = False
            _pos = self._io.pos()
            self._io.seek(self._parent.ofs_properties + self.ofs_prop)
            for i in range(len(self._m_params)):
                pass
                self._io.write_f4le(self._m_params[i])

            self._io.seek(_pos)


    class PropertiesHeader13(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMdf.PropertiesHeader13, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_name_raw = False
            self.name_raw__enabled = True
            self._should_write_params = False
            self.params__enabled = True

        def _read(self):
            self.ofs_name = self._io.read_u8le()
            self.name_hash_utf16 = self._io.read_u4le()
            self.name_hash_ascii = self._io.read_u4le()
            self.ofs_prop = self._io.read_u4le()
            self.num_params = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.name_raw
            if hasattr(self, '_m_name_raw'):
                pass
                for i in range(len(self._m_name_raw)):
                    pass


            _ = self.params
            if hasattr(self, '_m_params'):
                pass
                for i in range(len(self._m_params)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMdf.PropertiesHeader13, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._should_write_name_raw = self.name_raw__enabled
            self._should_write_params = self.params__enabled
            self._io.write_u8le(self.ofs_name)
            self._io.write_u4le(self.name_hash_utf16)
            self._io.write_u4le(self.name_hash_ascii)
            self._io.write_u4le(self.ofs_prop)
            self._io.write_u4le(self.num_params)


        def _check(self):
            if self.name__enabled:
                pass

            if self.name_raw__enabled:
                pass
                if len(self._m_name_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"name_raw", 0, len(self._m_name_raw))
                for i in range(len(self._m_name_raw)):
                    pass
                    _ = self._m_name_raw[i]
                    if (_ == 0) != (i == len(self._m_name_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"name_raw", i == len(self._m_name_raw) - 1, _ == 0)


            if self.params__enabled:
                pass
                if len(self._m_params) != self.num_params:
                    raise kaitaistruct.ConsistencyError(u"params", self.num_params, len(self._m_params))
                for i in range(len(self._m_params)):
                    pass


            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name = (self._io.read_bytes(len(self.name_raw) * 2 - 2)).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            if len((self._m_name).encode(u"utf-16")) != len(self.name_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"name", len(self.name_raw) * 2 - 2, len((self._m_name).encode(u"utf-16")))
            self._io.write_bytes((self._m_name).encode(u"utf-16"))
            self._io.seek(_pos)

        @property
        def name_raw(self):
            if self._should_write_name_raw:
                self._write_name_raw()
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            if not self.name_raw__enabled:
                return None

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

        @name_raw.setter
        def name_raw(self, v):
            self._dirty = True
            self._m_name_raw = v

        def _write_name_raw(self):
            self._should_write_name_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            for i in range(len(self._m_name_raw)):
                pass
                self._io.write_u2le(self._m_name_raw[i])

            self._io.seek(_pos)

        @property
        def params(self):
            if self._should_write_params:
                self._write_params()
            if hasattr(self, '_m_params'):
                return self._m_params

            if not self.params__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._parent.ofs_properties + self.ofs_prop)
            self._m_params = []
            for i in range(self.num_params):
                self._m_params.append(self._io.read_f4le())

            self._io.seek(_pos)
            return getattr(self, '_m_params', None)

        @params.setter
        def params(self, v):
            self._dirty = True
            self._m_params = v

        def _write_params(self):
            self._should_write_params = False
            _pos = self._io.pos()
            self._io.seek(self._parent.ofs_properties + self.ofs_prop)
            for i in range(len(self._m_params)):
                pass
                self._io.write_f4le(self._m_params[i])

            self._io.seek(_pos)


    class TextureHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMdf.TextureHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_texture_path = False
            self.texture_path__enabled = True
            self._should_write_texture_path_raw = False
            self.texture_path_raw__enabled = True
            self._should_write_texture_type = False
            self.texture_type__enabled = True
            self._should_write_texture_type_raw = False
            self.texture_type_raw__enabled = True

        def _read(self):
            self.ofs_texture_type = self._io.read_u8le()
            self.hash_utf16 = self._io.read_u4le()
            self.hash_ascii = self._io.read_u4le()
            self.ofs_texture_path = self._io.read_u8le()
            if self._root.mdf_version >= 13:
                pass
                self.unk_01 = self._io.read_u8le()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.mdf_version >= 13:
                pass

            _ = self.texture_path
            if hasattr(self, '_m_texture_path'):
                pass

            _ = self.texture_path_raw
            if hasattr(self, '_m_texture_path_raw'):
                pass
                for i in range(len(self._m_texture_path_raw)):
                    pass


            _ = self.texture_type
            if hasattr(self, '_m_texture_type'):
                pass

            _ = self.texture_type_raw
            if hasattr(self, '_m_texture_type_raw'):
                pass
                for i in range(len(self._m_texture_type_raw)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMdf.TextureHeader, self)._write__seq(io)
            self._should_write_texture_path = self.texture_path__enabled
            self._should_write_texture_path_raw = self.texture_path_raw__enabled
            self._should_write_texture_type = self.texture_type__enabled
            self._should_write_texture_type_raw = self.texture_type_raw__enabled
            self._io.write_u8le(self.ofs_texture_type)
            self._io.write_u4le(self.hash_utf16)
            self._io.write_u4le(self.hash_ascii)
            self._io.write_u8le(self.ofs_texture_path)
            if self._root.mdf_version >= 13:
                pass
                self._io.write_u8le(self.unk_01)



        def _check(self):
            if self._root.mdf_version >= 13:
                pass

            if self.texture_path__enabled:
                pass

            if self.texture_path_raw__enabled:
                pass
                if len(self._m_texture_path_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"texture_path_raw", 0, len(self._m_texture_path_raw))
                for i in range(len(self._m_texture_path_raw)):
                    pass
                    _ = self._m_texture_path_raw[i]
                    if (_ == 0) != (i == len(self._m_texture_path_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"texture_path_raw", i == len(self._m_texture_path_raw) - 1, _ == 0)


            if self.texture_type__enabled:
                pass

            if self.texture_type_raw__enabled:
                pass
                if len(self._m_texture_type_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"texture_type_raw", 0, len(self._m_texture_type_raw))
                for i in range(len(self._m_texture_type_raw)):
                    pass
                    _ = self._m_texture_type_raw[i]
                    if (_ == 0) != (i == len(self._m_texture_type_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"texture_type_raw", i == len(self._m_texture_type_raw) - 1, _ == 0)


            self._dirty = False

        @property
        def texture_path(self):
            if self._should_write_texture_path:
                self._write_texture_path()
            if hasattr(self, '_m_texture_path'):
                return self._m_texture_path

            if not self.texture_path__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_path)
            self._m_texture_path = (self._io.read_bytes(len(self.texture_path_raw) * 2 - 2)).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_texture_path', None)

        @texture_path.setter
        def texture_path(self, v):
            self._dirty = True
            self._m_texture_path = v

        def _write_texture_path(self):
            self._should_write_texture_path = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_path)
            if len((self._m_texture_path).encode(u"utf-16")) != len(self.texture_path_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"texture_path", len(self.texture_path_raw) * 2 - 2, len((self._m_texture_path).encode(u"utf-16")))
            self._io.write_bytes((self._m_texture_path).encode(u"utf-16"))
            self._io.seek(_pos)

        @property
        def texture_path_raw(self):
            if self._should_write_texture_path_raw:
                self._write_texture_path_raw()
            if hasattr(self, '_m_texture_path_raw'):
                return self._m_texture_path_raw

            if not self.texture_path_raw__enabled:
                return None

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

        @texture_path_raw.setter
        def texture_path_raw(self, v):
            self._dirty = True
            self._m_texture_path_raw = v

        def _write_texture_path_raw(self):
            self._should_write_texture_path_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_path)
            for i in range(len(self._m_texture_path_raw)):
                pass
                self._io.write_u2le(self._m_texture_path_raw[i])

            self._io.seek(_pos)

        @property
        def texture_type(self):
            if self._should_write_texture_type:
                self._write_texture_type()
            if hasattr(self, '_m_texture_type'):
                return self._m_texture_type

            if not self.texture_type__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_type)
            self._m_texture_type = (self._io.read_bytes(len(self.texture_type_raw) * 2 - 2)).decode(u"utf-16")
            self._io.seek(_pos)
            return getattr(self, '_m_texture_type', None)

        @texture_type.setter
        def texture_type(self, v):
            self._dirty = True
            self._m_texture_type = v

        def _write_texture_type(self):
            self._should_write_texture_type = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_type)
            if len((self._m_texture_type).encode(u"utf-16")) != len(self.texture_type_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"texture_type", len(self.texture_type_raw) * 2 - 2, len((self._m_texture_type).encode(u"utf-16")))
            self._io.write_bytes((self._m_texture_type).encode(u"utf-16"))
            self._io.seek(_pos)

        @property
        def texture_type_raw(self):
            if self._should_write_texture_type_raw:
                self._write_texture_type_raw()
            if hasattr(self, '_m_texture_type_raw'):
                return self._m_texture_type_raw

            if not self.texture_type_raw__enabled:
                return None

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

        @texture_type_raw.setter
        def texture_type_raw(self, v):
            self._dirty = True
            self._m_texture_type_raw = v

        def _write_texture_type_raw(self):
            self._should_write_texture_type_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_texture_type)
            for i in range(len(self._m_texture_type_raw)):
                pass
                self._io.write_u2le(self._m_texture_type_raw[i])

            self._io.seek(_pos)



