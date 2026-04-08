# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sbc21(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Sbc21, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Sbc21.SbcHeader(self._io, self, self._root)
        self.header._read()
        self.sbc_info = []
        for i in range(self.header.num_objects):
            _t_sbc_info = Sbc21.Info(self._io, self, self._root)
            try:
                _t_sbc_info._read()
            finally:
                self.sbc_info.append(_t_sbc_info)

        self.sbc_bvhc = []
        for i in range(self.header.num_objects):
            _t_sbc_bvhc = Sbc21.BvhCollision(self._io, self, self._root)
            try:
                _t_sbc_bvhc._read()
            finally:
                self.sbc_bvhc.append(_t_sbc_bvhc)

        self.bvh = Sbc21.BvhCollision(self._io, self, self._root)
        self.bvh._read()
        self.faces = []
        for i in range(self.header.num_faces):
            _t_faces = Sbc21.Face(self._io, self, self._root)
            try:
                _t_faces._read()
            finally:
                self.faces.append(_t_faces)

        self.vertices = []
        for i in range(self.header.num_vertices):
            _t_vertices = Sbc21.Vertex(self._io, self, self._root)
            try:
                _t_vertices._read()
            finally:
                self.vertices.append(_t_vertices)

        self.collision_types = []
        for i in range(self.header.num_stages):
            _t_collision_types = Sbc21.CollisionType(self._io, self, self._root)
            try:
                _t_collision_types._read()
            finally:
                self.collision_types.append(_t_collision_types)

        self.pairs_collections = []
        for i in range(self.header.num_pairs):
            _t_pairs_collections = Sbc21.SFacePair(self._io, self, self._root)
            try:
                _t_pairs_collections._read()
            finally:
                self.pairs_collections.append(_t_pairs_collections)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.sbc_info)):
            pass
            self.sbc_info[i]._fetch_instances()

        for i in range(len(self.sbc_bvhc)):
            pass
            self.sbc_bvhc[i]._fetch_instances()

        self.bvh._fetch_instances()
        for i in range(len(self.faces)):
            pass
            self.faces[i]._fetch_instances()

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._fetch_instances()

        for i in range(len(self.collision_types)):
            pass
            self.collision_types[i]._fetch_instances()

        for i in range(len(self.pairs_collections)):
            pass
            self.pairs_collections[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Sbc21, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.sbc_info)):
            pass
            self.sbc_info[i]._write__seq(self._io)

        for i in range(len(self.sbc_bvhc)):
            pass
            self.sbc_bvhc[i]._write__seq(self._io)

        self.bvh._write__seq(self._io)
        for i in range(len(self.faces)):
            pass
            self.faces[i]._write__seq(self._io)

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._write__seq(self._io)

        for i in range(len(self.collision_types)):
            pass
            self.collision_types[i]._write__seq(self._io)

        for i in range(len(self.pairs_collections)):
            pass
            self.pairs_collections[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.sbc_info) != self.header.num_objects:
            raise kaitaistruct.ConsistencyError(u"sbc_info", self.header.num_objects, len(self.sbc_info))
        for i in range(len(self.sbc_info)):
            pass
            if self.sbc_info[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self._root, self.sbc_info[i]._root)
            if self.sbc_info[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self, self.sbc_info[i]._parent)

        if len(self.sbc_bvhc) != self.header.num_objects:
            raise kaitaistruct.ConsistencyError(u"sbc_bvhc", self.header.num_objects, len(self.sbc_bvhc))
        for i in range(len(self.sbc_bvhc)):
            pass
            if self.sbc_bvhc[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sbc_bvhc", self._root, self.sbc_bvhc[i]._root)
            if self.sbc_bvhc[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sbc_bvhc", self, self.sbc_bvhc[i]._parent)

        if self.bvh._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bvh", self._root, self.bvh._root)
        if self.bvh._parent != self:
            raise kaitaistruct.ConsistencyError(u"bvh", self, self.bvh._parent)
        if len(self.faces) != self.header.num_faces:
            raise kaitaistruct.ConsistencyError(u"faces", self.header.num_faces, len(self.faces))
        for i in range(len(self.faces)):
            pass
            if self.faces[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"faces", self._root, self.faces[i]._root)
            if self.faces[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"faces", self, self.faces[i]._parent)

        if len(self.vertices) != self.header.num_vertices:
            raise kaitaistruct.ConsistencyError(u"vertices", self.header.num_vertices, len(self.vertices))
        for i in range(len(self.vertices)):
            pass
            if self.vertices[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vertices", self._root, self.vertices[i]._root)
            if self.vertices[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vertices", self, self.vertices[i]._parent)

        if len(self.collision_types) != self.header.num_stages:
            raise kaitaistruct.ConsistencyError(u"collision_types", self.header.num_stages, len(self.collision_types))
        for i in range(len(self.collision_types)):
            pass
            if self.collision_types[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"collision_types", self._root, self.collision_types[i]._root)
            if self.collision_types[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"collision_types", self, self.collision_types[i]._parent)

        if len(self.pairs_collections) != self.header.num_pairs:
            raise kaitaistruct.ConsistencyError(u"pairs_collections", self.header.num_pairs, len(self.pairs_collections))
        for i in range(len(self.pairs_collections)):
            pass
            if self.pairs_collections[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pairs_collections", self._root, self.pairs_collections[i]._root)
            if self.pairs_collections[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"pairs_collections", self, self.pairs_collections[i]._parent)

        self._dirty = False

    class AabbBlock(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.AabbBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = []
            for i in range(4):
                self.x.append(self._io.read_f4le())

            self.y = []
            for i in range(4):
                self.y.append(self._io.read_f4le())

            self.z = []
            for i in range(4):
                self.z.append(self._io.read_f4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.x)):
                pass

            for i in range(len(self.y)):
                pass

            for i in range(len(self.z)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.AabbBlock, self)._write__seq(io)
            for i in range(len(self.x)):
                pass
                self._io.write_f4le(self.x[i])

            for i in range(len(self.y)):
                pass
                self._io.write_f4le(self.y[i])

            for i in range(len(self.z)):
                pass
                self._io.write_f4le(self.z[i])



        def _check(self):
            if len(self.x) != 4:
                raise kaitaistruct.ConsistencyError(u"x", 4, len(self.x))
            for i in range(len(self.x)):
                pass

            if len(self.y) != 4:
                raise kaitaistruct.ConsistencyError(u"y", 4, len(self.y))
            for i in range(len(self.y)):
                pass

            if len(self.z) != 4:
                raise kaitaistruct.ConsistencyError(u"z", 4, len(self.z))
            for i in range(len(self.z)):
                pass

            self._dirty = False


    class Bbox4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.Bbox4, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = []
            for i in range(4):
                self.min.append(self._io.read_f4le())

            self.max = []
            for i in range(4):
                self.max.append(self._io.read_f4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.min)):
                pass

            for i in range(len(self.max)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.Bbox4, self)._write__seq(io)
            for i in range(len(self.min)):
                pass
                self._io.write_f4le(self.min[i])

            for i in range(len(self.max)):
                pass
                self._io.write_f4le(self.max[i])



        def _check(self):
            if len(self.min) != 4:
                raise kaitaistruct.ConsistencyError(u"min", 4, len(self.min))
            for i in range(len(self.min)):
                pass

            if len(self.max) != 4:
                raise kaitaistruct.ConsistencyError(u"max", 4, len(self.max))
            for i in range(len(self.max)):
                pass

            self._dirty = False


    class BvhCollision(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.BvhCollision, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bvhc = []
            for i in range(2):
                self.bvhc.append(self._io.read_u4le())

            self.soh = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.bounding_box = Sbc21.Bbox4(self._io, self, self._root)
            self.bounding_box._read()
            self.num_nodes = self._io.read_u4le()
            self.nulls = []
            for i in range(3):
                self.nulls.append(self._io.read_u4le())

            self.nodes = []
            for i in range(self.num_nodes):
                _t_nodes = Sbc21.BvhNode(self._io, self, self._root)
                try:
                    _t_nodes._read()
                finally:
                    self.nodes.append(_t_nodes)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.bvhc)):
                pass

            self.bounding_box._fetch_instances()
            for i in range(len(self.nulls)):
                pass

            for i in range(len(self.nodes)):
                pass
                self.nodes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Sbc21.BvhCollision, self)._write__seq(io)
            for i in range(len(self.bvhc)):
                pass
                self._io.write_u4le(self.bvhc[i])

            self._io.write_u4le(self.soh)
            self._io.write_u4le(self.unk_01)
            self.bounding_box._write__seq(self._io)
            self._io.write_u4le(self.num_nodes)
            for i in range(len(self.nulls)):
                pass
                self._io.write_u4le(self.nulls[i])

            for i in range(len(self.nodes)):
                pass
                self.nodes[i]._write__seq(self._io)



        def _check(self):
            if len(self.bvhc) != 2:
                raise kaitaistruct.ConsistencyError(u"bvhc", 2, len(self.bvhc))
            for i in range(len(self.bvhc)):
                pass

            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self._root, self.bounding_box._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self, self.bounding_box._parent)
            if len(self.nulls) != 3:
                raise kaitaistruct.ConsistencyError(u"nulls", 3, len(self.nulls))
            for i in range(len(self.nulls)):
                pass

            if len(self.nodes) != self.num_nodes:
                raise kaitaistruct.ConsistencyError(u"nodes", self.num_nodes, len(self.nodes))
            for i in range(len(self.nodes)):
                pass
                if self.nodes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"nodes", self._root, self.nodes[i]._root)
                if self.nodes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"nodes", self, self.nodes[i]._parent)

            self._dirty = False


    class BvhNode(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.BvhNode, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.node_type = []
            for i in range(4):
                self.node_type.append(self._io.read_u1())

            self.node_id = []
            for i in range(4):
                self.node_id.append(self._io.read_u2le())

            self.unk_05 = self._io.read_u4le()
            self.min_aabb = Sbc21.AabbBlock(self._io, self, self._root)
            self.min_aabb._read()
            self.max_aabb = Sbc21.AabbBlock(self._io, self, self._root)
            self.max_aabb._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.node_type)):
                pass

            for i in range(len(self.node_id)):
                pass

            self.min_aabb._fetch_instances()
            self.max_aabb._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc21.BvhNode, self)._write__seq(io)
            for i in range(len(self.node_type)):
                pass
                self._io.write_u1(self.node_type[i])

            for i in range(len(self.node_id)):
                pass
                self._io.write_u2le(self.node_id[i])

            self._io.write_u4le(self.unk_05)
            self.min_aabb._write__seq(self._io)
            self.max_aabb._write__seq(self._io)


        def _check(self):
            if len(self.node_type) != 4:
                raise kaitaistruct.ConsistencyError(u"node_type", 4, len(self.node_type))
            for i in range(len(self.node_type)):
                pass

            if len(self.node_id) != 4:
                raise kaitaistruct.ConsistencyError(u"node_id", 4, len(self.node_id))
            for i in range(len(self.node_id)):
                pass

            if self.min_aabb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min_aabb", self._root, self.min_aabb._root)
            if self.min_aabb._parent != self:
                raise kaitaistruct.ConsistencyError(u"min_aabb", self, self.min_aabb._parent)
            if self.max_aabb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max_aabb", self._root, self.max_aabb._root)
            if self.max_aabb._parent != self:
                raise kaitaistruct.ConsistencyError(u"max_aabb", self, self.max_aabb._parent)
            self._dirty = False


    class CollisionType(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.CollisionType, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_01 = self._io.read_f4le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u2le()
            self.unk_04 = []
            for i in range(3):
                self.unk_04.append(self._io.read_u4le())

            self.jp_path = []
            for i in range(12):
                self.jp_path.append(self._io.read_u1())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_04)):
                pass

            for i in range(len(self.jp_path)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.CollisionType, self)._write__seq(io)
            self._io.write_f4le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u2le(self.unk_03)
            for i in range(len(self.unk_04)):
                pass
                self._io.write_u4le(self.unk_04[i])

            for i in range(len(self.jp_path)):
                pass
                self._io.write_u1(self.jp_path[i])



        def _check(self):
            if len(self.unk_04) != 3:
                raise kaitaistruct.ConsistencyError(u"unk_04", 3, len(self.unk_04))
            for i in range(len(self.unk_04)):
                pass

            if len(self.jp_path) != 12:
                raise kaitaistruct.ConsistencyError(u"jp_path", 12, len(self.jp_path))
            for i in range(len(self.jp_path)):
                pass

            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.Face, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.normal = []
            for i in range(3):
                self.normal.append(self._io.read_f4le())

            self.vert = []
            for i in range(3):
                self.vert.append(self._io.read_u2le())

            self.type = self._io.read_u2le()
            self.nulls = self._io.read_u4le()
            self.adjacent = []
            for i in range(3):
                self.adjacent.append(self._io.read_u1())

            self.nulls_01 = self._io.read_u1()
            self.nulls_02 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.normal)):
                pass

            for i in range(len(self.vert)):
                pass

            for i in range(len(self.adjacent)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.Face, self)._write__seq(io)
            for i in range(len(self.normal)):
                pass
                self._io.write_f4le(self.normal[i])

            for i in range(len(self.vert)):
                pass
                self._io.write_u2le(self.vert[i])

            self._io.write_u2le(self.type)
            self._io.write_u4le(self.nulls)
            for i in range(len(self.adjacent)):
                pass
                self._io.write_u1(self.adjacent[i])

            self._io.write_u1(self.nulls_01)
            self._io.write_u4le(self.nulls_02)


        def _check(self):
            if len(self.normal) != 3:
                raise kaitaistruct.ConsistencyError(u"normal", 3, len(self.normal))
            for i in range(len(self.normal)):
                pass

            if len(self.vert) != 3:
                raise kaitaistruct.ConsistencyError(u"vert", 3, len(self.vert))
            for i in range(len(self.vert)):
                pass

            if len(self.adjacent) != 3:
                raise kaitaistruct.ConsistencyError(u"adjacent", 3, len(self.adjacent))
            for i in range(len(self.adjacent)):
                pass

            self._dirty = False


    class Info(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.Info, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bounding_box = Sbc21.Bbox4(self._io, self, self._root)
            self.bounding_box._read()
            self.unk_01 = self._io.read_u4le()
            self.nulls_01 = []
            for i in range(2):
                self.nulls_01.append(self._io.read_u4le())

            self.start_pairs = self._io.read_u4le()
            self.num_pairs = self._io.read_u4le()
            self.start_faces = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.start_vertices = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.index_id = self._io.read_u4le()
            self.nulls_02 = []
            for i in range(2):
                self.nulls_02.append(self._io.read_u4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            self.bounding_box._fetch_instances()
            for i in range(len(self.nulls_01)):
                pass

            for i in range(len(self.nulls_02)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.Info, self)._write__seq(io)
            self.bounding_box._write__seq(self._io)
            self._io.write_u4le(self.unk_01)
            for i in range(len(self.nulls_01)):
                pass
                self._io.write_u4le(self.nulls_01[i])

            self._io.write_u4le(self.start_pairs)
            self._io.write_u4le(self.num_pairs)
            self._io.write_u4le(self.start_faces)
            self._io.write_u4le(self.num_faces)
            self._io.write_u4le(self.start_vertices)
            self._io.write_u4le(self.num_vertices)
            self._io.write_u4le(self.index_id)
            for i in range(len(self.nulls_02)):
                pass
                self._io.write_u4le(self.nulls_02[i])



        def _check(self):
            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self._root, self.bounding_box._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self, self.bounding_box._parent)
            if len(self.nulls_01) != 2:
                raise kaitaistruct.ConsistencyError(u"nulls_01", 2, len(self.nulls_01))
            for i in range(len(self.nulls_01)):
                pass

            if len(self.nulls_02) != 2:
                raise kaitaistruct.ConsistencyError(u"nulls_02", 2, len(self.nulls_02))
            for i in range(len(self.nulls_02)):
                pass

            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 80
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class SFacePair(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.SFacePair, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.face_01 = self._io.read_u2le()
            self.face_02 = self._io.read_u2le()
            self.quad_order = []
            for i in range(4):
                self.quad_order.append(self._io.read_u1())

            self.type = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.quad_order)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.SFacePair, self)._write__seq(io)
            self._io.write_u2le(self.face_01)
            self._io.write_u2le(self.face_02)
            for i in range(len(self.quad_order)):
                pass
                self._io.write_u1(self.quad_order[i])

            self._io.write_u2le(self.type)


        def _check(self):
            if len(self.quad_order) != 4:
                raise kaitaistruct.ConsistencyError(u"quad_order", 4, len(self.quad_order))
            for i in range(len(self.quad_order)):
                pass

            self._dirty = False


    class SbcHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.SbcHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.indent = self._io.read_bytes(4)
            if not self.indent == b"\x53\x42\x43\xFF":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\xFF", self.indent, self._io, u"/types/sbc_header/seq/0")
            self.unk_00 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            self.num_objects = self._io.read_u2le()
            self.num_stages = self._io.read_u2le()
            self.num_pairs = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.nulls = []
            for i in range(4):
                self.nulls.append(self._io.read_u4le())

            self.bounding_box = Sbc21.Bbox4(self._io, self, self._root)
            self.bounding_box._read()
            self.bb_size = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.nulls)):
                pass

            self.bounding_box._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc21.SbcHeader, self)._write__seq(io)
            self._io.write_bytes(self.indent)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.unk_02)
            self._io.write_u4le(self.unk_03)
            self._io.write_u2le(self.num_objects)
            self._io.write_u2le(self.num_stages)
            self._io.write_u4le(self.num_pairs)
            self._io.write_u4le(self.num_faces)
            self._io.write_u4le(self.num_vertices)
            for i in range(len(self.nulls)):
                pass
                self._io.write_u4le(self.nulls[i])

            self.bounding_box._write__seq(self._io)
            self._io.write_u4le(self.bb_size)


        def _check(self):
            if len(self.indent) != 4:
                raise kaitaistruct.ConsistencyError(u"indent", 4, len(self.indent))
            if not self.indent == b"\x53\x42\x43\xFF":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\xFF", self.indent, None, u"/types/sbc_header/seq/0")
            if len(self.nulls) != 4:
                raise kaitaistruct.ConsistencyError(u"nulls", 4, len(self.nulls))
            for i in range(len(self.nulls)):
                pass

            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self._root, self.bounding_box._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self, self.bounding_box._parent)
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 84
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc21.Vertex, self).__init__(_io)
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
            super(Sbc21.Vertex, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False



