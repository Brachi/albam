# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mod156(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Mod156.ModHeader(self._io, self, self._root)
        self.reserved_01 = self._io.read_u4le()
        self.reserved_02 = self._io.read_u4le()
        self.bsphere = Mod156.Vec4(self._io, self, self._root)
        self.bbox_min = Mod156.Vec4(self._io, self, self._root)
        self.bbox_max = Mod156.Vec4(self._io, self, self._root)
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
            self.vtx8_unk_faces.append(Mod156.UnkVtx8Block00(self._io, self, self._root))

        self.vtx8_unk_uv = []
        for i in range(self.num_vtx8_unk_uv):
            self.vtx8_unk_uv.append(Mod156.UnkVtx8Block01(self._io, self, self._root))

        self.vtx8_unk_normals = []
        for i in range(self.num_vtx8_unk_normals):
            self.vtx8_unk_normals.append(Mod156.UnkVtx8Block02(self._io, self, self._root))


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


    class BonePalette(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_01 = self._io.read_u4le()
            self.indices = []
            for i in range(32):
                self.indices.append(self._io.read_u1())


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 36
            return getattr(self, '_m_size_', None)


    class UnkVtx8Block02(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_00 = self._io.read_u2le()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u2le()


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

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 72
            return getattr(self, '_m_size_', None)


    class Vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod156.Vec4S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(4):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(4):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod156.Vec4U1(self._io, self, self._root)
            self.tangent = Mod156.Vec4U1(self._io, self, self._root)
            self.uv = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod156.Vec2HalfFloat(self._io, self, self._root)


    class Vec2HalfFloat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.u = self._io.read_bytes(2)
            self.v = self._io.read_bytes(2)


    class Matrix4x4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.row_1 = Mod156.Vec4(self._io, self, self._root)
            self.row_2 = Mod156.Vec4(self._io, self, self._root)
            self.row_3 = Mod156.Vec4(self._io, self, self._root)
            self.row_4 = Mod156.Vec4(self._io, self, self._root)


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
            self.location = Mod156.Vec3(self._io, self, self._root)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
            return getattr(self, '_m_size_', None)


    class UnkVtx8Block00(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.idx = self._io.read_u2le()
            self.unk_00 = self._io.read_u2le()


    class Vertex0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod156.Vec3(self._io, self, self._root)
            self.normal = Mod156.Vec4U1(self._io, self, self._root)
            self.tangent = Mod156.Vec4U1(self._io, self, self._root)
            self.uv = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv2 = Mod156.Vec2HalfFloat(self._io, self, self._root)
            self.uv3 = Mod156.Vec2HalfFloat(self._io, self, self._root)


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
                self.meshes.append(Mod156.Mesh(self._io, self, self._root))

            self.num_weight_bounds = self._io.read_u4le()
            self.weight_bounds = []
            for i in range(self.num_weight_bounds):
                self.weight_bounds.append(Mod156.WeightBound(self._io, self, self._root))


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = (((self._root.header.num_meshes * self.meshes[0].size_) + 4) + (self.num_weight_bounds * self.weight_bounds[0].size_))
            return getattr(self, '_m_size_', None)


    class Mesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.idx_group = self._io.read_u2le()
            self.idx_material = self._io.read_u2le()
            self.constant = self._io.read_u1()
            self.level_of_detail = self._io.read_u1()
            self.unk_01 = self._io.read_u1()
            self.vertex_format = self._io.read_u1()
            self.vertex_stride = self._io.read_u1()
            self.vertex_stride_2 = self._io.read_u1()
            self.unk_03 = self._io.read_u1()
            self.unk_flags = self._io.read_u1()
            self.num_vertices = self._io.read_u2le()
            self.vertex_position_end = self._io.read_u2le()
            self.vertex_position_2 = self._io.read_u4le()
            self.vertex_offset = self._io.read_u4le()
            self.unk_05 = self._io.read_u4le()
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

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 52
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
            self._io.seek((((self._root.header.offset_vertex_buffer + (self.vertex_position * self.vertex_stride)) + self.vertex_offset) if self.vertex_position > self.vertex_position_2 else ((self._root.header.offset_vertex_buffer + (self.vertex_position * self.vertex_stride)) + self.vertex_offset)))
            self._m_vertices = []
            for i in range((((self.vertex_position_end - self.vertex_position) + 1) if self.vertex_position > self.vertex_position_2 else self.num_vertices)):
                _on = self.vertex_format
                if _on == 0:
                    self._m_vertices.append(Mod156.Vertex0(self._io, self, self._root))
                elif _on == 4:
                    self._m_vertices.append(Mod156.Vertex(self._io, self, self._root))
                elif _on == 6:
                    self._m_vertices.append(Mod156.Vertex5(self._io, self, self._root))
                elif _on == 7:
                    self._m_vertices.append(Mod156.Vertex5(self._io, self, self._root))
                elif _on == 1:
                    self._m_vertices.append(Mod156.Vertex(self._io, self, self._root))
                elif _on == 3:
                    self._m_vertices.append(Mod156.Vertex(self._io, self, self._root))
                elif _on == 5:
                    self._m_vertices.append(Mod156.Vertex5(self._io, self, self._root))
                elif _on == 8:
                    self._m_vertices.append(Mod156.Vertex5(self._io, self, self._root))
                elif _on == 2:
                    self._m_vertices.append(Mod156.Vertex(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_vertices', None)


    class UnkVtx8Block01(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u2le()
            self.unk_03 = self._io.read_u4le()
            self.unk_05 = self._io.read_u2le()
            self.unk_06 = self._io.read_u2le()
            self.unk_07 = self._io.read_u2le()
            self.unk_08 = self._io.read_u2le()


    class Material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk_01 = self._io.read_u2le()
            self.unk_flags = self._io.read_u2le()
            self.unk_shorts = []
            for i in range(10):
                self.unk_shorts.append(self._io.read_u2le())

            self.texture_slots = []
            for i in range(8):
                self.texture_slots.append(self._io.read_u4le())

            self.unk_floats = []
            for i in range(26):
                self.unk_floats.append(self._io.read_f4le())


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 160
            return getattr(self, '_m_size_', None)


    class WeightBound(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bone_id = self._io.read_u4le()
            self.unk_01 = Mod156.Vec3(self._io, self, self._root)
            self.bsphere = Mod156.Vec4(self._io, self, self._root)
            self.bbox_min = Mod156.Vec4(self._io, self, self._root)
            self.bbox_max = Mod156.Vec4(self._io, self, self._root)
            self.oabb = Mod156.Matrix4x4(self._io, self, self._root)
            self.oabb_dimension = Mod156.Vec4(self._io, self, self._root)

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


    class MaterialsData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.textures = []
            for i in range(self._root.header.num_textures):
                self.textures.append((KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ASCII"))

            self.materials = []
            for i in range(self._root.header.num_materials):
                self.materials.append(Mod156.Material(self._io, self, self._root))


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = ((64 * self._root.header.num_textures) + (self._root.header.num_materials * self.materials[0].size_))
            return getattr(self, '_m_size_', None)


    class BonesData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bones_hierarchy = []
            for i in range(self._root.header.num_bones):
                self.bones_hierarchy.append(Mod156.Bone(self._io, self, self._root))

            self.parent_space_matrices = []
            for i in range(self._root.header.num_bones):
                self.parent_space_matrices.append(Mod156.Matrix4x4(self._io, self, self._root))

            self.inverse_bind_matrices = []
            for i in range(self._root.header.num_bones):
                self.inverse_bind_matrices.append(Mod156.Matrix4x4(self._io, self, self._root))

            if self._root.header.num_bones != 0:
                self.bone_map = self._io.read_bytes(256)

            self.bone_palettes = []
            for i in range(self._root.header.num_bone_palettes):
                self.bone_palettes.append(Mod156.BonePalette(self._io, self, self._root))


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = ((((((self._root.header.num_bones * self.bones_hierarchy[0].size_) + (self._root.header.num_bones * 64)) + (self._root.header.num_bones * 64)) + 256) + (self._root.header.num_bone_palettes * self.bone_palettes[0].size_)) if self._root.header.num_bones > 0 else 0)
            return getattr(self, '_m_size_', None)


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


    class Vertex5(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = Mod156.Vec4S2(self._io, self, self._root)
            self.bone_indices = []
            for i in range(8):
                self.bone_indices.append(self._io.read_u1())

            self.weight_values = []
            for i in range(8):
                self.weight_values.append(self._io.read_u1())

            self.normal = Mod156.Vec4U1(self._io, self, self._root)
            self.uv = Mod156.Vec2HalfFloat(self._io, self, self._root)


    @property
    def vertex_buffer(self):
        if hasattr(self, '_m_vertex_buffer'):
            return self._m_vertex_buffer

        if self.header.offset_vertex_buffer > 0:
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
            self._m_materials_data = Mod156.MaterialsData(self._io, self, self._root)
            self._io.seek(_pos)

        return getattr(self, '_m_materials_data', None)

    @property
    def bones_data_size_(self):
        if hasattr(self, '_m_bones_data_size_'):
            return self._m_bones_data_size_

        self._m_bones_data_size_ = (0 if self.header.num_bones == 0 else self.bones_data.size_)
        return getattr(self, '_m_bones_data_size_', None)

    @property
    def vertex_buffer_2(self):
        if hasattr(self, '_m_vertex_buffer_2'):
            return self._m_vertex_buffer_2

        if self.header.offset_vertex_buffer_2 > 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_vertex_buffer)
            self._m_vertex_buffer_2 = self._io.read_bytes(self.header.size_vertex_buffer_2)
            self._io.seek(_pos)

        return getattr(self, '_m_vertex_buffer_2', None)

    @property
    def meshes_data(self):
        if hasattr(self, '_m_meshes_data'):
            return self._m_meshes_data

        if self.header.offset_meshes_data > 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_meshes_data)
            self._m_meshes_data = Mod156.MeshesData(self._io, self, self._root)
            self._io.seek(_pos)

        return getattr(self, '_m_meshes_data', None)

    @property
    def index_buffer(self):
        if hasattr(self, '_m_index_buffer'):
            return self._m_index_buffer

        if self.header.offset_index_buffer > 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer)
            self._m_index_buffer = self._io.read_bytes(((self.header.num_faces * 2) - 2))
            self._io.seek(_pos)

        return getattr(self, '_m_index_buffer', None)

    @property
    def size_top_level_(self):
        if hasattr(self, '_m_size_top_level_'):
            return self._m_size_top_level_

        self._m_size_top_level_ = (self._root.header.size_ + 104)
        return getattr(self, '_m_size_top_level_', None)

    @property
    def bones_data(self):
        if hasattr(self, '_m_bones_data'):
            return self._m_bones_data

        if self.header.num_bones != 0:
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones_data)
            self._m_bones_data = Mod156.BonesData(self._io, self, self._root)
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
            self._m_groups.append(Mod156.Group(self._io, self, self._root))

        self._io.seek(_pos)
        return getattr(self, '_m_groups', None)

    @property
    def groups_size_(self):
        if hasattr(self, '_m_groups_size_'):
            return self._m_groups_size_

        self._m_groups_size_ = (self.groups[0].size_ * self.header.num_groups)
        return getattr(self, '_m_groups_size_', None)


