# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Udas(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.header = Udas.UdasHeader(self._io, self, self._root)
        self.header._read()


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()


    def _write__seq(self, io=None):
        super(Udas, self)._write__seq(io)
        self.header._write__seq(self._io)


    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)

    class UdasHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_data_bloc = False
            self.data_bloc__to_write = True

        def _read(self):
            self.id_magic = []
            for i in range(8):
                self.id_magic.append(self._io.read_u4le())

            self.unk_00 = self._io.read_u4le()
            self.file_size = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.data_offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.id_magic)):
                pass

            _ = self.data_bloc
            self.data_bloc._fetch_instances()


        def _write__seq(self, io=None):
            super(Udas.UdasHeader, self)._write__seq(io)
            self._should_write_data_bloc = self.data_bloc__to_write
            for i in range(len(self.id_magic)):
                pass
                self._io.write_u4le(self.id_magic[i])

            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.file_size)
            self._io.write_u4le(self.unk_01)
            self._io.write_u4le(self.data_offset)


        def _check(self):
            pass
            if (len(self.id_magic) != 8):
                raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 8)
            for i in range(len(self.id_magic)):
                pass


        @property
        def data_bloc(self):
            if self._should_write_data_bloc:
                self._write_data_bloc()
            if hasattr(self, '_m_data_bloc'):
                return self._m_data_bloc

            _pos = self._io.pos()
            self._io.seek(self.data_offset)
            self._m_data_bloc = Udas.UdasData(self._io, self, self._root)
            self._m_data_bloc._read()
            self._io.seek(_pos)
            return getattr(self, '_m_data_bloc', None)

        @data_bloc.setter
        def data_bloc(self, v):
            self._m_data_bloc = v

        def _write_data_bloc(self):
            self._should_write_data_bloc = False
            _pos = self._io.pos()
            self._io.seek(self.data_offset)
            self.data_bloc._write__seq(self._io)
            self._io.seek(_pos)


        def _check_data_bloc(self):
            pass
            if self.data_bloc._root != self._root:
                raise kaitaistruct.ConsistencyError(u"data_bloc", self.data_bloc._root, self._root)
            if self.data_bloc._parent != self:
                raise kaitaistruct.ConsistencyError(u"data_bloc", self.data_bloc._parent, self)


    class UdasData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_file_entries = False
            self.file_entries__to_write = True

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
                _t_file_extension._read()
                self.file_extension.append(_t_file_extension)



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
            for i in range(len(self._m_file_entries)):
                pass
                self.file_entries[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Udas.UdasData, self)._write__seq(io)
            self._should_write_file_entries = self.file_entries__to_write
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
            pass
            if (len(self.padding) != 3):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 3)
            for i in range(len(self.padding)):
                pass

            if (len(self.offsets) != self.num_files):
                raise kaitaistruct.ConsistencyError(u"offsets", len(self.offsets), self.num_files)
            for i in range(len(self.offsets)):
                pass

            if (len(self.file_extension) != self.num_files):
                raise kaitaistruct.ConsistencyError(u"file_extension", len(self.file_extension), self.num_files)
            for i in range(len(self.file_extension)):
                pass
                if self.file_extension[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"file_extension", self.file_extension[i]._root, self._root)
                if self.file_extension[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"file_extension", self.file_extension[i]._parent, self)


        @property
        def file_entries(self):
            if self._should_write_file_entries:
                self._write_file_entries()
            if hasattr(self, '_m_file_entries'):
                return self._m_file_entries

            self._m_file_entries = []
            for i in range(self.num_files):
                _t__m_file_entries = Udas.FileEntry(i, self._io, self, self._root)
                _t__m_file_entries._read()
                self._m_file_entries.append(_t__m_file_entries)

            return getattr(self, '_m_file_entries', None)

        @file_entries.setter
        def file_entries(self, v):
            self._m_file_entries = v

        def _write_file_entries(self):
            self._should_write_file_entries = False
            for i in range(len(self._m_file_entries)):
                pass
                self.file_entries[i]._write__seq(self._io)



        def _check_file_entries(self):
            pass
            if (len(self.file_entries) != self.num_files):
                raise kaitaistruct.ConsistencyError(u"file_entries", len(self.file_entries), self.num_files)
            for i in range(len(self._m_file_entries)):
                pass
                if self.file_entries[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"file_entries", self.file_entries[i]._root, self._root)
                if self.file_entries[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"file_entries", self.file_entries[i]._parent, self)
                if (self.file_entries[i].i != i):
                    raise kaitaistruct.ConsistencyError(u"file_entries", self.file_entries[i].i, i)



    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, i, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self.i = i
            self._should_write_raw_data = False
            self.raw_data__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.raw_data


        def _write__seq(self, io=None):
            super(Udas.FileEntry, self)._write__seq(io)
            self._should_write_raw_data = self.raw_data__to_write


        def _check(self):
            pass

        @property
        def raw_data(self):
            if self._should_write_raw_data:
                self._write_raw_data()
            if hasattr(self, '_m_raw_data'):
                return self._m_raw_data

            _pos = self._io.pos()
            self._io.seek((self._parent.offsets[self.i] + self._root.header.data_offset))
            self._m_raw_data = self._io.read_bytes(((self._root.header.file_size - self._parent.offsets[self.i]) if (self.i == (self._parent.num_files - 1)) else (self._parent.offsets[(self.i + 1)] - self._parent.offsets[self.i])))
            self._io.seek(_pos)
            return getattr(self, '_m_raw_data', None)

        @raw_data.setter
        def raw_data(self, v):
            self._m_raw_data = v

        def _write_raw_data(self):
            self._should_write_raw_data = False
            _pos = self._io.pos()
            self._io.seek((self._parent.offsets[self.i] + self._root.header.data_offset))
            self._io.write_bytes(self.raw_data)
            self._io.seek(_pos)


        def _check_raw_data(self):
            pass
            if (len(self.raw_data) != ((self._root.header.file_size - self._parent.offsets[self.i]) if (self.i == (self._parent.num_files - 1)) else (self._parent.offsets[(self.i + 1)] - self._parent.offsets[self.i]))):
                raise kaitaistruct.ConsistencyError(u"raw_data", len(self.raw_data), ((self._root.header.file_size - self._parent.offsets[self.i]) if (self.i == (self._parent.num_files - 1)) else (self._parent.offsets[(self.i + 1)] - self._parent.offsets[self.i])))


    class Extension(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ext = (self._io.read_bytes_term(0, False, True, True)).decode("UTF-8")


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Udas.Extension, self)._write__seq(io)
            self._io.write_bytes((self.ext).encode(u"UTF-8"))
            self._io.write_u1(0)


        def _check(self):
            pass
            if (KaitaiStream.byte_array_index_of((self.ext).encode(u"UTF-8"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"ext", KaitaiStream.byte_array_index_of((self.ext).encode(u"UTF-8"), 0), -1)



