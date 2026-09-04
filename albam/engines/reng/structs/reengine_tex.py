# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineTex(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(ReengineTex, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.ident = self._io.read_bytes(4)
        if not self.ident == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.ident, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.width = self._io.read_u2le()
        self.height = self._io.read_u2le()
        self.unk_00 = self._io.read_u2le()
        _on = self.version
        if _on == 10:
            pass
            self.mipmap_header = ReengineTex.MipmapHeader1(self._io, self, self._root)
            self.mipmap_header._read()
        elif _on == 190820018:
            pass
            self.mipmap_header = ReengineTex.MipmapHeader1(self._io, self, self._root)
            self.mipmap_header._read()
        elif _on == 30:
            pass
            self.mipmap_header = ReengineTex.MipmapHeader2(self._io, self, self._root)
            self.mipmap_header._read()
        elif _on == 34:
            pass
            self.mipmap_header = ReengineTex.MipmapHeader2(self._io, self, self._root)
            self.mipmap_header._read()
        self.format = self._io.read_u4le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        if  ((self.version == 30) or (self.version == 34)) :
            pass
            self.unk_05 = self._io.read_u8le()

        self.mipmaps = []
        for i in range((self.mipmap_header.num_mipmaps if  ((self.version == 10) or (self.version == 190820018))  else self.mipmap_header.num_mipmaps)):
            _t_mipmaps = ReengineTex.MipmapData(self._io, self, self._root)
            try:
                _t_mipmaps._read()
            finally:
                self.mipmaps.append(_t_mipmaps)

        self._dirty = False


    def _fetch_instances(self):
        pass
        _on = self.version
        if _on == 10:
            pass
            self.mipmap_header._fetch_instances()
        elif _on == 190820018:
            pass
            self.mipmap_header._fetch_instances()
        elif _on == 30:
            pass
            self.mipmap_header._fetch_instances()
        elif _on == 34:
            pass
            self.mipmap_header._fetch_instances()
        if  ((self.version == 30) or (self.version == 34)) :
            pass

        for i in range(len(self.mipmaps)):
            pass
            self.mipmaps[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(ReengineTex, self)._write__seq(io)
        self._io.write_bytes(self.ident)
        self._io.write_u4le(self.version)
        self._io.write_u2le(self.width)
        self._io.write_u2le(self.height)
        self._io.write_u2le(self.unk_00)
        _on = self.version
        if _on == 10:
            pass
            self.mipmap_header._write__seq(self._io)
        elif _on == 190820018:
            pass
            self.mipmap_header._write__seq(self._io)
        elif _on == 30:
            pass
            self.mipmap_header._write__seq(self._io)
        elif _on == 34:
            pass
            self.mipmap_header._write__seq(self._io)
        self._io.write_u4le(self.format)
        self._io.write_u4le(self.unk_02)
        self._io.write_u4le(self.unk_03)
        self._io.write_u4le(self.unk_04)
        if  ((self.version == 30) or (self.version == 34)) :
            pass
            self._io.write_u8le(self.unk_05)

        for i in range(len(self.mipmaps)):
            pass
            self.mipmaps[i]._write__seq(self._io)



    def _check(self):
        if len(self.ident) != 4:
            raise kaitaistruct.ConsistencyError(u"ident", 4, len(self.ident))
        if not self.ident == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.ident, None, u"/seq/0")
        _on = self.version
        if _on == 10:
            pass
            if self.mipmap_header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self._root, self.mipmap_header._root)
            if self.mipmap_header._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self, self.mipmap_header._parent)
        elif _on == 190820018:
            pass
            if self.mipmap_header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self._root, self.mipmap_header._root)
            if self.mipmap_header._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self, self.mipmap_header._parent)
        elif _on == 30:
            pass
            if self.mipmap_header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self._root, self.mipmap_header._root)
            if self.mipmap_header._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self, self.mipmap_header._parent)
        elif _on == 34:
            pass
            if self.mipmap_header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self._root, self.mipmap_header._root)
            if self.mipmap_header._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self, self.mipmap_header._parent)
        if  ((self.version == 30) or (self.version == 34)) :
            pass

        if len(self.mipmaps) != (self.mipmap_header.num_mipmaps if  ((self.version == 10) or (self.version == 190820018))  else self.mipmap_header.num_mipmaps):
            raise kaitaistruct.ConsistencyError(u"mipmaps", (self.mipmap_header.num_mipmaps if  ((self.version == 10) or (self.version == 190820018))  else self.mipmap_header.num_mipmaps), len(self.mipmaps))
        for i in range(len(self.mipmaps)):
            pass
            if self.mipmaps[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmaps", self._root, self.mipmaps[i]._root)
            if self.mipmaps[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmaps", self, self.mipmaps[i]._parent)

        self._dirty = False

    class MipmapData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineTex.MipmapData, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_dds_data = False
            self.dds_data__enabled = True

        def _read(self):
            self.ofs_data = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.size_data = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.dds_data
            if hasattr(self, '_m_dds_data'):
                pass



        def _write__seq(self, io=None):
            super(ReengineTex.MipmapData, self)._write__seq(io)
            self._should_write_dds_data = self.dds_data__enabled
            self._io.write_u4le(self.ofs_data)
            self._io.write_u4le(self.unk_01)
            self._io.write_u4le(self.unk_02)
            self._io.write_u4le(self.size_data)


        def _check(self):
            if self.dds_data__enabled:
                pass
                if len(self._m_dds_data) != self.size_data:
                    raise kaitaistruct.ConsistencyError(u"dds_data", self.size_data, len(self._m_dds_data))

            self._dirty = False

        @property
        def dds_data(self):
            if self._should_write_dds_data:
                self._write_dds_data()
            if hasattr(self, '_m_dds_data'):
                return self._m_dds_data

            if not self.dds_data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_dds_data = self._io.read_bytes(self.size_data)
            self._io.seek(_pos)
            return getattr(self, '_m_dds_data', None)

        @dds_data.setter
        def dds_data(self, v):
            self._dirty = True
            self._m_dds_data = v

        def _write_dds_data(self):
            self._should_write_dds_data = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._io.write_bytes(self._m_dds_data)
            self._io.seek(_pos)


    class MipmapHeader1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineTex.MipmapHeader1, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_mipmaps = self._io.read_u1()
            self.num_images = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineTex.MipmapHeader1, self)._write__seq(io)
            self._io.write_u1(self.num_mipmaps)
            self._io.write_u1(self.num_images)


        def _check(self):
            self._dirty = False


    class MipmapHeader2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineTex.MipmapHeader2, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_images = self._io.read_u1()
            self.size_mipmap_header = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineTex.MipmapHeader2, self)._write__seq(io)
            self._io.write_u1(self.num_images)
            self._io.write_u1(self.size_mipmap_header)


        def _check(self):
            self._dirty = False

        @property
        def num_mipmaps(self):
            if hasattr(self, '_m_num_mipmaps'):
                return self._m_num_mipmaps

            self._m_num_mipmaps = self.size_mipmap_header // 16
            return getattr(self, '_m_num_mipmaps', None)

        def _invalidate_num_mipmaps(self):
            del self._m_num_mipmaps


