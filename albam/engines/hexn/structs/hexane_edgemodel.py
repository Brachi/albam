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
            self._should_write_bones_data = False
            self.bones_data__enabled = True
            self._should_write_marker_record_byte0 = False
            self.marker_record_byte0__enabled = True
            self._should_write_pre_bones_data = False
            self.pre_bones_data__enabled = True
            self._should_write_pre_trailing_footer = False
            self.pre_trailing_footer__enabled = True
            self._should_write_trailing_data = False
            self.trailing_data__enabled = True

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

            _ = self.bones_data
            if hasattr(self, '_m_bones_data'):
                pass

            _ = self.marker_record_byte0
            if hasattr(self, '_m_marker_record_byte0'):
                pass

            _ = self.pre_bones_data
            if hasattr(self, '_m_pre_bones_data'):
                pass

            _ = self.pre_trailing_footer
            if hasattr(self, '_m_pre_trailing_footer'):
                pass

            _ = self.trailing_data
            if hasattr(self, '_m_trailing_data'):
                pass



        def _write__seq(self, io=None):
            super(HexaneEdgemodel.EdgeHeader, self)._write__seq(io)
            self._should_write_bones_data = self.bones_data__enabled
            self._should_write_marker_record_byte0 = self.marker_record_byte0__enabled
            self._should_write_pre_bones_data = self.pre_bones_data__enabled
            self._should_write_pre_trailing_footer = self.pre_trailing_footer__enabled
            self._should_write_trailing_data = self.trailing_data__enabled
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

            if self.bones_data__enabled:
                pass
                if  ((self.num_bones > 0) and (self.ofs_unk_02 > self.ofs_bones)) :
                    pass
                    if len(self._m_bones_data) != self.ofs_unk_02 - self.ofs_bones:
                        raise kaitaistruct.ConsistencyError(u"bones_data", self.ofs_unk_02 - self.ofs_bones, len(self._m_bones_data))


            if self.marker_record_byte0__enabled:
                pass

            if self.pre_bones_data__enabled:
                pass

            if self.pre_trailing_footer__enabled:
                pass

            if self.trailing_data__enabled:
                pass
                if self.ofs_unk_02 > 0:
                    pass


            self._dirty = False

        @property
        def bones_data(self):
            if self._should_write_bones_data:
                self._write_bones_data()
            if hasattr(self, '_m_bones_data'):
                return self._m_bones_data

            if not self.bones_data__enabled:
                return None

            if  ((self.num_bones > 0) and (self.ofs_unk_02 > self.ofs_bones)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bones)
                self._m_bones_data = self._io.read_bytes(self.ofs_unk_02 - self.ofs_bones)
                self._io.seek(_pos)

            return getattr(self, '_m_bones_data', None)

        @bones_data.setter
        def bones_data(self, v):
            self._dirty = True
            self._m_bones_data = v

        def _write_bones_data(self):
            self._should_write_bones_data = False
            if  ((self.num_bones > 0) and (self.ofs_unk_02 > self.ofs_bones)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bones)
                self._io.write_bytes(self._m_bones_data)
                self._io.seek(_pos)


        @property
        def last_mesh_align_padding(self):
            if hasattr(self, '_m_last_mesh_align_padding'):
                return self._m_last_mesh_align_padding

            self._m_last_mesh_align_padding = (16 - self.last_mesh_max_end % 16) % 16
            return getattr(self, '_m_last_mesh_align_padding', None)

        def _invalidate_last_mesh_align_padding(self):
            del self._m_last_mesh_align_padding
        @property
        def last_mesh_header(self):
            if hasattr(self, '_m_last_mesh_header'):
                return self._m_last_mesh_header

            self._m_last_mesh_header = self._parent.meshes_header[self.num_meshes - 1]
            return getattr(self, '_m_last_mesh_header', None)

        def _invalidate_last_mesh_header(self):
            del self._m_last_mesh_header
        @property
        def last_mesh_indices_end(self):
            if hasattr(self, '_m_last_mesh_indices_end'):
                return self._m_last_mesh_indices_end

            self._m_last_mesh_indices_end = self.last_mesh_header.mesh.ofs_buffer_indices + self.last_mesh_header.mesh.size_buffer_indices
            return getattr(self, '_m_last_mesh_indices_end', None)

        def _invalidate_last_mesh_indices_end(self):
            del self._m_last_mesh_indices_end
        @property
        def last_mesh_max_end(self):
            if hasattr(self, '_m_last_mesh_max_end'):
                return self._m_last_mesh_max_end

            self._m_last_mesh_max_end = ((self.last_mesh_indices_end if self.last_mesh_indices_end > self.last_mesh_weights_end else self.last_mesh_weights_end) if self.last_mesh_indices_end > self.last_mesh_vertices_end else (self.last_mesh_vertices_end if self.last_mesh_vertices_end > self.last_mesh_weights_end else self.last_mesh_weights_end))
            return getattr(self, '_m_last_mesh_max_end', None)

        def _invalidate_last_mesh_max_end(self):
            del self._m_last_mesh_max_end
        @property
        def last_mesh_vertices_end(self):
            if hasattr(self, '_m_last_mesh_vertices_end'):
                return self._m_last_mesh_vertices_end

            self._m_last_mesh_vertices_end = self.last_mesh_header.mesh.ofs_buffer_vertices + self.last_mesh_header.mesh.size_buffer_vertices
            return getattr(self, '_m_last_mesh_vertices_end', None)

        def _invalidate_last_mesh_vertices_end(self):
            del self._m_last_mesh_vertices_end
        @property
        def last_mesh_weights_end(self):
            if hasattr(self, '_m_last_mesh_weights_end'):
                return self._m_last_mesh_weights_end

            self._m_last_mesh_weights_end = self.last_mesh_header.mesh.ofs_buffer_weights + self.last_mesh_header.mesh.size_buffer_weights
            return getattr(self, '_m_last_mesh_weights_end', None)

        def _invalidate_last_mesh_weights_end(self):
            del self._m_last_mesh_weights_end
        @property
        def marker_record_byte0(self):
            if self._should_write_marker_record_byte0:
                self._write_marker_record_byte0()
            if hasattr(self, '_m_marker_record_byte0'):
                return self._m_marker_record_byte0

            if not self.marker_record_byte0__enabled:
                return None

            if  ((self.num_meshes > 0) and (self.marker_record_pos < self._io.size())) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.marker_record_pos)
                self._m_marker_record_byte0 = self._io.read_u1()
                self._io.seek(_pos)

            return getattr(self, '_m_marker_record_byte0', None)

        @marker_record_byte0.setter
        def marker_record_byte0(self, v):
            self._dirty = True
            self._m_marker_record_byte0 = v

        def _write_marker_record_byte0(self):
            self._should_write_marker_record_byte0 = False
            if  ((self.num_meshes > 0) and (self.marker_record_pos < self._io.size())) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.marker_record_pos)
                self._io.write_u1(self._m_marker_record_byte0)
                self._io.seek(_pos)


        @property
        def marker_record_pos(self):
            if hasattr(self, '_m_marker_record_pos'):
                return self._m_marker_record_pos

            self._m_marker_record_pos = (self.last_mesh_max_end + self.last_mesh_align_padding) + 16
            return getattr(self, '_m_marker_record_pos', None)

        def _invalidate_marker_record_pos(self):
            del self._m_marker_record_pos
        @property
        def marker_record_readable(self):
            if hasattr(self, '_m_marker_record_readable'):
                return self._m_marker_record_readable

            self._m_marker_record_readable =  ((self.num_meshes > 0) and (self.marker_record_pos < self._io.size())) 
            return getattr(self, '_m_marker_record_readable', None)

        def _invalidate_marker_record_readable(self):
            del self._m_marker_record_readable
        @property
        def pre_bones_data(self):
            if self._should_write_pre_bones_data:
                self._write_pre_bones_data()
            if hasattr(self, '_m_pre_bones_data'):
                return self._m_pre_bones_data

            if not self.pre_bones_data__enabled:
                return None

            if  ((self.marker_record_readable) and (self.num_bones > 0) and (self.ofs_bones > self.pre_bones_data_size)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bones - self.pre_bones_data_size)
                self._m_pre_bones_data = self._io.read_bytes(self.pre_bones_data_size)
                self._io.seek(_pos)

            return getattr(self, '_m_pre_bones_data', None)

        @pre_bones_data.setter
        def pre_bones_data(self, v):
            self._dirty = True
            self._m_pre_bones_data = v

        def _write_pre_bones_data(self):
            self._should_write_pre_bones_data = False
            if  ((self.marker_record_readable) and (self.num_bones > 0) and (self.ofs_bones > self.pre_bones_data_size)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_bones - self.pre_bones_data_size)
                if len(self._m_pre_bones_data) != self.pre_bones_data_size:
                    raise kaitaistruct.ConsistencyError(u"pre_bones_data", self.pre_bones_data_size, len(self._m_pre_bones_data))
                self._io.write_bytes(self._m_pre_bones_data)
                self._io.seek(_pos)


        @property
        def pre_bones_data_size(self):
            if hasattr(self, '_m_pre_bones_data_size'):
                return self._m_pre_bones_data_size

            self._m_pre_bones_data_size = (((self.last_mesh_align_padding + 16) + 32) + 16 * (self.marker_record_byte0 // 2) if self.marker_record_readable else 0)
            return getattr(self, '_m_pre_bones_data_size', None)

        def _invalidate_pre_bones_data_size(self):
            del self._m_pre_bones_data_size
        @property
        def pre_trailing_footer(self):
            if self._should_write_pre_trailing_footer:
                self._write_pre_trailing_footer()
            if hasattr(self, '_m_pre_trailing_footer'):
                return self._m_pre_trailing_footer

            if not self.pre_trailing_footer__enabled:
                return None

            if  ((self.marker_record_readable) and (self.num_bones == 0) and (self.ofs_unk_02 > self.pre_trailing_footer_size)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_unk_02 - self.pre_trailing_footer_size)
                self._m_pre_trailing_footer = self._io.read_bytes(self.pre_trailing_footer_size)
                self._io.seek(_pos)

            return getattr(self, '_m_pre_trailing_footer', None)

        @pre_trailing_footer.setter
        def pre_trailing_footer(self, v):
            self._dirty = True
            self._m_pre_trailing_footer = v

        def _write_pre_trailing_footer(self):
            self._should_write_pre_trailing_footer = False
            if  ((self.marker_record_readable) and (self.num_bones == 0) and (self.ofs_unk_02 > self.pre_trailing_footer_size)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_unk_02 - self.pre_trailing_footer_size)
                if len(self._m_pre_trailing_footer) != self.pre_trailing_footer_size:
                    raise kaitaistruct.ConsistencyError(u"pre_trailing_footer", self.pre_trailing_footer_size, len(self._m_pre_trailing_footer))
                self._io.write_bytes(self._m_pre_trailing_footer)
                self._io.seek(_pos)


        @property
        def pre_trailing_footer_size(self):
            if hasattr(self, '_m_pre_trailing_footer_size'):
                return self._m_pre_trailing_footer_size

            self._m_pre_trailing_footer_size = ((((self.last_mesh_align_padding + 16) + 20) + 16 * (self.marker_record_byte0 // 2)) + 4 * (self.num_material_per_mesh - 1) if self.marker_record_readable else 0)
            return getattr(self, '_m_pre_trailing_footer_size', None)

        def _invalidate_pre_trailing_footer_size(self):
            del self._m_pre_trailing_footer_size
        @property
        def trailing_data(self):
            if self._should_write_trailing_data:
                self._write_trailing_data()
            if hasattr(self, '_m_trailing_data'):
                return self._m_trailing_data

            if not self.trailing_data__enabled:
                return None

            if self.ofs_unk_02 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_unk_02)
                self._m_trailing_data = self._io.read_bytes(self._io.size() - self.ofs_unk_02)
                self._io.seek(_pos)

            return getattr(self, '_m_trailing_data', None)

        @trailing_data.setter
        def trailing_data(self, v):
            self._dirty = True
            self._m_trailing_data = v

        def _write_trailing_data(self):
            self._should_write_trailing_data = False
            if self.ofs_unk_02 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_unk_02)
                if len(self._m_trailing_data) != self._io.size() - self.ofs_unk_02:
                    raise kaitaistruct.ConsistencyError(u"trailing_data", self._io.size() - self.ofs_unk_02, len(self._m_trailing_data))
                self._io.write_bytes(self._m_trailing_data)
                self._io.seek(_pos)



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
            if self._parent.ofs_materials > self._parent.ofs_data + 128:
                pass
                self.group_and_flags_data = self._io.read_bytes(self._parent.ofs_materials - (self._parent.ofs_data + 128))

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.reserved_01)):
                pass

            for i in range(len(self.reserved_02)):
                pass

            if self._parent.ofs_materials > self._parent.ofs_data + 128:
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
            if self._parent.ofs_materials > self._parent.ofs_data + 128:
                pass
                self._io.write_bytes(self.group_and_flags_data)



        def _check(self):
            if len(self.reserved_01) != 5:
                raise kaitaistruct.ConsistencyError(u"reserved_01", 5, len(self.reserved_01))
            for i in range(len(self.reserved_01)):
                pass

            if len(self.reserved_02) != 9:
                raise kaitaistruct.ConsistencyError(u"reserved_02", 9, len(self.reserved_02))
            for i in range(len(self.reserved_02)):
                pass

            if self._parent.ofs_materials > self._parent.ofs_data + 128:
                pass
                if len(self.group_and_flags_data) != self._parent.ofs_materials - (self._parent.ofs_data + 128):
                    raise kaitaistruct.ConsistencyError(u"group_and_flags_data", self._parent.ofs_materials - (self._parent.ofs_data + 128), len(self.group_and_flags_data))

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
            self._should_write_pre_mesh_data = False
            self.pre_mesh_data__enabled = True
            self._should_write_unk3_count = False
            self.unk3_count__enabled = True
            self._should_write_unk3_header_gap = False
            self.unk3_header_gap__enabled = True
            self._should_write_unk3_offset_a = False
            self.unk3_offset_a__enabled = True
            self._should_write_unk3_offset_b = False
            self.unk3_offset_b__enabled = True
            self._should_write_unk3_region0 = False
            self.unk3_region0__enabled = True
            self._should_write_unk3_region1 = False
            self.unk3_region1__enabled = True
            self._should_write_unk3_trailing = False
            self.unk3_trailing__enabled = True

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

            _ = self.pre_mesh_data
            if hasattr(self, '_m_pre_mesh_data'):
                pass

            _ = self.unk3_count
            if hasattr(self, '_m_unk3_count'):
                pass

            _ = self.unk3_header_gap
            if hasattr(self, '_m_unk3_header_gap'):
                pass

            _ = self.unk3_offset_a
            if hasattr(self, '_m_unk3_offset_a'):
                pass

            _ = self.unk3_offset_b
            if hasattr(self, '_m_unk3_offset_b'):
                pass

            _ = self.unk3_region0
            if hasattr(self, '_m_unk3_region0'):
                pass

            _ = self.unk3_region1
            if hasattr(self, '_m_unk3_region1'):
                pass

            _ = self.unk3_trailing
            if hasattr(self, '_m_unk3_trailing'):
                pass



        def _write__seq(self, io=None):
            super(HexaneEdgemodel.MeshHeader, self)._write__seq(io)
            self._should_write_materials = self.materials__enabled
            self._should_write_mesh = self.mesh__enabled
            self._should_write_pre_mesh_data = self.pre_mesh_data__enabled
            self._should_write_unk3_count = self.unk3_count__enabled
            self._should_write_unk3_header_gap = self.unk3_header_gap__enabled
            self._should_write_unk3_offset_a = self.unk3_offset_a__enabled
            self._should_write_unk3_offset_b = self.unk3_offset_b__enabled
            self._should_write_unk3_region0 = self.unk3_region0__enabled
            self._should_write_unk3_region1 = self.unk3_region1__enabled
            self._should_write_unk3_trailing = self.unk3_trailing__enabled
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

            if self.pre_mesh_data__enabled:
                pass
                if self.ofs_data >= 48:
                    pass
                    if len(self._m_pre_mesh_data) != 48:
                        raise kaitaistruct.ConsistencyError(u"pre_mesh_data", 48, len(self._m_pre_mesh_data))


            if self.unk3_count__enabled:
                pass
                if self.unk_ofs_3 > 0:
                    pass


            if self.unk3_header_gap__enabled:
                pass

            if self.unk3_offset_a__enabled:
                pass
                if self.unk_ofs_3 > 0:
                    pass


            if self.unk3_offset_b__enabled:
                pass
                if self.unk_ofs_3 > 0:
                    pass


            if self.unk3_region0__enabled:
                pass

            if self.unk3_region1__enabled:
                pass

            if self.unk3_trailing__enabled:
                pass

            self._dirty = False

        @property
        def buf_indices_or_sentinel(self):
            if hasattr(self, '_m_buf_indices_or_sentinel'):
                return self._m_buf_indices_or_sentinel

            self._m_buf_indices_or_sentinel = (self.mesh.ofs_buffer_indices if self.mesh.ofs_buffer_indices > self.materials_end else 2147483647)
            return getattr(self, '_m_buf_indices_or_sentinel', None)

        def _invalidate_buf_indices_or_sentinel(self):
            del self._m_buf_indices_or_sentinel
        @property
        def buf_vertices_or_sentinel(self):
            if hasattr(self, '_m_buf_vertices_or_sentinel'):
                return self._m_buf_vertices_or_sentinel

            self._m_buf_vertices_or_sentinel = (self.mesh.ofs_buffer_vertices if self.mesh.ofs_buffer_vertices > self.materials_end else 2147483647)
            return getattr(self, '_m_buf_vertices_or_sentinel', None)

        def _invalidate_buf_vertices_or_sentinel(self):
            del self._m_buf_vertices_or_sentinel
        @property
        def buf_weights_or_sentinel(self):
            if hasattr(self, '_m_buf_weights_or_sentinel'):
                return self._m_buf_weights_or_sentinel

            self._m_buf_weights_or_sentinel = (self.mesh.ofs_buffer_weights if self.mesh.ofs_buffer_weights > self.materials_end else 2147483647)
            return getattr(self, '_m_buf_weights_or_sentinel', None)

        def _invalidate_buf_weights_or_sentinel(self):
            del self._m_buf_weights_or_sentinel
        @property
        def gap_end(self):
            if hasattr(self, '_m_gap_end'):
                return self._m_gap_end

            self._m_gap_end = ((self.buf_indices_or_sentinel if self.buf_indices_or_sentinel < self.buf_weights_or_sentinel else self.buf_weights_or_sentinel) if self.buf_indices_or_sentinel < self.buf_vertices_or_sentinel else (self.buf_vertices_or_sentinel if self.buf_vertices_or_sentinel < self.buf_weights_or_sentinel else self.buf_weights_or_sentinel))
            return getattr(self, '_m_gap_end', None)

        def _invalidate_gap_end(self):
            del self._m_gap_end
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
        def materials_end(self):
            if hasattr(self, '_m_materials_end'):
                return self._m_materials_end

            self._m_materials_end = self.materials._io.pos()
            return getattr(self, '_m_materials_end', None)

        def _invalidate_materials_end(self):
            del self._m_materials_end
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

        @property
        def pre_mesh_data(self):
            if self._should_write_pre_mesh_data:
                self._write_pre_mesh_data()
            if hasattr(self, '_m_pre_mesh_data'):
                return self._m_pre_mesh_data

            if not self.pre_mesh_data__enabled:
                return None

            if self.ofs_data >= 48:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_data - 48)
                self._m_pre_mesh_data = self._io.read_bytes(48)
                self._io.seek(_pos)

            return getattr(self, '_m_pre_mesh_data', None)

        @pre_mesh_data.setter
        def pre_mesh_data(self, v):
            self._dirty = True
            self._m_pre_mesh_data = v

        def _write_pre_mesh_data(self):
            self._should_write_pre_mesh_data = False
            if self.ofs_data >= 48:
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_data - 48)
                self._io.write_bytes(self._m_pre_mesh_data)
                self._io.seek(_pos)


        @property
        def unk3_count(self):
            if self._should_write_unk3_count:
                self._write_unk3_count()
            if hasattr(self, '_m_unk3_count'):
                return self._m_unk3_count

            if not self.unk3_count__enabled:
                return None

            if self.unk_ofs_3 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3)
                self._m_unk3_count = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_count', None)

        @unk3_count.setter
        def unk3_count(self, v):
            self._dirty = True
            self._m_unk3_count = v

        def _write_unk3_count(self):
            self._should_write_unk3_count = False
            if self.unk_ofs_3 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3)
                self._io.write_u4le(self._m_unk3_count)
                self._io.seek(_pos)


        @property
        def unk3_header_gap(self):
            if self._should_write_unk3_header_gap:
                self._write_unk3_header_gap()
            if hasattr(self, '_m_unk3_header_gap'):
                return self._m_unk3_header_gap

            if not self.unk3_header_gap__enabled:
                return None

            if  ((self.unk_ofs_3 > 0) and (self.unk3_offset_a > self.unk_ofs_3 + 12)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3 + 12)
                self._m_unk3_header_gap = self._io.read_bytes(self.unk3_offset_a - (self.unk_ofs_3 + 12))
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_header_gap', None)

        @unk3_header_gap.setter
        def unk3_header_gap(self, v):
            self._dirty = True
            self._m_unk3_header_gap = v

        def _write_unk3_header_gap(self):
            self._should_write_unk3_header_gap = False
            if  ((self.unk_ofs_3 > 0) and (self.unk3_offset_a > self.unk_ofs_3 + 12)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3 + 12)
                if len(self._m_unk3_header_gap) != self.unk3_offset_a - (self.unk_ofs_3 + 12):
                    raise kaitaistruct.ConsistencyError(u"unk3_header_gap", self.unk3_offset_a - (self.unk_ofs_3 + 12), len(self._m_unk3_header_gap))
                self._io.write_bytes(self._m_unk3_header_gap)
                self._io.seek(_pos)


        @property
        def unk3_offset_a(self):
            if self._should_write_unk3_offset_a:
                self._write_unk3_offset_a()
            if hasattr(self, '_m_unk3_offset_a'):
                return self._m_unk3_offset_a

            if not self.unk3_offset_a__enabled:
                return None

            if self.unk_ofs_3 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3 + 4)
                self._m_unk3_offset_a = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_offset_a', None)

        @unk3_offset_a.setter
        def unk3_offset_a(self, v):
            self._dirty = True
            self._m_unk3_offset_a = v

        def _write_unk3_offset_a(self):
            self._should_write_unk3_offset_a = False
            if self.unk_ofs_3 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3 + 4)
                self._io.write_u4le(self._m_unk3_offset_a)
                self._io.seek(_pos)


        @property
        def unk3_offset_b(self):
            if self._should_write_unk3_offset_b:
                self._write_unk3_offset_b()
            if hasattr(self, '_m_unk3_offset_b'):
                return self._m_unk3_offset_b

            if not self.unk3_offset_b__enabled:
                return None

            if self.unk_ofs_3 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3 + 8)
                self._m_unk3_offset_b = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_offset_b', None)

        @unk3_offset_b.setter
        def unk3_offset_b(self, v):
            self._dirty = True
            self._m_unk3_offset_b = v

        def _write_unk3_offset_b(self):
            self._should_write_unk3_offset_b = False
            if self.unk_ofs_3 > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk_ofs_3 + 8)
                self._io.write_u4le(self._m_unk3_offset_b)
                self._io.seek(_pos)


        @property
        def unk3_region0(self):
            if self._should_write_unk3_region0:
                self._write_unk3_region0()
            if hasattr(self, '_m_unk3_region0'):
                return self._m_unk3_region0

            if not self.unk3_region0__enabled:
                return None

            if  ((self.unk_ofs_3 > 0) and (self.unk3_offset_b > self.unk3_offset_a)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk3_offset_a)
                self._m_unk3_region0 = self._io.read_bytes(self.unk3_offset_b - self.unk3_offset_a)
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_region0', None)

        @unk3_region0.setter
        def unk3_region0(self, v):
            self._dirty = True
            self._m_unk3_region0 = v

        def _write_unk3_region0(self):
            self._should_write_unk3_region0 = False
            if  ((self.unk_ofs_3 > 0) and (self.unk3_offset_b > self.unk3_offset_a)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk3_offset_a)
                if len(self._m_unk3_region0) != self.unk3_offset_b - self.unk3_offset_a:
                    raise kaitaistruct.ConsistencyError(u"unk3_region0", self.unk3_offset_b - self.unk3_offset_a, len(self._m_unk3_region0))
                self._io.write_bytes(self._m_unk3_region0)
                self._io.seek(_pos)


        @property
        def unk3_region1(self):
            if self._should_write_unk3_region1:
                self._write_unk3_region1()
            if hasattr(self, '_m_unk3_region1'):
                return self._m_unk3_region1

            if not self.unk3_region1__enabled:
                return None

            if  ((self.unk_ofs_3 > 0) and (self.unk3_region1_end <= self.gap_end)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk3_offset_b)
                self._m_unk3_region1 = self._io.read_bytes(8 * self.unk3_count)
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_region1', None)

        @unk3_region1.setter
        def unk3_region1(self, v):
            self._dirty = True
            self._m_unk3_region1 = v

        def _write_unk3_region1(self):
            self._should_write_unk3_region1 = False
            if  ((self.unk_ofs_3 > 0) and (self.unk3_region1_end <= self.gap_end)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk3_offset_b)
                if len(self._m_unk3_region1) != 8 * self.unk3_count:
                    raise kaitaistruct.ConsistencyError(u"unk3_region1", 8 * self.unk3_count, len(self._m_unk3_region1))
                self._io.write_bytes(self._m_unk3_region1)
                self._io.seek(_pos)


        @property
        def unk3_region1_end(self):
            if hasattr(self, '_m_unk3_region1_end'):
                return self._m_unk3_region1_end

            self._m_unk3_region1_end = self.unk3_offset_b + 8 * self.unk3_count
            return getattr(self, '_m_unk3_region1_end', None)

        def _invalidate_unk3_region1_end(self):
            del self._m_unk3_region1_end
        @property
        def unk3_trailing(self):
            if self._should_write_unk3_trailing:
                self._write_unk3_trailing()
            if hasattr(self, '_m_unk3_trailing'):
                return self._m_unk3_trailing

            if not self.unk3_trailing__enabled:
                return None

            if  ((self.unk_ofs_3 > 0) and (self.unk3_region1_end <= self.gap_end) and (self.gap_end > self.unk3_region1_end)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk3_region1_end)
                self._m_unk3_trailing = self._io.read_bytes(self.gap_end - self.unk3_region1_end)
                self._io.seek(_pos)

            return getattr(self, '_m_unk3_trailing', None)

        @unk3_trailing.setter
        def unk3_trailing(self, v):
            self._dirty = True
            self._m_unk3_trailing = v

        def _write_unk3_trailing(self):
            self._should_write_unk3_trailing = False
            if  ((self.unk_ofs_3 > 0) and (self.unk3_region1_end <= self.gap_end) and (self.gap_end > self.unk3_region1_end)) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.unk3_region1_end)
                if len(self._m_unk3_trailing) != self.gap_end - self.unk3_region1_end:
                    raise kaitaistruct.ConsistencyError(u"unk3_trailing", self.gap_end - self.unk3_region1_end, len(self._m_unk3_trailing))
                self._io.write_bytes(self._m_unk3_trailing)
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



