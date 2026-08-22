# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneSsg(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(HexaneSsg, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x06\x00\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x06\x00\x00\x00", self.id_magic, self._io, u"/seq/0")
        self.reserved_01 = self._io.read_u4le()
        self.size_files_info = self._io.read_u4le()
        self.size_file_names = self._io.read_u4le()
        self.size_chunks_buffer = self._io.read_u4le()
        self.reserverd_01 = self._io.read_u4le()
        self.size_chunks_info = self._io.read_u4le()
        self.size_padding = self._io.read_u4le()
        self.files_info = []
        for i in range(self.size_files_info // 32):
            _t_files_info = HexaneSsg.FileInfo(self._io, self, self._root)
            try:
                _t_files_info._read()
            finally:
                self.files_info.append(_t_files_info)

        self.chunk_sizes = []
        for i in range(self.size_chunks_info // 4):
            self.chunk_sizes.append(self._io.read_u4le())

        self.file_names = self._io.read_bytes(self.size_file_names)
        self.buffer_chunks = self._io.read_bytes(self.size_chunks_buffer)
        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.files_info)):
            pass
            self.files_info[i]._fetch_instances()

        for i in range(len(self.chunk_sizes)):
            pass



    def _write__seq(self, io=None):
        super(HexaneSsg, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u4le(self.reserved_01)
        self._io.write_u4le(self.size_files_info)
        self._io.write_u4le(self.size_file_names)
        self._io.write_u4le(self.size_chunks_buffer)
        self._io.write_u4le(self.reserverd_01)
        self._io.write_u4le(self.size_chunks_info)
        self._io.write_u4le(self.size_padding)
        for i in range(len(self.files_info)):
            pass
            self.files_info[i]._write__seq(self._io)

        for i in range(len(self.chunk_sizes)):
            pass
            self._io.write_u4le(self.chunk_sizes[i])

        self._io.write_bytes(self.file_names)
        self._io.write_bytes(self.buffer_chunks)


    def _check(self):
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x06\x00\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x06\x00\x00\x00", self.id_magic, None, u"/seq/0")
        if len(self.files_info) != self.size_files_info // 32:
            raise kaitaistruct.ConsistencyError(u"files_info", self.size_files_info // 32, len(self.files_info))
        for i in range(len(self.files_info)):
            pass
            if self.files_info[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"files_info", self._root, self.files_info[i]._root)
            if self.files_info[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"files_info", self, self.files_info[i]._parent)

        if len(self.chunk_sizes) != self.size_chunks_info // 4:
            raise kaitaistruct.ConsistencyError(u"chunk_sizes", self.size_chunks_info // 4, len(self.chunk_sizes))
        for i in range(len(self.chunk_sizes)):
            pass

        if len(self.file_names) != self.size_file_names:
            raise kaitaistruct.ConsistencyError(u"file_names", self.size_file_names, len(self.file_names))
        if len(self.buffer_chunks) != self.size_chunks_buffer:
            raise kaitaistruct.ConsistencyError(u"buffer_chunks", self.size_chunks_buffer, len(self.buffer_chunks))
        self._dirty = False

    class FileInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneSsg.FileInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.ident = self._io.read_u4le()
            self.name_offset_rel = self._io.read_u4le()
            self.size = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.reserved_02 = self._io.read_u4le()
            self.file_type = self._io.read_s4le()
            self.unk_01 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(HexaneSsg.FileInfo, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.ident)
            self._io.write_u4le(self.name_offset_rel)
            self._io.write_u4le(self.size)
            self._io.write_u4le(self.reserved_01)
            self._io.write_u4le(self.reserved_02)
            self._io.write_s4le(self.file_type)
            self._io.write_u4le(self.unk_01)
            self._io.write_u4le(self.unk_02)


        def _check(self):
            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(((32 + self._parent.size_files_info) + self._parent.size_chunks_info) + self.name_offset_rel)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(((32 + self._parent.size_files_info) + self._parent.size_chunks_info) + self.name_offset_rel)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)



