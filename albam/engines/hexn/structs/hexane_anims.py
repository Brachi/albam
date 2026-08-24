# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneAnims(ReadWriteKaitaiStruct):
    """RE:ORC's `Animation/Projects/*.anims.ssg` bundles many named animation
    clips for one or more skeletons into a single archive. The outer
    container is structurally identical to the regular Hexane .ssg archive
    (see ssg.ksy) - same 32-byte header, same 32-byte-per-entry file table,
    same trailing `buffer_chunks` blob - except every multi-byte integer is
    stored big-endian here instead of little-endian, and `id_magic` is 5 or
    6 rather than always 6 (both observed on real files; meaning not
    confirmed - possibly "uncompressed"/short archives get 5). Verified
    against the committed test dataset: every entry packs into
    `buffer_chunks` back-to-back with *no* padding between entries (unlike
    the regular, little-endian .ssg where each file is padded up to
    `size_padding`) - `size_padding` itself is present here too but never
    matches a real per-entry gap on any file checked, so it's kept only for
    round-trip fidelity, not used to compute entry offsets. `size_chunks_info`
    (the zlib chunk-size table) is always 0 on every real archive checked
    except a handful of leftover dev/test archives, which hold a garbage
    value far larger than the whole file and have a different, unrelated
    internal layout (confirmed by their file_info's own `reserved_01` field
    being 1 instead of 0, unlike every real archive) and fail to parse here;
    zlib chunk decompression itself is not implemented in this format for
    that reason - see hexane_ssg.py's own SsgFS for the (little-endian)
    precedent this would follow if a real compressed *.anims.ssg ever turns
    up.
    
    Each entry's own name follows an `<clip_path>--<skeleton_name>` naming
    convention - splitting on the last `--` recovers the skeleton this clip
    is meant to be played on, matching real files under
    `dlc/pack1/Characters/skel/<skeleton_name>.ssg` (weapon rigs use their
    own distinct skeleton names too, separate from humanoid/creature ones).
    `file_info.file_type` is always 5 for a clip entry here
    (vs. 4 for a skeleton entry in the sibling `skel/*.ssg` archives, which
    share this exact same big-endian container).
    
    A clip's own raw bytes (sliced out of `buffer_chunks` the same way
    hexane_ssg.py's SsgFS does, in Python, not in this .ksy) are themselves
    a small, little-endian header (`anim_clip` below) followed by the actual
    keyframe data. That inner format is Sony's PS3 "Edge" middleware
    animation format (`EdgeAnimAnimation`) - RE:ORC's own tooling reused it
    wholesale (`dlc/pack1/Characters/*.edgemodel` reusing Sony's "Edge"
    model format the same way is already established in edgemodel.ksy).
    `anim_clip`'s header fields (through `size_custom_data`, 88 bytes) are
    modeled field-for-field against a community Blender import script that
    documents `EdgeAnimAnimation`'s C struct layout - cross-checked here,
    not taken on faith: independently re-deriving `size_header` from the
    channel-count fields (aligned per-channel-type index arrays + const-
    channel data + the per-frameset dma/info tables, all 16-byte-aligned
    per the reference) reproduces the real stored `size_header` value
    exactly across the whole verified dataset (every clip entry except the
    handful of dev/test archives above) - 100% match, not a single byte
    off. Past `size_header`,
    the format is a bit-packed, adaptively-interpolated keyframe stream
    (constant channels store one value; animated channels are split into
    "framesets" that bracket each frame between two explicit keys located
    via a per-frame bitmask search, then slerp/lerp between them) - left
    entirely opaque here (`body`) since expressing that in Kaitai's own
    field model isn't practical; `albam.engines.hexn.animation` decodes it
    directly against these same raw bytes in Python instead, porting the
    reference script's algorithm (itself re-verified against real bytes,
    not trusted blindly).
    """
    def __init__(self, _io=None, _parent=None, _root=None):
        super(HexaneAnims, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_buffer_chunks = False
        self.buffer_chunks__enabled = True

    def _read(self):
        self.id_magic = self._io.read_u4be()
        self.reserved_01 = self._io.read_u4be()
        self.size_files_info = self._io.read_u4be()
        self.size_file_names = self._io.read_u4be()
        self.size_chunks_buffer = self._io.read_u4be()
        self.reserved_02 = self._io.read_u4be()
        self.size_chunks_info = self._io.read_u4be()
        self.size_padding = self._io.read_u4be()
        self.files_info = []
        for i in range(self.size_files_info // 32):
            _t_files_info = HexaneAnims.FileInfo(self._io, self, self._root)
            try:
                _t_files_info._read()
            finally:
                self.files_info.append(_t_files_info)

        self.chunk_sizes = []
        for i in range(self.size_chunks_info // 4):
            self.chunk_sizes.append(self._io.read_u4be())

        self.file_names = self._io.read_bytes(self.size_file_names)
        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.files_info)):
            pass
            self.files_info[i]._fetch_instances()

        for i in range(len(self.chunk_sizes)):
            pass

        _ = self.buffer_chunks
        if hasattr(self, '_m_buffer_chunks'):
            pass



    def _write__seq(self, io=None):
        super(HexaneAnims, self)._write__seq(io)
        self._should_write_buffer_chunks = self.buffer_chunks__enabled
        self._io.write_u4be(self.id_magic)
        self._io.write_u4be(self.reserved_01)
        self._io.write_u4be(self.size_files_info)
        self._io.write_u4be(self.size_file_names)
        self._io.write_u4be(self.size_chunks_buffer)
        self._io.write_u4be(self.reserved_02)
        self._io.write_u4be(self.size_chunks_info)
        self._io.write_u4be(self.size_padding)
        for i in range(len(self.files_info)):
            pass
            self.files_info[i]._write__seq(self._io)

        for i in range(len(self.chunk_sizes)):
            pass
            self._io.write_u4be(self.chunk_sizes[i])

        self._io.write_bytes(self.file_names)


    def _check(self):
        if len(self.files_info) != self.size_files_info // 32:
            raise kaitaistruct.ConsistencyError(u"files_info", self.size_files_info // 32, len(self.files_info))
        for i in range(len(self.files_info)):
            pass
            if self.files_info[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"files_info", self._root, self.files_info[i]._root)
            if self.files_info[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"files_info", self, self.files_info[i]._parent)

        if len(self.chunk_sizes) != self.size_chunks_info // 4:
            raise kaitaistruct.ConsistencyError(u"chunk_sizes", self.size_chunks_info // 4, len(self.chunk_sizes))
        for i in range(len(self.chunk_sizes)):
            pass

        if len(self.file_names) != self.size_file_names:
            raise kaitaistruct.ConsistencyError(u"file_names", self.size_file_names, len(self.file_names))
        if self.buffer_chunks__enabled:
            pass
            if len(self._m_buffer_chunks) != self.size_chunks_buffer:
                raise kaitaistruct.ConsistencyError(u"buffer_chunks", self.size_chunks_buffer, len(self._m_buffer_chunks))

        self._dirty = False

    class AnimClip(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneAnims.AnimClip, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.id_magic = self._io.read_bytes(4)
            if not self.id_magic == b"\x34\x30\x41\x45":
                raise kaitaistruct.ValidationNotEqualError(b"\x34\x30\x41\x45", self.id_magic, self._io, u"/types/anim_clip/seq/0")
            self.duration_seconds = self._io.read_f4le()
            self.framerate = self._io.read_f4le()
            self.size_header = self._io.read_u2le()
            self.num_bones = self._io.read_u2le()
            self.num_frames = self._io.read_u2le()
            self.num_frame_sets = self._io.read_u2le()
            self.buffer_size = self._io.read_u2le()
            self.num_const_r_channels = self._io.read_u2le()
            self.num_const_t_channels = self._io.read_u2le()
            self.num_const_s_channels = self._io.read_u2le()
            self.num_const_user_channels = self._io.read_u2le()
            self.num_anim_r_channels = self._io.read_u2le()
            self.num_anim_t_channels = self._io.read_u2le()
            self.num_anim_s_channels = self._io.read_u2le()
            self.num_anim_user_channels = self._io.read_u2le()
            self.flags = self._io.read_u2le()
            self.size_joints_weight_array = self._io.read_u4le()
            self.user_joints_weight_array = self._io.read_u4le()
            self.offset_joints_weight_array = self._io.read_u4le()
            self.offset_frame_set_dma_array = self._io.read_u4le()
            self.offset_frame_set_info_array = self._io.read_u4le()
            self.offset_const_r_data = self._io.read_u4le()
            self.offset_const_t_data = self._io.read_u4le()
            self.offset_const_s_data = self._io.read_u4le()
            self.offset_const_user_data = self._io.read_u4le()
            self.offset_packing_specs = self._io.read_u4le()
            self.offset_custom_data = self._io.read_u4le()
            self.size_custom_data = self._io.read_u4le()
            self.reserved_or_align = self._io.read_bytes(8)
            self.body = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(HexaneAnims.AnimClip, self)._write__seq(io)
            self._io.write_bytes(self.id_magic)
            self._io.write_f4le(self.duration_seconds)
            self._io.write_f4le(self.framerate)
            self._io.write_u2le(self.size_header)
            self._io.write_u2le(self.num_bones)
            self._io.write_u2le(self.num_frames)
            self._io.write_u2le(self.num_frame_sets)
            self._io.write_u2le(self.buffer_size)
            self._io.write_u2le(self.num_const_r_channels)
            self._io.write_u2le(self.num_const_t_channels)
            self._io.write_u2le(self.num_const_s_channels)
            self._io.write_u2le(self.num_const_user_channels)
            self._io.write_u2le(self.num_anim_r_channels)
            self._io.write_u2le(self.num_anim_t_channels)
            self._io.write_u2le(self.num_anim_s_channels)
            self._io.write_u2le(self.num_anim_user_channels)
            self._io.write_u2le(self.flags)
            self._io.write_u4le(self.size_joints_weight_array)
            self._io.write_u4le(self.user_joints_weight_array)
            self._io.write_u4le(self.offset_joints_weight_array)
            self._io.write_u4le(self.offset_frame_set_dma_array)
            self._io.write_u4le(self.offset_frame_set_info_array)
            self._io.write_u4le(self.offset_const_r_data)
            self._io.write_u4le(self.offset_const_t_data)
            self._io.write_u4le(self.offset_const_s_data)
            self._io.write_u4le(self.offset_const_user_data)
            self._io.write_u4le(self.offset_packing_specs)
            self._io.write_u4le(self.offset_custom_data)
            self._io.write_u4le(self.size_custom_data)
            self._io.write_bytes(self.reserved_or_align)
            self._io.write_bytes(self.body)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"body", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self.id_magic) != 4:
                raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
            if not self.id_magic == b"\x34\x30\x41\x45":
                raise kaitaistruct.ValidationNotEqualError(b"\x34\x30\x41\x45", self.id_magic, None, u"/types/anim_clip/seq/0")
            if len(self.reserved_or_align) != 8:
                raise kaitaistruct.ConsistencyError(u"reserved_or_align", 8, len(self.reserved_or_align))
            self._dirty = False


    class FileInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneAnims.FileInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.ident = self._io.read_u4be()
            self.name_offset_rel = self._io.read_u4be()
            self.size = self._io.read_u4be()
            self.reserved_01 = self._io.read_u4be()
            self.reserved_02 = self._io.read_u4be()
            self.file_type = self._io.read_s4be()
            self.unk_01 = self._io.read_u4be()
            self.unk_02 = self._io.read_u4be()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(HexaneAnims.FileInfo, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4be(self.ident)
            self._io.write_u4be(self.name_offset_rel)
            self._io.write_u4be(self.size)
            self._io.write_u4be(self.reserved_01)
            self._io.write_u4be(self.reserved_02)
            self._io.write_s4be(self.file_type)
            self._io.write_u4be(self.unk_01)
            self._io.write_u4be(self.unk_02)


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
            self._io.seek(((32 + self._parent.size_files_info) + self._parent.size_chunks_info) + self.name_offset_rel)
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
            self._io.seek(((32 + self._parent.size_files_info) + self._parent.size_chunks_info) + self.name_offset_rel)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    @property
    def buffer_chunks(self):
        if self._should_write_buffer_chunks:
            self._write_buffer_chunks()
        if hasattr(self, '_m_buffer_chunks'):
            return self._m_buffer_chunks

        if not self.buffer_chunks__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(((32 + self.size_files_info) + self.size_chunks_info) + self.size_file_names)
        self._m_buffer_chunks = self._io.read_bytes(self.size_chunks_buffer)
        self._io.seek(_pos)
        return getattr(self, '_m_buffer_chunks', None)

    @buffer_chunks.setter
    def buffer_chunks(self, v):
        self._dirty = True
        self._m_buffer_chunks = v

    def _write_buffer_chunks(self):
        self._should_write_buffer_chunks = False
        _pos = self._io.pos()
        self._io.seek(((32 + self.size_files_info) + self.size_chunks_info) + self.size_file_names)
        self._io.write_bytes(self._m_buffer_chunks)
        self._io.seek(_pos)


