# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineTex(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

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
            self.mipmap_header = ReengineTex.MipmapHeader1(self._io, self, self._root)
        elif _on == 190820018:
            self.mipmap_header = ReengineTex.MipmapHeader1(self._io, self, self._root)
        elif _on == 30:
            self.mipmap_header = ReengineTex.MipmapHeader2(self._io, self, self._root)
        elif _on == 34:
            self.mipmap_header = ReengineTex.MipmapHeader2(self._io, self, self._root)
        self.format = self._io.read_u4le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        if  ((self.version == 30) or (self.version == 34)) :
            self.unk_05 = self._io.read_u8le()

        self.mipmaps = []
        for i in range((self.mipmap_header.num_mipmaps if  ((self.version == 10) or (self.version == 190820018))  else self.mipmap_header.num_mipmaps)):
            self.mipmaps.append(ReengineTex.MipmapData(self._io, self, self._root))


    class MipmapData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_data = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.size_data = self._io.read_u4le()

        @property
        def dds_data(self):
            if hasattr(self, '_m_dds_data'):
                return self._m_dds_data

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_dds_data = self._io.read_bytes(self.size_data)
            self._io.seek(_pos)
            return getattr(self, '_m_dds_data', None)


    class MipmapHeader1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_mipmaps = self._io.read_u1()
            self.num_images = self._io.read_u1()


    class MipmapHeader2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_images = self._io.read_u1()
            self.size_mipmap_header = self._io.read_u1()

        @property
        def num_mipmaps(self):
            if hasattr(self, '_m_num_mipmaps'):
                return self._m_num_mipmaps

            self._m_num_mipmaps = self.size_mipmap_header // 16
            return getattr(self, '_m_num_mipmaps', None)



