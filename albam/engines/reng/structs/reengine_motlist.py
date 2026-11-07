# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineMotlist(ReadWriteKaitaiStruct):
    """One spec for both files, because a .motlist embeds whole .mot files: the
    top level reads version + magic and hands the file to `motlist` ("mlst")
    or `mot` ("mot "). Every offset inside a mot is relative to the mot's own
    start, so each one is parsed in a substream that begins there.
    
    Written against Resident Evil 2 (ray-tracing build): motlist 524, mot 492
    (the numeric suffixes of the file names). The version switches below are
    the ones alphaZomega's Noesis plugin (fmt_RE_MESH.py) and the community
    010 template (RE_Engine_motlist.bt) make; versions other than 524/492 are
    untested here.
    
    Sources: https://github.com/alphazolam/fmt_RE_MESH-Noesis-Plugin
    (fmt_RE_MESH.py, motFile/motlistFile) and
    https://github.com/kagenocookie/RE-Engine-010-Templates (RE_Engine_motlist.bt).
    """

    class KeyEncoding(IntEnum):
        translation_full = 0
        translation_5bit = 131072
        translation_x_16bit = 135168
        translation_y_16bit = 139264
        translation_z_16bit = 143360
        translation_xyz_16bit = 147456
        translation_10bit = 262144
        translation_x = 266240
        translation_y = 270336
        translation_z = 274432
        translation_xyz = 278528
        translation_21bit = 524288
        rotation_full = 1048576
        rotation_5bit = 1179648
        rotation_x_16bit = 1183744
        rotation_y_16bit = 1187840
        rotation_z_16bit = 1191936
        rotation_8bit = 1245184
        rotation_10bit = 1310720
        rotation_x = 1314816
        rotation_y = 1318912
        rotation_z = 1323008
        rotation_13bit = 1376256
        rotation_16bit = 1441792
        rotation_18bit = 1507328
        rotation_21bit = 1572864
        rotation_3component = 1769472
        rotation_3component_b = 1835008
    def __init__(self, _io=None, _parent=None, _root=None):
        super(ReengineMotlist, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_mot = False
        self.mot__enabled = True
        self._should_write_motlist = False
        self.motlist__enabled = True

    def _read(self):
        self.version = self._io.read_u4le()
        self.magic = (self._io.read_bytes(4)).decode(u"ASCII")
        self._dirty = False


    def _fetch_instances(self):
        pass
        _ = self.mot
        if hasattr(self, '_m_mot'):
            pass
            self._m_mot._fetch_instances()

        _ = self.motlist
        if hasattr(self, '_m_motlist'):
            pass
            self._m_motlist._fetch_instances()



    def _write__seq(self, io=None):
        super(ReengineMotlist, self)._write__seq(io)
        self._should_write_mot = self.mot__enabled
        self._should_write_motlist = self.motlist__enabled
        self._io.write_u4le(self.version)
        self._io.write_bytes((self.magic).encode(u"ASCII"))


    def _check(self):
        if len((self.magic).encode(u"ASCII")) != 4:
            raise kaitaistruct.ConsistencyError(u"magic", 4, len((self.magic).encode(u"ASCII")))
        if self.mot__enabled:
            pass
            if self.magic == u"mot ":
                pass
                if self._m_mot._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"mot", self._root, self._m_mot._root)
                if self._m_mot._parent != self:
                    raise kaitaistruct.ConsistencyError(u"mot", self, self._m_mot._parent)


        if self.motlist__enabled:
            pass
            if self.magic == u"mlst":
                pass
                if self._m_motlist._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"motlist", self._root, self._m_motlist._root)
                if self._m_motlist._parent != self:
                    raise kaitaistruct.ConsistencyError(u"motlist", self, self._m_motlist._parent)


        self._dirty = False

    class Bone(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Bone, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_name_raw = False
            self.name_raw__enabled = True

        def _read(self):
            self.ofs_name = self._io.read_u8le()
            self.ofs_parent = self._io.read_u8le()
            self.ofs_child = self._io.read_u8le()
            self.ofs_next_sibling = self._io.read_u8le()
            self.translation = []
            for i in range(4):
                self.translation.append(self._io.read_f4le())

            self.rotation = []
            for i in range(4):
                self.rotation.append(self._io.read_f4le())

            self.index = self._io.read_u4le()
            self.name_hash = self._io.read_u4le()
            self.reserved = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.translation)):
                pass

            for i in range(len(self.rotation)):
                pass

            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.name_raw
            if hasattr(self, '_m_name_raw'):
                pass
                for i in range(len(self._m_name_raw)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMotlist.Bone, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._should_write_name_raw = self.name_raw__enabled
            self._io.write_u8le(self.ofs_name)
            self._io.write_u8le(self.ofs_parent)
            self._io.write_u8le(self.ofs_child)
            self._io.write_u8le(self.ofs_next_sibling)
            for i in range(len(self.translation)):
                pass
                self._io.write_f4le(self.translation[i])

            for i in range(len(self.rotation)):
                pass
                self._io.write_f4le(self.rotation[i])

            self._io.write_u4le(self.index)
            self._io.write_u4le(self.name_hash)
            self._io.write_u8le(self.reserved)


        def _check(self):
            if len(self.translation) != 4:
                raise kaitaistruct.ConsistencyError(u"translation", 4, len(self.translation))
            for i in range(len(self.translation)):
                pass

            if len(self.rotation) != 4:
                raise kaitaistruct.ConsistencyError(u"rotation", 4, len(self.rotation))
            for i in range(len(self.rotation)):
                pass

            if self.name__enabled:
                pass

            if self.name_raw__enabled:
                pass
                if len(self._m_name_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"name_raw", 0, len(self._m_name_raw))
                for i in range(len(self._m_name_raw)):
                    pass
                    _ = self._m_name_raw[i]
                    if (_ == 0) != (i == len(self._m_name_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"name_raw", i == len(self._m_name_raw) - 1, _ == 0)


            self._dirty = False

        @property
        def idx_parent(self):
            if hasattr(self, '_m_idx_parent'):
                return self._m_idx_parent

            self._m_idx_parent = (-1 if self.ofs_parent == 0 else (self.ofs_parent - self._parent.ofs_bones) // 80)
            return getattr(self, '_m_idx_parent', None)

        def _invalidate_idx_parent(self):
            del self._m_idx_parent
        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name = (self._io.read_bytes(len(self.name_raw) * 2 - 2)).decode(u"UTF-16LE")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            if len((self._m_name).encode(u"UTF-16LE")) != len(self.name_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"name", len(self.name_raw) * 2 - 2, len((self._m_name).encode(u"UTF-16LE")))
            self._io.write_bytes((self._m_name).encode(u"UTF-16LE"))
            self._io.seek(_pos)

        @property
        def name_raw(self):
            if self._should_write_name_raw:
                self._write_name_raw()
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            if not self.name_raw__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_name_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_name_raw', None)

        @name_raw.setter
        def name_raw(self, v):
            self._dirty = True
            self._m_name_raw = v

        def _write_name_raw(self):
            self._should_write_name_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            for i in range(len(self._m_name_raw)):
                pass
                self._io.write_u2le(self._m_name_raw[i])

            self._io.seek(_pos)


    class BoneClipHeader(ReadWriteKaitaiStruct):
        def __init__(self, version, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.BoneClipHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.version = version
            self._should_write_tracks = False
            self.tracks__enabled = True

        def _read(self):
            self.bone_index = self._io.read_u2le()
            self.track_flags = self._io.read_u1()
            self.unk_flags = self._io.read_u1()
            self.bone_hash = self._io.read_u4le()
            if self.version == 65:
                pass
                self.unk_float_00 = self._io.read_f4le()

            if self.version == 65:
                pass
                self.reserved_00 = self._io.read_u4le()

            _on = self.version
            if _on == 43:
                pass
                self.ofs_tracks = self._io.read_u8le()
            elif _on == 65:
                pass
                self.ofs_tracks = self._io.read_u8le()
            else:
                pass
                self.ofs_tracks = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.version == 65:
                pass

            if self.version == 65:
                pass

            _on = self.version
            if _on == 43:
                pass
            elif _on == 65:
                pass
            else:
                pass
            _ = self.tracks
            if hasattr(self, '_m_tracks'):
                pass
                self._m_tracks._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMotlist.BoneClipHeader, self)._write__seq(io)
            self._should_write_tracks = self.tracks__enabled
            self._io.write_u2le(self.bone_index)
            self._io.write_u1(self.track_flags)
            self._io.write_u1(self.unk_flags)
            self._io.write_u4le(self.bone_hash)
            if self.version == 65:
                pass
                self._io.write_f4le(self.unk_float_00)

            if self.version == 65:
                pass
                self._io.write_u4le(self.reserved_00)

            _on = self.version
            if _on == 43:
                pass
                self._io.write_u8le(self.ofs_tracks)
            elif _on == 65:
                pass
                self._io.write_u8le(self.ofs_tracks)
            else:
                pass
                self._io.write_u4le(self.ofs_tracks)


        def _check(self):
            if self.version == 65:
                pass

            if self.version == 65:
                pass

            _on = self.version
            if _on == 43:
                pass
            elif _on == 65:
                pass
            else:
                pass
            if self.tracks__enabled:
                pass
                if self._m_tracks._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"tracks", self._root, self._m_tracks._root)
                if self._m_tracks._parent != self:
                    raise kaitaistruct.ConsistencyError(u"tracks", self, self._m_tracks._parent)
                if self._m_tracks.version != self.version:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.version, self._m_tracks.version)
                if self._m_tracks.track_flags != self.track_flags:
                    raise kaitaistruct.ConsistencyError(u"tracks", self.track_flags, self._m_tracks.track_flags)

            self._dirty = False

        @property
        def has_rotation(self):
            if hasattr(self, '_m_has_rotation'):
                return self._m_has_rotation

            self._m_has_rotation = self.track_flags & 2 != 0
            return getattr(self, '_m_has_rotation', None)

        def _invalidate_has_rotation(self):
            del self._m_has_rotation
        @property
        def has_scale(self):
            if hasattr(self, '_m_has_scale'):
                return self._m_has_scale

            self._m_has_scale = self.track_flags & 4 != 0
            return getattr(self, '_m_has_scale', None)

        def _invalidate_has_scale(self):
            del self._m_has_scale
        @property
        def has_translation(self):
            if hasattr(self, '_m_has_translation'):
                return self._m_has_translation

            self._m_has_translation = self.track_flags & 1 != 0
            return getattr(self, '_m_has_translation', None)

        def _invalidate_has_translation(self):
            del self._m_has_translation
        @property
        def tracks(self):
            if self._should_write_tracks:
                self._write_tracks()
            if hasattr(self, '_m_tracks'):
                return self._m_tracks

            if not self.tracks__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_tracks)
            self._m_tracks = ReengineMotlist.BoneTracks(self.version, self.track_flags, self._io, self, self._root)
            self._m_tracks._read()
            self._io.seek(_pos)
            return getattr(self, '_m_tracks', None)

        @tracks.setter
        def tracks(self, v):
            self._dirty = True
            self._m_tracks = v

        def _write_tracks(self):
            self._should_write_tracks = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_tracks)
            self._m_tracks._write__seq(self._io)
            self._io.seek(_pos)


    class BoneTracks(ReadWriteKaitaiStruct):
        def __init__(self, version, track_flags, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.BoneTracks, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.version = version
            self.track_flags = track_flags

        def _read(self):
            if self.track_flags & 1 != 0:
                pass
                self.translation = ReengineMotlist.Track(self.version, 0, self._io, self, self._root)
                self.translation._read()

            if self.track_flags & 2 != 0:
                pass
                self.rotation = ReengineMotlist.Track(self.version, 1, self._io, self, self._root)
                self.rotation._read()

            if self.track_flags & 4 != 0:
                pass
                self.scale = ReengineMotlist.Track(self.version, 2, self._io, self, self._root)
                self.scale._read()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.track_flags & 1 != 0:
                pass
                self.translation._fetch_instances()

            if self.track_flags & 2 != 0:
                pass
                self.rotation._fetch_instances()

            if self.track_flags & 4 != 0:
                pass
                self.scale._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMotlist.BoneTracks, self)._write__seq(io)
            if self.track_flags & 1 != 0:
                pass
                self.translation._write__seq(self._io)

            if self.track_flags & 2 != 0:
                pass
                self.rotation._write__seq(self._io)

            if self.track_flags & 4 != 0:
                pass
                self.scale._write__seq(self._io)



        def _check(self):
            if self.track_flags & 1 != 0:
                pass
                if self.translation._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"translation", self._root, self.translation._root)
                if self.translation._parent != self:
                    raise kaitaistruct.ConsistencyError(u"translation", self, self.translation._parent)
                if self.translation.version != self.version:
                    raise kaitaistruct.ConsistencyError(u"translation", self.version, self.translation.version)
                if self.translation.kind != 0:
                    raise kaitaistruct.ConsistencyError(u"translation", 0, self.translation.kind)

            if self.track_flags & 2 != 0:
                pass
                if self.rotation._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"rotation", self._root, self.rotation._root)
                if self.rotation._parent != self:
                    raise kaitaistruct.ConsistencyError(u"rotation", self, self.rotation._parent)
                if self.rotation.version != self.version:
                    raise kaitaistruct.ConsistencyError(u"rotation", self.version, self.rotation.version)
                if self.rotation.kind != 1:
                    raise kaitaistruct.ConsistencyError(u"rotation", 1, self.rotation.kind)

            if self.track_flags & 4 != 0:
                pass
                if self.scale._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"scale", self._root, self.scale._root)
                if self.scale._parent != self:
                    raise kaitaistruct.ConsistencyError(u"scale", self, self.scale._parent)
                if self.scale.version != self.version:
                    raise kaitaistruct.ConsistencyError(u"scale", self.version, self.scale.version)
                if self.scale.kind != 2:
                    raise kaitaistruct.ConsistencyError(u"scale", 2, self.scale.kind)

            self._dirty = False


    class BonesHeader(ReadWriteKaitaiStruct):
        """The motion's own copy of the skeleton (bind pose, local space)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.BonesHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_bones = False
            self.bones__enabled = True

        def _read(self):
            self.ofs_bones = self._io.read_u8le()
            self.num_bones = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.bones
            if hasattr(self, '_m_bones'):
                pass
                for i in range(len(self._m_bones)):
                    pass
                    self._m_bones[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(ReengineMotlist.BonesHeader, self)._write__seq(io)
            self._should_write_bones = self.bones__enabled
            self._io.write_u8le(self.ofs_bones)
            self._io.write_u8le(self.num_bones)


        def _check(self):
            if self.bones__enabled:
                pass
                if len(self._m_bones) != self.num_bones:
                    raise kaitaistruct.ConsistencyError(u"bones", self.num_bones, len(self._m_bones))
                for i in range(len(self._m_bones)):
                    pass
                    if self._m_bones[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"bones", self._root, self._m_bones[i]._root)
                    if self._m_bones[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"bones", self, self._m_bones[i]._parent)


            self._dirty = False

        @property
        def bones(self):
            if self._should_write_bones:
                self._write_bones()
            if hasattr(self, '_m_bones'):
                return self._m_bones

            if not self.bones__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_bones)
            self._m_bones = []
            for i in range(self.num_bones):
                _t__m_bones = ReengineMotlist.Bone(self._io, self, self._root)
                try:
                    _t__m_bones._read()
                finally:
                    self._m_bones.append(_t__m_bones)

            self._io.seek(_pos)
            return getattr(self, '_m_bones', None)

        @bones.setter
        def bones(self, v):
            self._dirty = True
            self._m_bones = v

        def _write_bones(self):
            self._should_write_bones = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_bones)
            for i in range(len(self._m_bones)):
                pass
                self._m_bones[i]._write__seq(self._io)

            self._io.seek(_pos)


    class F4Value(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.F4Value, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.value = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.F4Value, self)._write__seq(io)
            self._io.write_f4le(self.value)


        def _check(self):
            self._dirty = False


    class Mot(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Mot, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_bone_clip_headers = False
            self.bone_clip_headers__enabled = True
            self._should_write_bones_header = False
            self.bones_header__enabled = True
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_name_raw = False
            self.name_raw__enabled = True

        def _read(self):
            self.version = self._io.read_u4le()
            self.id_magic = self._io.read_bytes(4)
            if not self.id_magic == b"\x6D\x6F\x74\x20":
                raise kaitaistruct.ValidationNotEqualError(b"\x6D\x6F\x74\x20", self.id_magic, self._io, u"/types/mot/seq/1")
            self.unk_00 = self._io.read_u4le()
            self.size_mot = self._io.read_u4le()
            self.ofs_bones_header = self._io.read_u8le()
            self.ofs_bone_clip_headers = self._io.read_u8le()
            self.ofs_property_tracks = self._io.read_u8le()
            self.reserved_00 = self._io.read_u8le()
            self.ofs_clips = self._io.read_u8le()
            self.ofs_jmap = self._io.read_u8le()
            self.ofs_end_clips = self._io.read_u8le()
            if self.version >= 456:
                pass
                self.ofs_end_clip_frame_values = self._io.read_u8le()

            self.ofs_property_tree = self._io.read_u8le()
            self.ofs_name = self._io.read_u8le()
            self.num_frames = self._io.read_f4le()
            self.blending = self._io.read_f4le()
            self.unk_float_00 = self._io.read_f4le()
            self.unk_float_01 = self._io.read_f4le()
            self.num_bones = self._io.read_u2le()
            self.num_bone_clip_headers = self._io.read_u2le()
            self.num_clips = self._io.read_u1()
            self.num_end_clips = self._io.read_u1()
            if self.version >= 458:
                pass
                self.unk_01 = self._io.read_u2le()

            self.frame_rate = self._io.read_u2le()
            self.num_property_tracks = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.version >= 456:
                pass

            if self.version >= 458:
                pass

            _ = self.bone_clip_headers
            if hasattr(self, '_m_bone_clip_headers'):
                pass
                for i in range(len(self._m_bone_clip_headers)):
                    pass
                    self._m_bone_clip_headers[i]._fetch_instances()


            _ = self.bones_header
            if hasattr(self, '_m_bones_header'):
                pass
                self._m_bones_header._fetch_instances()

            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.name_raw
            if hasattr(self, '_m_name_raw'):
                pass
                for i in range(len(self._m_name_raw)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMotlist.Mot, self)._write__seq(io)
            self._should_write_bone_clip_headers = self.bone_clip_headers__enabled
            self._should_write_bones_header = self.bones_header__enabled
            self._should_write_name = self.name__enabled
            self._should_write_name_raw = self.name_raw__enabled
            self._io.write_u4le(self.version)
            self._io.write_bytes(self.id_magic)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.size_mot)
            self._io.write_u8le(self.ofs_bones_header)
            self._io.write_u8le(self.ofs_bone_clip_headers)
            self._io.write_u8le(self.ofs_property_tracks)
            self._io.write_u8le(self.reserved_00)
            self._io.write_u8le(self.ofs_clips)
            self._io.write_u8le(self.ofs_jmap)
            self._io.write_u8le(self.ofs_end_clips)
            if self.version >= 456:
                pass
                self._io.write_u8le(self.ofs_end_clip_frame_values)

            self._io.write_u8le(self.ofs_property_tree)
            self._io.write_u8le(self.ofs_name)
            self._io.write_f4le(self.num_frames)
            self._io.write_f4le(self.blending)
            self._io.write_f4le(self.unk_float_00)
            self._io.write_f4le(self.unk_float_01)
            self._io.write_u2le(self.num_bones)
            self._io.write_u2le(self.num_bone_clip_headers)
            self._io.write_u1(self.num_clips)
            self._io.write_u1(self.num_end_clips)
            if self.version >= 458:
                pass
                self._io.write_u2le(self.unk_01)

            self._io.write_u2le(self.frame_rate)
            self._io.write_u2le(self.num_property_tracks)
            self._io.write_u2le(self.unk_02)


        def _check(self):
            if len(self.id_magic) != 4:
                raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
            if not self.id_magic == b"\x6D\x6F\x74\x20":
                raise kaitaistruct.ValidationNotEqualError(b"\x6D\x6F\x74\x20", self.id_magic, None, u"/types/mot/seq/1")
            if self.version >= 456:
                pass

            if self.version >= 458:
                pass

            if self.bone_clip_headers__enabled:
                pass
                if len(self._m_bone_clip_headers) != self.num_bone_clip_headers:
                    raise kaitaistruct.ConsistencyError(u"bone_clip_headers", self.num_bone_clip_headers, len(self._m_bone_clip_headers))
                for i in range(len(self._m_bone_clip_headers)):
                    pass
                    if self._m_bone_clip_headers[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"bone_clip_headers", self._root, self._m_bone_clip_headers[i]._root)
                    if self._m_bone_clip_headers[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"bone_clip_headers", self, self._m_bone_clip_headers[i]._parent)
                    if self._m_bone_clip_headers[i].version != self.version:
                        raise kaitaistruct.ConsistencyError(u"bone_clip_headers", self.version, self._m_bone_clip_headers[i].version)


            if self.bones_header__enabled:
                pass
                if self.has_bones:
                    pass
                    if self._m_bones_header._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"bones_header", self._root, self._m_bones_header._root)
                    if self._m_bones_header._parent != self:
                        raise kaitaistruct.ConsistencyError(u"bones_header", self, self._m_bones_header._parent)


            if self.name__enabled:
                pass
                if self.ofs_name != 0:
                    pass


            if self.name_raw__enabled:
                pass
                if self.ofs_name != 0:
                    pass
                    if len(self._m_name_raw) == 0:
                        raise kaitaistruct.ConsistencyError(u"name_raw", 0, len(self._m_name_raw))
                    for i in range(len(self._m_name_raw)):
                        pass
                        _ = self._m_name_raw[i]
                        if (_ == 0) != (i == len(self._m_name_raw) - 1):
                            raise kaitaistruct.ConsistencyError(u"name_raw", i == len(self._m_name_raw) - 1, _ == 0)



            self._dirty = False

        @property
        def bone_clip_headers(self):
            if self._should_write_bone_clip_headers:
                self._write_bone_clip_headers()
            if hasattr(self, '_m_bone_clip_headers'):
                return self._m_bone_clip_headers

            if not self.bone_clip_headers__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_bone_clip_headers)
            self._m_bone_clip_headers = []
            for i in range(self.num_bone_clip_headers):
                _t__m_bone_clip_headers = ReengineMotlist.BoneClipHeader(self.version, self._io, self, self._root)
                try:
                    _t__m_bone_clip_headers._read()
                finally:
                    self._m_bone_clip_headers.append(_t__m_bone_clip_headers)

            self._io.seek(_pos)
            return getattr(self, '_m_bone_clip_headers', None)

        @bone_clip_headers.setter
        def bone_clip_headers(self, v):
            self._dirty = True
            self._m_bone_clip_headers = v

        def _write_bone_clip_headers(self):
            self._should_write_bone_clip_headers = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_bone_clip_headers)
            for i in range(len(self._m_bone_clip_headers)):
                pass
                self._m_bone_clip_headers[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def bones_header(self):
            if self._should_write_bones_header:
                self._write_bones_header()
            if hasattr(self, '_m_bones_header'):
                return self._m_bones_header

            if not self.bones_header__enabled:
                return None

            if self.has_bones:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bones_header)
                self._m_bones_header = ReengineMotlist.BonesHeader(self._io, self, self._root)
                self._m_bones_header._read()
                self._io.seek(_pos)

            return getattr(self, '_m_bones_header', None)

        @bones_header.setter
        def bones_header(self, v):
            self._dirty = True
            self._m_bones_header = v

        def _write_bones_header(self):
            self._should_write_bones_header = False
            if self.has_bones:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bones_header)
                self._m_bones_header._write__seq(self._io)
                self._io.seek(_pos)


        @property
        def has_bones(self):
            """In a motlist usually only the first mot carries the skeleton; the
            others point ofs_bones_header at (or past) their own end. Readers
            then reuse the bones of an earlier mot (Noesis: motlist.boneHeaders).
            """
            if hasattr(self, '_m_has_bones'):
                return self._m_has_bones

            self._m_has_bones =  ((self.ofs_bones_header != 0) and ( ((self.size_mot == 0) or (self.size_mot > self.ofs_bones_header)) )) 
            return getattr(self, '_m_has_bones', None)

        def _invalidate_has_bones(self):
            del self._m_has_bones
        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            if self.ofs_name != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_name)
                self._m_name = (self._io.read_bytes(len(self.name_raw) * 2 - 2)).decode(u"UTF-16LE")
                self._io.seek(_pos)

            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            if self.ofs_name != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_name)
                if len((self._m_name).encode(u"UTF-16LE")) != len(self.name_raw) * 2 - 2:
                    raise kaitaistruct.ConsistencyError(u"name", len(self.name_raw) * 2 - 2, len((self._m_name).encode(u"UTF-16LE")))
                self._io.write_bytes((self._m_name).encode(u"UTF-16LE"))
                self._io.seek(_pos)


        @property
        def name_raw(self):
            if self._should_write_name_raw:
                self._write_name_raw()
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            if not self.name_raw__enabled:
                return None

            if self.ofs_name != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_name)
                self._m_name_raw = []
                i = 0
                while True:
                    _ = self._io.read_u2le()
                    self._m_name_raw.append(_)
                    if _ == 0:
                        break
                    i += 1
                self._io.seek(_pos)

            return getattr(self, '_m_name_raw', None)

        @name_raw.setter
        def name_raw(self, v):
            self._dirty = True
            self._m_name_raw = v

        def _write_name_raw(self):
            self._should_write_name_raw = False
            if self.ofs_name != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_name)
                for i in range(len(self._m_name_raw)):
                    pass
                    self._io.write_u2le(self._m_name_raw[i])

                self._io.seek(_pos)



    class MotionId(ReadWriteKaitaiStruct):
        """72 bytes per entry for motlist >= 484 (Noesis motionIDsData [72, 8])."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.MotionId, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ofs_extra_clips = self._io.read_u8le()
            self.motion_id = self._io.read_u2le()
            self.switch = self._io.read_u2le()
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.unk_02 = []
            for i in range(3):
                self.unk_02.append(self._io.read_u1())

            self.num_extra_clips = self._io.read_u1()
            self.unk_03 = []
            for i in range(3):
                self.unk_03.append(self._io.read_u4le())

            self.reserved = self._io.read_bytes(36)
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_02)):
                pass

            for i in range(len(self.unk_03)):
                pass



        def _write__seq(self, io=None):
            super(ReengineMotlist.MotionId, self)._write__seq(io)
            self._io.write_u8le(self.ofs_extra_clips)
            self._io.write_u2le(self.motion_id)
            self._io.write_u2le(self.switch)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.unk_01)
            for i in range(len(self.unk_02)):
                pass
                self._io.write_u1(self.unk_02[i])

            self._io.write_u1(self.num_extra_clips)
            for i in range(len(self.unk_03)):
                pass
                self._io.write_u4le(self.unk_03[i])

            self._io.write_bytes(self.reserved)


        def _check(self):
            if len(self.unk_02) != 3:
                raise kaitaistruct.ConsistencyError(u"unk_02", 3, len(self.unk_02))
            for i in range(len(self.unk_02)):
                pass

            if len(self.unk_03) != 3:
                raise kaitaistruct.ConsistencyError(u"unk_03", 3, len(self.unk_03))
            for i in range(len(self.unk_03)):
                pass

            if len(self.reserved) != 36:
                raise kaitaistruct.ConsistencyError(u"reserved", 36, len(self.reserved))
            self._dirty = False


    class MotionPointer(ReadWriteKaitaiStruct):
        """Pointers can be 0 or repeat an earlier one; both readers skip those.
        What sits at the pointer is usually a mot; the 010 template also knows
        motion trees ("mtre"), camera motions ("mcam") and links (version 1).
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.MotionPointer, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_magic = False
            self.magic__enabled = True
            self._should_write_mot = False
            self.mot__enabled = True

        def _read(self):
            self.ofs_motion = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.magic
            if hasattr(self, '_m_magic'):
                pass

            _ = self.mot
            if hasattr(self, '_m_mot'):
                pass
                self._m_mot._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMotlist.MotionPointer, self)._write__seq(io)
            self._should_write_magic = self.magic__enabled
            self._should_write_mot = self.mot__enabled
            self._io.write_u8le(self.ofs_motion)


        def _check(self):
            if self.magic__enabled:
                pass
                if self.ofs_motion != 0:
                    pass
                    if len((self._m_magic).encode(u"ASCII")) != 4:
                        raise kaitaistruct.ConsistencyError(u"magic", 4, len((self._m_magic).encode(u"ASCII")))


            if self.mot__enabled:
                pass

            self._dirty = False

        @property
        def magic(self):
            if self._should_write_magic:
                self._write_magic()
            if hasattr(self, '_m_magic'):
                return self._m_magic

            if not self.magic__enabled:
                return None

            if self.ofs_motion != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_motion + 4)
                self._m_magic = (self._io.read_bytes(4)).decode(u"ASCII")
                self._io.seek(_pos)

            return getattr(self, '_m_magic', None)

        @magic.setter
        def magic(self, v):
            self._dirty = True
            self._m_magic = v

        def _write_magic(self):
            self._should_write_magic = False
            if self.ofs_motion != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_motion + 4)
                self._io.write_bytes((self._m_magic).encode(u"ASCII"))
                self._io.seek(_pos)


        @property
        def mot(self):
            if self._should_write_mot:
                self._write_mot()
            if hasattr(self, '_m_mot'):
                return self._m_mot

            if not self.mot__enabled:
                return None

            if  ((self.ofs_motion != 0) and (self.magic == u"mot ")) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_motion)
                self._raw__m_mot = self._io.read_bytes_full()
                _io__raw__m_mot = KaitaiStream(BytesIO(self._raw__m_mot))
                self._m_mot = ReengineMotlist.Mot(_io__raw__m_mot, self, self._root)
                self._m_mot._read()
                self._io.seek(_pos)

            return getattr(self, '_m_mot', None)

        @mot.setter
        def mot(self, v):
            self._dirty = True
            self._m_mot = v

        def _write_mot(self):
            self._should_write_mot = False
            if  ((self.ofs_motion != 0) and (self.magic == u"mot ")) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_motion)
                if self._m_mot._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"mot", self._root, self._m_mot._root)
                if self._m_mot._parent != self:
                    raise kaitaistruct.ConsistencyError(u"mot", self, self._m_mot._parent)
                _io__raw__m_mot = KaitaiStream(BytesIO(bytearray(self._io.size() - self._io.pos())))
                self._io.add_child_stream(_io__raw__m_mot)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + (self._io.size() - self._io.pos()))
                def handler(parent, _io__raw__m_mot=_io__raw__m_mot):
                    self._raw__m_mot = _io__raw__m_mot.to_byte_array()
                    parent.write_bytes(self._raw__m_mot)
                    if not parent.is_eof():
                        raise kaitaistruct.ConsistencyError(u"raw(mot)", 0, parent.size() - parent.pos())
                _io__raw__m_mot.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self._m_mot._write__seq(_io__raw__m_mot)
                self._io.seek(_pos)



    class Motlist(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Motlist, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_motion_ids = False
            self.motion_ids__enabled = True
            self._should_write_motions = False
            self.motions__enabled = True
            self._should_write_name = False
            self.name__enabled = True
            self._should_write_name_raw = False
            self.name_raw__enabled = True

        def _read(self):
            self.version = self._io.read_u4le()
            self.id_magic = self._io.read_bytes(4)
            if not self.id_magic == b"\x6D\x6C\x73\x74":
                raise kaitaistruct.ValidationNotEqualError(b"\x6D\x6C\x73\x74", self.id_magic, self._io, u"/types/motlist/seq/1")
            self.reserved_00 = self._io.read_u8le()
            self.ofs_motions = self._io.read_u8le()
            self.ofs_motion_ids = self._io.read_u8le()
            self.ofs_name = self._io.read_u8le()
            if self.version > 60:
                pass
                self.ofs_path = self._io.read_u8le()

            self.num_motions = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.version > 60:
                pass

            _ = self.motion_ids
            if hasattr(self, '_m_motion_ids'):
                pass
                for i in range(len(self._m_motion_ids)):
                    pass
                    self._m_motion_ids[i]._fetch_instances()


            _ = self.motions
            if hasattr(self, '_m_motions'):
                pass
                for i in range(len(self._m_motions)):
                    pass
                    self._m_motions[i]._fetch_instances()


            _ = self.name
            if hasattr(self, '_m_name'):
                pass

            _ = self.name_raw
            if hasattr(self, '_m_name_raw'):
                pass
                for i in range(len(self._m_name_raw)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMotlist.Motlist, self)._write__seq(io)
            self._should_write_motion_ids = self.motion_ids__enabled
            self._should_write_motions = self.motions__enabled
            self._should_write_name = self.name__enabled
            self._should_write_name_raw = self.name_raw__enabled
            self._io.write_u4le(self.version)
            self._io.write_bytes(self.id_magic)
            self._io.write_u8le(self.reserved_00)
            self._io.write_u8le(self.ofs_motions)
            self._io.write_u8le(self.ofs_motion_ids)
            self._io.write_u8le(self.ofs_name)
            if self.version > 60:
                pass
                self._io.write_u8le(self.ofs_path)

            self._io.write_u4le(self.num_motions)


        def _check(self):
            if len(self.id_magic) != 4:
                raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
            if not self.id_magic == b"\x6D\x6C\x73\x74":
                raise kaitaistruct.ValidationNotEqualError(b"\x6D\x6C\x73\x74", self.id_magic, None, u"/types/motlist/seq/1")
            if self.version > 60:
                pass

            if self.motion_ids__enabled:
                pass
                if len(self._m_motion_ids) != self.num_motions:
                    raise kaitaistruct.ConsistencyError(u"motion_ids", self.num_motions, len(self._m_motion_ids))
                for i in range(len(self._m_motion_ids)):
                    pass
                    if self._m_motion_ids[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"motion_ids", self._root, self._m_motion_ids[i]._root)
                    if self._m_motion_ids[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"motion_ids", self, self._m_motion_ids[i]._parent)


            if self.motions__enabled:
                pass
                if len(self._m_motions) != self.num_motions:
                    raise kaitaistruct.ConsistencyError(u"motions", self.num_motions, len(self._m_motions))
                for i in range(len(self._m_motions)):
                    pass
                    if self._m_motions[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"motions", self._root, self._m_motions[i]._root)
                    if self._m_motions[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"motions", self, self._m_motions[i]._parent)


            if self.name__enabled:
                pass

            if self.name_raw__enabled:
                pass
                if len(self._m_name_raw) == 0:
                    raise kaitaistruct.ConsistencyError(u"name_raw", 0, len(self._m_name_raw))
                for i in range(len(self._m_name_raw)):
                    pass
                    _ = self._m_name_raw[i]
                    if (_ == 0) != (i == len(self._m_name_raw) - 1):
                        raise kaitaistruct.ConsistencyError(u"name_raw", i == len(self._m_name_raw) - 1, _ == 0)


            self._dirty = False

        @property
        def motion_ids(self):
            if self._should_write_motion_ids:
                self._write_motion_ids()
            if hasattr(self, '_m_motion_ids'):
                return self._m_motion_ids

            if not self.motion_ids__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_motion_ids)
            self._m_motion_ids = []
            for i in range(self.num_motions):
                _t__m_motion_ids = ReengineMotlist.MotionId(self._io, self, self._root)
                try:
                    _t__m_motion_ids._read()
                finally:
                    self._m_motion_ids.append(_t__m_motion_ids)

            self._io.seek(_pos)
            return getattr(self, '_m_motion_ids', None)

        @motion_ids.setter
        def motion_ids(self, v):
            self._dirty = True
            self._m_motion_ids = v

        def _write_motion_ids(self):
            self._should_write_motion_ids = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_motion_ids)
            for i in range(len(self._m_motion_ids)):
                pass
                self._m_motion_ids[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def motions(self):
            if self._should_write_motions:
                self._write_motions()
            if hasattr(self, '_m_motions'):
                return self._m_motions

            if not self.motions__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_motions)
            self._m_motions = []
            for i in range(self.num_motions):
                _t__m_motions = ReengineMotlist.MotionPointer(self._io, self, self._root)
                try:
                    _t__m_motions._read()
                finally:
                    self._m_motions.append(_t__m_motions)

            self._io.seek(_pos)
            return getattr(self, '_m_motions', None)

        @motions.setter
        def motions(self, v):
            self._dirty = True
            self._m_motions = v

        def _write_motions(self):
            self._should_write_motions = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_motions)
            for i in range(len(self._m_motions)):
                pass
                self._m_motions[i]._write__seq(self._io)

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
            self._io.seek(self.ofs_name)
            self._m_name = (self._io.read_bytes(len(self.name_raw) * 2 - 2)).decode(u"UTF-16LE")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            if len((self._m_name).encode(u"UTF-16LE")) != len(self.name_raw) * 2 - 2:
                raise kaitaistruct.ConsistencyError(u"name", len(self.name_raw) * 2 - 2, len((self._m_name).encode(u"UTF-16LE")))
            self._io.write_bytes((self._m_name).encode(u"UTF-16LE"))
            self._io.seek(_pos)

        @property
        def name_raw(self):
            if self._should_write_name_raw:
                self._write_name_raw()
            if hasattr(self, '_m_name_raw'):
                return self._m_name_raw

            if not self.name_raw__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            self._m_name_raw = []
            i = 0
            while True:
                _ = self._io.read_u2le()
                self._m_name_raw.append(_)
                if _ == 0:
                    break
                i += 1
            self._io.seek(_pos)
            return getattr(self, '_m_name_raw', None)

        @name_raw.setter
        def name_raw(self, v):
            self._dirty = True
            self._m_name_raw = v

        def _write_name_raw(self):
            self._should_write_name_raw = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_name)
            for i in range(len(self._m_name_raw)):
                pass
                self._io.write_u2le(self._m_name_raw[i])

            self._io.seek(_pos)


    class Packed10bit(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Packed10bit, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(10)
            self.y = self._io.read_bits_int_le(10)
            self.z = self._io.read_bits_int_le(10)
            self.reserved = self._io.read_bits_int_le(2)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.Packed10bit, self)._write__seq(io)
            self._io.write_bits_int_le(10, self.x)
            self._io.write_bits_int_le(10, self.y)
            self._io.write_bits_int_le(10, self.z)
            self._io.write_bits_int_le(2, self.reserved)


        def _check(self):
            self._dirty = False


    class Packed13bitBe(ReadWriteKaitaiStruct):
        """5 bytes read as a big-endian 40-bit integer, x in its lowest 13 bits."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Packed13bitBe, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.reserved = self._io.read_bits_int_be(1) != 0
            self.z = self._io.read_bits_int_be(13)
            self.y = self._io.read_bits_int_be(13)
            self.x = self._io.read_bits_int_be(13)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.Packed13bitBe, self)._write__seq(io)
            self._io.write_bits_int_be(1, int(self.reserved))
            self._io.write_bits_int_be(13, self.z)
            self._io.write_bits_int_be(13, self.y)
            self._io.write_bits_int_be(13, self.x)


        def _check(self):
            self._dirty = False


    class Packed18bitBe(ReadWriteKaitaiStruct):
        """7 bytes read as a big-endian 56-bit integer, x in its lowest 18 bits."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Packed18bitBe, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.reserved = self._io.read_bits_int_be(2)
            self.z = self._io.read_bits_int_be(18)
            self.y = self._io.read_bits_int_be(18)
            self.x = self._io.read_bits_int_be(18)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.Packed18bitBe, self)._write__seq(io)
            self._io.write_bits_int_be(2, self.reserved)
            self._io.write_bits_int_be(18, self.z)
            self._io.write_bits_int_be(18, self.y)
            self._io.write_bits_int_be(18, self.x)


        def _check(self):
            self._dirty = False


    class Packed21bit(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Packed21bit, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(21)
            self.y = self._io.read_bits_int_le(21)
            self.z = self._io.read_bits_int_le(21)
            self.reserved = self._io.read_bits_int_le(1) != 0
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.Packed21bit, self)._write__seq(io)
            self._io.write_bits_int_le(21, self.x)
            self._io.write_bits_int_le(21, self.y)
            self._io.write_bits_int_le(21, self.z)
            self._io.write_bits_int_le(1, int(self.reserved))


        def _check(self):
            self._dirty = False


    class Packed5bit(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Packed5bit, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_bits_int_le(5)
            self.y = self._io.read_bits_int_le(5)
            self.z = self._io.read_bits_int_le(5)
            self.reserved = self._io.read_bits_int_le(1) != 0
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.Packed5bit, self)._write__seq(io)
            self._io.write_bits_int_le(5, self.x)
            self._io.write_bits_int_le(5, self.y)
            self._io.write_bits_int_le(5, self.z)
            self._io.write_bits_int_le(1, int(self.reserved))


        def _check(self):
            self._dirty = False


    class Track(ReadWriteKaitaiStruct):
        """One channel of one bone. `keys` holds the raw keys; turning them into
        values takes `unpack` (u) as below, with n = v / (2^bits - 1) for each
        packed component v (verified on every RE2 RT figure motion: the packed
        components of each track reach both 0 and 2^bits - 1).
        
        Translation / scale:
          full, x / y / z / xyz:  the floats as read; the axes a single-axis
                                  key leaves out are u[0], u[1], u[2] in order
                                  (x key -> (k, u1, u2), y -> (u0, k, u2), z -> (u0, u1, k)),
                                  xyz -> (k, k, k)
          5bit, 10bit, 21bit:     (u0*nx + u3, u1*ny + u4, u2*nz + u5)
          x_16bit:                (u0*n + u1, u2, u3); y_16bit (u1, u0*n + u2, u3);
                                  z_16bit (u1, u2, u0*n + u3); xyz_16bit all = u0*n + u1
        Rotation (quaternion x, y, z, w; w = sqrt(max(0, 1 - x^2 - y^2 - z^2))
        for everything but `full`):
          5bit, 8bit, 10bit, 13bit, 16bit, 18bit, 21bit:
                                  (u0*nx + u4, u1*ny + u5, u2*nz + u6)
          x_16bit / y_16bit / z_16bit: that axis = u0*n + u1, the other two 0
          x / y / z:              that axis = the float, the other two 0
          3component(_b):         the three floats as read
        The quaternions are in the same convention as the mesh's bind matrices
        (Noesis conjugates them because of its own convention).
        
        A track with one key has no frame indices; the key is at frame 0.
        """
        def __init__(self, version, kind, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Track, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.version = version
            self.kind = kind
            self._should_write_frame_indices = False
            self.frame_indices__enabled = True
            self._should_write_keys = False
            self.keys__enabled = True
            self._should_write_unpack = False
            self.unpack__enabled = True

        def _read(self):
            self.flags = self._io.read_u4le()
            self.num_keys = self._io.read_u4le()
            if self.version < 78:
                pass
                self.frame_rate = self._io.read_u4le()

            if self.version < 78:
                pass
                self.max_frame = self._io.read_f4le()

            _on = self.version >= 78
            if _on == False:
                pass
                self.ofs_frame_indices = self._io.read_u8le()
            elif _on == True:
                pass
                self.ofs_frame_indices = self._io.read_u4le()
            _on = self.version >= 78
            if _on == False:
                pass
                self.ofs_frame_data = self._io.read_u8le()
            elif _on == True:
                pass
                self.ofs_frame_data = self._io.read_u4le()
            _on = self.version >= 78
            if _on == False:
                pass
                self.ofs_unpack = self._io.read_u8le()
            elif _on == True:
                pass
                self.ofs_unpack = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.version < 78:
                pass

            if self.version < 78:
                pass

            _on = self.version >= 78
            if _on == False:
                pass
            elif _on == True:
                pass
            _on = self.version >= 78
            if _on == False:
                pass
            elif _on == True:
                pass
            _on = self.version >= 78
            if _on == False:
                pass
            elif _on == True:
                pass
            _ = self.frame_indices
            if hasattr(self, '_m_frame_indices'):
                pass
                for i in range(len(self._m_frame_indices)):
                    pass
                    _on = self.frame_index_type
                    if _on == 2:
                        pass
                    elif _on == 4:
                        pass
                    elif _on == 5:
                        pass


            _ = self.keys
            if hasattr(self, '_m_keys'):
                pass
                for i in range(len(self._m_keys)):
                    pass
                    _on = self.encoding
                    if _on == ReengineMotlist.KeyEncoding.rotation_10bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_13bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_18bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_21bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_3component:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_3component_b:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_5bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_8bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_full:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_x:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_x_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_y:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_y_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_z:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.rotation_z_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_10bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_21bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_5bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_full:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_x:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_x_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_xyz:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_xyz_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_y:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_y_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_z:
                        pass
                        self._m_keys[i]._fetch_instances()
                    elif _on == ReengineMotlist.KeyEncoding.translation_z_16bit:
                        pass
                        self._m_keys[i]._fetch_instances()


            _ = self.unpack
            if hasattr(self, '_m_unpack'):
                pass
                for i in range(len(self._m_unpack)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMotlist.Track, self)._write__seq(io)
            self._should_write_frame_indices = self.frame_indices__enabled
            self._should_write_keys = self.keys__enabled
            self._should_write_unpack = self.unpack__enabled
            self._io.write_u4le(self.flags)
            self._io.write_u4le(self.num_keys)
            if self.version < 78:
                pass
                self._io.write_u4le(self.frame_rate)

            if self.version < 78:
                pass
                self._io.write_f4le(self.max_frame)

            _on = self.version >= 78
            if _on == False:
                pass
                self._io.write_u8le(self.ofs_frame_indices)
            elif _on == True:
                pass
                self._io.write_u4le(self.ofs_frame_indices)
            _on = self.version >= 78
            if _on == False:
                pass
                self._io.write_u8le(self.ofs_frame_data)
            elif _on == True:
                pass
                self._io.write_u4le(self.ofs_frame_data)
            _on = self.version >= 78
            if _on == False:
                pass
                self._io.write_u8le(self.ofs_unpack)
            elif _on == True:
                pass
                self._io.write_u4le(self.ofs_unpack)


        def _check(self):
            if self.version < 78:
                pass

            if self.version < 78:
                pass

            _on = self.version >= 78
            if _on == False:
                pass
            elif _on == True:
                pass
            _on = self.version >= 78
            if _on == False:
                pass
            elif _on == True:
                pass
            _on = self.version >= 78
            if _on == False:
                pass
            elif _on == True:
                pass
            if self.frame_indices__enabled:
                pass
                if self.ofs_frame_indices != 0:
                    pass
                    if len(self._m_frame_indices) != self.num_keys:
                        raise kaitaistruct.ConsistencyError(u"frame_indices", self.num_keys, len(self._m_frame_indices))
                    for i in range(len(self._m_frame_indices)):
                        pass
                        _on = self.frame_index_type
                        if _on == 2:
                            pass
                        elif _on == 4:
                            pass
                        elif _on == 5:
                            pass



            if self.keys__enabled:
                pass
                if self.version >= 78:
                    pass
                    if len(self._m_keys) != self.num_keys:
                        raise kaitaistruct.ConsistencyError(u"keys", self.num_keys, len(self._m_keys))
                    for i in range(len(self._m_keys)):
                        pass
                        _on = self.encoding
                        if _on == ReengineMotlist.KeyEncoding.rotation_10bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_13bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_18bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_21bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_3component:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_3component_b:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_5bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_8bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_full:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_x:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_x_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_y:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_y_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_z:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.rotation_z_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_10bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_21bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_5bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_full:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_x:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_x_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_xyz:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_xyz_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_y:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_y_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_z:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)
                        elif _on == ReengineMotlist.KeyEncoding.translation_z_16bit:
                            pass
                            if self._m_keys[i]._root != self._root:
                                raise kaitaistruct.ConsistencyError(u"keys", self._root, self._m_keys[i]._root)
                            if self._m_keys[i]._parent != self:
                                raise kaitaistruct.ConsistencyError(u"keys", self, self._m_keys[i]._parent)



            if self.unpack__enabled:
                pass
                if self.ofs_unpack != 0:
                    pass
                    if len(self._m_unpack) != self.num_unpack:
                        raise kaitaistruct.ConsistencyError(u"unpack", self.num_unpack, len(self._m_unpack))
                    for i in range(len(self._m_unpack)):
                        pass



            self._dirty = False

        @property
        def compression(self):
            """Key encoding, flags & 0xff000 (Noesis readFrame, 010 Load* names)."""
            if hasattr(self, '_m_compression'):
                return self._m_compression

            self._m_compression = self.flags & 1044480
            return getattr(self, '_m_compression', None)

        def _invalidate_compression(self):
            del self._m_compression
        @property
        def encoding(self):
            """compression tagged with the track kind, since the same bits mean
            different things for rotations. Scales use the translation codes
            (Noesis reads both through the same branch). Only the meanings of
            mot >= 78 (RE3 onwards, which includes RE2 RT's 492) are listed.
            """
            if hasattr(self, '_m_encoding'):
                return self._m_encoding

            self._m_encoding = KaitaiStream.resolve_enum(ReengineMotlist.KeyEncoding, (1048576 if self.kind == 1 else 0) | self.compression)
            return getattr(self, '_m_encoding', None)

        def _invalidate_encoding(self):
            del self._m_encoding
        @property
        def frame_index_type(self):
            """Width of the frame numbers, flags >> 20 (2 u1, 4 u2, 5 u4)."""
            if hasattr(self, '_m_frame_index_type'):
                return self._m_frame_index_type

            self._m_frame_index_type = self.flags >> 20
            return getattr(self, '_m_frame_index_type', None)

        def _invalidate_frame_index_type(self):
            del self._m_frame_index_type
        @property
        def frame_indices(self):
            """Absent (offset 0) when the track has a single key, which is then at frame 0."""
            if self._should_write_frame_indices:
                self._write_frame_indices()
            if hasattr(self, '_m_frame_indices'):
                return self._m_frame_indices

            if not self.frame_indices__enabled:
                return None

            if self.ofs_frame_indices != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_frame_indices)
                self._m_frame_indices = []
                for i in range(self.num_keys):
                    _on = self.frame_index_type
                    if _on == 2:
                        pass
                        self._m_frame_indices.append(self._io.read_u1())
                    elif _on == 4:
                        pass
                        self._m_frame_indices.append(self._io.read_u2le())
                    elif _on == 5:
                        pass
                        self._m_frame_indices.append(self._io.read_u4le())

                self._io.seek(_pos)

            return getattr(self, '_m_frame_indices', None)

        @frame_indices.setter
        def frame_indices(self, v):
            self._dirty = True
            self._m_frame_indices = v

        def _write_frame_indices(self):
            self._should_write_frame_indices = False
            if self.ofs_frame_indices != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_frame_indices)
                for i in range(len(self._m_frame_indices)):
                    pass
                    _on = self.frame_index_type
                    if _on == 2:
                        pass
                        self._io.write_u1(self._m_frame_indices[i])
                    elif _on == 4:
                        pass
                        self._io.write_u2le(self._m_frame_indices[i])
                    elif _on == 5:
                        pass
                        self._io.write_u4le(self._m_frame_indices[i])

                self._io.seek(_pos)


        @property
        def keys(self):
            if self._should_write_keys:
                self._write_keys()
            if hasattr(self, '_m_keys'):
                return self._m_keys

            if not self.keys__enabled:
                return None

            if self.version >= 78:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_frame_data)
                self._m_keys = []
                for i in range(self.num_keys):
                    _on = self.encoding
                    if _on == ReengineMotlist.KeyEncoding.rotation_10bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed10bit(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_13bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed13bitBe(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Vec3(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_18bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed18bitBe(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_21bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed21bit(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_3component:
                        pass
                        _t__m_keys = ReengineMotlist.Vec3(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_3component_b:
                        pass
                        _t__m_keys = ReengineMotlist.Vec3(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_5bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed5bit(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_8bit:
                        pass
                        _t__m_keys = ReengineMotlist.U1Vec3(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_full:
                        pass
                        _t__m_keys = ReengineMotlist.Vec4(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_x:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_x_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_y:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_y_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_z:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_z_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_10bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed10bit(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_21bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed21bit(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_5bit:
                        pass
                        _t__m_keys = ReengineMotlist.Packed5bit(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_full:
                        pass
                        _t__m_keys = ReengineMotlist.Vec3(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_x:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_x_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_xyz:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_xyz_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_y:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_y_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_z:
                        pass
                        _t__m_keys = ReengineMotlist.F4Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)
                    elif _on == ReengineMotlist.KeyEncoding.translation_z_16bit:
                        pass
                        _t__m_keys = ReengineMotlist.U2Value(self._io, self, self._root)
                        try:
                            _t__m_keys._read()
                        finally:
                            self._m_keys.append(_t__m_keys)

                self._io.seek(_pos)

            return getattr(self, '_m_keys', None)

        @keys.setter
        def keys(self, v):
            self._dirty = True
            self._m_keys = v

        def _write_keys(self):
            self._should_write_keys = False
            if self.version >= 78:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_frame_data)
                for i in range(len(self._m_keys)):
                    pass
                    _on = self.encoding
                    if _on == ReengineMotlist.KeyEncoding.rotation_10bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_13bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_18bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_21bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_3component:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_3component_b:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_5bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_8bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_full:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_x:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_x_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_y:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_y_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_z:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.rotation_z_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_10bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_21bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_5bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_full:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_x:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_x_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_xyz:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_xyz_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_y:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_y_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_z:
                        pass
                        self._m_keys[i]._write__seq(self._io)
                    elif _on == ReengineMotlist.KeyEncoding.translation_z_16bit:
                        pass
                        self._m_keys[i]._write__seq(self._io)

                self._io.seek(_pos)


        @property
        def num_unpack(self):
            """Floats the quantized encodings scale and offset their keys with.
            The single-axis encodings (compression & 0xf000 != 0) use four,
            the others eight; see the `track` doc for which slot is which.
            """
            if hasattr(self, '_m_num_unpack'):
                return self._m_num_unpack

            self._m_num_unpack = (4 if self.compression & 61440 != 0 else 8)
            return getattr(self, '_m_num_unpack', None)

        def _invalidate_num_unpack(self):
            del self._m_num_unpack
        @property
        def unpack(self):
            if self._should_write_unpack:
                self._write_unpack()
            if hasattr(self, '_m_unpack'):
                return self._m_unpack

            if not self.unpack__enabled:
                return None

            if self.ofs_unpack != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_unpack)
                self._m_unpack = []
                for i in range(self.num_unpack):
                    self._m_unpack.append(self._io.read_f4le())

                self._io.seek(_pos)

            return getattr(self, '_m_unpack', None)

        @unpack.setter
        def unpack(self, v):
            self._dirty = True
            self._m_unpack = v

        def _write_unpack(self):
            self._should_write_unpack = False
            if self.ofs_unpack != 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_unpack)
                for i in range(len(self._m_unpack)):
                    pass
                    self._io.write_f4le(self._m_unpack[i])

                self._io.seek(_pos)



    class U1Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.U1Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.U1Vec3, self)._write__seq(io)
            self._io.write_u1(self.x)
            self._io.write_u1(self.y)
            self._io.write_u1(self.z)


        def _check(self):
            self._dirty = False


    class U2Value(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.U2Value, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.value = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.U2Value, self)._write__seq(io)
            self._io.write_u2le(self.value)


        def _check(self):
            self._dirty = False


    class U2Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.U2Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u2le()
            self.y = self._io.read_u2le()
            self.z = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMotlist.U2Vec3, self)._write__seq(io)
            self._io.write_u2le(self.x)
            self._io.write_u2le(self.y)
            self._io.write_u2le(self.z)


        def _check(self):
            self._dirty = False


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Vec3, self).__init__(_io)
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
            super(ReengineMotlist.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMotlist.Vec4, self).__init__(_io)
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
            super(ReengineMotlist.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    @property
    def mot(self):
        if self._should_write_mot:
            self._write_mot()
        if hasattr(self, '_m_mot'):
            return self._m_mot

        if not self.mot__enabled:
            return None

        if self.magic == u"mot ":
            pass
            _pos = self._io.pos()
            self._io.seek(0)
            self._raw__m_mot = self._io.read_bytes_full()
            _io__raw__m_mot = KaitaiStream(BytesIO(self._raw__m_mot))
            self._m_mot = ReengineMotlist.Mot(_io__raw__m_mot, self, self._root)
            self._m_mot._read()
            self._io.seek(_pos)

        return getattr(self, '_m_mot', None)

    @mot.setter
    def mot(self, v):
        self._dirty = True
        self._m_mot = v

    def _write_mot(self):
        self._should_write_mot = False
        if self.magic == u"mot ":
            pass
            _pos = self._io.pos()
            self._io.seek(0)
            _io__raw__m_mot = KaitaiStream(BytesIO(bytearray(self._io.size() - self._io.pos())))
            self._io.add_child_stream(_io__raw__m_mot)
            _pos2 = self._io.pos()
            self._io.seek(self._io.pos() + (self._io.size() - self._io.pos()))
            def handler(parent, _io__raw__m_mot=_io__raw__m_mot):
                self._raw__m_mot = _io__raw__m_mot.to_byte_array()
                parent.write_bytes(self._raw__m_mot)
                if not parent.is_eof():
                    raise kaitaistruct.ConsistencyError(u"raw(mot)", 0, parent.size() - parent.pos())
            _io__raw__m_mot.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
            self._m_mot._write__seq(_io__raw__m_mot)
            self._io.seek(_pos)


    @property
    def motlist(self):
        if self._should_write_motlist:
            self._write_motlist()
        if hasattr(self, '_m_motlist'):
            return self._m_motlist

        if not self.motlist__enabled:
            return None

        if self.magic == u"mlst":
            pass
            _pos = self._io.pos()
            self._io.seek(0)
            self._raw__m_motlist = self._io.read_bytes_full()
            _io__raw__m_motlist = KaitaiStream(BytesIO(self._raw__m_motlist))
            self._m_motlist = ReengineMotlist.Motlist(_io__raw__m_motlist, self, self._root)
            self._m_motlist._read()
            self._io.seek(_pos)

        return getattr(self, '_m_motlist', None)

    @motlist.setter
    def motlist(self, v):
        self._dirty = True
        self._m_motlist = v

    def _write_motlist(self):
        self._should_write_motlist = False
        if self.magic == u"mlst":
            pass
            _pos = self._io.pos()
            self._io.seek(0)
            _io__raw__m_motlist = KaitaiStream(BytesIO(bytearray(self._io.size() - self._io.pos())))
            self._io.add_child_stream(_io__raw__m_motlist)
            _pos2 = self._io.pos()
            self._io.seek(self._io.pos() + (self._io.size() - self._io.pos()))
            def handler(parent, _io__raw__m_motlist=_io__raw__m_motlist):
                self._raw__m_motlist = _io__raw__m_motlist.to_byte_array()
                parent.write_bytes(self._raw__m_motlist)
                if not parent.is_eof():
                    raise kaitaistruct.ConsistencyError(u"raw(motlist)", 0, parent.size() - parent.pos())
            _io__raw__m_motlist.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
            self._m_motlist._write__seq(_io__raw__m_motlist)
            self._io.seek(_pos)



