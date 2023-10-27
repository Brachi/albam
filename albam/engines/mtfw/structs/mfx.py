# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mfx(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x46\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x46\x58\x00", self.id_magic, self._io, u"/seq/0")
        self.unk_01 = self._io.read_u2le()
        self.unk_02 = self._io.read_u2le()
        self.unk_03 = self._io.read_u4le()
        self.num_entries = self._io.read_u4le()
        self.offset_string_table = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        self.entry_pointers = []
        for i in range(self.num_entries):
            self.entry_pointers.append(Mfx.MfxEntryPointer(self._io, self, self._root))


    class Attr0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_ofs = self._io.read_u4le()
            self.ofs_attr = self._io.read_u4le()
            self.ofs_floats = self._io.read_u4le()
            self.body = []
            for i in range(self._parent.num_attributes0):
                self.body.append(Mfx.MfxAttribute0(self._io, self, self._root))



    class SubAttr0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_00 = self._io.read_u4le()
            self.base_off = self._io.read_bits_int_le(4)
            self.instancing = self._io.read_bits_int_le(4)
            self.unk = self._io.read_bits_int_le(8)
            self.count = self._io.read_bits_int_le(8)
            self.comp_count = self._io.read_bits_int_le(8)
            self._io.align_to_byte()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u4le()
            self.unk_ofs_00 = self._io.read_u4le()
            self.unk_ofs_01 = self._io.read_u4le()

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self._root.offset_string_table + self.offset_name))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    class Attr8(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_u4le()
            self.body = []
            for i in range(self._parent.num_attributes):
                self.body.append(Mfx.MfxAttribute8(self._io, self, self._root))



    class MfxAttribute8(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_01 = self._io.read_bits_int_le(6)
            self.comp_type = self._io.read_bits_int_le(5)
            self.comp_count = self._io.read_bits_int_le(11)
            self.base_off = self._io.read_bits_int_le(9)
            self.instancing = self._io.read_bits_int_le(1) != 0
            self._io.align_to_byte()
            self.unk_02 = []
            for i in range(5):
                self.unk_02.append(self._io.read_u4le())


        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self._root.offset_string_table + self.offset_name))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    class MfxAttribute0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_00 = []
            for i in range(2):
                self.unk_00.append(self._io.read_u2le())

            self.base_off = self._io.read_bits_int_le(4)
            self.count = self._io.read_bits_int_le(4)
            self.instancing = self._io.read_bits_int_le(8)
            self.unk_bit = self._io.read_bits_int_le(8)
            self.comp_count = self._io.read_bits_int_le(8)
            self._io.align_to_byte()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_b00 = self._io.read_u1()
            self.float_buff_ofs = self._io.read_u1()
            self.unk_b01 = self._io.read_u1()
            self.sub_attr_num = self._io.read_u1()
            self.sub_attr_ofs = self._io.read_u4le()
            self.unk_ofs = self._io.read_u4le()

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self._root.offset_string_table + self.offset_name))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    class Attr9(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_u4le()
            self.body = []
            for i in range(self._parent.num_attributes):
                self.body.append(Mfx.MfxAttribute9(self._io, self, self._root))



    class MfxAttribute9(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_01 = self._io.read_bits_int_le(6)
            self.comp_type = self._io.read_bits_int_le(5)
            self.comp_count = self._io.read_bits_int_le(11)
            self.base_off = self._io.read_bits_int_le(9)
            self.instancing = self._io.read_bits_int_le(1) != 0

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self._root.offset_string_table + self.offset_name))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    class MfxEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_string_1 = self._io.read_u4le()
            self.offset_string_2 = self._io.read_u4le()
            self.field_8_a = self._io.read_bits_int_le(6)
            self.field_8_b = self._io.read_bits_int_le(16)
            self.fill = self._io.read_bits_int_le(10)
            self._io.align_to_byte()
            self.unk_01 = self._io.read_u2le()
            self.index = self._io.read_u2le()
            self.field_c = self._io.read_u4le()
            self.field_10 = self._io.read_u4le()
            self.num_attributes = self._io.read_u1()
            self.unk_02 = self._io.read_u1()
            self.num_attributes0 = self._io.read_u2le()
            _on = self.field_8_a
            if _on == 8:
                self.attributes = Mfx.Attr8(self._io, self, self._root)
            elif _on == 9:
                self.attributes = Mfx.Attr9(self._io, self, self._root)
            elif _on == 0:
                self.attributes = Mfx.Attr0(self._io, self, self._root)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self._root.offset_string_table + self.offset_string_1))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @property
        def friendly_name(self):
            if hasattr(self, '_m_friendly_name'):
                return self._m_friendly_name

            _pos = self._io.pos()
            self._io.seek((self._root.offset_string_table + self.offset_string_2))
            self._m_friendly_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_friendly_name', None)


    class MfxEntryPointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_u4le()

        @property
        def mfx_entry(self):
            if hasattr(self, '_m_mfx_entry'):
                return self._m_mfx_entry

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_mfx_entry = Mfx.MfxEntry(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_mfx_entry', None)



