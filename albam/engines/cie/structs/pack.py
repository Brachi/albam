# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Pack(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Pack, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.pack_name = self._io.read_u4le()
        self.num_files = self._io.read_u4le()
        self.file_entries = []
        for i in range(self.num_files):
            _t_file_entries = Pack.FileEntry(self._io, self, self._root)
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
        super(Pack, self)._write__seq(io)
        self._io.write_u4le(self.pack_name)
        self._io.write_u4le(self.num_files)
        for i in range(len(self.file_entries)):
            pass
            self.file_entries[i]._write__seq(self._io)



    def _check(self):
        if len(self.file_entries) != self.num_files:
            raise kaitaistruct.ConsistencyError(u"file_entries", self.num_files, len(self.file_entries))
        for i in range(len(self.file_entries)):
            pass
            if self.file_entries[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"file_entries", self._root, self.file_entries[i]._root)
            if self.file_entries[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"file_entries", self, self.file_entries[i]._parent)

        self._dirty = False

    class FileBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Pack.FileBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.size = self._io.read_u4le()
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.is_dds = self._io.read_u4le()
            self.raw_data = self._io.read_bytes(self.size)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Pack.FileBody, self)._write__seq(io)
            self._io.write_u4le(self.size)
            self._io.write_u4le(self.unk_00)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u4le(self.is_dds)
            self._io.write_bytes(self.raw_data)


        def _check(self):
            if len(self.raw_data) != self.size:
                raise kaitaistruct.ConsistencyError(u"raw_data", self.size, len(self.raw_data))
            self._dirty = False


    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Pack.FileEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_data = False
            self.data__enabled = True

        def _read(self):
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.data
            if hasattr(self, '_m_data'):
                pass
                self._m_data._fetch_instances()



        def _write__seq(self, io=None):
            super(Pack.FileEntry, self)._write__seq(io)
            self._should_write_data = self.data__enabled
            self._io.write_u4le(self.offset)


        def _check(self):
            if self.data__enabled:
                pass
                if self._m_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data._root)
                if self._m_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self._m_data._parent)

            self._dirty = False

        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            if not self.data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_data = Pack.FileBody(self._io, self, self._root)
            self._m_data._read()
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._dirty = True
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_data._write__seq(self._io)
            self._io.seek(_pos)



