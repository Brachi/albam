# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lfs(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Lfs, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Lfs.LfsHeader(self._io, self, self._root)
        self.header._read()
        self.file_entries = []
        for i in range(self.header.num_files):
            _t_file_entries = Lfs.FileEntry(self._io, self, self._root)
            try:
                _t_file_entries._read()
            finally:
                self.file_entries.append(_t_file_entries)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Lfs, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.file_entries) != self.header.num_files:
            raise kaitaistruct.ConsistencyError(u"file_entries", self.header.num_files, len(self.file_entries))
        for i in range(len(self.file_entries)):
            pass
            if self.file_entries[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"file_entries", self._root, self.file_entries[i]._root)
            if self.file_entries[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"file_entries", self, self.file_entries[i]._parent)

        self._dirty = False

    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lfs.FileEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_raw_data = False
            self.raw_data__enabled = True

        def _read(self):
            self.size_compressed = self._io.read_u2le()
            self.size_decompressed = self._io.read_u2le()
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.raw_data
            if hasattr(self, '_m_raw_data'):
                pass



        def _write__seq(self, io=None):
            super(Lfs.FileEntry, self)._write__seq(io)
            self._should_write_raw_data = self.raw_data__enabled
            self._io.write_u2le(self.size_compressed)
            self._io.write_u2le(self.size_decompressed)
            self._io.write_u4le(self.offset)


        def _check(self):
            if self.raw_data__enabled:
                pass
                if len(self._m_raw_data) != self.size_compressed:
                    raise kaitaistruct.ConsistencyError(u"raw_data", self.size_compressed, len(self._m_raw_data))

            self._dirty = False

        @property
        def raw_data(self):
            if self._should_write_raw_data:
                self._write_raw_data()
            if hasattr(self, '_m_raw_data'):
                return self._m_raw_data

            if not self.raw_data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek((self.offset & ~1) + 20)
            self._m_raw_data = self._io.read_bytes(self.size_compressed)
            self._io.seek(_pos)
            return getattr(self, '_m_raw_data', None)

        @raw_data.setter
        def raw_data(self, v):
            self._dirty = True
            self._m_raw_data = v

        def _write_raw_data(self):
            self._should_write_raw_data = False
            _pos = self._io.pos()
            self._io.seek((self.offset & ~1) + 20)
            self._io.write_bytes(self._m_raw_data)
            self._io.seek(_pos)


    class LfsHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lfs.LfsHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.id_magic = self._io.read_bytes(4)
            if not self.id_magic == b"\x52\x44\x4C\x58":
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x44\x4C\x58", self.id_magic, self._io, u"/types/lfs_header/seq/0")
            self.file_id = self._io.read_u4le()
            self.size_decompressed = self._io.read_u4le()
            self.size_compressed = self._io.read_u4le()
            self.num_files = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lfs.LfsHeader, self)._write__seq(io)
            self._io.write_bytes(self.id_magic)
            self._io.write_u4le(self.file_id)
            self._io.write_u4le(self.size_decompressed)
            self._io.write_u4le(self.size_compressed)
            self._io.write_u4le(self.num_files)


        def _check(self):
            if len(self.id_magic) != 4:
                raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
            if not self.id_magic == b"\x52\x44\x4C\x58":
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x44\x4C\x58", self.id_magic, None, u"/types/lfs_header/seq/0")
            self._dirty = False



