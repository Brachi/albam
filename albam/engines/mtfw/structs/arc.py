# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Arc(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.header = Arc.ArcHeader(self._io, self, self._root)
        self.header._read()
        self.file_entries = []
        for i in range(self._root.header.num_files):
            _t_file_entries = Arc.FileEntry(self._io, self, self._root)
            _t_file_entries._read()
            self.file_entries.append(_t_file_entries)

        self.padding = self._io.read_bytes((32760 - ((self._root.header.num_files * 80) % 32760)))


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Arc, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._write__seq(self._io)

        self._io.write_bytes(self.padding)


    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)
        if (len(self.file_entries) != self._root.header.num_files):
            raise kaitaistruct.ConsistencyError(u"file_entries", len(self.file_entries), self._root.header.num_files)
        for i in range(len(self.file_entries)):
            pass
            if self.file_entries[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"file_entries", self.file_entries[i]._root, self._root)
            if self.file_entries[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"file_entries", self.file_entries[i]._parent, self)

        if (len(self.padding) != (32760 - ((self._root.header.num_files * 80) % 32760))):
            raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), (32760 - ((self._root.header.num_files * 80) % 32760)))

    class ArcHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ident = self._io.read_bytes(4)
            if not (self.ident == b"\x41\x52\x43\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x41\x52\x43\x00", self.ident, self._io, u"/types/arc_header/seq/0")
            self.version = self._io.read_s2le()
            self.num_files = self._io.read_s2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Arc.ArcHeader, self)._write__seq(io)
            self._io.write_bytes(self.ident)
            self._io.write_s2le(self.version)
            self._io.write_s2le(self.num_files)


        def _check(self):
            pass
            if (len(self.ident) != 4):
                raise kaitaistruct.ConsistencyError(u"ident", len(self.ident), 4)
            if not (self.ident == b"\x41\x52\x43\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x41\x52\x43\x00", self.ident, None, u"/types/arc_header/seq/0")

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 8
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_raw_data = False
            self.raw_data__to_write = True

        def _read(self):
            self.file_path = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode("ASCII")
            self.file_type = self._io.read_s4le()
            self.zsize = self._io.read_u4le()
            self.size = self._io.read_bits_int_le(29)
            self.flags = self._io.read_bits_int_le(3)
            self.offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.raw_data


        def _write__seq(self, io=None):
            super(Arc.FileEntry, self)._write__seq(io)
            self._should_write_raw_data = self.raw_data__to_write
            self._io.write_bytes_limit((self.file_path).encode(u"ASCII"), 64, 0, 0)
            self._io.write_s4le(self.file_type)
            self._io.write_u4le(self.zsize)
            self._io.write_bits_int_le(29, self.size)
            self._io.write_bits_int_le(3, self.flags)
            self._io.write_u4le(self.offset)


        def _check(self):
            pass
            if (len((self.file_path).encode(u"ASCII")) > 64):
                raise kaitaistruct.ConsistencyError(u"file_path", len((self.file_path).encode(u"ASCII")), 64)
            if (KaitaiStream.byte_array_index_of((self.file_path).encode(u"ASCII"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"file_path", KaitaiStream.byte_array_index_of((self.file_path).encode(u"ASCII"), 0), -1)

        @property
        def raw_data(self):
            if self._should_write_raw_data:
                self._write_raw_data()
            if hasattr(self, '_m_raw_data'):
                return self._m_raw_data

            io = self._root._io
            _pos = io.pos()
            io.seek(self.offset)
            self._m_raw_data = io.read_bytes(self.zsize)
            io.seek(_pos)
            return getattr(self, '_m_raw_data', None)

        @raw_data.setter
        def raw_data(self, v):
            self._m_raw_data = v

        def _write_raw_data(self):
            self._should_write_raw_data = False
            io = self._root._io
            _pos = io.pos()
            io.seek(self.offset)
            io.write_bytes(self.raw_data)
            io.seek(_pos)


        def _check_raw_data(self):
            pass
            if (len(self.raw_data) != self.zsize):
                raise kaitaistruct.ConsistencyError(u"raw_data", len(self.raw_data), self.zsize)



