# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class MtTypes(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(MtTypes, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        pass
        self._dirty = False


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(MtTypes, self)._write__seq(io)


    def _check(self):
        self._dirty = False

    class Color(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Color, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r = self._io.read_f4le()
            self.g = self._io.read_f4le()
            self.b = self._io.read_f4le()
            self.a = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Color, self)._write__seq(io)
            self._io.write_f4le(self.r)
            self._io.write_f4le(self.g)
            self._io.write_f4le(self.b)
            self._io.write_f4le(self.a)


        def _check(self):
            self._dirty = False


    class Mat3x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Mat3x3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = MtTypes.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = MtTypes.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = MtTypes.Vec3(self._io, self, self._root)
            self.r2._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()


        def _write__seq(self, io=None):
            super(MtTypes.Mat3x3, self)._write__seq(io)
            self.r0._write__seq(self._io)
            self.r1._write__seq(self._io)
            self.r2._write__seq(self._io)


        def _check(self):
            if self.r0._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r0", self._root, self.r0._root)
            if self.r0._parent != self:
                raise kaitaistruct.ConsistencyError(u"r0", self, self.r0._parent)
            if self.r1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r1", self._root, self.r1._root)
            if self.r1._parent != self:
                raise kaitaistruct.ConsistencyError(u"r1", self, self.r1._parent)
            if self.r2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r2", self._root, self.r2._root)
            if self.r2._parent != self:
                raise kaitaistruct.ConsistencyError(u"r2", self, self.r2._parent)
            self._dirty = False


    class Mat4x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Mat4x3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = MtTypes.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = MtTypes.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = MtTypes.Vec3(self._io, self, self._root)
            self.r2._read()
            self.r3 = MtTypes.Vec3(self._io, self, self._root)
            self.r3._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(MtTypes.Mat4x3, self)._write__seq(io)
            self.r0._write__seq(self._io)
            self.r1._write__seq(self._io)
            self.r2._write__seq(self._io)
            self.r3._write__seq(self._io)


        def _check(self):
            if self.r0._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r0", self._root, self.r0._root)
            if self.r0._parent != self:
                raise kaitaistruct.ConsistencyError(u"r0", self, self.r0._parent)
            if self.r1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r1", self._root, self.r1._root)
            if self.r1._parent != self:
                raise kaitaistruct.ConsistencyError(u"r1", self, self.r1._parent)
            if self.r2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r2", self._root, self.r2._root)
            if self.r2._parent != self:
                raise kaitaistruct.ConsistencyError(u"r2", self, self.r2._parent)
            if self.r3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r3", self._root, self.r3._root)
            if self.r3._parent != self:
                raise kaitaistruct.ConsistencyError(u"r3", self, self.r3._parent)
            self._dirty = False


    class Mat4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Mat4x4, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = MtTypes.Vec4(self._io, self, self._root)
            self.r0._read()
            self.r1 = MtTypes.Vec4(self._io, self, self._root)
            self.r1._read()
            self.r2 = MtTypes.Vec4(self._io, self, self._root)
            self.r2._read()
            self.r3 = MtTypes.Vec4(self._io, self, self._root)
            self.r3._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(MtTypes.Mat4x4, self)._write__seq(io)
            self.r0._write__seq(self._io)
            self.r1._write__seq(self._io)
            self.r2._write__seq(self._io)
            self.r3._write__seq(self._io)


        def _check(self):
            if self.r0._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r0", self._root, self.r0._root)
            if self.r0._parent != self:
                raise kaitaistruct.ConsistencyError(u"r0", self, self.r0._parent)
            if self.r1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r1", self._root, self.r1._root)
            if self.r1._parent != self:
                raise kaitaistruct.ConsistencyError(u"r1", self, self.r1._parent)
            if self.r2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r2", self._root, self.r2._root)
            if self.r2._parent != self:
                raise kaitaistruct.ConsistencyError(u"r2", self, self.r2._parent)
            if self.r3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r3", self._root, self.r3._root)
            if self.r3._parent != self:
                raise kaitaistruct.ConsistencyError(u"r3", self, self.r3._parent)
            self._dirty = False


    class MtStr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.MtStr, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_string = False
            self.string__enabled = True

        def _read(self):
            self.ptr = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.string
            if hasattr(self, '_m_string'):
                pass



        def _write__seq(self, io=None):
            super(MtTypes.MtStr, self)._write__seq(io)
            self._should_write_string = self.string__enabled
            self._io.write_u4le(self.ptr)


        def _check(self):
            if self.string__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_string).encode(u"UTF-8"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"string", -1, KaitaiStream.byte_array_index_of((self._m_string).encode(u"UTF-8"), 0))

            self._dirty = False

        @property
        def string(self):
            if self._should_write_string:
                self._write_string()
            if hasattr(self, '_m_string'):
                return self._m_string

            if not self.string__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ptr)
            self._m_string = (self._io.read_bytes_term(0, False, True, True)).decode(u"UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_string', None)

        @string.setter
        def string(self, v):
            self._dirty = True
            self._m_string = v

        def _write_string(self):
            self._should_write_string = False
            _pos = self._io.pos()
            self._io.seek(self.ptr)
            self._io.write_bytes((self._m_string).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class Point(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Point, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Point, self)._write__seq(io)
            self._io.write_s4le(self.x)
            self._io.write_s4le(self.y)


        def _check(self):
            self._dirty = False


    class Rect(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Rect, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.l = self._io.read_s4le()
            self.t = self._io.read_s4le()
            self.r = self._io.read_s4le()
            self.b = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Rect, self)._write__seq(io)
            self._io.write_s4le(self.l)
            self._io.write_s4le(self.t)
            self._io.write_s4le(self.r)
            self._io.write_s4le(self.b)


        def _check(self):
            self._dirty = False


    class Size(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Size, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.w = self._io.read_s4le()
            self.h = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Size, self)._write__seq(io)
            self._io.write_s4le(self.w)
            self._io.write_s4le(self.h)


        def _check(self):
            self._dirty = False


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.padding = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.padding)


        def _check(self):
            self._dirty = False


    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(MtTypes.Vec4, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False



