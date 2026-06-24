# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Re4UhdBin(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Re4UhdBin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_adjacent = False
        self.adjacent__enabled = True
        self._should_write_bone_pairs = False
        self.bone_pairs__enabled = True
        self._should_write_bones = False
        self.bones__enabled = True
        self._should_write_indexes = False
        self.indexes__enabled = True
        self._should_write_indexes2 = False
        self.indexes2__enabled = True
        self._should_write_materials = False
        self.materials__enabled = True
        self._should_write_normals = False
        self.normals__enabled = True
        self._should_write_texcoords = False
        self.texcoords__enabled = True
        self._should_write_vertex_colors = False
        self.vertex_colors__enabled = True
        self._should_write_vertex_positions = False
        self.vertex_positions__enabled = True
        self._should_write_weights = False
        self.weights__enabled = True

    def _read(self):
        self.header = Re4UhdBin.UhdBinHeader(self._io, self, self._root)
        self.header._read()
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.adjacent
        if hasattr(self, '_m_adjacent'):
            pass
            self._m_adjacent._fetch_instances()

        _ = self.bone_pairs
        if hasattr(self, '_m_bone_pairs'):
            pass
            self._m_bone_pairs._fetch_instances()

        _ = self.bones
        if hasattr(self, '_m_bones'):
            pass
            for i in range(len(self._m_bones)):
                pass
                self._m_bones[i]._fetch_instances()


        _ = self.indexes
        if hasattr(self, '_m_indexes'):
            pass
            for i in range(len(self._m_indexes)):
                pass


        _ = self.indexes2
        if hasattr(self, '_m_indexes2'):
            pass
            for i in range(len(self._m_indexes2)):
                pass


        _ = self.materials
        if hasattr(self, '_m_materials'):
            pass
            for i in range(len(self._m_materials)):
                pass
                self._m_materials[i]._fetch_instances()


        _ = self.normals
        if hasattr(self, '_m_normals'):
            pass
            for i in range(len(self._m_normals)):
                pass
                self._m_normals[i]._fetch_instances()


        _ = self.texcoords
        if hasattr(self, '_m_texcoords'):
            pass
            for i in range(len(self._m_texcoords)):
                pass
                self._m_texcoords[i]._fetch_instances()


        _ = self.vertex_colors
        if hasattr(self, '_m_vertex_colors'):
            pass
            for i in range(len(self._m_vertex_colors)):
                pass
                self._m_vertex_colors[i]._fetch_instances()


        _ = self.vertex_positions
        if hasattr(self, '_m_vertex_positions'):
            pass
            for i in range(len(self._m_vertex_positions)):
                pass
                self._m_vertex_positions[i]._fetch_instances()


        _ = self.weights
        if hasattr(self, '_m_weights'):
            pass
            for i in range(len(self._m_weights)):
                pass
                _on = self.header.num_weights2 > 255
                if _on == False:
                    pass
                    self._m_weights[i]._fetch_instances()
                elif _on == True:
                    pass
                    self._m_weights[i]._fetch_instances()




    def _write__seq(self, io=None):
        super(Re4UhdBin, self)._write__seq(io)
        self._should_write_adjacent = self.adjacent__enabled
        self._should_write_bone_pairs = self.bone_pairs__enabled
        self._should_write_bones = self.bones__enabled
        self._should_write_indexes = self.indexes__enabled
        self._should_write_indexes2 = self.indexes2__enabled
        self._should_write_materials = self.materials__enabled
        self._should_write_normals = self.normals__enabled
        self._should_write_texcoords = self.texcoords__enabled
        self._should_write_vertex_colors = self.vertex_colors__enabled
        self._should_write_vertex_positions = self.vertex_positions__enabled
        self._should_write_weights = self.weights__enabled
        self.header._write__seq(self._io)


    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if self.adjacent__enabled:
            pass
            if self.header.offset_adjacents > 0:
                pass
                if self._m_adjacent._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"adjacent", self._root, self._m_adjacent._root)
                if self._m_adjacent._parent != self:
                    raise kaitaistruct.ConsistencyError(u"adjacent", self, self._m_adjacent._parent)


        if self.bone_pairs__enabled:
            pass
            if self.header.offset_bonepairs > 0:
                pass
                if self._m_bone_pairs._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bone_pairs", self._root, self._m_bone_pairs._root)
                if self._m_bone_pairs._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bone_pairs", self, self._m_bone_pairs._parent)


        if self.bones__enabled:
            pass
            if len(self._m_bones) != self.header.num_bones:
                raise kaitaistruct.ConsistencyError(u"bones", self.header.num_bones, len(self._m_bones))
            for i in range(len(self._m_bones)):
                pass
                if self._m_bones[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"bones", self._root, self._m_bones[i]._root)
                if self._m_bones[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"bones", self, self._m_bones[i]._parent)


        if self.indexes__enabled:
            pass
            if self.header.offset_index_buffer > 0:
                pass
                if len(self._m_indexes) != self.header.num_vertices:
                    raise kaitaistruct.ConsistencyError(u"indexes", self.header.num_vertices, len(self._m_indexes))
                for i in range(len(self._m_indexes)):
                    pass



        if self.indexes2__enabled:
            pass
            if self.header.offset_index_buffer2 > 0:
                pass
                if len(self._m_indexes2) != self.header.num_vertices:
                    raise kaitaistruct.ConsistencyError(u"indexes2", self.header.num_vertices, len(self._m_indexes2))
                for i in range(len(self._m_indexes2)):
                    pass



        if self.materials__enabled:
            pass
            if len(self._m_materials) != self.header.num_materials:
                raise kaitaistruct.ConsistencyError(u"materials", self.header.num_materials, len(self._m_materials))
            for i in range(len(self._m_materials)):
                pass
                if self._m_materials[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"materials", self._root, self._m_materials[i]._root)
                if self._m_materials[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"materials", self, self._m_materials[i]._parent)


        if self.normals__enabled:
            pass
            if len(self._m_normals) != self.header.num_vertex_normals:
                raise kaitaistruct.ConsistencyError(u"normals", self.header.num_vertex_normals, len(self._m_normals))
            for i in range(len(self._m_normals)):
                pass
                if self._m_normals[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"normals", self._root, self._m_normals[i]._root)
                if self._m_normals[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"normals", self, self._m_normals[i]._parent)


        if self.texcoords__enabled:
            pass
            if len(self._m_texcoords) != self.header.num_vertices:
                raise kaitaistruct.ConsistencyError(u"texcoords", self.header.num_vertices, len(self._m_texcoords))
            for i in range(len(self._m_texcoords)):
                pass
                if self._m_texcoords[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"texcoords", self._root, self._m_texcoords[i]._root)
                if self._m_texcoords[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"texcoords", self, self._m_texcoords[i]._parent)


        if self.vertex_colors__enabled:
            pass
            if self.header.offset_vertex_colors > 0:
                pass
                if len(self._m_vertex_colors) != self.header.num_vertices:
                    raise kaitaistruct.ConsistencyError(u"vertex_colors", self.header.num_vertices, len(self._m_vertex_colors))
                for i in range(len(self._m_vertex_colors)):
                    pass
                    if self._m_vertex_colors[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"vertex_colors", self._root, self._m_vertex_colors[i]._root)
                    if self._m_vertex_colors[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"vertex_colors", self, self._m_vertex_colors[i]._parent)



        if self.vertex_positions__enabled:
            pass
            if len(self._m_vertex_positions) != self.header.num_vertices:
                raise kaitaistruct.ConsistencyError(u"vertex_positions", self.header.num_vertices, len(self._m_vertex_positions))
            for i in range(len(self._m_vertex_positions)):
                pass
                if self._m_vertex_positions[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"vertex_positions", self._root, self._m_vertex_positions[i]._root)
                if self._m_vertex_positions[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"vertex_positions", self, self._m_vertex_positions[i]._parent)


        if self.weights__enabled:
            pass
            if len(self._m_weights) != self.header.num_weights:
                raise kaitaistruct.ConsistencyError(u"weights", self.header.num_weights, len(self._m_weights))
            for i in range(len(self._m_weights)):
                pass
                _on = self.header.num_weights2 > 255
                if _on == False:
                    pass
                    if self._m_weights[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"weights", self._root, self._m_weights[i]._root)
                    if self._m_weights[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"weights", self, self._m_weights[i]._parent)
                elif _on == True:
                    pass
                    if self._m_weights[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"weights", self._root, self._m_weights[i]._root)
                    if self._m_weights[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"weights", self, self._m_weights[i]._parent)


        self._dirty = False

    class Bone(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.Bone, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bone_id = self._io.read_u1()
            self.parent = self._io.read_u1()
            self.filler = self._io.read_u2le()
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.Bone, self)._write__seq(io)
            self._io.write_u1(self.bone_id)
            self._io.write_u1(self.parent)
            self._io.write_u2le(self.filler)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    class BoneAdj(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.BoneAdj, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.count = []
            for i in range(4):
                self.count.append(self._io.read_u1())

            self.adj = []
            for i in range(self.count[3]):
                self.adj.append(self._io.read_u2le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.count)):
                pass

            for i in range(len(self.adj)):
                pass



        def _write__seq(self, io=None):
            super(Re4UhdBin.BoneAdj, self)._write__seq(io)
            for i in range(len(self.count)):
                pass
                self._io.write_u1(self.count[i])

            for i in range(len(self.adj)):
                pass
                self._io.write_u2le(self.adj[i])



        def _check(self):
            if len(self.count) != 4:
                raise kaitaistruct.ConsistencyError(u"count", 4, len(self.count))
            for i in range(len(self.count)):
                pass

            if len(self.adj) != self.count[3]:
                raise kaitaistruct.ConsistencyError(u"adj", self.count[3], len(self.adj))
            for i in range(len(self.adj)):
                pass

            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4 + self.count[3] * 2
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class BonePair(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.BonePair, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_pair = self._io.read_u4le()
            self.line = []
            for i in range(self.num_pair):
                _t_line = Re4UhdBin.PairLine(self._io, self, self._root)
                try:
                    _t_line._read()
                finally:
                    self.line.append(_t_line)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.line)):
                pass
                self.line[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Re4UhdBin.BonePair, self)._write__seq(io)
            self._io.write_u4le(self.num_pair)
            for i in range(len(self.line)):
                pass
                self.line[i]._write__seq(self._io)



        def _check(self):
            if len(self.line) != self.num_pair:
                raise kaitaistruct.ConsistencyError(u"line", self.num_pair, len(self.line))
            for i in range(len(self.line)):
                pass
                if self.line[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"line", self._root, self.line[i]._root)
                if self.line[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"line", self, self.line[i]._parent)

            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 4 + 8 * self.num_pair
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class FaceIndex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.FaceIndex, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.buffer_size = self._io.read_u4le()
            self.count = self._io.read_u4le()
            self.strip_count = self._io.read_u4le()
            self.strips = []
            for i in range(self.strip_count):
                _t_strips = Re4UhdBin.Strip(self._io, self, self._root)
                try:
                    _t_strips._read()
                finally:
                    self.strips.append(_t_strips)

            self.padding = self._io.read_bytes(self.buffer_size - (self.strip_count * 4 + 4))
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.strips)):
                pass
                self.strips[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Re4UhdBin.FaceIndex, self)._write__seq(io)
            self._io.write_u4le(self.buffer_size)
            self._io.write_u4le(self.count)
            self._io.write_u4le(self.strip_count)
            for i in range(len(self.strips)):
                pass
                self.strips[i]._write__seq(self._io)

            self._io.write_bytes(self.padding)


        def _check(self):
            if len(self.strips) != self.strip_count:
                raise kaitaistruct.ConsistencyError(u"strips", self.strip_count, len(self.strips))
            for i in range(len(self.strips)):
                pass
                if self.strips[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"strips", self._root, self.strips[i]._root)
                if self.strips[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"strips", self, self.strips[i]._parent)

            if len(self.padding) != self.buffer_size - (self.strip_count * 4 + 4):
                raise kaitaistruct.ConsistencyError(u"padding", self.buffer_size - (self.strip_count * 4 + 4), len(self.padding))
            self._dirty = False


    class FmtbinWeight(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.FmtbinWeight, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bone_ids = []
            for i in range(3):
                self.bone_ids.append(self._io.read_u1())

            self.count = self._io.read_u1()
            self.weights = []
            for i in range(3):
                self.weights.append(self._io.read_u1())

            self.unk00 = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.bone_ids)):
                pass

            for i in range(len(self.weights)):
                pass



        def _write__seq(self, io=None):
            super(Re4UhdBin.FmtbinWeight, self)._write__seq(io)
            for i in range(len(self.bone_ids)):
                pass
                self._io.write_u1(self.bone_ids[i])

            self._io.write_u1(self.count)
            for i in range(len(self.weights)):
                pass
                self._io.write_u1(self.weights[i])

            self._io.write_u1(self.unk00)


        def _check(self):
            if len(self.bone_ids) != 3:
                raise kaitaistruct.ConsistencyError(u"bone_ids", 3, len(self.bone_ids))
            for i in range(len(self.bone_ids)):
                pass

            if len(self.weights) != 3:
                raise kaitaistruct.ConsistencyError(u"weights", 3, len(self.weights))
            for i in range(len(self.weights)):
                pass

            self._dirty = False


    class FmtbinWeightExt(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.FmtbinWeightExt, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bone_ids = []
            for i in range(3):
                self.bone_ids.append(self._io.read_u2le())

            self.count = self._io.read_u2le()
            self.weights = []
            for i in range(3):
                self.weights.append(self._io.read_u1())

            self.unk00 = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.bone_ids)):
                pass

            for i in range(len(self.weights)):
                pass



        def _write__seq(self, io=None):
            super(Re4UhdBin.FmtbinWeightExt, self)._write__seq(io)
            for i in range(len(self.bone_ids)):
                pass
                self._io.write_u2le(self.bone_ids[i])

            self._io.write_u2le(self.count)
            for i in range(len(self.weights)):
                pass
                self._io.write_u1(self.weights[i])

            self._io.write_u1(self.unk00)


        def _check(self):
            if len(self.bone_ids) != 3:
                raise kaitaistruct.ConsistencyError(u"bone_ids", 3, len(self.bone_ids))
            for i in range(len(self.bone_ids)):
                pass

            if len(self.weights) != 3:
                raise kaitaistruct.ConsistencyError(u"weights", 3, len(self.weights))
            for i in range(len(self.weights)):
                pass

            self._dirty = False


    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.Material, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_min_11 = self._io.read_u1()
            self.unk_min_10 = self._io.read_u1()
            self.unk_min_09 = self._io.read_u1()
            self.unk_min_08 = self._io.read_u1()
            self.unk_min_07 = self._io.read_u1()
            self.unk_min_06 = self._io.read_u1()
            self.unk_min_05 = self._io.read_u1()
            self.unk_min_04 = self._io.read_u1()
            self.unk_min_03 = self._io.read_u1()
            self.unk_min_02 = self._io.read_u1()
            self.unk_min_01 = self._io.read_u1()
            self.material_flag = self._io.read_u1()
            self.diffuse_map = self._io.read_u1()
            self.bump_map = self._io.read_u1()
            self.opacity_map = self._io.read_u1()
            self.generic_specular_map = self._io.read_u1()
            self.intensity_specular_r = self._io.read_u1()
            self.intensity_specular_g = self._io.read_u1()
            self.intensity_specular_b = self._io.read_u1()
            self.unk_00 = self._io.read_u1()
            self.unk_01 = self._io.read_u1()
            self.specular_scale = self._io.read_u1()
            self.unk_02 = self._io.read_u1()
            self.custom_specular_map = self._io.read_u1()
            self.face_index = Re4UhdBin.FaceIndex(self._io, self, self._root)
            self.face_index._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.face_index._fetch_instances()


        def _write__seq(self, io=None):
            super(Re4UhdBin.Material, self)._write__seq(io)
            self._io.write_u1(self.unk_min_11)
            self._io.write_u1(self.unk_min_10)
            self._io.write_u1(self.unk_min_09)
            self._io.write_u1(self.unk_min_08)
            self._io.write_u1(self.unk_min_07)
            self._io.write_u1(self.unk_min_06)
            self._io.write_u1(self.unk_min_05)
            self._io.write_u1(self.unk_min_04)
            self._io.write_u1(self.unk_min_03)
            self._io.write_u1(self.unk_min_02)
            self._io.write_u1(self.unk_min_01)
            self._io.write_u1(self.material_flag)
            self._io.write_u1(self.diffuse_map)
            self._io.write_u1(self.bump_map)
            self._io.write_u1(self.opacity_map)
            self._io.write_u1(self.generic_specular_map)
            self._io.write_u1(self.intensity_specular_r)
            self._io.write_u1(self.intensity_specular_g)
            self._io.write_u1(self.intensity_specular_b)
            self._io.write_u1(self.unk_00)
            self._io.write_u1(self.unk_01)
            self._io.write_u1(self.specular_scale)
            self._io.write_u1(self.unk_02)
            self._io.write_u1(self.custom_specular_map)
            self.face_index._write__seq(self._io)


        def _check(self):
            if self.face_index._root != self._root:
                raise kaitaistruct.ConsistencyError(u"face_index", self._root, self.face_index._root)
            if self.face_index._parent != self:
                raise kaitaistruct.ConsistencyError(u"face_index", self, self.face_index._parent)
            self._dirty = False


    class PairLine(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.PairLine, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.data = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.PairLine, self)._write__seq(io)
            self._io.write_bytes(self.data)


        def _check(self):
            if len(self.data) != 8:
                raise kaitaistruct.ConsistencyError(u"data", 8, len(self.data))
            self._dirty = False


    class Rgba(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.Rgba, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.a = self._io.read_u1()
            self.r = self._io.read_u1()
            self.g = self._io.read_u1()
            self.b = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.Rgba, self)._write__seq(io)
            self._io.write_u1(self.a)
            self._io.write_u1(self.r)
            self._io.write_u1(self.g)
            self._io.write_u1(self.b)


        def _check(self):
            self._dirty = False


    class Strip(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.Strip, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ftype = self._io.read_u2le()
            self.fcount = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.Strip, self)._write__seq(io)
            self._io.write_u2le(self.ftype)
            self._io.write_u2le(self.fcount)


        def _check(self):
            self._dirty = False


    class UhdBinHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.UhdBinHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.offset_bones = self._io.read_u4le()
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = self._io.read_u4le()
            self.offset_vertex_colors = self._io.read_u4le()
            self.offset_vertex_texcoord = self._io.read_u4le()
            self.offset_weights = self._io.read_u4le()
            self.num_weights = self._io.read_u1()
            self.num_bones = self._io.read_u1()
            self.num_materials = self._io.read_u2le()
            self.offset_materials = self._io.read_u4le()
            self.texture1_flags = self._io.read_u2le()
            self.texture2_flags = self._io.read_u2le()
            self.num_tpl = self._io.read_u4le()
            self.vertex_scale = self._io.read_u1()
            self.unk_02 = self._io.read_u1()
            self.num_weights2 = self._io.read_u2le()
            self.offset_morphs = self._io.read_u4le()
            self.offset_vertex_position = self._io.read_u4le()
            self.offset_vertex_normals = self._io.read_u4le()
            self.num_vertices = self._io.read_u2le()
            self.num_vertex_normals = self._io.read_u2le()
            self.version_flags = self._io.read_u4le()
            self.offset_bonepairs = self._io.read_u4le()
            self.offset_adjacents = self._io.read_u4le()
            self.offset_index_buffer = self._io.read_u4le()
            self.offset_index_buffer2 = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.UhdBinHeader, self)._write__seq(io)
            self._io.write_u4le(self.offset_bones)
            self._io.write_u4le(self.unk_00)
            self._io.write_u4le(self.unk_01)
            self._io.write_u4le(self.offset_vertex_colors)
            self._io.write_u4le(self.offset_vertex_texcoord)
            self._io.write_u4le(self.offset_weights)
            self._io.write_u1(self.num_weights)
            self._io.write_u1(self.num_bones)
            self._io.write_u2le(self.num_materials)
            self._io.write_u4le(self.offset_materials)
            self._io.write_u2le(self.texture1_flags)
            self._io.write_u2le(self.texture2_flags)
            self._io.write_u4le(self.num_tpl)
            self._io.write_u1(self.vertex_scale)
            self._io.write_u1(self.unk_02)
            self._io.write_u2le(self.num_weights2)
            self._io.write_u4le(self.offset_morphs)
            self._io.write_u4le(self.offset_vertex_position)
            self._io.write_u4le(self.offset_vertex_normals)
            self._io.write_u2le(self.num_vertices)
            self._io.write_u2le(self.num_vertex_normals)
            self._io.write_u4le(self.version_flags)
            self._io.write_u4le(self.offset_bonepairs)
            self._io.write_u4le(self.offset_adjacents)
            self._io.write_u4le(self.offset_index_buffer)
            self._io.write_u4le(self.offset_index_buffer2)


        def _check(self):
            self._dirty = False

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 96
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Uv(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.Uv, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.u = self._io.read_f4le()
            self.v = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.Uv, self)._write__seq(io)
            self._io.write_f4le(self.u)
            self._io.write_f4le(self.v)


        def _check(self):
            self._dirty = False


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdBin.Vec3, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdBin.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    @property
    def adjacent(self):
        if self._should_write_adjacent:
            self._write_adjacent()
        if hasattr(self, '_m_adjacent'):
            return self._m_adjacent

        if not self.adjacent__enabled:
            return None

        if self.header.offset_adjacents > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_adjacents)
            self._m_adjacent = Re4UhdBin.BoneAdj(self._io, self, self._root)
            self._m_adjacent._read()
            self._io.seek(_pos)

        return getattr(self, '_m_adjacent', None)

    @adjacent.setter
    def adjacent(self, v):
        self._dirty = True
        self._m_adjacent = v

    def _write_adjacent(self):
        self._should_write_adjacent = False
        if self.header.offset_adjacents > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_adjacents)
            self._m_adjacent._write__seq(self._io)
            self._io.seek(_pos)


    @property
    def bone_pairs(self):
        if self._should_write_bone_pairs:
            self._write_bone_pairs()
        if hasattr(self, '_m_bone_pairs'):
            return self._m_bone_pairs

        if not self.bone_pairs__enabled:
            return None

        if self.header.offset_bonepairs > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bonepairs)
            self._m_bone_pairs = Re4UhdBin.BonePair(self._io, self, self._root)
            self._m_bone_pairs._read()
            self._io.seek(_pos)

        return getattr(self, '_m_bone_pairs', None)

    @bone_pairs.setter
    def bone_pairs(self, v):
        self._dirty = True
        self._m_bone_pairs = v

    def _write_bone_pairs(self):
        self._should_write_bone_pairs = False
        if self.header.offset_bonepairs > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_bonepairs)
            self._m_bone_pairs._write__seq(self._io)
            self._io.seek(_pos)


    @property
    def bones(self):
        if self._should_write_bones:
            self._write_bones()
        if hasattr(self, '_m_bones'):
            return self._m_bones

        if not self.bones__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_bones)
        self._m_bones = []
        for i in range(self.header.num_bones):
            _t__m_bones = Re4UhdBin.Bone(self._io, self, self._root)
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
        self._io.seek(self.header.offset_bones)
        for i in range(len(self._m_bones)):
            pass
            self._m_bones[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def indexes(self):
        if self._should_write_indexes:
            self._write_indexes()
        if hasattr(self, '_m_indexes'):
            return self._m_indexes

        if not self.indexes__enabled:
            return None

        if self.header.offset_index_buffer > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer)
            self._m_indexes = []
            for i in range(self.header.num_vertices):
                self._m_indexes.append(self._io.read_u2le())

            self._io.seek(_pos)

        return getattr(self, '_m_indexes', None)

    @indexes.setter
    def indexes(self, v):
        self._dirty = True
        self._m_indexes = v

    def _write_indexes(self):
        self._should_write_indexes = False
        if self.header.offset_index_buffer > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer)
            for i in range(len(self._m_indexes)):
                pass
                self._io.write_u2le(self._m_indexes[i])

            self._io.seek(_pos)


    @property
    def indexes2(self):
        if self._should_write_indexes2:
            self._write_indexes2()
        if hasattr(self, '_m_indexes2'):
            return self._m_indexes2

        if not self.indexes2__enabled:
            return None

        if self.header.offset_index_buffer2 > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer2)
            self._m_indexes2 = []
            for i in range(self.header.num_vertices):
                self._m_indexes2.append(self._io.read_u2le())

            self._io.seek(_pos)

        return getattr(self, '_m_indexes2', None)

    @indexes2.setter
    def indexes2(self, v):
        self._dirty = True
        self._m_indexes2 = v

    def _write_indexes2(self):
        self._should_write_indexes2 = False
        if self.header.offset_index_buffer2 > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_index_buffer2)
            for i in range(len(self._m_indexes2)):
                pass
                self._io.write_u2le(self._m_indexes2[i])

            self._io.seek(_pos)


    @property
    def materials(self):
        if self._should_write_materials:
            self._write_materials()
        if hasattr(self, '_m_materials'):
            return self._m_materials

        if not self.materials__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_materials)
        self._m_materials = []
        for i in range(self.header.num_materials):
            _t__m_materials = Re4UhdBin.Material(self._io, self, self._root)
            try:
                _t__m_materials._read()
            finally:
                self._m_materials.append(_t__m_materials)

        self._io.seek(_pos)
        return getattr(self, '_m_materials', None)

    @materials.setter
    def materials(self, v):
        self._dirty = True
        self._m_materials = v

    def _write_materials(self):
        self._should_write_materials = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_materials)
        for i in range(len(self._m_materials)):
            pass
            self._m_materials[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def normals(self):
        if self._should_write_normals:
            self._write_normals()
        if hasattr(self, '_m_normals'):
            return self._m_normals

        if not self.normals__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_normals)
        self._m_normals = []
        for i in range(self.header.num_vertex_normals):
            _t__m_normals = Re4UhdBin.Vec3(self._io, self, self._root)
            try:
                _t__m_normals._read()
            finally:
                self._m_normals.append(_t__m_normals)

        self._io.seek(_pos)
        return getattr(self, '_m_normals', None)

    @normals.setter
    def normals(self, v):
        self._dirty = True
        self._m_normals = v

    def _write_normals(self):
        self._should_write_normals = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_normals)
        for i in range(len(self._m_normals)):
            pass
            self._m_normals[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def texcoords(self):
        if self._should_write_texcoords:
            self._write_texcoords()
        if hasattr(self, '_m_texcoords'):
            return self._m_texcoords

        if not self.texcoords__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_texcoord)
        self._m_texcoords = []
        for i in range(self.header.num_vertices):
            _t__m_texcoords = Re4UhdBin.Uv(self._io, self, self._root)
            try:
                _t__m_texcoords._read()
            finally:
                self._m_texcoords.append(_t__m_texcoords)

        self._io.seek(_pos)
        return getattr(self, '_m_texcoords', None)

    @texcoords.setter
    def texcoords(self, v):
        self._dirty = True
        self._m_texcoords = v

    def _write_texcoords(self):
        self._should_write_texcoords = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_texcoord)
        for i in range(len(self._m_texcoords)):
            pass
            self._m_texcoords[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def vertex_colors(self):
        if self._should_write_vertex_colors:
            self._write_vertex_colors()
        if hasattr(self, '_m_vertex_colors'):
            return self._m_vertex_colors

        if not self.vertex_colors__enabled:
            return None

        if self.header.offset_vertex_colors > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_vertex_colors)
            self._m_vertex_colors = []
            for i in range(self.header.num_vertices):
                _t__m_vertex_colors = Re4UhdBin.Rgba(self._io, self, self._root)
                try:
                    _t__m_vertex_colors._read()
                finally:
                    self._m_vertex_colors.append(_t__m_vertex_colors)

            self._io.seek(_pos)

        return getattr(self, '_m_vertex_colors', None)

    @vertex_colors.setter
    def vertex_colors(self, v):
        self._dirty = True
        self._m_vertex_colors = v

    def _write_vertex_colors(self):
        self._should_write_vertex_colors = False
        if self.header.offset_vertex_colors > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.header.offset_vertex_colors)
            for i in range(len(self._m_vertex_colors)):
                pass
                self._m_vertex_colors[i]._write__seq(self._io)

            self._io.seek(_pos)


    @property
    def vertex_positions(self):
        if self._should_write_vertex_positions:
            self._write_vertex_positions()
        if hasattr(self, '_m_vertex_positions'):
            return self._m_vertex_positions

        if not self.vertex_positions__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_position)
        self._m_vertex_positions = []
        for i in range(self.header.num_vertices):
            _t__m_vertex_positions = Re4UhdBin.Vec3(self._io, self, self._root)
            try:
                _t__m_vertex_positions._read()
            finally:
                self._m_vertex_positions.append(_t__m_vertex_positions)

        self._io.seek(_pos)
        return getattr(self, '_m_vertex_positions', None)

    @vertex_positions.setter
    def vertex_positions(self, v):
        self._dirty = True
        self._m_vertex_positions = v

    def _write_vertex_positions(self):
        self._should_write_vertex_positions = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_vertex_position)
        for i in range(len(self._m_vertex_positions)):
            pass
            self._m_vertex_positions[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def weights(self):
        if self._should_write_weights:
            self._write_weights()
        if hasattr(self, '_m_weights'):
            return self._m_weights

        if not self.weights__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_weights)
        self._m_weights = []
        for i in range(self.header.num_weights):
            _on = self.header.num_weights2 > 255
            if _on == False:
                pass
                _t__m_weights = Re4UhdBin.FmtbinWeight(self._io, self, self._root)
                try:
                    _t__m_weights._read()
                finally:
                    self._m_weights.append(_t__m_weights)
            elif _on == True:
                pass
                _t__m_weights = Re4UhdBin.FmtbinWeightExt(self._io, self, self._root)
                try:
                    _t__m_weights._read()
                finally:
                    self._m_weights.append(_t__m_weights)

        self._io.seek(_pos)
        return getattr(self, '_m_weights', None)

    @weights.setter
    def weights(self, v):
        self._dirty = True
        self._m_weights = v

    def _write_weights(self):
        self._should_write_weights = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_weights)
        for i in range(len(self._m_weights)):
            pass
            _on = self.header.num_weights2 > 255
            if _on == False:
                pass
                self._m_weights[i]._write__seq(self._io)
            elif _on == True:
                pass
                self._m_weights[i]._write__seq(self._io)

        self._io.seek(_pos)


