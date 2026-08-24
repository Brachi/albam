# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneSkel(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        super(HexaneSkel, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

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
        self.dc_ofs_post_transforms = self._io.read_u4le()
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
            self.hierarchy.append(HexaneSkel.HierarchyEntry(self._io, self, self._root))



    def _fetch_instances(self):
        pass
        for i in range(len(self.hierarchy)):
            pass
            self.hierarchy[i]._fetch_instances()

        _ = self.hash_array
        if hasattr(self, '_m_hash_array'):
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


        _ = self.post_transforms_data
        if hasattr(self, '_m_post_transforms_data'):
            pass

        _ = self.pre_transforms_data
        if hasattr(self, '_m_pre_transforms_data'):
            pass

        _ = self.trailing_padding
        if hasattr(self, '_m_trailing_padding'):
            pass


    class HierarchyEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(HexaneSkel.HierarchyEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.sort_key = self._io.read_u2le()
            self.parent_raw = self._io.read_u2le()


        def _fetch_instances(self):
            pass

        @property
        def is_root(self):
            if hasattr(self, '_m_is_root'):
                return self._m_is_root

            self._m_is_root = self.parent_raw == 65535
            return getattr(self, '_m_is_root', None)

        @property
        def parent_flag(self):
            """Unattributed - see parent_raw's own doc."""
            if hasattr(self, '_m_parent_flag'):
                return self._m_parent_flag

            self._m_parent_flag = self.parent_raw & 32768 != 0
            return getattr(self, '_m_parent_flag', None)

        @property
        def parent_index(self):
            """Real parent node index into this same hierarchy/local_transforms/ names array, or -1 for a root. Every real file checked has every parent_index < its own node index (safe to resolve/compose world transforms in a single forward pass).
            """
            if hasattr(self, '_m_parent_index'):
                return self._m_parent_index

            self._m_parent_index = (-1 if self.is_root else self.parent_raw & 32767)
            return getattr(self, '_m_parent_index', None)


    class LocalTrs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(HexaneSkel.LocalTrs, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.rotation = HexaneSkel.Vec4f(self._io, self, self._root)
            self.position = HexaneSkel.Vec4f(self._io, self, self._root)
            self.scale = HexaneSkel.Vec4f(self._io, self, self._root)


        def _fetch_instances(self):
            pass
            self.rotation._fetch_instances()
            self.position._fetch_instances()
            self.scale._fetch_instances()


    class Vec4f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(HexaneSkel.Vec4f, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


        def _fetch_instances(self):
            pass


    @property
    def body_end(self):
        if hasattr(self, '_m_body_end'):
            return self._m_body_end

        self._m_body_end = 192 + self.total
        return getattr(self, '_m_body_end', None)

    @property
    def hash_array(self):
        """node_count u32 values (hierarchy_size bytes total, same round-up-to-16 formula as `hierarchy`), immediately followed by body_end with no further gap (confirmed across the verified dataset: hash_array_start rounds `names`' real end up to the next 16-byte ABSOLUTE file boundary, not a names-blob-relative one, and hash_array_start + hierarchy_size == body_end exactly on every file). Values don't match fnv1, fnv1a, djb2 or crc32 of the corresponding bone name (all four checked against a real sample's names) - plausibly a per-node hash using some other algorithm, or an unrelated per-node id. Captured opaquely.
        """
        if hasattr(self, '_m_hash_array'):
            return self._m_hash_array

        _pos = self._io.pos()
        self._io.seek(self.hash_array_start)
        self._m_hash_array = self._io.read_bytes(self.hierarchy_size)
        self._io.seek(_pos)
        return getattr(self, '_m_hash_array', None)

    @property
    def hash_array_start(self):
        if hasattr(self, '_m_hash_array_start'):
            return self._m_hash_array_start

        self._m_hash_array_start = 224 + self.e0_ofs_hash_array
        return getattr(self, '_m_hash_array_start', None)

    @property
    def hierarchy_end(self):
        if hasattr(self, '_m_hierarchy_end'):
            return self._m_hierarchy_end

        self._m_hierarchy_end = 256 + self.hierarchy_size
        return getattr(self, '_m_hierarchy_end', None)

    @property
    def local_transforms(self):
        """Per-node bind-pose local transform (relative to the parent named in `hierarchy`), node_count entries of 48 bytes each - confirmed via an automated scan (unit-length quaternion, both trailing homogeneous w's exactly 1.0, verified against the following entry too to rule out a false positive) on the hand-checked samples, and the resulting recursively-composed world positions are a plausible humanoid bind pose (Y-up, confirmed by composing a real sample's full hierarchy - matches mesh.py's own (x, -z, y) game-to-Blender axis convention for vertex positions).
        """
        if hasattr(self, '_m_local_transforms'):
            return self._m_local_transforms

        _pos = self._io.pos()
        self._io.seek(self.local_transforms_start)
        self._m_local_transforms = []
        for i in range(self.node_count):
            self._m_local_transforms.append(HexaneSkel.LocalTrs(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_local_transforms', None)

    @property
    def local_transforms_end(self):
        if hasattr(self, '_m_local_transforms_end'):
            return self._m_local_transforms_end

        self._m_local_transforms_end = self.local_transforms_start + self.node_count * 48
        return getattr(self, '_m_local_transforms_end', None)

    @property
    def local_transforms_start(self):
        if hasattr(self, '_m_local_transforms_start'):
            return self._m_local_transforms_start

        self._m_local_transforms_start = 216 + self.d8_ofs_local_transforms
        return getattr(self, '_m_local_transforms_start', None)

    @property
    def name_offsets(self):
        """Byte offset of each node's name within `names`, relative to the start of `names` - confirmed exactly cumulative (offsets[i] == sum of len(name)+1 for every earlier name) on all node_count entries across every file in the verified dataset, so `names` below is read directly as a sequential null-terminated array instead of via this table's own per-entry pos (this table is still modeled as real data for round-trip, same reasoning as edgemodel.ksy's materials_table.offsets).
        """
        if hasattr(self, '_m_name_offsets'):
            return self._m_name_offsets

        _pos = self._io.pos()
        self._io.seek(self.name_offsets_start)
        self._m_name_offsets = []
        for i in range(self.node_count):
            self._m_name_offsets.append(self._io.read_u4le())

        self._io.seek(_pos)
        return getattr(self, '_m_name_offsets', None)

    @property
    def name_offsets_start(self):
        if hasattr(self, '_m_name_offsets_start'):
            return self._m_name_offsets_start

        self._m_name_offsets_start = 240 + self.f0_ofs_name_offsets
        return getattr(self, '_m_name_offsets_start', None)

    @property
    def names(self):
        """node_count null-terminated ASCII bone names, one per `hierarchy`/ `local_transforms` entry in the same order (index 0 is always a root, e.g. a root bone name) - confirmed by cross-referencing name_offsets above exactly, and by real, character-appropriate bone names across both humanoid and creature rigs.
        """
        if hasattr(self, '_m_names'):
            return self._m_names

        _pos = self._io.pos()
        self._io.seek(self.names_start)
        self._m_names = []
        for i in range(self.node_count):
            self._m_names.append((self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII"))

        self._io.seek(_pos)
        return getattr(self, '_m_names', None)

    @property
    def names_start(self):
        if hasattr(self, '_m_names_start'):
            return self._m_names_start

        self._m_names_start = self.name_offsets_start + self.node_count * 4
        return getattr(self, '_m_names_start', None)

    @property
    def post_transforms_data(self):
        """Contains an implicit node_count * 2 byte u16 array right after local_transforms (values loosely increasing but not strictly monotonic per node - possibly a hash-bucket/sort order artifact, not identified), padded with zeros up to name_offsets_start (round_up(node_count * 2, 16), confirmed via ec_ofs_u16_array_end / f0_ofs_name_offsets both resolving exactly as documented on those fields, across the verified dataset). Captured opaquely as one blob rather than split into the u16 array + its padding, since the array's own semantics aren't confirmed.
        """
        if hasattr(self, '_m_post_transforms_data'):
            return self._m_post_transforms_data

        if self.name_offsets_start > self.local_transforms_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.local_transforms_end)
            self._m_post_transforms_data = self._io.read_bytes(self.name_offsets_start - self.local_transforms_end)
            self._io.seek(_pos)

        return getattr(self, '_m_post_transforms_data', None)

    @property
    def pre_transforms_data(self):
        """Real (non-zero, non-constant) per-file data between the hierarchy array and local_transforms - NOT simply padding (sizes seen: 0, 16, 32, 48, 80, 96, 208, 224 bytes across the sweep, and its bytes decode as plausible small node-index-like u16 pairs on inspection). Purpose not identified; captured opaquely for round-trip, same convention as edgemodel.ksy's own unattributed regions.
        """
        if hasattr(self, '_m_pre_transforms_data'):
            return self._m_pre_transforms_data

        if self.local_transforms_start > self.hierarchy_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.hierarchy_end)
            self._m_pre_transforms_data = self._io.read_bytes(self.local_transforms_start - self.hierarchy_end)
            self._io.seek(_pos)

        return getattr(self, '_m_pre_transforms_data', None)

    @property
    def trailing_padding(self):
        """Zero-filled alignment padding out to the file's own size (see body_size doc)."""
        if hasattr(self, '_m_trailing_padding'):
            return self._m_trailing_padding

        if self._io.size() > self.body_end:
            pass
            _pos = self._io.pos()
            self._io.seek(self.body_end)
            self._m_trailing_padding = self._io.read_bytes(self._io.size() - self.body_end)
            self._io.seek(_pos)

        return getattr(self, '_m_trailing_padding', None)


