# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sbc21(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.header = Sbc21.SbcHeader(self._io, self, self._root)
        self.header._read()
        self.sbc_info = []
        for i in range(self.header.object_count):
            _t_sbc_info = Sbc21.Info(self._io, self, self._root)
            _t_sbc_info._read()
            self.sbc_info.append(_t_sbc_info)

        self.sbc_bvhc = []
        for i in range(self.header.object_count):
            _t_sbc_bvhc = Sbc21.BvhCollision(self._io, self, self._root)
            _t_sbc_bvhc._read()
            self.sbc_bvhc.append(_t_sbc_bvhc)

        self.bvh = Sbc21.BvhCollision(self._io, self, self._root)
        self.bvh._read()
        self.faces = []
        for i in range(self.header.face_count):
            _t_faces = Sbc21.Face(self._io, self, self._root)
            _t_faces._read()
            self.faces.append(_t_faces)

        self.vertices = []
        for i in range(self.header.vertex_count):
            _t_vertices = Sbc21.Vertex(self._io, self, self._root)
            _t_vertices._read()
            self.vertices.append(_t_vertices)

        self.collision_types = []
        for i in range(self.header.stage_count):
            _t_collision_types = Sbc21.CollisionType(self._io, self, self._root)
            _t_collision_types._read()
            self.collision_types.append(_t_collision_types)

        self.pairs_collections = []
        for i in range(self.header.pair_count):
            _t_pairs_collections = Sbc21.SFacePair(self._io, self, self._root)
            _t_pairs_collections._read()
            self.pairs_collections.append(_t_pairs_collections)



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
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)
        if (len(self.sbc_info) != self.header.object_count):
            raise kaitaistruct.ConsistencyError(u"sbc_info", len(self.sbc_info), self.header.object_count)
        for i in range(len(self.sbc_info)):
            pass
            if self.sbc_info[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self.sbc_info[i]._root, self._root)
            if self.sbc_info[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self.sbc_info[i]._parent, self)

        if (len(self.sbc_bvhc) != self.header.object_count):
            raise kaitaistruct.ConsistencyError(u"sbc_bvhc", len(self.sbc_bvhc), self.header.object_count)
        for i in range(len(self.sbc_bvhc)):
            pass
            if self.sbc_bvhc[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sbc_bvhc", self.sbc_bvhc[i]._root, self._root)
            if self.sbc_bvhc[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sbc_bvhc", self.sbc_bvhc[i]._parent, self)

        if self.bvh._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bvh", self.bvh._root, self._root)
        if self.bvh._parent != self:
            raise kaitaistruct.ConsistencyError(u"bvh", self.bvh._parent, self)
        if (len(self.faces) != self.header.face_count):
            raise kaitaistruct.ConsistencyError(u"faces", len(self.faces), self.header.face_count)
        for i in range(len(self.faces)):
            pass
            if self.faces[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"faces", self.faces[i]._root, self._root)
            if self.faces[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"faces", self.faces[i]._parent, self)

        if (len(self.vertices) != self.header.vertex_count):
            raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), self.header.vertex_count)
        for i in range(len(self.vertices)):
            pass
            if self.vertices[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
            if self.vertices[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)

        if (len(self.collision_types) != self.header.stage_count):
            raise kaitaistruct.ConsistencyError(u"collision_types", len(self.collision_types), self.header.stage_count)
        for i in range(len(self.collision_types)):
            pass
            if self.collision_types[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"collision_types", self.collision_types[i]._root, self._root)
            if self.collision_types[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"collision_types", self.collision_types[i]._parent, self)

        if (len(self.pairs_collections) != self.header.pair_count):
            raise kaitaistruct.ConsistencyError(u"pairs_collections", len(self.pairs_collections), self.header.pair_count)
        for i in range(len(self.pairs_collections)):
            pass
            if self.pairs_collections[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pairs_collections", self.pairs_collections[i]._root, self._root)
            if self.pairs_collections[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"pairs_collections", self.pairs_collections[i]._parent, self)


    class Vertex(ReadWriteKaitaiStruct):
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
            super(Sbc21.Vertex, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class Bbox(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = []
            for i in range(4):
                self.min.append(self._io.read_f4le())

            self.max = []
            for i in range(4):
                self.max.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.min)):
                pass

            for i in range(len(self.max)):
                pass



        def _write__seq(self, io=None):
            super(Sbc21.Bbox, self)._write__seq(io)
            for i in range(len(self.min)):
                pass
                self._io.write_f4le(self.min[i])

            for i in range(len(self.max)):
                pass
                self._io.write_f4le(self.max[i])



        def _check(self):
            pass
            if (len(self.min) != 4):
                raise kaitaistruct.ConsistencyError(u"min", len(self.min), 4)
            for i in range(len(self.min)):
                pass

            if (len(self.max) != 4):
                raise kaitaistruct.ConsistencyError(u"max", len(self.max), 4)
            for i in range(len(self.max)):
                pass



    class CollisionType(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
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
            pass
            if (len(self.unk_04) != 3):
                raise kaitaistruct.ConsistencyError(u"unk_04", len(self.unk_04), 3)
            for i in range(len(self.unk_04)):
                pass

            if (len(self.jp_path) != 12):
                raise kaitaistruct.ConsistencyError(u"jp_path", len(self.jp_path), 12)
            for i in range(len(self.jp_path)):
                pass



    class AabbBlock(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
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
            pass
            if (len(self.x) != 4):
                raise kaitaistruct.ConsistencyError(u"x", len(self.x), 4)
            for i in range(len(self.x)):
                pass

            if (len(self.y) != 4):
                raise kaitaistruct.ConsistencyError(u"y", len(self.y), 4)
            for i in range(len(self.y)):
                pass

            if (len(self.z) != 4):
                raise kaitaistruct.ConsistencyError(u"z", len(self.z), 4)
            for i in range(len(self.z)):
                pass



    class Info(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bounding_box = Sbc21.Bbox(self._io, self, self._root)
            self.bounding_box._read()
            self.unk_01 = self._io.read_u4le()
            self.nulls_01 = []
            for i in range(2):
                self.nulls_01.append(self._io.read_u4le())

            self.pairs_start = self._io.read_u4le()
            self.pairs_count = self._io.read_u4le()
            self.faces_start = self._io.read_u4le()
            self.face_count = self._io.read_u4le()
            self.vertex_start = self._io.read_u4le()
            self.vertex_count = self._io.read_u4le()
            self.index_id = self._io.read_u4le()
            self.nulls_02 = []
            for i in range(2):
                self.nulls_02.append(self._io.read_u4le())



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

            self._io.write_u4le(self.pairs_start)
            self._io.write_u4le(self.pairs_count)
            self._io.write_u4le(self.faces_start)
            self._io.write_u4le(self.face_count)
            self._io.write_u4le(self.vertex_start)
            self._io.write_u4le(self.vertex_count)
            self._io.write_u4le(self.index_id)
            for i in range(len(self.nulls_02)):
                pass
                self._io.write_u4le(self.nulls_02[i])



        def _check(self):
            pass
            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self.bounding_box._root, self._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self.bounding_box._parent, self)
            if (len(self.nulls_01) != 2):
                raise kaitaistruct.ConsistencyError(u"nulls_01", len(self.nulls_01), 2)
            for i in range(len(self.nulls_01)):
                pass

            if (len(self.nulls_02) != 2):
                raise kaitaistruct.ConsistencyError(u"nulls_02", len(self.nulls_02), 2)
            for i in range(len(self.nulls_02)):
                pass



    class SFacePair(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.face_01 = self._io.read_u2le()
            self.face_02 = self._io.read_u2le()
            self.quad_order = []
            for i in range(4):
                self.quad_order.append(self._io.read_u1())

            self.type = self._io.read_u2le()


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
            pass
            if (len(self.quad_order) != 4):
                raise kaitaistruct.ConsistencyError(u"quad_order", len(self.quad_order), 4)
            for i in range(len(self.quad_order)):
                pass



    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
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
            pass
            if (len(self.normal) != 3):
                raise kaitaistruct.ConsistencyError(u"normal", len(self.normal), 3)
            for i in range(len(self.normal)):
                pass

            if (len(self.vert) != 3):
                raise kaitaistruct.ConsistencyError(u"vert", len(self.vert), 3)
            for i in range(len(self.vert)):
                pass

            if (len(self.adjacent) != 3):
                raise kaitaistruct.ConsistencyError(u"adjacent", len(self.adjacent), 3)
            for i in range(len(self.adjacent)):
                pass



    class BvhNode(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
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
            pass
            if (len(self.node_type) != 4):
                raise kaitaistruct.ConsistencyError(u"node_type", len(self.node_type), 4)
            for i in range(len(self.node_type)):
                pass

            if (len(self.node_id) != 4):
                raise kaitaistruct.ConsistencyError(u"node_id", len(self.node_id), 4)
            for i in range(len(self.node_id)):
                pass

            if self.min_aabb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min_aabb", self.min_aabb._root, self._root)
            if self.min_aabb._parent != self:
                raise kaitaistruct.ConsistencyError(u"min_aabb", self.min_aabb._parent, self)
            if self.max_aabb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max_aabb", self.max_aabb._root, self._root)
            if self.max_aabb._parent != self:
                raise kaitaistruct.ConsistencyError(u"max_aabb", self.max_aabb._parent, self)


    class BvhCollision(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bvhc = []
            for i in range(2):
                self.bvhc.append(self._io.read_u4le())

            self.soh = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.bounding_box = Sbc21.Bbox(self._io, self, self._root)
            self.bounding_box._read()
            self.node_count = self._io.read_u4le()
            self.nulls = []
            for i in range(3):
                self.nulls.append(self._io.read_u4le())

            self.nodes = []
            for i in range(self.node_count):
                _t_nodes = Sbc21.BvhNode(self._io, self, self._root)
                _t_nodes._read()
                self.nodes.append(_t_nodes)



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
            self._io.write_u4le(self.node_count)
            for i in range(len(self.nulls)):
                pass
                self._io.write_u4le(self.nulls[i])

            for i in range(len(self.nodes)):
                pass
                self.nodes[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.bvhc) != 2):
                raise kaitaistruct.ConsistencyError(u"bvhc", len(self.bvhc), 2)
            for i in range(len(self.bvhc)):
                pass

            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self.bounding_box._root, self._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self.bounding_box._parent, self)
            if (len(self.nulls) != 3):
                raise kaitaistruct.ConsistencyError(u"nulls", len(self.nulls), 3)
            for i in range(len(self.nulls)):
                pass

            if (len(self.nodes) != self.node_count):
                raise kaitaistruct.ConsistencyError(u"nodes", len(self.nodes), self.node_count)
            for i in range(len(self.nodes)):
                pass
                if self.nodes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"nodes", self.nodes[i]._root, self._root)
                if self.nodes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"nodes", self.nodes[i]._parent, self)



    class SbcHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not (self.magic == b"\x53\x42\x43\xFF"):
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\xFF", self.magic, self._io, u"/types/sbc_header/seq/0")
            self.unk_00 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            self.object_count = self._io.read_u2le()
            self.stage_count = self._io.read_u2le()
            self.pair_count = self._io.read_u4le()
            self.face_count = self._io.read_u4le()
            self.vertex_count = self._io.read_u4le()
            self.nulls = []
            for i in range(4):
                self.nulls.append(self._io.read_u4le())

            self.box = Sbc21.Bbox(self._io, self, self._root)
            self.box._read()
            self.bb_size = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.nulls)):
                pass

            self.box._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc21.SbcHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.unk_02)
            self._io.write_u4le(self.unk_03)
            self._io.write_u2le(self.object_count)
            self._io.write_u2le(self.stage_count)
            self._io.write_u4le(self.pair_count)
            self._io.write_u4le(self.face_count)
            self._io.write_u4le(self.vertex_count)
            for i in range(len(self.nulls)):
                pass
                self._io.write_u4le(self.nulls[i])

            self.box._write__seq(self._io)
            self._io.write_u4le(self.bb_size)


        def _check(self):
            pass
            if (len(self.magic) != 4):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 4)
            if not (self.magic == b"\x53\x42\x43\xFF"):
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\xFF", self.magic, None, u"/types/sbc_header/seq/0")
            if (len(self.nulls) != 4):
                raise kaitaistruct.ConsistencyError(u"nulls", len(self.nulls), 4)
            for i in range(len(self.nulls)):
                pass

            if self.box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"box", self.box._root, self._root)
            if self.box._parent != self:
                raise kaitaistruct.ConsistencyError(u"box", self.box._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 84
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_


