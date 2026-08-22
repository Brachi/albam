# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneEdgemodel(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(HexaneEdgemodel, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = HexaneEdgemodel.EdgeHeader(self._io, self, self._root)
        self.header._read()
        self.meshes_header = []
        for i in range(self.header.num_meshes):
            _t_meshes_header = HexaneEdgemodel.MeshHeader(self._io, self, self._root)
            try:
                _t_meshes_header._read()
            finally:
                self.meshes_header.append(_t_meshes_header)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.meshes_header)):
            pass
            self.meshes_header[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(HexaneEdgemodel, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.meshes_header)):
            pass
            self.meshes_header[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.meshes_header) != self.header.num_meshes:
            raise kaitaistruct.ConsistencyError(u"meshes_header", self.header.num_meshes, len(self.meshes_header))
        for i in range(len(self.meshes_header)):
            pass
            if self.meshes_header[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"meshes_header", self._root, self.meshes_header[i]._root)
            if self.meshes_header[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"meshes_header", self, self.meshes_header[i]._parent)

        self._dirty = False

    class EdgeHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.EdgeHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.id_magic = self._io.read_bytes(4)
            if not self.id_magic == b"\x46\x4D\x36\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x46\x4D\x36\x53", self.id_magic, self._io, u"/types/edge_header/seq/0")
            self.version = self._io.read_u4le()
            self.num_models = self._io.read_u4le()
            self.num_meshes = self._io.read_u4le()
            self.ofs_meshes_start = self._io.read_u4le()
            self.ofs_meshes_end = self._io.read_u4le()
            self.ofs_meshes_info = self._io.read_u4le()
            self.num_bones = self._io.read_u4le()
            self.ofs_bones = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.reserved_02 = self._io.read_u4le()
            self.reserved_03 = self._io.read_u4le()
            self.unk_matrix_1 = []
            for i in range(8):
                self.unk_matrix_1.append(self._io.read_f4le())

            self.unk_matrix_2 = HexaneEdgemodel.Matrix4x4(self._io, self, self._root)
            self.unk_matrix_2._read()
            self.num_material_per_mesh = self._io.read_u4le()
            self.ofs_unk_01 = self._io.read_u4le()
            self.ofs_unk_02 = self._io.read_u4le()
            self.reserved_04 = self._io.read_u4le()
            self.ofs_models_start = []
            for i in range(5):
                self.ofs_models_start.append(self._io.read_u4le())

            self.ofs_models_end = []
            for i in range(5):
                self.ofs_models_end.append(self._io.read_u4le())

            self.reserved_05 = self._io.read_u4le()
            self.reserved_06 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_matrix_1)):
                pass

            self.unk_matrix_2._fetch_instances()
            for i in range(len(self.ofs_models_start)):
                pass

            for i in range(len(self.ofs_models_end)):
                pass



        def _write__seq(self, io=None):
            super(HexaneEdgemodel.EdgeHeader, self)._write__seq(io)
            self._io.write_bytes(self.id_magic)
            self._io.write_u4le(self.version)
            self._io.write_u4le(self.num_models)
            self._io.write_u4le(self.num_meshes)
            self._io.write_u4le(self.ofs_meshes_start)
            self._io.write_u4le(self.ofs_meshes_end)
            self._io.write_u4le(self.ofs_meshes_info)
            self._io.write_u4le(self.num_bones)
            self._io.write_u4le(self.ofs_bones)
            self._io.write_u4le(self.reserved_01)
            self._io.write_u4le(self.reserved_02)
            self._io.write_u4le(self.reserved_03)
            for i in range(len(self.unk_matrix_1)):
                pass
                self._io.write_f4le(self.unk_matrix_1[i])

            self.unk_matrix_2._write__seq(self._io)
            self._io.write_u4le(self.num_material_per_mesh)
            self._io.write_u4le(self.ofs_unk_01)
            self._io.write_u4le(self.ofs_unk_02)
            self._io.write_u4le(self.reserved_04)
            for i in range(len(self.ofs_models_start)):
                pass
                self._io.write_u4le(self.ofs_models_start[i])

            for i in range(len(self.ofs_models_end)):
                pass
                self._io.write_u4le(self.ofs_models_end[i])

            self._io.write_u4le(self.reserved_05)
            self._io.write_u4le(self.reserved_06)


        def _check(self):
            if len(self.id_magic) != 4:
                raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
            if not self.id_magic == b"\x46\x4D\x36\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x46\x4D\x36\x53", self.id_magic, None, u"/types/edge_header/seq/0")
            if len(self.unk_matrix_1) != 8:
                raise kaitaistruct.ConsistencyError(u"unk_matrix_1", 8, len(self.unk_matrix_1))
            for i in range(len(self.unk_matrix_1)):
                pass

            if self.unk_matrix_2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"unk_matrix_2", self._root, self.unk_matrix_2._root)
            if self.unk_matrix_2._parent != self:
                raise kaitaistruct.ConsistencyError(u"unk_matrix_2", self, self.unk_matrix_2._parent)
            if len(self.ofs_models_start) != 5:
                raise kaitaistruct.ConsistencyError(u"ofs_models_start", 5, len(self.ofs_models_start))
            for i in range(len(self.ofs_models_start)):
                pass

            if len(self.ofs_models_end) != 5:
                raise kaitaistruct.ConsistencyError(u"ofs_models_end", 5, len(self.ofs_models_end))
            for i in range(len(self.ofs_models_end)):
                pass

            self._dirty = False


    class Edgemesh(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.Edgemesh, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_buffer_indices = False
            self.buffer_indices__enabled = True
            self._should_write_buffer_vertices = False
            self.buffer_vertices__enabled = True
            self._should_write_buffer_weights = False
            self.buffer_weights__enabled = True

        def _read(self):
            self.unk_1_flag = self._io.read_u2le()
            self.unk_2_constant = self._io.read_u2le()
            self.unk_3_flag = self._io.read_u4le()
            self.num_vertices = self._io.read_u2le()
            self.num_indices = self._io.read_u2le()
            self.unk_4_flag = self._io.read_u4le()
            self.ofs_buffer_indices = self._io.read_u4le()
            self.size_buffer_indices = self._io.read_u4le()
            self.reserved_01 = []
            for i in range(5):
                self.reserved_01.append(self._io.read_u4le())

            self.ofs_buffer_vertices = self._io.read_u4le()
            self.size_buffer_vertices = self._io.read_u4le()
            self.reserved_06 = self._io.read_u4le()
            self.unk_5_flag = self._io.read_u4le()
            self.size_buffer_weights = self._io.read_u4le()
            self.ofs_buffer_weights = self._io.read_u4le()
            self.unk_6_flag = self._io.read_u4le()
            self.num_vertices_padding = self._io.read_u4le()
            self.reserved_02 = []
            for i in range(9):
                self.reserved_02.append(self._io.read_u4le())

            self.unk_7_offset = self._io.read_u4le()
            self.unk_8_offset = self._io.read_u4le()
            self.reserved_16 = self._io.read_u4le()
            self.unk_9_size = self._io.read_u2le()
            self.unk_10_size = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.reserved_01)):
                pass

            for i in range(len(self.reserved_02)):
                pass

            _ = self.buffer_indices
            if hasattr(self, '_m_buffer_indices'):
                pass

            _ = self.buffer_vertices
            if hasattr(self, '_m_buffer_vertices'):
                pass

            _ = self.buffer_weights
            if hasattr(self, '_m_buffer_weights'):
                pass



        def _write__seq(self, io=None):
            super(HexaneEdgemodel.Edgemesh, self)._write__seq(io)
            self._should_write_buffer_indices = self.buffer_indices__enabled
            self._should_write_buffer_vertices = self.buffer_vertices__enabled
            self._should_write_buffer_weights = self.buffer_weights__enabled
            self._io.write_u2le(self.unk_1_flag)
            self._io.write_u2le(self.unk_2_constant)
            self._io.write_u4le(self.unk_3_flag)
            self._io.write_u2le(self.num_vertices)
            self._io.write_u2le(self.num_indices)
            self._io.write_u4le(self.unk_4_flag)
            self._io.write_u4le(self.ofs_buffer_indices)
            self._io.write_u4le(self.size_buffer_indices)
            for i in range(len(self.reserved_01)):
                pass
                self._io.write_u4le(self.reserved_01[i])

            self._io.write_u4le(self.ofs_buffer_vertices)
            self._io.write_u4le(self.size_buffer_vertices)
            self._io.write_u4le(self.reserved_06)
            self._io.write_u4le(self.unk_5_flag)
            self._io.write_u4le(self.size_buffer_weights)
            self._io.write_u4le(self.ofs_buffer_weights)
            self._io.write_u4le(self.unk_6_flag)
            self._io.write_u4le(self.num_vertices_padding)
            for i in range(len(self.reserved_02)):
                pass
                self._io.write_u4le(self.reserved_02[i])

            self._io.write_u4le(self.unk_7_offset)
            self._io.write_u4le(self.unk_8_offset)
            self._io.write_u4le(self.reserved_16)
            self._io.write_u2le(self.unk_9_size)
            self._io.write_u2le(self.unk_10_size)


        def _check(self):
            if len(self.reserved_01) != 5:
                raise kaitaistruct.ConsistencyError(u"reserved_01", 5, len(self.reserved_01))
            for i in range(len(self.reserved_01)):
                pass

            if len(self.reserved_02) != 9:
                raise kaitaistruct.ConsistencyError(u"reserved_02", 9, len(self.reserved_02))
            for i in range(len(self.reserved_02)):
                pass

            if self.buffer_indices__enabled:
                pass
                if len(self._m_buffer_indices) != self.size_buffer_indices:
                    raise kaitaistruct.ConsistencyError(u"buffer_indices", self.size_buffer_indices, len(self._m_buffer_indices))

            if self.buffer_vertices__enabled:
                pass
                if len(self._m_buffer_vertices) != self.size_buffer_vertices:
                    raise kaitaistruct.ConsistencyError(u"buffer_vertices", self.size_buffer_vertices, len(self._m_buffer_vertices))

            if self.buffer_weights__enabled:
                pass
                if len(self._m_buffer_weights) != self.size_buffer_weights:
                    raise kaitaistruct.ConsistencyError(u"buffer_weights", self.size_buffer_weights, len(self._m_buffer_weights))

            self._dirty = False

        @property
        def buffer_indices(self):
            if self._should_write_buffer_indices:
                self._write_buffer_indices()
            if hasattr(self, '_m_buffer_indices'):
                return self._m_buffer_indices

            if not self.buffer_indices__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_indices)
            self._m_buffer_indices = self._io.read_bytes(self.size_buffer_indices)
            self._io.seek(_pos)
            return getattr(self, '_m_buffer_indices', None)

        @buffer_indices.setter
        def buffer_indices(self, v):
            self._dirty = True
            self._m_buffer_indices = v

        def _write_buffer_indices(self):
            self._should_write_buffer_indices = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_indices)
            self._io.write_bytes(self._m_buffer_indices)
            self._io.seek(_pos)

        @property
        def buffer_vertices(self):
            if self._should_write_buffer_vertices:
                self._write_buffer_vertices()
            if hasattr(self, '_m_buffer_vertices'):
                return self._m_buffer_vertices

            if not self.buffer_vertices__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_vertices)
            self._m_buffer_vertices = self._io.read_bytes(self.size_buffer_vertices)
            self._io.seek(_pos)
            return getattr(self, '_m_buffer_vertices', None)

        @buffer_vertices.setter
        def buffer_vertices(self, v):
            self._dirty = True
            self._m_buffer_vertices = v

        def _write_buffer_vertices(self):
            self._should_write_buffer_vertices = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_vertices)
            self._io.write_bytes(self._m_buffer_vertices)
            self._io.seek(_pos)

        @property
        def buffer_weights(self):
            if self._should_write_buffer_weights:
                self._write_buffer_weights()
            if hasattr(self, '_m_buffer_weights'):
                return self._m_buffer_weights

            if not self.buffer_weights__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_weights)
            self._m_buffer_weights = self._io.read_bytes(self.size_buffer_weights)
            self._io.seek(_pos)
            return getattr(self, '_m_buffer_weights', None)

        @buffer_weights.setter
        def buffer_weights(self, v):
            self._dirty = True
            self._m_buffer_weights = v

        def _write_buffer_weights(self):
            self._should_write_buffer_weights = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_weights)
            self._io.write_bytes(self._m_buffer_weights)
            self._io.seek(_pos)


    class MaterialsTable(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.MaterialsTable, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.offsets = []
            for i in range(self._parent._parent.header.num_material_per_mesh):
                self.offsets.append(self._io.read_u4le())

            self.all_materials = []
            for i in range(self._parent._parent.header.num_material_per_mesh):
                self.all_materials.append((self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII"))

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.offsets)):
                pass

            for i in range(len(self.all_materials)):
                pass



        def _write__seq(self, io=None):
            super(HexaneEdgemodel.MaterialsTable, self)._write__seq(io)
            for i in range(len(self.offsets)):
                pass
                self._io.write_u4le(self.offsets[i])

            for i in range(len(self.all_materials)):
                pass
                self._io.write_bytes((self.all_materials[i]).encode(u"ASCII"))
                self._io.write_u1(0)



        def _check(self):
            if len(self.offsets) != self._parent._parent.header.num_material_per_mesh:
                raise kaitaistruct.ConsistencyError(u"offsets", self._parent._parent.header.num_material_per_mesh, len(self.offsets))
            for i in range(len(self.offsets)):
                pass

            if len(self.all_materials) != self._parent._parent.header.num_material_per_mesh:
                raise kaitaistruct.ConsistencyError(u"all_materials", self._parent._parent.header.num_material_per_mesh, len(self.all_materials))
            for i in range(len(self.all_materials)):
                pass
                if KaitaiStream.byte_array_index_of((self.all_materials[i]).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"all_materials", -1, KaitaiStream.byte_array_index_of((self.all_materials[i]).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def first_material(self):
            if hasattr(self, '_m_first_material'):
                return self._m_first_material

            self._m_first_material = self.all_materials[0]
            return getattr(self, '_m_first_material', None)

        def _invalidate_first_material(self):
            del self._m_first_material

    class Matrix4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.Matrix4x4, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.row_1 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_1._read()
            self.row_2 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_2._read()
            self.row_3 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_3._read()
            self.row_4 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_4._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.row_1._fetch_instances()
            self.row_2._fetch_instances()
            self.row_3._fetch_instances()
            self.row_4._fetch_instances()


        def _write__seq(self, io=None):
            super(HexaneEdgemodel.Matrix4x4, self)._write__seq(io)
            self.row_1._write__seq(self._io)
            self.row_2._write__seq(self._io)
            self.row_3._write__seq(self._io)
            self.row_4._write__seq(self._io)


        def _check(self):
            if self.row_1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_1", self._root, self.row_1._root)
            if self.row_1._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_1", self, self.row_1._parent)
            if self.row_2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_2", self._root, self.row_2._root)
            if self.row_2._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_2", self, self.row_2._parent)
            if self.row_3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_3", self._root, self.row_3._root)
            if self.row_3._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_3", self, self.row_3._parent)
            if self.row_4._root != self._root:
                raise kaitaistruct.ConsistencyError(u"row_4", self._root, self.row_4._root)
            if self.row_4._parent != self:
                raise kaitaistruct.ConsistencyError(u"row_4", self, self.row_4._parent)
            self._dirty = False


    class MeshHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.MeshHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_materials = False
            self.materials__enabled = True
            self._should_write_mesh = False
            self.mesh__enabled = True

        def _read(self):
            self.num_groups = self._io.read_u4le()
            self.ofs_data = self._io.read_u4le()
            self.lod = self._io.read_u4le()
            self.ofs_materials = self._io.read_u4le()
            self.matrix_4x2_unk = []
            for i in range(8):
                self.matrix_4x2_unk.append(self._io.read_f4le())

            self.matrix_4x4_unk = HexaneEdgemodel.Matrix4x4(self._io, self, self._root)
            self.matrix_4x4_unk._read()
            self.unk_ofs_1 = self._io.read_u4le()
            self.unk_ofs_2 = self._io.read_u4le()
            self.unk_ofs_3 = self._io.read_u4le()
            self.unk_ofs_4 = self._io.read_u4le()
            self.unk_ofs_5 = self._io.read_u4le()
            self.unk_flags_1 = self._io.read_u4le()
            self.unk_ofs_6 = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.matrix_4x2_unk)):
                pass

            self.matrix_4x4_unk._fetch_instances()
            _ = self.materials
            if hasattr(self, '_m_materials'):
                pass
                self._m_materials._fetch_instances()

            _ = self.mesh
            if hasattr(self, '_m_mesh'):
                pass
                self._m_mesh._fetch_instances()



        def _write__seq(self, io=None):
            super(HexaneEdgemodel.MeshHeader, self)._write__seq(io)
            self._should_write_materials = self.materials__enabled
            self._should_write_mesh = self.mesh__enabled
            self._io.write_u4le(self.num_groups)
            self._io.write_u4le(self.ofs_data)
            self._io.write_u4le(self.lod)
            self._io.write_u4le(self.ofs_materials)
            for i in range(len(self.matrix_4x2_unk)):
                pass
                self._io.write_f4le(self.matrix_4x2_unk[i])

            self.matrix_4x4_unk._write__seq(self._io)
            self._io.write_u4le(self.unk_ofs_1)
            self._io.write_u4le(self.unk_ofs_2)
            self._io.write_u4le(self.unk_ofs_3)
            self._io.write_u4le(self.unk_ofs_4)
            self._io.write_u4le(self.unk_ofs_5)
            self._io.write_u4le(self.unk_flags_1)
            self._io.write_u4le(self.unk_ofs_6)
            self._io.write_u4le(self.reserved_01)


        def _check(self):
            if len(self.matrix_4x2_unk) != 8:
                raise kaitaistruct.ConsistencyError(u"matrix_4x2_unk", 8, len(self.matrix_4x2_unk))
            for i in range(len(self.matrix_4x2_unk)):
                pass

            if self.matrix_4x4_unk._root != self._root:
                raise kaitaistruct.ConsistencyError(u"matrix_4x4_unk", self._root, self.matrix_4x4_unk._root)
            if self.matrix_4x4_unk._parent != self:
                raise kaitaistruct.ConsistencyError(u"matrix_4x4_unk", self, self.matrix_4x4_unk._parent)
            if self.materials__enabled:
                pass
                if self._m_materials._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"materials", self._root, self._m_materials._root)
                if self._m_materials._parent != self:
                    raise kaitaistruct.ConsistencyError(u"materials", self, self._m_materials._parent)

            if self.mesh__enabled:
                pass
                if self._m_mesh._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"mesh", self._root, self._m_mesh._root)
                if self._m_mesh._parent != self:
                    raise kaitaistruct.ConsistencyError(u"mesh", self, self._m_mesh._parent)

            self._dirty = False

        @property
        def materials(self):
            if self._should_write_materials:
                self._write_materials()
            if hasattr(self, '_m_materials'):
                return self._m_materials

            if not self.materials__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_materials)
            self._m_materials = HexaneEdgemodel.MaterialsTable(self._io, self, self._root)
            self._m_materials._read()
            self._io.seek(_pos)
            return getattr(self, '_m_materials', None)

        @materials.setter
        def materials(self, v):
            self._dirty = True
            self._m_materials = v

        def _write_materials(self):
            self._should_write_materials = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_materials)
            self._m_materials._write__seq(self._io)
            self._io.seek(_pos)

        @property
        def mesh(self):
            if self._should_write_mesh:
                self._write_mesh()
            if hasattr(self, '_m_mesh'):
                return self._m_mesh

            if not self.mesh__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_mesh = HexaneEdgemodel.Edgemesh(self._io, self, self._root)
            self._m_mesh._read()
            self._io.seek(_pos)
            return getattr(self, '_m_mesh', None)

        @mesh.setter
        def mesh(self, v):
            self._dirty = True
            self._m_mesh = v

        def _write_mesh(self):
            self._should_write_mesh = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_mesh._write__seq(self._io)
            self._io.seek(_pos)


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.reserved_03 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(HexaneEdgemodel.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_u4le(self.reserved_03)


        def _check(self):
            self._dirty = False


    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(HexaneEdgemodel.Vec4, self).__init__(_io)
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
            super(HexaneEdgemodel.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False



