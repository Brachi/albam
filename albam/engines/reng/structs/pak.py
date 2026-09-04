# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Pak(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Pak, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.ident = self._io.read_bytes(4)
        if not self.ident == b"\x4B\x50\x4B\x41":
            raise kaitaistruct.ValidationNotEqualError(b"\x4B\x50\x4B\x41", self.ident, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.num_file_entries = self._io.read_u4le()
        self.reserved = self._io.read_u4le()
        self.file_entries = []
        for i in range(self.num_file_entries):
            _t_file_entries = Pak.FileEntry(self._io, self, self._root)
            try:
                _t_file_entries._read()
            finally:
                self.file_entries.append(_t_file_entries)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Pak, self)._write__seq(io)
        self._io.write_bytes(self.ident)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.num_file_entries)
        self._io.write_u4le(self.reserved)
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._write__seq(self._io)



    def _check(self):
        if len(self.ident) != 4:
            raise kaitaistruct.ConsistencyError(u"ident", 4, len(self.ident))
        if not self.ident == b"\x4B\x50\x4B\x41":
            raise kaitaistruct.ValidationNotEqualError(b"\x4B\x50\x4B\x41", self.ident, None, u"/seq/0")
        if len(self.file_entries) != self.num_file_entries:
            raise kaitaistruct.ConsistencyError(u"file_entries", self.num_file_entries, len(self.file_entries))
        for i in range(len(self.file_entries)):
            pass
            if self.file_entries[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"file_entries", self._root, self.file_entries[i]._root)
            if self.file_entries[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"file_entries", self, self.file_entries[i]._parent)

        self._dirty = False

    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Pak.FileEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.file_path_hash_case_insensitive = self._io.read_u4le()
            self.file_path_hash_case_sensitive = self._io.read_u4le()
            self.offset = self._io.read_u8le()
            self.zsize = self._io.read_u8le()
            self.size = self._io.read_u8le()
            self.flags = self._io.read_u8le()
            self.unk_01 = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Pak.FileEntry, self)._write__seq(io)
            self._io.write_u4le(self.file_path_hash_case_insensitive)
            self._io.write_u4le(self.file_path_hash_case_sensitive)
            self._io.write_u8le(self.offset)
            self._io.write_u8le(self.zsize)
            self._io.write_u8le(self.size)
            self._io.write_u8le(self.flags)
            self._io.write_u8le(self.unk_01)


        def _check(self):
            self._dirty = False



