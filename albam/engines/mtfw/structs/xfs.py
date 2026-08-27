# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Xfs(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Xfs, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_data_buffer = False
        self.data_buffer__enabled = True
        self._should_write_objects = False
        self.objects__enabled = True

    def _read(self):
        self.header = Xfs.XfsHeader(self._io, self, self._root)
        self.header._read()
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.data_buffer
        if hasattr(self, '_m_data_buffer'):
            pass

        _ = self.objects
        if hasattr(self, '_m_objects'):
            pass
            for i in range(len(self._m_objects)):
                pass
                self._m_objects[i]._fetch_instances()




    def _write__seq(self, io=None):
        super(Xfs, self)._write__seq(io)
        self._should_write_data_buffer = self.data_buffer__enabled
        self._should_write_objects = self.objects__enabled
        self.header._write__seq(self._io)


    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if self.data_buffer__enabled:
            pass

        if self.objects__enabled:
            pass
            if len(self._m_objects) != self.header.object_num:
                raise kaitaistruct.ConsistencyError(u"objects", self.header.object_num, len(self._m_objects))
            for i in range(len(self._m_objects)):
                pass
                if self._m_objects[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"objects", self._root, self._m_objects[i]._root)
                if self._m_objects[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"objects", self, self._m_objects[i]._parent)
                if self._m_objects[i].i != i:
                    raise kaitaistruct.ConsistencyError(u"objects", i, self._m_objects[i].i)


        self._dirty = False

    class MtProperty(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.MtProperty, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.name_ofs = self._io.read_u4le()
            self.type = self._io.read_u1()
            self.attr = self._io.read_u1()
            self.bytes = self._io.read_bits_int_le(15)
            self.disable = self._io.read_bits_int_le(1) != 0
            self.getter = self._io.read_u4le()
            self.getcount = self._io.read_u4le()
            self.setter = self._io.read_u4le()
            self.setcount = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Xfs.MtProperty, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.name_ofs)
            self._io.write_u1(self.type)
            self._io.write_u1(self.attr)
            self._io.write_bits_int_le(15, self.bytes)
            self._io.write_bits_int_le(1, int(self.disable))
            self._io.write_u4le(self.getter)
            self._io.write_u4le(self.getcount)
            self._io.write_u4le(self.setter)
            self._io.write_u4le(self.setcount)


        def _check(self):
            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"UTF-8"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"UTF-8"), 0))

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
            self._io.seek(self.name_ofs + 16)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.name_ofs + 16)
            self._io.write_bytes((self._m_name).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)

        @property
        def parent_index(self):
            if hasattr(self, '_m_parent_index'):
                return self._m_parent_index

            self._m_parent_index = self._parent._parent.i
            return getattr(self, '_m_parent_index', None)

        def _invalidate_parent_index(self):
            del self._m_parent_index

    class Obj(ReadWriteKaitaiStruct):
        def __init__(self, i, _io=None, _parent=None, _root=None):
            super(Xfs.Obj, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.i = i
            self._should_write_data = False
            self.data__enabled = True

        def _read(self):
            pass
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.data
            if hasattr(self, '_m_data'):
                pass
                self._m_data._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.Obj, self)._write__seq(io)
            self._should_write_data = self.data__enabled


        def _check(self):
            if self.data__enabled:
                pass
                if self._m_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data._root)
                if self._m_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self._m_data._parent)

            self._dirty = False

        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            if not self.data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._root.header.obj_pos[self.i] + 16)
            self._m_data = Xfs.ObjectData(self._io, self, self._root)
            self._m_data._read()
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._dirty = True
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek(self._root.header.obj_pos[self.i] + 16)
            self._m_data._write__seq(self._io)
            self._io.seek(_pos)


    class ObjectData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.ObjectData, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.dti = self._io.read_u4le()
            self.prop_num = self._io.read_bits_int_le(15)
            self.init = self._io.read_bits_int_le(1) != 0
            self.reserved = self._io.read_u2le()
            self.prop = []
            for i in range(self.prop_num):
                _t_prop = Xfs.MtProperty(self._io, self, self._root)
                try:
                    _t_prop._read()
                finally:
                    self.prop.append(_t_prop)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.prop)):
                pass
                self.prop[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.ObjectData, self)._write__seq(io)
            self._io.write_u4le(self.dti)
            self._io.write_bits_int_le(15, self.prop_num)
            self._io.write_bits_int_le(1, int(self.init))
            self._io.write_u2le(self.reserved)
            for i in range(len(self.prop)):
                pass
                self.prop[i]._write__seq(self._io)



        def _check(self):
            if len(self.prop) != self.prop_num:
                raise kaitaistruct.ConsistencyError(u"prop", self.prop_num, len(self.prop))
            for i in range(len(self.prop)):
                pass
                if self.prop[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"prop", self._root, self.prop[i]._root)
                if self.prop[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"prop", self, self.prop[i]._parent)

            self._dirty = False


    class XfsHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.XfsHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x58\x46\x53\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x58\x46\x53\x00", self.magic, self._io, u"/types/xfs_header/seq/0")
            self.major_ver = self._io.read_u2le()
            self.minor_ver = self._io.read_u2le()
            self.object_num = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            self.obj_pos = []
            for i in range(self.object_num):
                self.obj_pos.append(self._io.read_u4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.obj_pos)):
                pass



        def _write__seq(self, io=None):
            super(Xfs.XfsHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.major_ver)
            self._io.write_u2le(self.minor_ver)
            self._io.write_u4le(self.object_num)
            self._io.write_u4le(self.data_size)
            for i in range(len(self.obj_pos)):
                pass
                self._io.write_u4le(self.obj_pos[i])



        def _check(self):
            if len(self.magic) != 4:
                raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
            if not self.magic == b"\x58\x46\x53\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x58\x46\x53\x00", self.magic, None, u"/types/xfs_header/seq/0")
            if len(self.obj_pos) != self.object_num:
                raise kaitaistruct.ConsistencyError(u"obj_pos", self.object_num, len(self.obj_pos))
            for i in range(len(self.obj_pos)):
                pass

            self._dirty = False


    @property
    def data_buffer(self):
        if self._should_write_data_buffer:
            self._write_data_buffer()
        if hasattr(self, '_m_data_buffer'):
            return self._m_data_buffer

        if not self.data_buffer__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.data_size + 16)
        self._m_data_buffer = self._io.read_bytes_full()
        self._io.seek(_pos)
        return getattr(self, '_m_data_buffer', None)

    @data_buffer.setter
    def data_buffer(self, v):
        self._dirty = True
        self._m_data_buffer = v

    def _write_data_buffer(self):
        self._should_write_data_buffer = False
        _pos = self._io.pos()
        self._io.seek(self.header.data_size + 16)
        self._io.write_bytes(self._m_data_buffer)
        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"data_buffer", 0, self._io.size() - self._io.pos())
        self._io.seek(_pos)

    @property
    def objects(self):
        if self._should_write_objects:
            self._write_objects()
        if hasattr(self, '_m_objects'):
            return self._m_objects

        if not self.objects__enabled:
            return None

        self._m_objects = []
        for i in range(self.header.object_num):
            _t__m_objects = Xfs.Obj(i, self._io, self, self._root)
            try:
                _t__m_objects._read()
            finally:
                self._m_objects.append(_t__m_objects)

        return getattr(self, '_m_objects', None)

    @objects.setter
    def objects(self, v):
        self._dirty = True
        self._m_objects = v

    def _write_objects(self):
        self._should_write_objects = False
        for i in range(len(self._m_objects)):
            pass
            self._m_objects[i]._write__seq(self._io)



