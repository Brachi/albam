# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mod21(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Mod21.ModHeader(self._io, self, self._root)
        self.bones = []
        for i in range(self.header.num_bones):
            self.bones.append(Mod21.Bone(self._io, self, self._root))

        self.parent_space_matrices = []
        for i in range(self.header.num_bones):
            self.parent_space_matrices.append(Mod21.Matrix4x4(self._io, self, self._root))

        self.inverse_bind_matrices = []
        for i in range(self.header.num_bones):
            self.inverse_bind_matrices.append(Mod21.Matrix4x4(self._io, self, self._root))

        if self.header.num_bones != 0:
            self.bone_map = self._io.read_bytes(256)

        self.groups = []
        for i in range(self.header.num_groups):
            self.groups.append(Mod21.Group(self._io, self, self._root))

        if self.header.version == 210:
            self.material_names = []
            for i in range(self.header.num_material_names):
                self.material_names.append((KaitaiStream.bytes_terminate(self._io.read_bytes(128), 0, False)).decode(u"ascii"))


        if self.header.version == 211:
            self.material_hashes = []
            for i in range(self.header.num_material_hashes):
                self.material_hashes.append(self._io.read_u4le())


        self.meshes = []
        for i in range(self.header.num_meshes):
            self.meshes.append(Mod21.Mesh(self._io, self, self._root))

        if self.header.version == 211:
            self.num_weight_bounds_211 = self._io.read_u4le()

        if self.header.version == 210:
            self.weight_bounds_210 = []
            for i in range(self.header.num_weight_bounds_210):
                self.weight_bounds_210.append(Mod21.WeightBound(self._io, self, self._root))


        if self.header.version == 211:
            self.weight_bounds_211 = []
            for i in range(self.num_weight_bounds_211):
                self.weight_bounds_211.append(Mod21.WeightBound(self._io, self, self._root))


        self.vertex_buffer = self._io.read_bytes(self.header.size_vertex_buffer)
        self.index_buffer = self._io.read_bytes((self.header.num_faces * 2))

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


    class ModHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ident = self._io.read_bytes(4)
            if not self.ident == b"\x4D\x4F\x44\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x4D\x4F\x44\x00", self.ident, self._io, u"/types/mod_header/seq/0")
            self.version = self._io.read_u1()
            self.revision = self._io.read_u1()
            self.num_bones = self._io.read_u2le()
            self.num_meshes = self._io.read_u2le()
            if self.version == 210:
                self.num_material_names = self._io.read_u2le()

            if self.version == 211:
                self.num_material_hashes = self._io.read_u2le()

            self.num_vertices = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_edges = self._io.read_u4le()
            self.size_vertex_buffer = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.num_groups = self._io.read_u4le()
            self.offset_bones = self._io.read_u4le()
            self.offset_groups = self._io.read_u4le()
            self.offset_material = self._io.read_u4le()
            self.offset_meshes = self._io.read_u4le()
            self.offset_buffer_vertices = self._io.read_u4le()
            self.offset_buffer_indices = self._io.read_u4le()
            self.size_file = self._io.read_u4le()
            self.bsphere = Mod21.Vec4(self._io, self, self._root)
            self.bbox_min = Mod21.Vec4(self._io, self, self._root)
            self.bbox_max = Mod21.Vec4(self._io, self, self._root)
            self.unk_01 = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            self.unk_04 = self._io.read_u4le()
            if self.version == 210:
                self.num_weight_bounds_210 = self._io.read_u4le()



    class Vec2HalfFloat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.u = self._io.read_bytes(2)
            self.v = self._io.read_bytes(2)


    class VertexA8fa(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u1())

            self.todo_1 = []
            for i in range(9):
                self.todo_1.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexB098(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.todo = []
            for i in range(4):
                self.todo.append(self._io.read_u1())



    class Matrix4x4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.row_1 = Mod21.Vec4(self._io, self, self._root)
            self.row_2 = Mod21.Vec4(self._io, self, self._root)
            self.row_3 = Mod21.Vec4(self._io, self, self._root)
            self.row_4 = Mod21.Vec4(self._io, self, self._root)


    class VertexBb42(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.todo_1 = []
            for i in range(12):
                self.todo_1.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.todo_2 = []
            for i in range(12):
                self.todo_2.append(self._io.read_u1())



    class Bone(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.idx = self._io.read_u1()
            self.idx_parent = self._io.read_u1()
            self.idx_mirror = self._io.read_u1()
            self.idx_mapping = self._io.read_u1()
            self.unk_01 = self._io.read_f4le()
            self.parent_distance = self._io.read_f4le()
            self.location = Mod21.Vec3(self._io, self, self._root)


    class Vertex2f55(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.unk_01 = []
            for i in range(8):
                self.unk_01.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.todo = []
            for i in range(36):
                self.todo.append(self._io.read_u1())



    class VertexC31f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.todo_1 = []
            for i in range(8):
                self.todo_1.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))



    class Vertex14d4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.unk_01 = []
            for i in range(8):
                self.unk_01.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))



    class Mesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

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
            self.face_count = self._io.read_u4le()
            self.face_offset = self._io.read_u4le()
            self.bone_id_start = self._io.read_u1()
            self.num_unique_bone_ids = self._io.read_u1()
            self.mesh_index = self._io.read_u2le()
            self.min_index = self._io.read_u2le()
            self.max_index = self._io.read_u2le()
            self.hash = self._io.read_u4le()

        @property
        def indices(self):
            if hasattr(self, '_m_indices'):
                return self._m_indices

            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_buffer_indices + (self.face_offset * 2)) + (self.face_position * 2)))
            self._m_indices = []
            for i in range(self.face_count):
                self._m_indices.append(self._io.read_u2le())

            self._io.seek(_pos)
            return getattr(self, '_m_indices', None)

        @property
        def vertices(self):
            if hasattr(self, '_m_vertices'):
                return self._m_vertices

            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_buffer_vertices + self.vertex_offset) + (self.vertex_position * self.vertex_stride)))
            self._m_vertices = []
            for i in range(self.num_vertices):
                _on = self.vertex_format
                if _on == 794148925:
                    self._m_vertices.append(Mod21.Vertex2f55(self._io, self, self._root))
                elif _on == 3273596956:
                    self._m_vertices.append(Mod21.VertexC31f(self._io, self, self._root))
                elif _on == 3141681188:
                    self._m_vertices.append(Mod21.VertexBb42(self._io, self, self._root))
                elif _on == 2835001368:
                    self._m_vertices.append(Mod21.VertexA8fa(self._io, self, self._root))
                elif _on == 349437984:
                    self._m_vertices.append(Mod21.Vertex14d4(self._io, self, self._root))
                elif _on == 213286933:
                    self._m_vertices.append(Mod21.VertexCb68(self._io, self, self._root))
                elif _on == 3682443284:
                    self._m_vertices.append(Mod21.VertexDb7d(self._io, self, self._root))
                elif _on == 2736832534:
                    self._m_vertices.append(Mod21.VertexA320(self._io, self, self._root))
                elif _on == 2962763795:
                    self._m_vertices.append(Mod21.VertexB098(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_vertices', None)


    class VertexDb7d(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.todo = []
            for i in range(8):
                self.todo.append(self._io.read_u1())



    class Material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_floats = []
            for i in range(30):
                self.unk_floats.append(self._io.read_f4le())



    class WeightBound(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bone_id = self._io.read_u4le()
            self.unk_01 = Mod21.Vec3(self._io, self, self._root)
            self.bsphere = Mod21.Vec4(self._io, self, self._root)
            self.bbox_min = Mod21.Vec4(self._io, self, self._root)
            self.bbox_max = Mod21.Vec4(self._io, self, self._root)
            self.oabb_matrix = Mod21.Matrix4x4(self._io, self, self._root)
            self.oabb_dimension = Mod21.Vec4(self._io, self, self._root)


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


    class VertexA320(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.todo = []
            for i in range(20):
                self.todo.append(self._io.read_u1())



    class Vec3S2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()


    class Vec4S2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()
            self.w = self._io.read_s2le()


    class Group(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.group_index = self._io.read_u4le()
            self.unk_02 = self._io.read_f4le()
            self.unk_03 = self._io.read_f4le()
            self.unk_04 = self._io.read_f4le()
            self.unk_05 = self._io.read_f4le()
            self.unk_06 = self._io.read_f4le()
            self.unk_07 = self._io.read_f4le()
            self.unk_08 = self._io.read_f4le()


    class VertexCb68(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.todo_1 = []
            for i in range(8):
                self.todo_1.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)



