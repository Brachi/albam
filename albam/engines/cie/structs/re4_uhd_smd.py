# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Re4UhdSmd(ReadWriteKaitaiStruct):
    """A room's own geometry, as opposed to the props standing in it.
    
    An .smd is a placement table plus the models it places: a list of fixed
    size entries, each naming a model by index and carrying the position,
    rotation and scale to put it at, followed - much later in the file - by
    two tables of offsets, one to the embedded models (the same format as a
    standalone mesh .bin, see re4-uhd-bin.ksy) and one to the embedded .tpl
    each entry addresses its textures through.
    
    Neither offset table states its own length: what ends one is a zero
    entry past its last real offset. The entries are no help there - a table
    can hold a model no entry places, and files sampled carry one spare that
    points at nothing readable - so the terminator is the only bound, and an
    offset only means something once an entry indexes it.
    
    A room too big for one file is split: the entries of the extra files can
    point at models embedded in the room's shared file rather than in
    themselves (see entry_status).
    """
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Re4UhdSmd, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_offsets_models = False
        self.offsets_models__enabled = True
        self._should_write_offsets_tpls = False
        self.offsets_tpls__enabled = True

    def _read(self):
        self.header = Re4UhdSmd.SmdHeader(self._io, self, self._root)
        self.header._read()
        self.entries = []
        for i in range(self.header.num_entries):
            _t_entries = Re4UhdSmd.SmdEntry(self._io, self, self._root)
            try:
                _t_entries._read()
            finally:
                self.entries.append(_t_entries)

        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.entries)):
            pass
            self.entries[i]._fetch_instances()

        _ = self.offsets_models
        if hasattr(self, '_m_offsets_models'):
            pass
            for i in range(len(self._m_offsets_models)):
                pass


        _ = self.offsets_tpls
        if hasattr(self, '_m_offsets_tpls'):
            pass
            for i in range(len(self._m_offsets_tpls)):
                pass




    def _write__seq(self, io=None):
        super(Re4UhdSmd, self)._write__seq(io)
        self._should_write_offsets_models = self.offsets_models__enabled
        self._should_write_offsets_tpls = self.offsets_tpls__enabled
        self.header._write__seq(self._io)
        for i in range(len(self.entries)):
            pass
            self.entries[i]._write__seq(self._io)



    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.entries) != self.header.num_entries:
            raise kaitaistruct.ConsistencyError(u"entries", self.header.num_entries, len(self.entries))
        for i in range(len(self.entries)):
            pass
            if self.entries[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"entries", self._root, self.entries[i]._root)
            if self.entries[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"entries", self, self.entries[i]._parent)

        if self.offsets_models__enabled:
            pass
            if len(self._m_offsets_models) == 0:
                raise kaitaistruct.ConsistencyError(u"offsets_models", 0, len(self._m_offsets_models))
            for i in range(len(self._m_offsets_models)):
                pass
                _ = self._m_offsets_models[i]
                if (_ == 0) != (i == len(self._m_offsets_models) - 1):
                    raise kaitaistruct.ConsistencyError(u"offsets_models", i == len(self._m_offsets_models) - 1, _ == 0)


        if self.offsets_tpls__enabled:
            pass
            if len(self._m_offsets_tpls) == 0:
                raise kaitaistruct.ConsistencyError(u"offsets_tpls", 0, len(self._m_offsets_tpls))
            for i in range(len(self._m_offsets_tpls)):
                pass
                _ = self._m_offsets_tpls[i]
                if (_ == 0) != (i == len(self._m_offsets_tpls) - 1):
                    raise kaitaistruct.ConsistencyError(u"offsets_tpls", i == len(self._m_offsets_tpls) - 1, _ == 0)


        self._dirty = False

    class ExtraCounts(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdSmd.ExtraCounts, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_values = self._io.read_u4le()
            self.values = []
            for i in range(self.num_values):
                self.values.append(self._io.read_u4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.values)):
                pass



        def _write__seq(self, io=None):
            super(Re4UhdSmd.ExtraCounts, self)._write__seq(io)
            self._io.write_u4le(self.num_values)
            for i in range(len(self.values)):
                pass
                self._io.write_u4le(self.values[i])



        def _check(self):
            if len(self.values) != self.num_values:
                raise kaitaistruct.ConsistencyError(u"values", self.num_values, len(self.values))
            for i in range(len(self.values)):
                pass

            self._dirty = False


    class SmdEntry(ReadWriteKaitaiStruct):
        """One placed model. The position is in the same unit as a model's own
        vertices, the angles are radians applied X then Y then Z, and the
        scale multiplies the rotated position per axis.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdSmd.SmdEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position = Re4UhdSmd.Vec3f(self._io, self, self._root)
            self.position._read()
            self.angles = Re4UhdSmd.Vec3f(self._io, self, self._root)
            self.angles._read()
            self.scale = Re4UhdSmd.Vec3f(self._io, self, self._root)
            self.scale._read()
            self.model_id = self._io.read_u1()
            self.tpl_id = self._io.read_u1()
            self.enabled = self._io.read_u1()
            self.smx_id = self._io.read_u1()
            self.unk_00 = []
            for i in range(7):
                self.unk_00.append(self._io.read_u4le())

            self.status = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.angles._fetch_instances()
            self.scale._fetch_instances()
            for i in range(len(self.unk_00)):
                pass



        def _write__seq(self, io=None):
            super(Re4UhdSmd.SmdEntry, self)._write__seq(io)
            self.position._write__seq(self._io)
            self.angles._write__seq(self._io)
            self.scale._write__seq(self._io)
            self._io.write_u1(self.model_id)
            self._io.write_u1(self.tpl_id)
            self._io.write_u1(self.enabled)
            self._io.write_u1(self.smx_id)
            for i in range(len(self.unk_00)):
                pass
                self._io.write_u4le(self.unk_00[i])

            self._io.write_u4le(self.status)


        def _check(self):
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self._root, self.position._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self, self.position._parent)
            if self.angles._root != self._root:
                raise kaitaistruct.ConsistencyError(u"angles", self._root, self.angles._root)
            if self.angles._parent != self:
                raise kaitaistruct.ConsistencyError(u"angles", self, self.angles._parent)
            if self.scale._root != self._root:
                raise kaitaistruct.ConsistencyError(u"scale", self._root, self.scale._root)
            if self.scale._parent != self:
                raise kaitaistruct.ConsistencyError(u"scale", self, self.scale._parent)
            if len(self.unk_00) != 7:
                raise kaitaistruct.ConsistencyError(u"unk_00", 7, len(self.unk_00))
            for i in range(len(self.unk_00)):
                pass

            self._dirty = False

        @property
        def is_placed(self):
            if hasattr(self, '_m_is_placed'):
                return self._m_is_placed

            self._m_is_placed =  ((self.scale.x != 0.0) or (self.scale.y != 0.0) or (self.scale.z != 0.0)) 
            return getattr(self, '_m_is_placed', None)

        def _invalidate_is_placed(self):
            del self._m_is_placed
        @property
        def is_shared(self):
            if hasattr(self, '_m_is_shared'):
                return self._m_is_shared

            self._m_is_shared = self.status & 16 != 0
            return getattr(self, '_m_is_shared', None)

        def _invalidate_is_shared(self):
            del self._m_is_shared

    class SmdHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdSmd.SmdHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_u2le()
            self.num_entries = self._io.read_u2le()
            self.offset_model_table = self._io.read_u4le()
            self.offset_tpl_table = self._io.read_u4le()
            self.offset_first_model = self._io.read_u4le()
            if self.magic == 320:
                pass
                self.extra = Re4UhdSmd.ExtraCounts(self._io, self, self._root)
                self.extra._read()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.magic == 320:
                pass
                self.extra._fetch_instances()



        def _write__seq(self, io=None):
            super(Re4UhdSmd.SmdHeader, self)._write__seq(io)
            self._io.write_u2le(self.magic)
            self._io.write_u2le(self.num_entries)
            self._io.write_u4le(self.offset_model_table)
            self._io.write_u4le(self.offset_tpl_table)
            self._io.write_u4le(self.offset_first_model)
            if self.magic == 320:
                pass
                self.extra._write__seq(self._io)



        def _check(self):
            if self.magic == 320:
                pass
                if self.extra._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"extra", self._root, self.extra._root)
                if self.extra._parent != self:
                    raise kaitaistruct.ConsistencyError(u"extra", self, self.extra._parent)

            self._dirty = False


    class Vec3f(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdSmd.Vec3f, self).__init__(_io)
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
            super(Re4UhdSmd.Vec3f, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    @property
    def offsets_models(self):
        if self._should_write_offsets_models:
            self._write_offsets_models()
        if hasattr(self, '_m_offsets_models'):
            return self._m_offsets_models

        if not self.offsets_models__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_model_table)
        self._m_offsets_models = []
        i = 0
        while True:
            _ = self._io.read_u4le()
            self._m_offsets_models.append(_)
            if _ == 0:
                break
            i += 1
        self._io.seek(_pos)
        return getattr(self, '_m_offsets_models', None)

    @offsets_models.setter
    def offsets_models(self, v):
        self._dirty = True
        self._m_offsets_models = v

    def _write_offsets_models(self):
        self._should_write_offsets_models = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_model_table)
        for i in range(len(self._m_offsets_models)):
            pass
            self._io.write_u4le(self._m_offsets_models[i])

        self._io.seek(_pos)

    @property
    def offsets_tpls(self):
        if self._should_write_offsets_tpls:
            self._write_offsets_tpls()
        if hasattr(self, '_m_offsets_tpls'):
            return self._m_offsets_tpls

        if not self.offsets_tpls__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_tpl_table)
        self._m_offsets_tpls = []
        i = 0
        while True:
            _ = self._io.read_u4le()
            self._m_offsets_tpls.append(_)
            if _ == 0:
                break
            i += 1
        self._io.seek(_pos)
        return getattr(self, '_m_offsets_tpls', None)

    @offsets_tpls.setter
    def offsets_tpls(self, v):
        self._dirty = True
        self._m_offsets_tpls = v

    def _write_offsets_tpls(self):
        self._should_write_offsets_tpls = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_tpl_table)
        for i in range(len(self._m_offsets_tpls)):
            pass
            self._io.write_u4le(self._m_offsets_tpls[i])

        self._io.seek(_pos)


