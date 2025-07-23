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


    class KeyframeInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_keyframe_blocks = False
            self.keyframe_blocks__to_write = True

        def _read(self):
            self.type = self._io.read_bits_int_le(8)
            self.work = self._io.read_bits_int_le(16)
            self.attr = self._io.read_bits_int_le(8)
            self.num_key = self._io.read_u4le()
            self.ofs_seq = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.keyframe_blocks
            for i in range(len(self._m_keyframe_blocks)):
                pass
                self.keyframe_blocks[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.KeyframeInfo, self)._write__seq(io)
            self._should_write_keyframe_blocks = self.keyframe_blocks__to_write
            self._io.write_bits_int_le(8, self.type)
            self._io.write_bits_int_le(16, self.work)
            self._io.write_bits_int_le(8, self.attr)
            self._io.write_u4le(self.num_key)
            self._io.write_u4le(self.ofs_seq)


        def _check(self):
            pass

        @property
        def keyframe_blocks(self):
            if self._should_write_keyframe_blocks:
                self._write_keyframe_blocks()
            if hasattr(self, '_m_keyframe_blocks'):
                return self._m_keyframe_blocks

            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            self._m_keyframe_blocks = []
            for i in range(self.num_key):
                _t__m_keyframe_blocks = Lmt.KeyframeBlock(self._io, self, self._root)
                _t__m_keyframe_blocks._read()
                self._m_keyframe_blocks.append(_t__m_keyframe_blocks)

            self._io.seek(_pos)
            return getattr(self, '_m_keyframe_blocks', None)

        @keyframe_blocks.setter
        def keyframe_blocks(self, v):
            self._m_keyframe_blocks = v

        def _write_keyframe_blocks(self):
            self._should_write_keyframe_blocks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            for i in range(len(self._m_keyframe_blocks)):
                pass
                self.keyframe_blocks[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_keyframe_blocks(self):
            pass
            if (len(self.keyframe_blocks) != self.num_key):
                raise kaitaistruct.ConsistencyError(u"keyframe_blocks", len(self.keyframe_blocks), self.num_key)
            for i in range(len(self._m_keyframe_blocks)):
                pass
                if self.keyframe_blocks[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"keyframe_blocks", self.keyframe_blocks[i]._root, self._root)
                if self.keyframe_blocks[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"keyframe_blocks", self.keyframe_blocks[i]._parent, self)



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



    class SeqInfoAttr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u2le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.SeqInfoAttr, self)._write__seq(io)
            self._io.write_u2le(self.unk_00)
            self._io.write_u2le(self.unk_01)
            self._io.write_u4le(self.unk_02)


        def _check(self):
            pass


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



    class KeyframeBlock(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u2le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_f4le()
            self.unk_03 = self._io.read_f4le()
            self.unk_04 = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.KeyframeBlock, self)._write__seq(io)
            self._io.write_u2le(self.unk_00)
            self._io.write_u2le(self.unk_01)
            self._io.write_f4le(self.unk_02)
            self._io.write_f4le(self.unk_03)
            self._io.write_f4le(self.unk_04)


        def _check(self):
            pass


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



    class SequenceInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_attributes = False
            self.attributes__to_write = True

        def _read(self):
            self.work = []
            for i in range(32):
                self.work.append(self._io.read_u2le())

            self.num_seq = self._io.read_u4le()
            self.ofs_seq = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.work)):
                pass

            _ = self.attributes
            for i in range(len(self._m_attributes)):
                pass
                self.attributes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.SequenceInfo, self)._write__seq(io)
            self._should_write_attributes = self.attributes__to_write
            for i in range(len(self.work)):
                pass
                self._io.write_u2le(self.work[i])

            self._io.write_u4le(self.num_seq)
            self._io.write_u4le(self.ofs_seq)


        def _check(self):
            pass
            if (len(self.work) != 32):
                raise kaitaistruct.ConsistencyError(u"work", len(self.work), 32)
            for i in range(len(self.work)):
                pass


        @property
        def attributes(self):
            if self._should_write_attributes:
                self._write_attributes()
            if hasattr(self, '_m_attributes'):
                return self._m_attributes

            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            self._m_attributes = []
            for i in range(self.num_seq):
                _t__m_attributes = Lmt.SeqInfoAttr(self._io, self, self._root)
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
            self._io.seek(self.ofs_seq)
            for i in range(len(self._m_attributes)):
                pass
                self.attributes[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_attributes(self):
            pass
            if (len(self.attributes) != self.num_seq):
                raise kaitaistruct.ConsistencyError(u"attributes", len(self.attributes), self.num_seq)
            for i in range(len(self._m_attributes)):
                pass
                if self.attributes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.attributes[i]._root, self._root)
                if self.attributes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.attributes[i]._parent, self)



    class Track67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_data = False
            self.data__to_write = True
            self._should_write_bounds = False
            self.bounds__to_write = True

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

            self.ofs_bounds = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.reference_data)):
                pass

            _ = self.data
            if self.is_used:
                pass
                _ = self.bounds
                self.bounds._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.Track67, self)._write__seq(io)
            self._should_write_data = self.data__to_write
            self._should_write_bounds = self.bounds__to_write
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

            self._io.write_u4le(self.ofs_bounds)


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

        @property
        def is_used(self):
            if hasattr(self, '_m_is_used'):
                return self._m_is_used

            self._m_is_used = (self.ofs_data != 0)
            return getattr(self, '_m_is_used', None)

        def _invalidate_is_used(self):
            del self._m_is_used
        @property
        def bounds(self):
            if self._should_write_bounds:
                self._write_bounds()
            if hasattr(self, '_m_bounds'):
                return self._m_bounds

            if self.is_used:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bounds)
                self._m_bounds = Lmt.FloatBuffer(self._io, self, self._root)
                self._m_bounds._read()
                self._io.seek(_pos)

            return getattr(self, '_m_bounds', None)

        @bounds.setter
        def bounds(self, v):
            self._m_bounds = v

        def _write_bounds(self):
            self._should_write_bounds = False
            if self.is_used:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bounds)
                self.bounds._write__seq(self._io)
                self._io.seek(_pos)



        def _check_bounds(self):
            pass
            if self.is_used:
                pass
                if self.bounds._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bounds", self.bounds._root, self._root)
                if self.bounds._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bounds", self.bounds._parent, self)



    class BlockHeader67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_tracks = False
            self.tracks__to_write = True
            self._should_write_sequence_infos = False
            self.sequence_infos__to_write = True
            self._should_write_key_infos = False
            self.key_infos__to_write = True

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

            self.attr = self._io.read_bits_int_le(16)
            self.kf_num = self._io.read_bits_int_le(5)
            self.seq_num = self._io.read_bits_int_le(3)
            self.duplicate = self._io.read_bits_int_le(3)
            self.reserved = self._io.read_bits_int_le(5)
            self.ofs_sequence_infos = self._io.read_u4le()
            self.ofs_keyframe_infos = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.init_position)):
                pass

            for i in range(len(self.init_quaterion)):
                pass

            _ = self.tracks
            for i in range(len(self._m_tracks)):
                pass
                self.tracks[i]._fetch_instances()

            _ = self.sequence_infos
            for i in range(len(self._m_sequence_infos)):
                pass
                self.sequence_infos[i]._fetch_instances()

            _ = self.key_infos
            for i in range(len(self._m_key_infos)):
                pass
                self.key_infos[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.BlockHeader67, self)._write__seq(io)
            self._should_write_tracks = self.tracks__to_write
            self._should_write_sequence_infos = self.sequence_infos__to_write
            self._should_write_key_infos = self.key_infos__to_write
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

            self._io.write_bits_int_le(16, self.attr)
            self._io.write_bits_int_le(5, self.kf_num)
            self._io.write_bits_int_le(3, self.seq_num)
            self._io.write_bits_int_le(3, self.duplicate)
            self._io.write_bits_int_le(5, self.reserved)
            self._io.write_u4le(self.ofs_sequence_infos)
            self._io.write_u4le(self.ofs_keyframe_infos)


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
        def sequence_infos(self):
            if self._should_write_sequence_infos:
                self._write_sequence_infos()
            if hasattr(self, '_m_sequence_infos'):
                return self._m_sequence_infos

            _pos = self._io.pos()
            self._io.seek(self.ofs_sequence_infos)
            self._m_sequence_infos = []
            for i in range(self.seq_num):
                _t__m_sequence_infos = Lmt.SequenceInfo(self._io, self, self._root)
                _t__m_sequence_infos._read()
                self._m_sequence_infos.append(_t__m_sequence_infos)

            self._io.seek(_pos)
            return getattr(self, '_m_sequence_infos', None)

        @sequence_infos.setter
        def sequence_infos(self, v):
            self._m_sequence_infos = v

        def _write_sequence_infos(self):
            self._should_write_sequence_infos = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_sequence_infos)
            for i in range(len(self._m_sequence_infos)):
                pass
                self.sequence_infos[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_sequence_infos(self):
            pass
            if (len(self.sequence_infos) != self.seq_num):
                raise kaitaistruct.ConsistencyError(u"sequence_infos", len(self.sequence_infos), self.seq_num)
            for i in range(len(self._m_sequence_infos)):
                pass
                if self.sequence_infos[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"sequence_infos", self.sequence_infos[i]._root, self._root)
                if self.sequence_infos[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"sequence_infos", self.sequence_infos[i]._parent, self)


        @property
        def key_infos(self):
            if self._should_write_key_infos:
                self._write_key_infos()
            if hasattr(self, '_m_key_infos'):
                return self._m_key_infos

            _pos = self._io.pos()
            self._io.seek(self.ofs_keyframe_infos)
            self._m_key_infos = []
            for i in range(self.kf_num):
                _t__m_key_infos = Lmt.KeyframeInfo(self._io, self, self._root)
                _t__m_key_infos._read()
                self._m_key_infos.append(_t__m_key_infos)

            self._io.seek(_pos)
            return getattr(self, '_m_key_infos', None)

        @key_infos.setter
        def key_infos(self, v):
            self._m_key_infos = v

        def _write_key_infos(self):
            self._should_write_key_infos = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_keyframe_infos)
            for i in range(len(self._m_key_infos)):
                pass
                self.key_infos[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_key_infos(self):
            pass
            if (len(self.key_infos) != self.kf_num):
                raise kaitaistruct.ConsistencyError(u"key_infos", len(self.key_infos), self.kf_num)
            for i in range(len(self._m_key_infos)):
                pass
                if self.key_infos[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"key_infos", self.key_infos[i]._root, self._root)
                if self.key_infos[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"key_infos", self.key_infos[i]._parent, self)




