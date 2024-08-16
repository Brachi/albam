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
        self.model_info = Mod156.ModelInfo(self._io, self, self._root)
        self.model_info._read()
        self.rcn_header = Mod156.RcnHeader(self._io, self, self._root)
        self.rcn_header._read()
        self.rcn_tables = []
        for i in range(self.rcn_header.num_tbl):
            _t_rcn_tables = Mod156.RcnTable(self._io, self, self._root)
            _t_rcn_tables._read()
            self.rcn_tables.append(_t_rcn_tables)

        self.rcn_vertices = []
        for i in range(self.rcn_header.num_vtx):
            _t_rcn_vertices = Mod156.RcnVertex(self._io, self, self._root)
            _t_rcn_vertices._read()
            self.rcn_vertices.append(_t_rcn_vertices)

        self.rcn_trianlges = []
        for i in range(self.rcn_header.num_tri):
            _t_rcn_trianlges = Mod156.RcnTriangle(self._io, self, self._root)
            _t_rcn_trianlges._read()
            self.rcn_trianlges.append(_t_rcn_trianlges)



    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        self.bsphere._fetch_instances()
        self.bbox_min._fetch_instances()
        self.bbox_max._fetch_instances()
        self.model_info._fetch_instances()
        self.rcn_header._fetch_instances()
        for i in range(len(self.rcn_tables)):
            pass
            self.rcn_tables[i]._fetch_instances()

        for i in range(len(self.rcn_vertices)):
            pass
            self.rcn_vertices[i]._fetch_instances()

        for i in range(len(self.rcn_trianlges)):
            pass
            self.rcn_trianlges[i]._fetch_instances()

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
        self.model_info._write__seq(self._io)
        self.rcn_header._write__seq(self._io)
        for i in range(len(self.rcn_tables)):
            pass
            self.rcn_tables[i]._write__seq(self._io)

        for i in range(len(self.rcn_vertices)):
            pass
            self.rcn_vertices[i]._write__seq(self._io)

        for i in range(len(self.rcn_trianlges)):
            pass
            self.rcn_trianlges[i]._write__seq(self._io)



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
        if self.model_info._root != self._root:
            raise kaitaistruct.ConsistencyError(u"model_info", self.model_info._root, self._root)
        if self.model_info._parent != self:
            raise kaitaistruct.ConsistencyError(u"model_info", self.model_info._parent, self)
        if self.rcn_header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"rcn_header", self.rcn_header._root, self._root)
        if self.rcn_header._parent != self:
            raise kaitaistruct.ConsistencyError(u"rcn_header", self.rcn_header._parent, self)
        if (len(self.rcn_tables) != self.rcn_header.num_tbl):
            raise kaitaistruct.ConsistencyError(u"rcn_tables", len(self.rcn_tables), self.rcn_header.num_tbl)
        for i in range(len(self.rcn_tables)):
            pass
            if self.rcn_tables[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rcn_tables", self.rcn_tables[i]._root, self._root)
            if self.rcn_tables[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"rcn_tables", self.rcn_tables[i]._parent, self)

        if (len(self.rcn_vertices) != self.rcn_header.num_vtx):
            raise kaitaistruct.ConsistencyError(u"rcn_vertices", len(self.rcn_vertices), self.rcn_header.num_vtx)
        for i in range(len(self.rcn_vertices)):
            pass
            if self.rcn_vertices[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rcn_vertices", self.rcn_vertices[i]._root, self._root)
            if self.rcn_vertices[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"rcn_vertices", self.rcn_vertices[i]._parent, self)

        if (len(self.rcn_trianlges) != self.rcn_header.num_tri):
            raise kaitaistruct.ConsistencyError(u"rcn_trianlges", len(self.rcn_trianlges), self.rcn_header.num_tri)
        for i in range(len(self.rcn_trianlges)):
            pass
            if self.rcn_trianlges[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rcn_trianlges", self.rcn_trianlges[i]._root, self._root)
            if self.rcn_trianlges[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"rcn_trianlges", self.rcn_trianlges[i]._parent, self)


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


    class VfSkin(ReadWriteKaitaiStruct):
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
            super(Mod156.VfSkin, self)._write__seq(io)
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


    class RcnTriangle(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.v0 = self._io.read_bits_int_le(21)
            self.v1 = self._io.read_bits_int_le(21)
            self.v2 = self._io.read_bits_int_le(21)
            self.reserved = self._io.read_bits_int_le(1) != 0


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.RcnTriangle, self)._write__seq(io)
            self._io.write_bits_int_le(21, self.v0)
            self._io.write_bits_int_le(21, self.v1)
            self._io.write_bits_int_le(21, self.v2)
            self._io.write_bits_int_le(1, int(self.reserved))


        def _check(self):
            pass


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


    class VfNonSkinCol(ReadWriteKaitaiStruct):
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
            self.rgba = Mod156.Vec4U1(self._io, self, self._root)
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
            super(Mod156.VfNonSkinCol, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
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

    class ModelInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.middist = self._io.read_s4le()
            self.lowdist = self._io.read_s4le()
            self.light_group = self._io.read_u4le()
            self.strip_type = self._io.read_u1()
            self.memory = self._io.read_u1()
            self.reserved = self._io.read_u2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.ModelInfo, self)._write__seq(io)
            self._io.write_s4le(self.middist)
            self._io.write_s4le(self.lowdist)
            self._io.write_u4le(self.light_group)
            self._io.write_u1(self.strip_type)
            self._io.write_u1(self.memory)
            self._io.write_u2le(self.reserved)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Vec2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.Vec2, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)


        def _check(self):
            pass


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
            self._should_write_vertices2 = False
            self.vertices2__to_write = True

        def _read(self):
            self.idx_group = self._io.read_u2le()
            self.idx_material = self._io.read_u2le()
            self.disp = self._io.read_u1()
            self.level_of_detail = self._io.read_u1()
            self.alpha_priority = self._io.read_u1()
            self.max_bones_per_vertex = self._io.read_u1()
            self.vertex_stride = self._io.read_u1()
            self.vertex_stride_2 = self._io.read_u1()
            self.connective = self._io.read_u1()
            self.shape = self._io.read_bits_int_le(1) != 0
            self.env = self._io.read_bits_int_le(1) != 0
            self.refrect = self._io.read_bits_int_le(1) != 0
            self.reserved2_flag_1 = self._io.read_bits_int_le(1) != 0
            self.reserved2_flag_2 = self._io.read_bits_int_le(1) != 0
            self.shadow_cast = self._io.read_bits_int_le(1) != 0
            self.shadow_receive = self._io.read_bits_int_le(1) != 0
            self.sort = self._io.read_bits_int_le(1) != 0
            self.num_vertices = self._io.read_u2le()
            self.vertex_position_end = self._io.read_u2le()
            self.vertex_position_2 = self._io.read_u4le()
            self.vertex_offset = self._io.read_u4le()
            self.vertex_offset_2 = self._io.read_u4le()
            self.face_position = self._io.read_u4le()
            self.num_indices = self._io.read_u4le()
            self.face_offset = self._io.read_u4le()
            self.vdeclbase = self._io.read_u1()
            self.vdecl = self._io.read_u1()
            self.vertex_position = self._io.read_u2le()
            self.num_weight_bounds = self._io.read_u1()
            self.idx_bone_palette = self._io.read_u1()
            self.rcn_base = self._io.read_u2le()
            self.boundary = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.indices
            for i in range(len(self._m_indices)):
                pass

            _ = self.vertices
            for i in range(len(self._m_vertices)):
                pass
                _on = self._root.materials_data.materials[self.idx_material].vtype
                if _on == 0:
                    pass
                    self.vertices[i]._fetch_instances()
                elif _on == 4:
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
                elif _on == 2:
                    pass
                    self.vertices[i]._fetch_instances()

            if (self.vertex_stride_2 > 0):
                pass
                _ = self.vertices2
                for i in range(len(self._m_vertices2)):
                    pass
                    _on = self.vertex_stride_2
                    if _on == 4:
                        pass
                        self.vertices2[i]._fetch_instances()
                    elif _on == 8:
                        pass
                        self.vertices2[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Mod156.Mesh, self)._write__seq(io)
            self._should_write_indices = self.indices__to_write
            self._should_write_vertices = self.vertices__to_write
            self._should_write_vertices2 = self.vertices2__to_write
            self._io.write_u2le(self.idx_group)
            self._io.write_u2le(self.idx_material)
            self._io.write_u1(self.disp)
            self._io.write_u1(self.level_of_detail)
            self._io.write_u1(self.alpha_priority)
            self._io.write_u1(self.max_bones_per_vertex)
            self._io.write_u1(self.vertex_stride)
            self._io.write_u1(self.vertex_stride_2)
            self._io.write_u1(self.connective)
            self._io.write_bits_int_le(1, int(self.shape))
            self._io.write_bits_int_le(1, int(self.env))
            self._io.write_bits_int_le(1, int(self.refrect))
            self._io.write_bits_int_le(1, int(self.reserved2_flag_1))
            self._io.write_bits_int_le(1, int(self.reserved2_flag_2))
            self._io.write_bits_int_le(1, int(self.shadow_cast))
            self._io.write_bits_int_le(1, int(self.shadow_receive))
            self._io.write_bits_int_le(1, int(self.sort))
            self._io.write_u2le(self.num_vertices)
            self._io.write_u2le(self.vertex_position_end)
            self._io.write_u4le(self.vertex_position_2)
            self._io.write_u4le(self.vertex_offset)
            self._io.write_u4le(self.vertex_offset_2)
            self._io.write_u4le(self.face_position)
            self._io.write_u4le(self.num_indices)
            self._io.write_u4le(self.face_offset)
            self._io.write_u1(self.vdeclbase)
            self._io.write_u1(self.vdecl)
            self._io.write_u2le(self.vertex_position)
            self._io.write_u1(self.num_weight_bounds)
            self._io.write_u1(self.idx_bone_palette)
            self._io.write_u2le(self.rcn_base)
            self._io.write_u4le(self.boundary)


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
                _on = self._root.materials_data.materials[self.idx_material].vtype
                if _on == 0:
                    pass
                    _t__m_vertices = Mod156.VfSkin(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 4:
                    pass
                    _t__m_vertices = Mod156.VfSkin(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 1:
                    pass
                    _t__m_vertices = Mod156.VfSkinEx(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 3:
                    pass
                    _t__m_vertices = Mod156.VfNonSkinCol(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 5:
                    pass
                    _t__m_vertices = Mod156.VfSkin(self._io, self, self._root)
                    _t__m_vertices._read()
                    self._m_vertices.append(_t__m_vertices)
                elif _on == 2:
                    pass
                    _t__m_vertices = Mod156.VfNonSkin(self._io, self, self._root)
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
                _on = self._root.materials_data.materials[self.idx_material].vtype
                if _on == 0:
                    pass
                    self.vertices[i]._write__seq(self._io)
                elif _on == 4:
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
                _on = self._root.materials_data.materials[self.idx_material].vtype
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
                elif _on == 2:
                    pass
                    if self.vertices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                    if self.vertices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)


        @property
        def vertices2(self):
            if self._should_write_vertices2:
                self._write_vertices2()
            if hasattr(self, '_m_vertices2'):
                return self._m_vertices2

            if (self.vertex_stride_2 > 0):
                pass
                _pos = self._io.pos()
                self._io.seek(((self._root.header.offset_vertex_buffer_2 + (self.vertex_position_2 * self.vertex_stride_2)) + self.vertex_offset_2))
                self._m_vertices2 = []
                for i in range(self.num_vertices):
                    _on = self.vertex_stride_2
                    if _on == 4:
                        pass
                        _t__m_vertices2 = Mod156.Vertex24(self._io, self, self._root)
                        _t__m_vertices2._read()
                        self._m_vertices2.append(_t__m_vertices2)
                    elif _on == 8:
                        pass
                        _t__m_vertices2 = Mod156.Vertex28(self._io, self, self._root)
                        _t__m_vertices2._read()
                        self._m_vertices2.append(_t__m_vertices2)

                self._io.seek(_pos)

            return getattr(self, '_m_vertices2', None)

        @vertices2.setter
        def vertices2(self, v):
            self._m_vertices2 = v

        def _write_vertices2(self):
            self._should_write_vertices2 = False
            if (self.vertex_stride_2 > 0):
                pass
                _pos = self._io.pos()
                self._io.seek(((self._root.header.offset_vertex_buffer_2 + (self.vertex_position_2 * self.vertex_stride_2)) + self.vertex_offset_2))
                for i in range(len(self._m_vertices2)):
                    pass
                    _on = self.vertex_stride_2
                    if _on == 4:
                        pass
                        self.vertices2[i]._write__seq(self._io)
                    elif _on == 8:
                        pass
                        self.vertices2[i]._write__seq(self._io)

                self._io.seek(_pos)



        def _check_vertices2(self):
            pass
            if (self.vertex_stride_2 > 0):
                pass
                if (len(self.vertices2) != self.num_vertices):
                    raise kaitaistruct.ConsistencyError(u"vertices2", len(self.vertices2), self.num_vertices)
                for i in range(len(self._m_vertices2)):
                    pass
                    _on = self.vertex_stride_2
                    if _on == 4:
                        pass
                        if self.vertices2[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"vertices2", self.vertices2[i]._root, self._root)
                        if self.vertices2[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"vertices2", self.vertices2[i]._parent, self)
                    elif _on == 8:
                        pass
                        if self.vertices2[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"vertices2", self.vertices2[i]._root, self._root)
                        if self.vertices2[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"vertices2", self.vertices2[i]._parent, self)




    class RcnTable(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vindex = self._io.read_bits_int_le(21)
            self.noffset = self._io.read_bits_int_le(10)
            self.edge = self._io.read_bits_int_le(1) != 0


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.RcnTable, self)._write__seq(io)
            self._io.write_bits_int_le(21, self.vindex)
            self._io.write_bits_int_le(10, self.noffset)
            self._io.write_bits_int_le(1, int(self.edge))


        def _check(self):
            pass


    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.fog_enable = self._io.read_bits_int_le(1) != 0
            self.zwrite = self._io.read_bits_int_le(1) != 0
            self.attr = self._io.read_bits_int_le(12)
            self.num = self._io.read_bits_int_le(8)
            self.envmap_bias = self._io.read_bits_int_le(5)
            self.vtype = self._io.read_bits_int_le(3)
            self.uvscroll_enable = self._io.read_bits_int_le(1) != 0
            self.ztest = self._io.read_bits_int_le(1) != 0
            self.func_skin = self._io.read_bits_int_le(4)
            self.func_reserved2 = self._io.read_bits_int_le(2)
            self.func_lighting = self._io.read_bits_int_le(4)
            self.func_normalmap = self._io.read_bits_int_le(4)
            self.func_specular = self._io.read_bits_int_le(4)
            self.func_lightmap = self._io.read_bits_int_le(4)
            self.func_multitexture = self._io.read_bits_int_le(4)
            self.func_reserved = self._io.read_bits_int_le(6)
            self.htechnique = self._io.read_u4le()
            self.pipeline = self._io.read_u4le()
            self.pvdeclbase = self._io.read_u4le()
            self.pvdecl = self._io.read_u4le()
            self.basemap = self._io.read_u4le()
            self.normalmap = self._io.read_u4le()
            self.maskmap = self._io.read_u4le()
            self.lightmap = self._io.read_u4le()
            self.shadowmap = self._io.read_u4le()
            self.additionalmap = self._io.read_u4le()
            self.envmap = self._io.read_u4le()
            self.detailmap = self._io.read_u4le()
            self.occlusionmap = self._io.read_u4le()
            self.transparency = self._io.read_f4le()
            self.fresnel_factor = []
            for i in range(4):
                self.fresnel_factor.append(self._io.read_f4le())

            self.lightmap_factor = []
            for i in range(4):
                self.lightmap_factor.append(self._io.read_f4le())

            self.detail_factor = []
            for i in range(4):
                self.detail_factor.append(self._io.read_f4le())

            self.reserved1 = self._io.read_u4le()
            self.reserved2 = self._io.read_u4le()
            self.lightblendmap = self._io.read_u4le()
            self.shadowblendmap = self._io.read_u4le()
            self.parallax_factor = []
            for i in range(2):
                self.parallax_factor.append(self._io.read_f4le())

            self.flip_binormal = self._io.read_f4le()
            self.heightmap_occ = self._io.read_f4le()
            self.blend_state = self._io.read_u4le()
            self.alpha_ref = self._io.read_u4le()
            self.heightmap = self._io.read_u4le()
            self.glossmap = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.fresnel_factor)):
                pass

            for i in range(len(self.lightmap_factor)):
                pass

            for i in range(len(self.detail_factor)):
                pass

            for i in range(len(self.parallax_factor)):
                pass



        def _write__seq(self, io=None):
            super(Mod156.Material, self)._write__seq(io)
            self._io.write_bits_int_le(1, int(self.fog_enable))
            self._io.write_bits_int_le(1, int(self.zwrite))
            self._io.write_bits_int_le(12, self.attr)
            self._io.write_bits_int_le(8, self.num)
            self._io.write_bits_int_le(5, self.envmap_bias)
            self._io.write_bits_int_le(3, self.vtype)
            self._io.write_bits_int_le(1, int(self.uvscroll_enable))
            self._io.write_bits_int_le(1, int(self.ztest))
            self._io.write_bits_int_le(4, self.func_skin)
            self._io.write_bits_int_le(2, self.func_reserved2)
            self._io.write_bits_int_le(4, self.func_lighting)
            self._io.write_bits_int_le(4, self.func_normalmap)
            self._io.write_bits_int_le(4, self.func_specular)
            self._io.write_bits_int_le(4, self.func_lightmap)
            self._io.write_bits_int_le(4, self.func_multitexture)
            self._io.write_bits_int_le(6, self.func_reserved)
            self._io.write_u4le(self.htechnique)
            self._io.write_u4le(self.pipeline)
            self._io.write_u4le(self.pvdeclbase)
            self._io.write_u4le(self.pvdecl)
            self._io.write_u4le(self.basemap)
            self._io.write_u4le(self.normalmap)
            self._io.write_u4le(self.maskmap)
            self._io.write_u4le(self.lightmap)
            self._io.write_u4le(self.shadowmap)
            self._io.write_u4le(self.additionalmap)
            self._io.write_u4le(self.envmap)
            self._io.write_u4le(self.detailmap)
            self._io.write_u4le(self.occlusionmap)
            self._io.write_f4le(self.transparency)
            for i in range(len(self.fresnel_factor)):
                pass
                self._io.write_f4le(self.fresnel_factor[i])

            for i in range(len(self.lightmap_factor)):
                pass
                self._io.write_f4le(self.lightmap_factor[i])

            for i in range(len(self.detail_factor)):
                pass
                self._io.write_f4le(self.detail_factor[i])

            self._io.write_u4le(self.reserved1)
            self._io.write_u4le(self.reserved2)
            self._io.write_u4le(self.lightblendmap)
            self._io.write_u4le(self.shadowblendmap)
            for i in range(len(self.parallax_factor)):
                pass
                self._io.write_f4le(self.parallax_factor[i])

            self._io.write_f4le(self.flip_binormal)
            self._io.write_f4le(self.heightmap_occ)
            self._io.write_u4le(self.blend_state)
            self._io.write_u4le(self.alpha_ref)
            self._io.write_u4le(self.heightmap)
            self._io.write_u4le(self.glossmap)


        def _check(self):
            pass
            if (len(self.fresnel_factor) != 4):
                raise kaitaistruct.ConsistencyError(u"fresnel_factor", len(self.fresnel_factor), 4)
            for i in range(len(self.fresnel_factor)):
                pass

            if (len(self.lightmap_factor) != 4):
                raise kaitaistruct.ConsistencyError(u"lightmap_factor", len(self.lightmap_factor), 4)
            for i in range(len(self.lightmap_factor)):
                pass

            if (len(self.detail_factor) != 4):
                raise kaitaistruct.ConsistencyError(u"detail_factor", len(self.detail_factor), 4)
            for i in range(len(self.detail_factor)):
                pass

            if (len(self.parallax_factor) != 2):
                raise kaitaistruct.ConsistencyError(u"parallax_factor", len(self.parallax_factor), 2)
            for i in range(len(self.parallax_factor)):
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


    class VfNonSkin(ReadWriteKaitaiStruct):
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
            super(Mod156.VfNonSkin, self)._write__seq(io)
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


    class RcnVertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_u2le()
            self.y = self._io.read_u2le()
            self.z = self._io.read_u2le()
            self.w = self._io.read_u2le()
            self.w0 = self._io.read_u1()
            self.w1 = self._io.read_u1()
            self.w2 = self._io.read_u1()
            self.w3 = self._io.read_u1()
            self.j0 = self._io.read_u1()
            self.j1 = self._io.read_u1()
            self.j2 = self._io.read_u1()
            self.j3 = self._io.read_u1()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.RcnVertex, self)._write__seq(io)
            self._io.write_u2le(self.x)
            self._io.write_u2le(self.y)
            self._io.write_u2le(self.z)
            self._io.write_u2le(self.w)
            self._io.write_u1(self.w0)
            self._io.write_u1(self.w1)
            self._io.write_u1(self.w2)
            self._io.write_u1(self.w3)
            self._io.write_u1(self.j0)
            self._io.write_u1(self.j1)
            self._io.write_u1(self.j2)
            self._io.write_u1(self.j3)


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

    class Vertex24(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.occlusion = Mod156.Vec4U1(self._io, self, self._root)
            self.occlusion._read()


        def _fetch_instances(self):
            pass
            self.occlusion._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Vertex24, self)._write__seq(io)
            self.occlusion._write__seq(self._io)


        def _check(self):
            pass
            if self.occlusion._root != self._root:
                raise kaitaistruct.ConsistencyError(u"occlusion", self.occlusion._root, self._root)
            if self.occlusion._parent != self:
                raise kaitaistruct.ConsistencyError(u"occlusion", self.occlusion._parent, self)


    class VfSkinEx(ReadWriteKaitaiStruct):
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
            super(Mod156.VfSkinEx, self)._write__seq(io)
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

    class Vertex28(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.occlusion = Mod156.Vec4U1(self._io, self, self._root)
            self.occlusion._read()
            self.tangent = Mod156.Vec4U1(self._io, self, self._root)
            self.tangent._read()


        def _fetch_instances(self):
            pass
            self.occlusion._fetch_instances()
            self.tangent._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Vertex28, self)._write__seq(io)
            self.occlusion._write__seq(self._io)
            self.tangent._write__seq(self._io)


        def _check(self):
            pass
            if self.occlusion._root != self._root:
                raise kaitaistruct.ConsistencyError(u"occlusion", self.occlusion._root, self._root)
            if self.occlusion._parent != self:
                raise kaitaistruct.ConsistencyError(u"occlusion", self.occlusion._parent, self)
            if self.tangent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._root, self._root)
            if self.tangent._parent != self:
                raise kaitaistruct.ConsistencyError(u"tangent", self.tangent._parent, self)


    class RcnHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ptri = self._io.read_u4le()
            self.pvtx = self._io.read_u4le()
            self.ptb = self._io.read_u4le()
            self.num_tri = self._io.read_u4le()
            self.num_vtx = self._io.read_u4le()
            self.num_tbl = self._io.read_u4le()
            self.parts = self._io.read_u4le()
            self.reserved = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mod156.RcnHeader, self)._write__seq(io)
            self._io.write_u4le(self.ptri)
            self._io.write_u4le(self.pvtx)
            self._io.write_u4le(self.ptb)
            self._io.write_u4le(self.num_tri)
            self._io.write_u4le(self.num_vtx)
            self._io.write_u4le(self.num_tbl)
            self._io.write_u4le(self.parts)
            self._io.write_u4le(self.reserved)


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
            self.reserved = []
            for i in range(3):
                self.reserved.append(self._io.read_u4le())

            self.pos = Mod156.Vec3(self._io, self, self._root)
            self.pos._read()
            self.radius = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.reserved)):
                pass

            self.pos._fetch_instances()


        def _write__seq(self, io=None):
            super(Mod156.Group, self)._write__seq(io)
            self._io.write_u4le(self.group_index)
            for i in range(len(self.reserved)):
                pass
                self._io.write_u4le(self.reserved[i])

            self.pos._write__seq(self._io)
            self._io.write_f4le(self.radius)


        def _check(self):
            pass
            if (len(self.reserved) != 3):
                raise kaitaistruct.ConsistencyError(u"reserved", len(self.reserved), 3)
            for i in range(len(self.reserved)):
                pass

            if self.pos._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pos", self.pos._root, self._root)
            if self.pos._parent != self:
                raise kaitaistruct.ConsistencyError(u"pos", self.pos._parent, self)

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

