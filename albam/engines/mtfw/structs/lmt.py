# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lmt(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Lmt, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4C\x4D\x54\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4C\x4D\x54\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.num_block_offsets = self._io.read_u2le()
        self.block_offsets = []
        for i in range(self.num_block_offsets):
            _t_block_offsets = Lmt.BlockOffset(self._io, self, self._root)
            try:
                _t_block_offsets._read()
            finally:
                self.block_offsets.append(_t_block_offsets)

        self._dirty = False


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
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x4C\x4D\x54\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4C\x4D\x54\x00", self.id_magic, None, u"/seq/0")
        if len(self.block_offsets) != self.num_block_offsets:
            raise kaitaistruct.ConsistencyError(u"block_offsets", self.num_block_offsets, len(self.block_offsets))
        for i in range(len(self.block_offsets)):
            pass
            if self.block_offsets[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"block_offsets", self._root, self.block_offsets[i]._root)
            if self.block_offsets[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"block_offsets", self, self.block_offsets[i]._parent)

        self._dirty = False

    class Attr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Attr, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.group = self._io.read_u4le()
            self.frame = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Attr, self)._write__seq(io)
            self._io.write_u4le(self.group)
            self._io.write_u4le(self.frame)


        def _check(self):
            self._dirty = False


    class BlockHeader51(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.BlockHeader51, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_tracks = False
            self.tracks__enabled = True

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

            self.collision_events = Lmt.EventCollision(self._io, self, self._root)
            self.collision_events._read()
            self.motion_sound_effects = Lmt.MotionSe(self._io, self, self._root)
            self.motion_sound_effects._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.init_position)):
                pass

            for i in range(len(self.init_quaterion)):
                pass

            self.collision_events._fetch_instances()
            self.motion_sound_effects._fetch_instances()
            _ = self.tracks
            if hasattr(self, '_m_tracks'):
                pass
                for i in range(len(self._m_tracks)):
                    pass
                    self._m_tracks[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.BlockHeader51, self)._write__seq(io)
            self._should_write_tracks = self.tracks__enabled
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

            self.collision_events._write__seq(self._io)
            self.motion_sound_effects._write__seq(self._io)


        def _check(self):
            if len(self.init_position) != 3:
                raise kaitaistruct.ConsistencyError(u"init_position", 3, len(self.init_position))
            for i in range(len(self.init_position)):
                pass

            if len(self.init_quaterion) != 4:
                raise kaitaistruct.ConsistencyError(u"init_quaterion", 4, len(self.init_quaterion))
            for i in range(len(self.init_quaterion)):
                pass

            if self.collision_events._root != self._root:
                raise kaitaistruct.ConsistencyError(u"collision_events", self._root, self.collision_events._root)
            if self.collision_events._parent != self:
                raise kaitaistruct.ConsistencyError(u"collision_events", self, self.collision_events._parent)
            if self.motion_sound_effects._root != self._root:
                raise kaitaistruct.ConsistencyError(u"motion_sound_effects", self._root, self.motion_sound_effects._root)
            if self.motion_sound_effects._parent != self:
                raise kaitaistruct.ConsistencyError(u"motion_sound_effects", self, self.motion_sound_effects._parent)
            if self.tracks__enabled:
                pass
                if len(self._m_tracks) != self.num_tracks:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.num_tracks, len(self._m_tracks))
                for i in range(len(self._m_tracks)):
                    pass
                    if self._m_tracks[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"tracks", self._root, self._m_tracks[i]._root)
                    if self._m_tracks[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"tracks", self, self._m_tracks[i]._parent)


            self._dirty = False

        @property
        def tracks(self):
            if self._should_write_tracks:
                self._write_tracks()
            if hasattr(self, '_m_tracks'):
                return self._m_tracks

            if not self.tracks__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            self._m_tracks = []
            for i in range(self.num_tracks):
                _t__m_tracks = Lmt.Track51(self._io, self, self._root)
                try:
                    _t__m_tracks._read()
                finally:
                    self._m_tracks.append(_t__m_tracks)

            self._io.seek(_pos)
            return getattr(self, '_m_tracks', None)

        @tracks.setter
        def tracks(self, v):
            self._dirty = True
            self._m_tracks = v

        def _write_tracks(self):
            self._should_write_tracks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            for i in range(len(self._m_tracks)):
                pass
                self._m_tracks[i]._write__seq(self._io)

            self._io.seek(_pos)


    class BlockHeader67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.BlockHeader67, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_key_infos = False
            self.key_infos__enabled = True
            self._should_write_sequence_infos = False
            self.sequence_infos__enabled = True
            self._should_write_tracks = False
            self.tracks__enabled = True

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
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.init_position)):
                pass

            for i in range(len(self.init_quaterion)):
                pass

            _ = self.key_infos
            if hasattr(self, '_m_key_infos'):
                pass
                for i in range(len(self._m_key_infos)):
                    pass
                    self._m_key_infos[i]._fetch_instances()


            _ = self.sequence_infos
            if hasattr(self, '_m_sequence_infos'):
                pass
                for i in range(len(self._m_sequence_infos)):
                    pass
                    self._m_sequence_infos[i]._fetch_instances()


            _ = self.tracks
            if hasattr(self, '_m_tracks'):
                pass
                for i in range(len(self._m_tracks)):
                    pass
                    self._m_tracks[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.BlockHeader67, self)._write__seq(io)
            self._should_write_key_infos = self.key_infos__enabled
            self._should_write_sequence_infos = self.sequence_infos__enabled
            self._should_write_tracks = self.tracks__enabled
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
            if len(self.init_position) != 3:
                raise kaitaistruct.ConsistencyError(u"init_position", 3, len(self.init_position))
            for i in range(len(self.init_position)):
                pass

            if len(self.init_quaterion) != 4:
                raise kaitaistruct.ConsistencyError(u"init_quaterion", 4, len(self.init_quaterion))
            for i in range(len(self.init_quaterion)):
                pass

            if self.key_infos__enabled:
                pass
                if len(self._m_key_infos) != self.kf_num:
                    raise kaitaistruct.ConsistencyError(u"key_infos", self.kf_num, len(self._m_key_infos))
                for i in range(len(self._m_key_infos)):
                    pass
                    if self._m_key_infos[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"key_infos", self._root, self._m_key_infos[i]._root)
                    if self._m_key_infos[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"key_infos", self, self._m_key_infos[i]._parent)


            if self.sequence_infos__enabled:
                pass
                if len(self._m_sequence_infos) != self.seq_num:
                    raise kaitaistruct.ConsistencyError(u"sequence_infos", self.seq_num, len(self._m_sequence_infos))
                for i in range(len(self._m_sequence_infos)):
                    pass
                    if self._m_sequence_infos[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"sequence_infos", self._root, self._m_sequence_infos[i]._root)
                    if self._m_sequence_infos[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"sequence_infos", self, self._m_sequence_infos[i]._parent)


            if self.tracks__enabled:
                pass
                if len(self._m_tracks) != self.num_tracks:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.num_tracks, len(self._m_tracks))
                for i in range(len(self._m_tracks)):
                    pass
                    if self._m_tracks[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"tracks", self._root, self._m_tracks[i]._root)
                    if self._m_tracks[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"tracks", self, self._m_tracks[i]._parent)


            self._dirty = False

        @property
        def key_infos(self):
            if self._should_write_key_infos:
                self._write_key_infos()
            if hasattr(self, '_m_key_infos'):
                return self._m_key_infos

            if not self.key_infos__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_keyframe_infos)
            self._m_key_infos = []
            for i in range(self.kf_num):
                _t__m_key_infos = Lmt.KeyframeInfo(self._io, self, self._root)
                try:
                    _t__m_key_infos._read()
                finally:
                    self._m_key_infos.append(_t__m_key_infos)

            self._io.seek(_pos)
            return getattr(self, '_m_key_infos', None)

        @key_infos.setter
        def key_infos(self, v):
            self._dirty = True
            self._m_key_infos = v

        def _write_key_infos(self):
            self._should_write_key_infos = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_keyframe_infos)
            for i in range(len(self._m_key_infos)):
                pass
                self._m_key_infos[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def sequence_infos(self):
            if self._should_write_sequence_infos:
                self._write_sequence_infos()
            if hasattr(self, '_m_sequence_infos'):
                return self._m_sequence_infos

            if not self.sequence_infos__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_sequence_infos)
            self._m_sequence_infos = []
            for i in range(self.seq_num):
                _t__m_sequence_infos = Lmt.SequenceInfo(self._io, self, self._root)
                try:
                    _t__m_sequence_infos._read()
                finally:
                    self._m_sequence_infos.append(_t__m_sequence_infos)

            self._io.seek(_pos)
            return getattr(self, '_m_sequence_infos', None)

        @sequence_infos.setter
        def sequence_infos(self, v):
            self._dirty = True
            self._m_sequence_infos = v

        def _write_sequence_infos(self):
            self._should_write_sequence_infos = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_sequence_infos)
            for i in range(len(self._m_sequence_infos)):
                pass
                self._m_sequence_infos[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def tracks(self):
            if self._should_write_tracks:
                self._write_tracks()
            if hasattr(self, '_m_tracks'):
                return self._m_tracks

            if not self.tracks__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            self._m_tracks = []
            for i in range(self.num_tracks):
                _t__m_tracks = Lmt.Track67(self._io, self, self._root)
                try:
                    _t__m_tracks._read()
                finally:
                    self._m_tracks.append(_t__m_tracks)

            self._io.seek(_pos)
            return getattr(self, '_m_tracks', None)

        @tracks.setter
        def tracks(self, v):
            self._dirty = True
            self._m_tracks = v

        def _write_tracks(self):
            self._should_write_tracks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_frame)
            for i in range(len(self._m_tracks)):
                pass
                self._m_tracks[i]._write__seq(self._io)

            self._io.seek(_pos)


    class BlockOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.BlockOffset, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_block_header = False
            self.block_header__enabled = True

        def _read(self):
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.block_header
            if hasattr(self, '_m_block_header'):
                pass
                _on = self.lmt_ver
                if _on == 51:
                    pass
                    self._m_block_header._fetch_instances()
                elif _on == 67:
                    pass
                    self._m_block_header._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.BlockOffset, self)._write__seq(io)
            self._should_write_block_header = self.block_header__enabled
            self._io.write_u4le(self.offset)


        def _check(self):
            if self.block_header__enabled:
                pass
                if self.is_used:
                    pass
                    _on = self.lmt_ver
                    if _on == 51:
                        pass
                        if self._m_block_header._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"block_header", self._root, self._m_block_header._root)
                        if self._m_block_header._parent != self:
                            raise kaitaistruct.ConsistencyError(u"block_header", self, self._m_block_header._parent)
                    elif _on == 67:
                        pass
                        if self._m_block_header._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"block_header", self._root, self._m_block_header._root)
                        if self._m_block_header._parent != self:
                            raise kaitaistruct.ConsistencyError(u"block_header", self, self._m_block_header._parent)


            self._dirty = False

        @property
        def block_header(self):
            if self._should_write_block_header:
                self._write_block_header()
            if hasattr(self, '_m_block_header'):
                return self._m_block_header

            if not self.block_header__enabled:
                return None

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
            self._dirty = True
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
                    self._m_block_header._write__seq(self._io)
                elif _on == 67:
                    pass
                    self._m_block_header._write__seq(self._io)
                self._io.seek(_pos)


        @property
        def is_used(self):
            if hasattr(self, '_m_is_used'):
                return self._m_is_used

            self._m_is_used = self.offset != 0
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

    class EventCollision(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.EventCollision, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_attributes = False
            self.attributes__enabled = True

        def _read(self):
            self.event_id = []
            for i in range(32):
                self.event_id.append(self._io.read_u2le())

            self.num_events = self._io.read_u4le()
            self.ofs_events = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.event_id)):
                pass

            _ = self.attributes
            if hasattr(self, '_m_attributes'):
                pass
                for i in range(len(self._m_attributes)):
                    pass
                    self._m_attributes[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.EventCollision, self)._write__seq(io)
            self._should_write_attributes = self.attributes__enabled
            for i in range(len(self.event_id)):
                pass
                self._io.write_u2le(self.event_id[i])

            self._io.write_u4le(self.num_events)
            self._io.write_u4le(self.ofs_events)


        def _check(self):
            if len(self.event_id) != 32:
                raise kaitaistruct.ConsistencyError(u"event_id", 32, len(self.event_id))
            for i in range(len(self.event_id)):
                pass

            if self.attributes__enabled:
                pass
                if len(self._m_attributes) != self.num_events:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.num_events, len(self._m_attributes))
                for i in range(len(self._m_attributes)):
                    pass
                    if self._m_attributes[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"attributes", self._root, self._m_attributes[i]._root)
                    if self._m_attributes[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"attributes", self, self._m_attributes[i]._parent)


            self._dirty = False

        @property
        def attributes(self):
            if self._should_write_attributes:
                self._write_attributes()
            if hasattr(self, '_m_attributes'):
                return self._m_attributes

            if not self.attributes__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            self._m_attributes = []
            for i in range(self.num_events):
                _t__m_attributes = Lmt.Attr(self._io, self, self._root)
                try:
                    _t__m_attributes._read()
                finally:
                    self._m_attributes.append(_t__m_attributes)

            self._io.seek(_pos)
            return getattr(self, '_m_attributes', None)

        @attributes.setter
        def attributes(self, v):
            self._dirty = True
            self._m_attributes = v

        def _write_attributes(self):
            self._should_write_attributes = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            for i in range(len(self._m_attributes)):
                pass
                self._m_attributes[i]._write__seq(self._io)

            self._io.seek(_pos)


    class FloatBuffer(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.FloatBuffer, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.addin = []
            for i in range(4):
                self.addin.append(self._io.read_f4le())

            self.offset = []
            for i in range(4):
                self.offset.append(self._io.read_f4le())

            self._dirty = False


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
            if len(self.addin) != 4:
                raise kaitaistruct.ConsistencyError(u"addin", 4, len(self.addin))
            for i in range(len(self.addin)):
                pass

            if len(self.offset) != 4:
                raise kaitaistruct.ConsistencyError(u"offset", 4, len(self.offset))
            for i in range(len(self.offset)):
                pass

            self._dirty = False


    class KeyframeBlock(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.KeyframeBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u2le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_f4le()
            self.unk_03 = self._io.read_f4le()
            self.unk_04 = self._io.read_f4le()
            self._dirty = False


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
            self._dirty = False


    class KeyframeInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.KeyframeInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_keyframe_blocks = False
            self.keyframe_blocks__enabled = True

        def _read(self):
            self.type = self._io.read_bits_int_le(8)
            self.work = self._io.read_bits_int_le(16)
            self.attr = self._io.read_bits_int_le(8)
            self.num_key = self._io.read_u4le()
            self.ofs_seq = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.keyframe_blocks
            if hasattr(self, '_m_keyframe_blocks'):
                pass
                for i in range(len(self._m_keyframe_blocks)):
                    pass
                    self._m_keyframe_blocks[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.KeyframeInfo, self)._write__seq(io)
            self._should_write_keyframe_blocks = self.keyframe_blocks__enabled
            self._io.write_bits_int_le(8, self.type)
            self._io.write_bits_int_le(16, self.work)
            self._io.write_bits_int_le(8, self.attr)
            self._io.write_u4le(self.num_key)
            self._io.write_u4le(self.ofs_seq)


        def _check(self):
            if self.keyframe_blocks__enabled:
                pass
                if len(self._m_keyframe_blocks) != self.num_key:
                    raise kaitaistruct.ConsistencyError(u"keyframe_blocks", self.num_key, len(self._m_keyframe_blocks))
                for i in range(len(self._m_keyframe_blocks)):
                    pass
                    if self._m_keyframe_blocks[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"keyframe_blocks", self._root, self._m_keyframe_blocks[i]._root)
                    if self._m_keyframe_blocks[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"keyframe_blocks", self, self._m_keyframe_blocks[i]._parent)


            self._dirty = False

        @property
        def keyframe_blocks(self):
            if self._should_write_keyframe_blocks:
                self._write_keyframe_blocks()
            if hasattr(self, '_m_keyframe_blocks'):
                return self._m_keyframe_blocks

            if not self.keyframe_blocks__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            self._m_keyframe_blocks = []
            for i in range(self.num_key):
                _t__m_keyframe_blocks = Lmt.KeyframeBlock(self._io, self, self._root)
                try:
                    _t__m_keyframe_blocks._read()
                finally:
                    self._m_keyframe_blocks.append(_t__m_keyframe_blocks)

            self._io.seek(_pos)
            return getattr(self, '_m_keyframe_blocks', None)

        @keyframe_blocks.setter
        def keyframe_blocks(self, v):
            self._dirty = True
            self._m_keyframe_blocks = v

        def _write_keyframe_blocks(self):
            self._should_write_keyframe_blocks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            for i in range(len(self._m_keyframe_blocks)):
                pass
                self._m_keyframe_blocks[i]._write__seq(self._io)

            self._io.seek(_pos)


    class MotionSe(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.MotionSe, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_attributes = False
            self.attributes__enabled = True

        def _read(self):
            self.event_id = []
            for i in range(32):
                self.event_id.append(self._io.read_u2le())

            self.num_events = self._io.read_u4le()
            self.ofs_events = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.event_id)):
                pass

            _ = self.attributes
            if hasattr(self, '_m_attributes'):
                pass
                for i in range(len(self._m_attributes)):
                    pass
                    self._m_attributes[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.MotionSe, self)._write__seq(io)
            self._should_write_attributes = self.attributes__enabled
            for i in range(len(self.event_id)):
                pass
                self._io.write_u2le(self.event_id[i])

            self._io.write_u4le(self.num_events)
            self._io.write_u4le(self.ofs_events)


        def _check(self):
            if len(self.event_id) != 32:
                raise kaitaistruct.ConsistencyError(u"event_id", 32, len(self.event_id))
            for i in range(len(self.event_id)):
                pass

            if self.attributes__enabled:
                pass
                if len(self._m_attributes) != self.num_events:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.num_events, len(self._m_attributes))
                for i in range(len(self._m_attributes)):
                    pass
                    if self._m_attributes[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"attributes", self._root, self._m_attributes[i]._root)
                    if self._m_attributes[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"attributes", self, self._m_attributes[i]._parent)


            self._dirty = False

        @property
        def attributes(self):
            if self._should_write_attributes:
                self._write_attributes()
            if hasattr(self, '_m_attributes'):
                return self._m_attributes

            if not self.attributes__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            self._m_attributes = []
            for i in range(self.num_events):
                _t__m_attributes = Lmt.Attr(self._io, self, self._root)
                try:
                    _t__m_attributes._read()
                finally:
                    self._m_attributes.append(_t__m_attributes)

            self._io.seek(_pos)
            return getattr(self, '_m_attributes', None)

        @attributes.setter
        def attributes(self, v):
            self._dirty = True
            self._m_attributes = v

        def _write_attributes(self):
            self._should_write_attributes = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_events)
            for i in range(len(self._m_attributes)):
                pass
                self._m_attributes[i]._write__seq(self._io)

            self._io.seek(_pos)


    class PolarFrame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.PolarFrame, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(17)
            self.y = self._io.read_bits_int_le(17)
            self.w = self._io.read_bits_int_le(19)
            self.flags = self._io.read_bits_int_le(3)
            self.duration = self._io.read_bits_int_le(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.PolarFrame, self)._write__seq(io)
            self._io.write_bits_int_le(17, self.x)
            self._io.write_bits_int_le(17, self.y)
            self._io.write_bits_int_le(19, self.w)
            self._io.write_bits_int_le(3, self.flags)
            self._io.write_bits_int_le(8, self.duration)


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

    class QuadraticVector3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.QuadraticVector3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.size = self._io.read_u1()
            self.flags = self._io.read_u1()
            self.duration = self._io.read_u2le()
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            if self.flags >> 1 > 0:
                pass
                self.outtangent_x = self._io.read_f4le()

            if self.flags >> 2 > 0:
                pass
                self.outtangent_y = self._io.read_f4le()

            if self.flags >> 4 > 0:
                pass
                self.outtangent_z = self._io.read_f4le()

            if self.flags >> 8 > 0:
                pass
                self.nextframeintangent_x = self._io.read_f4le()

            if self.flags >> 16 > 0:
                pass
                self.nextframeintangent_y = self._io.read_f4le()

            if self.flags >> 32 > 0:
                pass
                self.nextframeintangent_z = self._io.read_f4le()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.flags >> 1 > 0:
                pass

            if self.flags >> 2 > 0:
                pass

            if self.flags >> 4 > 0:
                pass

            if self.flags >> 8 > 0:
                pass

            if self.flags >> 16 > 0:
                pass

            if self.flags >> 32 > 0:
                pass



        def _write__seq(self, io=None):
            super(Lmt.QuadraticVector3, self)._write__seq(io)
            self._io.write_u1(self.size)
            self._io.write_u1(self.flags)
            self._io.write_u2le(self.duration)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            if self.flags >> 1 > 0:
                pass
                self._io.write_f4le(self.outtangent_x)

            if self.flags >> 2 > 0:
                pass
                self._io.write_f4le(self.outtangent_y)

            if self.flags >> 4 > 0:
                pass
                self._io.write_f4le(self.outtangent_z)

            if self.flags >> 8 > 0:
                pass
                self._io.write_f4le(self.nextframeintangent_x)

            if self.flags >> 16 > 0:
                pass
                self._io.write_f4le(self.nextframeintangent_y)

            if self.flags >> 32 > 0:
                pass
                self._io.write_f4le(self.nextframeintangent_z)



        def _check(self):
            if self.flags >> 1 > 0:
                pass

            if self.flags >> 2 > 0:
                pass

            if self.flags >> 4 > 0:
                pass

            if self.flags >> 8 > 0:
                pass

            if self.flags >> 16 > 0:
                pass

            if self.flags >> 32 > 0:
                pass

            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = self.size
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Quat3Frame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Quat3Frame, self).__init__(_io)
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
            super(Lmt.Quat3Frame, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 12
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class QuatFramev14(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.QuatFramev14, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.w = self._io.read_bits_int_le(14)
            self.z = self._io.read_bits_int_le(14)
            self.y = self._io.read_bits_int_le(14)
            self.x = self._io.read_bits_int_le(14)
            self.duration = self._io.read_bits_int_le(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.QuatFramev14, self)._write__seq(io)
            self._io.write_bits_int_le(14, self.w)
            self._io.write_bits_int_le(14, self.z)
            self._io.write_bits_int_le(14, self.y)
            self._io.write_bits_int_le(14, self.x)
            self._io.write_bits_int_le(8, self.duration)


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

    class Quatized11Quat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Quatized11Quat, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(11)
            self.y = self._io.read_bits_int_le(11)
            self.z = self._io.read_bits_int_le(11)
            self.w = self._io.read_bits_int_le(11)
            self.duration = self._io.read_bits_int_le(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Quatized11Quat, self)._write__seq(io)
            self._io.write_bits_int_le(11, self.x)
            self._io.write_bits_int_le(11, self.y)
            self._io.write_bits_int_le(11, self.z)
            self._io.write_bits_int_le(11, self.w)
            self._io.write_bits_int_le(4, self.duration)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 6
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Quatized16Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Quatized16Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u2le()
            self.y = self._io.read_u2le()
            self.z = self._io.read_u2le()
            self.duration = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Quatized16Vec3, self)._write__seq(io)
            self._io.write_u2le(self.x)
            self._io.write_u2le(self.y)
            self._io.write_u2le(self.z)
            self._io.write_u2le(self.duration)


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

    class Quatized32Quat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Quatized32Quat, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.w = self._io.read_bits_int_le(7)
            self.z = self._io.read_bits_int_le(7)
            self.y = self._io.read_bits_int_le(7)
            self.x = self._io.read_bits_int_le(7)
            self.duration = self._io.read_bits_int_le(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Quatized32Quat, self)._write__seq(io)
            self._io.write_bits_int_le(7, self.w)
            self._io.write_bits_int_le(7, self.z)
            self._io.write_bits_int_le(7, self.y)
            self._io.write_bits_int_le(7, self.x)
            self._io.write_bits_int_le(4, self.duration)


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

    class Quatized8Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Quatized8Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()
            self.duration = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Quatized8Vec3, self)._write__seq(io)
            self._io.write_u1(self.x)
            self._io.write_u1(self.y)
            self._io.write_u1(self.z)
            self._io.write_u1(self.duration)


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

    class Quatized9Quat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Quatized9Quat, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(9)
            self.y = self._io.read_bits_int_le(9)
            self.z = self._io.read_bits_int_le(9)
            self.w = self._io.read_bits_int_le(9)
            self.duration = self._io.read_bits_int_le(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Quatized9Quat, self)._write__seq(io)
            self._io.write_bits_int_le(9, self.x)
            self._io.write_bits_int_le(9, self.y)
            self._io.write_bits_int_le(9, self.z)
            self._io.write_bits_int_le(9, self.w)
            self._io.write_bits_int_le(4, self.duration)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 5
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class SeqInfoAttr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.SeqInfoAttr, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u2le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.SeqInfoAttr, self)._write__seq(io)
            self._io.write_u2le(self.unk_00)
            self._io.write_u2le(self.unk_01)
            self._io.write_u4le(self.unk_02)


        def _check(self):
            self._dirty = False


    class SequenceInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.SequenceInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_attributes = False
            self.attributes__enabled = True

        def _read(self):
            self.work = []
            for i in range(32):
                self.work.append(self._io.read_u2le())

            self.num_seq = self._io.read_u4le()
            self.ofs_seq = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.work)):
                pass

            _ = self.attributes
            if hasattr(self, '_m_attributes'):
                pass
                for i in range(len(self._m_attributes)):
                    pass
                    self._m_attributes[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.SequenceInfo, self)._write__seq(io)
            self._should_write_attributes = self.attributes__enabled
            for i in range(len(self.work)):
                pass
                self._io.write_u2le(self.work[i])

            self._io.write_u4le(self.num_seq)
            self._io.write_u4le(self.ofs_seq)


        def _check(self):
            if len(self.work) != 32:
                raise kaitaistruct.ConsistencyError(u"work", 32, len(self.work))
            for i in range(len(self.work)):
                pass

            if self.attributes__enabled:
                pass
                if len(self._m_attributes) != self.num_seq:
                    raise kaitaistruct.ConsistencyError(u"attributes", self.num_seq, len(self._m_attributes))
                for i in range(len(self._m_attributes)):
                    pass
                    if self._m_attributes[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"attributes", self._root, self._m_attributes[i]._root)
                    if self._m_attributes[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"attributes", self, self._m_attributes[i]._parent)


            self._dirty = False

        @property
        def attributes(self):
            if self._should_write_attributes:
                self._write_attributes()
            if hasattr(self, '_m_attributes'):
                return self._m_attributes

            if not self.attributes__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            self._m_attributes = []
            for i in range(self.num_seq):
                _t__m_attributes = Lmt.SeqInfoAttr(self._io, self, self._root)
                try:
                    _t__m_attributes._read()
                finally:
                    self._m_attributes.append(_t__m_attributes)

            self._io.seek(_pos)
            return getattr(self, '_m_attributes', None)

        @attributes.setter
        def attributes(self, v):
            self._dirty = True
            self._m_attributes = v

        def _write_attributes(self):
            self._should_write_attributes = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_seq)
            for i in range(len(self._m_attributes)):
                pass
                self._m_attributes[i]._write__seq(self._io)

            self._io.seek(_pos)


    class Track51(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Track51, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_data = False
            self.data__enabled = True

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

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.reference_data)):
                pass

            _ = self.data
            if hasattr(self, '_m_data'):
                pass



        def _write__seq(self, io=None):
            super(Lmt.Track51, self)._write__seq(io)
            self._should_write_data = self.data__enabled
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
            if len(self.reference_data) != 4:
                raise kaitaistruct.ConsistencyError(u"reference_data", 4, len(self.reference_data))
            for i in range(len(self.reference_data)):
                pass

            if self.data__enabled:
                pass
                if len(self._m_data) != self.len_data:
                    raise kaitaistruct.ConsistencyError(u"data", self.len_data, len(self._m_data))

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
            self._io.seek(self.ofs_data)
            self._m_data = self._io.read_bytes(self.len_data)
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._dirty = True
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._io.write_bytes(self._m_data)
            self._io.seek(_pos)


    class Track67(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Track67, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_bounds = False
            self.bounds__enabled = True
            self._should_write_data = False
            self.data__enabled = True

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
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.reference_data)):
                pass

            _ = self.bounds
            if hasattr(self, '_m_bounds'):
                pass
                self._m_bounds._fetch_instances()

            _ = self.data
            if hasattr(self, '_m_data'):
                pass



        def _write__seq(self, io=None):
            super(Lmt.Track67, self)._write__seq(io)
            self._should_write_bounds = self.bounds__enabled
            self._should_write_data = self.data__enabled
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
            if len(self.reference_data) != 4:
                raise kaitaistruct.ConsistencyError(u"reference_data", 4, len(self.reference_data))
            for i in range(len(self.reference_data)):
                pass

            if self.bounds__enabled:
                pass
                if self.is_used:
                    pass
                    if self._m_bounds._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"bounds", self._root, self._m_bounds._root)
                    if self._m_bounds._parent != self:
                        raise kaitaistruct.ConsistencyError(u"bounds", self, self._m_bounds._parent)


            if self.data__enabled:
                pass
                if len(self._m_data) != self.len_data:
                    raise kaitaistruct.ConsistencyError(u"data", self.len_data, len(self._m_data))

            self._dirty = False

        @property
        def bounds(self):
            if self._should_write_bounds:
                self._write_bounds()
            if hasattr(self, '_m_bounds'):
                return self._m_bounds

            if not self.bounds__enabled:
                return None

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
            self._dirty = True
            self._m_bounds = v

        def _write_bounds(self):
            self._should_write_bounds = False
            if self.is_used:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bounds)
                self._m_bounds._write__seq(self._io)
                self._io.seek(_pos)


        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            if not self.data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_data = self._io.read_bytes(self.len_data)
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._dirty = True
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._io.write_bytes(self._m_data)
            self._io.seek(_pos)

        @property
        def is_used(self):
            if hasattr(self, '_m_is_used'):
                return self._m_is_used

            self._m_is_used = self.ofs_bounds != 0
            return getattr(self, '_m_is_used', None)

        def _invalidate_is_used(self):
            del self._m_is_used

    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Vec3, self).__init__(_io)
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
            super(Lmt.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    class Vec3Frame12(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Vec3Frame12, self).__init__(_io)
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
            super(Lmt.Vec3Frame12, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 12
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec3Frame16(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Vec3Frame16, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.duration = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Vec3Frame16, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_u4le(self.duration)


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
            super(Lmt.Vec4, self).__init__(_io)
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
            super(Lmt.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    class XwQuat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.XwQuat, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(14)
            self.w = self._io.read_bits_int_le(14)
            self.duration = self._io.read_bits_int_le(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.XwQuat, self)._write__seq(io)
            self._io.write_bits_int_le(14, self.x)
            self._io.write_bits_int_le(14, self.w)
            self._io.write_bits_int_le(4, self.duration)


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

    class YwQuat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.YwQuat, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.y = self._io.read_bits_int_le(14)
            self.w = self._io.read_bits_int_le(14)
            self.duration = self._io.read_bits_int_le(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.YwQuat, self)._write__seq(io)
            self._io.write_bits_int_le(14, self.y)
            self._io.write_bits_int_le(14, self.w)
            self._io.write_bits_int_le(4, self.duration)


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

    class ZwQuat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.ZwQuat, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.z = self._io.read_bits_int_le(14)
            self.w = self._io.read_bits_int_le(14)
            self.duration = self._io.read_bits_int_le(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.ZwQuat, self)._write__seq(io)
            self._io.write_bits_int_le(14, self.z)
            self._io.write_bits_int_le(14, self.w)
            self._io.write_bits_int_le(4, self.duration)


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


