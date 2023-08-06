# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineMesh(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x45\x53\x48":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x45\x53\x48", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.size_file = self._io.read_u8le()
        self.header = ReengineMesh.Header(self._io, self, self._root)

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


    class MeshGroupTest(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_u8le()

        @property
        def mesh_group(self):
            if hasattr(self, '_m_mesh_group'):
                return self._m_mesh_group

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_mesh_group = ReengineMesh.MeshGroup(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_mesh_group', None)


    class TestName(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_u8le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_value = (self._io.read_bytes_term(0, False, True, True)).decode(u"ascii")
            self._io.seek(_pos)
            return getattr(self, '_m_value', None)


    class Model(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_mesh_groups = self._io.read_u4le()
            self.unk = self._io.read_u4le()
            self.offset_main_mesh_header = self._io.read_u8le()
            self.mesh_groups = []
            for i in range(self.num_mesh_groups):
                self.mesh_groups.append(ReengineMesh.MeshGroupTest(self._io, self, self._root))

            self.padding = self._io.read_u8le()


    class Matrix4x4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.row_1 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_2 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_3 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_4 = ReengineMesh.Vec4(self._io, self, self._root)


    class ModelOffset(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_u8le()

        @property
        def model(self):
            if hasattr(self, '_m_model'):
                return self._m_model

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_model = ReengineMesh.Model(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_model', None)


    class BuffersHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_primitive_accessors = self._io.read_u8le()
            self.offset_vertex_buffer = self._io.read_u8le()
            self.offset_index_buffer = self._io.read_u8le()
            if self._root.version == 21041600:
                self.unk_00 = self._io.read_u8le()

            self.size_vertex_buffer = self._io.read_u4le()
            self.size_index_buffer = self._io.read_u4le()
            self.num_unk = self._io.read_u2le()
            self.num_primitive_accessors = self._io.read_u2le()
            self.unk_01 = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.unk_2 = self._io.read_u2le()
            self.unk_3 = self._io.read_u2le()
            if  ((self._root.version == 21041600) and (self.unk_00 == 0)) :
                self.unk_00_a = self._io.read_u4le()

            if  ((self._root.version == 21041600) and (self.unk_00 == 0)) :
                self.unk_00_b = self._io.read_u4le()


        @property
        def vertex_buffer(self):
            if hasattr(self, '_m_vertex_buffer'):
                return self._m_vertex_buffer

            _pos = self._io.pos()
            self._io.seek(self.offset_vertex_buffer)
            self._m_vertex_buffer = self._io.read_bytes(self.size_vertex_buffer)
            self._io.seek(_pos)
            return getattr(self, '_m_vertex_buffer', None)

        @property
        def index_buffer(self):
            if hasattr(self, '_m_index_buffer'):
                return self._m_index_buffer

            _pos = self._io.pos()
            self._io.seek(self.offset_index_buffer)
            self._m_index_buffer = self._io.read_bytes(self.size_index_buffer)
            self._io.seek(_pos)
            return getattr(self, '_m_index_buffer', None)

        @property
        def primitive_accessors(self):
            if hasattr(self, '_m_primitive_accessors'):
                return self._m_primitive_accessors

            _pos = self._io.pos()
            self._io.seek(self.offset_primitive_accessors)
            self._m_primitive_accessors = []
            for i in range(self.num_primitive_accessors):
                self._m_primitive_accessors.append(ReengineMesh.PrimitiveAccessor(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_primitive_accessors', None)


    class BoneHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_bones = self._io.read_u4le()
            self.num_bone_maps = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.reserved_02 = self._io.read_u4le()
            self.offset_parent_bone = self._io.read_u8le()
            self.offset_matrix_1 = self._io.read_u8le()
            self.offset_matrix_2 = self._io.read_u8le()
            self.offset_inverse_bind_matrices = self._io.read_u8le()
            self.bone_maps = []
            for i in range(self.num_bone_maps):
                self.bone_maps.append(self._io.read_u2le())


        @property
        def bones(self):
            if hasattr(self, '_m_bones'):
                return self._m_bones

            _pos = self._io.pos()
            self._io.seek(self.offset_parent_bone)
            self._m_bones = []
            for i in range(self.num_bones):
                self._m_bones.append(ReengineMesh.Bone(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_bones', None)

        @property
        def inverse_bind_matrices(self):
            if hasattr(self, '_m_inverse_bind_matrices'):
                return self._m_inverse_bind_matrices

            _pos = self._io.pos()
            self._io.seek(self.offset_inverse_bind_matrices)
            self._m_inverse_bind_matrices = []
            for i in range(self.num_bones):
                self._m_inverse_bind_matrices.append(ReengineMesh.Matrix4x4(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_inverse_bind_matrices', None)


    class MeshGroup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u1()
            self.num_meshes = self._io.read_u1()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.num_indices = self._io.read_u4le()
            self.meshes = []
            for i in range(self.num_meshes):
                self.meshes.append(ReengineMesh.Mesh(self._io, self, self._root))



    class Bone(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.idx = self._io.read_u2le()
            self.parent_idx = self._io.read_u2le()
            self.unk_02 = []
            for i in range(6):
                self.unk_02.append(self._io.read_u2le())



    class ModelInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_offsets_models = self._io.read_u1()
            self.num_materials = self._io.read_u1()
            self.num_uv_layers = self._io.read_u1()
            self.num_skin_weights = self._io.read_u1()
            self.num_meshes = self._io.read_u4le()
            if self._root.version == 386270720:
                self.reserved_01 = self._io.read_u8le()

            self.box = []
            for i in range(12):
                self.box.append(self._io.read_f4le())

            self.offset_lod_info = self._io.read_u4le()
            self.reserved_02 = self._io.read_u4le()

        @property
        def model_offsets(self):
            if hasattr(self, '_m_model_offsets'):
                return self._m_model_offsets

            _pos = self._io.pos()
            self._io.seek(self.offset_lod_info)
            self._m_model_offsets = []
            for i in range(self.len_offsets_models):
                self._m_model_offsets.append(ReengineMesh.ModelOffset(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_model_offsets', None)


    class Mesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.material_id = self._io.read_u4le()
            self.num_indices = self._io.read_u4le()
            self.pos_index_buffer = self._io.read_u4le()
            self.pos_vertex_buffer = self._io.read_u4le()
            if self._root.version != 386270720:
                self.unk_01 = self._io.read_u8le()


        @property
        def normals(self):
            if hasattr(self, '_m_normals'):
                return self._m_normals

            _pos = self._io.pos()
            self._io.seek(((self._root.buffers_data.offset_vertex_buffer + self._root.buffers_data.primitive_accessors[1].offset) + (self._root.buffers_data.primitive_accessors[1].size * self.pos_vertex_buffer)))
            self._m_normals = []
            for i in range(100):
                self._m_normals.append(self._io.read_s1())

            self._io.seek(_pos)
            return getattr(self, '_m_normals', None)


    class PrimitiveAccessor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.primitive_type = self._io.read_u2le()
            self.size = self._io.read_u2le()
            self.offset = self._io.read_u4le()


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk1 = self._io.read_u2le()
            self.num_named_nodes = self._io.read_u2le()
            self.reserved_02 = self._io.read_u4le()
            self.offset_data = self._io.read_u8le()
            self.offset_unk_1 = self._io.read_u8le()
            self.offset_unk_2 = self._io.read_u8le()
            self.offset_bones = self._io.read_u8le()
            self.offset_unk_3 = self._io.read_u8le()
            self.offset_unk_4 = self._io.read_u8le()
            self.offset_unk_5 = self._io.read_u8le()
            self.offset_buffers_header = self._io.read_u8le()
            self.offset_unk_6 = self._io.read_u8le()
            self.offset_test_remap = self._io.read_u8le()
            self.offset_unk_8 = self._io.read_u8le()
            self.offset_unk_9 = self._io.read_u8le()
            self.offset_names = self._io.read_u8le()


    class NameOffset(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_u8le()

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ascii")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)


    @property
    def buffers_data(self):
        if hasattr(self, '_m_buffers_data'):
            return self._m_buffers_data

        _pos = self._io.pos()
        self._io.seek(self.header.offset_buffers_header)
        self._m_buffers_data = ReengineMesh.BuffersHeader(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_buffers_data', None)

    @property
    def named_nodes(self):
        if hasattr(self, '_m_named_nodes'):
            return self._m_named_nodes

        _pos = self._io.pos()
        self._io.seek(self.header.offset_names)
        self._m_named_nodes = []
        for i in range(self.header.num_named_nodes):
            self._m_named_nodes.append(ReengineMesh.TestName(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_named_nodes', None)

    @property
    def model_info(self):
        if hasattr(self, '_m_model_info'):
            return self._m_model_info

        _pos = self._io.pos()
        self._io.seek(self.header.offset_data)
        self._m_model_info = ReengineMesh.ModelInfo(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_model_info', None)

    @property
    def bones_header(self):
        if hasattr(self, '_m_bones_header'):
            return self._m_bones_header

        if self.header.offset_bones != 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones)
            self._m_bones_header = ReengineMesh.BoneHeader(self._io, self, self._root)
            self._io.seek(_pos)

        return getattr(self, '_m_bones_header', None)

    @property
    def id_to_names_remap(self):
        if hasattr(self, '_m_id_to_names_remap'):
            return self._m_id_to_names_remap

        _pos = self._io.pos()
        self._io.seek(self.header.offset_test_remap)
        self._m_id_to_names_remap = []
        for i in range(self.header.num_named_nodes):
            self._m_id_to_names_remap.append(self._io.read_u2le())

        self._io.seek(_pos)
        return getattr(self, '_m_id_to_names_remap', None)


