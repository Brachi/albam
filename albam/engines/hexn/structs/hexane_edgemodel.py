# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class HexaneEdgemodel(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = HexaneEdgemodel.EdgeHeader(self._io, self, self._root)
        self.meshes_header = []
        for i in range(self.header.num_meshes):
            self.meshes_header.append(HexaneEdgemodel.MeshHeader(self._io, self, self._root))



    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.meshes_header)):
            pass
            self.meshes_header[i]._fetch_instances()


    class Vec4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


        def _fetch_instances(self):
            pass


    class MaterialsTable(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.offsets = []
            for i in range(self._parent._parent.header.num_material_per_mesh):
                self.offsets.append(self._io.read_u4le())

            self.first_material = (self._io.read_bytes_term(0, False, True, True)).decode("ASCII")


        def _fetch_instances(self):
            pass
            for i in range(len(self.offsets)):
                pass



    class Matrix4x4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.row_1 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_2 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_3 = HexaneEdgemodel.Vec4(self._io, self, self._root)
            self.row_4 = HexaneEdgemodel.Vec4(self._io, self, self._root)


        def _fetch_instances(self):
            pass
            self.row_1._fetch_instances()
            self.row_2._fetch_instances()
            self.row_3._fetch_instances()
            self.row_4._fetch_instances()


    class Edgemesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

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


        def _fetch_instances(self):
            pass
            for i in range(len(self.reserved_01)):
                pass

            for i in range(len(self.reserved_02)):
                pass

            _ = self.buffer_indices
            _ = self.buffer_vertices
            _ = self.buffer_weights

        @property
        def buffer_indices(self):
            if hasattr(self, '_m_buffer_indices'):
                return self._m_buffer_indices

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_indices)
            self._m_buffer_indices = self._io.read_bytes(self.size_buffer_indices)
            self._io.seek(_pos)
            return getattr(self, '_m_buffer_indices', None)

        @property
        def buffer_vertices(self):
            if hasattr(self, '_m_buffer_vertices'):
                return self._m_buffer_vertices

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_vertices)
            self._m_buffer_vertices = self._io.read_bytes(self.size_buffer_vertices)
            self._io.seek(_pos)
            return getattr(self, '_m_buffer_vertices', None)

        @property
        def buffer_weights(self):
            if hasattr(self, '_m_buffer_weights'):
                return self._m_buffer_weights

            _pos = self._io.pos()
            self._io.seek(self.ofs_buffer_vertices)
            self._m_buffer_weights = self._io.read_bytes(self.size_buffer_vertices)
            self._io.seek(_pos)
            return getattr(self, '_m_buffer_weights', None)


    class Vec3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.reserved_03 = self._io.read_u4le()


        def _fetch_instances(self):
            pass


    class EdgeHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.id_magic = self._io.read_bytes(4)
            if not (self.id_magic == b"\x46\x4D\x36\x53"):
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


        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_matrix_1)):
                pass

            self.unk_matrix_2._fetch_instances()
            for i in range(len(self.ofs_models_start)):
                pass

            for i in range(len(self.ofs_models_end)):
                pass



    class MeshHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.num_groups = self._io.read_u4le()
            self.ofs_data = self._io.read_u4le()
            self.lod = self._io.read_u4le()
            self.ofs_materials = self._io.read_u4le()
            self.matrix_4x2_unk = []
            for i in range(8):
                self.matrix_4x2_unk.append(self._io.read_f4le())

            self.matrix_4x4_unk = HexaneEdgemodel.Matrix4x4(self._io, self, self._root)
            self.unk_ofs_1 = self._io.read_u4le()
            self.unk_ofs_2 = self._io.read_u4le()
            self.unk_ofs_3 = self._io.read_u4le()
            self.unk_ofs_4 = self._io.read_u4le()
            self.unk_ofs_5 = self._io.read_u4le()
            self.unk_flags_1 = self._io.read_u4le()
            self.unk_ofs_6 = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.matrix_4x2_unk)):
                pass

            self.matrix_4x4_unk._fetch_instances()
            _ = self.mesh
            self.mesh._fetch_instances()
            _ = self.materials
            self.materials._fetch_instances()

        @property
        def mesh(self):
            if hasattr(self, '_m_mesh'):
                return self._m_mesh

            _pos = self._io.pos()
            self._io.seek(self.ofs_data)
            self._m_mesh = HexaneEdgemodel.Edgemesh(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_mesh', None)

        @property
        def materials(self):
            if hasattr(self, '_m_materials'):
                return self._m_materials

            _pos = self._io.pos()
            self._io.seek(self.ofs_materials)
            self._m_materials = HexaneEdgemodel.MaterialsTable(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_materials', None)



