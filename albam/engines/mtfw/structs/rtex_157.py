# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Rtex157(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x52\x54\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x54\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.packed_data_1 = self._io.read_u4le()
        self.packed_data_2 = self._io.read_u4le()
        self.packed_data_3 = self._io.read_u4le()


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(Rtex157, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u4le(self.packed_data_1)
        self._io.write_u4le(self.packed_data_2)
        self._io.write_u4le(self.packed_data_3)


    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x52\x54\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x54\x58\x00", self.id_magic, None, u"/seq/0")

    @property
    def num_mipmaps_per_image(self):
        if hasattr(self, '_m_num_mipmaps_per_image'):
            return self._m_num_mipmaps_per_image

        self._m_num_mipmaps_per_image = (self.packed_data_2 & 63)
        return getattr(self, '_m_num_mipmaps_per_image', None)

    def _invalidate_num_mipmaps_per_image(self):
        del self._m_num_mipmaps_per_image
    @property
    def num_images(self):
        if hasattr(self, '_m_num_images'):
            return self._m_num_images

        self._m_num_images = (self.packed_data_3 & 255)
        return getattr(self, '_m_num_images', None)

    def _invalidate_num_images(self):
        del self._m_num_images
    @property
    def height(self):
        if hasattr(self, '_m_height'):
            return self._m_height

        self._m_height = ((self.packed_data_2 >> 19) & 8191)
        return getattr(self, '_m_height', None)

    def _invalidate_height(self):
        del self._m_height
    @property
    def constant(self):
        if hasattr(self, '_m_constant'):
            return self._m_constant

        self._m_constant = ((self.packed_data_3 >> 16) & 8191)
        return getattr(self, '_m_constant', None)

    def _invalidate_constant(self):
        del self._m_constant
    @property
    def unk_type(self):
        if hasattr(self, '_m_unk_type'):
            return self._m_unk_type

        self._m_unk_type = (self.packed_data_1 & 65535)
        return getattr(self, '_m_unk_type', None)

    def _invalidate_unk_type(self):
        del self._m_unk_type
    @property
    def dimension(self):
        if hasattr(self, '_m_dimension'):
            return self._m_dimension

        self._m_dimension = ((self.packed_data_1 >> 28) & 15)
        return getattr(self, '_m_dimension', None)

    def _invalidate_dimension(self):
        del self._m_dimension
    @property
    def width(self):
        if hasattr(self, '_m_width'):
            return self._m_width

        self._m_width = ((self.packed_data_2 >> 6) & 8191)
        return getattr(self, '_m_width', None)

    def _invalidate_width(self):
        del self._m_width
    @property
    def compression_format(self):
        if hasattr(self, '_m_compression_format'):
            return self._m_compression_format

        self._m_compression_format = ((self.packed_data_3 >> 8) & 255)
        return getattr(self, '_m_compression_format', None)

    def _invalidate_compression_format(self):
        del self._m_compression_format
    @property
    def reserved_01(self):
        if hasattr(self, '_m_reserved_01'):
            return self._m_reserved_01

        self._m_reserved_01 = ((self.packed_data_1 >> 16) & 255)
        return getattr(self, '_m_reserved_01', None)

    def _invalidate_reserved_01(self):
        del self._m_reserved_01
    @property
    def reserved_02(self):
        if hasattr(self, '_m_reserved_02'):
            return self._m_reserved_02

        self._m_reserved_02 = ((self.packed_data_3 >> 29) & 3)
        return getattr(self, '_m_reserved_02', None)

    def _invalidate_reserved_02(self):
        del self._m_reserved_02
    @property
    def shift(self):
        if hasattr(self, '_m_shift'):
            return self._m_shift

        self._m_shift = ((self.packed_data_1 >> 24) & 15)
        return getattr(self, '_m_shift', None)

    def _invalidate_shift(self):
        del self._m_shift
    @property
    def size_before_data_(self):
        if hasattr(self, '_m_size_before_data_'):
            return self._m_size_before_data_

        self._m_size_before_data_ = ((16 + ((4 * self.num_mipmaps_per_image) * self.num_images)) if (self.num_images == 1) else ((16 + ((4 * self.num_mipmaps_per_image) * self.num_images)) + (36 * 3)))
        return getattr(self, '_m_size_before_data_', None)

    def _invalidate_size_before_data_(self):
        del self._m_size_before_data_

