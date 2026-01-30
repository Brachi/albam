# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sbc156(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x53\x42\x43\x31"):
            raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.num_groups = self._io.read_u2le()
        self.num_groups_nodes = self._io.read_u2le()
        self.max_parts_nest_count = self._io.read_u1()
        self.max_nest_count = self._io.read_u1()
        self.num_boxes = self._io.read_u4le()
        self.num_faces = self._io.read_u4le()
        self.num_vertices = self._io.read_u4le()
        self.bbox = Sbc156.Tbox(self._io, self, self._root)
        self.bbox._read()
        self.boxes = []
        for i in range(self.num_boxes):
            _t_boxes = Sbc156.Re5boxes(self._io, self, self._root)
            _t_boxes._read()
            self.boxes.append(_t_boxes)

        self.groups = []
        for i in range(self.num_groups):
            _t_groups = Sbc156.Sbcgroup(self._io, self, self._root)
            _t_groups._read()
            self.groups.append(_t_groups)

        self.triangles = []
        for i in range(self.num_faces):
            _t_triangles = Sbc156.Re5triangle(self._io, self, self._root)
            _t_triangles._read()
            self.triangles.append(_t_triangles)

        self.vertices = []
        for i in range(self.num_vertices):
            _t_vertices = Sbc156.Vertex(self._io, self, self._root)
            _t_vertices._read()
            self.vertices.append(_t_vertices)



    def _fetch_instances(self):
        pass
        self.bbox._fetch_instances()
        for i in range(len(self.boxes)):
            pass
            self.boxes[i]._fetch_instances()

        for i in range(len(self.groups)):
            pass
            self.groups[i]._fetch_instances()

        for i in range(len(self.triangles)):
            pass
            self.triangles[i]._fetch_instances()

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Sbc156, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u2le(self.version)
        self._io.write_u2le(self.num_groups)
        self._io.write_u2le(self.num_groups_nodes)
        self._io.write_u1(self.max_parts_nest_count)
        self._io.write_u1(self.max_nest_count)
        self._io.write_u4le(self.num_boxes)
        self._io.write_u4le(self.num_faces)
        self._io.write_u4le(self.num_vertices)
        self.bbox._write__seq(self._io)
        for i in range(len(self.boxes)):
            pass
            self.boxes[i]._write__seq(self._io)

        for i in range(len(self.groups)):
            pass
            self.groups[i]._write__seq(self._io)

        for i in range(len(self.triangles)):
            pass
            self.triangles[i]._write__seq(self._io)

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._write__seq(self._io)



    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x53\x42\x43\x31"):
            raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.id_magic, None, u"/seq/0")
        if self.bbox._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bbox", self.bbox._root, self._root)
        if self.bbox._parent != self:
            raise kaitaistruct.ConsistencyError(u"bbox", self.bbox._parent, self)
        if (len(self.boxes) != self.num_boxes):
            raise kaitaistruct.ConsistencyError(u"boxes", len(self.boxes), self.num_boxes)
        for i in range(len(self.boxes)):
            pass
            if self.boxes[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxes", self.boxes[i]._root, self._root)
            if self.boxes[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxes", self.boxes[i]._parent, self)

        if (len(self.groups) != self.num_groups):
            raise kaitaistruct.ConsistencyError(u"groups", len(self.groups), self.num_groups)
        for i in range(len(self.groups)):
            pass
            if self.groups[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"groups", self.groups[i]._root, self._root)
            if self.groups[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"groups", self.groups[i]._parent, self)

        if (len(self.triangles) != self.num_faces):
            raise kaitaistruct.ConsistencyError(u"triangles", len(self.triangles), self.num_faces)
        for i in range(len(self.triangles)):
            pass
            if self.triangles[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"triangles", self.triangles[i]._root, self._root)
            if self.triangles[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"triangles", self.triangles[i]._parent, self)

        if (len(self.vertices) != self.num_vertices):
            raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), self.num_vertices)
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


    class Sbcgroup(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.base = self._io.read_u4le()
            self.start_tris = self._io.read_u4le()
            self.start_boxes = self._io.read_u4le()
            self.start_vertices = self._io.read_u4le()
            self.group_id = self._io.read_u4le()
            self.bbox_this = Sbc156.Tbox(self._io, self, self._root)
            self.bbox_this._read()
            self.vmin = []
            for i in range(2):
                _t_vmin = Sbc156.Vec3(self._io, self, self._root)
                _t_vmin._read()
                self.vmin.append(_t_vmin)

            self.vmax = []
            for i in range(2):
                _t_vmax = Sbc156.Vec3(self._io, self, self._root)
                _t_vmax._read()
                self.vmax.append(_t_vmax)

            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())



        def _fetch_instances(self):
            pass
            self.bbox_this._fetch_instances()
            for i in range(len(self.vmin)):
                pass
                self.vmin[i]._fetch_instances()

            for i in range(len(self.vmax)):
                pass
                self.vmax[i]._fetch_instances()

            for i in range(len(self.child_index)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Sbcgroup, self)._write__seq(io)
            self._io.write_u4le(self.base)
            self._io.write_u4le(self.start_tris)
            self._io.write_u4le(self.start_boxes)
            self._io.write_u4le(self.start_vertices)
            self._io.write_u4le(self.group_id)
            self.bbox_this._write__seq(self._io)
            for i in range(len(self.vmin)):
                pass
                self.vmin[i]._write__seq(self._io)

            for i in range(len(self.vmax)):
                pass
                self.vmax[i]._write__seq(self._io)

            for i in range(len(self.child_index)):
                pass
                self._io.write_u2le(self.child_index[i])



        def _check(self):
            pass
            if self.bbox_this._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bbox_this", self.bbox_this._root, self._root)
            if self.bbox_this._parent != self:
                raise kaitaistruct.ConsistencyError(u"bbox_this", self.bbox_this._parent, self)
            if (len(self.vmin) != 2):
                raise kaitaistruct.ConsistencyError(u"vmin", len(self.vmin), 2)
            for i in range(len(self.vmin)):
                pass
                if self.vmin[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"vmin", self.vmin[i]._root, self._root)
                if self.vmin[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"vmin", self.vmin[i]._parent, self)

            if (len(self.vmax) != 2):
                raise kaitaistruct.ConsistencyError(u"vmax", len(self.vmax), 2)
            for i in range(len(self.vmax)):
                pass
                if self.vmax[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"vmax", self.vmax[i]._root, self._root)
                if self.vmax[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"vmax", self.vmax[i]._parent, self)

            if (len(self.child_index) != 2):
                raise kaitaistruct.ConsistencyError(u"child_index", len(self.child_index), 2)
            for i in range(len(self.child_index)):
                pass



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


    class Tbox(ReadWriteKaitaiStruct):
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
            super(Sbc156.Tbox, self)._write__seq(io)
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


    class Re5triangle(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vert = []
            for i in range(3):
                self.vert.append(self._io.read_u2le())

            self.unk_00 = self._io.read_u1()
            self.unk_01 = self._io.read_u1()
            self.runtime_attr = self._io.read_u4le()
            self.type = self._io.read_u4le()
            self.special_attr = self._io.read_u4le()
            self.surface_attr = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.vert)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Re5triangle, self)._write__seq(io)
            for i in range(len(self.vert)):
                pass
                self._io.write_u2le(self.vert[i])

            self._io.write_u1(self.unk_00)
            self._io.write_u1(self.unk_01)
            self._io.write_u4le(self.runtime_attr)
            self._io.write_u4le(self.type)
            self._io.write_u4le(self.special_attr)
            self._io.write_u4le(self.surface_attr)
            self._io.write_u4le(self.unk_02)


        def _check(self):
            pass
            if (len(self.vert) != 3):
                raise kaitaistruct.ConsistencyError(u"vert", len(self.vert), 3)
            for i in range(len(self.vert)):
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


    class Re5boxes(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.boxes = []
            for i in range(2):
                _t_boxes = Sbc156.Pbox(self._io, self, self._root)
                _t_boxes._read()
                self.boxes.append(_t_boxes)

            self.bit = self._io.read_u2le()
            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())

            self.nulls = []
            for i in range(10):
                self.nulls.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.boxes)):
                pass
                self.boxes[i]._fetch_instances()

            for i in range(len(self.child_index)):
                pass

            for i in range(len(self.nulls)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Re5boxes, self)._write__seq(io)
            for i in range(len(self.boxes)):
                pass
                self.boxes[i]._write__seq(self._io)

            self._io.write_u2le(self.bit)
            for i in range(len(self.child_index)):
                pass
                self._io.write_u2le(self.child_index[i])

            for i in range(len(self.nulls)):
                pass
                self._io.write_u1(self.nulls[i])



        def _check(self):
            pass
            if (len(self.boxes) != 2):
                raise kaitaistruct.ConsistencyError(u"boxes", len(self.boxes), 2)
            for i in range(len(self.boxes)):
                pass
                if self.boxes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"boxes", self.boxes[i]._root, self._root)
                if self.boxes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"boxes", self.boxes[i]._parent, self)

            if (len(self.child_index) != 2):
                raise kaitaistruct.ConsistencyError(u"child_index", len(self.child_index), 2)
            for i in range(len(self.child_index)):
                pass

            if (len(self.nulls) != 10):
                raise kaitaistruct.ConsistencyError(u"nulls", len(self.nulls), 10)
            for i in range(len(self.nulls)):
                pass




