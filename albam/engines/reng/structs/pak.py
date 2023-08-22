# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Pak(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ident = self._io.read_bytes(4)
        if not self.ident == b"\x4B\x50\x4B\x41":
            raise kaitaistruct.ValidationNotEqualError(b"\x4B\x50\x4B\x41", self.ident, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.num_file_entries = self._io.read_u4le()
        self.reserved = self._io.read_u4le()
        self.file_entries = []
        for i in range(self.num_file_entries):
            self.file_entries.append(Pak.FileEntry(self._io, self, self._root))


    class FileEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_path_hash_case_insensitive = self._io.read_u4le()
            self.file_path_hash_case_sensitive = self._io.read_u4le()
            self.offset = self._io.read_u8le()
            self.zsize = self._io.read_u8le()
            self.size = self._io.read_u8le()
            self.flags = self._io.read_u8le()
            self.unk_01 = self._io.read_u8le()



