# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class ReengineMesh(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(ReengineMesh, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_bones_header = False
        self.bones_header__enabled = True
        self._should_write_buffers_data = False
        self.buffers_data__enabled = True
        self._should_write_id_to_names_remap = False
        self.id_to_names_remap__enabled = True
        self._should_write_model_info = False
        self.model_info__enabled = True
        self._should_write_named_nodes = False
        self.named_nodes__enabled = True

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
        _ = self.bones_header
        if hasattr(self, '_m_bones_header'):
            pass
            self._m_bones_header._fetch_instances()

        _ = self.buffers_data
        if hasattr(self, '_m_buffers_data'):
            pass
            self._m_buffers_data._fetch_instances()

        _ = self.id_to_names_remap
        if hasattr(self, '_m_id_to_names_remap'):
            pass
            for i in range(len(self._m_id_to_names_remap)):
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




    def _write__seq(self, io=None):
        super(ReengineMesh, self)._write__seq(io)
        self._should_write_bones_header = self.bones_header__enabled
        self._should_write_buffers_data = self.buffers_data__enabled
        self._should_write_id_to_names_remap = self.id_to_names_remap__enabled
        self._should_write_model_info = self.model_info__enabled
        self._should_write_named_nodes = self.named_nodes__enabled
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

        if self.id_to_names_remap__enabled:
            pass
            if  ((self.header.offset_test_remap != 0) and (self.header.offset_data != 0)) :
                pass
                for i in range(len(self._m_id_to_names_remap)):
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


    class BoneHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.BoneHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_bones = False
            self.bones__enabled = True
            self._should_write_inverse_bind_matrices = False
            self.inverse_bind_matrices__enabled = True

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




        def _write__seq(self, io=None):
            super(ReengineMesh.BoneHeader, self)._write__seq(io)
            self._should_write_bones = self.bones__enabled
            self._should_write_inverse_bind_matrices = self.inverse_bind_matrices__enabled
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
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMesh.Header, self)._write__seq(io)
            self._io.write_u2le(self.unk1)
            self._io.write_u2le(self.num_named_nodes)
            self._io.write_u4le(self.reserved_02)
            self._io.write_u8le(self.offset_data)
            self._io.write_u8le(self.offset_unk_1)
            self._io.write_u8le(self.offset_unk_2)
            self._io.write_u8le(self.offset_bones)
            self._io.write_u8le(self.offset_unk_3)
            self._io.write_u8le(self.offset_unk_4)
            self._io.write_u8le(self.offset_unk_5)
            self._io.write_u8le(self.offset_buffers_header)
            self._io.write_u8le(self.offset_unk_6)
            self._io.write_u8le(self.offset_test_remap)
            self._io.write_u8le(self.offset_unk_8)
            self._io.write_u8le(self.offset_unk_9)
            self._io.write_u8le(self.offset_names)


        def _check(self):
            self._dirty = False


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
            self._should_write_normals = False
            self.normals__enabled = True

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

            _ = self.normals
            if hasattr(self, '_m_normals'):
                pass
                for i in range(len(self._m_normals)):
                    pass




        def _write__seq(self, io=None):
            super(ReengineMesh.Mesh, self)._write__seq(io)
            self._should_write_normals = self.normals__enabled
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

            if self.normals__enabled:
                pass
                if len(self._m_normals) != 100:
                    raise kaitaistruct.ConsistencyError(u"normals", 100, len(self._m_normals))
                for i in range(len(self._m_normals)):
                    pass


            self._dirty = False

        @property
        def normals(self):
            if self._should_write_normals:
                self._write_normals()
            if hasattr(self, '_m_normals'):
                return self._m_normals

            if not self.normals__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek((self._root.buffers_data.offset_vertex_buffer + self._root.buffers_data.primitive_accessors[1].offset) + self._root.buffers_data.primitive_accessors[1].size * self.pos_vertex_buffer)
            self._m_normals = []
            for i in range(100):
                self._m_normals.append(self._io.read_s1())

            self._io.seek(_pos)
            return getattr(self, '_m_normals', None)

        @normals.setter
        def normals(self, v):
            self._dirty = True
            self._m_normals = v

        def _write_normals(self):
            self._should_write_normals = False
            _pos = self._io.pos()
            self._io.seek((self._root.buffers_data.offset_vertex_buffer + self._root.buffers_data.primitive_accessors[1].offset) + self._root.buffers_data.primitive_accessors[1].size * self.pos_vertex_buffer)
            for i in range(len(self._m_normals)):
                pass
                self._io.write_s1(self._m_normals[i])

            self._io.seek(_pos)


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


    class MeshGroupTest(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.MeshGroupTest, self).__init__(_io)
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
            super(ReengineMesh.MeshGroupTest, self)._write__seq(io)
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


    class Model(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.Model, self).__init__(_io)
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
                _t_mesh_groups = ReengineMesh.MeshGroupTest(self._io, self, self._root)
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
            super(ReengineMesh.Model, self)._write__seq(io)
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


    class ModelInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.ModelInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_model_offsets = False
            self.model_offsets__enabled = True

        def _read(self):
            self.len_offsets_models = self._io.read_u1()
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

            self.offset_lod_info = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self._root.version == 386270720:
                pass

            for i in range(len(self.box)):
                pass

            _ = self.model_offsets
            if hasattr(self, '_m_model_offsets'):
                pass
                for i in range(len(self._m_model_offsets)):
                    pass
                    self._m_model_offsets[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(ReengineMesh.ModelInfo, self)._write__seq(io)
            self._should_write_model_offsets = self.model_offsets__enabled
            self._io.write_u1(self.len_offsets_models)
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

            self._io.write_u8le(self.offset_lod_info)


        def _check(self):
            if self._root.version == 386270720:
                pass

            if len(self.box) != 12:
                raise kaitaistruct.ConsistencyError(u"box", 12, len(self.box))
            for i in range(len(self.box)):
                pass

            if self.model_offsets__enabled:
                pass
                if len(self._m_model_offsets) != self.len_offsets_models:
                    raise kaitaistruct.ConsistencyError(u"model_offsets", self.len_offsets_models, len(self._m_model_offsets))
                for i in range(len(self._m_model_offsets)):
                    pass
                    if self._m_model_offsets[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"model_offsets", self._root, self._m_model_offsets[i]._root)
                    if self._m_model_offsets[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"model_offsets", self, self._m_model_offsets[i]._parent)


            self._dirty = False

        @property
        def model_offsets(self):
            if self._should_write_model_offsets:
                self._write_model_offsets()
            if hasattr(self, '_m_model_offsets'):
                return self._m_model_offsets

            if not self.model_offsets__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_lod_info)
            self._m_model_offsets = []
            for i in range(self.len_offsets_models):
                _t__m_model_offsets = ReengineMesh.ModelOffset(self._io, self, self._root)
                try:
                    _t__m_model_offsets._read()
                finally:
                    self._m_model_offsets.append(_t__m_model_offsets)

            self._io.seek(_pos)
            return getattr(self, '_m_model_offsets', None)

        @model_offsets.setter
        def model_offsets(self, v):
            self._dirty = True
            self._m_model_offsets = v

        def _write_model_offsets(self):
            self._should_write_model_offsets = False
            _pos = self._io.pos()
            self._io.seek(self.offset_lod_info)
            for i in range(len(self._m_model_offsets)):
                pass
                self._m_model_offsets[i]._write__seq(self._io)

            self._io.seek(_pos)


    class ModelOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.ModelOffset, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_model = False
            self.model__enabled = True

        def _read(self):
            self.offset = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.model
            if hasattr(self, '_m_model'):
                pass
                self._m_model._fetch_instances()



        def _write__seq(self, io=None):
            super(ReengineMesh.ModelOffset, self)._write__seq(io)
            self._should_write_model = self.model__enabled
            self._io.write_u8le(self.offset)


        def _check(self):
            if self.model__enabled:
                pass
                if self._m_model._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"model", self._root, self._m_model._root)
                if self._m_model._parent != self:
                    raise kaitaistruct.ConsistencyError(u"model", self, self._m_model._parent)

            self._dirty = False

        @property
        def model(self):
            if self._should_write_model:
                self._write_model()
            if hasattr(self, '_m_model'):
                return self._m_model

            if not self.model__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_model = ReengineMesh.Model(self._io, self, self._root)
            self._m_model._read()
            self._io.seek(_pos)
            return getattr(self, '_m_model', None)

        @model.setter
        def model(self, v):
            self._dirty = True
            self._m_model = v

        def _write_model(self):
            self._should_write_model = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_model._write__seq(self._io)
            self._io.seek(_pos)


    class NameOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.NameOffset, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.offset = self._io.read_u8le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(ReengineMesh.NameOffset, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u8le(self.offset)


        def _check(self):
            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._io.write_bytes((self._m_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.seek(_pos)


    class PrimitiveAccessor(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.PrimitiveAccessor, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.primitive_type = self._io.read_u2le()
            self.size = self._io.read_u2le()
            self.offset = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(ReengineMesh.PrimitiveAccessor, self)._write__seq(io)
            self._io.write_u2le(self.primitive_type)
            self._io.write_u2le(self.size)
            self._io.write_u4le(self.offset)


        def _check(self):
            self._dirty = False


    class TestName(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(ReengineMesh.TestName, self).__init__(_io)
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
            super(ReengineMesh.TestName, self)._write__seq(io)
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
    def id_to_names_remap(self):
        if self._should_write_id_to_names_remap:
            self._write_id_to_names_remap()
        if hasattr(self, '_m_id_to_names_remap'):
            return self._m_id_to_names_remap

        if not self.id_to_names_remap__enabled:
            return None

        if  ((self.header.offset_test_remap != 0) and (self.header.offset_data != 0)) :
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_test_remap)
            self._m_id_to_names_remap = []
            for i in range(self.model_info.num_materials):
                self._m_id_to_names_remap.append(self._io.read_u2le())

            self._io.seek(_pos)

        return getattr(self, '_m_id_to_names_remap', None)

    @id_to_names_remap.setter
    def id_to_names_remap(self, v):
        self._dirty = True
        self._m_id_to_names_remap = v

    def _write_id_to_names_remap(self):
        self._should_write_id_to_names_remap = False
        if  ((self.header.offset_test_remap != 0) and (self.header.offset_data != 0)) :
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_test_remap)
            if len(self._m_id_to_names_remap) != self.model_info.num_materials:
                raise kaitaistruct.ConsistencyError(u"id_to_names_remap", self.model_info.num_materials, len(self._m_id_to_names_remap))
            for i in range(len(self._m_id_to_names_remap)):
                pass
                self._io.write_u2le(self._m_id_to_names_remap[i])

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
            _t__m_named_nodes = ReengineMesh.TestName(self._io, self, self._root)
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


