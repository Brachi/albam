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
        self.packed_data_3 = self._io.read_u4le()
        if self.num_images == 6:
            self.cube_faces = []
            for i in range(3):
                self.cube_faces.append(Tex157.CubeFace(self._io, self, self._root))


        self.mipmap_offsets = []
        for i in range((self.num_mipmaps_per_image * self.num_images)):
            self.mipmap_offsets.append(self._io.read_u4le())

        self.dds_data = self._io.read_bytes_full()

    class CubeFace(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.field_00 = self._io.read_f4le()
            self.negative_co = []
            for i in range(3):
                self.negative_co.append(self._io.read_f4le())

            self.positive_co = []
            for i in range(3):
                self.positive_co.append(self._io.read_f4le())

            self.uv = []
            for i in range(2):
                self.uv.append(self._io.read_f4le())


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)


    @property
    def num_mipmaps_per_image(self):
        if hasattr(self, '_m_num_mipmaps_per_image'):
            return self._m_num_mipmaps_per_image

        self._m_num_mipmaps_per_image = (self.packed_data_2 & 63)
        return getattr(self, '_m_num_mipmaps_per_image', None)

    @property
    def num_images(self):
        if hasattr(self, '_m_num_images'):
            return self._m_num_images

        self._m_num_images = (self.packed_data_3 & 255)
        return getattr(self, '_m_num_images', None)

    @property
    def height(self):
        if hasattr(self, '_m_height'):
            return self._m_height

        self._m_height = ((self.packed_data_2 >> 19) & 8191)
        return getattr(self, '_m_height', None)

    @property
    def constant(self):
        if hasattr(self, '_m_constant'):
            return self._m_constant

        self._m_constant = ((self.packed_data_3 >> 16) & 8191)
        return getattr(self, '_m_constant', None)

    @property
    def dimension(self):
        if hasattr(self, '_m_dimension'):
            return self._m_dimension

        self._m_dimension = ((self.packed_data_1 >> 28) & 15)
        return getattr(self, '_m_dimension', None)

    @property
    def width(self):
        if hasattr(self, '_m_width'):
            return self._m_width

        self._m_width = ((self.packed_data_2 >> 6) & 8191)
        return getattr(self, '_m_width', None)

    @property
    def compression_format(self):
        if hasattr(self, '_m_compression_format'):
            return self._m_compression_format

        self._m_compression_format = ((self.packed_data_3 >> 8) & 255)
        return getattr(self, '_m_compression_format', None)

    @property
    def reserved_01(self):
        if hasattr(self, '_m_reserved_01'):
            return self._m_reserved_01

        self._m_reserved_01 = ((self.packed_data_1 >> 16) & 255)
        return getattr(self, '_m_reserved_01', None)

    @property
    def type(self):
        if hasattr(self, '_m_type'):
            return self._m_type

        self._m_type = (self.packed_data_1 & 65535)
        return getattr(self, '_m_type', None)

    @property
    def reserved_02(self):
        if hasattr(self, '_m_reserved_02'):
            return self._m_reserved_02

        self._m_reserved_02 = ((self.packed_data_3 >> 29) & 3)
        return getattr(self, '_m_reserved_02', None)

    @property
    def shift(self):
        if hasattr(self, '_m_shift'):
            return self._m_shift

        self._m_shift = ((self.packed_data_1 >> 24) & 15)
        return getattr(self, '_m_shift', None)

    @property
    def size_before_data_(self):
        if hasattr(self, '_m_size_before_data_'):
            return self._m_size_before_data_

        self._m_size_before_data_ = ((16 + ((4 * self.num_mipmaps_per_image) * self.num_images)) if self.num_images == 1 else ((16 + ((4 * self.num_mipmaps_per_image) * self.num_images)) + (36 * 3)))
        return getattr(self, '_m_size_before_data_', None)


