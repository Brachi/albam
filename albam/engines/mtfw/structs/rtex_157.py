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


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(Rtex157, self)._write__seq(io)
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


    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x52\x54\x58\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x54\x58\x00", self.id_magic, None, u"/seq/0")

    @property
    def size_before_data_(self):
        if hasattr(self, '_m_size_before_data_'):
            return self._m_size_before_data_

        self._m_size_before_data_ = 16
        return getattr(self, '_m_size_before_data_', None)

    def _invalidate_size_before_data_(self):
        del self._m_size_before_data_

