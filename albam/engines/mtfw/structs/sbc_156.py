# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sbc156(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.header = Sbc156.SbcHeader(self._io, self, self._root)
        self.header._read()
        self.nodes = []
        for i in range(self.header.num_nodes):
            _t_nodes = Sbc156.BvhNode(self._io, self, self._root)
            _t_nodes._read()
            self.nodes.append(_t_nodes)

        self.sbc_info = []
        for i in range(self.header.num_infos):
            _t_sbc_info = Sbc156.Info(self._io, self, self._root)
            _t_sbc_info._read()
            self.sbc_info.append(_t_sbc_info)

        self.faces = []
        for i in range(self.header.num_faces):
            _t_faces = Sbc156.Face(self._io, self, self._root)
            _t_faces._read()
            self.faces.append(_t_faces)

        self.vertices = []
        for i in range(self.header.num_vertices):
            _t_vertices = Sbc156.Vec4(self._io, self, self._root)
            _t_vertices._read()
            self.vertices.append(_t_vertices)



    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.nodes)):
            pass
            self.nodes[i]._fetch_instances()

        for i in range(len(self.sbc_info)):
            pass
            self.sbc_info[i]._fetch_instances()

        for i in range(len(self.faces)):
            pass
            self.faces[i]._fetch_instances()

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Sbc156, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.nodes)):
            pass
            self.nodes[i]._write__seq(self._io)

        for i in range(len(self.sbc_info)):
            pass
            self.sbc_info[i]._write__seq(self._io)

        for i in range(len(self.faces)):
            pass
            self.faces[i]._write__seq(self._io)

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._write__seq(self._io)



    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)
        if (len(self.nodes) != self.header.num_nodes):
            raise kaitaistruct.ConsistencyError(u"nodes", len(self.nodes), self.header.num_nodes)
        for i in range(len(self.nodes)):
            pass
            if self.nodes[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"nodes", self.nodes[i]._root, self._root)
            if self.nodes[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"nodes", self.nodes[i]._parent, self)

        if (len(self.sbc_info) != self.header.num_infos):
            raise kaitaistruct.ConsistencyError(u"sbc_info", len(self.sbc_info), self.header.num_infos)
        for i in range(len(self.sbc_info)):
            pass
            if self.sbc_info[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self.sbc_info[i]._root, self._root)
            if self.sbc_info[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self.sbc_info[i]._parent, self)

        if (len(self.faces) != self.header.num_faces):
            raise kaitaistruct.ConsistencyError(u"faces", len(self.faces), self.header.num_faces)
        for i in range(len(self.faces)):
            pass
            if self.faces[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"faces", self.faces[i]._root, self._root)
            if self.faces[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"faces", self.faces[i]._parent, self)

        if (len(self.vertices) != self.header.num_vertices):
            raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), self.header.num_vertices)
        for i in range(len(self.vertices)):
            pass
            if self.vertices[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
            if self.vertices[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)


    class Vec4(ReadWriteKaitaiStruct):
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
            super(Sbc156.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class Pbox(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = Sbc156.Vec4(self._io, self, self._root)
            self.min._read()
            self.max = Sbc156.Vec4(self._io, self, self._root)
            self.max._read()


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Pbox, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            pass
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self.min._root, self._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self.min._parent, self)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self.max._root, self._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self.max._parent, self)


    class Vertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vector = Sbc156.Vec4(self._io, self, self._root)
            self.vector._read()


        def _fetch_instances(self):
            pass
            self.vector._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Vertex, self)._write__seq(io)
            self.vector._write__seq(self._io)


        def _check(self):
            pass
            if self.vector._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vector", self.vector._root, self._root)
            if self.vector._parent != self:
                raise kaitaistruct.ConsistencyError(u"vector", self.vector._parent, self)


    class Bbox(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = Sbc156.Vec3(self._io, self, self._root)
            self.min._read()
            self.max = Sbc156.Vec3(self._io, self, self._root)
            self.max._read()


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Bbox, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            pass
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self.min._root, self._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self.min._parent, self)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self.max._root, self._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self.max._parent, self)


    class Rgba(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.red = self._io.read_u1()
            self.green = self._io.read_u1()
            self.blue = self._io.read_u1()
            self.alpha = self._io.read_u1()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sbc156.Rgba, self)._write__seq(io)
            self._io.write_u1(self.red)
            self._io.write_u1(self.green)
            self._io.write_u1(self.blue)
            self._io.write_u1(self.alpha)


        def _check(self):
            pass


    class Info(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.flags = self._io.read_u4le()
            self.start_tris = self._io.read_u4le()
            self.start_nodes = self._io.read_u4le()
            self.start_vertices = self._io.read_u4le()
            self.index_id = self._io.read_u4le()
            self.bounding_box = Sbc156.Bbox(self._io, self, self._root)
            self.bounding_box._read()
            self.min = []
            for i in range(2):
                _t_min = Sbc156.Vec3(self._io, self, self._root)
                _t_min._read()
                self.min.append(_t_min)

            self.max = []
            for i in range(2):
                _t_max = Sbc156.Vec3(self._io, self, self._root)
                _t_max._read()
                self.max.append(_t_max)

            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())



        def _fetch_instances(self):
            pass
            self.bounding_box._fetch_instances()
            for i in range(len(self.min)):
                pass
                self.min[i]._fetch_instances()

            for i in range(len(self.max)):
                pass
                self.max[i]._fetch_instances()

            for i in range(len(self.child_index)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Info, self)._write__seq(io)
            self._io.write_u4le(self.flags)
            self._io.write_u4le(self.start_tris)
            self._io.write_u4le(self.start_nodes)
            self._io.write_u4le(self.start_vertices)
            self._io.write_u4le(self.index_id)
            self.bounding_box._write__seq(self._io)
            for i in range(len(self.min)):
                pass
                self.min[i]._write__seq(self._io)

            for i in range(len(self.max)):
                pass
                self.max[i]._write__seq(self._io)

            for i in range(len(self.child_index)):
                pass
                self._io.write_u2le(self.child_index[i])



        def _check(self):
            pass
            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self.bounding_box._root, self._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self.bounding_box._parent, self)
            if (len(self.min) != 2):
                raise kaitaistruct.ConsistencyError(u"min", len(self.min), 2)
            for i in range(len(self.min)):
                pass
                if self.min[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"min", self.min[i]._root, self._root)
                if self.min[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"min", self.min[i]._parent, self)

            if (len(self.max) != 2):
                raise kaitaistruct.ConsistencyError(u"max", len(self.max), 2)
            for i in range(len(self.max)):
                pass
                if self.max[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"max", self.max[i]._root, self._root)
                if self.max[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"max", self.max[i]._parent, self)

            if (len(self.child_index) != 2):
                raise kaitaistruct.ConsistencyError(u"child_index", len(self.child_index), 2)
            for i in range(len(self.child_index)):
                pass



    class Aabb(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = Sbc156.Vec4(self._io, self, self._root)
            self.min._read()
            self.max = Sbc156.Vec4(self._io, self, self._root)
            self.max._read()


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Aabb, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            pass
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self.min._root, self._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self.min._parent, self)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self.max._root, self._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self.max._parent, self)


    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vert = []
            for i in range(3):
                self.vert.append(self._io.read_u2le())

            self.unk_00 = []
            for i in range(2):
                self.unk_00.append(self._io.read_u1())

            self.type = self._io.read_u4le()
            self.attr = []
            for i in range(4):
                self.attr.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.vert)):
                pass

            for i in range(len(self.unk_00)):
                pass

            for i in range(len(self.attr)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Face, self)._write__seq(io)
            for i in range(len(self.vert)):
                pass
                self._io.write_u2le(self.vert[i])

            for i in range(len(self.unk_00)):
                pass
                self._io.write_u1(self.unk_00[i])

            self._io.write_u4le(self.type)
            for i in range(len(self.attr)):
                pass
                self._io.write_u4le(self.attr[i])



        def _check(self):
            pass
            if (len(self.vert) != 3):
                raise kaitaistruct.ConsistencyError(u"vert", len(self.vert), 3)
            for i in range(len(self.vert)):
                pass

            if (len(self.unk_00) != 2):
                raise kaitaistruct.ConsistencyError(u"unk_00", len(self.unk_00), 2)
            for i in range(len(self.unk_00)):
                pass

            if (len(self.attr) != 4):
                raise kaitaistruct.ConsistencyError(u"attr", len(self.attr), 4)
            for i in range(len(self.attr)):
                pass



    class BvhNode(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.aabb_01 = Sbc156.Aabb(self._io, self, self._root)
            self.aabb_01._read()
            self.aabb_02 = Sbc156.Aabb(self._io, self, self._root)
            self.aabb_02._read()
            self.bit = self._io.read_u1()
            self.unk = self._io.read_u1()
            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())

            self.nulls = []
            for i in range(10):
                self.nulls.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            self.aabb_01._fetch_instances()
            self.aabb_02._fetch_instances()
            for i in range(len(self.child_index)):
                pass

            for i in range(len(self.nulls)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.BvhNode, self)._write__seq(io)
            self.aabb_01._write__seq(self._io)
            self.aabb_02._write__seq(self._io)
            self._io.write_u1(self.bit)
            self._io.write_u1(self.unk)
            for i in range(len(self.child_index)):
                pass
                self._io.write_u2le(self.child_index[i])

            for i in range(len(self.nulls)):
                pass
                self._io.write_u1(self.nulls[i])



        def _check(self):
            pass
            if self.aabb_01._root != self._root:
                raise kaitaistruct.ConsistencyError(u"aabb_01", self.aabb_01._root, self._root)
            if self.aabb_01._parent != self:
                raise kaitaistruct.ConsistencyError(u"aabb_01", self.aabb_01._parent, self)
            if self.aabb_02._root != self._root:
                raise kaitaistruct.ConsistencyError(u"aabb_02", self.aabb_02._root, self._root)
            if self.aabb_02._parent != self:
                raise kaitaistruct.ConsistencyError(u"aabb_02", self.aabb_02._parent, self)
            if (len(self.child_index) != 2):
                raise kaitaistruct.ConsistencyError(u"child_index", len(self.child_index), 2)
            for i in range(len(self.child_index)):
                pass

            if (len(self.nulls) != 10):
                raise kaitaistruct.ConsistencyError(u"nulls", len(self.nulls), 10)
            for i in range(len(self.nulls)):
                pass



    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sbc156.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            pass


    class SbcHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not (self.magic == b"\x53\x42\x43\x31"):
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.magic, self._io, u"/types/sbc_header/seq/0")
            self.version = self._io.read_u2le()
            self.num_infos = self._io.read_u2le()
            self.num_parts = self._io.read_u2le()
            self.num_parts_nest = self._io.read_u1()
            self.max_nest_count = self._io.read_u1()
            self.num_nodes = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.box = Sbc156.Bbox(self._io, self, self._root)
            self.box._read()


        def _fetch_instances(self):
            pass
            self.box._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.SbcHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.version)
            self._io.write_u2le(self.num_infos)
            self._io.write_u2le(self.num_parts)
            self._io.write_u1(self.num_parts_nest)
            self._io.write_u1(self.max_nest_count)
            self._io.write_u4le(self.num_nodes)
            self._io.write_u4le(self.num_faces)
            self._io.write_u4le(self.num_vertices)
            self.box._write__seq(self._io)


        def _check(self):
            pass
            if (len(self.magic) != 4):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 4)
            if not (self.magic == b"\x53\x42\x43\x31"):
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.magic, None, u"/types/sbc_header/seq/0")
            if self.box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"box", self.box._root, self._root)
            if self.box._parent != self:
                raise kaitaistruct.ConsistencyError(u"box", self.box._parent, self)



