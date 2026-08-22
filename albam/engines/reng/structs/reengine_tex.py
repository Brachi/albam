# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineTex(ReadWriteKaitaiStruct):

    class DxgiFormat(IntEnum):
        unknown = 0
        r32g32b32a32_typeless = 1
        r32g32b32a32_float = 2
        r32g32b32a32_uint = 3
        r32g32b32a32_sint = 4
        r32g32b32_typeless = 5
        r32g32b32_float = 6
        r32g32b32_uint = 7
        r32g32b32_sint = 8
        r16g16b16a16_typeless = 9
        r16g16b16a16_float = 10
        r16g16b16a16_unorm = 11
        r16g16b16a16_uint = 12
        r16g16b16a16_snorm = 13
        r16g16b16a16_sint = 14
        r32g32_typeless = 15
        r32g32_float = 16
        r32g32_uint = 17
        r32g32_sint = 18
        r32g8x24_typeless = 19
        d32_float_s8x24_uint = 20
        r32_float_x8x24_typeless = 21
        x32_typeless_g8x24_uint = 22
        r10g10b10a2_typeless = 23
        r10g10b10a2_unorm = 24
        r10g10b10a2_uint = 25
        r11g11b10_float = 26
        r8g8b8a8_typeless = 27
        r8g8b8a8_unorm = 28
        r8g8b8a8_unorm_srgb = 29
        r8g8b8a8_uint = 30
        r8g8b8a8_snorm = 31
        r8g8b8a8_sint = 32
        r16g16_typeless = 33
        r16g16_float = 34
        r16g16_unorm = 35
        r16g16_uint = 36
        r16g16_snorm = 37
        r16g16_sint = 38
        r32_typeless = 39
        d32_float = 40
        r32_float = 41
        r32_uint = 42
        r32_sint = 43
        r24g8_typeless = 44
        d24_unorm_s8_uint = 45
        r24_unorm_x8_typeless = 46
        x24_typeless_g8_uint = 47
        r8g8_typeless = 48
        r8g8_unorm = 49
        r8g8_uint = 50
        r8g8_snorm = 51
        r8g8_sint = 52
        r16_typeless = 53
        r16_float = 54
        d16_unorm = 55
        r16_unorm = 56
        r16_uint = 57
        r16_snorm = 58
        r16_sint = 59
        r8_typeless = 60
        r8_unorm = 61
        r8_uint = 62
        r8_snorm = 63
        r8_sint = 64
        a8_unorm = 65
        r1_unorm = 66
        r9g9b9e5_sharedexp = 67
        r8g8_b8g8_unorm = 68
        g8r8_g8b8_unorm = 69
        bc1_typeless = 70
        bc1_unorm = 71
        bc1_unorm_srgb = 72
        bc2_typeless = 73
        bc2_unorm = 74
        bc2_unorm_srgb = 75
        bc3_typeless = 76
        bc3_unorm = 77
        bc3_unorm_srgb = 78
        bc4_typeless = 79
        bc4_unorm = 80
        bc4_snorm = 81
        bc5_typeless = 82
        bc5_unorm = 83
        bc5_snorm = 84
        b5g6r5_unorm = 85
        b5g5r5a1_unorm = 86
        b8g8r8a8_unorm = 87
        b8g8r8x8_unorm = 88
        r10g10b10_xr_bias_a2_unorm = 89
        b8g8r8a8_typeless = 90
        b8g8r8a8_unorm_srgb = 91
        b8g8r8x8_typeless = 92
        b8g8r8x8_unorm_srgb = 93
        bc6h_typeless = 94
        bc6h_uf16 = 95
        bc6h_sf16 = 96
        bc7_typeless = 97
        bc7_unorm = 98
        bc7_unorm_srgb = 99
    def __init__(self, _io=None, _parent=None, _root=None):
        super(ReengineTex, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.ident = self._io.read_bytes(4)
        if not self.ident == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.ident, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.width = self._io.read_u2le()
        self.height = self._io.read_u2le()
        self.depth = self._io.read_u2le()
        _on =  ((self.version > 11) and (self.version != 190820018)) 
        if _on == False:
            pass
            self.mipmap_header = ReengineTex.MipmapHeader1(self._io, self, self._root)
            self.mipmap_header._read()
        elif _on == True:
            pass
            self.mipmap_header = ReengineTex.MipmapHeader2(self._io, self, self._root)
            self.mipmap_header._read()
        self.format = KaitaiStream.resolve_enum(ReengineTex.DxgiFormat, self._io.read_u4le())
        self.swizzle_control = self._io.read_s4le()
        self.cubemap_marker = self._io.read_u4le()
        self.unk_04a = self._io.read_u1()
        self.unk_04b = self._io.read_u1()
        self.unk_05_null = self._io.read_u2le()
        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self.swizzle_height_depth = self._io.read_u1()

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self.swizzle_width = self._io.read_u1()

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self.unk_06_null = self._io.read_u2le()

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self.unk_07_seven = self._io.read_u2le()

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self.unk_08_one = self._io.read_u2le()

        self.mipmaps = []
        for i in range((self.mipmap_header.num_mipmaps if  ((self.version > 11) and (self.version != 190820018))  else self.mipmap_header.num_mipmaps)):
            _t_mipmaps = ReengineTex.MipmapData(self._io, self, self._root)
            try:
                _t_mipmaps._read()
            finally:
                self.mipmaps.append(_t_mipmaps)

        self._dirty = False


    def _fetch_instances(self):
        pass
        _on =  ((self.version > 11) and (self.version != 190820018)) 
        if _on == False:
            pass
            self.mipmap_header._fetch_instances()
        elif _on == True:
            pass
            self.mipmap_header._fetch_instances()
        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        for i in range(len(self.mipmaps)):
            pass
            self.mipmaps[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(ReengineTex, self)._write__seq(io)
        self._io.write_bytes(self.ident)
        self._io.write_u4le(self.version)
        self._io.write_u2le(self.width)
        self._io.write_u2le(self.height)
        self._io.write_u2le(self.depth)
        _on =  ((self.version > 11) and (self.version != 190820018)) 
        if _on == False:
            pass
            self.mipmap_header._write__seq(self._io)
        elif _on == True:
            pass
            self.mipmap_header._write__seq(self._io)
        self._io.write_u4le(int(self.format))
        self._io.write_s4le(self.swizzle_control)
        self._io.write_u4le(self.cubemap_marker)
        self._io.write_u1(self.unk_04a)
        self._io.write_u1(self.unk_04b)
        self._io.write_u2le(self.unk_05_null)
        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self._io.write_u1(self.swizzle_height_depth)

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self._io.write_u1(self.swizzle_width)

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self._io.write_u2le(self.unk_06_null)

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self._io.write_u2le(self.unk_07_seven)

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass
            self._io.write_u2le(self.unk_08_one)

        for i in range(len(self.mipmaps)):
            pass
            self.mipmaps[i]._write__seq(self._io)



    def _check(self):
        if len(self.ident) != 4:
            raise kaitaistruct.ConsistencyError(u"ident", 4, len(self.ident))
        if not self.ident == b"\x54\x45\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x54\x45\x58\x00", self.ident, None, u"/seq/0")
        _on =  ((self.version > 11) and (self.version != 190820018)) 
        if _on == False:
            pass
            if self.mipmap_header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self._root, self.mipmap_header._root)
            if self.mipmap_header._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self, self.mipmap_header._parent)
        elif _on == True:
            pass
            if self.mipmap_header._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self._root, self.mipmap_header._root)
            if self.mipmap_header._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmap_header", self, self.mipmap_header._parent)
        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if  ((self.version > 27) and (self.version != 190820018)) :
            pass

        if len(self.mipmaps) != (self.mipmap_header.num_mipmaps if  ((self.version > 11) and (self.version != 190820018))  else self.mipmap_header.num_mipmaps):
            raise kaitaistruct.ConsistencyError(u"mipmaps", (self.mipmap_header.num_mipmaps if  ((self.version > 11) and (self.version != 190820018))  else self.mipmap_header.num_mipmaps), len(self.mipmaps))
        for i in range(len(self.mipmaps)):
            pass
            if self.mipmaps[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"mipmaps", self._root, self.mipmaps[i]._root)
            if self.mipmaps[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"mipmaps", self, self.mipmaps[i]._parent)

        self._dirty = False

    class MipmapData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineTex.MipmapData, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_dds_data = False
            self.dds_data__enabled = True

        def _read(self):
            self.ofs_data = self._io.read_u8le()
            self.scanline_length = self._io.read_u4le()
            self.size_data = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.dds_data
            if hasattr(self, '_m_dds_data'):
                pass



        def _write__seq(self, io=None):
            super(ReengineTex.MipmapData, self)._write__seq(io)
            self._should_write_dds_data = self.dds_data__enabled
            self._io.write_u8le(self.ofs_data)
            self._io.write_u4le(self.scanline_length)
            self._io.write_u4le(self.size_data)


        def _check(self):
            if self.dds_data__enabled:
                pass
                if len(self._m_dds_data) != self.size_data:
                    raise kaitaistruct.ConsistencyError(u"dds_data", self.size_data, len(self._m_dds_data))

            self._dirty = False

        @property
        def dds_data(self):
            if self._should_write_dds_data:
                self._write_dds_data()
            if hasattr(self, '_m_dds_data'):
                return self._m_dds_data

            if not self.dds_data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_dds_data = self._io.read_bytes(self.size_data)
            self._io.seek(_pos)
            return getattr(self, '_m_dds_data', None)

        @dds_data.setter
        def dds_data(self, v):
            self._dirty = True
            self._m_dds_data = v

        def _write_dds_data(self):
            self._should_write_dds_data = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._io.write_bytes(self._m_dds_data)
            self._io.seek(_pos)


    class MipmapHeader1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineTex.MipmapHeader1, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_mipmaps = self._io.read_u1()
            self.num_images = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineTex.MipmapHeader1, self)._write__seq(io)
            self._io.write_u1(self.num_mipmaps)
            self._io.write_u1(self.num_images)


        def _check(self):
            self._dirty = False


    class MipmapHeader2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineTex.MipmapHeader2, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_images = self._io.read_u1()
            self.size_mipmap_header = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineTex.MipmapHeader2, self)._write__seq(io)
            self._io.write_u1(self.num_images)
            self._io.write_u1(self.size_mipmap_header)


        def _check(self):
            self._dirty = False

        @property
        def num_mipmaps(self):
            if hasattr(self, '_m_num_mipmaps'):
                return self._m_num_mipmaps

            self._m_num_mipmaps = self.size_mipmap_header // 16
            return getattr(self, '_m_num_mipmaps', None)

        def _invalidate_num_mipmaps(self):
            del self._m_num_mipmaps


