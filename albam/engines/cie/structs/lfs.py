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
    fields are u2. That is one byte too narrow for a full chunk, so both are
    stored **modulo 0x10000**: `size_decompressed` reads 0 for a full chunk
    (346438 of 350907 across a real install), and `size_compressed` wraps for a
    chunk that barely compresses - one whose real compressed size is 65564
    reads as 28. A chunk's real size can only be recovered from the distance to
    the next chunk, which is why albam/engines/cie/lfs_decompress.py slices the
    chunk data rather than this declaring a size for it. Chunks are padded to
    16 bytes, the last one not being padded at all.
    
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

        def _read(self):
            self.size_compressed = self._io.read_u2le()
            self.size_decompressed = self._io.read_u2le()
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lfs.Chunk, self)._write__seq(io)
            self._io.write_u2le(self.size_compressed)
            self._io.write_u2le(self.size_decompressed)
            self._io.write_u4le(self.offset)


        def _check(self):
            self._dirty = False

        @property
        def data_offset(self):
            if hasattr(self, '_m_data_offset'):
                return self._m_data_offset

            self._m_data_offset = (self.offset & ~1) + 20
            return getattr(self, '_m_data_offset', None)

        def _invalidate_data_offset(self):
            del self._m_data_offset
        @property
        def is_compressed(self):
            if hasattr(self, '_m_is_compressed'):
                return self._m_is_compressed

            self._m_is_compressed = self.offset & 1 != 0
            return getattr(self, '_m_is_compressed', None)

        def _invalidate_is_compressed(self):
            del self._m_is_compressed

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



