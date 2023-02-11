# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tex157(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.packed_data_1 = self._io.read_u4le()
        self.packed_data_2 = self._io.read_u4le()
        self.num_images = self._io.read_u1()
        self.compression_format = self._io.read_u1()
        self.unk_01 = self._io.read_u1()
        self.unk_02 = self._io.read_u1()
        self.mipmap_offsets = []
        for i in range((self.num_mipmaps_per_image * self.num_images)):
            self.mipmap_offsets.append(self._io.read_u4le())

        self.dds_data = self._io.read_bytes_full()

    @property
    def num_mipmaps_per_image(self):
        if hasattr(self, '_m_num_mipmaps_per_image'):
            return self._m_num_mipmaps_per_image

        self._m_num_mipmaps_per_image = (self.packed_data_2 & 63)
        return getattr(self, '_m_num_mipmaps_per_image', None)

    @property
    def width(self):
        if hasattr(self, '_m_width'):
            return self._m_width

        self._m_width = ((self.packed_data_2 >> 6) & 8191)
        return getattr(self, '_m_width', None)

    @property
    def height(self):
        if hasattr(self, '_m_height'):
            return self._m_height

        self._m_height = ((self.packed_data_2 >> 19) & 8191)
        return getattr(self, '_m_height', None)


