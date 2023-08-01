# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class MtframeworkSbc(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x53\x42\x43\x31":
            raise kaitaistruct.ValidationNotEqualError(b"\x53\x42\x43\x31", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u2le()
        self.num_groups = self._io.read_u2le()
        self.num_groups_bb = self._io.read_u2le()
        self.unk_num_03 = self._io.read_u2le()
        self.num_boxes = self._io.read_u4le()
        self.num_faces = self._io.read_u4le()
        self.num_vertices = self._io.read_u4le()
        self.bbox = MtframeworkSbc.Tbox(self._io, self, self._root)
        self.boxes = []
        for i in range(self.num_boxes):
            self.boxes.append(MtframeworkSbc.Re5boxes(self._io, self, self._root))

        self.groups = []
        for i in range(self.num_groups):
            self.groups.append(MtframeworkSbc.Sbcgroup(self._io, self, self._root))

        self.triangles = []
        for i in range(self.num_faces):
            self.triangles.append(MtframeworkSbc.Re5triangle(self._io, self, self._root))

        self.vertices = []
        for i in range(self.num_vertices):
            self.vertices.append(MtframeworkSbc.Vertex(self._io, self, self._root))


    class Vec4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


    class Pbox(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = MtframeworkSbc.Vec4(self._io, self, self._root)
            self.max = MtframeworkSbc.Vec4(self._io, self, self._root)


    class Sbcgroup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.base = self._io.read_u4le()
            self.start_tris = self._io.read_u4le()
            self.start_boxes = self._io.read_u4le()
            self.start_vertices = self._io.read_u4le()
            self.group_id = self._io.read_u4le()
            self.boxa = MtframeworkSbc.Tbox(self._io, self, self._root)
            self.boxb = MtframeworkSbc.Tbox(self._io, self, self._root)
            self.boxc = MtframeworkSbc.Tbox(self._io, self, self._root)
            self.ida = self._io.read_u2le()
            self.idb = self._io.read_u2le()


    class Vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vector = MtframeworkSbc.Vec4(self._io, self, self._root)


    class Rgba(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.red = self._io.read_u1()
            self.green = self._io.read_u1()
            self.blue = self._io.read_u1()
            self.alpha = self._io.read_u1()


    class Tbox(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = MtframeworkSbc.Vec3(self._io, self, self._root)
            self.max = MtframeworkSbc.Vec3(self._io, self, self._root)


    class Re5triangle(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a = self._io.read_u2le()
            self.b = self._io.read_u2le()
            self.c = self._io.read_u2le()
            self.unk_00 = self._io.read_u1()
            self.unk_01 = self._io.read_u1()
            self.unk_02 = self._io.read_u4le()
            self.unk_eff = self._io.read_u4le()
            self.nulls = []
            for i in range(3):
                self.nulls.append(self._io.read_u4le())



    class Vec3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


    class Re5boxes(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.boxa = MtframeworkSbc.Pbox(self._io, self, self._root)
            self.boxb = MtframeworkSbc.Pbox(self._io, self, self._root)
            self.ida = self._io.read_u2le()
            self.idb = self._io.read_u2le()
            self.idc = self._io.read_u2le()
            self.nulls = []
            for i in range(10):
                self.nulls.append(self._io.read_u1())




