# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Nav156(ReadWriteKaitaiStruct):

    class Edge(IntEnum):
        v1_v2 = 0
        v2_v3 = 1
        v1_v3 = 2
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Nav156, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x4E\x41\x56\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4E\x41\x56\x00", self.magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        if not self.version == 2:
            raise kaitaistruct.ValidationNotEqualError(2, self.version, self._io, u"/seq/1")
        self.reserved = self._io.read_u4le()
        self.vertex_count = self._io.read_u4le()
        self.face_count = self._io.read_u4le()
        self.header_padding = self._io.read_u4le()
        self.vertices = []
        for i in range(self.vertex_count):
            _t_vertices = Nav156.Vertex(self._io, self, self._root)
            try:
                _t_vertices._read()
            finally:
                self.vertices.append(_t_vertices)

        self.faces = []
        for i in range(self.face_count):
            _t_faces = Nav156.Face(self._io, self, self._root)
            try:
                _t_faces._read()
            finally:
                self.faces.append(_t_faces)

        self.bbox = Nav156.BoundingBox(self._io, self, self._root)
        self.bbox._read()
        self.footer_magic = self._io.read_bytes(5)
        if not self.footer_magic == b"\x07\x55\x15\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x07\x55\x15\x00\x00", self.footer_magic, self._io, u"/seq/9")
        self.footer_padding = self._io.read_bytes(5460)
        self.lookup_grid = []
        i = 0
        while not self._io.is_eof():
            _t_lookup_grid = Nav156.GridCell(self._io, self, self._root)
            try:
                _t_lookup_grid._read()
            finally:
                self.lookup_grid.append(_t_lookup_grid)
            i += 1

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._fetch_instances()

        for i in range(len(self.faces)):
            pass
            self.faces[i]._fetch_instances()

        self.bbox._fetch_instances()
        for i in range(len(self.lookup_grid)):
            pass
            self.lookup_grid[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Nav156, self)._write__seq(io)
        self._io.write_bytes(self.magic)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.reserved)
        self._io.write_u4le(self.vertex_count)
        self._io.write_u4le(self.face_count)
        self._io.write_u4le(self.header_padding)
        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._write__seq(self._io)

        for i in range(len(self.faces)):
            pass
            self.faces[i]._write__seq(self._io)

        self.bbox._write__seq(self._io)
        self._io.write_bytes(self.footer_magic)
        self._io.write_bytes(self.footer_padding)
        for i in range(len(self.lookup_grid)):
            pass
            if self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"lookup_grid", 0, self._io.size() - self._io.pos())
            self.lookup_grid[i]._write__seq(self._io)

        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"lookup_grid", 0, self._io.size() - self._io.pos())


    def _check(self):
        if len(self.magic) != 4:
            raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
        if not self.magic == b"\x4E\x41\x56\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4E\x41\x56\x00", self.magic, None, u"/seq/0")
        if not self.version == 2:
            raise kaitaistruct.ValidationNotEqualError(2, self.version, None, u"/seq/1")
        if len(self.vertices) != self.vertex_count:
            raise kaitaistruct.ConsistencyError(u"vertices", self.vertex_count, len(self.vertices))
        for i in range(len(self.vertices)):
            pass
            if self.vertices[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vertices", self._root, self.vertices[i]._root)
            if self.vertices[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vertices", self, self.vertices[i]._parent)

        if len(self.faces) != self.face_count:
            raise kaitaistruct.ConsistencyError(u"faces", self.face_count, len(self.faces))
        for i in range(len(self.faces)):
            pass
            if self.faces[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"faces", self._root, self.faces[i]._root)
            if self.faces[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"faces", self, self.faces[i]._parent)

        if self.bbox._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bbox", self._root, self.bbox._root)
        if self.bbox._parent != self:
            raise kaitaistruct.ConsistencyError(u"bbox", self, self.bbox._parent)
        if len(self.footer_magic) != 5:
            raise kaitaistruct.ConsistencyError(u"footer_magic", 5, len(self.footer_magic))
        if not self.footer_magic == b"\x07\x55\x15\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x07\x55\x15\x00\x00", self.footer_magic, None, u"/seq/9")
        if len(self.footer_padding) != 5460:
            raise kaitaistruct.ConsistencyError(u"footer_padding", 5460, len(self.footer_padding))
        for i in range(len(self.lookup_grid)):
            pass
            if self.lookup_grid[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"lookup_grid", self._root, self.lookup_grid[i]._root)
            if self.lookup_grid[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"lookup_grid", self, self.lookup_grid[i]._parent)

        self._dirty = False

    class BoundingBox(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.BoundingBox, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.padding0 = self._io.read_u4le()
            self.lower = Nav156.Vertex(self._io, self, self._root)
            self.lower._read()
            self.padding1 = self._io.read_bytes(4)
            self.upper = Nav156.Vertex(self._io, self, self._root)
            self.upper._read()
            self.padding2 = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.lower._fetch_instances()
            self.upper._fetch_instances()


        def _write__seq(self, io=None):
            super(Nav156.BoundingBox, self)._write__seq(io)
            self._io.write_u4le(self.padding0)
            self.lower._write__seq(self._io)
            self._io.write_bytes(self.padding1)
            self.upper._write__seq(self._io)
            self._io.write_bytes(self.padding2)


        def _check(self):
            if self.lower._root != self._root:
                raise kaitaistruct.ConsistencyError(u"lower", self._root, self.lower._root)
            if self.lower._parent != self:
                raise kaitaistruct.ConsistencyError(u"lower", self, self.lower._parent)
            if len(self.padding1) != 4:
                raise kaitaistruct.ConsistencyError(u"padding1", 4, len(self.padding1))
            if self.upper._root != self._root:
                raise kaitaistruct.ConsistencyError(u"upper", self._root, self.upper._root)
            if self.upper._parent != self:
                raise kaitaistruct.ConsistencyError(u"upper", self, self.upper._parent)
            if len(self.padding2) != 4:
                raise kaitaistruct.ConsistencyError(u"padding2", 4, len(self.padding2))
            self._dirty = False


    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Nav156.Face, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.index = self._io.read_u4le()
            self.unk1 = self._io.read_u4le()
            self.unk2 = self._io.read_u4le()
            self.vertex_per_face = self._io.read_u4le()
            self.v1 = self._io.read_u4le()
            self.v2 = self._io.read_u4le()
            self.v3 = self._io.read_u4le()
            self.neighbor_count = self._io.read_u4le()
            self.neighbors = []
            for i in range(self.neighbor_count):
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
            self._io.write_u4le(self.unk1)
            self._io.write_u4le(self.unk2)
            self._io.write_u4le(self.vertex_per_face)
            self._io.write_u4le(self.v1)
            self._io.write_u4le(self.v2)
            self._io.write_u4le(self.v3)
            self._io.write_u4le(self.neighbor_count)
            for i in range(len(self.neighbors)):
                pass
                self.neighbors[i]._write__seq(self._io)



        def _check(self):
            if len(self.neighbors) != self.neighbor_count:
                raise kaitaistruct.ConsistencyError(u"neighbors", self.neighbor_count, len(self.neighbors))
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
            self.face_count = self._io.read_u4le()
            self.faces = []
            for i in range(self.face_count):
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
            self._io.write_u4le(self.face_count)
            for i in range(len(self.faces)):
                pass
                self.faces[i]._write__seq(self._io)



        def _check(self):
            if len(self.faces) != self.face_count:
                raise kaitaistruct.ConsistencyError(u"faces", self.face_count, len(self.faces))
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



