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
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x53\x42\x43\x31"):
            raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.num_groups = self._io.read_u2le()
        self.num_groups_bb = self._io.read_u2le()
        self.unk_num_03 = self._io.read_u2le()
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
        self._io.write_u2le(self.num_groups_bb)
        self._io.write_u2le(self.unk_num_03)
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
            self.boxa = Sbc156.Tbox(self._io, self, self._root)
            self.boxa._read()
            self.boxb = Sbc156.Tbox(self._io, self, self._root)
            self.boxb._read()
            self.boxc = Sbc156.Tbox(self._io, self, self._root)
            self.boxc._read()
            self.ida = self._io.read_u2le()
            self.idb = self._io.read_u2le()


        def _fetch_instances(self):
            pass
            self.boxa._fetch_instances()
            self.boxb._fetch_instances()
            self.boxc._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Sbcgroup, self)._write__seq(io)
            self._io.write_u4le(self.base)
            self._io.write_u4le(self.start_tris)
            self._io.write_u4le(self.start_boxes)
            self._io.write_u4le(self.start_vertices)
            self._io.write_u4le(self.group_id)
            self.boxa._write__seq(self._io)
            self.boxb._write__seq(self._io)
            self.boxc._write__seq(self._io)
            self._io.write_u2le(self.ida)
            self._io.write_u2le(self.idb)


        def _check(self):
            pass
            if self.boxa._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxa", self.boxa._root, self._root)
            if self.boxa._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxa", self.boxa._parent, self)
            if self.boxb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxb", self.boxb._root, self._root)
            if self.boxb._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxb", self.boxb._parent, self)
            if self.boxc._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxc", self.boxc._root, self._root)
            if self.boxc._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxc", self.boxc._parent, self)


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
            self.a = self._io.read_u2le()
            self.b = self._io.read_u2le()
            self.c = self._io.read_u2le()
            self.ida = self._io.read_u1()
            self.idb = self._io.read_u1()
            self.idc = self._io.read_u1()
            self.idd = self._io.read_u1()
            self.ide = self._io.read_u2le()
            self.idf = self._io.read_u2le()
            self.idg = self._io.read_u2le()
            self.idh = self._io.read_u2le()
            self.idi = self._io.read_u2le()
            self.idj = self._io.read_u2le()
            self.idk = self._io.read_u2le()
            self.nulls = []
            for i in range(4):
                self.nulls.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.nulls)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Re5triangle, self)._write__seq(io)
            self._io.write_u2le(self.a)
            self._io.write_u2le(self.b)
            self._io.write_u2le(self.c)
            self._io.write_u1(self.ida)
            self._io.write_u1(self.idb)
            self._io.write_u1(self.idc)
            self._io.write_u1(self.idd)
            self._io.write_u2le(self.ide)
            self._io.write_u2le(self.idf)
            self._io.write_u2le(self.idg)
            self._io.write_u2le(self.idh)
            self._io.write_u2le(self.idi)
            self._io.write_u2le(self.idj)
            self._io.write_u2le(self.idk)
            for i in range(len(self.nulls)):
                pass
                self._io.write_u1(self.nulls[i])



        def _check(self):
            pass
            if (len(self.nulls) != 4):
                raise kaitaistruct.ConsistencyError(u"nulls", len(self.nulls), 4)
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


    class Re5boxes(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.boxa = Sbc156.Pbox(self._io, self, self._root)
            self.boxa._read()
            self.boxb = Sbc156.Pbox(self._io, self, self._root)
            self.boxb._read()
            self.ida = self._io.read_u2le()
            self.idb = self._io.read_u2le()
            self.idc = self._io.read_u2le()
            self.nulls = []
            for i in range(10):
                self.nulls.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            self.boxa._fetch_instances()
            self.boxb._fetch_instances()
            for i in range(len(self.nulls)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Re5boxes, self)._write__seq(io)
            self.boxa._write__seq(self._io)
            self.boxb._write__seq(self._io)
            self._io.write_u2le(self.ida)
            self._io.write_u2le(self.idb)
            self._io.write_u2le(self.idc)
            for i in range(len(self.nulls)):
                pass
                self._io.write_u1(self.nulls[i])



        def _check(self):
            pass
            if self.boxa._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxa", self.boxa._root, self._root)
            if self.boxa._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxa", self.boxa._parent, self)
            if self.boxb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxb", self.boxb._root, self._root)
            if self.boxb._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxb", self.boxb._parent, self)
            if (len(self.nulls) != 10):
                raise kaitaistruct.ConsistencyError(u"nulls", len(self.nulls), 10)
            for i in range(len(self.nulls)):
                pass




