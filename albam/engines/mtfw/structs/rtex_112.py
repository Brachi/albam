# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Rtex112(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x52\x54\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x54\x58\x00", self.id_magic, self._io, u"/seq/0")
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


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(Rtex112, self)._write__seq(io)
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


    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x52\x54\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x54\x58\x00", self.id_magic, None, u"/seq/0")
        if (len((self.compression_format).encode(u"ASCII")) != 4):
            raise kaitaistruct.ConsistencyError(u"compression_format", len((self.compression_format).encode(u"ASCII")), 4)

    @property
    def size_before_data_(self):
        if hasattr(self, '_m_size_before_data_'):
            return self._m_size_before_data_

        self._m_size_before_data_ = 40
        return getattr(self, '_m_size_before_data_', None)

    def _invalidate_size_before_data_(self):
        del self._m_size_before_data_

