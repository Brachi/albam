# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tex157(ReadWriteKaitaiStruct):
    def __init__(self, use_64bit_ofs, _io=None, _parent=None, _root=None):
        super(Tex157, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self.use_64bit_ofs = use_64bit_ofs

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_bits_int_le(8)
        self.unk = self._io.read_bits_int_le(8)
        self.attr = self._io.read_bits_int_le(8)
        self.prebias = self._io.read_bits_int_le(4)
        self.type = self._io.read_bits_int_le(4)
        self.num_mipmaps_per_image = self._io.read_bits_int_le(6)
        self.width = self._io.read_bits_int_le(13)
        self.height = self._io.read_bits_int_le(13)
        self.num_images = self._io.read_bits_int_le(8)
        self.compression_format = self._io.read_bits_int_le(8)
        self.depth = self._io.read_bits_int_le(13)
        self.auto_resize = self._io.read_bits_int_le(1) != 0
        self.render_target = self._io.read_bits_int_le(1) != 0
        self.use_vtf = self._io.read_bits_int_le(1) != 0
        if self.num_images == 6:
            pass
            self.cube_faces = []
            for i in range(3):
                _t_cube_faces = Tex157.CubeFace(self._io, self, self._root)
                try:
                    _t_cube_faces._read()
                finally:
                    self.cube_faces.append(_t_cube_faces)


        self.mipmap_offsets = []
        for i in range(self.num_mipmaps_per_image * self.num_images):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.mipmap_offsets.append(self._io.read_u4le())
            elif _on == True:
                pass
                self.mipmap_offsets.append(self._io.read_u8le())
            else:
                pass
                self.mipmap_offsets.append(self._io.read_u4le())

        self.dds_data = self._io.read_bytes_full()
        self._dirty = False


    def _fetch_instances(self):
        pass
        if self.num_images == 6:
            pass
            for i in range(len(self.cube_faces)):
                pass
                self.cube_faces[i]._fetch_instances()


        for i in range(len(self.mipmap_offsets)):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass



    def _write__seq(self, io=None):
        super(Tex157, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_bits_int_le(8, self.version)
        self._io.write_bits_int_le(8, self.unk)
        self._io.write_bits_int_le(8, self.attr)
        self._io.write_bits_int_le(4, self.prebias)
        self._io.write_bits_int_le(4, self.type)
        self._io.write_bits_int_le(6, self.num_mipmaps_per_image)
        self._io.write_bits_int_le(13, self.width)
        self._io.write_bits_int_le(13, self.height)
        self._io.write_bits_int_le(8, self.num_images)
        self._io.write_bits_int_le(8, self.compression_format)
        self._io.write_bits_int_le(13, self.depth)
        self._io.write_bits_int_le(1, int(self.auto_resize))
        self._io.write_bits_int_le(1, int(self.render_target))
        self._io.write_bits_int_le(1, int(self.use_vtf))
        if self.num_images == 6:
            pass
            for i in range(len(self.cube_faces)):
                pass
                self.cube_faces[i]._write__seq(self._io)


        for i in range(len(self.mipmap_offsets)):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.mipmap_offsets[i])
            elif _on == True:
                pass
                self._io.write_u8le(self.mipmap_offsets[i])
            else:
                pass
                self._io.write_u4le(self.mipmap_offsets[i])

        self._io.write_bytes(self.dds_data)
        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"dds_data", 0, self._io.size() - self._io.pos())


    def _check(self):
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, None, u"/seq/0")
        if self.num_images == 6:
            pass
            if len(self.cube_faces) != 3:
                raise kaitaistruct.ConsistencyError(u"cube_faces", 3, len(self.cube_faces))
            for i in range(len(self.cube_faces)):
                pass
                if self.cube_faces[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"cube_faces", self._root, self.cube_faces[i]._root)
                if self.cube_faces[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"cube_faces", self, self.cube_faces[i]._parent)


        if len(self.mipmap_offsets) != self.num_mipmaps_per_image * self.num_images:
            raise kaitaistruct.ConsistencyError(u"mipmap_offsets", self.num_mipmaps_per_image * self.num_images, len(self.mipmap_offsets))
        for i in range(len(self.mipmap_offsets)):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass

        self._dirty = False

    class CubeFace(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Tex157.CubeFace, self).__init__(_io)
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

            self._dirty = False


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
            if len(self.negative_co) != 3:
                raise kaitaistruct.ConsistencyError(u"negative_co", 3, len(self.negative_co))
            for i in range(len(self.negative_co)):
                pass

            if len(self.positive_co) != 3:
                raise kaitaistruct.ConsistencyError(u"positive_co", 3, len(self.positive_co))
            for i in range(len(self.positive_co)):
                pass

            if len(self.uv) != 2:
                raise kaitaistruct.ConsistencyError(u"uv", 2, len(self.uv))
            for i in range(len(self.uv)):
                pass

            self._dirty = False

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

        self._m_size_before_data_ = (16 + (4 * self.num_mipmaps_per_image) * self.num_images if self.num_images == 1 else (16 + (4 * self.num_mipmaps_per_image) * self.num_images) + 36 * 3)
        return getattr(self, '_m_size_before_data_', None)

    def _invalidate_size_before_data_(self):
        del self._m_size_before_data_

