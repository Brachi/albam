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
        self.bsphere = Mod21.Vec4(self._io, self, self._root)
        self.bbox_min = Mod21.Vec4(self._io, self, self._root)
        self.bbox_max = Mod21.Vec4(self._io, self, self._root)
        self.unk_01 = self._io.read_u4le()
        self.unk_02 = self._io.read_u4le()
        self.unk_03 = self._io.read_u4le()
        self.unk_04 = self._io.read_u4le()
        if self._root.header.version == 210:
            self.num_weight_bounds = self._io.read_u4le()


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

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 64
            return getattr(self, '_m_size_', None)


    class VertexA7d7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vertex2082(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)


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
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vec3U1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()


    class VertexB098(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec4U1(self._io, self, self._root)


    class VertexB668(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)


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
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)


    class VertexD877(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexD84e(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class Vertex6459(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vertex926f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class Vertex667b(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vertex77d8(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class Vertex63b6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.vertex_alpha = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.occlusion = self._io.read_u4le()


    class Vertex5e7f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexA14e(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class VertexB392(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexD9e8(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Bone(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.idx_anim_map = self._io.read_u1()
            self.idx_parent = self._io.read_u1()
            self.idx_mirror = self._io.read_u1()
            self.idx_mapping = self._io.read_u1()
            self.unk_01 = self._io.read_f4le()
            self.parent_distance = self._io.read_f4le()
            self.location = Mod21.Vec3(self._io, self, self._root)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)


    class Vertex2f55(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.morph_position = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position2 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position3 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position4 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_normal = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal2 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal3 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal4 = Mod21.Vec3U1(self._io, self, self._root)


    class Vertex747d(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexC31f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))



    class Vertex75c3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexCbf6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(1):
                self.bone_indices.append(self._io.read_u2le())

            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class Vec4U1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()
            self.w = self._io.read_u1()


    class MeshesData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.meshes = []
            for i in range(self._root.header.num_meshes):
                self.meshes.append(Mod21.Mesh(self._io, self, self._root))

            if self._root.header.version == 211:
                self.num_weight_bounds = self._io.read_u4le()

            self.weight_bounds = []
            for i in range((self._root.num_weight_bounds if self._root.header.version == 210 else self.num_weight_bounds)):
                self.weight_bounds.append(Mod21.WeightBound(self._io, self, self._root))


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = (((self._root.header.num_meshes * self.meshes[0].size_) + (self._root.num_weight_bounds * self.weight_bounds[0].size_)) if self._root.header.version == 210 else ((self._root.header.num_meshes * self.meshes[0].size_) + (self.num_weight_bounds * self.weight_bounds[0].size_)))
            return getattr(self, '_m_size_', None)


    class VertexA013(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.bone_indices = []
            for i in range(2):
                self.bone_indices.append(self._io.read_bytes(2))

            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class Vertex14d4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
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
            self.num_indices = self._io.read_u4le()
            self.face_offset = self._io.read_u4le()
            self.bone_id_start = self._io.read_u1()
            self.num_unique_bone_ids = self._io.read_u1()
            self.mesh_index = self._io.read_u2le()
            self.min_index = self._io.read_u2le()
            self.max_index = self._io.read_u2le()
            self.hash = self._io.read_u4le()

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 48
            return getattr(self, '_m_size_', None)

        @property
        def indices(self):
            if hasattr(self, '_m_indices'):
                return self._m_indices

            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_index_buffer + (self.face_offset * 2)) + (self.face_position * 2)))
            self._m_indices = []
            for i in range(self.num_indices):
                self._m_indices.append(self._io.read_u2le())

            self._io.seek(_pos)
            return getattr(self, '_m_indices', None)

        @property
        def vertices(self):
            if hasattr(self, '_m_vertices'):
                return self._m_vertices

            _pos = self._io.pos()
            self._io.seek(((self._root.header.offset_vertex_buffer + self.vertex_offset) + (self.vertex_position * self.vertex_stride)))
            self._m_vertices = []
            for i in range(self.num_vertices):
                _on = self.vertex_format
                if _on == 1585389612:
                    self._m_vertices.append(Mod21.Vertex5e7f(self._io, self, self._root))
                elif _on == 3094208554:
                    self._m_vertices.append(Mod21.VertexB86d(self._io, self, self._root))
                elif _on == 1672921135:
                    self._m_vertices.append(Mod21.Vertex63b6(self._io, self, self._root))
                elif _on == 933552181:
                    self._m_vertices.append(Mod21.Vertex37a4(self._io, self, self._root))
                elif _on == 3663044641:
                    self._m_vertices.append(Mod21.VertexDa55(self._io, self, self._root))
                elif _on == 794148925:
                    self._m_vertices.append(Mod21.Vertex2f55(self._io, self, self._root))
                elif _on == 3273596956:
                    self._m_vertices.append(Mod21.VertexC31f(self._io, self, self._root))
                elif _on == 2456801326:
                    self._m_vertices.append(Mod21.Vertex926f(self._io, self, self._root))
                elif _on == 3329204282:
                    self._m_vertices.append(Mod21.VertexC66f(self._io, self, self._root))
                elif _on == 2685620254:
                    self._m_vertices.append(Mod21.VertexA013(self._io, self, self._root))
                elif _on == 3141681188:
                    self._m_vertices.append(Mod21.VertexBb42(self._io, self, self._root))
                elif _on == 2706243644:
                    self._m_vertices.append(Mod21.VertexA14e(self._io, self, self._root))
                elif _on == 3626594344:
                    self._m_vertices.append(Mod21.Vertex8297(self._io, self, self._root))
                elif _on == 3421945882:
                    self._m_vertices.append(Mod21.VertexCbf6(self._io, self, self._root))
                elif _on == 2835001368:
                    self._m_vertices.append(Mod21.VertexA8fa(self._io, self, self._root))
                elif _on == 2476326963:
                    self._m_vertices.append(Mod21.Vertex9399(self._io, self, self._root))
                elif _on == 3012694047:
                    self._m_vertices.append(Mod21.VertexB392(self._io, self, self._root))
                elif _on == 307572786:
                    self._m_vertices.append(Mod21.Vertex1255(self._io, self, self._root))
                elif _on == 1126539326:
                    self._m_vertices.append(Mod21.Vertex4325(self._io, self, self._root))
                elif _on == 545452091:
                    self._m_vertices.append(Mod21.Vertex2082(self._io, self, self._root))
                elif _on == 3060273204:
                    self._m_vertices.append(Mod21.VertexB668(self._io, self, self._root))
                elif _on == 349437984:
                    self._m_vertices.append(Mod21.Vertex14d4(self._io, self, self._root))
                elif _on == 545087543:
                    self._m_vertices.append(Mod21.Vertex207d(self._io, self, self._root))
                elif _on == 213286933:
                    self._m_vertices.append(Mod21.VertexCb68(self._io, self, self._root))
                elif _on == 1719341081:
                    self._m_vertices.append(Mod21.Vertex667b(self._io, self, self._root))
                elif _on == 3682443284:
                    self._m_vertices.append(Mod21.VertexDb7d(self._io, self, self._root))
                elif _on == 1236594729:
                    self._m_vertices.append(Mod21.Vertex49b4(self._io, self, self._root))
                elif _on == 228491293:
                    self._m_vertices.append(Mod21.VertexD9e8(self._io, self, self._root))
                elif _on == 2010673186:
                    self._m_vertices.append(Mod21.Vertex77d8(self._io, self, self._root))
                elif _on == 3631710235:
                    self._m_vertices.append(Mod21.VertexD877(self._io, self, self._root))
                elif _on == 2815938614:
                    self._m_vertices.append(Mod21.VertexA7d7(self._io, self, self._root))
                elif _on == 3517214776:
                    self._m_vertices.append(Mod21.VertexD1a4(self._io, self, self._root))
                elif _on == 2736832534:
                    self._m_vertices.append(Mod21.VertexA320(self._io, self, self._root))
                elif _on == 3419369511:
                    self._m_vertices.append(Mod21.VertexCbcf(self._io, self, self._root))
                elif _on == 1683566627:
                    self._m_vertices.append(Mod21.Vertex6459(self._io, self, self._root))
                elif _on == 1975771173:
                    self._m_vertices.append(Mod21.Vertex75c3(self._io, self, self._root))
                elif _on == 3629002790:
                    self._m_vertices.append(Mod21.VertexD84e(self._io, self, self._root))
                elif _on == 2946904109:
                    self._m_vertices.append(Mod21.VertexAfa6(self._io, self, self._root))
                elif _on == 2962763795:
                    self._m_vertices.append(Mod21.VertexB098(self._io, self, self._root))
                elif _on == 1954353201:
                    self._m_vertices.append(Mod21.Vertex747d(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_vertices', None)


    class Vertex49b4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class VertexD1a4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vertex37a4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vertex4325(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.morph_position = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position2 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position3 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_position4 = Mod21.Vec3S2(self._io, self, self._root)
            self.morph_normal = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal2 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal3 = Mod21.Vec3U1(self._io, self, self._root)
            self.morph_normal4 = Mod21.Vec3U1(self._io, self, self._root)


    class VertexDb7d(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())



    class VertexC66f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexB86d(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.vertex_alpha = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.occlusion = self._io.read_u4le()


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



    class Vertex207d(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


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
            self.oabb = Mod21.Matrix4x4(self._io, self, self._root)
            self.oabb_dimension = Mod21.Vec4(self._io, self, self._root)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 144
            return getattr(self, '_m_size_', None)


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
            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(8):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod21.Vec4U1(self._io, self, self._root)


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


    class MaterialsData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.header.version == 210:
                self.material_names = []
                for i in range(self._root.header.num_materials):
                    self.material_names.append((KaitaiStream.bytes_terminate(self._io.read_bytes(128), 0, False)).decode(u"ASCII"))


            if self._root.header.version == 211:
                self.material_hashes = []
                for i in range(self._root.header.num_materials):
                    self.material_hashes.append(self._io.read_u4le())



        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = ((128 * self._root.header.num_materials) if self._root.header.version == 210 else (4 * self._root.header.num_materials))
            return getattr(self, '_m_size_', None)


    class VertexCbcf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values2 = []
            for i in range(2):
                self.weight_values2.append(self._io.read_bytes(2))

            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv4 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class BonesData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bones_hierarchy = []
            for i in range(self._root.header.num_bones):
                self.bones_hierarchy.append(Mod21.Bone(self._io, self, self._root))

            self.parent_space_matrices = []
            for i in range(self._root.header.num_bones):
                self.parent_space_matrices.append(Mod21.Matrix4x4(self._io, self, self._root))

            self.inverse_bind_matrices = []
            for i in range(self._root.header.num_bones):
                self.inverse_bind_matrices.append(Mod21.Matrix4x4(self._io, self, self._root))

            if self._root.header.num_bones != 0:
                self.bone_map = self._io.read_bytes(256)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = (((((self._root.header.num_bones * self.bones_hierarchy[0].size_) + (self._root.header.num_bones * 64)) + (self._root.header.num_bones * 64)) + 256) if self._root.header.num_bones > 0 else 0)
            return getattr(self, '_m_size_', None)


    class Vertex8297(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec4U1(self._io, self, self._root)
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class Vertex1255(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod21.Vec2HalfFloat(self._io, self, self._root)


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

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)


    class VertexAfa6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    class VertexCb68(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod21.Vec4U1(self._io, self, self._root)


    class Vertex9399(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec3(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.rgba = Mod21.Vec4U1(self._io, self, self._root)


    class VertexDa55(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod21.Vec4S2(self._io, self, self._root)
            self.normal = Mod21.Vec3U1(self._io, self, self._root)
            self.occlusion = self._io.read_u1()
            self.tangent = Mod21.Vec4U1(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.uv = Mod21.Vec2HalfFloat(self._io, self, self._root)
            self.weight_values = []
            for i in range(2):
                self.weight_values.append(self._io.read_bytes(2))

            self.uv2 = Mod21.Vec2HalfFloat(self._io, self, self._root)


    @property
    def vertex_buffer(self):
        if hasattr(self, '_m_vertex_buffer'):
            return self._m_vertex_buffer

        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_buffer)
        self._m_vertex_buffer = self._io.read_bytes(self.header.size_vertex_buffer)
        self._io.seek(_pos)
        return getattr(self, '_m_vertex_buffer', None)

    @property
    def materials_data(self):
        if hasattr(self, '_m_materials_data'):
            return self._m_materials_data

        if self.header.offset_materials_data > 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_materials_data)
            self._m_materials_data = Mod21.MaterialsData(self._io, self, self._root)
            self._io.seek(_pos)

        return getattr(self, '_m_materials_data', None)

    @property
    def bones_data_size_(self):
        if hasattr(self, '_m_bones_data_size_'):
            return self._m_bones_data_size_

        self._m_bones_data_size_ = (0 if self.header.num_bones == 0 else self.bones_data.size_)
        return getattr(self, '_m_bones_data_size_', None)

    @property
    def meshes_data(self):
        if hasattr(self, '_m_meshes_data'):
            return self._m_meshes_data

        if self.header.offset_meshes_data > 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_meshes_data)
            self._m_meshes_data = Mod21.MeshesData(self._io, self, self._root)
            self._io.seek(_pos)

        return getattr(self, '_m_meshes_data', None)

    @property
    def index_buffer(self):
        if hasattr(self, '_m_index_buffer'):
            return self._m_index_buffer

        _pos = self._io.pos()
        self._io.seek(self.header.offset_index_buffer)
        self._m_index_buffer = self._io.read_bytes((self.header.num_faces * 2))
        self._io.seek(_pos)
        return getattr(self, '_m_index_buffer', None)

    @property
    def size_top_level_(self):
        if hasattr(self, '_m_size_top_level_'):
            return self._m_size_top_level_

        self._m_size_top_level_ = ((self._root.header.size_ + 68) if self._root.header.version == 210 else (self._root.header.size_ + 64))
        return getattr(self, '_m_size_top_level_', None)

    @property
    def bones_data(self):
        if hasattr(self, '_m_bones_data'):
            return self._m_bones_data

        if self.header.num_bones != 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones_data)
            self._m_bones_data = Mod21.BonesData(self._io, self, self._root)
            self._io.seek(_pos)

        return getattr(self, '_m_bones_data', None)

    @property
    def groups(self):
        if hasattr(self, '_m_groups'):
            return self._m_groups

        _pos = self._io.pos()
        self._io.seek(self.header.offset_groups)
        self._m_groups = []
        for i in range(self.header.num_groups):
            self._m_groups.append(Mod21.Group(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_groups', None)

    @property
    def groups_size_(self):
        if hasattr(self, '_m_groups_size_'):
            return self._m_groups_size_

        self._m_groups_size_ = (self.groups[0].size_ * self.header.num_groups)
        return getattr(self, '_m_groups_size_', None)


