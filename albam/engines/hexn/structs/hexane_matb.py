# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneMatb(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x4D\x41\x54\x07"):
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


    def _fetch_instances(self):
        pass
        _ = self.shader
        self.shader._fetch_instances()

    class Tmp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.shader = (self._io.read_bytes_term(0, False, True, True)).decode("ASCII")
            self.textures = []
            for i in range(self._parent.num_textures):
                self.textures.append((self._io.read_bytes_term(0, False, True, True)).decode("ASCII"))



        def _fetch_instances(self):
            pass
            for i in range(len(self.textures)):
                pass



    @property
    def shader(self):
        if hasattr(self, '_m_shader'):
            return self._m_shader

        _pos = self._io.pos()
        self._io.seek(self.ofs_names)
        self._m_shader = HexaneMatb.Tmp(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_shader', None)


