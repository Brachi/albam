# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Arc(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ident = self._io.read_bytes(4)
        if not self.ident == b"\x41\x52\x43\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x41\x52\x43\x00", self.ident, self._io, u"/seq/0")
        self.version = self._io.read_s2le()
        self.num_files = self._io.read_s2le()
        self.file_entries = []
        for i in range(self.num_files):
            self.file_entries.append(Arc.FileEntry(self._io, self, self._root))


    class FileEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_path = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ascii")
            self.file_type = self._io.read_s4le()
            self.zsize = self._io.read_u4le()
            self.size = self._io.read_bits_int_be(24)
            self.flags = self._io.read_bits_int_be(8)
            self._io.align_to_byte()
            self.offset = self._io.read_u4le()

        @property
        def raw_data(self):
            if hasattr(self, '_m_raw_data'):
                return self._m_raw_data

            io = self._root._io
            _pos = io.pos()
            io.seek(self.offset)
            self._m_raw_data = io.read_bytes(self.zsize)
            io.seek(_pos)
            return getattr(self, '_m_raw_data', None)



