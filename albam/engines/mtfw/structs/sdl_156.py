# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sdl156(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Sdl156, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Sdl156.BaseHeader(self._io, self, self._root)
        self.header._read()
        self.tracks = []
        for i in range(self.header.num_tracks):
            _t_tracks = Sdl156.Track(self._io, self, self._root)
            try:
                _t_tracks._read()
            finally:
                self.tracks.append(_t_tracks)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.tracks)):
            pass
            self.tracks[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Sdl156, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.tracks)):
            pass
            self.tracks[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.tracks) != self.header.num_tracks:
            raise kaitaistruct.ConsistencyError(u"tracks", self.header.num_tracks, len(self.tracks))
        for i in range(len(self.tracks)):
            pass
            if self.tracks[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tracks", self._root, self.tracks[i]._root)
            if self.tracks[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"tracks", self, self.tracks[i]._parent)

        self._dirty = False

    class BaseHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.BaseHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x53\x44\x4C\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x44\x4C\x00", self.magic, self._io, u"/types/base_header/seq/0")
            self.version = self._io.read_u2le()
            self.num_tracks = self._io.read_u2le()
            self.frames = self._io.read_u4le()
            self.ofs_dti_table = self._io.read_u4le()
            self.ofs_names = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.BaseHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.version)
            self._io.write_u2le(self.num_tracks)
            self._io.write_u4le(self.frames)
            self._io.write_u4le(self.ofs_dti_table)
            self._io.write_u4le(self.ofs_names)


        def _check(self):
            if len(self.magic) != 4:
                raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
            if not self.magic == b"\x53\x44\x4C\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x44\x4C\x00", self.magic, None, u"/types/base_header/seq/0")
            self._dirty = False


    class Bool(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Bool, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.Bool, self)._write__seq(io)
            self._io.write_u1(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Color(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Color, self).__init__(_io)
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
            super(Sdl156.Color, self)._write__seq(io)
            self._io.write_f4le(self.r)
            self._io.write_f4le(self.g)
            self._io.write_f4le(self.b)
            self._io.write_f4le(self.a)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class F32(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.F32, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.F32, self)._write__seq(io)
            self._io.write_f4le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class F64(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.F64, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_f8le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.F64, self)._write__seq(io)
            self._io.write_f8le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 8
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Float2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Float2, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.Float2, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)


        def _check(self):
            self._dirty = False


    class Float3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Float3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.Float3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    class Float4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Float4, self).__init__(_io)
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
            super(Sdl156.Float4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    class Mat3x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Mat3x3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Sdl156.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = Sdl156.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = Sdl156.Vec3(self._io, self, self._root)
            self.r2._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()


        def _write__seq(self, io=None):
            super(Sdl156.Mat3x3, self)._write__seq(io)
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
            super(Sdl156.Mat4x3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Sdl156.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = Sdl156.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = Sdl156.Vec3(self._io, self, self._root)
            self.r2._read()
            self.r3 = Sdl156.Vec3(self._io, self, self._root)
            self.r3._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(Sdl156.Mat4x3, self)._write__seq(io)
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
            super(Sdl156.Mat4x4, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Sdl156.Vec4(self._io, self, self._root)
            self.r0._read()
            self.r1 = Sdl156.Vec4(self._io, self, self._root)
            self.r1._read()
            self.r2 = Sdl156.Vec4(self._io, self, self._root)
            self.r2._read()
            self.r3 = Sdl156.Vec4(self._io, self, self._root)
            self.r3._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(Sdl156.Mat4x4, self)._write__seq(io)
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


    class MtEasecurve(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.MtEasecurve, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.p1 = self._io.read_f4le()
            self.p2 = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.MtEasecurve, self)._write__seq(io)
            self._io.write_f4le(self.p1)
            self._io.write_f4le(self.p2)


        def _check(self):
            self._dirty = False


    class MtStr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.MtStr, self).__init__(_io)
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
            super(Sdl156.MtStr, self)._write__seq(io)
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
            super(Sdl156.Point, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.Point, self)._write__seq(io)
            self._io.write_s4le(self.x)
            self._io.write_s4le(self.y)


        def _check(self):
            self._dirty = False


    class Quaternion(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Quaternion, self).__init__(_io)
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
            super(Sdl156.Quaternion, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Rect(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Rect, self).__init__(_io)
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
            super(Sdl156.Rect, self)._write__seq(io)
            self._io.write_s4le(self.l)
            self._io.write_s4le(self.t)
            self._io.write_s4le(self.r)
            self._io.write_s4le(self.b)


        def _check(self):
            self._dirty = False


    class Resource(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Resource, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_ref_dti = False
            self.ref_dti__enabled = True
            self._should_write_ref_path = False
            self.ref_path__enabled = True

        def _read(self):
            self.ref_ofs = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.ref_dti
            if hasattr(self, '_m_ref_dti'):
                pass

            _ = self.ref_path
            if hasattr(self, '_m_ref_path'):
                pass



        def _write__seq(self, io=None):
            super(Sdl156.Resource, self)._write__seq(io)
            self._should_write_ref_dti = self.ref_dti__enabled
            self._should_write_ref_path = self.ref_path__enabled
            self._io.write_u4le(self.ref_ofs)


        def _check(self):
            if self.ref_dti__enabled:
                pass
                if self.ref_ofs != 0:
                    pass


            if self.ref_path__enabled:
                pass
                if self.ref_ofs != 0:
                    pass
                    if KaitaiStream.byte_array_index_of((self._m_ref_path).encode(u"UTF-8"), 0) != -1:
                        raise kaitaistruct.ConsistencyError(u"ref_path", -1, KaitaiStream.byte_array_index_of((self._m_ref_path).encode(u"UTF-8"), 0))


            self._dirty = False

        @property
        def ref_dti(self):
            if self._should_write_ref_dti:
                self._write_ref_dti()
            if hasattr(self, '_m_ref_dti'):
                return self._m_ref_dti

            if not self.ref_dti__enabled:
                return None

            if self.ref_ofs != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ref_ofs + self._root.header.ofs_names)
                self._m_ref_dti = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_ref_dti', None)

        @ref_dti.setter
        def ref_dti(self, v):
            self._dirty = True
            self._m_ref_dti = v

        def _write_ref_dti(self):
            self._should_write_ref_dti = False
            if self.ref_ofs != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ref_ofs + self._root.header.ofs_names)
                self._io.write_u4le(self._m_ref_dti)
                self._io.seek(_pos)


        @property
        def ref_path(self):
            if self._should_write_ref_path:
                self._write_ref_path()
            if hasattr(self, '_m_ref_path'):
                return self._m_ref_path

            if not self.ref_path__enabled:
                return None

            if self.ref_ofs != 0:
                pass
                _pos = self._io.pos()
                self._io.seek((self.ref_ofs + self._root.header.ofs_names) + 4)
                self._m_ref_path = (self._io.read_bytes_term(0, False, True, True)).decode(u"UTF-8")
                self._io.seek(_pos)

            return getattr(self, '_m_ref_path', None)

        @ref_path.setter
        def ref_path(self, v):
            self._dirty = True
            self._m_ref_path = v

        def _write_ref_path(self):
            self._should_write_ref_path = False
            if self.ref_ofs != 0:
                pass
                _pos = self._io.pos()
                self._io.seek((self.ref_ofs + self._root.header.ofs_names) + 4)
                self._io.write_bytes((self._m_ref_path).encode(u"UTF-8"))
                self._io.write_u1(0)
                self._io.seek(_pos)



    class S16(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.S16, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_s2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.S16, self)._write__seq(io)
            self._io.write_s2le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class S32(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.S32, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.S32, self)._write__seq(io)
            self._io.write_s4le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class S64(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.S64, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_s8le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.S64, self)._write__seq(io)
            self._io.write_s8le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 8
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class S8(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.S8, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_s1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.S8, self)._write__seq(io)
            self._io.write_s1(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Size(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Size, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.w = self._io.read_s4le()
            self.h = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.Size, self)._write__seq(io)
            self._io.write_s4le(self.w)
            self._io.write_s4le(self.h)


        def _check(self):
            self._dirty = False


    class TimingFrame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.TimingFrame, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.frame = self._io.read_bits_int_le(24)
            self.type = self._io.read_bits_int_le(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.TimingFrame, self)._write__seq(io)
            self._io.write_bits_int_le(24, self.frame)
            self._io.write_bits_int_le(8, self.type)


        def _check(self):
            self._dirty = False


    class Track(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Track, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_data = False
            self.data__enabled = True
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_timing_frames = False
            self.timing_frames__enabled = True

        def _read(self):
            self.track_type = self._io.read_u1()
            self.prop_type = self._io.read_u1()
            self.num_frames = self._io.read_u2le()
            self.parent = self._io.read_u4le()
            self.ofs_name = self._io.read_u4le()
            self.dti_ref = self._io.read_u4le()
            self.ofs_timing = self._io.read_u4le()
            self.ofs_data = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.data
            if hasattr(self, '_m_data'):
                pass
                for i in range(len(self._m_data)):
                    pass
                    _on = self.prop_type
                    if _on == 10:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 11:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 12:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 13:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 14:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 15:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 20:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 21:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 22:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 24:
                        pass
                    elif _on == 28:
                        pass
                    elif _on == 3:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 34:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 35:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 36:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 4:
                        pass
                    elif _on == 40:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 5:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 55:
                        pass
                    elif _on == 57:
                        pass
                    elif _on == 58:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 6:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 7:
                        pass
                        self._m_data[i]._fetch_instances()
                    elif _on == 8:
                        pass
                    elif _on == 9:
                        pass
                        self._m_data[i]._fetch_instances()


            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.timing_frames
            if hasattr(self, '_m_timing_frames'):
                pass
                for i in range(len(self._m_timing_frames)):
                    pass
                    self._m_timing_frames[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Sdl156.Track, self)._write__seq(io)
            self._should_write_data = self.data__enabled
            self._should_write_name = self.name__enabled
            self._should_write_timing_frames = self.timing_frames__enabled
            self._io.write_u1(self.track_type)
            self._io.write_u1(self.prop_type)
            self._io.write_u2le(self.num_frames)
            self._io.write_u4le(self.parent)
            self._io.write_u4le(self.ofs_name)
            self._io.write_u4le(self.dti_ref)
            self._io.write_u4le(self.ofs_timing)
            self._io.write_u4le(self.ofs_data)


        def _check(self):
            if self.data__enabled:
                pass
                if  ((self.ofs_data > 0) and (self.track_type > 5)) :
                    pass
                    if len(self._m_data) != self.num_frames:
                        raise kaitaistruct.ConsistencyError(u"data", self.num_frames, len(self._m_data))
                    for i in range(len(self._m_data)):
                        pass
                        _on = self.prop_type
                        if _on == 10:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 11:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 12:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 13:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 14:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 15:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 20:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 21:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 22:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 24:
                            pass
                        elif _on == 28:
                            pass
                        elif _on == 3:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 34:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 35:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 36:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 4:
                            pass
                        elif _on == 40:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 5:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 55:
                            pass
                        elif _on == 57:
                            pass
                        elif _on == 58:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 6:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 7:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)
                        elif _on == 8:
                            pass
                        elif _on == 9:
                            pass
                            if self._m_data[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"data", self._root, self._m_data[i]._root)
                            if self._m_data[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"data", self, self._m_data[i]._parent)



            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"UTF-8"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"UTF-8"), 0))

            if self.timing_frames__enabled:
                pass
                if len(self._m_timing_frames) != self.num_frames:
                    raise kaitaistruct.ConsistencyError(u"timing_frames", self.num_frames, len(self._m_timing_frames))
                for i in range(len(self._m_timing_frames)):
                    pass
                    if self._m_timing_frames[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"timing_frames", self._root, self._m_timing_frames[i]._root)
                    if self._m_timing_frames[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"timing_frames", self, self._m_timing_frames[i]._parent)


            self._dirty = False

        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            if not self.data__enabled:
                return None

            if  ((self.ofs_data > 0) and (self.track_type > 5)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_data)
                self._m_data = []
                for i in range(self.num_frames):
                    _on = self.prop_type
                    if _on == 10:
                        pass
                        _t__m_data = Sdl156.S32(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 11:
                        pass
                        _t__m_data = Sdl156.S64(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 12:
                        pass
                        _t__m_data = Sdl156.F32(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 13:
                        pass
                        _t__m_data = Sdl156.F64(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 14:
                        pass
                        _t__m_data = Sdl156.MtStr(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 15:
                        pass
                        _t__m_data = Sdl156.Color(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 20:
                        pass
                        _t__m_data = Sdl156.Vec3(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 21:
                        pass
                        _t__m_data = Sdl156.Vec4(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 22:
                        pass
                        _t__m_data = Sdl156.Quaternion(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 24:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 28:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 3:
                        pass
                        _t__m_data = Sdl156.Bool(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 34:
                        pass
                        _t__m_data = Sdl156.Float2(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 35:
                        pass
                        _t__m_data = Sdl156.Float3(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 36:
                        pass
                        _t__m_data = Sdl156.Float4(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 4:
                        pass
                        self._m_data.append(self._io.read_u8le())
                    elif _on == 40:
                        pass
                        _t__m_data = Sdl156.MtEasecurve(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 5:
                        pass
                        _t__m_data = Sdl156.U16(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 55:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 57:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 58:
                        pass
                        _t__m_data = Sdl156.Resource(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 6:
                        pass
                        _t__m_data = Sdl156.U32(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 7:
                        pass
                        _t__m_data = Sdl156.U64(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)
                    elif _on == 8:
                        pass
                        self._m_data.append(self._io.read_s8le())
                    elif _on == 9:
                        pass
                        _t__m_data = Sdl156.S16(self._io, self, self._root)
                        try:
                            _t__m_data._read()
                        finally:
                            self._m_data.append(_t__m_data)

                self._io.seek(_pos)

            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._dirty = True
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            if  ((self.ofs_data > 0) and (self.track_type > 5)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_data)
                for i in range(len(self._m_data)):
                    pass
                    _on = self.prop_type
                    if _on == 10:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 11:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 12:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 13:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 14:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 15:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 20:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 21:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 22:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 24:
                        pass
                        self._io.write_u4le(self._m_data[i])
                    elif _on == 28:
                        pass
                        self._io.write_u4le(self._m_data[i])
                    elif _on == 3:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 34:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 35:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 36:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 4:
                        pass
                        self._io.write_u8le(self._m_data[i])
                    elif _on == 40:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 5:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 55:
                        pass
                        self._io.write_u4le(self._m_data[i])
                    elif _on == 57:
                        pass
                        self._io.write_u4le(self._m_data[i])
                    elif _on == 58:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 6:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 7:
                        pass
                        self._m_data[i]._write__seq(self._io)
                    elif _on == 8:
                        pass
                        self._io.write_s8le(self._m_data[i])
                    elif _on == 9:
                        pass
                        self._m_data[i]._write__seq(self._io)

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
            self._io.seek(self.ofs_name + self._root.header.ofs_names)
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
            self._io.seek(self.ofs_name + self._root.header.ofs_names)
            self._io.write_bytes((self._m_name).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_
        @property
        def timing_frames(self):
            if self._should_write_timing_frames:
                self._write_timing_frames()
            if hasattr(self, '_m_timing_frames'):
                return self._m_timing_frames

            if not self.timing_frames__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_timing)
            self._m_timing_frames = []
            for i in range(self.num_frames):
                _t__m_timing_frames = Sdl156.TimingFrame(self._io, self, self._root)
                try:
                    _t__m_timing_frames._read()
                finally:
                    self._m_timing_frames.append(_t__m_timing_frames)

            self._io.seek(_pos)
            return getattr(self, '_m_timing_frames', None)

        @timing_frames.setter
        def timing_frames(self, v):
            self._dirty = True
            self._m_timing_frames = v

        def _write_timing_frames(self):
            self._should_write_timing_frames = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_timing)
            for i in range(len(self._m_timing_frames)):
                pass
                self._m_timing_frames[i]._write__seq(self._io)

            self._io.seek(_pos)


    class U16(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.U16, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.U16, self)._write__seq(io)
            self._io.write_u2le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class U32(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.U32, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.U32, self)._write__seq(io)
            self._io.write_u4le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class U64(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.U64, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.U64, self)._write__seq(io)
            self._io.write_u8le(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 8
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class U8(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.U8, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.U8, self)._write__seq(io)
            self._io.write_u1(self.val)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl156.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sdl156.Vec4, self).__init__(_io)
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
            super(Sdl156.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_


