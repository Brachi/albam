# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mfx(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Mfx, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

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
            _t_entry_pointers = Mfx.MfxEntryPointer(self._io, self, self._root)
            try:
                _t_entry_pointers._read()
            finally:
                self.entry_pointers.append(_t_entry_pointers)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.entry_pointers)):
            pass
            self.entry_pointers[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Mfx, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u2le(self.unk_01)
        self._io.write_u2le(self.unk_02)
        self._io.write_u4le(self.unk_03)
        self._io.write_u4le(self.num_entries)
        self._io.write_u4le(self.offset_string_table)
        self._io.write_u4le(self.unk_04)
        for i in range(len(self.entry_pointers)):
            pass
            self.entry_pointers[i]._write__seq(self._io)



    def _check(self):
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x4D\x46\x58\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x46\x58\x00", self.id_magic, None, u"/seq/0")
        if len(self.entry_pointers) != self.num_entries:
            raise kaitaistruct.ConsistencyError(u"entry_pointers", self.num_entries, len(self.entry_pointers))
        for i in range(len(self.entry_pointers)):
            pass
            if self.entry_pointers[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"entry_pointers", self._root, self.entry_pointers[i]._root)
            if self.entry_pointers[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"entry_pointers", self, self.entry_pointers[i]._parent)

        self._dirty = False

    class Attr0(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.Attr0, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_ofs = self._io.read_u4le()
            self.ofs_attr = self._io.read_u4le()
            self.ofs_floats = self._io.read_u4le()
            self.body = []
            for i in range(self._parent.num_attributes0):
                _t_body = Mfx.MfxAttribute0(self._io, self, self._root)
                try:
                    _t_body._read()
                finally:
                    self.body.append(_t_body)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.body)):
                pass
                self.body[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mfx.Attr0, self)._write__seq(io)
            self._io.write_u4le(self.unk_ofs)
            self._io.write_u4le(self.ofs_attr)
            self._io.write_u4le(self.ofs_floats)
            for i in range(len(self.body)):
                pass
                self.body[i]._write__seq(self._io)



        def _check(self):
            if len(self.body) != self._parent.num_attributes0:
                raise kaitaistruct.ConsistencyError(u"body", self._parent.num_attributes0, len(self.body))
            for i in range(len(self.body)):
                pass
                if self.body[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"body", self._root, self.body[i]._root)
                if self.body[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"body", self, self.body[i]._parent)

            self._dirty = False


    class Attr8(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.Attr8, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = self._io.read_u4le()
            self.body = []
            for i in range(self._parent.num_attributes):
                _t_body = Mfx.MfxAttribute8(self._io, self, self._root)
                try:
                    _t_body._read()
                finally:
                    self.body.append(_t_body)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.body)):
                pass
                self.body[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mfx.Attr8, self)._write__seq(io)
            self._io.write_u4le(self.header)
            for i in range(len(self.body)):
                pass
                self.body[i]._write__seq(self._io)



        def _check(self):
            if len(self.body) != self._parent.num_attributes:
                raise kaitaistruct.ConsistencyError(u"body", self._parent.num_attributes, len(self.body))
            for i in range(len(self.body)):
                pass
                if self.body[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"body", self._root, self.body[i]._root)
                if self.body[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"body", self, self.body[i]._parent)

            self._dirty = False


    class Attr9(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.Attr9, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = self._io.read_u4le()
            self.body = []
            for i in range(self._parent.num_attributes):
                _t_body = Mfx.MfxAttribute9(self._io, self, self._root)
                try:
                    _t_body._read()
                finally:
                    self.body.append(_t_body)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.body)):
                pass
                self.body[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mfx.Attr9, self)._write__seq(io)
            self._io.write_u4le(self.header)
            for i in range(len(self.body)):
                pass
                self.body[i]._write__seq(self._io)



        def _check(self):
            if len(self.body) != self._parent.num_attributes:
                raise kaitaistruct.ConsistencyError(u"body", self._parent.num_attributes, len(self.body))
            for i in range(len(self.body)):
                pass
                if self.body[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"body", self._root, self.body[i]._root)
                if self.body[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"body", self, self.body[i]._parent)

            self._dirty = False


    class MfxAttribute0(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.MfxAttribute0, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

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
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_b00 = self._io.read_u1()
            self.float_buff_ofs = self._io.read_u1()
            self.unk_b01 = self._io.read_u1()
            self.sub_attr_num = self._io.read_u1()
            self.sub_attr_ofs = self._io.read_u4le()
            self.unk_ofs = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_00)):
                pass

            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Mfx.MfxAttribute0, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.offset_name)
            for i in range(len(self.unk_00)):
                pass
                self._io.write_u2le(self.unk_00[i])

            self._io.write_bits_int_le(4, self.base_off)
            self._io.write_bits_int_le(4, self.count)
            self._io.write_bits_int_le(8, self.instancing)
            self._io.write_bits_int_le(8, self.unk_bit)
            self._io.write_bits_int_le(8, self.comp_count)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u1(self.unk_b00)
            self._io.write_u1(self.float_buff_ofs)
            self._io.write_u1(self.unk_b01)
            self._io.write_u1(self.sub_attr_num)
            self._io.write_u4le(self.sub_attr_ofs)
            self._io.write_u4le(self.unk_ofs)


        def _check(self):
            if len(self.unk_00) != 2:
                raise kaitaistruct.ConsistencyError(u"unk_00", 2, len(self.unk_00))
            for i in range(len(self.unk_00)):
                pass

            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class MfxAttribute8(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.MfxAttribute8, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_01 = self._io.read_bits_int_le(6)
            self.comp_type = self._io.read_bits_int_le(5)
            self.comp_count = self._io.read_bits_int_le(11)
            self.base_off = self._io.read_bits_int_le(9)
            self.instancing = self._io.read_bits_int_le(1) != 0
            self.unk_02 = []
            for i in range(5):
                self.unk_02.append(self._io.read_u4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_02)):
                pass

            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Mfx.MfxAttribute8, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.offset_name)
            self._io.write_bits_int_le(6, self.unk_01)
            self._io.write_bits_int_le(5, self.comp_type)
            self._io.write_bits_int_le(11, self.comp_count)
            self._io.write_bits_int_le(9, self.base_off)
            self._io.write_bits_int_le(1, int(self.instancing))
            for i in range(len(self.unk_02)):
                pass
                self._io.write_u4le(self.unk_02[i])



        def _check(self):
            if len(self.unk_02) != 5:
                raise kaitaistruct.ConsistencyError(u"unk_02", 5, len(self.unk_02))
            for i in range(len(self.unk_02)):
                pass

            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class MfxAttribute9(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.MfxAttribute9, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_01 = self._io.read_bits_int_le(6)
            self.comp_type = self._io.read_bits_int_le(5)
            self.comp_count = self._io.read_bits_int_le(11)
            self.base_off = self._io.read_bits_int_le(9)
            self.instancing = self._io.read_bits_int_le(1) != 0
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Mfx.MfxAttribute9, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.offset_name)
            self._io.write_bits_int_le(6, self.unk_01)
            self._io.write_bits_int_le(5, self.comp_type)
            self._io.write_bits_int_le(11, self.comp_count)
            self._io.write_bits_int_le(9, self.base_off)
            self._io.write_bits_int_le(1, int(self.instancing))


        def _check(self):
            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class MfxEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.MfxEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_friendly_name = False
            self.friendly_name__enabled = True
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.offset_string_1 = self._io.read_u4le()
            self.offset_string_2 = self._io.read_u4le()
            self.field_8_a = self._io.read_bits_int_le(6)
            self.field_8_b = self._io.read_bits_int_le(16)
            self.fill = self._io.read_bits_int_le(10)
            self.unk_01 = self._io.read_u2le()
            self.index = self._io.read_u2le()
            self.field_c = self._io.read_u4le()
            self.field_10 = self._io.read_u4le()
            self.num_attributes = self._io.read_u1()
            self.unk_02 = self._io.read_u1()
            self.num_attributes0 = self._io.read_u2le()
            _on = self.field_8_a
            if _on == 0:
                pass
                self.attributes = Mfx.Attr0(self._io, self, self._root)
                self.attributes._read()
            elif _on == 8:
                pass
                self.attributes = Mfx.Attr8(self._io, self, self._root)
                self.attributes._read()
            elif _on == 9:
                pass
                self.attributes = Mfx.Attr9(self._io, self, self._root)
                self.attributes._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self.field_8_a
            if _on == 0:
                pass
                self.attributes._fetch_instances()
            elif _on == 8:
                pass
                self.attributes._fetch_instances()
            elif _on == 9:
                pass
                self.attributes._fetch_instances()
            _ = self.friendly_name
            if hasattr(self, '_m_friendly_name'):
                pass

            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Mfx.MfxEntry, self)._write__seq(io)
            self._should_write_friendly_name = self.friendly_name__enabled
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.offset_string_1)
            self._io.write_u4le(self.offset_string_2)
            self._io.write_bits_int_le(6, self.field_8_a)
            self._io.write_bits_int_le(16, self.field_8_b)
            self._io.write_bits_int_le(10, self.fill)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.index)
            self._io.write_u4le(self.field_c)
            self._io.write_u4le(self.field_10)
            self._io.write_u1(self.num_attributes)
            self._io.write_u1(self.unk_02)
            self._io.write_u2le(self.num_attributes0)
            _on = self.field_8_a
            if _on == 0:
                pass
                self.attributes._write__seq(self._io)
            elif _on == 8:
                pass
                self.attributes._write__seq(self._io)
            elif _on == 9:
                pass
                self.attributes._write__seq(self._io)


        def _check(self):
            _on = self.field_8_a
            if _on == 0:
                pass
                if self.attributes._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attributes", self._root, self.attributes._root)
                if self.attributes._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attributes", self, self.attributes._parent)
            elif _on == 8:
                pass
                if self.attributes._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attributes", self._root, self.attributes._root)
                if self.attributes._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attributes", self, self.attributes._parent)
            elif _on == 9:
                pass
                if self.attributes._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attributes", self._root, self.attributes._root)
                if self.attributes._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attributes", self, self.attributes._parent)
            if self.friendly_name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_friendly_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"friendly_name", -1, KaitaiStream.byte_array_index_of((self._m_friendly_name).encode(u"ASCII"), 0))

            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def friendly_name(self):
            if self._should_write_friendly_name:
                self._write_friendly_name()
            if hasattr(self, '_m_friendly_name'):
                return self._m_friendly_name

            if not self.friendly_name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_string_2)
            self._m_friendly_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_friendly_name', None)

        @friendly_name.setter
        def friendly_name(self, v):
            self._dirty = True
            self._m_friendly_name = v

        def _write_friendly_name(self):
            self._should_write_friendly_name = False
            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_string_2)
            self._io.write_bytes((self._m_friendly_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_string_1)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_string_1)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class MfxEntryPointer(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.MfxEntryPointer, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_mfx_entry = False
            self.mfx_entry__enabled = True

        def _read(self):
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.mfx_entry
            if hasattr(self, '_m_mfx_entry'):
                pass
                self._m_mfx_entry._fetch_instances()



        def _write__seq(self, io=None):
            super(Mfx.MfxEntryPointer, self)._write__seq(io)
            self._should_write_mfx_entry = self.mfx_entry__enabled
            self._io.write_u4le(self.offset)


        def _check(self):
            if self.mfx_entry__enabled:
                pass
                if self._m_mfx_entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"mfx_entry", self._root, self._m_mfx_entry._root)
                if self._m_mfx_entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"mfx_entry", self, self._m_mfx_entry._parent)

            self._dirty = False

        @property
        def mfx_entry(self):
            if self._should_write_mfx_entry:
                self._write_mfx_entry()
            if hasattr(self, '_m_mfx_entry'):
                return self._m_mfx_entry

            if not self.mfx_entry__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_mfx_entry = Mfx.MfxEntry(self._io, self, self._root)
            self._m_mfx_entry._read()
            self._io.seek(_pos)
            return getattr(self, '_m_mfx_entry', None)

        @mfx_entry.setter
        def mfx_entry(self, v):
            self._dirty = True
            self._m_mfx_entry = v

        def _write_mfx_entry(self):
            self._should_write_mfx_entry = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_mfx_entry._write__seq(self._io)
            self._io.seek(_pos)


    class SubAttr0(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Mfx.SubAttr0, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.offset_name = self._io.read_u4le()
            self.unk_00 = self._io.read_u4le()
            self.base_off = self._io.read_bits_int_le(4)
            self.instancing = self._io.read_bits_int_le(4)
            self.unk = self._io.read_bits_int_le(8)
            self.count = self._io.read_bits_int_le(8)
            self.comp_count = self._io.read_bits_int_le(8)
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u4le()
            self.unk_ofs_00 = self._io.read_u4le()
            self.unk_ofs_01 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Mfx.SubAttr0, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.offset_name)
            self._io.write_u4le(self.unk_00)
            self._io.write_bits_int_le(4, self.base_off)
            self._io.write_bits_int_le(4, self.instancing)
            self._io.write_bits_int_le(8, self.unk)
            self._io.write_bits_int_le(8, self.count)
            self._io.write_bits_int_le(8, self.comp_count)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u4le(self.unk_03)
            self._io.write_u4le(self.unk_ofs_00)
            self._io.write_u4le(self.unk_ofs_01)


        def _check(self):
            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self._root.offset_string_table + self.offset_name)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)



