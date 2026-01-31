# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sbc156(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Sbc156, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Sbc156.SbcHeader(self._io, self, self._root)
        self.header._read()
        self.boxes = []
        for i in range(self.header.num_boxes):
            _t_boxes = Sbc156.Re5boxes(self._io, self, self._root)
            try:
                _t_boxes._read()
            finally:
                self.boxes.append(_t_boxes)

        self.groups = []
        for i in range(self.header.num_groups):
            _t_groups = Sbc156.Sbcgroup(self._io, self, self._root)
            try:
                _t_groups._read()
            finally:
                self.groups.append(_t_groups)

        self.faces = []
        for i in range(self.header.num_faces):
            _t_faces = Sbc156.Re5triangle(self._io, self, self._root)
            try:
                _t_faces._read()
            finally:
                self.faces.append(_t_faces)

        self.vertices = []
        for i in range(self.header.num_vertices):
            _t_vertices = Sbc156.Vertex(self._io, self, self._root)
            try:
                _t_vertices._read()
            finally:
                self.vertices.append(_t_vertices)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.boxes)):
            pass
            self.boxes[i]._fetch_instances()

        for i in range(len(self.groups)):
            pass
            self.groups[i]._fetch_instances()

        for i in range(len(self.faces)):
            pass
            self.faces[i]._fetch_instances()

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Sbc156, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.boxes)):
            pass
            self.boxes[i]._write__seq(self._io)

        for i in range(len(self.groups)):
            pass
            self.groups[i]._write__seq(self._io)

        for i in range(len(self.faces)):
            pass
            self.faces[i]._write__seq(self._io)

        for i in range(len(self.vertices)):
            pass
            self.vertices[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.boxes) != self.header.num_boxes:
            raise kaitaistruct.ConsistencyError(u"boxes", self.header.num_boxes, len(self.boxes))
        for i in range(len(self.boxes)):
            pass
            if self.boxes[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"boxes", self._root, self.boxes[i]._root)
            if self.boxes[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"boxes", self, self.boxes[i]._parent)

        if len(self.groups) != self.header.num_groups:
            raise kaitaistruct.ConsistencyError(u"groups", self.header.num_groups, len(self.groups))
        for i in range(len(self.groups)):
            pass
            if self.groups[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"groups", self._root, self.groups[i]._root)
            if self.groups[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"groups", self, self.groups[i]._parent)

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

        self._dirty = False

    class Aabb(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Aabb, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = Sbc156.Vec4(self._io, self, self._root)
            self.min._read()
            self.max = Sbc156.Vec4(self._io, self, self._root)
            self.max._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Aabb, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self._root, self.min._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self, self.min._parent)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self._root, self.max._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self, self.max._parent)
            self._dirty = False


    class BvhNode(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.BvhNode, self).__init__(_io)
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

            self._dirty = False


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
            if self.aabb_01._root != self._root:
                raise kaitaistruct.ConsistencyError(u"aabb_01", self._root, self.aabb_01._root)
            if self.aabb_01._parent != self:
                raise kaitaistruct.ConsistencyError(u"aabb_01", self, self.aabb_01._parent)
            if self.aabb_02._root != self._root:
                raise kaitaistruct.ConsistencyError(u"aabb_02", self._root, self.aabb_02._root)
            if self.aabb_02._parent != self:
                raise kaitaistruct.ConsistencyError(u"aabb_02", self, self.aabb_02._parent)
            if len(self.child_index) != 2:
                raise kaitaistruct.ConsistencyError(u"child_index", 2, len(self.child_index))
            for i in range(len(self.child_index)):
                pass

            if len(self.nulls) != 10:
                raise kaitaistruct.ConsistencyError(u"nulls", 10, len(self.nulls))
            for i in range(len(self.nulls)):
                pass

            self._dirty = False


    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Face, self).__init__(_io)
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

            self._dirty = False


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
            if len(self.vert) != 3:
                raise kaitaistruct.ConsistencyError(u"vert", 3, len(self.vert))
            for i in range(len(self.vert)):
                pass

            if len(self.unk_00) != 2:
                raise kaitaistruct.ConsistencyError(u"unk_00", 2, len(self.unk_00))
            for i in range(len(self.unk_00)):
                pass

            if len(self.attr) != 4:
                raise kaitaistruct.ConsistencyError(u"attr", 4, len(self.attr))
            for i in range(len(self.attr)):
                pass

            self._dirty = False


    class Info(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Info, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.flags = self._io.read_u4le()
            self.start_tris = self._io.read_u4le()
            self.start_nodes = self._io.read_u4le()
            self.start_vertices = self._io.read_u4le()
            self.index_id = self._io.read_u4le()
            self.bounding_box = Sbc156.Tbox(self._io, self, self._root)
            self.bounding_box._read()
            self.min = []
            for i in range(2):
                _t_min = Sbc156.Vec3(self._io, self, self._root)
                try:
                    _t_min._read()
                finally:
                    self.min.append(_t_min)

            self.max = []
            for i in range(2):
                _t_max = Sbc156.Vec3(self._io, self, self._root)
                try:
                    _t_max._read()
                finally:
                    self.max.append(_t_max)

            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())

            self._dirty = False


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
            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self._root, self.bounding_box._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self, self.bounding_box._parent)
            if len(self.min) != 2:
                raise kaitaistruct.ConsistencyError(u"min", 2, len(self.min))
            for i in range(len(self.min)):
                pass
                if self.min[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"min", self._root, self.min[i]._root)
                if self.min[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"min", self, self.min[i]._parent)

            if len(self.max) != 2:
                raise kaitaistruct.ConsistencyError(u"max", 2, len(self.max))
            for i in range(len(self.max)):
                pass
                if self.max[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"max", self._root, self.max[i]._root)
                if self.max[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"max", self, self.max[i]._parent)

            if len(self.child_index) != 2:
                raise kaitaistruct.ConsistencyError(u"child_index", 2, len(self.child_index))
            for i in range(len(self.child_index)):
                pass

            self._dirty = False


    class Pbox(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Pbox, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = Sbc156.Vec4(self._io, self, self._root)
            self.min._read()
            self.max = Sbc156.Vec4(self._io, self, self._root)
            self.max._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Pbox, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self._root, self.min._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self, self.min._parent)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self._root, self.max._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self, self.max._parent)
            self._dirty = False


    class Re5boxes(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Re5boxes, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.boxes = []
            for i in range(2):
                _t_boxes = Sbc156.Pbox(self._io, self, self._root)
                try:
                    _t_boxes._read()
                finally:
                    self.boxes.append(_t_boxes)

            self.bit = self._io.read_u2le()
            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())

            self.nulls = []
            for i in range(10):
                self.nulls.append(self._io.read_u1())

            self._dirty = False


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
            if len(self.boxes) != 2:
                raise kaitaistruct.ConsistencyError(u"boxes", 2, len(self.boxes))
            for i in range(len(self.boxes)):
                pass
                if self.boxes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"boxes", self._root, self.boxes[i]._root)
                if self.boxes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"boxes", self, self.boxes[i]._parent)

            if len(self.child_index) != 2:
                raise kaitaistruct.ConsistencyError(u"child_index", 2, len(self.child_index))
            for i in range(len(self.child_index)):
                pass

            if len(self.nulls) != 10:
                raise kaitaistruct.ConsistencyError(u"nulls", 10, len(self.nulls))
            for i in range(len(self.nulls)):
                pass

            self._dirty = False


    class Re5triangle(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Re5triangle, self).__init__(_io)
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
            self._dirty = False


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
            if len(self.vert) != 3:
                raise kaitaistruct.ConsistencyError(u"vert", 3, len(self.vert))
            for i in range(len(self.vert)):
                pass

            self._dirty = False


    class Rgba(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Rgba, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.red = self._io.read_u1()
            self.green = self._io.read_u1()
            self.blue = self._io.read_u1()
            self.alpha = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sbc156.Rgba, self)._write__seq(io)
            self._io.write_u1(self.red)
            self._io.write_u1(self.green)
            self._io.write_u1(self.blue)
            self._io.write_u1(self.alpha)


        def _check(self):
            self._dirty = False


    class SbcHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.SbcHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x53\x42\x43\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.magic, self._io, u"/types/sbc_header/seq/0")
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
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.bbox._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.SbcHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.version)
            self._io.write_u2le(self.num_groups)
            self._io.write_u2le(self.num_groups_nodes)
            self._io.write_u1(self.max_parts_nest_count)
            self._io.write_u1(self.max_nest_count)
            self._io.write_u4le(self.num_boxes)
            self._io.write_u4le(self.num_faces)
            self._io.write_u4le(self.num_vertices)
            self.bbox._write__seq(self._io)


        def _check(self):
            if len(self.magic) != 4:
                raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
            if not self.magic == b"\x53\x42\x43\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.magic, None, u"/types/sbc_header/seq/0")
            if self.bbox._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bbox", self._root, self.bbox._root)
            if self.bbox._parent != self:
                raise kaitaistruct.ConsistencyError(u"bbox", self, self.bbox._parent)
            self._dirty = False


    class SbcHeaderOg(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.SbcHeaderOg, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x53\x42\x43\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.magic, self._io, u"/types/sbc_header_og/seq/0")
            self.version = self._io.read_u2le()
            self.num_infos = self._io.read_u2le()
            self.num_parts = self._io.read_u2le()
            self.num_parts_nest = self._io.read_u1()
            self.max_nest_count = self._io.read_u1()
            self.num_nodes = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.box = Sbc156.Tbox(self._io, self, self._root)
            self.box._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.box._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.SbcHeaderOg, self)._write__seq(io)
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
            if len(self.magic) != 4:
                raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
            if not self.magic == b"\x53\x42\x43\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.magic, None, u"/types/sbc_header_og/seq/0")
            if self.box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"box", self._root, self.box._root)
            if self.box._parent != self:
                raise kaitaistruct.ConsistencyError(u"box", self, self.box._parent)
            self._dirty = False


    class Sbcgroup(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Sbcgroup, self).__init__(_io)
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
                try:
                    _t_vmin._read()
                finally:
                    self.vmin.append(_t_vmin)

            self.vmax = []
            for i in range(2):
                _t_vmax = Sbc156.Vec3(self._io, self, self._root)
                try:
                    _t_vmax._read()
                finally:
                    self.vmax.append(_t_vmax)

            self.child_index = []
            for i in range(2):
                self.child_index.append(self._io.read_u2le())

            self._dirty = False


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
            if self.bbox_this._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bbox_this", self._root, self.bbox_this._root)
            if self.bbox_this._parent != self:
                raise kaitaistruct.ConsistencyError(u"bbox_this", self, self.bbox_this._parent)
            if len(self.vmin) != 2:
                raise kaitaistruct.ConsistencyError(u"vmin", 2, len(self.vmin))
            for i in range(len(self.vmin)):
                pass
                if self.vmin[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"vmin", self._root, self.vmin[i]._root)
                if self.vmin[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"vmin", self, self.vmin[i]._parent)

            if len(self.vmax) != 2:
                raise kaitaistruct.ConsistencyError(u"vmax", 2, len(self.vmax))
            for i in range(len(self.vmax)):
                pass
                if self.vmax[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"vmax", self._root, self.vmax[i]._root)
                if self.vmax[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"vmax", self, self.vmax[i]._parent)

            if len(self.child_index) != 2:
                raise kaitaistruct.ConsistencyError(u"child_index", 2, len(self.child_index))
            for i in range(len(self.child_index)):
                pass

            self._dirty = False


    class Tbox(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Tbox, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = Sbc156.Vec3(self._io, self, self._root)
            self.min._read()
            self.max = Sbc156.Vec3(self._io, self, self._root)
            self.max._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Tbox, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self._root, self.min._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self, self.min._parent)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self._root, self.max._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self, self.max._parent)
            self._dirty = False


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Vec3, self).__init__(_io)
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
            super(Sbc156.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Vec4, self).__init__(_io)
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
            super(Sbc156.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    class Vertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Vertex, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vector = Sbc156.Vec4(self._io, self, self._root)
            self.vector._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.vector._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.Vertex, self)._write__seq(io)
            self.vector._write__seq(self._io)


        def _check(self):
            if self.vector._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vector", self._root, self.vector._root)
            if self.vector._parent != self:
                raise kaitaistruct.ConsistencyError(u"vector", self, self.vector._parent)
            self._dirty = False



