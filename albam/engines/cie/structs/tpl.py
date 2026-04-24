# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tpl(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Tpl, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_tpl_entries = False
        self.tpl_entries__enabled = True

    def _read(self):
        self.magic = self._io.read_u4le()
        self.num_tpl = self._io.read_u4le()
        self.offset = self._io.read_u4le()
        self._dirty = False


    def _fetch_instances(self):
        pass
        _ = self.tpl_entries
        if hasattr(self, '_m_tpl_entries'):
            pass
            for i in range(len(self._m_tpl_entries)):
                pass
                self._m_tpl_entries[i]._fetch_instances()




    def _write__seq(self, io=None):
        super(Tpl, self)._write__seq(io)
        self._should_write_tpl_entries = self.tpl_entries__enabled
        self._io.write_u4le(self.magic)
        self._io.write_u4le(self.num_tpl)
        self._io.write_u4le(self.offset)


    def _check(self):
        if self.tpl_entries__enabled:
            pass
            if len(self._m_tpl_entries) != self.num_tpl:
                raise kaitaistruct.ConsistencyError(u"tpl_entries", self.num_tpl, len(self._m_tpl_entries))
            for i in range(len(self._m_tpl_entries)):
                pass
                if self._m_tpl_entries[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"tpl_entries", self._root, self._m_tpl_entries[i]._root)
                if self._m_tpl_entries[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"tpl_entries", self, self._m_tpl_entries[i]._parent)


        self._dirty = False

    class TplEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Tpl.TplEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_image_data = False
            self.image_data__enabled = True

        def _read(self):
            self.offset_image_data = self._io.read_u4le()
            self.offset_palette = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.image_data
            if hasattr(self, '_m_image_data'):
                pass
                self._m_image_data._fetch_instances()



        def _write__seq(self, io=None):
            super(Tpl.TplEntry, self)._write__seq(io)
            self._should_write_image_data = self.image_data__enabled
            self._io.write_u4le(self.offset_image_data)
            self._io.write_u4le(self.offset_palette)


        def _check(self):
            if self.image_data__enabled:
                pass
                if self._m_image_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"image_data", self._root, self._m_image_data._root)
                if self._m_image_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"image_data", self, self._m_image_data._parent)

            self._dirty = False

        @property
        def image_data(self):
            if self._should_write_image_data:
                self._write_image_data()
            if hasattr(self, '_m_image_data'):
                return self._m_image_data

            if not self.image_data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset_image_data)
            self._m_image_data = Tpl.TplInfo(self._io, self, self._root)
            self._m_image_data._read()
            self._io.seek(_pos)
            return getattr(self, '_m_image_data', None)

        @image_data.setter
        def image_data(self, v):
            self._dirty = True
            self._m_image_data = v

        def _write_image_data(self):
            self._should_write_image_data = False
            _pos = self._io.pos()
            self._io.seek(self.offset_image_data)
            self._m_image_data._write__seq(self._io)
            self._io.seek(_pos)


    class TplInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Tpl.TplInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.width = self._io.read_u2le()
            self.height = self._io.read_u2le()
            self.pixel_format_type = self._io.read_u4le()
            self.id_offset = self._io.read_u4le()
            self.wrap_s = self._io.read_u4le()
            self.wrap_4 = self._io.read_u4le()
            self.min_filter = self._io.read_u4le()
            self.mag_filter = self._io.read_u4le()
            self.lod_bias = self._io.read_f4le()
            self.enable_lod = self._io.read_u1()
            self.min_lod = self._io.read_u1()
            self.max_lod = self._io.read_u1()
            self.is_compressed = self._io.read_u1()
            self.pack_id = self._io.read_u4le()
            self.texture_id = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Tpl.TplInfo, self)._write__seq(io)
            self._io.write_u2le(self.width)
            self._io.write_u2le(self.height)
            self._io.write_u4le(self.pixel_format_type)
            self._io.write_u4le(self.id_offset)
            self._io.write_u4le(self.wrap_s)
            self._io.write_u4le(self.wrap_4)
            self._io.write_u4le(self.min_filter)
            self._io.write_u4le(self.mag_filter)
            self._io.write_f4le(self.lod_bias)
            self._io.write_u1(self.enable_lod)
            self._io.write_u1(self.min_lod)
            self._io.write_u1(self.max_lod)
            self._io.write_u1(self.is_compressed)
            self._io.write_u4le(self.pack_id)
            self._io.write_u4le(self.texture_id)


        def _check(self):
            self._dirty = False


    @property
    def tpl_entries(self):
        if self._should_write_tpl_entries:
            self._write_tpl_entries()
        if hasattr(self, '_m_tpl_entries'):
            return self._m_tpl_entries

        if not self.tpl_entries__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.offset)
        self._m_tpl_entries = []
        for i in range(self.num_tpl):
            _t__m_tpl_entries = Tpl.TplEntry(self._io, self, self._root)
            try:
                _t__m_tpl_entries._read()
            finally:
                self._m_tpl_entries.append(_t__m_tpl_entries)

        self._io.seek(_pos)
        return getattr(self, '_m_tpl_entries', None)

    @tpl_entries.setter
    def tpl_entries(self, v):
        self._dirty = True
        self._m_tpl_entries = v

    def _write_tpl_entries(self):
        self._should_write_tpl_entries = False
        _pos = self._io.pos()
        self._io.seek(self.offset)
        for i in range(len(self._m_tpl_entries)):
            pass
            self._m_tpl_entries[i]._write__seq(self._io)

        self._io.seek(_pos)


