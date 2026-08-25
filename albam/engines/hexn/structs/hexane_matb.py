# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneMatb(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(HexaneMatb, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_params_table = False
        self.params_table__enabled = True
        self._should_write_shader = False
        self.shader__enabled = True
        self._should_write_textures_table = False
        self.textures_table__enabled = True

    def _read(self):
        self.id_magic = self._io.read_bytes(3)
        if not self.id_magic == b"\x4D\x41\x54":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x41\x54", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u1()
        self.ofs_names = self._io.read_u4le()
        self.num_textures = self._io.read_u4le()
        self.num_params = self._io.read_u4le()
        self.header_size = self._io.read_u4le()
        self.ofs_params = self._io.read_u4le()
        self.extra_flags = []
        for i in range((self.header_size - 24) // 4):
            self.extra_flags.append(self._io.read_u4le())

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.extra_flags)):
            pass

        _ = self.params_table
        if hasattr(self, '_m_params_table'):
            pass
            for i in range(len(self._m_params_table)):
                pass
                self._m_params_table[i]._fetch_instances()


        _ = self.shader
        if hasattr(self, '_m_shader'):
            pass
            self._m_shader._fetch_instances()

        _ = self.textures_table
        if hasattr(self, '_m_textures_table'):
            pass
            for i in range(len(self._m_textures_table)):
                pass
                self._m_textures_table[i]._fetch_instances()




    def _write__seq(self, io=None):
        super(HexaneMatb, self)._write__seq(io)
        self._should_write_params_table = self.params_table__enabled
        self._should_write_shader = self.shader__enabled
        self._should_write_textures_table = self.textures_table__enabled
        self._io.write_bytes(self.id_magic)
        self._io.write_u1(self.version)
        self._io.write_u4le(self.ofs_names)
        self._io.write_u4le(self.num_textures)
        self._io.write_u4le(self.num_params)
        self._io.write_u4le(self.header_size)
        self._io.write_u4le(self.ofs_params)
        for i in range(len(self.extra_flags)):
            pass
            self._io.write_u4le(self.extra_flags[i])



    def _check(self):
        if len(self.id_magic) != 3:
            raise kaitaistruct.ConsistencyError(u"id_magic", 3, len(self.id_magic))
        if not self.id_magic == b"\x4D\x41\x54":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x41\x54", self.id_magic, None, u"/seq/0")
        if len(self.extra_flags) != (self.header_size - 24) // 4:
            raise kaitaistruct.ConsistencyError(u"extra_flags", (self.header_size - 24) // 4, len(self.extra_flags))
        for i in range(len(self.extra_flags)):
            pass

        if self.params_table__enabled:
            pass
            if len(self._m_params_table) != self.num_params:
                raise kaitaistruct.ConsistencyError(u"params_table", self.num_params, len(self._m_params_table))
            for i in range(len(self._m_params_table)):
                pass
                if self._m_params_table[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"params_table", self._root, self._m_params_table[i]._root)
                if self._m_params_table[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"params_table", self, self._m_params_table[i]._parent)


        if self.shader__enabled:
            pass
            if self._m_shader._root != self._root:
                raise kaitaistruct.ConsistencyError(u"shader", self._root, self._m_shader._root)
            if self._m_shader._parent != self:
                raise kaitaistruct.ConsistencyError(u"shader", self, self._m_shader._parent)

        if self.textures_table__enabled:
            pass
            if len(self._m_textures_table) != self.num_textures:
                raise kaitaistruct.ConsistencyError(u"textures_table", self.num_textures, len(self._m_textures_table))
            for i in range(len(self._m_textures_table)):
                pass
                if self._m_textures_table[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"textures_table", self._root, self._m_textures_table[i]._root)
                if self._m_textures_table[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"textures_table", self, self._m_textures_table[i]._parent)


        self._dirty = False

    class NamesBlock(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneMatb.NamesBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.shader = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self.textures = []
            for i in range(self._parent.num_textures):
                self.textures.append((self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII"))

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.textures)):
                pass



        def _write__seq(self, io=None):
            super(HexaneMatb.NamesBlock, self)._write__seq(io)
            self._io.write_bytes((self.shader).encode(u"ASCII"))
            self._io.write_u1(0)
            for i in range(len(self.textures)):
                pass
                self._io.write_bytes((self.textures[i]).encode(u"ASCII"))
                self._io.write_u1(0)



        def _check(self):
            if KaitaiStream.byte_array_index_of((self.shader).encode(u"ASCII"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"shader", -1, KaitaiStream.byte_array_index_of((self.shader).encode(u"ASCII"), 0))
            if len(self.textures) != self._parent.num_textures:
                raise kaitaistruct.ConsistencyError(u"textures", self._parent.num_textures, len(self.textures))
            for i in range(len(self.textures)):
                pass
                if KaitaiStream.byte_array_index_of((self.textures[i]).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"textures", -1, KaitaiStream.byte_array_index_of((self.textures[i]).encode(u"ASCII"), 0))

            self._dirty = False


    class ParamEntry(ReadWriteKaitaiStruct):
        """A shader-parameter override: hash plus a 4-float value. Some params use only x, as a scalar (glow intensity and the like); others use all four as an RGBA color, in 0.0-1.0 with w=1.0.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneMatb.ParamEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.param_hash = self._io.read_u4le()
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(HexaneMatb.ParamEntry, self)._write__seq(io)
            self._io.write_u4le(self.param_hash)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    class TextureEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneMatb.TextureEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_path = False
            self.path__enabled = True

        def _read(self):
            self.usage_hash = self._io.read_u4le()
            self.ofs_path = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.path
            if hasattr(self, '_m_path'):
                pass



        def _write__seq(self, io=None):
            super(HexaneMatb.TextureEntry, self)._write__seq(io)
            self._should_write_path = self.path__enabled
            self._io.write_u4le(self.usage_hash)
            self._io.write_u4le(self.ofs_path)


        def _check(self):
            if self.path__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_path).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"path", -1, KaitaiStream.byte_array_index_of((self._m_path).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def path(self):
            if self._should_write_path:
                self._write_path()
            if hasattr(self, '_m_path'):
                return self._m_path

            if not self.path__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_path)
            self._m_path = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_path', None)

        @path.setter
        def path(self, v):
            self._dirty = True
            self._m_path = v

        def _write_path(self):
            self._should_write_path = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_path)
            self._io.write_bytes((self._m_path).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    @property
    def params_table(self):
        if self._should_write_params_table:
            self._write_params_table()
        if hasattr(self, '_m_params_table'):
            return self._m_params_table

        if not self.params_table__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.ofs_params)
        self._m_params_table = []
        for i in range(self.num_params):
            _t__m_params_table = HexaneMatb.ParamEntry(self._io, self, self._root)
            try:
                _t__m_params_table._read()
            finally:
                self._m_params_table.append(_t__m_params_table)

        self._io.seek(_pos)
        return getattr(self, '_m_params_table', None)

    @params_table.setter
    def params_table(self, v):
        self._dirty = True
        self._m_params_table = v

    def _write_params_table(self):
        self._should_write_params_table = False
        _pos = self._io.pos()
        self._io.seek(self.ofs_params)
        for i in range(len(self._m_params_table)):
            pass
            self._m_params_table[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def shader(self):
        if self._should_write_shader:
            self._write_shader()
        if hasattr(self, '_m_shader'):
            return self._m_shader

        if not self.shader__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.ofs_names)
        self._m_shader = HexaneMatb.NamesBlock(self._io, self, self._root)
        self._m_shader._read()
        self._io.seek(_pos)
        return getattr(self, '_m_shader', None)

    @shader.setter
    def shader(self, v):
        self._dirty = True
        self._m_shader = v

    def _write_shader(self):
        self._should_write_shader = False
        _pos = self._io.pos()
        self._io.seek(self.ofs_names)
        self._m_shader._write__seq(self._io)
        self._io.seek(_pos)

    @property
    def textures_table(self):
        """One entry per texture, immediately after the fixed header. Not the same data as `shader.textures` below (that's the plain path strings) - this is the shader-binding metadata for each one.
        """
        if self._should_write_textures_table:
            self._write_textures_table()
        if hasattr(self, '_m_textures_table'):
            return self._m_textures_table

        if not self.textures_table__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header_size)
        self._m_textures_table = []
        for i in range(self.num_textures):
            _t__m_textures_table = HexaneMatb.TextureEntry(self._io, self, self._root)
            try:
                _t__m_textures_table._read()
            finally:
                self._m_textures_table.append(_t__m_textures_table)

        self._io.seek(_pos)
        return getattr(self, '_m_textures_table', None)

    @textures_table.setter
    def textures_table(self, v):
        self._dirty = True
        self._m_textures_table = v

    def _write_textures_table(self):
        self._should_write_textures_table = False
        _pos = self._io.pos()
        self._io.seek(self.header_size)
        for i in range(len(self._m_textures_table)):
            pass
            self._m_textures_table[i]._write__seq(self._io)

        self._io.seek(_pos)


