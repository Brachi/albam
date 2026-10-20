# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Nav156(ReadWriteKaitaiStruct):
    """Tail layout: the footer holds a node count (0x1555 = 5461), which is a full
    quadtree for a 64x64 leaf grid:
        4096 leaves (64x64) + 1024 + 256 + 64 + 16 + 4 + 1 = 5461 nodes.
    The first 1365 nodes (32x32 down to 1x1) are all zero in every sample; the
    last 4096 entries are the leaf cells, stored in Morton (Z-order) order.
    Leaf cell size = (node_info.upper - node_info.lower) / 64 on X and Z.
    """

    class Edge(IntEnum):
        v1_v2 = 0
        v2_v3 = 1
        v1_v3 = 2
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Nav156, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.indent = self._io.read_bytes(4)
        if not self.indent == b"\x4E\x41\x56\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4E\x41\x56\x00", self.indent, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        if not self.version == 2:
            raise kaitaistruct.ValidationNotEqualError(2, self.version, self._io, u"/seq/1")
        self.reserved = self._io.read_u4le()
        self.num_vertices = self._io.read_u4le()
        self.num_faces = self._io.read_u4le()
        self.num_node_infos = self._io.read_u4le()
        self.vertices = []
        for i in range(self.num_vertices):
            _t_vertices = Nav156.Vertex(self._io, self, self._root)
            try:
                _t_vertices._read()
            finally:
                self.vertices.append(_t_vertices)

        self.faces = []
        for i in range(self.num_faces):
            _t_faces = Nav156.Face(self._io, self, self._root)
            try:
                _t_faces._read()
            finally:
                self.faces.append(_t_faces)

        self.node_infos = []
        for i in range(self.num_node_infos):
            _t_node_infos = Nav156.NodeInfo(self._io, self, self._root)
            try:
                _t_node_infos._read()
            finally:
                self.node_infos.append(_t_node_infos)

        self.footer_tag = self._io.read_bytes(1)
        if not self.footer_tag == b"\x07":
            raise kaitaistruct.ValidationNotEqualError(b"\x07", self.footer_tag, self._io, u"/seq/9")
        self.num_grid_nodes = self._io.read_u4le()
        self.internal_nodes = []
        for i in range(self.num_grid_nodes - 4096):
            _t_internal_nodes = Nav156.GridCell(self._io, self, self._root)
            try:
                _t_internal_nodes._read()
            finally:
                self.internal_nodes.append(_t_internal_nodes)

        self.lookup_grid = []
        for i in range(4096):
            _t_lookup_grid = Nav156.GridCell(self._io, self, self._root)
            try:
                _t_lookup_grid._read()
            finally:
                self.lookup_grid.append(_t_lookup_grid)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._fetch_instances()

        for i in range(len(self.faces)):
            pass
            self.faces[i]._fetch_instances()

        for i in range(len(self.node_infos)):
            pass
            self.node_infos[i]._fetch_instances()

        for i in range(len(self.internal_nodes)):
            pass
            self.internal_nodes[i]._fetch_instances()

        for i in range(len(self.lookup_grid)):
            pass
            self.lookup_grid[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Nav156, self)._write__seq(io)
        self._io.write_bytes(self.indent)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.reserved)
        self._io.write_u4le(self.num_vertices)
        self._io.write_u4le(self.num_faces)
        self._io.write_u4le(self.num_node_infos)
        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._write__seq(self._io)

        for i in range(len(self.faces)):
            pass
            self.faces[i]._write__seq(self._io)

        for i in range(len(self.node_infos)):
            pass
            self.node_infos[i]._write__seq(self._io)

        self._io.write_bytes(self.footer_tag)
        self._io.write_u4le(self.num_grid_nodes)
        for i in range(len(self.internal_nodes)):
            pass
            self.internal_nodes[i]._write__seq(self._io)

        for i in range(len(self.lookup_grid)):
            pass
            self.lookup_grid[i]._write__seq(self._io)



    def _check(self):
        if len(self.indent) != 4:
            raise kaitaistruct.ConsistencyError(u"indent", 4, len(self.indent))
        if not self.indent == b"\x4E\x41\x56\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4E\x41\x56\x00", self.indent, None, u"/seq/0")
        if not self.version == 2:
            raise kaitaistruct.ValidationNotEqualError(2, self.version, None, u"/seq/1")
        if len(self.vertices) != self.num_vertices:
            raise kaitaistruct.ConsistencyError(u"vertices", self.num_vertices, len(self.vertices))
        for i in range(len(self.vertices)):
            pass
            if self.vertices[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vertices", self._root, self.vertices[i]._root)
            if self.vertices[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vertices", self, self.vertices[i]._parent)

        if len(self.faces) != self.num_faces:
            raise kaitaistruct.ConsistencyError(u"faces", self.num_faces, len(self.faces))
        for i in range(len(self.faces)):
            pass
            if self.faces[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"faces", self._root, self.faces[i]._root)
            if self.faces[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"faces", self, self.faces[i]._parent)

        if len(self.node_infos) != self.num_node_infos:
            raise kaitaistruct.ConsistencyError(u"node_infos", self.num_node_infos, len(self.node_infos))
        for i in range(len(self.node_infos)):
            pass
            if self.node_infos[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"node_infos", self._root, self.node_infos[i]._root)
            if self.node_infos[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"node_infos", self, self.node_infos[i]._parent)

        if len(self.footer_tag) != 1:
            raise kaitaistruct.ConsistencyError(u"footer_tag", 1, len(self.footer_tag))
        if not self.footer_tag == b"\x07":
            raise kaitaistruct.ValidationNotEqualError(b"\x07", self.footer_tag, None, u"/seq/9")
        if len(self.internal_nodes) != self.num_grid_nodes - 4096:
            raise kaitaistruct.ConsistencyError(u"internal_nodes", self.num_grid_nodes - 4096, len(self.internal_nodes))
        for i in range(len(self.internal_nodes)):
            pass
            if self.internal_nodes[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"internal_nodes", self._root, self.internal_nodes[i]._root)
            if self.internal_nodes[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"internal_nodes", self, self.internal_nodes[i]._parent)

        if len(self.lookup_grid) != 4096:
            raise kaitaistruct.ConsistencyError(u"lookup_grid", 4096, len(self.lookup_grid))
        for i in range(len(self.lookup_grid)):
            pass
            if self.lookup_grid[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"lookup_grid", self._root, self.lookup_grid[i]._root)
            if self.lookup_grid[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"lookup_grid", self, self.lookup_grid[i]._parent)

        self._dirty = False

    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.Face, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.index = self._io.read_u4le()
            self.unk_00 = self._io.read_u4le()
            self.flags = self._io.read_u4le()
            self.vertex_per_face = self._io.read_u4le()
            self.v1 = self._io.read_u4le()
            self.v2 = self._io.read_u4le()
            self.v3 = self._io.read_u4le()
            self.num_neighbors = self._io.read_u4le()
            self.neighbors = []
            for i in range(self.num_neighbors):
                _t_neighbors = Nav156.Neighbor(self._io, self, self._root)
                try:
                    _t_neighbors._read()
                finally:
                    self.neighbors.append(_t_neighbors)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.neighbors)):
                pass
                self.neighbors[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Nav156.Face, self)._write__seq(io)
            self._io.write_u4le(self.index)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.flags)
            self._io.write_u4le(self.vertex_per_face)
            self._io.write_u4le(self.v1)
            self._io.write_u4le(self.v2)
            self._io.write_u4le(self.v3)
            self._io.write_u4le(self.num_neighbors)
            for i in range(len(self.neighbors)):
                pass
                self.neighbors[i]._write__seq(self._io)



        def _check(self):
            if len(self.neighbors) != self.num_neighbors:
                raise kaitaistruct.ConsistencyError(u"neighbors", self.num_neighbors, len(self.neighbors))
            for i in range(len(self.neighbors)):
                pass
                if self.neighbors[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"neighbors", self._root, self.neighbors[i]._root)
                if self.neighbors[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"neighbors", self, self.neighbors[i]._parent)

            self._dirty = False


    class GridCell(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.GridCell, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_faces = self._io.read_u4le()
            self.faces = []
            for i in range(self.num_faces):
                _t_faces = Nav156.GridFace(self._io, self, self._root)
                try:
                    _t_faces._read()
                finally:
                    self.faces.append(_t_faces)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.faces)):
                pass
                self.faces[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Nav156.GridCell, self)._write__seq(io)
            self._io.write_u4le(self.num_faces)
            for i in range(len(self.faces)):
                pass
                self.faces[i]._write__seq(self._io)



        def _check(self):
            if len(self.faces) != self.num_faces:
                raise kaitaistruct.ConsistencyError(u"faces", self.num_faces, len(self.faces))
            for i in range(len(self.faces)):
                pass
                if self.faces[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"faces", self._root, self.faces[i]._root)
                if self.faces[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"faces", self, self.faces[i]._parent)

            self._dirty = False


    class GridFace(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.GridFace, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.face_index = self._io.read_u4le()
            self.padding = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Nav156.GridFace, self)._write__seq(io)
            self._io.write_u4le(self.face_index)
            self._io.write_u4le(self.padding)


        def _check(self):
            self._dirty = False


    class Neighbor(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.Neighbor, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.face_index = self._io.read_u4le()
            self.padding = self._io.read_u4le()
            self.edge = KaitaiStream.resolve_enum(Nav156.Edge, self._io.read_u4le())
            self.centroid_distance = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Nav156.Neighbor, self)._write__seq(io)
            self._io.write_u4le(self.face_index)
            self._io.write_u4le(self.padding)
            self._io.write_u4le(int(self.edge))
            self._io.write_f4le(self.centroid_distance)


        def _check(self):
            self._dirty = False


    class NodeInfo(ReadWriteKaitaiStruct):
        """36 bytes on disk; runtime struct is 0x30. The 4-byte pads are
        uninitialized in some builds (0xCDCDCDCD = MSVC debug fill).
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.NodeInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.type = self._io.read_u4le()
            self.lower = Nav156.Vertex(self._io, self, self._root)
            self.lower._read()
            self.padding_00 = self._io.read_bytes(4)
            self.upper = Nav156.Vertex(self._io, self, self._root)
            self.upper._read()
            self.padding_01 = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.lower._fetch_instances()
            self.upper._fetch_instances()


        def _write__seq(self, io=None):
            super(Nav156.NodeInfo, self)._write__seq(io)
            self._io.write_u4le(self.type)
            self.lower._write__seq(self._io)
            self._io.write_bytes(self.padding_00)
            self.upper._write__seq(self._io)
            self._io.write_bytes(self.padding_01)


        def _check(self):
            if self.lower._root != self._root:
                raise kaitaistruct.ConsistencyError(u"lower", self._root, self.lower._root)
            if self.lower._parent != self:
                raise kaitaistruct.ConsistencyError(u"lower", self, self.lower._parent)
            if len(self.padding_00) != 4:
                raise kaitaistruct.ConsistencyError(u"padding_00", 4, len(self.padding_00))
            if self.upper._root != self._root:
                raise kaitaistruct.ConsistencyError(u"upper", self._root, self.upper._root)
            if self.upper._parent != self:
                raise kaitaistruct.ConsistencyError(u"upper", self, self.upper._parent)
            if len(self.padding_01) != 4:
                raise kaitaistruct.ConsistencyError(u"padding_01", 4, len(self.padding_01))
            self._dirty = False


    class Vertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.Vertex, self).__init__(_io)
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
            super(Nav156.Vertex, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False



