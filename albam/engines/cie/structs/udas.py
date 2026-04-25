# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Udas(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Udas, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Udas.UdasHeader(self._io, self, self._root)
        self.header._read()
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()


    def _write__seq(self, io=None):
        super(Udas, self)._write__seq(io)
        self.header._write__seq(self._io)


    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        self._dirty = False

    class Extension(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Udas.Extension, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ext = (KaitaiStream.bytes_terminate(self._io.read_bytes(4), 0, False)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Udas.Extension, self)._write__seq(io)
            self._io.write_bytes_limit((self.ext).encode(u"UTF-8"), 4, 0, 0)


        def _check(self):
            if len((self.ext).encode(u"UTF-8")) > 4:
                raise kaitaistruct.ConsistencyError(u"ext", 4, len((self.ext).encode(u"UTF-8")))
            if KaitaiStream.byte_array_index_of((self.ext).encode(u"UTF-8"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"ext", -1, KaitaiStream.byte_array_index_of((self.ext).encode(u"UTF-8"), 0))
            self._dirty = False


    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, i, _io=None, _parent=None, _root=None):
            super(Udas.FileEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.i = i
            self._should_write_raw_data = False
            self.raw_data__enabled = True

        def _read(self):
            pass
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.raw_data
            if hasattr(self, '_m_raw_data'):
                pass



        def _write__seq(self, io=None):
            super(Udas.FileEntry, self)._write__seq(io)
            self._should_write_raw_data = self.raw_data__enabled


        def _check(self):
            if self.raw_data__enabled:
                pass
                if len(self._m_raw_data) != (self._root.header.file_size - self._parent.offsets[self.i] if self.i == self._parent.num_files - 1 else self._parent.offsets[self.i + 1] - self._parent.offsets[self.i]):
                    raise kaitaistruct.ConsistencyError(u"raw_data", (self._root.header.file_size - self._parent.offsets[self.i] if self.i == self._parent.num_files - 1 else self._parent.offsets[self.i + 1] - self._parent.offsets[self.i]), len(self._m_raw_data))

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
            self._io.seek(self._parent.offsets[self.i] + self._root.header.data_offset)
            self._m_raw_data = self._io.read_bytes((self._root.header.file_size - self._parent.offsets[self.i] if self.i == self._parent.num_files - 1 else self._parent.offsets[self.i + 1] - self._parent.offsets[self.i]))
            self._io.seek(_pos)
            return getattr(self, '_m_raw_data', None)

        @raw_data.setter
        def raw_data(self, v):
            self._dirty = True
            self._m_raw_data = v

        def _write_raw_data(self):
            self._should_write_raw_data = False
            _pos = self._io.pos()
            self._io.seek(self._parent.offsets[self.i] + self._root.header.data_offset)
            self._io.write_bytes(self._m_raw_data)
            self._io.seek(_pos)


    class UdasData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Udas.UdasData, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_file_entries = False
            self.file_entries__enabled = True

        def _read(self):
            self.num_files = self._io.read_u4le()
            self.padding = []
            for i in range(3):
                self.padding.append(self._io.read_u4le())

            self.offsets = []
            for i in range(self.num_files):
                self.offsets.append(self._io.read_u4le())

            self.file_extension = []
            for i in range(self.num_files):
                _t_file_extension = Udas.Extension(self._io, self, self._root)
                try:
                    _t_file_extension._read()
                finally:
                    self.file_extension.append(_t_file_extension)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.padding)):
                pass

            for i in range(len(self.offsets)):
                pass

            for i in range(len(self.file_extension)):
                pass
                self.file_extension[i]._fetch_instances()

            _ = self.file_entries
            if hasattr(self, '_m_file_entries'):
                pass
                for i in range(len(self._m_file_entries)):
                    pass
                    self._m_file_entries[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Udas.UdasData, self)._write__seq(io)
            self._should_write_file_entries = self.file_entries__enabled
            self._io.write_u4le(self.num_files)
            for i in range(len(self.padding)):
                pass
                self._io.write_u4le(self.padding[i])

            for i in range(len(self.offsets)):
                pass
                self._io.write_u4le(self.offsets[i])

            for i in range(len(self.file_extension)):
                pass
                self.file_extension[i]._write__seq(self._io)



        def _check(self):
            if len(self.padding) != 3:
                raise kaitaistruct.ConsistencyError(u"padding", 3, len(self.padding))
            for i in range(len(self.padding)):
                pass

            if len(self.offsets) != self.num_files:
                raise kaitaistruct.ConsistencyError(u"offsets", self.num_files, len(self.offsets))
            for i in range(len(self.offsets)):
                pass

            if len(self.file_extension) != self.num_files:
                raise kaitaistruct.ConsistencyError(u"file_extension", self.num_files, len(self.file_extension))
            for i in range(len(self.file_extension)):
                pass
                if self.file_extension[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"file_extension", self._root, self.file_extension[i]._root)
                if self.file_extension[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"file_extension", self, self.file_extension[i]._parent)

            if self.file_entries__enabled:
                pass
                if len(self._m_file_entries) != self.num_files:
                    raise kaitaistruct.ConsistencyError(u"file_entries", self.num_files, len(self._m_file_entries))
                for i in range(len(self._m_file_entries)):
                    pass
                    if self._m_file_entries[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"file_entries", self._root, self._m_file_entries[i]._root)
                    if self._m_file_entries[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"file_entries", self, self._m_file_entries[i]._parent)
                    if self._m_file_entries[i].i != i:
                        raise kaitaistruct.ConsistencyError(u"file_entries", i, self._m_file_entries[i].i)


            self._dirty = False

        @property
        def file_entries(self):
            if self._should_write_file_entries:
                self._write_file_entries()
            if hasattr(self, '_m_file_entries'):
                return self._m_file_entries

            if not self.file_entries__enabled:
                return None

            self._m_file_entries = []
            for i in range(self.num_files):
                _t__m_file_entries = Udas.FileEntry(i, self._io, self, self._root)
                try:
                    _t__m_file_entries._read()
                finally:
                    self._m_file_entries.append(_t__m_file_entries)

            return getattr(self, '_m_file_entries', None)

        @file_entries.setter
        def file_entries(self, v):
            self._dirty = True
            self._m_file_entries = v

        def _write_file_entries(self):
            self._should_write_file_entries = False
            for i in range(len(self._m_file_entries)):
                pass
                self._m_file_entries[i]._write__seq(self._io)



    class UdasHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Udas.UdasHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_data_blocks = False
            self.data_blocks__enabled = True

        def _read(self):
            self.id_magic = []
            for i in range(8):
                self.id_magic.append(self._io.read_u4le())

            self.unk_00 = self._io.read_u4le()
            self.file_size = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.data_offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.id_magic)):
                pass

            _ = self.data_blocks
            if hasattr(self, '_m_data_blocks'):
                pass
                self._m_data_blocks._fetch_instances()



        def _write__seq(self, io=None):
            super(Udas.UdasHeader, self)._write__seq(io)
            self._should_write_data_blocks = self.data_blocks__enabled
            for i in range(len(self.id_magic)):
                pass
                self._io.write_u4le(self.id_magic[i])

            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.file_size)
            self._io.write_u4le(self.unk_01)
            self._io.write_u4le(self.data_offset)


        def _check(self):
            if len(self.id_magic) != 8:
                raise kaitaistruct.ConsistencyError(u"id_magic", 8, len(self.id_magic))
            for i in range(len(self.id_magic)):
                pass

            if self.data_blocks__enabled:
                pass
                if self._m_data_blocks._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data_blocks", self._root, self._m_data_blocks._root)
                if self._m_data_blocks._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data_blocks", self, self._m_data_blocks._parent)

            self._dirty = False

        @property
        def data_blocks(self):
            if self._should_write_data_blocks:
                self._write_data_blocks()
            if hasattr(self, '_m_data_blocks'):
                return self._m_data_blocks

            if not self.data_blocks__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.data_offset)
            self._m_data_blocks = Udas.UdasData(self._io, self, self._root)
            self._m_data_blocks._read()
            self._io.seek(_pos)
            return getattr(self, '_m_data_blocks', None)

        @data_blocks.setter
        def data_blocks(self, v):
            self._dirty = True
            self._m_data_blocks = v

        def _write_data_blocks(self):
            self._should_write_data_blocks = False
            _pos = self._io.pos()
            self._io.seek(self.data_offset)
            self._m_data_blocks._write__seq(self._io)
            self._io.seek(_pos)



