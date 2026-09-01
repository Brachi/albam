# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lfs(ReadWriteKaitaiStruct):
    """An .lfs is a compression wrapper, not a file archive: it holds exactly one
    payload, split into fixed-size chunks that are each compressed on their own.
    What the payload *is* comes from the extension the file name carries before
    ".lfs" - "r20d.udas.lfs" is a UDAS container, "icon_u.tpl.lfs" is a single
    TPL (see albam/engines/cie/fs.py).
    
    Every chunk decompresses to 0x10000 bytes except the last, and both size
    fields are u2, so a full-size chunk is stored as 0 in them. Across a real
    install (350907 chunks) `size_decompressed` is 0 for 346438 of them and
    `size_compressed` is never 0, compressed chunks always coming out smaller
    than the chunk size.
    
    Chunks are not necessarily compressed. The low bit of `offset` is the
    compressed flag and the rest is the chunk's own position, measured from the
    start of the chunk table (that is, from byte 20, past this header). A chunk
    with the bit clear is stored: its bytes are the payload's, verbatim. Real
    game data almost never uses this - exactly one chunk in the whole install is
    stored - but the game's own loader accepts it, which is what lets albam
    write an .lfs without implementing an LZX encoder.
    """
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Lfs, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Lfs.LfsHeader(self._io, self, self._root)
        self.header._read()
        self.chunks = []
        for i in range(self.header.num_chunks):
            _t_chunks = Lfs.Chunk(self._io, self, self._root)
            try:
                _t_chunks._read()
            finally:
                self.chunks.append(_t_chunks)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.chunks)):
            pass
            self.chunks[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Lfs, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.chunks)):
            pass
            self.chunks[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.chunks) != self.header.num_chunks:
            raise kaitaistruct.ConsistencyError(u"chunks", self.header.num_chunks, len(self.chunks))
        for i in range(len(self.chunks)):
            pass
            if self.chunks[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"chunks", self._root, self.chunks[i]._root)
            if self.chunks[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"chunks", self, self.chunks[i]._parent)

        self._dirty = False

    class Chunk(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lfs.Chunk, self).__init__(_io)
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
            super(Lfs.Chunk, self)._write__seq(io)
            self._should_write_raw_data = self.raw_data__enabled
            self._io.write_u2le(self.size_compressed)
            self._io.write_u2le(self.size_decompressed)
            self._io.write_u4le(self.offset)


        def _check(self):
            if self.raw_data__enabled:
                pass
                if len(self._m_raw_data) != self.len_raw_data:
                    raise kaitaistruct.ConsistencyError(u"raw_data", self.len_raw_data, len(self._m_raw_data))

            self._dirty = False

        @property
        def is_compressed(self):
            if hasattr(self, '_m_is_compressed'):
                return self._m_is_compressed

            self._m_is_compressed = self.offset & 1 != 0
            return getattr(self, '_m_is_compressed', None)

        def _invalidate_is_compressed(self):
            del self._m_is_compressed
        @property
        def len_raw_data(self):
            if hasattr(self, '_m_len_raw_data'):
                return self._m_len_raw_data

            self._m_len_raw_data = (65536 if self.size_compressed == 0 else self.size_compressed)
            return getattr(self, '_m_len_raw_data', None)

        def _invalidate_len_raw_data(self):
            del self._m_len_raw_data
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
            self._m_raw_data = self._io.read_bytes(self.len_raw_data)
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
            self.num_chunks = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lfs.LfsHeader, self)._write__seq(io)
            self._io.write_bytes(self.id_magic)
            self._io.write_u4le(self.file_id)
            self._io.write_u4le(self.size_decompressed)
            self._io.write_u4le(self.size_compressed)
            self._io.write_u4le(self.num_chunks)


        def _check(self):
            if len(self.id_magic) != 4:
                raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
            if not self.id_magic == b"\x52\x44\x4C\x58":
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x44\x4C\x58", self.id_magic, None, u"/types/lfs_header/seq/0")
            self._dirty = False



