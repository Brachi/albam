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
        self.nodes = []
        for i in range(self.header.num_boxes):
            _t_nodes = Sbc156.BvhNode(self._io, self, self._root)
            try:
                _t_nodes._read()
            finally:
                self.nodes.append(_t_nodes)

        self.sbc_info = []
        for i in range(self.header.num_objects):
            _t_sbc_info = Sbc156.Info(self._io, self, self._root)
            try:
                _t_sbc_info._read()
            finally:
                self.sbc_info.append(_t_sbc_info)

        self.faces = []
        for i in range(self.header.num_faces):
            _t_faces = Sbc156.Face(self._io, self, self._root)
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
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.nodes) != self.header.num_boxes:
            raise kaitaistruct.ConsistencyError(u"nodes", self.header.num_boxes, len(self.nodes))
        for i in range(len(self.nodes)):
            pass
            if self.nodes[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"nodes", self._root, self.nodes[i]._root)
            if self.nodes[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"nodes", self, self.nodes[i]._parent)

        if len(self.sbc_info) != self.header.num_objects:
            raise kaitaistruct.ConsistencyError(u"sbc_info", self.header.num_objects, len(self.sbc_info))
        for i in range(len(self.sbc_info)):
            pass
            if self.sbc_info[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self._root, self.sbc_info[i]._root)
            if self.sbc_info[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"sbc_info", self, self.sbc_info[i]._parent)

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

    class Bbox3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Bbox3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = []
            for i in range(3):
                self.min.append(self._io.read_f4le())

            self.max = []
            for i in range(3):
                self.max.append(self._io.read_f4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.min)):
                pass

            for i in range(len(self.max)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Bbox3, self)._write__seq(io)
            for i in range(len(self.min)):
                pass
                self._io.write_f4le(self.min[i])

            for i in range(len(self.max)):
                pass
                self._io.write_f4le(self.max[i])



        def _check(self):
            if len(self.min) != 3:
                raise kaitaistruct.ConsistencyError(u"min", 3, len(self.min))
            for i in range(len(self.min)):
                pass

            if len(self.max) != 3:
                raise kaitaistruct.ConsistencyError(u"max", 3, len(self.max))
            for i in range(len(self.max)):
                pass

            self._dirty = False


    class Bbox4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Bbox4, self).__init__(_io)
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
            super(Sbc156.Bbox4, self)._write__seq(io)
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


    class BvhNode(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.BvhNode, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.boxes = []
            for i in range(2):
                _t_boxes = Sbc156.Bbox4(self._io, self, self._root)
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
            super(Sbc156.BvhNode, self)._write__seq(io)
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


    class Face(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Face, self).__init__(_io)
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
            super(Sbc156.Face, self)._write__seq(io)
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


    class Info(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.Info, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.base = self._io.read_u4le()
            self.start_faces = self._io.read_u4le()
            self.start_nodes = self._io.read_u4le()
            self.start_vertices = self._io.read_u4le()
            self.index_id = self._io.read_u4le()
            self.bounding_box = Sbc156.Bbox3(self._io, self, self._root)
            self.bounding_box._read()
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
            self.bounding_box._fetch_instances()
            for i in range(len(self.vmin)):
                pass
                self.vmin[i]._fetch_instances()

            for i in range(len(self.vmax)):
                pass
                self.vmax[i]._fetch_instances()

            for i in range(len(self.child_index)):
                pass



        def _write__seq(self, io=None):
            super(Sbc156.Info, self)._write__seq(io)
            self._io.write_u4le(self.base)
            self._io.write_u4le(self.start_faces)
            self._io.write_u4le(self.start_nodes)
            self._io.write_u4le(self.start_vertices)
            self._io.write_u4le(self.index_id)
            self.bounding_box._write__seq(self._io)
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
            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self._root, self.bounding_box._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self, self.bounding_box._parent)
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


    class SbcHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Sbc156.SbcHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.indent = self._io.read_bytes(4)
            if not self.indent == b"\x53\x42\x43\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.indent, self._io, u"/types/sbc_header/seq/0")
            self.version = self._io.read_u2le()
            self.num_objects = self._io.read_u2le()
            self.num_objects_nodes = self._io.read_u2le()
            self.num_max_objects_nest = self._io.read_u1()
            self.num_max_nest = self._io.read_u1()
            self.num_boxes = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.bounding_box = Sbc156.Bbox3(self._io, self, self._root)
            self.bounding_box._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.bounding_box._fetch_instances()


        def _write__seq(self, io=None):
            super(Sbc156.SbcHeader, self)._write__seq(io)
            self._io.write_bytes(self.indent)
            self._io.write_u2le(self.version)
            self._io.write_u2le(self.num_objects)
            self._io.write_u2le(self.num_objects_nodes)
            self._io.write_u1(self.num_max_objects_nest)
            self._io.write_u1(self.num_max_nest)
            self._io.write_u4le(self.num_boxes)
            self._io.write_u4le(self.num_faces)
            self._io.write_u4le(self.num_vertices)
            self.bounding_box._write__seq(self._io)


        def _check(self):
            if len(self.indent) != 4:
                raise kaitaistruct.ConsistencyError(u"indent", 4, len(self.indent))
            if not self.indent == b"\x53\x42\x43\x31":
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.indent, None, u"/types/sbc_header/seq/0")
            if self.bounding_box._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self._root, self.bounding_box._root)
            if self.bounding_box._parent != self:
                raise kaitaistruct.ConsistencyError(u"bounding_box", self, self.bounding_box._parent)
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
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sbc156.Vertex, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False



