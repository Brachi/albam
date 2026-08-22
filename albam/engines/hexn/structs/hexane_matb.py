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
        self._should_write_shader = False
        self.shader__enabled = True

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x41\x54\x07":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x41\x54\x07", self.id_magic, self._io, u"/seq/0")
        self.ofs_names = self._io.read_u4le()
        self.num_textures = self._io.read_u4le()
        self.unk_01 = self._io.read_u4le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        self.unk_05 = self._io.read_u4le()
        self.unk_06 = self._io.read_u4le()
        self.unk_07 = self._io.read_u4le()
        self._dirty = False


    def _fetch_instances(self):
        pass
        _ = self.shader
        if hasattr(self, '_m_shader'):
            pass
            self._m_shader._fetch_instances()



    def _write__seq(self, io=None):
        super(HexaneMatb, self)._write__seq(io)
        self._should_write_shader = self.shader__enabled
        self._io.write_bytes(self.id_magic)
        self._io.write_u4le(self.ofs_names)
        self._io.write_u4le(self.num_textures)
        self._io.write_u4le(self.unk_01)
        self._io.write_u4le(self.unk_02)
        self._io.write_u4le(self.unk_03)
        self._io.write_u4le(self.unk_04)
        self._io.write_u4le(self.unk_05)
        self._io.write_u4le(self.unk_06)
        self._io.write_u4le(self.unk_07)


    def _check(self):
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x4D\x41\x54\x07":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x41\x54\x07", self.id_magic, None, u"/seq/0")
        if self.shader__enabled:
            pass
            if self._m_shader._root != self._root:
                raise kaitaistruct.ConsistencyError(u"shader", self._root, self._m_shader._root)
            if self._m_shader._parent != self:
                raise kaitaistruct.ConsistencyError(u"shader", self, self._m_shader._parent)

        self._dirty = False

    class Tmp(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneMatb.Tmp, self).__init__(_io)
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
            super(HexaneMatb.Tmp, self)._write__seq(io)
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
        self._m_shader = HexaneMatb.Tmp(self._io, self, self._root)
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


