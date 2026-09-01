# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lmt(ReadWriteKaitaiStruct):
    def __init__(self, app_id, _io=None, _parent=None, _root=None):
        super(Lmt, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self.app_id = app_id

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

    class Atk(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Atk, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.duration = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Atk, self)._write__seq(io)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.duration)


        def _check(self):
            self._dirty = False


    class Atk2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.Atk2, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Lmt.Atk2, self)._write__seq(io)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.unk_01)


        def _check(self):
            self._dirty = False


    class BlockHeader51(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.BlockHeader51, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_atk_buff = False
            self.atk_buff__enabled = True
            self._should_write_atk_buff2 = False
            self.atk_buff2__enabled = True
            self._should_write_tracks = False
            self.tracks__enabled = True

        def _read(self):
            self.ofs_frame = self._io.read_u4le()
            self.num_tracks = self._io.read_u4le()
            self.num_frames = self._io.read_u4le()
            self.unk_01 = []
            for i in range(9):
                self.unk_01.append(self._io.read_f4le())

            self.unk_02 = []
            for i in range(16):
                self.unk_02.append(self._io.read_u4le())

            self.count_01 = self._io.read_u4le()
            self.ofs_buffer_01 = self._io.read_u4le()
            self.sfx = []
            for i in range(32):
                self.sfx.append(self._io.read_u2le())

            self.count_02 = self._io.read_u4le()
            self.ofs_buffer_02 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_01)):
                pass

            for i in range(len(self.unk_02)):
                pass

            for i in range(len(self.sfx)):
                pass

            _ = self.atk_buff
            if hasattr(self, '_m_atk_buff'):
                pass
                for i in range(len(self._m_atk_buff)):
                    pass
                    self._m_atk_buff[i]._fetch_instances()


            _ = self.atk_buff2
            if hasattr(self, '_m_atk_buff2'):
                pass
                for i in range(len(self._m_atk_buff2)):
                    pass
                    self._m_atk_buff2[i]._fetch_instances()


            _ = self.tracks
            if hasattr(self, '_m_tracks'):
                pass
                for i in range(len(self._m_tracks)):
                    pass
                    self._m_tracks[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.BlockHeader51, self)._write__seq(io)
            self._should_write_atk_buff = self.atk_buff__enabled
            self._should_write_atk_buff2 = self.atk_buff2__enabled
            self._should_write_tracks = self.tracks__enabled
            self._io.write_u4le(self.ofs_frame)
            self._io.write_u4le(self.num_tracks)
            self._io.write_u4le(self.num_frames)
            for i in range(len(self.unk_01)):
                pass
                self._io.write_f4le(self.unk_01[i])

            for i in range(len(self.unk_02)):
                pass
                self._io.write_u4le(self.unk_02[i])

            self._io.write_u4le(self.count_01)
            self._io.write_u4le(self.ofs_buffer_01)
            for i in range(len(self.sfx)):
                pass
                self._io.write_u2le(self.sfx[i])

            self._io.write_u4le(self.count_02)
            self._io.write_u4le(self.ofs_buffer_02)


        def _check(self):
            if len(self.unk_01) != 9:
                raise kaitaistruct.ConsistencyError(u"unk_01", 9, len(self.unk_01))
            for i in range(len(self.unk_01)):
                pass

            if len(self.unk_02) != 16:
                raise kaitaistruct.ConsistencyError(u"unk_02", 16, len(self.unk_02))
            for i in range(len(self.unk_02)):
                pass

            if len(self.sfx) != 32:
                raise kaitaistruct.ConsistencyError(u"sfx", 32, len(self.sfx))
            for i in range(len(self.sfx)):
                pass

            if self.atk_buff__enabled:
                pass
                if len(self._m_atk_buff) != self.count_01:
                    raise kaitaistruct.ConsistencyError(u"atk_buff", self.count_01, len(self._m_atk_buff))
                for i in range(len(self._m_atk_buff)):
                    pass
                    if self._m_atk_buff[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"atk_buff", self._root, self._m_atk_buff[i]._root)
                    if self._m_atk_buff[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"atk_buff", self, self._m_atk_buff[i]._parent)


            if self.atk_buff2__enabled:
                pass
                if len(self._m_atk_buff2) != self.count_02:
                    raise kaitaistruct.ConsistencyError(u"atk_buff2", self.count_02, len(self._m_atk_buff2))
                for i in range(len(self._m_atk_buff2)):
                    pass
                    if self._m_atk_buff2[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"atk_buff2", self._root, self._m_atk_buff2[i]._root)
                    if self._m_atk_buff2[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"atk_buff2", self, self._m_atk_buff2[i]._parent)


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
        def atk_buff(self):
            if self._should_write_atk_buff:
                self._write_atk_buff()
            if hasattr(self, '_m_atk_buff'):
                return self._m_atk_buff

            if not self.atk_buff__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_01)
            self._m_atk_buff = []
            for i in range(self.count_01):
                _t__m_atk_buff = Lmt.Atk(self._io, self, self._root)
                try:
                    _t__m_atk_buff._read()
                finally:
                    self._m_atk_buff.append(_t__m_atk_buff)

            self._io.seek(_pos)
            return getattr(self, '_m_atk_buff', None)

        @atk_buff.setter
        def atk_buff(self, v):
            self._dirty = True
            self._m_atk_buff = v

        def _write_atk_buff(self):
            self._should_write_atk_buff = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_01)
            for i in range(len(self._m_atk_buff)):
                pass
                self._m_atk_buff[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def atk_buff2(self):
            if self._should_write_atk_buff2:
                self._write_atk_buff2()
            if hasattr(self, '_m_atk_buff2'):
                return self._m_atk_buff2

            if not self.atk_buff2__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_02)
            self._m_atk_buff2 = []
            for i in range(self.count_02):
                _t__m_atk_buff2 = Lmt.Atk2(self._io, self, self._root)
                try:
                    _t__m_atk_buff2._read()
                finally:
                    self._m_atk_buff2.append(_t__m_atk_buff2)

            self._io.seek(_pos)
            return getattr(self, '_m_atk_buff2', None)

        @atk_buff2.setter
        def atk_buff2(self, v):
            self._dirty = True
            self._m_atk_buff2 = v

        def _write_atk_buff2(self):
            self._should_write_atk_buff2 = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_02)
            for i in range(len(self._m_atk_buff2)):
                pass
                self._m_atk_buff2[i]._write__seq(self._io)

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
            self._should_write_tracks = False
            self.tracks__enabled = True

        def _read(self):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.ofs_frame = self._io.read_u4le()
            elif _on == True:
                pass
                self.ofs_frame = self._io.read_u8le()
            else:
                pass
                self.ofs_frame = self._io.read_u4le()
            self.num_tracks = self._io.read_u4le()
            self.num_frames = self._io.read_u4le()
            self.loop_frame = self._io.read_u4le()
            if self._root.use_64bit_ofs:
                pass
                self.unk_01 = self._io.read_bytes(12)

            self.unk_floats = []
            for i in range(8):
                self.unk_floats.append(self._io.read_f4le())

            self.unk_00 = self._io.read_u4le()
            if self._root.use_64bit_ofs:
                pass
                self.unk_02 = self._io.read_bytes(4)

            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.ofs_buffer_1 = self._io.read_u4le()
            elif _on == True:
                pass
                self.ofs_buffer_1 = self._io.read_u8le()
            else:
                pass
                self.ofs_buffer_1 = self._io.read_u4le()
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.ofs_buffer_2 = self._io.read_u4le()
            elif _on == True:
                pass
                self.ofs_buffer_2 = self._io.read_u8le()
            else:
                pass
                self.ofs_buffer_2 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            if self._root.use_64bit_ofs:
                pass
                self.unk_04 = self._io.read_f4le()

            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if self._root.use_64bit_ofs:
                pass

            for i in range(len(self.unk_floats)):
                pass

            if self._root.use_64bit_ofs:
                pass

            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if self._root.use_64bit_ofs:
                pass

            _ = self.tracks
            if hasattr(self, '_m_tracks'):
                pass
                for i in range(len(self._m_tracks)):
                    pass
                    self._m_tracks[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Lmt.BlockHeader67, self)._write__seq(io)
            self._should_write_tracks = self.tracks__enabled
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.ofs_frame)
            elif _on == True:
                pass
                self._io.write_u8le(self.ofs_frame)
            else:
                pass
                self._io.write_u4le(self.ofs_frame)
            self._io.write_u4le(self.num_tracks)
            self._io.write_u4le(self.num_frames)
            self._io.write_u4le(self.loop_frame)
            if self._root.use_64bit_ofs:
                pass
                self._io.write_bytes(self.unk_01)

            for i in range(len(self.unk_floats)):
                pass
                self._io.write_f4le(self.unk_floats[i])

            self._io.write_u4le(self.unk_00)
            if self._root.use_64bit_ofs:
                pass
                self._io.write_bytes(self.unk_02)

            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.ofs_buffer_1)
            elif _on == True:
                pass
                self._io.write_u8le(self.ofs_buffer_1)
            else:
                pass
                self._io.write_u4le(self.ofs_buffer_1)
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.ofs_buffer_2)
            elif _on == True:
                pass
                self._io.write_u8le(self.ofs_buffer_2)
            else:
                pass
                self._io.write_u4le(self.ofs_buffer_2)
            self._io.write_u4le(self.unk_03)
            if self._root.use_64bit_ofs:
                pass
                self._io.write_f4le(self.unk_04)



        def _check(self):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if self._root.use_64bit_ofs:
                pass
                if len(self.unk_01) != 12:
                    raise kaitaistruct.ConsistencyError(u"unk_01", 12, len(self.unk_01))

            if len(self.unk_floats) != 8:
                raise kaitaistruct.ConsistencyError(u"unk_floats", 8, len(self.unk_floats))
            for i in range(len(self.unk_floats)):
                pass

            if self._root.use_64bit_ofs:
                pass
                if len(self.unk_02) != 4:
                    raise kaitaistruct.ConsistencyError(u"unk_02", 4, len(self.unk_02))

            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if self._root.use_64bit_ofs:
                pass

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
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.offset = self._io.read_u4le()
            elif _on == True:
                pass
                self.offset = self._io.read_u8le()
            else:
                pass
                self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
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
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.offset)
            elif _on == True:
                pass
                self._io.write_u8le(self.offset)
            else:
                pass
                self._io.write_u4le(self.offset)


        def _check(self):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if self.block_header__enabled:
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
        def lmt_ver(self):
            if hasattr(self, '_m_lmt_ver'):
                return self._m_lmt_ver

            self._m_lmt_ver = self._parent.version
            return getattr(self, '_m_lmt_ver', None)

        def _invalidate_lmt_ver(self):
            del self._m_lmt_ver

    class FloatBuffer(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.FloatBuffer, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = []
            for i in range(8):
                self.unk_00.append(self._io.read_f4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_00)):
                pass



        def _write__seq(self, io=None):
            super(Lmt.FloatBuffer, self)._write__seq(io)
            for i in range(len(self.unk_00)):
                pass
                self._io.write_f4le(self.unk_00[i])



        def _check(self):
            if len(self.unk_00) != 8:
                raise kaitaistruct.ConsistencyError(u"unk_00", 8, len(self.unk_00))
            for i in range(len(self.unk_00)):
                pass

            self._dirty = False


    class OfsFloatBuff(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Lmt.OfsFloatBuff, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_body = False
            self.body__enabled = True

        def _read(self):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.ofs_buffer = self._io.read_u4le()
            elif _on == True:
                pass
                self.ofs_buffer = self._io.read_u8le()
            else:
                pass
                self.ofs_buffer = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            _ = self.body
            if hasattr(self, '_m_body'):
                pass
                self._m_body._fetch_instances()



        def _write__seq(self, io=None):
            super(Lmt.OfsFloatBuff, self)._write__seq(io)
            self._should_write_body = self.body__enabled
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.ofs_buffer)
            elif _on == True:
                pass
                self._io.write_u8le(self.ofs_buffer)
            else:
                pass
                self._io.write_u4le(self.ofs_buffer)


        def _check(self):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if self.body__enabled:
                pass
                if self.is_exist != 0:
                    pass
                    if self._m_body._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"body", self._root, self._m_body._root)
                    if self._m_body._parent != self:
                        raise kaitaistruct.ConsistencyError(u"body", self, self._m_body._parent)


            self._dirty = False

        @property
        def body(self):
            if self._should_write_body:
                self._write_body()
            if hasattr(self, '_m_body'):
                return self._m_body

            if not self.body__enabled:
                return None

            if self.is_exist != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_buffer)
                self._m_body = Lmt.FloatBuffer(self._io, self, self._root)
                self._m_body._read()
                self._io.seek(_pos)

            return getattr(self, '_m_body', None)

        @body.setter
        def body(self, v):
            self._dirty = True
            self._m_body = v

        def _write_body(self):
            self._should_write_body = False
            if self.is_exist != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_buffer)
                self._m_body._write__seq(self._io)
                self._io.seek(_pos)


        @property
        def is_exist(self):
            if hasattr(self, '_m_is_exist'):
                return self._m_is_exist

            self._m_is_exist = self.ofs_buffer
            return getattr(self, '_m_is_exist', None)

        def _invalidate_is_exist(self):
            del self._m_is_exist

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
            self.unk_01 = self._io.read_f4le()
            self.len_data = self._io.read_u4le()
            self.ofs_data = self._io.read_u4le()
            self.unk_reference_data = []
            for i in range(4):
                self.unk_reference_data.append(self._io.read_f4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_reference_data)):
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
            self._io.write_f4le(self.unk_01)
            self._io.write_u4le(self.len_data)
            self._io.write_u4le(self.ofs_data)
            for i in range(len(self.unk_reference_data)):
                pass
                self._io.write_f4le(self.unk_reference_data[i])



        def _check(self):
            if len(self.unk_reference_data) != 4:
                raise kaitaistruct.ConsistencyError(u"unk_reference_data", 4, len(self.unk_reference_data))
            for i in range(len(self.unk_reference_data)):
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
            self._should_write_data = False
            self.data__enabled = True

        def _read(self):
            self.buffer_type = self._io.read_u1()
            self.usage = self._io.read_u1()
            self.joint_type = self._io.read_u1()
            self.bone_index = self._io.read_u1()
            self.weight = self._io.read_f4le()
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.len_data = self._io.read_u4le()
            elif _on == True:
                pass
                self.len_data = self._io.read_u8le()
            else:
                pass
                self.len_data = self._io.read_u4le()
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self.ofs_data = self._io.read_u4le()
            elif _on == True:
                pass
                self.ofs_data = self._io.read_u8le()
            else:
                pass
                self.ofs_data = self._io.read_u4le()
            self.unk_reference_data = []
            for i in range(4):
                self.unk_reference_data.append(self._io.read_f4le())

            self.ofs_floats = Lmt.OfsFloatBuff(self._io, self, self._root)
            self.ofs_floats._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            for i in range(len(self.unk_reference_data)):
                pass

            self.ofs_floats._fetch_instances()
            _ = self.data
            if hasattr(self, '_m_data'):
                pass



        def _write__seq(self, io=None):
            super(Lmt.Track67, self)._write__seq(io)
            self._should_write_data = self.data__enabled
            self._io.write_u1(self.buffer_type)
            self._io.write_u1(self.usage)
            self._io.write_u1(self.joint_type)
            self._io.write_u1(self.bone_index)
            self._io.write_f4le(self.weight)
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.len_data)
            elif _on == True:
                pass
                self._io.write_u8le(self.len_data)
            else:
                pass
                self._io.write_u4le(self.len_data)
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
                self._io.write_u4le(self.ofs_data)
            elif _on == True:
                pass
                self._io.write_u8le(self.ofs_data)
            else:
                pass
                self._io.write_u4le(self.ofs_data)
            for i in range(len(self.unk_reference_data)):
                pass
                self._io.write_f4le(self.unk_reference_data[i])

            self.ofs_floats._write__seq(self._io)


        def _check(self):
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            _on = self._root.use_64bit_ofs
            if _on == False:
                pass
            elif _on == True:
                pass
            else:
                pass
            if len(self.unk_reference_data) != 4:
                raise kaitaistruct.ConsistencyError(u"unk_reference_data", 4, len(self.unk_reference_data))
            for i in range(len(self.unk_reference_data)):
                pass

            if self.ofs_floats._root != self._root:
                raise kaitaistruct.ConsistencyError(u"ofs_floats", self._root, self.ofs_floats._root)
            if self.ofs_floats._parent != self:
                raise kaitaistruct.ConsistencyError(u"ofs_floats", self, self.ofs_floats._parent)
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


    @property
    def use_64bit_ofs(self):
        if hasattr(self, '_m_use_64bit_ofs'):
            return self._m_use_64bit_ofs

        self._m_use_64bit_ofs = self._root.app_id == u"umvc3"
        return getattr(self, '_m_use_64bit_ofs', None)

    def _invalidate_use_64bit_ofs(self):
        del self._m_use_64bit_ofs

