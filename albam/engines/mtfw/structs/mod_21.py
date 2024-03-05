# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mod21(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_vertex_buffer = False
        self.vertex_buffer__to_write = True
        self._should_write_materials_data = False
        self.materials_data__to_write = True
        self._should_write_meshes_data = False
        self.meshes_data__to_write = True
        self._should_write_index_buffer = False
        self.index_buffer__to_write = True
        self._should_write_bones_data = False
        self.bones_data__to_write = True
        self._should_write_groups = False
        self.groups__to_write = True

    def _read(self):
        self.header = Mod21.ModHeader(self._io, self, self._root)
        self.header._read()
        self.bsphere = Mod21.Vec4(self._io, self, self._root)
        self.bsphere._read()
        self.bbox_min = Mod21.Vec4(self._io, self, self._root)
        self.bbox_min._read()
        self.bbox_max = Mod21.Vec4(self._io, self, self._root)
        self.bbox_max._read()
        self.unk_01 = self._io.read_u4le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        if (self._root.header.version == 210):
            pass
            self.num_weight_bounds = self._io.read_u4le()



    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        self.bsphere._fetch_instances()
        self.bbox_min._fetch_instances()
        self.bbox_max._fetch_instances()
        if (self._root.header.version == 210):
            pass

        _ = self.vertex_buffer
        if (self.header.offset_materials_data > 0):
            pass
            _ = self.materials_data
            self.materials_data._fetch_instances()

        if (self.header.offset_meshes_data > 0):
            pass
            _ = self.meshes_data
            self.meshes_data._fetch_instances()

        _ = self.index_buffer
        if (self.header.num_bones != 0):
            pass
            _ = self.bones_data
            self.bones_data._fetch_instances()

        _ = self.groups
        for i in range(len(self._m_groups)):
            pass
            self.groups[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Mod21, self)._write__seq(io)
        self._should_write_vertex_buffer = self.vertex_buffer__to_write
        self._should_write_materials_data = self.materials_data__to_write
        self._should_write_meshes_data = self.meshes_data__to_write
        self._should_write_index_buffer = self.index_buffer__to_write
        self._should_write_bones_data = self.bones_data__to_write
        self._should_write_groups = self.groups__to_write
        self.header._write__seq(self._io)
        self.bsphere._write__seq(self._io)
        self.bbox_min._write__seq(self._io)
        self.bbox_max._write__seq(self._io)
        self._io.write_u4le(self.unk_01)
        self._io.write_u4le(self.unk_02)
        self._io.write_u4le(self.unk_03)
        self._io.write_u4le(self.unk_04)
        if (self._root.header.version == 210):
            pass
            self._io.write_u4le(self.num_weight_bounds)



    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)
        if self.bsphere._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bsphere", self.bsphere._root, self._root)
        if self.bsphere._parent != self:
            raise kaitaistruct.ConsistencyError(u"bsphere", self.bsphere._parent, self)
        if self.bbox_min._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bbox_min", self.bbox_min._root, self._root)
        if self.bbox_min._parent != self:
            raise kaitaistruct.ConsistencyError(u"bbox_min", self.bbox_min._parent, self)
        if self.bbox_max._root != self._root:
            raise kaitaistruct.ConsistencyError(u"bbox_max", self.bbox_max._root, self._root)
        if self.bbox_max._parent != self:
            raise kaitaistruct.ConsistencyError(u"bbox_max", self.bbox_max._parent, self)
        if (self._root.header.version == 210):
            pass


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
            super(Mod21.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class ModHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ident = self._io.read_bytes(4)
            if not (self.ident == b"\x4D\x4F\x44\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x4D\x4F\x44\x00", self.ident, self._io, u"/types/mod_header/seq/0")
            self.version = self._io.read_u1()
            self.revision = self._io.read_u1()
            self.num_bones = self._io.read_u2le()
            self.num_meshes = self._io.read_u2le()
            self.num_materials = self._io.read_u2le()
            self.num_vertices = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_edges = self._io.read_u4le()
            self.size_vertex_buffer = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.num_groups = self._io.read_u4le()
            self.offset_bones_data = self._io.read_u4le()
            self.offset_groups = self._io.read_u4le()
            self.offset_materials_data = self._io.read_u4le()
            self.offset_meshes_data = self._io.read_u4le()
            self.offset_vertex_buffer = self._io.read_u4le()
            self.offset_index_buffer = self._io.read_u4le()
            self.size_file = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.ModHeader, self)._write__seq(io)
            self._io.write_bytes(self.ident)
            self._io.write_u1(self.version)
            self._io.write_u1(self.revision)
            self._io.write_u2le(self.num_bones)
            self._io.write_u2le(self.num_meshes)
            self._io.write_u2le(self.num_materials)
            self._io.write_u4le(self.num_vertices)
            self._io.write_u4le(self.num_faces)
            self._io.write_u4le(self.num_edges)
            self._io.write_u4le(self.size_vertex_buffer)
            self._io.write_u4le(self.reserved_01)
            self._io.write_u4le(self.num_groups)
            self._io.write_u4le(self.offset_bones_data)
            self._io.write_u4le(self.offset_groups)
            self._io.write_u4le(self.offset_materials_data)
            self._io.write_u4le(self.offset_meshes_data)
            self._io.write_u4le(self.offset_vertex_buffer)
            self._io.write_u4le(self.offset_index_buffer)
            self._io.write_u4le(self.size_file)


        def _check(self):
            pass
            if (len(self.ident) != 4):
                raise kaitaistruct.ConsistencyError(u"ident", len(self.ident), 4)
            if not (self.ident == b"\x4D\x4F\x44\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x4D\x4F\x44\x00", self.ident, None, u"/types/mod_header/seq/0")

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 64
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexA7d7(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.uv._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexA7d7, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 20
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex2082(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex2082, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec2HalfFloat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.u = self._io.read_bytes(2)
            self.v = self._io.read_bytes(2)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.Vec2HalfFloat, self)._write__seq(io)
            self._io.write_bytes(self.u)
            self._io.write_bytes(self.v)


        def _check(self):
            pass
            if (len(self.u) != 2):
                raise kaitaistruct.ConsistencyError(u"u", len(self.u), 2)
            if (len(self.v) != 2):
                raise kaitaistruct.ConsistencyError(u"v", len(self.v), 2)


    class VertexA8fa(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexA8fa, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u2le(self.bone_indices[i])

            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 1):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 1)
            for i in range(len(self.bone_indices)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 20
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec3U1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.Vec3U1, self)._write__seq(io)
            self._io.write_u1(self.x)
            self._io.write_u1(self.y)
            self._io.write_u1(self.z)


        def _check(self):
            pass


    class VertexB098(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.normal._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexB098, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u2le(self.bone_indices[i])

            self.normal._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 1):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 1)
            for i in range(len(self.bone_indices)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 12
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexB668(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.rgba._fetch_instances()
            self.uv3._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexB668, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.rgba._write__seq(self._io)
            self.uv3._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Matrix4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.row_1 = Mod21.Vec4(self._io, self, self._root)
            self.row_1._read()
            self.row_2 = Mod21.Vec4(self._io, self, self._root)
            self.row_2._read()
            self.row_3 = Mod21.Vec4(self._io, self, self._root)
            self.row_3._read()
            self.row_4 = Mod21.Vec4(self._io, self, self._root)
            self.row_4._read()


        def _fetch_instances(self):
            pass
            self.row_1._fetch_instances()
            self.row_2._fetch_instances()
            self.row_3._fetch_instances()
            self.row_4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Matrix4x4, self)._write__seq(io)
            self.row_1._write__seq(self._io)
            self.row_2._write__seq(self._io)
            self.row_3._write__seq(self._io)
            self.row_4._write__seq(self._io)


        def _check(self):
            pass
            if self.row_1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_1", self.row_1._root, self._root)
            if self.row_1._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_1", self.row_1._parent, self)
            if self.row_2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_2", self.row_2._root, self._root)
            if self.row_2._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_2", self.row_2._parent, self)
            if self.row_3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_3", self.row_3._root, self._root)
            if self.row_3._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_3", self.row_3._parent, self)
            if self.row_4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_4", self.row_4._root, self._root)
            if self.row_4._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_4", self.row_4._parent, self)


    class VertexBb42(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values2)):
                pass

            self.tangent._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexBb42, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values2)):
                pass
                self._io.write_bytes(self.weight_values2[i])

            self.tangent._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if (len(self.weight_values) != 4):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 4)
            for i in range(len(self.weight_values)):
                pass

            if (len(self.bone_indices) != 8):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 8)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values2) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2), 2)
            for i in range(len(self.weight_values2)):
                pass
                if (len(self.weight_values2[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2[i]), 2)

            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexD877(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()
            self.uv4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexD877, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u2le(self.bone_indices[i])

            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)
            self.uv4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 1):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 1)
            for i in range(len(self.bone_indices)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)
            if self.uv4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._root, self._root)
            if self.uv4._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexD84e(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values2)):
                pass

            self.tangent._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexD84e, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values2)):
                pass
                self._io.write_bytes(self.weight_values2[i])

            self.tangent._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if (len(self.weight_values) != 4):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 4)
            for i in range(len(self.weight_values)):
                pass

            if (len(self.bone_indices) != 8):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 8)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values2) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2), 2)
            for i in range(len(self.weight_values2)):
                pass
                if (len(self.weight_values2[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2[i]), 2)

            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 40
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex6459(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            self.uv2._fetch_instances()
            self.uv3._fetch_instances()
            self.uv4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex6459, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_bytes(self.weight_values[i])

            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)
            self.uv4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 2)
            for i in range(len(self.weight_values)):
                pass
                if (len(self.weight_values[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values[i]), 2)

            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)
            if self.uv4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._root, self._root)
            if self.uv4._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 40
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex926f(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex926f, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex667b(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex667b, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u2le(self.bone_indices[i])

            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 1):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 1)
            for i in range(len(self.bone_indices)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex77d8(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex77d8, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_bytes(self.weight_values[i])

            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 2)
            for i in range(len(self.weight_values)):
                pass
                if (len(self.weight_values[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values[i]), 2)

            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex63b6(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.vertex_alpha = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()
            self.occlusion = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex63b6, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.vertex_alpha)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)
            self._io.write_u4le(self.occlusion)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex5e7f(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex5e7f, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexA14e(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexA14e, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexB392(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()
            self.uv4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexB392, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_bytes(self.bone_indices[i])

            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)
            self.uv4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 2):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 2)
            for i in range(len(self.bone_indices)):
                pass
                if (len(self.bone_indices[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices[i]), 2)

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)
            if self.uv4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._root, self._root)
            if self.uv4._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexD9e8(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexD9e8, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_bytes(self.bone_indices[i])

            self.uv._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 2):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 2)
            for i in range(len(self.bone_indices)):
                pass
                if (len(self.bone_indices[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices[i]), 2)

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Bone(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.idx_anim_map = self._io.read_u1()
            self.idx_parent = self._io.read_u1()
            self.idx_mirror = self._io.read_u1()
            self.idx_mapping = self._io.read_u1()
            self.unk_01 = self._io.read_f4le()
            self.parent_distance = self._io.read_f4le()
            self.location = Mod21.Vec3(self._io, self, self._root)
            self.location._read()


        def _fetch_instances(self):
            pass
            self.location._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Bone, self)._write__seq(io)
            self._io.write_u1(self.idx_anim_map)
            self._io.write_u1(self.idx_parent)
            self._io.write_u1(self.idx_mirror)
            self._io.write_u1(self.idx_mapping)
            self._io.write_f4le(self.unk_01)
            self._io.write_f4le(self.parent_distance)
            self.location._write__seq(self._io)


        def _check(self):
            pass
            if self.location._root != self._root:
                raise kaitaistruct.ConsistencyError(u"location", self.location._root, self._root)
            if self.location._parent != self:
                raise kaitaistruct.ConsistencyError(u"location", self.location._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex2f55(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.morph_position = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position._read()
            self.morph_position2 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position2._read()
            self.morph_position3 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position3._read()
            self.morph_position4 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position4._read()
            self.morph_normal = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal._read()
            self.morph_normal2 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal2._read()
            self.morph_normal3 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal3._read()
            self.morph_normal4 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            self.morph_position._fetch_instances()
            self.morph_position2._fetch_instances()
            self.morph_position3._fetch_instances()
            self.morph_position4._fetch_instances()
            self.morph_normal._fetch_instances()
            self.morph_normal2._fetch_instances()
            self.morph_normal3._fetch_instances()
            self.morph_normal4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex2f55, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_bytes(self.weight_values[i])

            self.morph_position._write__seq(self._io)
            self.morph_position2._write__seq(self._io)
            self.morph_position3._write__seq(self._io)
            self.morph_position4._write__seq(self._io)
            self.morph_normal._write__seq(self._io)
            self.morph_normal2._write__seq(self._io)
            self.morph_normal3._write__seq(self._io)
            self.morph_normal4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 2)
            for i in range(len(self.weight_values)):
                pass
                if (len(self.weight_values[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values[i]), 2)

            if self.morph_position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position", self.morph_position._root, self._root)
            if self.morph_position._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position", self.morph_position._parent, self)
            if self.morph_position2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position2", self.morph_position2._root, self._root)
            if self.morph_position2._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position2", self.morph_position2._parent, self)
            if self.morph_position3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position3", self.morph_position3._root, self._root)
            if self.morph_position3._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position3", self.morph_position3._parent, self)
            if self.morph_position4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position4", self.morph_position4._root, self._root)
            if self.morph_position4._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position4", self.morph_position4._parent, self)
            if self.morph_normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal", self.morph_normal._root, self._root)
            if self.morph_normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal", self.morph_normal._parent, self)
            if self.morph_normal2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal2", self.morph_normal2._root, self._root)
            if self.morph_normal2._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal2", self.morph_normal2._parent, self)
            if self.morph_normal3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal3", self.morph_normal3._root, self._root)
            if self.morph_normal3._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal3", self.morph_normal3._parent, self)
            if self.morph_normal4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal4", self.morph_normal4._root, self._root)
            if self.morph_normal4._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal4", self.morph_normal4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 64
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex747d(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex747d, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexC31f(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))



        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass



        def _write__seq(self, io=None):
            super(Mod21.VertexC31f, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_bytes(self.bone_indices[i])



        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.bone_indices) != 2):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 2)
            for i in range(len(self.bone_indices)):
                pass
                if (len(self.bone_indices[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices[i]), 2)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex75c3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values2)):
                pass

            self.tangent._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex75c3, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values2)):
                pass
                self._io.write_bytes(self.weight_values2[i])

            self.tangent._write__seq(self._io)
            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if (len(self.weight_values) != 4):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 4)
            for i in range(len(self.weight_values)):
                pass

            if (len(self.bone_indices) != 8):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 8)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values2) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2), 2)
            for i in range(len(self.weight_values2)):
                pass
                if (len(self.weight_values2[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2[i]), 2)

            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 40
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexCbf6(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexCbf6, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u2le(self.bone_indices[i])

            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 1):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 1)
            for i in range(len(self.bone_indices)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec4U1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()
            self.w = self._io.read_u1()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.Vec4U1, self)._write__seq(io)
            self._io.write_u1(self.x)
            self._io.write_u1(self.y)
            self._io.write_u1(self.z)
            self._io.write_u1(self.w)


        def _check(self):
            pass


    class MeshesData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.meshes = []
            for i in range(self._root.header.num_meshes):
                _t_meshes = Mod21.Mesh(self._io, self, self._root)
                _t_meshes._read()
                self.meshes.append(_t_meshes)

            if (self._root.header.version == 211):
                pass
                self.num_weight_bounds = self._io.read_u4le()

            self.weight_bounds = []
            for i in range((self._root.num_weight_bounds if (self._root.header.version == 210) else self.num_weight_bounds)):
                _t_weight_bounds = Mod21.WeightBound(self._io, self, self._root)
                _t_weight_bounds._read()
                self.weight_bounds.append(_t_weight_bounds)



        def _fetch_instances(self):
            pass
            for i in range(len(self.meshes)):
                pass
                self.meshes[i]._fetch_instances()

            if (self._root.header.version == 211):
                pass

            for i in range(len(self.weight_bounds)):
                pass
                self.weight_bounds[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mod21.MeshesData, self)._write__seq(io)
            for i in range(len(self.meshes)):
                pass
                self.meshes[i]._write__seq(self._io)

            if (self._root.header.version == 211):
                pass
                self._io.write_u4le(self.num_weight_bounds)

            for i in range(len(self.weight_bounds)):
                pass
                self.weight_bounds[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.meshes) != self._root.header.num_meshes):
                raise kaitaistruct.ConsistencyError(u"meshes", len(self.meshes), self._root.header.num_meshes)
            for i in range(len(self.meshes)):
                pass
                if self.meshes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"meshes", self.meshes[i]._root, self._root)
                if self.meshes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"meshes", self.meshes[i]._parent, self)

            if (self._root.header.version == 211):
                pass

            if (len(self.weight_bounds) != (self._root.num_weight_bounds if (self._root.header.version == 210) else self.num_weight_bounds)):
                raise kaitaistruct.ConsistencyError(u"weight_bounds", len(self.weight_bounds), (self._root.num_weight_bounds if (self._root.header.version == 210) else self.num_weight_bounds))
            for i in range(len(self.weight_bounds)):
                pass
                if self.weight_bounds[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"weight_bounds", self.weight_bounds[i]._root, self._root)
                if self.weight_bounds[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"weight_bounds", self.weight_bounds[i]._parent, self)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = (((self._root.header.num_meshes * self.meshes[0].size_) + (self._root.num_weight_bounds * self.weight_bounds[0].size_)) if (self._root.header.version == 210) else ((self._root.header.num_meshes * self.meshes[0].size_) + (self.num_weight_bounds * self.weight_bounds[0].size_)))
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexA013(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))

            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexA013, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_bytes(self.bone_indices[i])

            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.bone_indices) != 2):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 2)
            for i in range(len(self.bone_indices)):
                pass
                if (len(self.bone_indices[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices[i]), 2)

            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex14d4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))



        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values)):
                pass



        def _write__seq(self, io=None):
            super(Mod21.Vertex14d4, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_bytes(self.weight_values[i])



        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 2)
            for i in range(len(self.weight_values)):
                pass
                if (len(self.weight_values[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values[i]), 2)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Mesh(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_indices = False
            self.indices__to_write = True
            self._should_write_vertices = False
            self.vertices__to_write = True

        def _read(self):
            self.idx_group = self._io.read_u2le()
            self.num_vertices = self._io.read_u2le()
            self.unk_01 = self._io.read_u1()
            self.idx_material = self._io.read_u2le()
            self.level_of_detail = self._io.read_u1()
            self.type_mesh = self._io.read_u1()
            self.unk_class_mesh = self._io.read_u1()
            self.vertex_stride = self._io.read_u1()
            self.unk_render_mode = self._io.read_u1()
            self.vertex_position = self._io.read_u4le()
            self.vertex_offset = self._io.read_u4le()
            self.vertex_format = self._io.read_u4le()
            self.face_position = self._io.read_u4le()
            self.num_indices = self._io.read_u4le()
            self.face_offset = self._io.read_u4le()
            self.bone_id_start = self._io.read_u1()
            self.num_unique_bone_ids = self._io.read_u1()
            self.mesh_index = self._io.read_u2le()
            self.min_index = self._io.read_u2le()
            self.max_index = self._io.read_u2le()
            self.hash = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.indices
            for i in range(len(self._m_indices)):
                pass

            _ = self.vertices
            for i in range(len(self._m_vertices)):
                pass
                _on = self.vertex_format
                if _on == 1585389612:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3094208554:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1672921135:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 933552181:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3663044641:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 794148925:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3273596956:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2456801326:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3329204282:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2685620254:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3141681188:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2706243644:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3626594344:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3421945882:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2835001368:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2476326963:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3012694047:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 307572786:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1126539326:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 545452091:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3060273204:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 349437984:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 545087543:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 213286933:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1719341081:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3682443284:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1236594729:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 228491293:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2010673186:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3631710235:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2815938614:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3517214776:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2736832534:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3419369511:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1683566627:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1975771173:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3629002790:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2946904109:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2962763795:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1954353201:
                    pass
                    self.vertices[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mod21.Mesh, self)._write__seq(io)
            self._should_write_indices = self.indices__to_write
            self._should_write_vertices = self.vertices__to_write
            self._io.write_u2le(self.idx_group)
            self._io.write_u2le(self.num_vertices)
            self._io.write_u1(self.unk_01)
            self._io.write_u2le(self.idx_material)
            self._io.write_u1(self.level_of_detail)
            self._io.write_u1(self.type_mesh)
            self._io.write_u1(self.unk_class_mesh)
            self._io.write_u1(self.vertex_stride)
            self._io.write_u1(self.unk_render_mode)
            self._io.write_u4le(self.vertex_position)
            self._io.write_u4le(self.vertex_offset)
            self._io.write_u4le(self.vertex_format)
            self._io.write_u4le(self.face_position)
            self._io.write_u4le(self.num_indices)
            self._io.write_u4le(self.face_offset)
            self._io.write_u1(self.bone_id_start)
            self._io.write_u1(self.num_unique_bone_ids)
            self._io.write_u2le(self.mesh_index)
            self._io.write_u2le(self.min_index)
            self._io.write_u2le(self.max_index)
            self._io.write_u4le(self.hash)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 48
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_
        @property
        def indices(self):
            if self._should_write_indices:
                self._write_indices()
            if hasattr(self, '_m_indices'):
                return self._m_indices

            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_index_buffer + (self.face_offset * 2)) + (self.face_position * 2)))
            self._m_indices = []
            for i in range(self.num_indices):
                self._m_indices.append(self._io.read_u2le())

            self._io.seek(_pos)
            return getattr(self, '_m_indices', None)

        @indices.setter
        def indices(self, v):
            self._m_indices = v

        def _write_indices(self):
            self._should_write_indices = False
            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_index_buffer + (self.face_offset * 2)) + (self.face_position * 2)))
            for i in range(len(self._m_indices)):
                pass
                self._io.write_u2le(self.indices[i])

            self._io.seek(_pos)


        def _check_indices(self):
            pass
            if (len(self.indices) != self.num_indices):
                raise kaitaistruct.ConsistencyError(u"indices", len(self.indices), self.num_indices)
            for i in range(len(self._m_indices)):
                pass


        @property
        def vertices(self):
            if self._should_write_vertices:
                self._write_vertices()
            if hasattr(self, '_m_vertices'):
                return self._m_vertices

            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_vertex_buffer + self.vertex_offset) + (self.vertex_position * self.vertex_stride)))
            self._m_vertices = []
            for i in range(self.num_vertices):
                _on = self.vertex_format
                if _on == 1585389612:
                    pass
                    _t__m_vertices = Mod21.Vertex5e7f(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3094208554:
                    pass
                    _t__m_vertices = Mod21.VertexB86d(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1672921135:
                    pass
                    _t__m_vertices = Mod21.Vertex63b6(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 933552181:
                    pass
                    _t__m_vertices = Mod21.Vertex37a4(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3663044641:
                    pass
                    _t__m_vertices = Mod21.VertexDa55(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 794148925:
                    pass
                    _t__m_vertices = Mod21.Vertex2f55(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3273596956:
                    pass
                    _t__m_vertices = Mod21.VertexC31f(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2456801326:
                    pass
                    _t__m_vertices = Mod21.Vertex926f(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3329204282:
                    pass
                    _t__m_vertices = Mod21.VertexC66f(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2685620254:
                    pass
                    _t__m_vertices = Mod21.VertexA013(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3141681188:
                    pass
                    _t__m_vertices = Mod21.VertexBb42(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2706243644:
                    pass
                    _t__m_vertices = Mod21.VertexA14e(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3626594344:
                    pass
                    _t__m_vertices = Mod21.Vertex8297(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3421945882:
                    pass
                    _t__m_vertices = Mod21.VertexCbf6(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2835001368:
                    pass
                    _t__m_vertices = Mod21.VertexA8fa(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2476326963:
                    pass
                    _t__m_vertices = Mod21.Vertex9399(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3012694047:
                    pass
                    _t__m_vertices = Mod21.VertexB392(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 307572786:
                    pass
                    _t__m_vertices = Mod21.Vertex1255(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1126539326:
                    pass
                    _t__m_vertices = Mod21.Vertex4325(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 545452091:
                    pass
                    _t__m_vertices = Mod21.Vertex2082(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3060273204:
                    pass
                    _t__m_vertices = Mod21.VertexB668(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 349437984:
                    pass
                    _t__m_vertices = Mod21.Vertex14d4(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 545087543:
                    pass
                    _t__m_vertices = Mod21.Vertex207d(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 213286933:
                    pass
                    _t__m_vertices = Mod21.VertexCb68(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1719341081:
                    pass
                    _t__m_vertices = Mod21.Vertex667b(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3682443284:
                    pass
                    _t__m_vertices = Mod21.VertexDb7d(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1236594729:
                    pass
                    _t__m_vertices = Mod21.Vertex49b4(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 228491293:
                    pass
                    _t__m_vertices = Mod21.VertexD9e8(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2010673186:
                    pass
                    _t__m_vertices = Mod21.Vertex77d8(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3631710235:
                    pass
                    _t__m_vertices = Mod21.VertexD877(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2815938614:
                    pass
                    _t__m_vertices = Mod21.VertexA7d7(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3517214776:
                    pass
                    _t__m_vertices = Mod21.VertexD1a4(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2736832534:
                    pass
                    _t__m_vertices = Mod21.VertexA320(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3419369511:
                    pass
                    _t__m_vertices = Mod21.VertexCbcf(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1683566627:
                    pass
                    _t__m_vertices = Mod21.Vertex6459(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1975771173:
                    pass
                    _t__m_vertices = Mod21.Vertex75c3(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3629002790:
                    pass
                    _t__m_vertices = Mod21.VertexD84e(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2946904109:
                    pass
                    _t__m_vertices = Mod21.VertexAfa6(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2962763795:
                    pass
                    _t__m_vertices = Mod21.VertexB098(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1954353201:
                    pass
                    _t__m_vertices = Mod21.Vertex747d(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)

            self._io.seek(_pos)
            return getattr(self, '_m_vertices', None)

        @vertices.setter
        def vertices(self, v):
            self._m_vertices = v

        def _write_vertices(self):
            self._should_write_vertices = False
            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_vertex_buffer + self.vertex_offset) + (self.vertex_position * self.vertex_stride)))
            for i in range(len(self._m_vertices)):
                pass
                _on = self.vertex_format
                if _on == 1585389612:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3094208554:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1672921135:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 933552181:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3663044641:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 794148925:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3273596956:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2456801326:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3329204282:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2685620254:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3141681188:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2706243644:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3626594344:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3421945882:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2835001368:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2476326963:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3012694047:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 307572786:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1126539326:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 545452091:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3060273204:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 349437984:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 545087543:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 213286933:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1719341081:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3682443284:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1236594729:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 228491293:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2010673186:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3631710235:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2815938614:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3517214776:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2736832534:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3419369511:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1683566627:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1975771173:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3629002790:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2946904109:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2962763795:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1954353201:
                    pass
                    self.vertices[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_vertices(self):
            pass
            if (len(self.vertices) != self.num_vertices):
                raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), self.num_vertices)
            for i in range(len(self._m_vertices)):
                pass
                _on = self.vertex_format
                if _on == 1585389612:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3094208554:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1672921135:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 933552181:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3663044641:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 794148925:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3273596956:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2456801326:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3329204282:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2685620254:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3141681188:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2706243644:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3626594344:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3421945882:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2835001368:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2476326963:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3012694047:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 307572786:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1126539326:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 545452091:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3060273204:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 349437984:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 545087543:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 213286933:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1719341081:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3682443284:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1236594729:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 228491293:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2010673186:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3631710235:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2815938614:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3517214776:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2736832534:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3419369511:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1683566627:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1975771173:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3629002790:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2946904109:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2962763795:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1954353201:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)



    class Vertex49b4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex49b4, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexD1a4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexD1a4, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex37a4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()
            self.uv4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex37a4, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)
            self.uv4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)
            if self.uv4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._root, self._root)
            if self.uv4._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex4325(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.morph_position = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position._read()
            self.morph_position2 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position2._read()
            self.morph_position3 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position3._read()
            self.morph_position4 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position4._read()
            self.morph_normal = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal._read()
            self.morph_normal2 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal2._read()
            self.morph_normal3 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal3._read()
            self.morph_normal4 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.morph_position._fetch_instances()
            self.morph_position2._fetch_instances()
            self.morph_position3._fetch_instances()
            self.morph_position4._fetch_instances()
            self.morph_normal._fetch_instances()
            self.morph_normal2._fetch_instances()
            self.morph_normal3._fetch_instances()
            self.morph_normal4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex4325, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.morph_position._write__seq(self._io)
            self.morph_position2._write__seq(self._io)
            self.morph_position3._write__seq(self._io)
            self.morph_position4._write__seq(self._io)
            self.morph_normal._write__seq(self._io)
            self.morph_normal2._write__seq(self._io)
            self.morph_normal3._write__seq(self._io)
            self.morph_normal4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.morph_position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position", self.morph_position._root, self._root)
            if self.morph_position._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position", self.morph_position._parent, self)
            if self.morph_position2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position2", self.morph_position2._root, self._root)
            if self.morph_position2._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position2", self.morph_position2._parent, self)
            if self.morph_position3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position3", self.morph_position3._root, self._root)
            if self.morph_position3._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position3", self.morph_position3._parent, self)
            if self.morph_position4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_position4", self.morph_position4._root, self._root)
            if self.morph_position4._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_position4", self.morph_position4._parent, self)
            if self.morph_normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal", self.morph_normal._root, self._root)
            if self.morph_normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal", self.morph_normal._parent, self)
            if self.morph_normal2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal2", self.morph_normal2._root, self._root)
            if self.morph_normal2._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal2", self.morph_normal2._parent, self)
            if self.morph_normal3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal3", self.morph_normal3._root, self._root)
            if self.morph_normal3._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal3", self.morph_normal3._parent, self)
            if self.morph_normal4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"morph_normal4", self.morph_normal4._root, self._root)
            if self.morph_normal4._parent != self:
                raise kaitaistruct.ConsistencyError(u"morph_normal4", self.morph_normal4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 64
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexDb7d(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass



        def _write__seq(self, io=None):
            super(Mod21.VertexDb7d, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])



        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexC66f(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexC66f, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexB86d(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.vertex_alpha = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.occlusion = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexB86d, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.vertex_alpha)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self._io.write_u4le(self.occlusion)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_floats = []
            for i in range(30):
                self.unk_floats.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_floats)):
                pass



        def _write__seq(self, io=None):
            super(Mod21.Material, self)._write__seq(io)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            for i in range(len(self.unk_floats)):
                pass
                self._io.write_f4le(self.unk_floats[i])



        def _check(self):
            pass
            if (len(self.unk_floats) != 30):
                raise kaitaistruct.ConsistencyError(u"unk_floats", len(self.unk_floats), 30)
            for i in range(len(self.unk_floats)):
                pass



    class Vertex207d(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.uv._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex207d, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class WeightBound(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bone_id = self._io.read_u4le()
            self.unk_01 = Mod21.Vec3(self._io, self, self._root)
            self.unk_01._read()
            self.bsphere = Mod21.Vec4(self._io, self, self._root)
            self.bsphere._read()
            self.bbox_min = Mod21.Vec4(self._io, self, self._root)
            self.bbox_min._read()
            self.bbox_max = Mod21.Vec4(self._io, self, self._root)
            self.bbox_max._read()
            self.oabb = Mod21.Matrix4x4(self._io, self, self._root)
            self.oabb._read()
            self.oabb_dimension = Mod21.Vec4(self._io, self, self._root)
            self.oabb_dimension._read()


        def _fetch_instances(self):
            pass
            self.unk_01._fetch_instances()
            self.bsphere._fetch_instances()
            self.bbox_min._fetch_instances()
            self.bbox_max._fetch_instances()
            self.oabb._fetch_instances()
            self.oabb_dimension._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.WeightBound, self)._write__seq(io)
            self._io.write_u4le(self.bone_id)
            self.unk_01._write__seq(self._io)
            self.bsphere._write__seq(self._io)
            self.bbox_min._write__seq(self._io)
            self.bbox_max._write__seq(self._io)
            self.oabb._write__seq(self._io)
            self.oabb_dimension._write__seq(self._io)


        def _check(self):
            pass
            if self.unk_01._root != self._root:
                raise kaitaistruct.ConsistencyError(u"unk_01", self.unk_01._root, self._root)
            if self.unk_01._parent != self:
                raise kaitaistruct.ConsistencyError(u"unk_01", self.unk_01._parent, self)
            if self.bsphere._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bsphere", self.bsphere._root, self._root)
            if self.bsphere._parent != self:
                raise kaitaistruct.ConsistencyError(u"bsphere", self.bsphere._parent, self)
            if self.bbox_min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bbox_min", self.bbox_min._root, self._root)
            if self.bbox_min._parent != self:
                raise kaitaistruct.ConsistencyError(u"bbox_min", self.bbox_min._parent, self)
            if self.bbox_max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bbox_max", self.bbox_max._root, self._root)
            if self.bbox_max._parent != self:
                raise kaitaistruct.ConsistencyError(u"bbox_max", self.bbox_max._parent, self)
            if self.oabb._root != self._root:
                raise kaitaistruct.ConsistencyError(u"oabb", self.oabb._root, self._root)
            if self.oabb._parent != self:
                raise kaitaistruct.ConsistencyError(u"oabb", self.oabb._parent, self)
            if self.oabb_dimension._root != self._root:
                raise kaitaistruct.ConsistencyError(u"oabb_dimension", self.oabb_dimension._root, self._root)
            if self.oabb_dimension._parent != self:
                raise kaitaistruct.ConsistencyError(u"oabb_dimension", self.oabb_dimension._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 144
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

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
            super(Mod21.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            pass


    class VertexA320(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(8):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            for i in range(len(self.weight_values)):
                pass

            self.normal._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexA320, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            self.normal._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 8):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 8)
            for i in range(len(self.bone_indices)):
                pass

            if (len(self.weight_values) != 8):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 8)
            for i in range(len(self.weight_values)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec3S2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.Vec3S2, self)._write__seq(io)
            self._io.write_s2le(self.x)
            self._io.write_s2le(self.y)
            self._io.write_s2le(self.z)


        def _check(self):
            pass


    class MaterialsData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            if (self._root.header.version == 210):
                pass
                self.material_names = []
                for i in range(self._root.header.num_materials):
                    self.material_names.append((KaitaiStream.bytes_terminate(self._io.read_bytes(128), 0, False)).decode("ASCII"))


            if (self._root.header.version == 211):
                pass
                self.material_hashes = []
                for i in range(self._root.header.num_materials):
                    self.material_hashes.append(self._io.read_u4le())




        def _fetch_instances(self):
            pass
            if (self._root.header.version == 210):
                pass
                for i in range(len(self.material_names)):
                    pass


            if (self._root.header.version == 211):
                pass
                for i in range(len(self.material_hashes)):
                    pass




        def _write__seq(self, io=None):
            super(Mod21.MaterialsData, self)._write__seq(io)
            if (self._root.header.version == 210):
                pass
                for i in range(len(self.material_names)):
                    pass
                    self._io.write_bytes_limit((self.material_names[i]).encode(u"ASCII"), 128, 0, 0)


            if (self._root.header.version == 211):
                pass
                for i in range(len(self.material_hashes)):
                    pass
                    self._io.write_u4le(self.material_hashes[i])




        def _check(self):
            pass
            if (self._root.header.version == 210):
                pass
                if (len(self.material_names) != self._root.header.num_materials):
                    raise kaitaistruct.ConsistencyError(u"material_names", len(self.material_names), self._root.header.num_materials)
                for i in range(len(self.material_names)):
                    pass
                    if (len((self.material_names[i]).encode(u"ASCII")) > 128):
                        raise kaitaistruct.ConsistencyError(u"material_names", len((self.material_names[i]).encode(u"ASCII")), 128)
                    if (KaitaiStream.byte_array_index_of((self.material_names[i]).encode(u"ASCII"), 0) != -1):
                        raise kaitaistruct.ConsistencyError(u"material_names", KaitaiStream.byte_array_index_of((self.material_names[i]).encode(u"ASCII"), 0), -1)


            if (self._root.header.version == 211):
                pass
                if (len(self.material_hashes) != self._root.header.num_materials):
                    raise kaitaistruct.ConsistencyError(u"material_hashes", len(self.material_hashes), self._root.header.num_materials)
                for i in range(len(self.material_hashes)):
                    pass



        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = ((128 * self._root.header.num_materials) if (self._root.header.version == 210) else (4 * self._root.header.num_materials))
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexCbcf(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values2)):
                pass

            self.tangent._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()
            self.uv4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexCbcf, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values2)):
                pass
                self._io.write_bytes(self.weight_values2[i])

            self.tangent._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)
            self.uv4._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if (len(self.weight_values) != 4):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 4)
            for i in range(len(self.weight_values)):
                pass

            if (len(self.bone_indices) != 8):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 8)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values2) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2), 2)
            for i in range(len(self.weight_values2)):
                pass
                if (len(self.weight_values2[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values2", len(self.weight_values2[i]), 2)

            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)
            if self.uv4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._root, self._root)
            if self.uv4._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv4", self.uv4._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 48
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class BonesData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bones_hierarchy = []
            for i in range(self._root.header.num_bones):
                _t_bones_hierarchy = Mod21.Bone(self._io, self, self._root)
                _t_bones_hierarchy._read()
                self.bones_hierarchy.append(_t_bones_hierarchy)

            self.parent_space_matrices = []
            for i in range(self._root.header.num_bones):
                _t_parent_space_matrices = Mod21.Matrix4x4(self._io, self, self._root)
                _t_parent_space_matrices._read()
                self.parent_space_matrices.append(_t_parent_space_matrices)

            self.inverse_bind_matrices = []
            for i in range(self._root.header.num_bones):
                _t_inverse_bind_matrices = Mod21.Matrix4x4(self._io, self, self._root)
                _t_inverse_bind_matrices._read()
                self.inverse_bind_matrices.append(_t_inverse_bind_matrices)

            if (self._root.header.num_bones != 0):
                pass
                self.bone_map = self._io.read_bytes(256)



        def _fetch_instances(self):
            pass
            for i in range(len(self.bones_hierarchy)):
                pass
                self.bones_hierarchy[i]._fetch_instances()

            for i in range(len(self.parent_space_matrices)):
                pass
                self.parent_space_matrices[i]._fetch_instances()

            for i in range(len(self.inverse_bind_matrices)):
                pass
                self.inverse_bind_matrices[i]._fetch_instances()

            if (self._root.header.num_bones != 0):
                pass



        def _write__seq(self, io=None):
            super(Mod21.BonesData, self)._write__seq(io)
            for i in range(len(self.bones_hierarchy)):
                pass
                self.bones_hierarchy[i]._write__seq(self._io)

            for i in range(len(self.parent_space_matrices)):
                pass
                self.parent_space_matrices[i]._write__seq(self._io)

            for i in range(len(self.inverse_bind_matrices)):
                pass
                self.inverse_bind_matrices[i]._write__seq(self._io)

            if (self._root.header.num_bones != 0):
                pass
                self._io.write_bytes(self.bone_map)



        def _check(self):
            pass
            if (len(self.bones_hierarchy) != self._root.header.num_bones):
                raise kaitaistruct.ConsistencyError(u"bones_hierarchy", len(self.bones_hierarchy), self._root.header.num_bones)
            for i in range(len(self.bones_hierarchy)):
                pass
                if self.bones_hierarchy[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bones_hierarchy", self.bones_hierarchy[i]._root, self._root)
                if self.bones_hierarchy[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bones_hierarchy", self.bones_hierarchy[i]._parent, self)

            if (len(self.parent_space_matrices) != self._root.header.num_bones):
                raise kaitaistruct.ConsistencyError(u"parent_space_matrices", len(self.parent_space_matrices), self._root.header.num_bones)
            for i in range(len(self.parent_space_matrices)):
                pass
                if self.parent_space_matrices[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"parent_space_matrices", self.parent_space_matrices[i]._root, self._root)
                if self.parent_space_matrices[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"parent_space_matrices", self.parent_space_matrices[i]._parent, self)

            if (len(self.inverse_bind_matrices) != self._root.header.num_bones):
                raise kaitaistruct.ConsistencyError(u"inverse_bind_matrices", len(self.inverse_bind_matrices), self._root.header.num_bones)
            for i in range(len(self.inverse_bind_matrices)):
                pass
                if self.inverse_bind_matrices[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"inverse_bind_matrices", self.inverse_bind_matrices[i]._root, self._root)
                if self.inverse_bind_matrices[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"inverse_bind_matrices", self.inverse_bind_matrices[i]._parent, self)

            if (self._root.header.num_bones != 0):
                pass
                if (len(self.bone_map) != 256):
                    raise kaitaistruct.ConsistencyError(u"bone_map", len(self.bone_map), 256)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = (((((self._root.header.num_bones * self.bones_hierarchy[0].size_) + (self._root.header.num_bones * 64)) + (self._root.header.num_bones * 64)) + 256) if (self._root.header.num_bones > 0) else 0)
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex8297(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex8297, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex1255(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.uv3._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex1255, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.uv3._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.uv3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._root, self._root)
            if self.uv3._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv3", self.uv3._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec4S2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()
            self.w = self._io.read_s2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.Vec4S2, self)._write__seq(io)
            self._io.write_s2le(self.x)
            self._io.write_s2le(self.y)
            self._io.write_s2le(self.z)
            self._io.write_s2le(self.w)


        def _check(self):
            pass


    class Group(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.group_index = self._io.read_u4le()
            self.unk_02 = self._io.read_f4le()
            self.unk_03 = self._io.read_f4le()
            self.unk_04 = self._io.read_f4le()
            self.unk_05 = self._io.read_f4le()
            self.unk_06 = self._io.read_f4le()
            self.unk_07 = self._io.read_f4le()
            self.unk_08 = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod21.Group, self)._write__seq(io)
            self._io.write_u4le(self.group_index)
            self._io.write_f4le(self.unk_02)
            self._io.write_f4le(self.unk_03)
            self._io.write_f4le(self.unk_04)
            self._io.write_f4le(self.unk_05)
            self._io.write_f4le(self.unk_06)
            self._io.write_f4le(self.unk_07)
            self._io.write_f4le(self.unk_08)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexAfa6(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexAfa6, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexCb68(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.normal._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            for i in range(len(self.weight_values)):
                pass

            self.normal._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexCb68, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            self.normal._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass

            if (len(self.weight_values) != 4):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 4)
            for i in range(len(self.weight_values)):
                pass

            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 20
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex9399(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()
            self.rgba._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.Vertex9399, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)
            self.rgba._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)
            if self.rgba._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._root, self._root)
            if self.rgba._parent != self:
                raise kaitaistruct.ConsistencyError(u"rgba", self.rgba._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class VertexDa55(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.normal._read()
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            self.uv._fetch_instances()
            for i in range(len(self.weight_values)):
                pass

            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod21.VertexDa55, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            self._io.write_u1(self.occlusion)
            self.tangent._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            self.uv._write__seq(self._io)
            for i in range(len(self.weight_values)):
                pass
                self._io.write_bytes(self.weight_values[i])

            self.uv2._write__seq(self._io)


        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)
            if (len(self.bone_indices) != 4):
                raise kaitaistruct.ConsistencyError(u"bone_indices", len(self.bone_indices), 4)
            for i in range(len(self.bone_indices)):
                pass

            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)
            if (len(self.weight_values) != 2):
                raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values), 2)
            for i in range(len(self.weight_values)):
                pass
                if (len(self.weight_values[i]) != 2):
                    raise kaitaistruct.ConsistencyError(u"weight_values", len(self.weight_values[i]), 2)

            if self.uv2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._root, self._root)
            if self.uv2._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv2", self.uv2._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    @property
    def vertex_buffer(self):
        if self._should_write_vertex_buffer:
            self._write_vertex_buffer()
        if hasattr(self, '_m_vertex_buffer'):
            return self._m_vertex_buffer

        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_buffer)
        self._m_vertex_buffer = self._io.read_bytes(self.header.size_vertex_buffer)
        self._io.seek(_pos)
        return getattr(self, '_m_vertex_buffer', None)

    @vertex_buffer.setter
    def vertex_buffer(self, v):
        self._m_vertex_buffer = v

    def _write_vertex_buffer(self):
        self._should_write_vertex_buffer = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_buffer)
        self._io.write_bytes(self.vertex_buffer)
        self._io.seek(_pos)


    def _check_vertex_buffer(self):
        pass
        if (len(self.vertex_buffer) != self.header.size_vertex_buffer):
            raise kaitaistruct.ConsistencyError(u"vertex_buffer", len(self.vertex_buffer), self.header.size_vertex_buffer)

    @property
    def materials_data(self):
        if self._should_write_materials_data:
            self._write_materials_data()
        if hasattr(self, '_m_materials_data'):
            return self._m_materials_data

        if (self.header.offset_materials_data > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_materials_data)
            self._m_materials_data = Mod21.MaterialsData(self._io, self, self._root)
            self._m_materials_data._read()
            self._io.seek(_pos)

        return getattr(self, '_m_materials_data', None)

    @materials_data.setter
    def materials_data(self, v):
        self._m_materials_data = v

    def _write_materials_data(self):
        self._should_write_materials_data = False
        if (self.header.offset_materials_data > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_materials_data)
            self.materials_data._write__seq(self._io)
            self._io.seek(_pos)



    def _check_materials_data(self):
        pass
        if (self.header.offset_materials_data > 0):
            pass
            if self.materials_data._root != self._root:
                raise kaitaistruct.ConsistencyError(u"materials_data", self.materials_data._root, self._root)
            if self.materials_data._parent != self:
                raise kaitaistruct.ConsistencyError(u"materials_data", self.materials_data._parent, self)


    @property
    def bones_data_size_(self):
        if hasattr(self, '_m_bones_data_size_'):
            return self._m_bones_data_size_

        self._m_bones_data_size_ = (0 if (self.header.num_bones == 0) else self.bones_data.size_)
        return getattr(self, '_m_bones_data_size_', None)

    def _invalidate_bones_data_size_(self):
        del self._m_bones_data_size_
    @property
    def meshes_data(self):
        if self._should_write_meshes_data:
            self._write_meshes_data()
        if hasattr(self, '_m_meshes_data'):
            return self._m_meshes_data

        if (self.header.offset_meshes_data > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_meshes_data)
            self._m_meshes_data = Mod21.MeshesData(self._io, self, self._root)
            self._m_meshes_data._read()
            self._io.seek(_pos)

        return getattr(self, '_m_meshes_data', None)

    @meshes_data.setter
    def meshes_data(self, v):
        self._m_meshes_data = v

    def _write_meshes_data(self):
        self._should_write_meshes_data = False
        if (self.header.offset_meshes_data > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_meshes_data)
            self.meshes_data._write__seq(self._io)
            self._io.seek(_pos)



    def _check_meshes_data(self):
        pass
        if (self.header.offset_meshes_data > 0):
            pass
            if self.meshes_data._root != self._root:
                raise kaitaistruct.ConsistencyError(u"meshes_data", self.meshes_data._root, self._root)
            if self.meshes_data._parent != self:
                raise kaitaistruct.ConsistencyError(u"meshes_data", self.meshes_data._parent, self)


    @property
    def index_buffer(self):
        if self._should_write_index_buffer:
            self._write_index_buffer()
        if hasattr(self, '_m_index_buffer'):
            return self._m_index_buffer

        _pos = self._io.pos()
        self._io.seek(self.header.offset_index_buffer)
        self._m_index_buffer = self._io.read_bytes((self.header.num_faces * 2))
        self._io.seek(_pos)
        return getattr(self, '_m_index_buffer', None)

    @index_buffer.setter
    def index_buffer(self, v):
        self._m_index_buffer = v

    def _write_index_buffer(self):
        self._should_write_index_buffer = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_index_buffer)
        self._io.write_bytes(self.index_buffer)
        self._io.seek(_pos)


    def _check_index_buffer(self):
        pass
        if (len(self.index_buffer) != (self.header.num_faces * 2)):
            raise kaitaistruct.ConsistencyError(u"index_buffer", len(self.index_buffer), (self.header.num_faces * 2))

    @property
    def size_top_level_(self):
        if hasattr(self, '_m_size_top_level_'):
            return self._m_size_top_level_

        self._m_size_top_level_ = ((self._root.header.size_ + 68) if (self._root.header.version == 210) else (self._root.header.size_ + 64))
        return getattr(self, '_m_size_top_level_', None)

    def _invalidate_size_top_level_(self):
        del self._m_size_top_level_
    @property
    def bones_data(self):
        if self._should_write_bones_data:
            self._write_bones_data()
        if hasattr(self, '_m_bones_data'):
            return self._m_bones_data

        if (self.header.num_bones != 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones_data)
            self._m_bones_data = Mod21.BonesData(self._io, self, self._root)
            self._m_bones_data._read()
            self._io.seek(_pos)

        return getattr(self, '_m_bones_data', None)

    @bones_data.setter
    def bones_data(self, v):
        self._m_bones_data = v

    def _write_bones_data(self):
        self._should_write_bones_data = False
        if (self.header.num_bones != 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones_data)
            self.bones_data._write__seq(self._io)
            self._io.seek(_pos)



    def _check_bones_data(self):
        pass
        if (self.header.num_bones != 0):
            pass
            if self.bones_data._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bones_data", self.bones_data._root, self._root)
            if self.bones_data._parent != self:
                raise kaitaistruct.ConsistencyError(u"bones_data", self.bones_data._parent, self)


    @property
    def groups(self):
        if self._should_write_groups:
            self._write_groups()
        if hasattr(self, '_m_groups'):
            return self._m_groups

        _pos = self._io.pos()
        self._io.seek(self.header.offset_groups)
        self._m_groups = []
        for i in range(self.header.num_groups):
            _t__m_groups = Mod21.Group(self._io, self, self._root)
            _t__m_groups._read()
            self._m_groups.append(_t__m_groups)

        self._io.seek(_pos)
        return getattr(self, '_m_groups', None)

    @groups.setter
    def groups(self, v):
        self._m_groups = v

    def _write_groups(self):
        self._should_write_groups = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_groups)
        for i in range(len(self._m_groups)):
            pass
            self.groups[i]._write__seq(self._io)

        self._io.seek(_pos)


    def _check_groups(self):
        pass
        if (len(self.groups) != self.header.num_groups):
            raise kaitaistruct.ConsistencyError(u"groups", len(self.groups), self.header.num_groups)
        for i in range(len(self._m_groups)):
            pass
            if self.groups[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"groups", self.groups[i]._root, self._root)
            if self.groups[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"groups", self.groups[i]._parent, self)


    @property
    def groups_size_(self):
        if hasattr(self, '_m_groups_size_'):
            return self._m_groups_size_

        self._m_groups_size_ = (self.groups[0].size_ * self.header.num_groups)
        return getattr(self, '_m_groups_size_', None)

    def _invalidate_groups_size_(self):
        del self._m_groups_size_

