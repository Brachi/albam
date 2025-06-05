# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneSsg(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x06\x00\x00\x00"):
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
            self.files_info.append(HexaneSsg.FileInfo(self._io, self, self._root))

        self.chunk_sizes = []
        for i in range(self.size_chunks_info // 4):
            self.chunk_sizes.append(self._io.read_u4le())

        self.file_names = self._io.read_bytes(self.size_file_names)
        self.buffer_chunks = self._io.read_bytes(self.size_chunks_buffer)


    def _fetch_instances(self):
        pass
        for i in range(len(self.files_info)):
            pass
            self.files_info[i]._fetch_instances()

        for i in range(len(self.chunk_sizes)):
            pass


    class FileInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.ident = self._io.read_u4le()
            self.name_offset_rel = self._io.read_u4le()
            self.size = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.reserved_02 = self._io.read_u4le()
            self.file_type = self._io.read_s4le()
            self.unk_01 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.name

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((((32 + self._parent.size_files_info) + self._parent.size_chunks_info) + self.name_offset_rel))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode("ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)



