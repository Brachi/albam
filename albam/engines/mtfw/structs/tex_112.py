# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tex112(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x54\x45\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.texture_type = self._io.read_bits_int_le(4)
        self.encoded_type = self._io.read_bits_int_le(4)
        self.depend_screen = self._io.read_bits_int_le(1) != 0
        self.render_target = self._io.read_bits_int_le(1) != 0
        self.attr = self._io.read_bits_int_le(6)
        self.num_mipmaps_per_image = self._io.read_u1()
        self.num_images = self._io.read_u1()
        self.padding = self._io.read_u2le()
        self.width = self._io.read_u2le()
        self.height = self._io.read_u2le()
        self.depth = self._io.read_u4le()
        self.compression_format = (self._io.read_bytes(4)).decode("ASCII")
        self.red = self._io.read_f4le()
        self.green = self._io.read_f4le()
        self.blue = self._io.read_f4le()
        self.alpha = self._io.read_f4le()
        if (self.num_images == 6):
            pass
            self.cube_faces = []
            for i in range(3):
                _t_cube_faces = Tex112.CubeFace(self._io, self, self._root)
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
        super(Tex112, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u2le(self.version)
        self._io.write_bits_int_le(4, self.texture_type)
        self._io.write_bits_int_le(4, self.encoded_type)
        self._io.write_bits_int_le(1, int(self.depend_screen))
        self._io.write_bits_int_le(1, int(self.render_target))
        self._io.write_bits_int_le(6, self.attr)
        self._io.write_u1(self.num_mipmaps_per_image)
        self._io.write_u1(self.num_images)
        self._io.write_u2le(self.padding)
        self._io.write_u2le(self.width)
        self._io.write_u2le(self.height)
        self._io.write_u4le(self.depth)
        self._io.write_bytes((self.compression_format).encode(u"ASCII"))
        self._io.write_f4le(self.red)
        self._io.write_f4le(self.green)
        self._io.write_f4le(self.blue)
        self._io.write_f4le(self.alpha)
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
        if (len((self.compression_format).encode(u"ASCII")) != 4):
            raise kaitaistruct.ConsistencyError(u"compression_format", len((self.compression_format).encode(u"ASCII")), 4)
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
            super(Tex112.CubeFace, self)._write__seq(io)
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
    def size_before_data_(self):
        if hasattr(self, '_m_size_before_data_'):
            return self._m_size_before_data_

        self._m_size_before_data_ = ((40 + ((4 * self.num_mipmaps_per_image) * self.num_images)) if (self.num_images == 1) else ((40 + ((4 * self.num_mipmaps_per_image) * self.num_images)) + 108))
        return getattr(self, '_m_size_before_data_', None)

    def _invalidate_size_before_data_(self):
        del self._m_size_before_data_

