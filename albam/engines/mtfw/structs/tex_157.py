# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tex157(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x54\x45\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.packed_data_1 = self._io.read_u4le()
        self.packed_data_2 = self._io.read_u4le()
        self.packed_data_3 = self._io.read_u4le()
        if (self.num_images == 6):
            pass
            self.cube_faces = []
            for i in range(3):
                _t_cube_faces = Tex157.CubeFace(self._io, self, self._root)
                _t_cube_faces._read()
                self.cube_faces.append(_t_cube_faces)


        self.mipmap_offsets = []
        for i in range((self.num_mipmaps_per_image * self.num_images)):
            self.mipmap_offsets.append(self._io.read_u4le())

        self.dds_data = self._io.read_bytes_full()


    def _fetch_instances(self):
        pass
        if (self.num_images == 6):
            pass
            for i in range(len(self.cube_faces)):
                pass
                self.cube_faces[i]._fetch_instances()


        for i in range(len(self.mipmap_offsets)):
            pass



    def _write__seq(self, io=None):
        super(Tex157, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u4le(self.packed_data_1)
        self._io.write_u4le(self.packed_data_2)
        self._io.write_u4le(self.packed_data_3)
        if (self.num_images == 6):
            pass
            for i in range(len(self.cube_faces)):
                pass
                self.cube_faces[i]._write__seq(self._io)


        for i in range(len(self.mipmap_offsets)):
            pass
            self._io.write_u4le(self.mipmap_offsets[i])

        self._io.write_bytes(self.dds_data)
        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"dds_data", self._io.size() - self._io.pos(), 0)


    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x54\x45\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, None, u"/seq/0")
        if (self.num_images == 6):
            pass
            if (len(self.cube_faces) != 3):
                raise kaitaistruct.ConsistencyError(u"cube_faces", len(self.cube_faces), 3)
            for i in range(len(self.cube_faces)):
                pass
                if self.cube_faces[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"cube_faces", self.cube_faces[i]._root, self._root)
                if self.cube_faces[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"cube_faces", self.cube_faces[i]._parent, self)


        if (len(self.mipmap_offsets) != (self.num_mipmaps_per_image * self.num_images)):
            raise kaitaistruct.ConsistencyError(u"mipmap_offsets", len(self.mipmap_offsets), (self.num_mipmaps_per_image * self.num_images))
        for i in range(len(self.mipmap_offsets)):
            pass


    class CubeFace(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

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



        def _fetch_instances(self):
            pass
            for i in range(len(self.negative_co)):
                pass

            for i in range(len(self.positive_co)):
                pass

            for i in range(len(self.uv)):
                pass



        def _write__seq(self, io=None):
            super(Tex157.CubeFace, self)._write__seq(io)
            self._io.write_f4le(self.field_00)
            for i in range(len(self.negative_co)):
                pass
                self._io.write_f4le(self.negative_co[i])

            for i in range(len(self.positive_co)):
                pass
                self._io.write_f4le(self.positive_co[i])

            for i in range(len(self.uv)):
                pass
                self._io.write_f4le(self.uv[i])



        def _check(self):
            pass
            if (len(self.negative_co) != 3):
                raise kaitaistruct.ConsistencyError(u"negative_co", len(self.negative_co), 3)
            for i in range(len(self.negative_co)):
                pass

            if (len(self.positive_co) != 3):
                raise kaitaistruct.ConsistencyError(u"positive_co", len(self.positive_co), 3)
            for i in range(len(self.positive_co)):
                pass

            if (len(self.uv) != 2):
                raise kaitaistruct.ConsistencyError(u"uv", len(self.uv), 2)
            for i in range(len(self.uv)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

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

