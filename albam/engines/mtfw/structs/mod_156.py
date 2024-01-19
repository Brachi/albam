# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mod156(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_vertex_buffer = False
        self.vertex_buffer__to_write = True
        self._should_write_materials_data = False
        self.materials_data__to_write = True
        self._should_write_vertex_buffer_2 = False
        self.vertex_buffer_2__to_write = True
        self._should_write_meshes_data = False
        self.meshes_data__to_write = True
        self._should_write_index_buffer = False
        self.index_buffer__to_write = True
        self._should_write_bones_data = False
        self.bones_data__to_write = True
        self._should_write_groups = False
        self.groups__to_write = True

    def _read(self):
        self.header = Mod156.ModHeader(self._io, self, self._root)
        self.header._read()
        self.reserved_01 = self._io.read_u4le()
        self.reserved_02 = self._io.read_u4le()
        self.bsphere = Mod156.Vec4(self._io, self, self._root)
        self.bsphere._read()
        self.bbox_min = Mod156.Vec4(self._io, self, self._root)
        self.bbox_min._read()
        self.bbox_max = Mod156.Vec4(self._io, self, self._root)
        self.bbox_max._read()
        self.unk_01 = self._io.read_u4le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        self.unk_05 = self._io.read_u4le()
        self.unk_06 = self._io.read_u4le()
        self.unk_07 = self._io.read_u4le()
        self.unk_08 = self._io.read_u4le()
        self.num_vtx8_unk_faces = self._io.read_u4le()
        self.num_vtx8_unk_uv = self._io.read_u4le()
        self.num_vtx8_unk_normals = self._io.read_u4le()
        self.reserved_03 = self._io.read_u4le()
        self.vtx8_unk_faces = []
        for i in range(self.num_vtx8_unk_faces):
            _t_vtx8_unk_faces = Mod156.UnkVtx8Block00(self._io, self, self._root)
            _t_vtx8_unk_faces._read()
            self.vtx8_unk_faces.append(_t_vtx8_unk_faces)

        self.vtx8_unk_uv = []
        for i in range(self.num_vtx8_unk_uv):
            _t_vtx8_unk_uv = Mod156.UnkVtx8Block01(self._io, self, self._root)
            _t_vtx8_unk_uv._read()
            self.vtx8_unk_uv.append(_t_vtx8_unk_uv)

        self.vtx8_unk_normals = []
        for i in range(self.num_vtx8_unk_normals):
            _t_vtx8_unk_normals = Mod156.UnkVtx8Block02(self._io, self, self._root)
            _t_vtx8_unk_normals._read()
            self.vtx8_unk_normals.append(_t_vtx8_unk_normals)



    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        self.bsphere._fetch_instances()
        self.bbox_min._fetch_instances()
        self.bbox_max._fetch_instances()
        for i in range(len(self.vtx8_unk_faces)):
            pass
            self.vtx8_unk_faces[i]._fetch_instances()

        for i in range(len(self.vtx8_unk_uv)):
            pass
            self.vtx8_unk_uv[i]._fetch_instances()

        for i in range(len(self.vtx8_unk_normals)):
            pass
            self.vtx8_unk_normals[i]._fetch_instances()

        if (self.header.offset_vertex_buffer > 0):
            pass
            _ = self.vertex_buffer

        if (self.header.offset_materials_data > 0):
            pass
            _ = self.materials_data
            self.materials_data._fetch_instances()

        if (self.header.offset_vertex_buffer_2 > 0):
            pass
            _ = self.vertex_buffer_2

        if (self.header.offset_meshes_data > 0):
            pass
            _ = self.meshes_data
            self.meshes_data._fetch_instances()

        if (self.header.offset_index_buffer > 0):
            pass
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
        super(Mod156, self)._write__seq(io)
        self._should_write_vertex_buffer = self.vertex_buffer__to_write
        self._should_write_materials_data = self.materials_data__to_write
        self._should_write_vertex_buffer_2 = self.vertex_buffer_2__to_write
        self._should_write_meshes_data = self.meshes_data__to_write
        self._should_write_index_buffer = self.index_buffer__to_write
        self._should_write_bones_data = self.bones_data__to_write
        self._should_write_groups = self.groups__to_write
        self.header._write__seq(self._io)
        self._io.write_u4le(self.reserved_01)
        self._io.write_u4le(self.reserved_02)
        self.bsphere._write__seq(self._io)
        self.bbox_min._write__seq(self._io)
        self.bbox_max._write__seq(self._io)
        self._io.write_u4le(self.unk_01)
        self._io.write_u4le(self.unk_02)
        self._io.write_u4le(self.unk_03)
        self._io.write_u4le(self.unk_04)
        self._io.write_u4le(self.unk_05)
        self._io.write_u4le(self.unk_06)
        self._io.write_u4le(self.unk_07)
        self._io.write_u4le(self.unk_08)
        self._io.write_u4le(self.num_vtx8_unk_faces)
        self._io.write_u4le(self.num_vtx8_unk_uv)
        self._io.write_u4le(self.num_vtx8_unk_normals)
        self._io.write_u4le(self.reserved_03)
        for i in range(len(self.vtx8_unk_faces)):
            pass
            self.vtx8_unk_faces[i]._write__seq(self._io)

        for i in range(len(self.vtx8_unk_uv)):
            pass
            self.vtx8_unk_uv[i]._write__seq(self._io)

        for i in range(len(self.vtx8_unk_normals)):
            pass
            self.vtx8_unk_normals[i]._write__seq(self._io)



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
        if (len(self.vtx8_unk_faces) != self.num_vtx8_unk_faces):
            raise kaitaistruct.ConsistencyError(u"vtx8_unk_faces", len(self.vtx8_unk_faces), self.num_vtx8_unk_faces)
        for i in range(len(self.vtx8_unk_faces)):
            pass
            if self.vtx8_unk_faces[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vtx8_unk_faces", self.vtx8_unk_faces[i]._root, self._root)
            if self.vtx8_unk_faces[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vtx8_unk_faces", self.vtx8_unk_faces[i]._parent, self)

        if (len(self.vtx8_unk_uv) != self.num_vtx8_unk_uv):
            raise kaitaistruct.ConsistencyError(u"vtx8_unk_uv", len(self.vtx8_unk_uv), self.num_vtx8_unk_uv)
        for i in range(len(self.vtx8_unk_uv)):
            pass
            if self.vtx8_unk_uv[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vtx8_unk_uv", self.vtx8_unk_uv[i]._root, self._root)
            if self.vtx8_unk_uv[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vtx8_unk_uv", self.vtx8_unk_uv[i]._parent, self)

        if (len(self.vtx8_unk_normals) != self.num_vtx8_unk_normals):
            raise kaitaistruct.ConsistencyError(u"vtx8_unk_normals", len(self.vtx8_unk_normals), self.num_vtx8_unk_normals)
        for i in range(len(self.vtx8_unk_normals)):
            pass
            if self.vtx8_unk_normals[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vtx8_unk_normals", self.vtx8_unk_normals[i]._root, self._root)
            if self.vtx8_unk_normals[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"vtx8_unk_normals", self.vtx8_unk_normals[i]._parent, self)


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
            super(Mod156.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class BonePalette(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_01 = self._io.read_u4le()
            self.indices = []
            for i in range(32):
                self.indices.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.indices)):
                pass



        def _write__seq(self, io=None):
            super(Mod156.BonePalette, self)._write__seq(io)
            self._io.write_u4le(self.unk_01)
            for i in range(len(self.indices)):
                pass
                self._io.write_u1(self.indices[i])



        def _check(self):
            pass
            if (len(self.indices) != 32):
                raise kaitaistruct.ConsistencyError(u"indices", len(self.indices), 32)
            for i in range(len(self.indices)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class UnkVtx8Block02(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u2le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.UnkVtx8Block02, self)._write__seq(io)
            self._io.write_u2le(self.unk_00)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u2le(self.unk_03)


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
            self.size_vertex_buffer_2 = self._io.read_u4le()
            self.num_textures = self._io.read_u4le()
            self.num_groups = self._io.read_u4le()
            self.num_bone_palettes = self._io.read_u4le()
            self.offset_bones_data = self._io.read_u4le()
            self.offset_groups = self._io.read_u4le()
            self.offset_materials_data = self._io.read_u4le()
            self.offset_meshes_data = self._io.read_u4le()
            self.offset_vertex_buffer = self._io.read_u4le()
            self.offset_vertex_buffer_2 = self._io.read_u4le()
            self.offset_index_buffer = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.ModHeader, self)._write__seq(io)
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
            self._io.write_u4le(self.size_vertex_buffer_2)
            self._io.write_u4le(self.num_textures)
            self._io.write_u4le(self.num_groups)
            self._io.write_u4le(self.num_bone_palettes)
            self._io.write_u4le(self.offset_bones_data)
            self._io.write_u4le(self.offset_groups)
            self._io.write_u4le(self.offset_materials_data)
            self._io.write_u4le(self.offset_meshes_data)
            self._io.write_u4le(self.offset_vertex_buffer)
            self._io.write_u4le(self.offset_vertex_buffer_2)
            self._io.write_u4le(self.offset_index_buffer)


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

            self._m_size_ = 72
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod156.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod156.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.tangent = Mod156.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            for i in range(len(self.weight_values)):
                pass

            self.normal._fetch_instances()
            self.tangent._fetch_instances()
            self.uv._fetch_instances()
            self.uv2._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Vertex, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            self.normal._write__seq(self._io)
            self.tangent._write__seq(self._io)
            self.uv._write__seq(self._io)
            self.uv2._write__seq(self._io)


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
            super(Mod156.Vec2HalfFloat, self)._write__seq(io)
            self._io.write_bytes(self.u)
            self._io.write_bytes(self.v)


        def _check(self):
            pass
            if (len(self.u) != 2):
                raise kaitaistruct.ConsistencyError(u"u", len(self.u), 2)
            if (len(self.v) != 2):
                raise kaitaistruct.ConsistencyError(u"v", len(self.v), 2)


    class Matrix4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.row_1 = Mod156.Vec4(self._io, self, self._root)
            self.row_1._read()
            self.row_2 = Mod156.Vec4(self._io, self, self._root)
            self.row_2._read()
            self.row_3 = Mod156.Vec4(self._io, self, self._root)
            self.row_3._read()
            self.row_4 = Mod156.Vec4(self._io, self, self._root)
            self.row_4._read()


        def _fetch_instances(self):
            pass
            self.row_1._fetch_instances()
            self.row_2._fetch_instances()
            self.row_3._fetch_instances()
            self.row_4._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Matrix4x4, self)._write__seq(io)
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
            self.location = Mod156.Vec3(self._io, self, self._root)
            self.location._read()


        def _fetch_instances(self):
            pass
            self.location._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Bone, self)._write__seq(io)
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

    class UnkVtx8Block00(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.idx = self._io.read_u2le()
            self.unk_00 = self._io.read_u2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.UnkVtx8Block00, self)._write__seq(io)
            self._io.write_u2le(self.idx)
            self._io.write_u2le(self.unk_00)


        def _check(self):
            pass


    class Vertex0(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod156.Vec3(self._io, self, self._root)
            self.position._read()
            self.normal = Mod156.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.tangent = Mod156.Vec4U1(self._io, self, self._root)
            self.tangent._read()
            self.uv = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()
            self.uv2 = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv2._read()
            self.uv3 = Mod156.Vec2HalfFloat(self._io, self, self._root)
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
            super(Mod156.Vertex0, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
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
            super(Mod156.Vec4U1, self)._write__seq(io)
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
                _t_meshes = Mod156.Mesh(self._io, self, self._root)
                _t_meshes._read()
                self.meshes.append(_t_meshes)

            self.num_weight_bounds = self._io.read_u4le()
            self.weight_bounds = []
            for i in range(self.num_weight_bounds):
                _t_weight_bounds = Mod156.WeightBound(self._io, self, self._root)
                _t_weight_bounds._read()
                self.weight_bounds.append(_t_weight_bounds)



        def _fetch_instances(self):
            pass
            for i in range(len(self.meshes)):
                pass
                self.meshes[i]._fetch_instances()

            for i in range(len(self.weight_bounds)):
                pass
                self.weight_bounds[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mod156.MeshesData, self)._write__seq(io)
            for i in range(len(self.meshes)):
                pass
                self.meshes[i]._write__seq(self._io)

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

            if (len(self.weight_bounds) != self.num_weight_bounds):
                raise kaitaistruct.ConsistencyError(u"weight_bounds", len(self.weight_bounds), self.num_weight_bounds)
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

            self._m_size_ = (((self._root.header.num_meshes * self.meshes[0].size_) + 4) + (self.num_weight_bounds * self.weight_bounds[0].size_))
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
            self.idx_material = self._io.read_u2le()
            self.constant = self._io.read_u1()
            self.level_of_detail = self._io.read_u1()
            self.z_buffer_order = self._io.read_u1()
            self.vertex_format = self._io.read_u1()
            self.vertex_stride = self._io.read_u1()
            self.vertex_stride_2 = self._io.read_u1()
            self.unk_03 = self._io.read_u1()
            self.unk_flag_01 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_02 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_03 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_04 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_05 = self._io.read_bits_int_le(1) != 0
            self.use_cast_shadows = self._io.read_bits_int_le(1) != 0
            self.use_receive_shadows = self._io.read_bits_int_le(1) != 0
            self.unk_flag_08 = self._io.read_bits_int_le(1) != 0
            self.num_vertices = self._io.read_u2le()
            self.vertex_position_end = self._io.read_u2le()
            self.vertex_position_2 = self._io.read_u4le()
            self.vertex_offset = self._io.read_u4le()
            self.vertex_offset_2 = self._io.read_u4le()
            self.face_position = self._io.read_u4le()
            self.num_indices = self._io.read_u4le()
            self.face_offset = self._io.read_u4le()
            self.unk_06 = self._io.read_u1()
            self.unk_07 = self._io.read_u1()
            self.vertex_position = self._io.read_u2le()
            self.num_unique_bone_ids = self._io.read_u1()
            self.idx_bone_palette = self._io.read_u1()
            self.unk_08 = self._io.read_u1()
            self.unk_09 = self._io.read_u1()
            self.unk_10 = self._io.read_u2le()
            self.unk_11 = self._io.read_u2le()


        def _fetch_instances(self):
            pass
            _ = self.indices
            for i in range(len(self._m_indices)):
                pass

            _ = self.vertices
            for i in range(len(self._m_vertices)):
                pass
                _on = self.vertex_format
                if _on == 0:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 4:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 6:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 7:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 1:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 3:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 5:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 8:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 2:
                    pass
                    self.vertices[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mod156.Mesh, self)._write__seq(io)
            self._should_write_indices = self.indices__to_write
            self._should_write_vertices = self.vertices__to_write
            self._io.write_u2le(self.idx_group)
            self._io.write_u2le(self.idx_material)
            self._io.write_u1(self.constant)
            self._io.write_u1(self.level_of_detail)
            self._io.write_u1(self.z_buffer_order)
            self._io.write_u1(self.vertex_format)
            self._io.write_u1(self.vertex_stride)
            self._io.write_u1(self.vertex_stride_2)
            self._io.write_u1(self.unk_03)
            self._io.write_bits_int_le(1, int(self.unk_flag_01))
            self._io.write_bits_int_le(1, int(self.unk_flag_02))
            self._io.write_bits_int_le(1, int(self.unk_flag_03))
            self._io.write_bits_int_le(1, int(self.unk_flag_04))
            self._io.write_bits_int_le(1, int(self.unk_flag_05))
            self._io.write_bits_int_le(1, int(self.use_cast_shadows))
            self._io.write_bits_int_le(1, int(self.use_receive_shadows))
            self._io.write_bits_int_le(1, int(self.unk_flag_08))
            self._io.write_u2le(self.num_vertices)
            self._io.write_u2le(self.vertex_position_end)
            self._io.write_u4le(self.vertex_position_2)
            self._io.write_u4le(self.vertex_offset)
            self._io.write_u4le(self.vertex_offset_2)
            self._io.write_u4le(self.face_position)
            self._io.write_u4le(self.num_indices)
            self._io.write_u4le(self.face_offset)
            self._io.write_u1(self.unk_06)
            self._io.write_u1(self.unk_07)
            self._io.write_u2le(self.vertex_position)
            self._io.write_u1(self.num_unique_bone_ids)
            self._io.write_u1(self.idx_bone_palette)
            self._io.write_u1(self.unk_08)
            self._io.write_u1(self.unk_09)
            self._io.write_u2le(self.unk_10)
            self._io.write_u2le(self.unk_11)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 52
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
            self._io.seek((((self._root.header.offset_vertex_buffer + (self.vertex_position * self.vertex_stride)) + self.vertex_offset) if (self.vertex_position > self.vertex_position_2) else ((self._root.header.offset_vertex_buffer + (self.vertex_position * self.vertex_stride)) + self.vertex_offset)))
            self._m_vertices = []
            for i in range((((self.vertex_position_end - self.vertex_position) + 1) if (self.vertex_position > self.vertex_position_2) else self.num_vertices)):
                _on = self.vertex_format
                if _on == 0:
                    pass
                    _t__m_vertices = Mod156.Vertex0(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 4:
                    pass
                    _t__m_vertices = Mod156.Vertex(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 6:
                    pass
                    _t__m_vertices = Mod156.Vertex5(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 7:
                    pass
                    _t__m_vertices = Mod156.Vertex5(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1:
                    pass
                    _t__m_vertices = Mod156.Vertex(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3:
                    pass
                    _t__m_vertices = Mod156.Vertex(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 5:
                    pass
                    _t__m_vertices = Mod156.Vertex5(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 8:
                    pass
                    _t__m_vertices = Mod156.Vertex5(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2:
                    pass
                    _t__m_vertices = Mod156.Vertex(self._io, self, self._root)
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
            self._io.seek((((self._root.header.offset_vertex_buffer + (self.vertex_position * self.vertex_stride)) + self.vertex_offset) if (self.vertex_position > self.vertex_position_2) else ((self._root.header.offset_vertex_buffer + (self.vertex_position * self.vertex_stride)) + self.vertex_offset)))
            for i in range(len(self._m_vertices)):
                pass
                _on = self.vertex_format
                if _on == 0:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 4:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 6:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 7:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 1:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 3:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 5:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 8:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 2:
                    pass
                    self.vertices[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_vertices(self):
            pass
            if (len(self.vertices) != (((self.vertex_position_end - self.vertex_position) + 1) if (self.vertex_position > self.vertex_position_2) else self.num_vertices)):
                raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), (((self.vertex_position_end - self.vertex_position) + 1) if (self.vertex_position > self.vertex_position_2) else self.num_vertices))
            for i in range(len(self._m_vertices)):
                pass
                _on = self.vertex_format
                if _on == 0:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 4:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 6:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 7:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 1:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 3:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 5:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 8:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)
                elif _on == 2:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)



    class UnkVtx8Block01(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u4le()
            self.unk_05 = self._io.read_u2le()
            self.unk_06 = self._io.read_u2le()
            self.unk_07 = self._io.read_u2le()
            self.unk_08 = self._io.read_u2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.UnkVtx8Block01, self)._write__seq(io)
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u4le(self.unk_03)
            self._io.write_u2le(self.unk_05)
            self._io.write_u2le(self.unk_06)
            self._io.write_u2le(self.unk_07)
            self._io.write_u2le(self.unk_08)


        def _check(self):
            pass


    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.surface_unk = self._io.read_bits_int_le(1) != 0
            self.surface_opaque = self._io.read_bits_int_le(1) != 0
            self.use_bridge_lines = self._io.read_bits_int_le(1) != 0
            self.unk_flag_04 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_05 = self._io.read_bits_int_le(1) != 0
            self.use_alpha_clip = self._io.read_bits_int_le(1) != 0
            self.use_opaque = self._io.read_bits_int_le(1) != 0
            self.use_translusent = self._io.read_bits_int_le(1) != 0
            self.use_alpha_transparency = self._io.read_bits_int_le(1) != 0
            self.unk_flag_10 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_11 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_12 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_13 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_14 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_15 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_16 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_17 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_18 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_19 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_20 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_21 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_22 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_23 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_24 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_25 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_26 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_27 = self._io.read_bits_int_le(1) != 0
            self.use_8_bones = self._io.read_bits_int_le(1) != 0
            self.unk_flag_29 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_30 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_31 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_32 = self._io.read_bits_int_le(1) != 0
            self.skin_weights_type = self._io.read_bits_int_le(3)
            self.unk_flag_36 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_37 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_38 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_39 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_40 = self._io.read_bits_int_le(1) != 0
            self.use_emmisive_map = self._io.read_bits_int_le(1) != 0
            self.unk_flag_42 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_43 = self._io.read_bits_int_le(1) != 0
            self.use_detail_map = self._io.read_bits_int_le(1) != 0
            self.unk_flag_45 = self._io.read_bits_int_le(1) != 0
            self.unk_flag_46 = self._io.read_bits_int_le(1) != 0
            self.use_cubemap = self._io.read_bits_int_le(1) != 0
            self.unk_flag_48 = self._io.read_bits_int_le(1) != 0
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u2le()
            self.unk_04 = self._io.read_u2le()
            self.unk_05 = self._io.read_u2le()
            self.unk_06 = self._io.read_u2le()
            self.unk_07 = self._io.read_u2le()
            self.unk_08 = self._io.read_u2le()
            self.unk_09 = self._io.read_u2le()
            self.texture_slots = []
            for i in range(8):
                self.texture_slots.append(self._io.read_u4le())

            self.unk_param_01 = self._io.read_f4le()
            self.unk_param_02 = self._io.read_f4le()
            self.unk_param_03 = self._io.read_f4le()
            self.unk_param_04 = self._io.read_f4le()
            self.unk_param_05 = self._io.read_f4le()
            self.cubemap_roughness = self._io.read_f4le()
            self.unk_param_07 = self._io.read_f4le()
            self.unk_param_08 = self._io.read_f4le()
            self.unk_param_09 = self._io.read_f4le()
            self.unk_param_10 = self._io.read_f4le()
            self.detail_normal_power = self._io.read_f4le()
            self.detail_normal_multiplier = self._io.read_f4le()
            self.unk_param_13 = self._io.read_f4le()
            self.unk_param_14 = self._io.read_f4le()
            self.unk_param_15 = self._io.read_f4le()
            self.unk_param_16 = self._io.read_f4le()
            self.unk_param_17 = self._io.read_f4le()
            self.unk_param_18 = self._io.read_f4le()
            self.unk_param_19 = self._io.read_f4le()
            self.unk_param_20 = self._io.read_f4le()
            self.normal_scale = self._io.read_f4le()
            self.unk_param_22 = self._io.read_f4le()
            self.unk_param_23 = self._io.read_f4le()
            self.unk_param_24 = self._io.read_f4le()
            self.unk_param_25 = self._io.read_f4le()
            self.unk_param_26 = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.texture_slots)):
                pass



        def _write__seq(self, io=None):
            super(Mod156.Material, self)._write__seq(io)
            self._io.write_bits_int_le(1, int(self.surface_unk))
            self._io.write_bits_int_le(1, int(self.surface_opaque))
            self._io.write_bits_int_le(1, int(self.use_bridge_lines))
            self._io.write_bits_int_le(1, int(self.unk_flag_04))
            self._io.write_bits_int_le(1, int(self.unk_flag_05))
            self._io.write_bits_int_le(1, int(self.use_alpha_clip))
            self._io.write_bits_int_le(1, int(self.use_opaque))
            self._io.write_bits_int_le(1, int(self.use_translusent))
            self._io.write_bits_int_le(1, int(self.use_alpha_transparency))
            self._io.write_bits_int_le(1, int(self.unk_flag_10))
            self._io.write_bits_int_le(1, int(self.unk_flag_11))
            self._io.write_bits_int_le(1, int(self.unk_flag_12))
            self._io.write_bits_int_le(1, int(self.unk_flag_13))
            self._io.write_bits_int_le(1, int(self.unk_flag_14))
            self._io.write_bits_int_le(1, int(self.unk_flag_15))
            self._io.write_bits_int_le(1, int(self.unk_flag_16))
            self._io.write_bits_int_le(1, int(self.unk_flag_17))
            self._io.write_bits_int_le(1, int(self.unk_flag_18))
            self._io.write_bits_int_le(1, int(self.unk_flag_19))
            self._io.write_bits_int_le(1, int(self.unk_flag_20))
            self._io.write_bits_int_le(1, int(self.unk_flag_21))
            self._io.write_bits_int_le(1, int(self.unk_flag_22))
            self._io.write_bits_int_le(1, int(self.unk_flag_23))
            self._io.write_bits_int_le(1, int(self.unk_flag_24))
            self._io.write_bits_int_le(1, int(self.unk_flag_25))
            self._io.write_bits_int_le(1, int(self.unk_flag_26))
            self._io.write_bits_int_le(1, int(self.unk_flag_27))
            self._io.write_bits_int_le(1, int(self.use_8_bones))
            self._io.write_bits_int_le(1, int(self.unk_flag_29))
            self._io.write_bits_int_le(1, int(self.unk_flag_30))
            self._io.write_bits_int_le(1, int(self.unk_flag_31))
            self._io.write_bits_int_le(1, int(self.unk_flag_32))
            self._io.write_bits_int_le(3, self.skin_weights_type)
            self._io.write_bits_int_le(1, int(self.unk_flag_36))
            self._io.write_bits_int_le(1, int(self.unk_flag_37))
            self._io.write_bits_int_le(1, int(self.unk_flag_38))
            self._io.write_bits_int_le(1, int(self.unk_flag_39))
            self._io.write_bits_int_le(1, int(self.unk_flag_40))
            self._io.write_bits_int_le(1, int(self.use_emmisive_map))
            self._io.write_bits_int_le(1, int(self.unk_flag_42))
            self._io.write_bits_int_le(1, int(self.unk_flag_43))
            self._io.write_bits_int_le(1, int(self.use_detail_map))
            self._io.write_bits_int_le(1, int(self.unk_flag_45))
            self._io.write_bits_int_le(1, int(self.unk_flag_46))
            self._io.write_bits_int_le(1, int(self.use_cubemap))
            self._io.write_bits_int_le(1, int(self.unk_flag_48))
            self._io.write_u2le(self.unk_01)
            self._io.write_u2le(self.unk_02)
            self._io.write_u2le(self.unk_03)
            self._io.write_u2le(self.unk_04)
            self._io.write_u2le(self.unk_05)
            self._io.write_u2le(self.unk_06)
            self._io.write_u2le(self.unk_07)
            self._io.write_u2le(self.unk_08)
            self._io.write_u2le(self.unk_09)
            for i in range(len(self.texture_slots)):
                pass
                self._io.write_u4le(self.texture_slots[i])

            self._io.write_f4le(self.unk_param_01)
            self._io.write_f4le(self.unk_param_02)
            self._io.write_f4le(self.unk_param_03)
            self._io.write_f4le(self.unk_param_04)
            self._io.write_f4le(self.unk_param_05)
            self._io.write_f4le(self.cubemap_roughness)
            self._io.write_f4le(self.unk_param_07)
            self._io.write_f4le(self.unk_param_08)
            self._io.write_f4le(self.unk_param_09)
            self._io.write_f4le(self.unk_param_10)
            self._io.write_f4le(self.detail_normal_power)
            self._io.write_f4le(self.detail_normal_multiplier)
            self._io.write_f4le(self.unk_param_13)
            self._io.write_f4le(self.unk_param_14)
            self._io.write_f4le(self.unk_param_15)
            self._io.write_f4le(self.unk_param_16)
            self._io.write_f4le(self.unk_param_17)
            self._io.write_f4le(self.unk_param_18)
            self._io.write_f4le(self.unk_param_19)
            self._io.write_f4le(self.unk_param_20)
            self._io.write_f4le(self.normal_scale)
            self._io.write_f4le(self.unk_param_22)
            self._io.write_f4le(self.unk_param_23)
            self._io.write_f4le(self.unk_param_24)
            self._io.write_f4le(self.unk_param_25)
            self._io.write_f4le(self.unk_param_26)


        def _check(self):
            pass
            if (len(self.texture_slots) != 8):
                raise kaitaistruct.ConsistencyError(u"texture_slots", len(self.texture_slots), 8)
            for i in range(len(self.texture_slots)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 160
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
            self.unk_01 = Mod156.Vec3(self._io, self, self._root)
            self.unk_01._read()
            self.bsphere = Mod156.Vec4(self._io, self, self._root)
            self.bsphere._read()
            self.bbox_min = Mod156.Vec4(self._io, self, self._root)
            self.bbox_min._read()
            self.bbox_max = Mod156.Vec4(self._io, self, self._root)
            self.bbox_max._read()
            self.oabb = Mod156.Matrix4x4(self._io, self, self._root)
            self.oabb._read()
            self.oabb_dimension = Mod156.Vec4(self._io, self, self._root)
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
            super(Mod156.WeightBound, self)._write__seq(io)
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
            super(Mod156.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            pass


    class MaterialsData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.textures = []
            for i in range(self._root.header.num_textures):
                self.textures.append((KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode("ASCII"))

            self.materials = []
            for i in range(self._root.header.num_materials):
                _t_materials = Mod156.Material(self._io, self, self._root)
                _t_materials._read()
                self.materials.append(_t_materials)



        def _fetch_instances(self):
            pass
            for i in range(len(self.textures)):
                pass

            for i in range(len(self.materials)):
                pass
                self.materials[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mod156.MaterialsData, self)._write__seq(io)
            for i in range(len(self.textures)):
                pass
                self._io.write_bytes_limit((self.textures[i]).encode(u"ASCII"), 64, 0, 0)

            for i in range(len(self.materials)):
                pass
                self.materials[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.textures) != self._root.header.num_textures):
                raise kaitaistruct.ConsistencyError(u"textures", len(self.textures), self._root.header.num_textures)
            for i in range(len(self.textures)):
                pass
                if (len((self.textures[i]).encode(u"ASCII")) > 64):
                    raise kaitaistruct.ConsistencyError(u"textures", len((self.textures[i]).encode(u"ASCII")), 64)
                if (KaitaiStream.byte_array_index_of((self.textures[i]).encode(u"ASCII"), 0) != -1):
                    raise kaitaistruct.ConsistencyError(u"textures", KaitaiStream.byte_array_index_of((self.textures[i]).encode(u"ASCII"), 0), -1)

            if (len(self.materials) != self._root.header.num_materials):
                raise kaitaistruct.ConsistencyError(u"materials", len(self.materials), self._root.header.num_materials)
            for i in range(len(self.materials)):
                pass
                if self.materials[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"materials", self.materials[i]._root, self._root)
                if self.materials[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"materials", self.materials[i]._parent, self)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = ((64 * self._root.header.num_textures) + (self._root.header.num_materials * self.materials[0].size_))
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
                _t_bones_hierarchy = Mod156.Bone(self._io, self, self._root)
                _t_bones_hierarchy._read()
                self.bones_hierarchy.append(_t_bones_hierarchy)

            self.parent_space_matrices = []
            for i in range(self._root.header.num_bones):
                _t_parent_space_matrices = Mod156.Matrix4x4(self._io, self, self._root)
                _t_parent_space_matrices._read()
                self.parent_space_matrices.append(_t_parent_space_matrices)

            self.inverse_bind_matrices = []
            for i in range(self._root.header.num_bones):
                _t_inverse_bind_matrices = Mod156.Matrix4x4(self._io, self, self._root)
                _t_inverse_bind_matrices._read()
                self.inverse_bind_matrices.append(_t_inverse_bind_matrices)

            if (self._root.header.num_bones != 0):
                pass
                self.bone_map = self._io.read_bytes(256)

            self.bone_palettes = []
            for i in range(self._root.header.num_bone_palettes):
                _t_bone_palettes = Mod156.BonePalette(self._io, self, self._root)
                _t_bone_palettes._read()
                self.bone_palettes.append(_t_bone_palettes)



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

            for i in range(len(self.bone_palettes)):
                pass
                self.bone_palettes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mod156.BonesData, self)._write__seq(io)
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

            for i in range(len(self.bone_palettes)):
                pass
                self.bone_palettes[i]._write__seq(self._io)



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

            if (len(self.bone_palettes) != self._root.header.num_bone_palettes):
                raise kaitaistruct.ConsistencyError(u"bone_palettes", len(self.bone_palettes), self._root.header.num_bone_palettes)
            for i in range(len(self.bone_palettes)):
                pass
                if self.bone_palettes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bone_palettes", self.bone_palettes[i]._root, self._root)
                if self.bone_palettes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bone_palettes", self.bone_palettes[i]._parent, self)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = ((((((self._root.header.num_bones * self.bones_hierarchy[0].size_) + (self._root.header.num_bones * 64)) + (self._root.header.num_bones * 64)) + 256) + (self._root.header.num_bone_palettes * self.bone_palettes[0].size_)) if (self._root.header.num_bones > 0) else 0)
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
            super(Mod156.Vec4S2, self)._write__seq(io)
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
            super(Mod156.Group, self)._write__seq(io)
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

    class Vertex5(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Mod156.Vec4S2(self._io, self, self._root)
            self.position._read()
            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(8):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod156.Vec4U1(self._io, self, self._root)
            self.normal._read()
            self.uv = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv._read()


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            for i in range(len(self.bone_indices)):
                pass

            for i in range(len(self.weight_values)):
                pass

            self.normal._fetch_instances()
            self.uv._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Vertex5, self)._write__seq(io)
            self.position._write__seq(self._io)
            for i in range(len(self.bone_indices)):
                pass
                self._io.write_u1(self.bone_indices[i])

            for i in range(len(self.weight_values)):
                pass
                self._io.write_u1(self.weight_values[i])

            self.normal._write__seq(self._io)
            self.uv._write__seq(self._io)


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
            if self.uv._root != self._root:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._root, self._root)
            if self.uv._parent != self:
                raise kaitaistruct.ConsistencyError(u"uv", self.uv._parent, self)


    @property
    def vertex_buffer(self):
        if self._should_write_vertex_buffer:
            self._write_vertex_buffer()
        if hasattr(self, '_m_vertex_buffer'):
            return self._m_vertex_buffer

        if (self.header.offset_vertex_buffer > 0):
            pass
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
        if (self.header.offset_vertex_buffer > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_vertex_buffer)
            self._io.write_bytes(self.vertex_buffer)
            self._io.seek(_pos)



    def _check_vertex_buffer(self):
        pass
        if (self.header.offset_vertex_buffer > 0):
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
            self._m_materials_data = Mod156.MaterialsData(self._io, self, self._root)
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
    def vertex_buffer_2(self):
        if self._should_write_vertex_buffer_2:
            self._write_vertex_buffer_2()
        if hasattr(self, '_m_vertex_buffer_2'):
            return self._m_vertex_buffer_2

        if (self.header.offset_vertex_buffer_2 > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_vertex_buffer)
            self._m_vertex_buffer_2 = self._io.read_bytes(self.header.size_vertex_buffer_2)
            self._io.seek(_pos)

        return getattr(self, '_m_vertex_buffer_2', None)

    @vertex_buffer_2.setter
    def vertex_buffer_2(self, v):
        self._m_vertex_buffer_2 = v

    def _write_vertex_buffer_2(self):
        self._should_write_vertex_buffer_2 = False
        if (self.header.offset_vertex_buffer_2 > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_vertex_buffer)
            self._io.write_bytes(self.vertex_buffer_2)
            self._io.seek(_pos)



    def _check_vertex_buffer_2(self):
        pass
        if (self.header.offset_vertex_buffer_2 > 0):
            pass
            if (len(self.vertex_buffer_2) != self.header.size_vertex_buffer_2):
                raise kaitaistruct.ConsistencyError(u"vertex_buffer_2", len(self.vertex_buffer_2), self.header.size_vertex_buffer_2)


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
            self._m_meshes_data = Mod156.MeshesData(self._io, self, self._root)
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

        if (self.header.offset_index_buffer > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer)
            self._m_index_buffer = self._io.read_bytes(((self.header.num_faces * 2) - 2))
            self._io.seek(_pos)

        return getattr(self, '_m_index_buffer', None)

    @index_buffer.setter
    def index_buffer(self, v):
        self._m_index_buffer = v

    def _write_index_buffer(self):
        self._should_write_index_buffer = False
        if (self.header.offset_index_buffer > 0):
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer)
            self._io.write_bytes(self.index_buffer)
            self._io.seek(_pos)



    def _check_index_buffer(self):
        pass
        if (self.header.offset_index_buffer > 0):
            pass
            if (len(self.index_buffer) != ((self.header.num_faces * 2) - 2)):
                raise kaitaistruct.ConsistencyError(u"index_buffer", len(self.index_buffer), ((self.header.num_faces * 2) - 2))


    @property
    def size_top_level_(self):
        if hasattr(self, '_m_size_top_level_'):
            return self._m_size_top_level_

        self._m_size_top_level_ = (self._root.header.size_ + 104)
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
            self._m_bones_data = Mod156.BonesData(self._io, self, self._root)
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
            _t__m_groups = Mod156.Group(self._io, self, self._root)
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

