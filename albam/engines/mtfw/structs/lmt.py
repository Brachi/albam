# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lmt(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x4C\x4D\x54\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x4C\x4D\x54\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.num_block_offsets = self._io.read_u2le()
        self.block_offsets = []
        for i in range(self.num_block_offsets):
            _t_block_offsets = Lmt.BlockOffset(self._io, self, self._root)
            _t_block_offsets._read()
            self.block_offsets.append(_t_block_offsets)



    def _fetch_instances(self):
        pass
        for i in range(len(self.block_offsets)):
            pass
            self.block_offsets[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Lmt, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u2le(self.version)
        self._io.write_u2le(self.num_block_offsets)
        for i in range(len(self.block_offsets)):
            pass
            self.block_offsets[i]._write__seq(self._io)



    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x4C\x4D\x54\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x4C\x4D\x54\x00", self.id_magic, None, u"/seq/0")
        if (len(self.block_offsets) != self.num_block_offsets):
            raise kaitaistruct.ConsistencyError(u"block_offsets", len(self.block_offsets), self.num_block_offsets)
        for i in range(len(self.block_offsets)):
            pass
            if self.block_offsets[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"block_offsets", self.block_offsets[i]._root, self._root)
            if self.block_offsets[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"block_offsets", self.block_offsets[i]._parent, self)


    class Attributes67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_attr_00 = False
            self.attr_00__to_write = True
            self._should_write_attr_01 = False
            self.attr_01__to_write = True
            self._should_write_attr_02 = False
            self.attr_02__to_write = True
            self._should_write_attr_03 = False
            self.attr_03__to_write = True

        def _read(self):
            self.event_id_00 = []
            for i in range(32):
                self.event_id_00.append(self._io.read_u2le())

            self.unk_num_00 = self._io.read_u4le()
            self.unk_ofs_00 = self._io.read_u4le()
            self.event_id_01 = []
            for i in range(32):
                self.event_id_01.append(self._io.read_u2le())

            self.unk_num_01 = self._io.read_u4le()
            self.unk_ofs_01 = self._io.read_u4le()
            self.event_id_02 = []
            for i in range(32):
                self.event_id_02.append(self._io.read_u2le())

            self.unk_num_02 = self._io.read_u4le()
            self.unk_ofs_02 = self._io.read_u4le()
            self.event_id_03 = []
            for i in range(32):
                self.event_id_03.append(self._io.read_u2le())

            self.unk_num_03 = self._io.read_u4le()
            self.unk_ofs_03 = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.event_id_00)):
                pass

            for i in range(len(self.event_id_01)):
                pass

            for i in range(len(self.event_id_02)):
                pass

            for i in range(len(self.event_id_03)):
                pass

            _ = self.attr_00
            for i in range(len(self._m_attr_00)):
                pass
                self.attr_00[i]._fetch_instances()

            _ = self.attr_01
            for i in range(len(self._m_attr_01)):
                pass
                self.attr_01[i]._fetch_instances()

            _ = self.attr_02
            for i in range(len(self._m_attr_02)):
                pass
                self.attr_02[i]._fetch_instances()

            _ = self.attr_03
            for i in range(len(self._m_attr_03)):
                pass
                self.attr_03[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.Attributes67, self)._write__seq(io)
            self._should_write_attr_00 = self.attr_00__to_write
            self._should_write_attr_01 = self.attr_01__to_write
            self._should_write_attr_02 = self.attr_02__to_write
            self._should_write_attr_03 = self.attr_03__to_write
            for i in range(len(self.event_id_00)):
                pass
                self._io.write_u2le(self.event_id_00[i])

            self._io.write_u4le(self.unk_num_00)
            self._io.write_u4le(self.unk_ofs_00)
            for i in range(len(self.event_id_01)):
                pass
                self._io.write_u2le(self.event_id_01[i])

            self._io.write_u4le(self.unk_num_01)
            self._io.write_u4le(self.unk_ofs_01)
            for i in range(len(self.event_id_02)):
                pass
                self._io.write_u2le(self.event_id_02[i])

            self._io.write_u4le(self.unk_num_02)
            self._io.write_u4le(self.unk_ofs_02)
            for i in range(len(self.event_id_03)):
                pass
                self._io.write_u2le(self.event_id_03[i])

            self._io.write_u4le(self.unk_num_03)
            self._io.write_u4le(self.unk_ofs_03)


        def _check(self):
            pass
            if (len(self.event_id_00) != 32):
                raise kaitaistruct.ConsistencyError(u"event_id_00", len(self.event_id_00), 32)
            for i in range(len(self.event_id_00)):
                pass

            if (len(self.event_id_01) != 32):
                raise kaitaistruct.ConsistencyError(u"event_id_01", len(self.event_id_01), 32)
            for i in range(len(self.event_id_01)):
                pass

            if (len(self.event_id_02) != 32):
                raise kaitaistruct.ConsistencyError(u"event_id_02", len(self.event_id_02), 32)
            for i in range(len(self.event_id_02)):
                pass

            if (len(self.event_id_03) != 32):
                raise kaitaistruct.ConsistencyError(u"event_id_03", len(self.event_id_03), 32)
            for i in range(len(self.event_id_03)):
                pass


        @property
        def attr_00(self):
            if self._should_write_attr_00:
                self._write_attr_00()
            if hasattr(self, '_m_attr_00'):
                return self._m_attr_00

            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_00)
            self._m_attr_00 = []
            for i in range(self.unk_num_00):
                _t__m_attr_00 = Lmt.Attr(self._io, self, self._root)
                _t__m_attr_00._read()
                self._m_attr_00.append(_t__m_attr_00)

            self._io.seek(_pos)
            return getattr(self, '_m_attr_00', None)

        @attr_00.setter
        def attr_00(self, v):
            self._m_attr_00 = v

        def _write_attr_00(self):
            self._should_write_attr_00 = False
            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_00)
            for i in range(len(self._m_attr_00)):
                pass
                self.attr_00[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attr_00(self):
            pass
            if (len(self.attr_00) != self.unk_num_00):
                raise kaitaistruct.ConsistencyError(u"attr_00", len(self.attr_00), self.unk_num_00)
            for i in range(len(self._m_attr_00)):
                pass
                if self.attr_00[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attr_00", self.attr_00[i]._root, self._root)
                if self.attr_00[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attr_00", self.attr_00[i]._parent, self)


        @property
        def attr_01(self):
            if self._should_write_attr_01:
                self._write_attr_01()
            if hasattr(self, '_m_attr_01'):
                return self._m_attr_01

            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_01)
            self._m_attr_01 = []
            for i in range(self.unk_num_01):
                _t__m_attr_01 = Lmt.Attr(self._io, self, self._root)
                _t__m_attr_01._read()
                self._m_attr_01.append(_t__m_attr_01)

            self._io.seek(_pos)
            return getattr(self, '_m_attr_01', None)

        @attr_01.setter
        def attr_01(self, v):
            self._m_attr_01 = v

        def _write_attr_01(self):
            self._should_write_attr_01 = False
            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_01)
            for i in range(len(self._m_attr_01)):
                pass
                self.attr_01[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attr_01(self):
            pass
            if (len(self.attr_01) != self.unk_num_01):
                raise kaitaistruct.ConsistencyError(u"attr_01", len(self.attr_01), self.unk_num_01)
            for i in range(len(self._m_attr_01)):
                pass
                if self.attr_01[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attr_01", self.attr_01[i]._root, self._root)
                if self.attr_01[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attr_01", self.attr_01[i]._parent, self)


        @property
        def attr_02(self):
            if self._should_write_attr_02:
                self._write_attr_02()
            if hasattr(self, '_m_attr_02'):
                return self._m_attr_02

            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_02)
            self._m_attr_02 = []
            for i in range(self.unk_num_02):
                _t__m_attr_02 = Lmt.Attr(self._io, self, self._root)
                _t__m_attr_02._read()
                self._m_attr_02.append(_t__m_attr_02)

            self._io.seek(_pos)
            return getattr(self, '_m_attr_02', None)

        @attr_02.setter
        def attr_02(self, v):
            self._m_attr_02 = v

        def _write_attr_02(self):
            self._should_write_attr_02 = False
            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_02)
            for i in range(len(self._m_attr_02)):
                pass
                self.attr_02[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attr_02(self):
            pass
            if (len(self.attr_02) != self.unk_num_02):
                raise kaitaistruct.ConsistencyError(u"attr_02", len(self.attr_02), self.unk_num_02)
            for i in range(len(self._m_attr_02)):
                pass
                if self.attr_02[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attr_02", self.attr_02[i]._root, self._root)
                if self.attr_02[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attr_02", self.attr_02[i]._parent, self)


        @property
        def attr_03(self):
            if self._should_write_attr_03:
                self._write_attr_03()
            if hasattr(self, '_m_attr_03'):
                return self._m_attr_03

            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_03)
            self._m_attr_03 = []
            for i in range(self.unk_num_03):
                _t__m_attr_03 = Lmt.Attr(self._io, self, self._root)
                _t__m_attr_03._read()
                self._m_attr_03.append(_t__m_attr_03)

            self._io.seek(_pos)
            return getattr(self, '_m_attr_03', None)

        @attr_03.setter
        def attr_03(self, v):
            self._m_attr_03 = v

        def _write_attr_03(self):
            self._should_write_attr_03 = False
            _pos = self._io.pos()
            self._io.seek(self.unk_ofs_03)
            for i in range(len(self._m_attr_03)):
                pass
                self.attr_03[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attr_03(self):
            pass
            if (len(self.attr_03) != self.unk_num_03):
                raise kaitaistruct.ConsistencyError(u"attr_03", len(self.attr_03), self.unk_num_03)
            for i in range(len(self._m_attr_03)):
                pass
                if self.attr_03[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attr_03", self.attr_03[i]._root, self._root)
                if self.attr_03[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attr_03", self.attr_03[i]._parent, self)



    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class MotionSe(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_attributes = False
            self.attributes__to_write = True

        def _read(self):
            self.event_id = []
            for i in range(32):
                self.event_id.append(self._io.read_u2le())

            self.num_events = self._io.read_u4le()
            self.ofs_events = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.event_id)):
                pass

            _ = self.attributes
            for i in range(len(self._m_attributes)):
                pass
                self.attributes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.MotionSe, self)._write__seq(io)
            self._should_write_attributes = self.attributes__to_write
            for i in range(len(self.event_id)):
                pass
                self._io.write_u2le(self.event_id[i])

            self._io.write_u4le(self.num_events)
            self._io.write_u4le(self.ofs_events)


        def _check(self):
            pass
            if (len(self.event_id) != 32):
                raise kaitaistruct.ConsistencyError(u"event_id", len(self.event_id), 32)
            for i in range(len(self.event_id)):
                pass


        @property
        def attributes(self):
            if self._should_write_attributes:
                self._write_attributes()
            if hasattr(self, '_m_attributes'):
                return self._m_attributes

            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            self._m_attributes = []
            for i in range(self.num_events):
                _t__m_attributes = Lmt.Attr(self._io, self, self._root)
                _t__m_attributes._read()
                self._m_attributes.append(_t__m_attributes)

            self._io.seek(_pos)
            return getattr(self, '_m_attributes', None)

        @attributes.setter
        def attributes(self, v):
            self._m_attributes = v

        def _write_attributes(self):
            self._should_write_attributes = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            for i in range(len(self._m_attributes)):
                pass
                self.attributes[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attributes(self):
            pass
            if (len(self.attributes) != self.num_events):
                raise kaitaistruct.ConsistencyError(u"attributes", len(self.attributes), self.num_events)
            for i in range(len(self._m_attributes)):
                pass
                if self.attributes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.attributes[i]._root, self._root)
                if self.attributes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.attributes[i]._parent, self)



    class OfsFrameBounds(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_body = False
            self.body__to_write = True

        def _read(self):
            self.ofs_buffer = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            if (self.is_exist != 0):
                pass
                _ = self.body
                self.body._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.OfsFrameBounds, self)._write__seq(io)
            self._should_write_body = self.body__to_write
            self._io.write_u4le(self.ofs_buffer)


        def _check(self):
            pass

        @property
        def is_exist(self):
            if hasattr(self, '_m_is_exist'):
                return self._m_is_exist

            self._m_is_exist = self.ofs_buffer
            return getattr(self, '_m_is_exist', None)

        def _invalidate_is_exist(self):
            del self._m_is_exist
        @property
        def body(self):
            if self._should_write_body:
                self._write_body()
            if hasattr(self, '_m_body'):
                return self._m_body

            if (self.is_exist != 0):
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_buffer)
                self._m_body = Lmt.FloatBuffer(self._io, self, self._root)
                self._m_body._read()
                self._io.seek(_pos)

            return getattr(self, '_m_body', None)

        @body.setter
        def body(self, v):
            self._m_body = v

        def _write_body(self):
            self._should_write_body = False
            if (self.is_exist != 0):
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_buffer)
                self.body._write__seq(self._io)
                self._io.seek(_pos)



        def _check_body(self):
            pass
            if (self.is_exist != 0):
                pass
                if self.body._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"body", self.body._root, self._root)
                if self.body._parent != self:
                    raise kaitaistruct.ConsistencyError(u"body", self.body._parent, self)



    class BlockOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_block_header = False
            self.block_header__to_write = True

        def _read(self):
            self.offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            if self.is_used:
                pass
                _ = self.block_header
                _on = self.lmt_ver
                if _on == 51:
                    pass
                    self.block_header._fetch_instances()
                elif _on == 67:
                    pass
                    self.block_header._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.BlockOffset, self)._write__seq(io)
            self._should_write_block_header = self.block_header__to_write
            self._io.write_u4le(self.offset)


        def _check(self):
            pass

        @property
        def is_used(self):
            if hasattr(self, '_m_is_used'):
                return self._m_is_used

            self._m_is_used = (self.offset != 0)
            return getattr(self, '_m_is_used', None)

        def _invalidate_is_used(self):
            del self._m_is_used
        @property
        def lmt_ver(self):
            if hasattr(self, '_m_lmt_ver'):
                return self._m_lmt_ver

            self._m_lmt_ver = self._parent.version
            return getattr(self, '_m_lmt_ver', None)

        def _invalidate_lmt_ver(self):
            del self._m_lmt_ver
        @property
        def block_header(self):
            if self._should_write_block_header:
                self._write_block_header()
            if hasattr(self, '_m_block_header'):
                return self._m_block_header

            if self.is_used:
                pass
                _pos = self._io.pos()
                self._io.seek(self.offset)
                _on = self.lmt_ver
                if _on == 51:
                    pass
                    self._m_block_header = Lmt.BlockHeader51(self._io, self, self._root)
                    self._m_block_header._read()
                elif _on == 67:
                    pass
                    self._m_block_header = Lmt.BlockHeader67(self._io, self, self._root)
                    self._m_block_header._read()
                self._io.seek(_pos)

            return getattr(self, '_m_block_header', None)

        @block_header.setter
        def block_header(self, v):
            self._m_block_header = v

        def _write_block_header(self):
            self._should_write_block_header = False
            if self.is_used:
                pass
                _pos = self._io.pos()
                self._io.seek(self.offset)
                _on = self.lmt_ver
                if _on == 51:
                    pass
                    self.block_header._write__seq(self._io)
                elif _on == 67:
                    pass
                    self.block_header._write__seq(self._io)
                self._io.seek(_pos)



        def _check_block_header(self):
            pass
            if self.is_used:
                pass
                _on = self.lmt_ver
                if _on == 51:
                    pass
                    if self.block_header._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"block_header", self.block_header._root, self._root)
                    if self.block_header._parent != self:
                        raise kaitaistruct.ConsistencyError(u"block_header", self.block_header._parent, self)
                elif _on == 67:
                    pass
                    if self.block_header._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"block_header", self.block_header._root, self._root)
                    if self.block_header._parent != self:
                        raise kaitaistruct.ConsistencyError(u"block_header", self.block_header._parent, self)



    class BlockHeader51(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_tracks = False
            self.tracks__to_write = True

        def _read(self):
            self.ofs_frame = self._io.read_u4le()
            self.num_tracks = self._io.read_u4le()
            self.num_frames = self._io.read_u4le()
            self.loop_frame = self._io.read_u4le()
            self.init_position = []
            for i in range(3):
                self.init_position.append(self._io.read_f4le())

            self.filler = self._io.read_u4le()
            self.init_quaterion = []
            for i in range(4):
                self.init_quaterion.append(self._io.read_f4le())

            self.collision_events = Lmt.EventCollision(self._io, self, self._root)
            self.collision_events._read()
            self.motion_sound_effects = Lmt.MotionSe(self._io, self, self._root)
            self.motion_sound_effects._read()


        def _fetch_instances(self):
            pass
            for i in range(len(self.init_position)):
                pass

            for i in range(len(self.init_quaterion)):
                pass

            self.collision_events._fetch_instances()
            self.motion_sound_effects._fetch_instances()
            _ = self.tracks
            for i in range(len(self._m_tracks)):
                pass
                self.tracks[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.BlockHeader51, self)._write__seq(io)
            self._should_write_tracks = self.tracks__to_write
            self._io.write_u4le(self.ofs_frame)
            self._io.write_u4le(self.num_tracks)
            self._io.write_u4le(self.num_frames)
            self._io.write_u4le(self.loop_frame)
            for i in range(len(self.init_position)):
                pass
                self._io.write_f4le(self.init_position[i])

            self._io.write_u4le(self.filler)
            for i in range(len(self.init_quaterion)):
                pass
                self._io.write_f4le(self.init_quaterion[i])

            self.collision_events._write__seq(self._io)
            self.motion_sound_effects._write__seq(self._io)


        def _check(self):
            pass
            if (len(self.init_position) != 3):
                raise kaitaistruct.ConsistencyError(u"init_position", len(self.init_position), 3)
            for i in range(len(self.init_position)):
                pass

            if (len(self.init_quaterion) != 4):
                raise kaitaistruct.ConsistencyError(u"init_quaterion", len(self.init_quaterion), 4)
            for i in range(len(self.init_quaterion)):
                pass

            if self.collision_events._root != self._root:
                raise kaitaistruct.ConsistencyError(u"collision_events", self.collision_events._root, self._root)
            if self.collision_events._parent != self:
                raise kaitaistruct.ConsistencyError(u"collision_events", self.collision_events._parent, self)
            if self.motion_sound_effects._root != self._root:
                raise kaitaistruct.ConsistencyError(u"motion_sound_effects", self.motion_sound_effects._root, self._root)
            if self.motion_sound_effects._parent != self:
                raise kaitaistruct.ConsistencyError(u"motion_sound_effects", self.motion_sound_effects._parent, self)

        @property
        def tracks(self):
            if self._should_write_tracks:
                self._write_tracks()
            if hasattr(self, '_m_tracks'):
                return self._m_tracks

            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            self._m_tracks = []
            for i in range(self.num_tracks):
                _t__m_tracks = Lmt.Track51(self._io, self, self._root)
                _t__m_tracks._read()
                self._m_tracks.append(_t__m_tracks)

            self._io.seek(_pos)
            return getattr(self, '_m_tracks', None)

        @tracks.setter
        def tracks(self, v):
            self._m_tracks = v

        def _write_tracks(self):
            self._should_write_tracks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            for i in range(len(self._m_tracks)):
                pass
                self.tracks[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_tracks(self):
            pass
            if (len(self.tracks) != self.num_tracks):
                raise kaitaistruct.ConsistencyError(u"tracks", len(self.tracks), self.num_tracks)
            for i in range(len(self._m_tracks)):
                pass
                if self.tracks[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.tracks[i]._root, self._root)
                if self.tracks[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.tracks[i]._parent, self)



    class EventCollision(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_attributes = False
            self.attributes__to_write = True

        def _read(self):
            self.event_id = []
            for i in range(32):
                self.event_id.append(self._io.read_u2le())

            self.num_events = self._io.read_u4le()
            self.ofs_events = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.event_id)):
                pass

            _ = self.attributes
            for i in range(len(self._m_attributes)):
                pass
                self.attributes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.EventCollision, self)._write__seq(io)
            self._should_write_attributes = self.attributes__to_write
            for i in range(len(self.event_id)):
                pass
                self._io.write_u2le(self.event_id[i])

            self._io.write_u4le(self.num_events)
            self._io.write_u4le(self.ofs_events)


        def _check(self):
            pass
            if (len(self.event_id) != 32):
                raise kaitaistruct.ConsistencyError(u"event_id", len(self.event_id), 32)
            for i in range(len(self.event_id)):
                pass


        @property
        def attributes(self):
            if self._should_write_attributes:
                self._write_attributes()
            if hasattr(self, '_m_attributes'):
                return self._m_attributes

            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            self._m_attributes = []
            for i in range(self.num_events):
                _t__m_attributes = Lmt.Attr(self._io, self, self._root)
                _t__m_attributes._read()
                self._m_attributes.append(_t__m_attributes)

            self._io.seek(_pos)
            return getattr(self, '_m_attributes', None)

        @attributes.setter
        def attributes(self, v):
            self._m_attributes = v

        def _write_attributes(self):
            self._should_write_attributes = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            for i in range(len(self._m_attributes)):
                pass
                self.attributes[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attributes(self):
            pass
            if (len(self.attributes) != self.num_events):
                raise kaitaistruct.ConsistencyError(u"attributes", len(self.attributes), self.num_events)
            for i in range(len(self._m_attributes)):
                pass
                if self.attributes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.attributes[i]._root, self._root)
                if self.attributes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.attributes[i]._parent, self)



    class Attr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.group = self._io.read_u4le()
            self.frame = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Attr, self)._write__seq(io)
            self._io.write_u4le(self.group)
            self._io.write_u4le(self.frame)


        def _check(self):
            pass


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            pass


    class Track51(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_data = False
            self.data__to_write = True

        def _read(self):
            self.buffer_type = self._io.read_u1()
            self.usage = self._io.read_u1()
            self.joint_type = self._io.read_u1()
            self.bone_index = self._io.read_u1()
            self.weight = self._io.read_f4le()
            self.len_data = self._io.read_u4le()
            self.ofs_data = self._io.read_u4le()
            self.reference_data = []
            for i in range(4):
                self.reference_data.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.reference_data)):
                pass

            _ = self.data


        def _write__seq(self, io=None):
            super(Lmt.Track51, self)._write__seq(io)
            self._should_write_data = self.data__to_write
            self._io.write_u1(self.buffer_type)
            self._io.write_u1(self.usage)
            self._io.write_u1(self.joint_type)
            self._io.write_u1(self.bone_index)
            self._io.write_f4le(self.weight)
            self._io.write_u4le(self.len_data)
            self._io.write_u4le(self.ofs_data)
            for i in range(len(self.reference_data)):
                pass
                self._io.write_f4le(self.reference_data[i])



        def _check(self):
            pass
            if (len(self.reference_data) != 4):
                raise kaitaistruct.ConsistencyError(u"reference_data", len(self.reference_data), 4)
            for i in range(len(self.reference_data)):
                pass


        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_data = self._io.read_bytes(self.len_data)
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._io.write_bytes(self.data)
            self._io.seek(_pos)


        def _check_data(self):
            pass
            if (len(self.data) != self.len_data):
                raise kaitaistruct.ConsistencyError(u"data", len(self.data), self.len_data)


    class FloatBuffer(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.addin = []
            for i in range(4):
                self.addin.append(self._io.read_f4le())

            self.offset = []
            for i in range(4):
                self.offset.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.addin)):
                pass

            for i in range(len(self.offset)):
                pass



        def _write__seq(self, io=None):
            super(Lmt.FloatBuffer, self)._write__seq(io)
            for i in range(len(self.addin)):
                pass
                self._io.write_f4le(self.addin[i])

            for i in range(len(self.offset)):
                pass
                self._io.write_f4le(self.offset[i])



        def _check(self):
            pass
            if (len(self.addin) != 4):
                raise kaitaistruct.ConsistencyError(u"addin", len(self.addin), 4)
            for i in range(len(self.addin)):
                pass

            if (len(self.offset) != 4):
                raise kaitaistruct.ConsistencyError(u"offset", len(self.offset), 4)
            for i in range(len(self.offset)):
                pass



    class Track67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_data = False
            self.data__to_write = True

        def _read(self):
            self.buffer_type = self._io.read_u1()
            self.usage = self._io.read_u1()
            self.joint_type = self._io.read_u1()
            self.bone_index = self._io.read_u1()
            self.weight = self._io.read_f4le()
            self.len_data = self._io.read_u4le()
            self.ofs_data = self._io.read_u4le()
            self.reference_data = []
            for i in range(4):
                self.reference_data.append(self._io.read_f4le())

            self.ofs_bounds = Lmt.OfsFrameBounds(self._io, self, self._root)
            self.ofs_bounds._read()


        def _fetch_instances(self):
            pass
            for i in range(len(self.reference_data)):
                pass

            self.ofs_bounds._fetch_instances()
            _ = self.data


        def _write__seq(self, io=None):
            super(Lmt.Track67, self)._write__seq(io)
            self._should_write_data = self.data__to_write
            self._io.write_u1(self.buffer_type)
            self._io.write_u1(self.usage)
            self._io.write_u1(self.joint_type)
            self._io.write_u1(self.bone_index)
            self._io.write_f4le(self.weight)
            self._io.write_u4le(self.len_data)
            self._io.write_u4le(self.ofs_data)
            for i in range(len(self.reference_data)):
                pass
                self._io.write_f4le(self.reference_data[i])

            self.ofs_bounds._write__seq(self._io)


        def _check(self):
            pass
            if (len(self.reference_data) != 4):
                raise kaitaistruct.ConsistencyError(u"reference_data", len(self.reference_data), 4)
            for i in range(len(self.reference_data)):
                pass

            if self.ofs_bounds._root != self._root:
                raise kaitaistruct.ConsistencyError(u"ofs_bounds", self.ofs_bounds._root, self._root)
            if self.ofs_bounds._parent != self:
                raise kaitaistruct.ConsistencyError(u"ofs_bounds", self.ofs_bounds._parent, self)

        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_data = self._io.read_bytes(self.len_data)
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._io.write_bytes(self.data)
            self._io.seek(_pos)


        def _check_data(self):
            pass
            if (len(self.data) != self.len_data):
                raise kaitaistruct.ConsistencyError(u"data", len(self.data), self.len_data)


    class BlockHeader67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_tracks = False
            self.tracks__to_write = True
            self._should_write_block_attributes = False
            self.block_attributes__to_write = True

        def _read(self):
            self.ofs_frame = self._io.read_u4le()
            self.num_tracks = self._io.read_u4le()
            self.num_frames = self._io.read_u4le()
            self.loop_frame = self._io.read_s4le()
            self.init_position = []
            for i in range(3):
                self.init_position.append(self._io.read_f4le())

            self.filler = self._io.read_u4le()
            self.init_quaterion = []
            for i in range(4):
                self.init_quaterion.append(self._io.read_f4le())

            self.flags = []
            for i in range(4):
                self.flags.append(self._io.read_u1())

            self.ofs_attributes = self._io.read_u4le()
            self.ofs_buffer_2 = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.init_position)):
                pass

            for i in range(len(self.init_quaterion)):
                pass

            for i in range(len(self.flags)):
                pass

            _ = self.tracks
            for i in range(len(self._m_tracks)):
                pass
                self.tracks[i]._fetch_instances()

            _ = self.block_attributes
            self.block_attributes._fetch_instances()


        def _write__seq(self, io=None):
            super(Lmt.BlockHeader67, self)._write__seq(io)
            self._should_write_tracks = self.tracks__to_write
            self._should_write_block_attributes = self.block_attributes__to_write
            self._io.write_u4le(self.ofs_frame)
            self._io.write_u4le(self.num_tracks)
            self._io.write_u4le(self.num_frames)
            self._io.write_s4le(self.loop_frame)
            for i in range(len(self.init_position)):
                pass
                self._io.write_f4le(self.init_position[i])

            self._io.write_u4le(self.filler)
            for i in range(len(self.init_quaterion)):
                pass
                self._io.write_f4le(self.init_quaterion[i])

            for i in range(len(self.flags)):
                pass
                self._io.write_u1(self.flags[i])

            self._io.write_u4le(self.ofs_attributes)
            self._io.write_u4le(self.ofs_buffer_2)


        def _check(self):
            pass
            if (len(self.init_position) != 3):
                raise kaitaistruct.ConsistencyError(u"init_position", len(self.init_position), 3)
            for i in range(len(self.init_position)):
                pass

            if (len(self.init_quaterion) != 4):
                raise kaitaistruct.ConsistencyError(u"init_quaterion", len(self.init_quaterion), 4)
            for i in range(len(self.init_quaterion)):
                pass

            if (len(self.flags) != 4):
                raise kaitaistruct.ConsistencyError(u"flags", len(self.flags), 4)
            for i in range(len(self.flags)):
                pass


        @property
        def tracks(self):
            if self._should_write_tracks:
                self._write_tracks()
            if hasattr(self, '_m_tracks'):
                return self._m_tracks

            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            self._m_tracks = []
            for i in range(self.num_tracks):
                _t__m_tracks = Lmt.Track67(self._io, self, self._root)
                _t__m_tracks._read()
                self._m_tracks.append(_t__m_tracks)

            self._io.seek(_pos)
            return getattr(self, '_m_tracks', None)

        @tracks.setter
        def tracks(self, v):
            self._m_tracks = v

        def _write_tracks(self):
            self._should_write_tracks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            for i in range(len(self._m_tracks)):
                pass
                self.tracks[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_tracks(self):
            pass
            if (len(self.tracks) != self.num_tracks):
                raise kaitaistruct.ConsistencyError(u"tracks", len(self.tracks), self.num_tracks)
            for i in range(len(self._m_tracks)):
                pass
                if self.tracks[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.tracks[i]._root, self._root)
                if self.tracks[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.tracks[i]._parent, self)


        @property
        def block_attributes(self):
            if self._should_write_block_attributes:
                self._write_block_attributes()
            if hasattr(self, '_m_block_attributes'):
                return self._m_block_attributes

            _pos = self._io.pos()
            self._io.seek(self.ofs_attributes)
            self._m_block_attributes = Lmt.Attributes67(self._io, self, self._root)
            self._m_block_attributes._read()
            self._io.seek(_pos)
            return getattr(self, '_m_block_attributes', None)

        @block_attributes.setter
        def block_attributes(self, v):
            self._m_block_attributes = v

        def _write_block_attributes(self):
            self._should_write_block_attributes = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_attributes)
            self.block_attributes._write__seq(self._io)
            self._io.seek(_pos)


        def _check_block_attributes(self):
            pass
            if self.block_attributes._root != self._root:
                raise kaitaistruct.ConsistencyError(u"block_attributes", self.block_attributes._root, self._root)
            if self.block_attributes._parent != self:
                raise kaitaistruct.ConsistencyError(u"block_attributes", self.block_attributes._parent, self)



