# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tex112(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.revision = self._io.read_u2le()
        self.num_mipmaps_per_image = self._io.read_u1()
        self.num_images = self._io.read_u1()
        self.unk_02 = self._io.read_u1()
        self.unk_03 = self._io.read_u1()
        self.width = self._io.read_u2le()
        self.height = self._io.read_u2le()
        self.reserved = self._io.read_u4le()
        self.compression_format = (self._io.read_bytes(4)).decode(u"ascii")
        self.red = self._io.read_f4le()
        self.green = self._io.read_f4le()
        self.blue = self._io.read_f4le()
        self.alpha = self._io.read_f4le()
        if self.num_images > 1:
            self.unk_offset = []
            for i in range(27):
                self.unk_offset.append(self._io.read_u4le())


        self.offsets_mipmaps = []
        for i in range((self.num_mipmaps_per_image * self.num_images)):
            self.offsets_mipmaps.append(self._io.read_u4le())

        self.dds_data = self._io.read_bytes_full()


