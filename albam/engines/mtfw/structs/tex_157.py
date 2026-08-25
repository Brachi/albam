# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tex157(KaitaiStruct):
    def __init__(self, app_id, _io, _parent=None, _root=None):
        super(Tex157, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self.app_id = app_id
        self._read()

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
                self.cube_faces.append(Tex157.CubeFace(self._io, self, self._root))


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


    class CubeFace(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Tex157.CubeFace, self).__init__(_io)
            self._parent = _parent
            self._root = _root
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



        def _fetch_instances(self):
            pass
            for i in range(len(self.negative_co)):
                pass

            for i in range(len(self.positive_co)):
                pass

            for i in range(len(self.uv)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)


    @property
    def size_before_data_(self):
        if hasattr(self, '_m_size_before_data_'):
            return self._m_size_before_data_

        self._m_size_before_data_ = (16 + (self.size_mipmap_offset * self.num_mipmaps_per_image) * self.num_images if self.num_images == 1 else (16 + (4 * self.num_mipmaps_per_image) * self.num_images) + 36 * 3)
        return getattr(self, '_m_size_before_data_', None)

    @property
    def size_mipmap_offset(self):
        if hasattr(self, '_m_size_mipmap_offset'):
            return self._m_size_mipmap_offset

        self._m_size_mipmap_offset = (8 if self._root.use_64bit_ofs == True else 4)
        return getattr(self, '_m_size_mipmap_offset', None)

    @property
    def use_64bit_ofs(self):
        if hasattr(self, '_m_use_64bit_ofs'):
            return self._m_use_64bit_ofs

        self._m_use_64bit_ofs = self._root.app_id == u"umvc3"
        return getattr(self, '_m_use_64bit_ofs', None)


