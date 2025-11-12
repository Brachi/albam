# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lfs(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.lfs_header = Lfs.Header(self._io, self, self._root)
        self.lfs_header._read()
        self.data_chunks = []
        for i in range(self.lfs_header.num_chunks):
            _t_data_chunks = Lfs.DataChunk(self._io, self, self._root)
            _t_data_chunks._read()
            self.data_chunks.append(_t_data_chunks)



    def _fetch_instances(self):
        pass
        self.lfs_header._fetch_instances()
        for i in range(len(self.data_chunks)):
            pass
            self.data_chunks[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Lfs, self)._write__seq(io)
        self.lfs_header._write__seq(self._io)
        for i in range(len(self.data_chunks)):
            pass
            self.data_chunks[i]._write__seq(self._io)



    def _check(self):
        pass
        if self.lfs_header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"lfs_header", self.lfs_header._root, self._root)
        if self.lfs_header._parent != self:
            raise kaitaistruct.ConsistencyError(u"lfs_header", self.lfs_header._parent, self)
        if (len(self.data_chunks) != self.lfs_header.num_chunks):
            raise kaitaistruct.ConsistencyError(u"data_chunks", len(self.data_chunks), self.lfs_header.num_chunks)
        for i in range(len(self.data_chunks)):
            pass
            if self.data_chunks[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"data_chunks", self.data_chunks[i]._root, self._root)
            if self.data_chunks[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"data_chunks", self.data_chunks[i]._parent, self)


    class Header(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.id_magic = self._io.read_bytes(4)
            if not (self.id_magic == b"\x52\x44\x4C\x58"):
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x44\x4C\x58", self.id_magic, self._io, u"/types/header/seq/0")
            self.id_magic_2 = self._io.read_u4le()
            self.size_decompressed = self._io.read_u4le()
            self.size_compressed = self._io.read_u4le()
            self.num_chunks = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lfs.Header, self)._write__seq(io)
            self._io.write_bytes(self.id_magic)
            self._io.write_u4le(self.id_magic_2)
            self._io.write_u4le(self.size_decompressed)
            self._io.write_u4le(self.size_compressed)
            self._io.write_u4le(self.num_chunks)


        def _check(self):
            pass
            if (len(self.id_magic) != 4):
                raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
            if not (self.id_magic == b"\x52\x44\x4C\x58"):
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x44\x4C\x58", self.id_magic, None, u"/types/header/seq/0")

        @property
        def size(self):
            if hasattr(self, '_m_size'):
                return self._m_size

            self._m_size = 20
            return getattr(self, '_m_size', None)

        def _invalidate_size(self):
            del self._m_size

    class DataChunk(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_chunk = False
            self.chunk__to_write = True

        def _read(self):
            self.size_compressed = self._io.read_u2le()
            self.size_decompressed = self._io.read_u2le()
            self.offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.chunk


        def _write__seq(self, io=None):
            super(Lfs.DataChunk, self)._write__seq(io)
            self._should_write_chunk = self.chunk__to_write
            self._io.write_u2le(self.size_compressed)
            self._io.write_u2le(self.size_decompressed)
            self._io.write_u4le(self.offset)


        def _check(self):
            pass

        @property
        def comp_offset(self):
            if hasattr(self, '_m_comp_offset'):
                return self._m_comp_offset

            self._m_comp_offset = (self.offset & ~1)
            return getattr(self, '_m_comp_offset', None)

        def _invalidate_comp_offset(self):
            del self._m_comp_offset
        @property
        def chunk(self):
            if self._should_write_chunk:
                self._write_chunk()
            if hasattr(self, '_m_chunk'):
                return self._m_chunk

            _pos = self._io.pos()
            self._io.seek((self.comp_offset + self._root.lfs_header.size))
            self._m_chunk = self._io.read_bytes(self.size_compressed)
            self._io.seek(_pos)
            return getattr(self, '_m_chunk', None)

        @chunk.setter
        def chunk(self, v):
            self._m_chunk = v

        def _write_chunk(self):
            self._should_write_chunk = False
            _pos = self._io.pos()
            self._io.seek((self.comp_offset + self._root.lfs_header.size))
            self._io.write_bytes(self.chunk)
            self._io.seek(_pos)


        def _check_chunk(self):
            pass
            if (len(self.chunk) != self.size_compressed):
                raise kaitaistruct.ConsistencyError(u"chunk", len(self.chunk), self.size_compressed)



