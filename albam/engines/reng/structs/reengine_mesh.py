# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineMesh(ReadWriteKaitaiStruct):

    class PrimitiveType(IntEnum):
        position = 0
        nor_tan = 1
        uv = 2
        uv2 = 3
        weight = 4
        color = 5
        sf6_unknown_vertex_data_type = 6
        extra_weight = 7
    def __init__(self, _io=None, _parent=None, _root=None):
        super(ReengineMesh, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_blend_shape_name_remap = False
        self.blend_shape_name_remap__enabled = True
        self._should_write_bone_aabb_group = False
        self.bone_aabb_group__enabled = True
        self._should_write_bone_name_remap = False
        self.bone_name_remap__enabled = True
        self._should_write_bones_header = False
        self.bones_header__enabled = True
        self._should_write_buffers_data = False
        self.buffers_data__enabled = True
        self._should_write_material_name_remap = False
        self.material_name_remap__enabled = True
        self._should_write_model_info = False
        self.model_info__enabled = True
        self._should_write_named_nodes = False
        self.named_nodes__enabled = True
        self._should_write_occlusion_mesh_group = False
        self.occlusion_mesh_group__enabled = True
        self._should_write_shadow_header = False
        self.shadow_header__enabled = True

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x45\x53\x48":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x45\x53\x48", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.file_size = self._io.read_u4le()
        self.lod_group_name_hash = self._io.read_u4le()
        self.header = ReengineMesh.Header(self._io, self, self._root)
        self.header._read()
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.blend_shape_name_remap
        if hasattr(self, '_m_blend_shape_name_remap'):
            pass
            for i in range(len(self._m_blend_shape_name_remap)):
                pass


        _ = self.bone_aabb_group
        if hasattr(self, '_m_bone_aabb_group'):
            pass
            self._m_bone_aabb_group._fetch_instances()

        _ = self.bone_name_remap
        if hasattr(self, '_m_bone_name_remap'):
            pass
            for i in range(len(self._m_bone_name_remap)):
                pass


        _ = self.bones_header
        if hasattr(self, '_m_bones_header'):
            pass
            self._m_bones_header._fetch_instances()

        _ = self.buffers_data
        if hasattr(self, '_m_buffers_data'):
            pass
            self._m_buffers_data._fetch_instances()

        _ = self.material_name_remap
        if hasattr(self, '_m_material_name_remap'):
            pass
            for i in range(len(self._m_material_name_remap)):
                pass


        _ = self.model_info
        if hasattr(self, '_m_model_info'):
            pass
            self._m_model_info._fetch_instances()

        _ = self.named_nodes
        if hasattr(self, '_m_named_nodes'):
            pass
            for i in range(len(self._m_named_nodes)):
                pass
                self._m_named_nodes[i]._fetch_instances()


        _ = self.occlusion_mesh_group
        if hasattr(self, '_m_occlusion_mesh_group'):
            pass
            self._m_occlusion_mesh_group._fetch_instances()

        _ = self.shadow_header
        if hasattr(self, '_m_shadow_header'):
            pass
            self._m_shadow_header._fetch_instances()



    def _write__seq(self, io=None):
        super(ReengineMesh, self)._write__seq(io)
        self._should_write_blend_shape_name_remap = self.blend_shape_name_remap__enabled
        self._should_write_bone_aabb_group = self.bone_aabb_group__enabled
        self._should_write_bone_name_remap = self.bone_name_remap__enabled
        self._should_write_bones_header = self.bones_header__enabled
        self._should_write_buffers_data = self.buffers_data__enabled
        self._should_write_material_name_remap = self.material_name_remap__enabled
        self._should_write_model_info = self.model_info__enabled
        self._should_write_named_nodes = self.named_nodes__enabled
        self._should_write_occlusion_mesh_group = self.occlusion_mesh_group__enabled
        self._should_write_shadow_header = self.shadow_header__enabled
        self._io.write_bytes(self.id_magic)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.file_size)
        self._io.write_u4le(self.lod_group_name_hash)
        self.header._write__seq(self._io)


    def _check(self):
        if len(self.id_magic) != 4:
            raise kaitaistruct.ConsistencyError(u"id_magic", 4, len(self.id_magic))
        if not self.id_magic == b"\x4D\x45\x53\x48":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x45\x53\x48", self.id_magic, None, u"/seq/0")
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if self.blend_shape_name_remap__enabled:
            pass
            if self.header.offset_blend_shape_name_remap != 0:
                pass
                for i in range(len(self._m_blend_shape_name_remap)):
                    pass



        if self.bone_aabb_group__enabled:
            pass
            if self.header.offset_bone_aabb != 0:
                pass
                if self._m_bone_aabb_group._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bone_aabb_group", self._root, self._m_bone_aabb_group._root)
                if self._m_bone_aabb_group._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bone_aabb_group", self, self._m_bone_aabb_group._parent)


        if self.bone_name_remap__enabled:
            pass
            if  ((self.header.offset_bone_name_remap != 0) and (self.header.offset_bones != 0)) :
                pass
                for i in range(len(self._m_bone_name_remap)):
                    pass



        if self.bones_header__enabled:
            pass
            if self.header.offset_bones != 0:
                pass
                if self._m_bones_header._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bones_header", self._root, self._m_bones_header._root)
                if self._m_bones_header._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bones_header", self, self._m_bones_header._parent)


        if self.buffers_data__enabled:
            pass
            if self._m_buffers_data._root != self._root:
                raise kaitaistruct.ConsistencyError(u"buffers_data", self._root, self._m_buffers_data._root)
            if self._m_buffers_data._parent != self:
                raise kaitaistruct.ConsistencyError(u"buffers_data", self, self._m_buffers_data._parent)

        if self.material_name_remap__enabled:
            pass
            if  ((self.header.offset_material_name_remap != 0) and (self.header.offset_data != 0)) :
                pass
                for i in range(len(self._m_material_name_remap)):
                    pass



        if self.model_info__enabled:
            pass
            if self.header.offset_data != 0:
                pass
                if self._m_model_info._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"model_info", self._root, self._m_model_info._root)
                if self._m_model_info._parent != self:
                    raise kaitaistruct.ConsistencyError(u"model_info", self, self._m_model_info._parent)


        if self.named_nodes__enabled:
            pass
            if len(self._m_named_nodes) != self.header.num_named_nodes:
                raise kaitaistruct.ConsistencyError(u"named_nodes", self.header.num_named_nodes, len(self._m_named_nodes))
            for i in range(len(self._m_named_nodes)):
                pass
                if self._m_named_nodes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"named_nodes", self._root, self._m_named_nodes[i]._root)
                if self._m_named_nodes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"named_nodes", self, self._m_named_nodes[i]._parent)


        if self.occlusion_mesh_group__enabled:
            pass
            if self.header.offset_occlusion_mesh_group != 0:
                pass
                if self._m_occlusion_mesh_group._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"occlusion_mesh_group", self._root, self._m_occlusion_mesh_group._root)
                if self._m_occlusion_mesh_group._parent != self:
                    raise kaitaistruct.ConsistencyError(u"occlusion_mesh_group", self, self._m_occlusion_mesh_group._parent)


        if self.shadow_header__enabled:
            pass
            if self.header.offset_shadow_mesh_group != 0:
                pass
                if self._m_shadow_header._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"shadow_header", self._root, self._m_shadow_header._root)
                if self._m_shadow_header._parent != self:
                    raise kaitaistruct.ConsistencyError(u"shadow_header", self, self._m_shadow_header._parent)


        self._dirty = False

    class Aabb(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Aabb, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.min = ReengineMesh.Vec4(self._io, self, self._root)
            self.min._read()
            self.max = ReengineMesh.Vec4(self._io, self, self._root)
            self.max._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.min._fetch_instances()
            self.max._fetch_instances()


        def _write__seq(self, io=None):
            super(ReengineMesh.Aabb, self)._write__seq(io)
            self.min._write__seq(self._io)
            self.max._write__seq(self._io)


        def _check(self):
            if self.min._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min", self._root, self.min._root)
            if self.min._parent != self:
                raise kaitaistruct.ConsistencyError(u"min", self, self.min._parent)
            if self.max._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max", self._root, self.max._root)
            if self.max._parent != self:
                raise kaitaistruct.ConsistencyError(u"max", self, self.max._parent)
            self._dirty = False


    class Bone(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Bone, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.idx = self._io.read_u2le()
            self.parent_idx = self._io.read_s2le()
            self.sibling_idx = self._io.read_s2le()
            self.child_idx = self._io.read_s2le()
            self.symmetric_idx = self._io.read_s2le()
            self.use_secondary_weight = self._io.read_s2le()
            self.padding_0 = self._io.read_u2le()
            self.padding_1 = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMesh.Bone, self)._write__seq(io)
            self._io.write_u2le(self.idx)
            self._io.write_s2le(self.parent_idx)
            self._io.write_s2le(self.sibling_idx)
            self._io.write_s2le(self.child_idx)
            self._io.write_s2le(self.symmetric_idx)
            self._io.write_s2le(self.use_secondary_weight)
            self._io.write_u2le(self.padding_0)
            self._io.write_u2le(self.padding_1)


        def _check(self):
            self._dirty = False


    class BoneAabbGroup(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.BoneAabbGroup, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_entries = self._io.read_u8le()
            self.offset_entries = self._io.read_u8le()
            self.entries = []
            for i in range(self.num_entries):
                _t_entries = ReengineMesh.Aabb(self._io, self, self._root)
                try:
                    _t_entries._read()
                finally:
                    self.entries.append(_t_entries)

            self.padding = self._io.read_bytes((16 - self._io.pos() % 16) % 16)
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass
                self.entries[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMesh.BoneAabbGroup, self)._write__seq(io)
            self._io.write_u8le(self.num_entries)
            self._io.write_u8le(self.offset_entries)
            for i in range(len(self.entries)):
                pass
                self.entries[i]._write__seq(self._io)

            if len(self.padding) != (16 - self._io.pos() % 16) % 16:
                raise kaitaistruct.ConsistencyError(u"padding", (16 - self._io.pos() % 16) % 16, len(self.padding))
            self._io.write_bytes(self.padding)


        def _check(self):
            if len(self.entries) != self.num_entries:
                raise kaitaistruct.ConsistencyError(u"entries", self.num_entries, len(self.entries))
            for i in range(len(self.entries)):
                pass
                if self.entries[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entries", self._root, self.entries[i]._root)
                if self.entries[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entries", self, self.entries[i]._parent)

            self._dirty = False


    class BoneHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.BoneHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_bones = False
            self.bones__enabled = True
            self._should_write_inverse_bind_matrices = False
            self.inverse_bind_matrices__enabled = True
            self._should_write_local_matrices = False
            self.local_matrices__enabled = True
            self._should_write_world_matrices = False
            self.world_matrices__enabled = True

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

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.bone_maps)):
                pass

            _ = self.bones
            if hasattr(self, '_m_bones'):
                pass
                for i in range(len(self._m_bones)):
                    pass
                    self._m_bones[i]._fetch_instances()


            _ = self.inverse_bind_matrices
            if hasattr(self, '_m_inverse_bind_matrices'):
                pass
                for i in range(len(self._m_inverse_bind_matrices)):
                    pass
                    self._m_inverse_bind_matrices[i]._fetch_instances()


            _ = self.local_matrices
            if hasattr(self, '_m_local_matrices'):
                pass
                for i in range(len(self._m_local_matrices)):
                    pass
                    self._m_local_matrices[i]._fetch_instances()


            _ = self.world_matrices
            if hasattr(self, '_m_world_matrices'):
                pass
                for i in range(len(self._m_world_matrices)):
                    pass
                    self._m_world_matrices[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(ReengineMesh.BoneHeader, self)._write__seq(io)
            self._should_write_bones = self.bones__enabled
            self._should_write_inverse_bind_matrices = self.inverse_bind_matrices__enabled
            self._should_write_local_matrices = self.local_matrices__enabled
            self._should_write_world_matrices = self.world_matrices__enabled
            self._io.write_u4le(self.num_bones)
            self._io.write_u4le(self.num_bone_maps)
            self._io.write_u4le(self.reserved_01)
            self._io.write_u4le(self.reserved_02)
            self._io.write_u8le(self.offset_parent_bone)
            self._io.write_u8le(self.offset_matrix_1)
            self._io.write_u8le(self.offset_matrix_2)
            self._io.write_u8le(self.offset_inverse_bind_matrices)
            for i in range(len(self.bone_maps)):
                pass
                self._io.write_u2le(self.bone_maps[i])



        def _check(self):
            if len(self.bone_maps) != self.num_bone_maps:
                raise kaitaistruct.ConsistencyError(u"bone_maps", self.num_bone_maps, len(self.bone_maps))
            for i in range(len(self.bone_maps)):
                pass

            if self.bones__enabled:
                pass
                if len(self._m_bones) != self.num_bones:
                    raise kaitaistruct.ConsistencyError(u"bones", self.num_bones, len(self._m_bones))
                for i in range(len(self._m_bones)):
                    pass
                    if self._m_bones[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"bones", self._root, self._m_bones[i]._root)
                    if self._m_bones[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"bones", self, self._m_bones[i]._parent)


            if self.inverse_bind_matrices__enabled:
                pass
                if len(self._m_inverse_bind_matrices) != self.num_bones:
                    raise kaitaistruct.ConsistencyError(u"inverse_bind_matrices", self.num_bones, len(self._m_inverse_bind_matrices))
                for i in range(len(self._m_inverse_bind_matrices)):
                    pass
                    if self._m_inverse_bind_matrices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"inverse_bind_matrices", self._root, self._m_inverse_bind_matrices[i]._root)
                    if self._m_inverse_bind_matrices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"inverse_bind_matrices", self, self._m_inverse_bind_matrices[i]._parent)


            if self.local_matrices__enabled:
                pass
                if len(self._m_local_matrices) != self.num_bones:
                    raise kaitaistruct.ConsistencyError(u"local_matrices", self.num_bones, len(self._m_local_matrices))
                for i in range(len(self._m_local_matrices)):
                    pass
                    if self._m_local_matrices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"local_matrices", self._root, self._m_local_matrices[i]._root)
                    if self._m_local_matrices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"local_matrices", self, self._m_local_matrices[i]._parent)


            if self.world_matrices__enabled:
                pass
                if len(self._m_world_matrices) != self.num_bones:
                    raise kaitaistruct.ConsistencyError(u"world_matrices", self.num_bones, len(self._m_world_matrices))
                for i in range(len(self._m_world_matrices)):
                    pass
                    if self._m_world_matrices[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"world_matrices", self._root, self._m_world_matrices[i]._root)
                    if self._m_world_matrices[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"world_matrices", self, self._m_world_matrices[i]._parent)


            self._dirty = False

        @property
        def bones(self):
            if self._should_write_bones:
                self._write_bones()
            if hasattr(self, '_m_bones'):
                return self._m_bones

            if not self.bones__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_parent_bone)
            self._m_bones = []
            for i in range(self.num_bones):
                _t__m_bones = ReengineMesh.Bone(self._io, self, self._root)
                try:
                    _t__m_bones._read()
                finally:
                    self._m_bones.append(_t__m_bones)

            self._io.seek(_pos)
            return getattr(self, '_m_bones', None)

        @bones.setter
        def bones(self, v):
            self._dirty = True
            self._m_bones = v

        def _write_bones(self):
            self._should_write_bones = False
            _pos = self._io.pos()
            self._io.seek(self.offset_parent_bone)
            for i in range(len(self._m_bones)):
                pass
                self._m_bones[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def inverse_bind_matrices(self):
            if self._should_write_inverse_bind_matrices:
                self._write_inverse_bind_matrices()
            if hasattr(self, '_m_inverse_bind_matrices'):
                return self._m_inverse_bind_matrices

            if not self.inverse_bind_matrices__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_inverse_bind_matrices)
            self._m_inverse_bind_matrices = []
            for i in range(self.num_bones):
                _t__m_inverse_bind_matrices = ReengineMesh.Matrix4x4(self._io, self, self._root)
                try:
                    _t__m_inverse_bind_matrices._read()
                finally:
                    self._m_inverse_bind_matrices.append(_t__m_inverse_bind_matrices)

            self._io.seek(_pos)
            return getattr(self, '_m_inverse_bind_matrices', None)

        @inverse_bind_matrices.setter
        def inverse_bind_matrices(self, v):
            self._dirty = True
            self._m_inverse_bind_matrices = v

        def _write_inverse_bind_matrices(self):
            self._should_write_inverse_bind_matrices = False
            _pos = self._io.pos()
            self._io.seek(self.offset_inverse_bind_matrices)
            for i in range(len(self._m_inverse_bind_matrices)):
                pass
                self._m_inverse_bind_matrices[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def local_matrices(self):
            if self._should_write_local_matrices:
                self._write_local_matrices()
            if hasattr(self, '_m_local_matrices'):
                return self._m_local_matrices

            if not self.local_matrices__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_matrix_1)
            self._m_local_matrices = []
            for i in range(self.num_bones):
                _t__m_local_matrices = ReengineMesh.Matrix4x4(self._io, self, self._root)
                try:
                    _t__m_local_matrices._read()
                finally:
                    self._m_local_matrices.append(_t__m_local_matrices)

            self._io.seek(_pos)
            return getattr(self, '_m_local_matrices', None)

        @local_matrices.setter
        def local_matrices(self, v):
            self._dirty = True
            self._m_local_matrices = v

        def _write_local_matrices(self):
            self._should_write_local_matrices = False
            _pos = self._io.pos()
            self._io.seek(self.offset_matrix_1)
            for i in range(len(self._m_local_matrices)):
                pass
                self._m_local_matrices[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def world_matrices(self):
            if self._should_write_world_matrices:
                self._write_world_matrices()
            if hasattr(self, '_m_world_matrices'):
                return self._m_world_matrices

            if not self.world_matrices__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_matrix_2)
            self._m_world_matrices = []
            for i in range(self.num_bones):
                _t__m_world_matrices = ReengineMesh.Matrix4x4(self._io, self, self._root)
                try:
                    _t__m_world_matrices._read()
                finally:
                    self._m_world_matrices.append(_t__m_world_matrices)

            self._io.seek(_pos)
            return getattr(self, '_m_world_matrices', None)

        @world_matrices.setter
        def world_matrices(self, v):
            self._dirty = True
            self._m_world_matrices = v

        def _write_world_matrices(self):
            self._should_write_world_matrices = False
            _pos = self._io.pos()
            self._io.seek(self.offset_matrix_2)
            for i in range(len(self._m_world_matrices)):
                pass
                self._m_world_matrices[i]._write__seq(self._io)

            self._io.seek(_pos)


    class BuffersHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.BuffersHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_index_buffer = False
            self.index_buffer__enabled = True
            self._should_write_primitive_accessors = False
            self.primitive_accessors__enabled = True
            self._should_write_vertex_buffer = False
            self.vertex_buffer__enabled = True

        def _read(self):
            self.offset_primitive_accessors = self._io.read_u8le()
            self.offset_vertex_buffer = self._io.read_u8le()
            self.offset_index_buffer = self._io.read_u8le()
            if self._root.version == 21041600:
                pass
                self.unk_00 = self._io.read_u8le()

            self.size_vertex_buffer = self._io.read_u4le()
            self.size_index_buffer = self._io.read_u4le()
            self.num_unk = self._io.read_u2le()
            self.num_primitive_accessors = self._io.read_u2le()
            self.unk_01 = self._io.read_u4le()
            self.reserved_01 = self._io.read_u4le()
            self.unk_2 = self._io.read_u2le()
            self.unk_3 = self._io.read_u2le()
            if self._root.version == 21041600:
                pass
                self.unk_04 = self._io.read_u8le()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.version == 21041600:
                pass

            if self._root.version == 21041600:
                pass

            _ = self.index_buffer
            if hasattr(self, '_m_index_buffer'):
                pass

            _ = self.primitive_accessors
            if hasattr(self, '_m_primitive_accessors'):
                pass
                for i in range(len(self._m_primitive_accessors)):
                    pass
                    self._m_primitive_accessors[i]._fetch_instances()


            _ = self.vertex_buffer
            if hasattr(self, '_m_vertex_buffer'):
                pass



        def _write__seq(self, io=None):
            super(ReengineMesh.BuffersHeader, self)._write__seq(io)
            self._should_write_index_buffer = self.index_buffer__enabled
            self._should_write_primitive_accessors = self.primitive_accessors__enabled
            self._should_write_vertex_buffer = self.vertex_buffer__enabled
            self._io.write_u8le(self.offset_primitive_accessors)
            self._io.write_u8le(self.offset_vertex_buffer)
            self._io.write_u8le(self.offset_index_buffer)
            if self._root.version == 21041600:
                pass
                self._io.write_u8le(self.unk_00)

            self._io.write_u4le(self.size_vertex_buffer)
            self._io.write_u4le(self.size_index_buffer)
            self._io.write_u2le(self.num_unk)
            self._io.write_u2le(self.num_primitive_accessors)
            self._io.write_u4le(self.unk_01)
            self._io.write_u4le(self.reserved_01)
            self._io.write_u2le(self.unk_2)
            self._io.write_u2le(self.unk_3)
            if self._root.version == 21041600:
                pass
                self._io.write_u8le(self.unk_04)



        def _check(self):
            if self._root.version == 21041600:
                pass

            if self._root.version == 21041600:
                pass

            if self.index_buffer__enabled:
                pass
                if len(self._m_index_buffer) != self.size_index_buffer:
                    raise kaitaistruct.ConsistencyError(u"index_buffer", self.size_index_buffer, len(self._m_index_buffer))

            if self.primitive_accessors__enabled:
                pass
                if len(self._m_primitive_accessors) != self.num_primitive_accessors:
                    raise kaitaistruct.ConsistencyError(u"primitive_accessors", self.num_primitive_accessors, len(self._m_primitive_accessors))
                for i in range(len(self._m_primitive_accessors)):
                    pass
                    if self._m_primitive_accessors[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"primitive_accessors", self._root, self._m_primitive_accessors[i]._root)
                    if self._m_primitive_accessors[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"primitive_accessors", self, self._m_primitive_accessors[i]._parent)


            if self.vertex_buffer__enabled:
                pass
                if len(self._m_vertex_buffer) != self.size_vertex_buffer:
                    raise kaitaistruct.ConsistencyError(u"vertex_buffer", self.size_vertex_buffer, len(self._m_vertex_buffer))

            self._dirty = False

        @property
        def index_buffer(self):
            if self._should_write_index_buffer:
                self._write_index_buffer()
            if hasattr(self, '_m_index_buffer'):
                return self._m_index_buffer

            if not self.index_buffer__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_index_buffer)
            self._m_index_buffer = self._io.read_bytes(self.size_index_buffer)
            self._io.seek(_pos)
            return getattr(self, '_m_index_buffer', None)

        @index_buffer.setter
        def index_buffer(self, v):
            self._dirty = True
            self._m_index_buffer = v

        def _write_index_buffer(self):
            self._should_write_index_buffer = False
            _pos = self._io.pos()
            self._io.seek(self.offset_index_buffer)
            self._io.write_bytes(self._m_index_buffer)
            self._io.seek(_pos)

        @property
        def primitive_accessors(self):
            if self._should_write_primitive_accessors:
                self._write_primitive_accessors()
            if hasattr(self, '_m_primitive_accessors'):
                return self._m_primitive_accessors

            if not self.primitive_accessors__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_primitive_accessors)
            self._m_primitive_accessors = []
            for i in range(self.num_primitive_accessors):
                _t__m_primitive_accessors = ReengineMesh.PrimitiveAccessor(self._io, self, self._root)
                try:
                    _t__m_primitive_accessors._read()
                finally:
                    self._m_primitive_accessors.append(_t__m_primitive_accessors)

            self._io.seek(_pos)
            return getattr(self, '_m_primitive_accessors', None)

        @primitive_accessors.setter
        def primitive_accessors(self, v):
            self._dirty = True
            self._m_primitive_accessors = v

        def _write_primitive_accessors(self):
            self._should_write_primitive_accessors = False
            _pos = self._io.pos()
            self._io.seek(self.offset_primitive_accessors)
            for i in range(len(self._m_primitive_accessors)):
                pass
                self._m_primitive_accessors[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def vertex_buffer(self):
            if self._should_write_vertex_buffer:
                self._write_vertex_buffer()
            if hasattr(self, '_m_vertex_buffer'):
                return self._m_vertex_buffer

            if not self.vertex_buffer__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_vertex_buffer)
            self._m_vertex_buffer = self._io.read_bytes(self.size_vertex_buffer)
            self._io.seek(_pos)
            return getattr(self, '_m_vertex_buffer', None)

        @vertex_buffer.setter
        def vertex_buffer(self, v):
            self._dirty = True
            self._m_vertex_buffer = v

        def _write_vertex_buffer(self):
            self._should_write_vertex_buffer = False
            _pos = self._io.pos()
            self._io.seek(self.offset_vertex_buffer)
            self._io.write_bytes(self._m_vertex_buffer)
            self._io.seek(_pos)


    class Header(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Header, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.content_flags = self._io.read_u2le()
            self.num_named_nodes = self._io.read_u2le()
            self.unk_01 = self._io.read_u4le()
            self.offset_data = self._io.read_u8le()
            self.offset_shadow_mesh_group = self._io.read_u8le()
            self.offset_occlusion_mesh_group = self._io.read_u8le()
            self.offset_bones = self._io.read_u8le()
            self.offset_normal_recalc = self._io.read_u8le()
            self.offset_blend_shapes = self._io.read_u8le()
            self.offset_bone_aabb = self._io.read_u8le()
            self.offset_buffers_header = self._io.read_u8le()
            self.offset_floats = self._io.read_u8le()
            self.offset_material_name_remap = self._io.read_u8le()
            self.offset_bone_name_remap = self._io.read_u8le()
            self.offset_blend_shape_name_remap = self._io.read_u8le()
            self.offset_names = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMesh.Header, self)._write__seq(io)
            self._io.write_u2le(self.content_flags)
            self._io.write_u2le(self.num_named_nodes)
            self._io.write_u4le(self.unk_01)
            self._io.write_u8le(self.offset_data)
            self._io.write_u8le(self.offset_shadow_mesh_group)
            self._io.write_u8le(self.offset_occlusion_mesh_group)
            self._io.write_u8le(self.offset_bones)
            self._io.write_u8le(self.offset_normal_recalc)
            self._io.write_u8le(self.offset_blend_shapes)
            self._io.write_u8le(self.offset_bone_aabb)
            self._io.write_u8le(self.offset_buffers_header)
            self._io.write_u8le(self.offset_floats)
            self._io.write_u8le(self.offset_material_name_remap)
            self._io.write_u8le(self.offset_bone_name_remap)
            self._io.write_u8le(self.offset_blend_shape_name_remap)
            self._io.write_u8le(self.offset_names)


        def _check(self):
            self._dirty = False


    class LodGroup(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.LodGroup, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_mesh_groups = self._io.read_u1()
            self.vertex_format = self._io.read_u1()
            self.reserved_01 = self._io.read_u2le()
            self.distance = self._io.read_f4le()
            self.offset_main_mesh_header = self._io.read_u8le()
            self.mesh_groups = []
            for i in range(self.num_mesh_groups):
                _t_mesh_groups = ReengineMesh.MeshGroupOffset(self._io, self, self._root)
                try:
                    _t_mesh_groups._read()
                finally:
                    self.mesh_groups.append(_t_mesh_groups)

            self.padding = self._io.read_bytes((16 - self._io.pos() % 16) % 16)
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.mesh_groups)):
                pass
                self.mesh_groups[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMesh.LodGroup, self)._write__seq(io)
            self._io.write_u1(self.num_mesh_groups)
            self._io.write_u1(self.vertex_format)
            self._io.write_u2le(self.reserved_01)
            self._io.write_f4le(self.distance)
            self._io.write_u8le(self.offset_main_mesh_header)
            for i in range(len(self.mesh_groups)):
                pass
                self.mesh_groups[i]._write__seq(self._io)

            if len(self.padding) != (16 - self._io.pos() % 16) % 16:
                raise kaitaistruct.ConsistencyError(u"padding", (16 - self._io.pos() % 16) % 16, len(self.padding))
            self._io.write_bytes(self.padding)


        def _check(self):
            if len(self.mesh_groups) != self.num_mesh_groups:
                raise kaitaistruct.ConsistencyError(u"mesh_groups", self.num_mesh_groups, len(self.mesh_groups))
            for i in range(len(self.mesh_groups)):
                pass
                if self.mesh_groups[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"mesh_groups", self._root, self.mesh_groups[i]._root)
                if self.mesh_groups[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"mesh_groups", self, self.mesh_groups[i]._parent)

            self._dirty = False


    class LodGroupOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.LodGroupOffset, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_lod_group = False
            self.lod_group__enabled = True

        def _read(self):
            self.offset = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.lod_group
            if hasattr(self, '_m_lod_group'):
                pass
                self._m_lod_group._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMesh.LodGroupOffset, self)._write__seq(io)
            self._should_write_lod_group = self.lod_group__enabled
            self._io.write_u8le(self.offset)


        def _check(self):
            if self.lod_group__enabled:
                pass
                if self._m_lod_group._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"lod_group", self._root, self._m_lod_group._root)
                if self._m_lod_group._parent != self:
                    raise kaitaistruct.ConsistencyError(u"lod_group", self, self._m_lod_group._parent)

            self._dirty = False

        @property
        def lod_group(self):
            if self._should_write_lod_group:
                self._write_lod_group()
            if hasattr(self, '_m_lod_group'):
                return self._m_lod_group

            if not self.lod_group__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_lod_group = ReengineMesh.LodGroup(self._io, self, self._root)
            self._m_lod_group._read()
            self._io.seek(_pos)
            return getattr(self, '_m_lod_group', None)

        @lod_group.setter
        def lod_group(self, v):
            self._dirty = True
            self._m_lod_group = v

        def _write_lod_group(self):
            self._should_write_lod_group = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_lod_group._write__seq(self._io)
            self._io.seek(_pos)


    class Matrix4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Matrix4x4, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.row_1 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_1._read()
            self.row_2 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_2._read()
            self.row_3 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_3._read()
            self.row_4 = ReengineMesh.Vec4(self._io, self, self._root)
            self.row_4._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.row_1._fetch_instances()
            self.row_2._fetch_instances()
            self.row_3._fetch_instances()
            self.row_4._fetch_instances()


        def _write__seq(self, io=None):
            super(ReengineMesh.Matrix4x4, self)._write__seq(io)
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


    class Mesh(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Mesh, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.material_index = self._io.read_u1()
            self.is_quad = self._io.read_u1()
            self.vertex_buffer_index = self._io.read_u1()
            self.padding = self._io.read_u1()
            self.num_indices = self._io.read_u4le()
            self.pos_index_buffer = self._io.read_u4le()
            self.pos_vertex_buffer = self._io.read_u4le()
            if self._root.version != 386270720:
                pass
                self.unk_01 = self._io.read_u8le()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.version != 386270720:
                pass



        def _write__seq(self, io=None):
            super(ReengineMesh.Mesh, self)._write__seq(io)
            self._io.write_u1(self.material_index)
            self._io.write_u1(self.is_quad)
            self._io.write_u1(self.vertex_buffer_index)
            self._io.write_u1(self.padding)
            self._io.write_u4le(self.num_indices)
            self._io.write_u4le(self.pos_index_buffer)
            self._io.write_u4le(self.pos_vertex_buffer)
            if self._root.version != 386270720:
                pass
                self._io.write_u8le(self.unk_01)



        def _check(self):
            if self._root.version != 386270720:
                pass

            self._dirty = False


    class MeshGroup(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.MeshGroup, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.type = self._io.read_u1()
            self.num_meshes = self._io.read_u1()
            self.unk_01 = self._io.read_u2le()
            self.unk_02 = self._io.read_u4le()
            self.num_vertices = self._io.read_u4le()
            self.num_indices = self._io.read_u4le()
            self.meshes = []
            for i in range(self.num_meshes):
                _t_meshes = ReengineMesh.Mesh(self._io, self, self._root)
                try:
                    _t_meshes._read()
                finally:
                    self.meshes.append(_t_meshes)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.meshes)):
                pass
                self.meshes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMesh.MeshGroup, self)._write__seq(io)
            self._io.write_u1(self.type)
            self._io.write_u1(self.num_meshes)
            self._io.write_u2le(self.unk_01)
            self._io.write_u4le(self.unk_02)
            self._io.write_u4le(self.num_vertices)
            self._io.write_u4le(self.num_indices)
            for i in range(len(self.meshes)):
                pass
                self.meshes[i]._write__seq(self._io)



        def _check(self):
            if len(self.meshes) != self.num_meshes:
                raise kaitaistruct.ConsistencyError(u"meshes", self.num_meshes, len(self.meshes))
            for i in range(len(self.meshes)):
                pass
                if self.meshes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"meshes", self._root, self.meshes[i]._root)
                if self.meshes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"meshes", self, self.meshes[i]._parent)

            self._dirty = False


    class MeshGroupOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.MeshGroupOffset, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_mesh_group = False
            self.mesh_group__enabled = True

        def _read(self):
            self.offset = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.mesh_group
            if hasattr(self, '_m_mesh_group'):
                pass
                self._m_mesh_group._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMesh.MeshGroupOffset, self)._write__seq(io)
            self._should_write_mesh_group = self.mesh_group__enabled
            self._io.write_u8le(self.offset)


        def _check(self):
            if self.mesh_group__enabled:
                pass
                if self._m_mesh_group._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"mesh_group", self._root, self._m_mesh_group._root)
                if self._m_mesh_group._parent != self:
                    raise kaitaistruct.ConsistencyError(u"mesh_group", self, self._m_mesh_group._parent)

            self._dirty = False

        @property
        def mesh_group(self):
            if self._should_write_mesh_group:
                self._write_mesh_group()
            if hasattr(self, '_m_mesh_group'):
                return self._m_mesh_group

            if not self.mesh_group__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_mesh_group = ReengineMesh.MeshGroup(self._io, self, self._root)
            self._m_mesh_group._read()
            self._io.seek(_pos)
            return getattr(self, '_m_mesh_group', None)

        @mesh_group.setter
        def mesh_group(self, v):
            self._dirty = True
            self._m_mesh_group = v

        def _write_mesh_group(self):
            self._should_write_mesh_group = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_mesh_group._write__seq(self._io)
            self._io.seek(_pos)


    class ModelInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.ModelInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_lod_group_offsets = False
            self.lod_group_offsets__enabled = True

        def _read(self):
            self.num_lod_groups = self._io.read_u1()
            self.num_materials = self._io.read_u1()
            self.num_uv_layers = self._io.read_u1()
            self.num_skin_weights = self._io.read_u1()
            self.num_meshes = self._io.read_u2le()
            self.has_32bit_index_buffer = self._io.read_u1()
            self.shared_lod_bits = self._io.read_u1()
            if self._root.version == 386270720:
                pass
                self.reserved_01 = self._io.read_u8le()

            self.box = []
            for i in range(12):
                self.box.append(self._io.read_f4le())

            self.offset_lod_group_list = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.version == 386270720:
                pass

            for i in range(len(self.box)):
                pass

            _ = self.lod_group_offsets
            if hasattr(self, '_m_lod_group_offsets'):
                pass
                for i in range(len(self._m_lod_group_offsets)):
                    pass
                    self._m_lod_group_offsets[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(ReengineMesh.ModelInfo, self)._write__seq(io)
            self._should_write_lod_group_offsets = self.lod_group_offsets__enabled
            self._io.write_u1(self.num_lod_groups)
            self._io.write_u1(self.num_materials)
            self._io.write_u1(self.num_uv_layers)
            self._io.write_u1(self.num_skin_weights)
            self._io.write_u2le(self.num_meshes)
            self._io.write_u1(self.has_32bit_index_buffer)
            self._io.write_u1(self.shared_lod_bits)
            if self._root.version == 386270720:
                pass
                self._io.write_u8le(self.reserved_01)

            for i in range(len(self.box)):
                pass
                self._io.write_f4le(self.box[i])

            self._io.write_u8le(self.offset_lod_group_list)


        def _check(self):
            if self._root.version == 386270720:
                pass

            if len(self.box) != 12:
                raise kaitaistruct.ConsistencyError(u"box", 12, len(self.box))
            for i in range(len(self.box)):
                pass

            if self.lod_group_offsets__enabled:
                pass
                if len(self._m_lod_group_offsets) != self.num_lod_groups:
                    raise kaitaistruct.ConsistencyError(u"lod_group_offsets", self.num_lod_groups, len(self._m_lod_group_offsets))
                for i in range(len(self._m_lod_group_offsets)):
                    pass
                    if self._m_lod_group_offsets[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"lod_group_offsets", self._root, self._m_lod_group_offsets[i]._root)
                    if self._m_lod_group_offsets[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"lod_group_offsets", self, self._m_lod_group_offsets[i]._parent)


            self._dirty = False

        @property
        def lod_group_offsets(self):
            if self._should_write_lod_group_offsets:
                self._write_lod_group_offsets()
            if hasattr(self, '_m_lod_group_offsets'):
                return self._m_lod_group_offsets

            if not self.lod_group_offsets__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_lod_group_list)
            self._m_lod_group_offsets = []
            for i in range(self.num_lod_groups):
                _t__m_lod_group_offsets = ReengineMesh.LodGroupOffset(self._io, self, self._root)
                try:
                    _t__m_lod_group_offsets._read()
                finally:
                    self._m_lod_group_offsets.append(_t__m_lod_group_offsets)

            self._io.seek(_pos)
            return getattr(self, '_m_lod_group_offsets', None)

        @lod_group_offsets.setter
        def lod_group_offsets(self, v):
            self._dirty = True
            self._m_lod_group_offsets = v

        def _write_lod_group_offsets(self):
            self._should_write_lod_group_offsets = False
            _pos = self._io.pos()
            self._io.seek(self.offset_lod_group_list)
            for i in range(len(self._m_lod_group_offsets)):
                pass
                self._m_lod_group_offsets[i]._write__seq(self._io)

            self._io.seek(_pos)


    class NameOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.NameOffset, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_value = False
            self.value__enabled = True

        def _read(self):
            self.offset = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.value
            if hasattr(self, '_m_value'):
                pass



        def _write__seq(self, io=None):
            super(ReengineMesh.NameOffset, self)._write__seq(io)
            self._should_write_value = self.value__enabled
            self._io.write_u8le(self.offset)


        def _check(self):
            if self.value__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_value).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"value", -1, KaitaiStream.byte_array_index_of((self._m_value).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def value(self):
            if self._should_write_value:
                self._write_value()
            if hasattr(self, '_m_value'):
                return self._m_value

            if not self.value__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_value = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_value', None)

        @value.setter
        def value(self, v):
            self._dirty = True
            self._m_value = v

        def _write_value(self):
            self._should_write_value = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._io.write_bytes((self._m_value).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class PrimitiveAccessor(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.PrimitiveAccessor, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.primitive_type = KaitaiStream.resolve_enum(ReengineMesh.PrimitiveType, self._io.read_u2le())
            self.size = self._io.read_u2le()
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMesh.PrimitiveAccessor, self)._write__seq(io)
            self._io.write_u2le(int(self.primitive_type))
            self._io.write_u2le(self.size)
            self._io.write_u4le(self.offset)


        def _check(self):
            self._dirty = False


    class ShadowHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.ShadowHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.lod_group_count = self._io.read_u1()
            self.material_count = self._io.read_u1()
            self.uv_count = self._io.read_u1()
            self.skin_weight_count = self._io.read_u1()
            self.total_mesh_count = self._io.read_u4le()
            if self._root.version == 386270720:
                pass
                self.null_padding = self._io.read_u8le()

            self.offset_offset = self._io.read_u8le()
            self.reserved_0 = []
            for i in range(6):
                self.reserved_0.append(self._io.read_u8le())

            self.lod_group_offsets = []
            for i in range(self.lod_group_count):
                self.lod_group_offsets.append(self._io.read_u8le())

            self.padding = self._io.read_bytes((16 - self._io.pos() % 16) % 16)
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.version == 386270720:
                pass

            for i in range(len(self.reserved_0)):
                pass

            for i in range(len(self.lod_group_offsets)):
                pass



        def _write__seq(self, io=None):
            super(ReengineMesh.ShadowHeader, self)._write__seq(io)
            self._io.write_u1(self.lod_group_count)
            self._io.write_u1(self.material_count)
            self._io.write_u1(self.uv_count)
            self._io.write_u1(self.skin_weight_count)
            self._io.write_u4le(self.total_mesh_count)
            if self._root.version == 386270720:
                pass
                self._io.write_u8le(self.null_padding)

            self._io.write_u8le(self.offset_offset)
            for i in range(len(self.reserved_0)):
                pass
                self._io.write_u8le(self.reserved_0[i])

            for i in range(len(self.lod_group_offsets)):
                pass
                self._io.write_u8le(self.lod_group_offsets[i])

            if len(self.padding) != (16 - self._io.pos() % 16) % 16:
                raise kaitaistruct.ConsistencyError(u"padding", (16 - self._io.pos() % 16) % 16, len(self.padding))
            self._io.write_bytes(self.padding)


        def _check(self):
            if self._root.version == 386270720:
                pass

            if len(self.reserved_0) != 6:
                raise kaitaistruct.ConsistencyError(u"reserved_0", 6, len(self.reserved_0))
            for i in range(len(self.reserved_0)):
                pass

            if len(self.lod_group_offsets) != self.lod_group_count:
                raise kaitaistruct.ConsistencyError(u"lod_group_offsets", self.lod_group_count, len(self.lod_group_offsets))
            for i in range(len(self.lod_group_offsets)):
                pass

            self._dirty = False


    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Vec4, self).__init__(_io)
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
            super(ReengineMesh.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            self._dirty = False


    @property
    def blend_shape_name_remap(self):
        if self._should_write_blend_shape_name_remap:
            self._write_blend_shape_name_remap()
        if hasattr(self, '_m_blend_shape_name_remap'):
            return self._m_blend_shape_name_remap

        if not self.blend_shape_name_remap__enabled:
            return None

        if self.header.offset_blend_shape_name_remap != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_blend_shape_name_remap)
            self._m_blend_shape_name_remap = []
            for i in range((self.header.num_named_nodes - (self.model_info.num_materials if self.header.offset_data != 0 else 0)) - (self.bones_header.num_bones if self.header.offset_bones != 0 else 0)):
                self._m_blend_shape_name_remap.append(self._io.read_u2le())

            self._io.seek(_pos)

        return getattr(self, '_m_blend_shape_name_remap', None)

    @blend_shape_name_remap.setter
    def blend_shape_name_remap(self, v):
        self._dirty = True
        self._m_blend_shape_name_remap = v

    def _write_blend_shape_name_remap(self):
        self._should_write_blend_shape_name_remap = False
        if self.header.offset_blend_shape_name_remap != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_blend_shape_name_remap)
            if len(self._m_blend_shape_name_remap) != (self.header.num_named_nodes - (self.model_info.num_materials if self.header.offset_data != 0 else 0)) - (self.bones_header.num_bones if self.header.offset_bones != 0 else 0):
                raise kaitaistruct.ConsistencyError(u"blend_shape_name_remap", (self.header.num_named_nodes - (self.model_info.num_materials if self.header.offset_data != 0 else 0)) - (self.bones_header.num_bones if self.header.offset_bones != 0 else 0), len(self._m_blend_shape_name_remap))
            for i in range(len(self._m_blend_shape_name_remap)):
                pass
                self._io.write_u2le(self._m_blend_shape_name_remap[i])

            self._io.seek(_pos)


    @property
    def bone_aabb_group(self):
        if self._should_write_bone_aabb_group:
            self._write_bone_aabb_group()
        if hasattr(self, '_m_bone_aabb_group'):
            return self._m_bone_aabb_group

        if not self.bone_aabb_group__enabled:
            return None

        if self.header.offset_bone_aabb != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bone_aabb)
            self._m_bone_aabb_group = ReengineMesh.BoneAabbGroup(self._io, self, self._root)
            self._m_bone_aabb_group._read()
            self._io.seek(_pos)

        return getattr(self, '_m_bone_aabb_group', None)

    @bone_aabb_group.setter
    def bone_aabb_group(self, v):
        self._dirty = True
        self._m_bone_aabb_group = v

    def _write_bone_aabb_group(self):
        self._should_write_bone_aabb_group = False
        if self.header.offset_bone_aabb != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bone_aabb)
            self._m_bone_aabb_group._write__seq(self._io)
            self._io.seek(_pos)


    @property
    def bone_name_remap(self):
        if self._should_write_bone_name_remap:
            self._write_bone_name_remap()
        if hasattr(self, '_m_bone_name_remap'):
            return self._m_bone_name_remap

        if not self.bone_name_remap__enabled:
            return None

        if  ((self.header.offset_bone_name_remap != 0) and (self.header.offset_bones != 0)) :
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bone_name_remap)
            self._m_bone_name_remap = []
            for i in range(self.bones_header.num_bones):
                self._m_bone_name_remap.append(self._io.read_u2le())

            self._io.seek(_pos)

        return getattr(self, '_m_bone_name_remap', None)

    @bone_name_remap.setter
    def bone_name_remap(self, v):
        self._dirty = True
        self._m_bone_name_remap = v

    def _write_bone_name_remap(self):
        self._should_write_bone_name_remap = False
        if  ((self.header.offset_bone_name_remap != 0) and (self.header.offset_bones != 0)) :
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bone_name_remap)
            if len(self._m_bone_name_remap) != self.bones_header.num_bones:
                raise kaitaistruct.ConsistencyError(u"bone_name_remap", self.bones_header.num_bones, len(self._m_bone_name_remap))
            for i in range(len(self._m_bone_name_remap)):
                pass
                self._io.write_u2le(self._m_bone_name_remap[i])

            self._io.seek(_pos)


    @property
    def bones_header(self):
        if self._should_write_bones_header:
            self._write_bones_header()
        if hasattr(self, '_m_bones_header'):
            return self._m_bones_header

        if not self.bones_header__enabled:
            return None

        if self.header.offset_bones != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones)
            self._m_bones_header = ReengineMesh.BoneHeader(self._io, self, self._root)
            self._m_bones_header._read()
            self._io.seek(_pos)

        return getattr(self, '_m_bones_header', None)

    @bones_header.setter
    def bones_header(self, v):
        self._dirty = True
        self._m_bones_header = v

    def _write_bones_header(self):
        self._should_write_bones_header = False
        if self.header.offset_bones != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bones)
            self._m_bones_header._write__seq(self._io)
            self._io.seek(_pos)


    @property
    def buffers_data(self):
        if self._should_write_buffers_data:
            self._write_buffers_data()
        if hasattr(self, '_m_buffers_data'):
            return self._m_buffers_data

        if not self.buffers_data__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_buffers_header)
        self._m_buffers_data = ReengineMesh.BuffersHeader(self._io, self, self._root)
        self._m_buffers_data._read()
        self._io.seek(_pos)
        return getattr(self, '_m_buffers_data', None)

    @buffers_data.setter
    def buffers_data(self, v):
        self._dirty = True
        self._m_buffers_data = v

    def _write_buffers_data(self):
        self._should_write_buffers_data = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_buffers_header)
        self._m_buffers_data._write__seq(self._io)
        self._io.seek(_pos)

    @property
    def material_name_remap(self):
        if self._should_write_material_name_remap:
            self._write_material_name_remap()
        if hasattr(self, '_m_material_name_remap'):
            return self._m_material_name_remap

        if not self.material_name_remap__enabled:
            return None

        if  ((self.header.offset_material_name_remap != 0) and (self.header.offset_data != 0)) :
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_material_name_remap)
            self._m_material_name_remap = []
            for i in range(self.model_info.num_materials):
                self._m_material_name_remap.append(self._io.read_u2le())

            self._io.seek(_pos)

        return getattr(self, '_m_material_name_remap', None)

    @material_name_remap.setter
    def material_name_remap(self, v):
        self._dirty = True
        self._m_material_name_remap = v

    def _write_material_name_remap(self):
        self._should_write_material_name_remap = False
        if  ((self.header.offset_material_name_remap != 0) and (self.header.offset_data != 0)) :
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_material_name_remap)
            if len(self._m_material_name_remap) != self.model_info.num_materials:
                raise kaitaistruct.ConsistencyError(u"material_name_remap", self.model_info.num_materials, len(self._m_material_name_remap))
            for i in range(len(self._m_material_name_remap)):
                pass
                self._io.write_u2le(self._m_material_name_remap[i])

            self._io.seek(_pos)


    @property
    def model_info(self):
        if self._should_write_model_info:
            self._write_model_info()
        if hasattr(self, '_m_model_info'):
            return self._m_model_info

        if not self.model_info__enabled:
            return None

        if self.header.offset_data != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_data)
            self._m_model_info = ReengineMesh.ModelInfo(self._io, self, self._root)
            self._m_model_info._read()
            self._io.seek(_pos)

        return getattr(self, '_m_model_info', None)

    @model_info.setter
    def model_info(self, v):
        self._dirty = True
        self._m_model_info = v

    def _write_model_info(self):
        self._should_write_model_info = False
        if self.header.offset_data != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_data)
            self._m_model_info._write__seq(self._io)
            self._io.seek(_pos)


    @property
    def named_nodes(self):
        if self._should_write_named_nodes:
            self._write_named_nodes()
        if hasattr(self, '_m_named_nodes'):
            return self._m_named_nodes

        if not self.named_nodes__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_names)
        self._m_named_nodes = []
        for i in range(self.header.num_named_nodes):
            _t__m_named_nodes = ReengineMesh.NameOffset(self._io, self, self._root)
            try:
                _t__m_named_nodes._read()
            finally:
                self._m_named_nodes.append(_t__m_named_nodes)

        self._io.seek(_pos)
        return getattr(self, '_m_named_nodes', None)

    @named_nodes.setter
    def named_nodes(self, v):
        self._dirty = True
        self._m_named_nodes = v

    def _write_named_nodes(self):
        self._should_write_named_nodes = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_names)
        for i in range(len(self._m_named_nodes)):
            pass
            self._m_named_nodes[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def occlusion_mesh_group(self):
        if self._should_write_occlusion_mesh_group:
            self._write_occlusion_mesh_group()
        if hasattr(self, '_m_occlusion_mesh_group'):
            return self._m_occlusion_mesh_group

        if not self.occlusion_mesh_group__enabled:
            return None

        if self.header.offset_occlusion_mesh_group != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_occlusion_mesh_group)
            self._m_occlusion_mesh_group = ReengineMesh.LodGroup(self._io, self, self._root)
            self._m_occlusion_mesh_group._read()
            self._io.seek(_pos)

        return getattr(self, '_m_occlusion_mesh_group', None)

    @occlusion_mesh_group.setter
    def occlusion_mesh_group(self, v):
        self._dirty = True
        self._m_occlusion_mesh_group = v

    def _write_occlusion_mesh_group(self):
        self._should_write_occlusion_mesh_group = False
        if self.header.offset_occlusion_mesh_group != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_occlusion_mesh_group)
            self._m_occlusion_mesh_group._write__seq(self._io)
            self._io.seek(_pos)


    @property
    def shadow_header(self):
        if self._should_write_shadow_header:
            self._write_shadow_header()
        if hasattr(self, '_m_shadow_header'):
            return self._m_shadow_header

        if not self.shadow_header__enabled:
            return None

        if self.header.offset_shadow_mesh_group != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_shadow_mesh_group)
            self._m_shadow_header = ReengineMesh.ShadowHeader(self._io, self, self._root)
            self._m_shadow_header._read()
            self._io.seek(_pos)

        return getattr(self, '_m_shadow_header', None)

    @shadow_header.setter
    def shadow_header(self, v):
        self._dirty = True
        self._m_shadow_header = v

    def _write_shadow_header(self):
        self._should_write_shadow_header = False
        if self.header.offset_shadow_mesh_group != 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_shadow_mesh_group)
            self._m_shadow_header._write__seq(self._io)
            self._io.seek(_pos)



