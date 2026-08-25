# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneSkel(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(HexaneSkel, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_hash_array = False
        self.hash_array__enabled = True
        self._should_write_hierarchy_padding = False
        self.hierarchy_padding__enabled = True
        self._should_write_local_transforms = False
        self.local_transforms__enabled = True
        self._should_write_name_offsets = False
        self.name_offsets__enabled = True
        self._should_write_names = False
        self.names__enabled = True
        self._should_write_parents = False
        self.parents__enabled = True
        self._should_write_parents_padding = False
        self.parents_padding__enabled = True
        self._should_write_pre_transforms_data = False
        self.pre_transforms_data__enabled = True
        self._should_write_trailing_padding = False
        self.trailing_padding__enabled = True

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x00\x00\x00\x06":
            raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x06", self.magic, self._io, u"/seq/0")
        self.reserved_01 = self._io.read_u4be()
        self.header_size = self._io.read_u4be()
        self.name_field_size = self._io.read_u4be()
        self.body_size = self._io.read_u4be()
        self.reserved_02 = self._io.read_u4be()
        self.reserved_03 = self._io.read_u4be()
        self.reserved_04 = self._io.read_u4be()
        self.checksum_1 = self._io.read_u4be()
        self.reserved_05 = self._io.read_u4be()
        self.inner_body_size = self._io.read_u4be()
        self.reserved_06 = self._io.read_u4be()
        self.reserved_07 = self._io.read_u4be()
        self.reserved_08 = self._io.read_u4be()
        self.checksum_2 = self._io.read_u4be()
        self.reserved_09 = self._io.read_u4be()
        self.own_path = (KaitaiStream.bytes_terminate(self._io.read_bytes(128), 0, False)).decode(u"ASCII")
        self.tag = self._io.read_bytes(4)
        if not self.tag == b"\x32\x30\x53\x45":
            raise kaitaistruct.ValidationNotEqualError(b"\x32\x30\x53\x45", self.tag, self._io, u"/seq/17")
        self.total = self._io.read_u4le()
        self.c8_unk = self._io.read_u4le()
        self.hierarchy_size = self._io.read_u4le()
        self.node_count = self._io.read_u4le()
        self.second_count = self._io.read_u4le()
        self.d8_ofs_local_transforms = self._io.read_u4le()
        self.dc_ofs_parents = self._io.read_u4le()
        self.e0_ofs_hash_array = self._io.read_u4le()
        self.e4_ofs_body_end_a = self._io.read_u4le()
        self.e8_ofs_body_end_b = self._io.read_u4le()
        self.ec_ofs_u16_array_end = self._io.read_u4le()
        self.f0_ofs_name_offsets = self._io.read_u4le()
        self.reserved_10 = self._io.read_u4le()
        self.reserved_11 = self._io.read_u4le()
        self.reserved_12 = self._io.read_u4le()
        self.hierarchy = []
        for i in range(self.node_count):
            _t_hierarchy = HexaneSkel.HierarchyEntry(self._io, self, self._root)
            try:
                _t_hierarchy._read()
            finally:
                self.hierarchy.append(_t_hierarchy)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.hierarchy)):
            pass
            self.hierarchy[i]._fetch_instances()

        _ = self.hash_array
        if hasattr(self, '_m_hash_array'):
            pass

        _ = self.hierarchy_padding
        if hasattr(self, '_m_hierarchy_padding'):
            pass

        _ = self.local_transforms
        if hasattr(self, '_m_local_transforms'):
            pass
            for i in range(len(self._m_local_transforms)):
                pass
                self._m_local_transforms[i]._fetch_instances()


        _ = self.name_offsets
        if hasattr(self, '_m_name_offsets'):
            pass
            for i in range(len(self._m_name_offsets)):
                pass


        _ = self.names
        if hasattr(self, '_m_names'):
            pass
            for i in range(len(self._m_names)):
                pass


        _ = self.parents
        if hasattr(self, '_m_parents'):
            pass
            for i in range(len(self._m_parents)):
                pass


        _ = self.parents_padding
        if hasattr(self, '_m_parents_padding'):
            pass

        _ = self.pre_transforms_data
        if hasattr(self, '_m_pre_transforms_data'):
            pass

        _ = self.trailing_padding
        if hasattr(self, '_m_trailing_padding'):
            pass



    def _write__seq(self, io=None):
        super(HexaneSkel, self)._write__seq(io)
        self._should_write_hash_array = self.hash_array__enabled
        self._should_write_hierarchy_padding = self.hierarchy_padding__enabled
        self._should_write_local_transforms = self.local_transforms__enabled
        self._should_write_name_offsets = self.name_offsets__enabled
        self._should_write_names = self.names__enabled
        self._should_write_parents = self.parents__enabled
        self._should_write_parents_padding = self.parents_padding__enabled
        self._should_write_pre_transforms_data = self.pre_transforms_data__enabled
        self._should_write_trailing_padding = self.trailing_padding__enabled
        self._io.write_bytes(self.magic)
        self._io.write_u4be(self.reserved_01)
        self._io.write_u4be(self.header_size)
        self._io.write_u4be(self.name_field_size)
        self._io.write_u4be(self.body_size)
        self._io.write_u4be(self.reserved_02)
        self._io.write_u4be(self.reserved_03)
        self._io.write_u4be(self.reserved_04)
        self._io.write_u4be(self.checksum_1)
        self._io.write_u4be(self.reserved_05)
        self._io.write_u4be(self.inner_body_size)
        self._io.write_u4be(self.reserved_06)
        self._io.write_u4be(self.reserved_07)
        self._io.write_u4be(self.reserved_08)
        self._io.write_u4be(self.checksum_2)
        self._io.write_u4be(self.reserved_09)
        self._io.write_bytes_limit((self.own_path).encode(u"ASCII"), 128, 0, 0)
        self._io.write_bytes(self.tag)
        self._io.write_u4le(self.total)
        self._io.write_u4le(self.c8_unk)
        self._io.write_u4le(self.hierarchy_size)
        self._io.write_u4le(self.node_count)
        self._io.write_u4le(self.second_count)
        self._io.write_u4le(self.d8_ofs_local_transforms)
        self._io.write_u4le(self.dc_ofs_parents)
        self._io.write_u4le(self.e0_ofs_hash_array)
        self._io.write_u4le(self.e4_ofs_body_end_a)
        self._io.write_u4le(self.e8_ofs_body_end_b)
        self._io.write_u4le(self.ec_ofs_u16_array_end)
        self._io.write_u4le(self.f0_ofs_name_offsets)
        self._io.write_u4le(self.reserved_10)
        self._io.write_u4le(self.reserved_11)
        self._io.write_u4le(self.reserved_12)
        for i in range(len(self.hierarchy)):
            pass
            self.hierarchy[i]._write__seq(self._io)



    def _check(self):
        if len(self.magic) != 4:
            raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
        if not self.magic == b"\x00\x00\x00\x06":
            raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x06", self.magic, None, u"/seq/0")
        if len((self.own_path).encode(u"ASCII")) > 128:
            raise kaitaistruct.ConsistencyError(u"own_path", 128, len((self.own_path).encode(u"ASCII")))
        if KaitaiStream.byte_array_index_of((self.own_path).encode(u"ASCII"), 0) != -1:
            raise kaitaistruct.ConsistencyError(u"own_path", -1, KaitaiStream.byte_array_index_of((self.own_path).encode(u"ASCII"), 0))
        if len(self.tag) != 4:
            raise kaitaistruct.ConsistencyError(u"tag", 4, len(self.tag))
        if not self.tag == b"\x32\x30\x53\x45":
            raise kaitaistruct.ValidationNotEqualError(b"\x32\x30\x53\x45", self.tag, None, u"/seq/17")
        if len(self.hierarchy) != self.node_count:
            raise kaitaistruct.ConsistencyError(u"hierarchy", self.node_count, len(self.hierarchy))
        for i in range(len(self.hierarchy)):
            pass
            if self.hierarchy[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"hierarchy", self._root, self.hierarchy[i]._root)
            if self.hierarchy[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"hierarchy", self, self.hierarchy[i]._parent)

        if self.hash_array__enabled:
            pass
            if len(self._m_hash_array) != self.hierarchy_size:
                raise kaitaistruct.ConsistencyError(u"hash_array", self.hierarchy_size, len(self._m_hash_array))

        if self.hierarchy_padding__enabled:
            pass
            if self.hierarchy_size > self.node_count * 4:
                pass
                if len(self._m_hierarchy_padding) != self.hierarchy_size - self.node_count * 4:
                    raise kaitaistruct.ConsistencyError(u"hierarchy_padding", self.hierarchy_size - self.node_count * 4, len(self._m_hierarchy_padding))


        if self.local_transforms__enabled:
            pass
            if len(self._m_local_transforms) != self.node_count:
                raise kaitaistruct.ConsistencyError(u"local_transforms", self.node_count, len(self._m_local_transforms))
            for i in range(len(self._m_local_transforms)):
                pass
                if self._m_local_transforms[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"local_transforms", self._root, self._m_local_transforms[i]._root)
                if self._m_local_transforms[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"local_transforms", self, self._m_local_transforms[i]._parent)


        if self.name_offsets__enabled:
            pass
            if len(self._m_name_offsets) != self.node_count:
                raise kaitaistruct.ConsistencyError(u"name_offsets", self.node_count, len(self._m_name_offsets))
            for i in range(len(self._m_name_offsets)):
                pass


        if self.names__enabled:
            pass
            if len(self._m_names) != self.node_count:
                raise kaitaistruct.ConsistencyError(u"names", self.node_count, len(self._m_names))
            for i in range(len(self._m_names)):
                pass
                if KaitaiStream.byte_array_index_of((self._m_names[i]).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"names", -1, KaitaiStream.byte_array_index_of((self._m_names[i]).encode(u"ASCII"), 0))


        if self.parents__enabled:
            pass
            if len(self._m_parents) != self.node_count:
                raise kaitaistruct.ConsistencyError(u"parents", self.node_count, len(self._m_parents))
            for i in range(len(self._m_parents)):
                pass


        if self.parents_padding__enabled:
            pass
            if self.name_offsets_start > self.parents_end:
                pass
                if len(self._m_parents_padding) != self.name_offsets_start - self.parents_end:
                    raise kaitaistruct.ConsistencyError(u"parents_padding", self.name_offsets_start - self.parents_end, len(self._m_parents_padding))


        if self.pre_transforms_data__enabled:
            pass
            if self.local_transforms_start > self.hierarchy_end:
                pass
                if len(self._m_pre_transforms_data) != self.local_transforms_start - self.hierarchy_end:
                    raise kaitaistruct.ConsistencyError(u"pre_transforms_data", self.local_transforms_start - self.hierarchy_end, len(self._m_pre_transforms_data))


        if self.trailing_padding__enabled:
            pass

        self._dirty = False

    class HierarchyEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneSkel.HierarchyEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_a = self._io.read_u2le()
            self.unk_b = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(HexaneSkel.HierarchyEntry, self)._write__seq(io)
            self._io.write_u2le(self.unk_a)
            self._io.write_u2le(self.unk_b)


        def _check(self):
            self._dirty = False


    class LocalTrs(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneSkel.LocalTrs, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.rotation = HexaneSkel.Vec4f(self._io, self, self._root)
            self.rotation._read()
            self.position = HexaneSkel.Vec4f(self._io, self, self._root)
            self.position._read()
            self.scale = HexaneSkel.Vec4f(self._io, self, self._root)
            self.scale._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.rotation._fetch_instances()
            self.position._fetch_instances()
            self.scale._fetch_instances()


        def _write__seq(self, io=None):
            super(HexaneSkel.LocalTrs, self)._write__seq(io)
            self.rotation._write__seq(self._io)
            self.position._write__seq(self._io)
            self.scale._write__seq(self._io)


        def _check(self):
            if self.rotation._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rotation", self._root, self.rotation._root)
            if self.rotation._parent != self:
                raise kaitaistruct.ConsistencyError(u"rotation", self, self.rotation._parent)
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self._root, self.position._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self, self.position._parent)
            if self.scale._root != self._root:
                raise kaitaistruct.ConsistencyError(u"scale", self._root, self.scale._root)
            if self.scale._parent != self:
                raise kaitaistruct.ConsistencyError(u"scale", self, self.scale._parent)
            self._dirty = False


    class Vec4f(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneSkel.Vec4f, self).__init__(_io)
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
            super(HexaneSkel.Vec4f, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    @property
    def body_end(self):
        if hasattr(self, '_m_body_end'):
            return self._m_body_end

        self._m_body_end = 192 + self.total
        return getattr(self, '_m_body_end', None)

    def _invalidate_body_end(self):
        del self._m_body_end
    @property
    def hash_array(self):
        """node_count u32 values (hierarchy_size bytes total, same round-up-to-16 formula as `hierarchy`), immediately followed by body_end with no further gap (confirmed across the verified dataset: hash_array_start rounds `names`' real end up to the next 16-byte ABSOLUTE file boundary, not a names-blob-relative one, and hash_array_start + hierarchy_size == body_end exactly on every file). Values don't match fnv1, fnv1a, djb2 or crc32 of the corresponding bone name (all four checked against a real sample's names) - plausibly a per-node hash using some other algorithm, or an unrelated per-node id. Captured opaquely.
        """
        if self._should_write_hash_array:
            self._write_hash_array()
        if hasattr(self, '_m_hash_array'):
            return self._m_hash_array

        if not self.hash_array__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.hash_array_start)
        self._m_hash_array = self._io.read_bytes(self.hierarchy_size)
        self._io.seek(_pos)
        return getattr(self, '_m_hash_array', None)

    @hash_array.setter
    def hash_array(self, v):
        self._dirty = True
        self._m_hash_array = v

    def _write_hash_array(self):
        self._should_write_hash_array = False
        _pos = self._io.pos()
        self._io.seek(self.hash_array_start)
        self._io.write_bytes(self._m_hash_array)
        self._io.seek(_pos)

    @property
    def hash_array_start(self):
        if hasattr(self, '_m_hash_array_start'):
            return self._m_hash_array_start

        self._m_hash_array_start = 224 + self.e0_ofs_hash_array
        return getattr(self, '_m_hash_array_start', None)

    def _invalidate_hash_array_start(self):
        del self._m_hash_array_start
    @property
    def hierarchy_end(self):
        if hasattr(self, '_m_hierarchy_end'):
            return self._m_hierarchy_end

        self._m_hierarchy_end = 256 + self.hierarchy_size
        return getattr(self, '_m_hierarchy_end', None)

    def _invalidate_hierarchy_end(self):
        del self._m_hierarchy_end
    @property
    def hierarchy_padding(self):
        """The gap between the real hierarchy entries (node_count * 4 bytes) and hierarchy_end. NOT plain alignment padding - real, non-zero data on most files checked, the same 4-bytes-per-entry shape as `hierarchy` itself (plausible small node-index-like u16 pairs), just not accounted for by node_count. Purpose not identified - captured opaquely, same convention as edgemodel.ksy's own unattributed regions. Modeled as its own field (rather than left to `hierarchy`'s own declared size) so it round-trips at all: a Kaitai `seq` array's write only emits its real repeat-expr entries, never bytes beyond them.
        """
        if self._should_write_hierarchy_padding:
            self._write_hierarchy_padding()
        if hasattr(self, '_m_hierarchy_padding'):
            return self._m_hierarchy_padding

        if not self.hierarchy_padding__enabled:
            return None

        if self.hierarchy_size > self.node_count * 4:
            pass
            _pos = self._io.pos()
            self._io.seek(256 + self.node_count * 4)
            self._m_hierarchy_padding = self._io.read_bytes(self.hierarchy_size - self.node_count * 4)
            self._io.seek(_pos)

        return getattr(self, '_m_hierarchy_padding', None)

    @hierarchy_padding.setter
    def hierarchy_padding(self, v):
        self._dirty = True
        self._m_hierarchy_padding = v

    def _write_hierarchy_padding(self):
        self._should_write_hierarchy_padding = False
        if self.hierarchy_size > self.node_count * 4:
            pass
            _pos = self._io.pos()
            self._io.seek(256 + self.node_count * 4)
            self._io.write_bytes(self._m_hierarchy_padding)
            self._io.seek(_pos)


    @property
    def local_transforms(self):
        """Per-node bind-pose local transform (relative to the parent named in `hierarchy`), node_count entries of 48 bytes each - confirmed via an automated scan (unit-length quaternion, both trailing homogeneous w's exactly 1.0, verified against the following entry too to rule out a false positive) on the hand-checked samples, and the resulting recursively-composed world positions are a plausible humanoid bind pose (Y-up, confirmed by composing a real sample's full hierarchy - matches mesh.py's own (x, -z, y) game-to-Blender axis convention for vertex positions).
        """
        if self._should_write_local_transforms:
            self._write_local_transforms()
        if hasattr(self, '_m_local_transforms'):
            return self._m_local_transforms

        if not self.local_transforms__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.local_transforms_start)
        self._m_local_transforms = []
        for i in range(self.node_count):
            _t__m_local_transforms = HexaneSkel.LocalTrs(self._io, self, self._root)
            try:
                _t__m_local_transforms._read()
            finally:
                self._m_local_transforms.append(_t__m_local_transforms)

        self._io.seek(_pos)
        return getattr(self, '_m_local_transforms', None)

    @local_transforms.setter
    def local_transforms(self, v):
        self._dirty = True
        self._m_local_transforms = v

    def _write_local_transforms(self):
        self._should_write_local_transforms = False
        _pos = self._io.pos()
        self._io.seek(self.local_transforms_start)
        for i in range(len(self._m_local_transforms)):
            pass
            self._m_local_transforms[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def local_transforms_end(self):
        if hasattr(self, '_m_local_transforms_end'):
            return self._m_local_transforms_end

        self._m_local_transforms_end = self.local_transforms_start + self.node_count * 48
        return getattr(self, '_m_local_transforms_end', None)

    def _invalidate_local_transforms_end(self):
        del self._m_local_transforms_end
    @property
    def local_transforms_start(self):
        if hasattr(self, '_m_local_transforms_start'):
            return self._m_local_transforms_start

        self._m_local_transforms_start = 216 + self.d8_ofs_local_transforms
        return getattr(self, '_m_local_transforms_start', None)

    def _invalidate_local_transforms_start(self):
        del self._m_local_transforms_start
    @property
    def name_offsets(self):
        """Byte offset of each node's name within `names`, relative to the start of `names` - confirmed exactly cumulative (offsets[i] == sum of len(name)+1 for every earlier name) on all node_count entries across every file in the verified dataset, so `names` below is read directly as a sequential null-terminated array instead of via this table's own per-entry pos (this table is still modeled as real data for round-trip, same reasoning as edgemodel.ksy's materials_table.offsets).
        """
        if self._should_write_name_offsets:
            self._write_name_offsets()
        if hasattr(self, '_m_name_offsets'):
            return self._m_name_offsets

        if not self.name_offsets__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.name_offsets_start)
        self._m_name_offsets = []
        for i in range(self.node_count):
            self._m_name_offsets.append(self._io.read_u4le())

        self._io.seek(_pos)
        return getattr(self, '_m_name_offsets', None)

    @name_offsets.setter
    def name_offsets(self, v):
        self._dirty = True
        self._m_name_offsets = v

    def _write_name_offsets(self):
        self._should_write_name_offsets = False
        _pos = self._io.pos()
        self._io.seek(self.name_offsets_start)
        for i in range(len(self._m_name_offsets)):
            pass
            self._io.write_u4le(self._m_name_offsets[i])

        self._io.seek(_pos)

    @property
    def name_offsets_start(self):
        if hasattr(self, '_m_name_offsets_start'):
            return self._m_name_offsets_start

        self._m_name_offsets_start = 240 + self.f0_ofs_name_offsets
        return getattr(self, '_m_name_offsets_start', None)

    def _invalidate_name_offsets_start(self):
        del self._m_name_offsets_start
    @property
    def names(self):
        """node_count null-terminated ASCII bone names, one per `hierarchy`/ `local_transforms` entry in the same order (index 0 is always a root, e.g. a root bone name) - confirmed by cross-referencing name_offsets above exactly, and by real, character-appropriate bone names across both humanoid and creature rigs.
        """
        if self._should_write_names:
            self._write_names()
        if hasattr(self, '_m_names'):
            return self._m_names

        if not self.names__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.names_start)
        self._m_names = []
        for i in range(self.node_count):
            self._m_names.append((self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII"))

        self._io.seek(_pos)
        return getattr(self, '_m_names', None)

    @names.setter
    def names(self, v):
        self._dirty = True
        self._m_names = v

    def _write_names(self):
        self._should_write_names = False
        _pos = self._io.pos()
        self._io.seek(self.names_start)
        for i in range(len(self._m_names)):
            pass
            self._io.write_bytes((self._m_names[i]).encode(u"ASCII"))
            self._io.write_u1(0)

        self._io.seek(_pos)

    @property
    def names_start(self):
        if hasattr(self, '_m_names_start'):
            return self._m_names_start

        self._m_names_start = self.name_offsets_start + self.node_count * 4
        return getattr(self, '_m_names_start', None)

    def _invalidate_names_start(self):
        del self._m_names_start
    @property
    def parents(self):
        """The skeleton's own parent table: node_count u2 entries, one per `hierarchy`/`local_transforms`/`names` node in the same order, each the index of that node's parent in those same arrays. 0xffff marks a root - exactly one root (node 0) on every real character skeleton in the verified dataset, and every other entry is strictly less than its own node index, so world transforms compose in a single forward pass. Composing `local_transforms` through this table yields a coherent bind pose - a standing figure, mirrored left/right, feet at y ~ 0 and head at full character height - and matches the corresponding .edgemodel's own skinned geometry.
        """
        if self._should_write_parents:
            self._write_parents()
        if hasattr(self, '_m_parents'):
            return self._m_parents

        if not self.parents__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.local_transforms_end)
        self._m_parents = []
        for i in range(self.node_count):
            self._m_parents.append(self._io.read_u2le())

        self._io.seek(_pos)
        return getattr(self, '_m_parents', None)

    @parents.setter
    def parents(self, v):
        self._dirty = True
        self._m_parents = v

    def _write_parents(self):
        self._should_write_parents = False
        _pos = self._io.pos()
        self._io.seek(self.local_transforms_end)
        for i in range(len(self._m_parents)):
            pass
            self._io.write_u2le(self._m_parents[i])

        self._io.seek(_pos)

    @property
    def parents_end(self):
        if hasattr(self, '_m_parents_end'):
            return self._m_parents_end

        self._m_parents_end = self.local_transforms_end + self.node_count * 2
        return getattr(self, '_m_parents_end', None)

    def _invalidate_parents_end(self):
        del self._m_parents_end
    @property
    def parents_padding(self):
        """Zero padding from `parents`' real end up to name_offsets_start (round_up(node_count * 2, 16), confirmed via ec_ofs_u16_array_end / f0_ofs_name_offsets both resolving exactly as documented on those fields, across the verified dataset). Modeled as its own field so the file round-trips - see hierarchy_padding for the same reasoning.
        """
        if self._should_write_parents_padding:
            self._write_parents_padding()
        if hasattr(self, '_m_parents_padding'):
            return self._m_parents_padding

        if not self.parents_padding__enabled:
            return None

        if self.name_offsets_start > self.parents_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.parents_end)
            self._m_parents_padding = self._io.read_bytes(self.name_offsets_start - self.parents_end)
            self._io.seek(_pos)

        return getattr(self, '_m_parents_padding', None)

    @parents_padding.setter
    def parents_padding(self, v):
        self._dirty = True
        self._m_parents_padding = v

    def _write_parents_padding(self):
        self._should_write_parents_padding = False
        if self.name_offsets_start > self.parents_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.parents_end)
            self._io.write_bytes(self._m_parents_padding)
            self._io.seek(_pos)


    @property
    def pre_transforms_data(self):
        """Real (non-zero, non-constant) per-file data between the hierarchy array and local_transforms - NOT simply padding (sizes seen: 0, 16, 32, 48, 80, 96, 208, 224 bytes across the sweep, and its bytes decode as plausible small node-index-like u16 pairs on inspection). Purpose not identified; captured opaquely for round-trip, same convention as edgemodel.ksy's own unattributed regions.
        """
        if self._should_write_pre_transforms_data:
            self._write_pre_transforms_data()
        if hasattr(self, '_m_pre_transforms_data'):
            return self._m_pre_transforms_data

        if not self.pre_transforms_data__enabled:
            return None

        if self.local_transforms_start > self.hierarchy_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.hierarchy_end)
            self._m_pre_transforms_data = self._io.read_bytes(self.local_transforms_start - self.hierarchy_end)
            self._io.seek(_pos)

        return getattr(self, '_m_pre_transforms_data', None)

    @pre_transforms_data.setter
    def pre_transforms_data(self, v):
        self._dirty = True
        self._m_pre_transforms_data = v

    def _write_pre_transforms_data(self):
        self._should_write_pre_transforms_data = False
        if self.local_transforms_start > self.hierarchy_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.hierarchy_end)
            self._io.write_bytes(self._m_pre_transforms_data)
            self._io.seek(_pos)


    @property
    def trailing_padding(self):
        """Zero-filled alignment padding out to the file's own size (see body_size doc)."""
        if self._should_write_trailing_padding:
            self._write_trailing_padding()
        if hasattr(self, '_m_trailing_padding'):
            return self._m_trailing_padding

        if not self.trailing_padding__enabled:
            return None

        if self._io.size() > self.body_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.body_end)
            self._m_trailing_padding = self._io.read_bytes(self._io.size() - self.body_end)
            self._io.seek(_pos)

        return getattr(self, '_m_trailing_padding', None)

    @trailing_padding.setter
    def trailing_padding(self, v):
        self._dirty = True
        self._m_trailing_padding = v

    def _write_trailing_padding(self):
        self._should_write_trailing_padding = False
        if self._io.size() > self.body_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.body_end)
            if len(self._m_trailing_padding) != self._io.size() - self.body_end:
                raise kaitaistruct.ConsistencyError(u"trailing_padding", self._io.size() - self.body_end, len(self._m_trailing_padding))
            self._io.write_bytes(self._m_trailing_padding)
            self._io.seek(_pos)



