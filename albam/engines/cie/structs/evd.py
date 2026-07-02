# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Evd(ReadWriteKaitaiStruct):

    class EvpTp(IntEnum):
        evp_tp_begin_evt = 0
        evp_tp_set_pl = 1
        evp_tp_set_em = 2
        evp_tp_set_om = 3
        evp_tp_set_parts = 4
        evp_tp_set_list = 5
        evp_tp_cam = 6
        evp_tp_cam_pos = 7
        evp_tp_cam_dammy = 8
        evp_tp_pos = 9
        evp_tp_pos_pl = 10
        evp_tp_mot = 11
        evp_tp_shp = 12
        evp_tp_esp = 13
        evp_tp_lit = 14
        evp_tp_str = 15
        evp_tp_se = 16
        evp_tp_mes = 17
        evp_tp_func = 18
        evp_tp_parent_on = 19
        evp_tp_parent_off = 20
        evp_tp_end_pl = 21
        evp_tp_end_em = 22
        evp_tp_end_om = 23
        evp_tp_end_parts = 24
        evp_tp_end_list = 25
        evp_tp_end_evt = 26
        evp_tp_end_pac = 27
        evp_tp_set_eff = 28
        evp_tp_fade = 29
        evp_tp_fog = 30
        evp_tp_focus = 31
        evp_tp_set_mdt = 32

    class EvtEspKindId(IntEnum):
        evt_esp_room = 0
        evt_esp_core = 1
        evt_esp_pl = 2
        evt_esp_em = 3
        evt_esp_wep = 4
        evt_esp_evt = 5
        evt_esp_et00 = 6

    class EvtFade(IntEnum):
        evt_fade_in = 0
        evt_fade_out = 1
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Evd, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._should_write_file_entries = False
        self.file_entries__enabled = True
        self._should_write_packets = False
        self.packets__enabled = True

    def _read(self):
        self.header = Evd.EvdHeader(self._io, self, self._root)
        self.header._read()
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.file_entries
        if hasattr(self, '_m_file_entries'):
            pass
            for i in range(len(self._m_file_entries)):
                pass
                self._m_file_entries[i]._fetch_instances()


        _ = self.packets
        if hasattr(self, '_m_packets'):
            pass
            for i in range(len(self._m_packets)):
                pass
                self._m_packets[i]._fetch_instances()




    def _write__seq(self, io=None):
        super(Evd, self)._write__seq(io)
        self._should_write_file_entries = self.file_entries__enabled
        self._should_write_packets = self.packets__enabled
        self.header._write__seq(self._io)


    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if self.file_entries__enabled:
            pass
            if len(self._m_file_entries) != self.header.num_bin_tbl:
                raise kaitaistruct.ConsistencyError(u"file_entries", self.header.num_bin_tbl, len(self._m_file_entries))
            for i in range(len(self._m_file_entries)):
                pass
                if self._m_file_entries[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"file_entries", self._root, self._m_file_entries[i]._root)
                if self._m_file_entries[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"file_entries", self, self._m_file_entries[i]._parent)


        if self.packets__enabled:
            pass
            if len(self._m_packets) == 0:
                raise kaitaistruct.ConsistencyError(u"packets", 0, len(self._m_packets))
            for i in range(len(self._m_packets)):
                pass
                if self._m_packets[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"packets", self._root, self._m_packets[i]._root)
                if self._m_packets[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"packets", self, self._m_packets[i]._parent)


        self._dirty = False

    class EvdHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvdHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.info = Evd.EvdInfo(self._io, self, self._root)
            self.info._read()
            self.offset_pac = self._io.read_u4le()
            self.size_pac = self._io.read_u4le()
            self.num_bin_tbl = self._io.read_u4le()
            self.offst_bin_tbl = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.info._fetch_instances()


        def _write__seq(self, io=None):
            super(Evd.EvdHeader, self)._write__seq(io)
            self.info._write__seq(self._io)
            self._io.write_u4le(self.offset_pac)
            self._io.write_u4le(self.size_pac)
            self._io.write_u4le(self.num_bin_tbl)
            self._io.write_u4le(self.offst_bin_tbl)


        def _check(self):
            if self.info._root != self._root:
                raise kaitaistruct.ConsistencyError(u"info", self._root, self.info._root)
            if self.info._parent != self:
                raise kaitaistruct.ConsistencyError(u"info", self, self.info._parent)
            self._dirty = False


    class EvdInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvdInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name = (self._io.read_bytes(32)).decode(u"UTF-8")
            self.room_no = (self._io.read_bytes(8)).decode(u"UTF-8")
            self.event_no = (self._io.read_bytes(8)).decode(u"UTF-8")
            self.serial_no = self._io.read_u4le()
            self.evd_flag = self._io.read_u4le()
            self.filler = []
            for i in range(2):
                self.filler.append(self._io.read_u4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.filler)):
                pass



        def _write__seq(self, io=None):
            super(Evd.EvdInfo, self)._write__seq(io)
            self._io.write_bytes((self.name).encode(u"UTF-8"))
            self._io.write_bytes((self.room_no).encode(u"UTF-8"))
            self._io.write_bytes((self.event_no).encode(u"UTF-8"))
            self._io.write_u4le(self.serial_no)
            self._io.write_u4le(self.evd_flag)
            for i in range(len(self.filler)):
                pass
                self._io.write_u4le(self.filler[i])



        def _check(self):
            if len((self.name).encode(u"UTF-8")) != 32:
                raise kaitaistruct.ConsistencyError(u"name", 32, len((self.name).encode(u"UTF-8")))
            if len((self.room_no).encode(u"UTF-8")) != 8:
                raise kaitaistruct.ConsistencyError(u"room_no", 8, len((self.room_no).encode(u"UTF-8")))
            if len((self.event_no).encode(u"UTF-8")) != 8:
                raise kaitaistruct.ConsistencyError(u"event_no", 8, len((self.event_no).encode(u"UTF-8")))
            if len(self.filler) != 2:
                raise kaitaistruct.ConsistencyError(u"filler", 2, len(self.filler))
            for i in range(len(self.filler)):
                pass

            self._dirty = False


    class EvpCam(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpCam, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpCam, self)._write__seq(io)
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))


        def _check(self):
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            self._dirty = False


    class EvpCamDammy(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpCamDammy, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.time = self._io.read_u4le()
            self.filler = self._io.read_bytes(12)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpCamDammy, self)._write__seq(io)
            self._io.write_u4le(self.time)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len(self.filler) != 12:
                raise kaitaistruct.ConsistencyError(u"filler", 12, len(self.filler))
            self._dirty = False


    class EvpCamPos(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpCamPos, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.pos = Evd.Vec3(self._io, self, self._root)
            self.pos._read()
            self.ang = Evd.Vec3(self._io, self, self._root)
            self.ang._read()
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.pos._fetch_instances()
            self.ang._fetch_instances()


        def _write__seq(self, io=None):
            super(Evd.EvpCamPos, self)._write__seq(io)
            self.pos._write__seq(self._io)
            self.ang._write__seq(self._io)
            self._io.write_bytes(self.filler)


        def _check(self):
            if self.pos._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pos", self._root, self.pos._root)
            if self.pos._parent != self:
                raise kaitaistruct.ConsistencyError(u"pos", self, self.pos._parent)
            if self.ang._root != self._root:
                raise kaitaistruct.ConsistencyError(u"ang", self._root, self.ang._root)
            if self.ang._parent != self:
                raise kaitaistruct.ConsistencyError(u"ang", self, self.ang._parent)
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpEndEm(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpEndEm, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpEndEm, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpEndList(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpEndList, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpEndList, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpEndOm(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpEndOm, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpEndOm, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpEndParts(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpEndParts, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpEndParts, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpEndPl(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpEndPl, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpEndPl, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpEsp(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpEsp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.kind = KaitaiStream.resolve_enum(Evd.EvtEspKindId, self._io.read_u4le())
            self.id_est = self._io.read_u4le()
            self.filler = self._io.read_bytes(12)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpEsp, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_u4le(int(self.kind))
            self._io.write_u4le(self.id_est)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 12:
                raise kaitaistruct.ConsistencyError(u"filler", 12, len(self.filler))
            self._dirty = False


    class EvpFade(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpFade, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.flat = KaitaiStream.resolve_enum(Evd.EvtFade, self._io.read_u4le())
            self.fade_no = self._io.read_u4le()
            self.timer = self._io.read_u4le()
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpFade, self)._write__seq(io)
            self._io.write_u4le(int(self.flat))
            self._io.write_u4le(self.fade_no)
            self._io.write_u4le(self.timer)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpFocus(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpFocus, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpFocus, self)._write__seq(io)
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))


        def _check(self):
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            self._dirty = False


    class EvpFog(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpFog, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpFog, self)._write__seq(io)
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))


        def _check(self):
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            self._dirty = False


    class EvpFunc(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpFunc, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.no_func = self._io.read_u4le()
            self.param = self._io.read_u4le()
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpFunc, self)._write__seq(io)
            self._io.write_u4le(self.no_func)
            self._io.write_u4le(self.param)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.evp_type = KaitaiStream.resolve_enum(Evd.EvpTp, self._io.read_u4le())
            self.flag_common = self._io.read_u4le()
            self.no_cut = self._io.read_u2le()
            self.frame = self._io.read_u2le()
            self.size = self._io.read_u2le()
            self.no_pack = self._io.read_u2le()
            _on = self.evp_type
            if _on == Evd.EvpTp.evp_tp_cam:
                pass
                self.data = Evd.EvpCam(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_cam_dammy:
                pass
                self.data = Evd.EvpCamDammy(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_cam_pos:
                pass
                self.data = Evd.EvpCamPos(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_end_em:
                pass
                self.data = Evd.EvpEndEm(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_end_list:
                pass
                self.data = Evd.EvpEndList(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_end_om:
                pass
                self.data = Evd.EvpEndOm(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_end_parts:
                pass
                self.data = Evd.EvpEndParts(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_end_pl:
                pass
                self.data = Evd.EvpEndPl(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_esp:
                pass
                self.data = Evd.EvpEsp(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_fade:
                pass
                self.data = Evd.EvpFade(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_focus:
                pass
                self.data = Evd.EvpFocus(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_fog:
                pass
                self.data = Evd.EvpFog(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_func:
                pass
                self.data = Evd.EvpFunc(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_lit:
                pass
                self.data = Evd.EvpLit(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_mes:
                pass
                self.data = Evd.EvpMes(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_mot:
                pass
                self.data = Evd.EvpMot(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_parent_off:
                pass
                self.data = Evd.EvpParentOff(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_parent_on:
                pass
                self.data = Evd.EvpParentOn(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_pos:
                pass
                self.data = Evd.EvpPos(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_pos_pl:
                pass
                self.data = Evd.EvpPosPl(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_se:
                pass
                self.data = Evd.EvpSe(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_eff:
                pass
                self.data = Evd.EvpSetEff(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_em:
                pass
                self.data = Evd.EvpSetEm(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_list:
                pass
                self.data = Evd.EvpSetList(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_mdt:
                pass
                self.data = Evd.EvpSetMdt(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_om:
                pass
                self.data = Evd.EvpSetOm(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_parts:
                pass
                self.data = Evd.EvpSetParts(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_set_pl:
                pass
                self.data = Evd.EvpSetPl(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_shp:
                pass
                self.data = Evd.EvpShp(self._io, self, self._root)
                self.data._read()
            elif _on == Evd.EvpTp.evp_tp_str:
                pass
                self.data = Evd.EvpStr(self._io, self, self._root)
                self.data._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self.evp_type
            if _on == Evd.EvpTp.evp_tp_cam:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_cam_dammy:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_cam_pos:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_end_em:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_end_list:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_end_om:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_end_parts:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_end_pl:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_esp:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_fade:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_focus:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_fog:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_func:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_lit:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_mes:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_mot:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_parent_off:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_parent_on:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_pos:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_pos_pl:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_se:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_eff:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_em:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_list:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_mdt:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_om:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_parts:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_set_pl:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_shp:
                pass
                self.data._fetch_instances()
            elif _on == Evd.EvpTp.evp_tp_str:
                pass
                self.data._fetch_instances()


        def _write__seq(self, io=None):
            super(Evd.EvpHeader, self)._write__seq(io)
            self._io.write_u4le(int(self.evp_type))
            self._io.write_u4le(self.flag_common)
            self._io.write_u2le(self.no_cut)
            self._io.write_u2le(self.frame)
            self._io.write_u2le(self.size)
            self._io.write_u2le(self.no_pack)
            _on = self.evp_type
            if _on == Evd.EvpTp.evp_tp_cam:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_cam_dammy:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_cam_pos:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_end_em:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_end_list:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_end_om:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_end_parts:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_end_pl:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_esp:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_fade:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_focus:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_fog:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_func:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_lit:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_mes:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_mot:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_parent_off:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_parent_on:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_pos:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_pos_pl:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_se:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_eff:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_em:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_list:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_mdt:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_om:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_parts:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_set_pl:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_shp:
                pass
                self.data._write__seq(self._io)
            elif _on == Evd.EvpTp.evp_tp_str:
                pass
                self.data._write__seq(self._io)


        def _check(self):
            _on = self.evp_type
            if _on == Evd.EvpTp.evp_tp_cam:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_cam_dammy:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_cam_pos:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_end_em:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_end_list:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_end_om:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_end_parts:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_end_pl:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_esp:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_fade:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_focus:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_fog:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_func:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_lit:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_mes:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_mot:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_parent_off:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_parent_on:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_pos:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_pos_pl:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_se:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_eff:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_em:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_list:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_mdt:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_om:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_parts:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_set_pl:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_shp:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == Evd.EvpTp.evp_tp_str:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            self._dirty = False


    class EvpLit(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpLit, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpLit, self)._write__seq(io)
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))


        def _check(self):
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            self._dirty = False


    class EvpMes(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpMes, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.no_mes = self._io.read_u4le()
            self.timer = self._io.read_u4le()
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpMes, self)._write__seq(io)
            self._io.write_u4le(self.no_mes)
            self._io.write_u4le(self.timer)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpMot(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpMot, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpMot, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpParentOff(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpParentOff, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpParentOff, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpParentOn(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpParentOn, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_oya = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpParentOn, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes((self.name_oya).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len((self.name_oya).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_oya", 12, len((self.name_oya).encode(u"UTF-8")))
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpPos(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpPos, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_oya = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.pos = Evd.Vec3(self._io, self, self._root)
            self.pos._read()
            self.ang = Evd.Vec3(self._io, self, self._root)
            self.ang._read()
            self.parts_no = self._io.read_u4le()
            self.filler = self._io.read_bytes(12)
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.pos._fetch_instances()
            self.ang._fetch_instances()


        def _write__seq(self, io=None):
            super(Evd.EvpPos, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes((self.name_oya).encode(u"UTF-8"))
            self.pos._write__seq(self._io)
            self.ang._write__seq(self._io)
            self._io.write_u4le(self.parts_no)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len((self.name_oya).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_oya", 12, len((self.name_oya).encode(u"UTF-8")))
            if self.pos._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pos", self._root, self.pos._root)
            if self.pos._parent != self:
                raise kaitaistruct.ConsistencyError(u"pos", self, self.pos._parent)
            if self.ang._root != self._root:
                raise kaitaistruct.ConsistencyError(u"ang", self._root, self.ang._root)
            if self.ang._parent != self:
                raise kaitaistruct.ConsistencyError(u"ang", self, self.ang._parent)
            if len(self.filler) != 12:
                raise kaitaistruct.ConsistencyError(u"filler", 12, len(self.filler))
            self._dirty = False


    class EvpPosPl(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpPosPl, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpPosPl, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpSe(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSe, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.no_tar = self._io.read_u4le()
            self.no_se = self._io.read_u4le()
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSe, self)._write__seq(io)
            self._io.write_u4le(self.no_tar)
            self._io.write_u4le(self.no_se)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpSetEff(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetEff, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetEff, self)._write__seq(io)
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))


        def _check(self):
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            self._dirty = False


    class EvpSetEm(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetEm, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetEm, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpSetList(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetList, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.no_list = self._io.read_u4le()
            self.filler = self._io.read_bytes(1)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetList, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_u4le(self.no_list)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 1:
                raise kaitaistruct.ConsistencyError(u"filler", 1, len(self.filler))
            self._dirty = False


    class EvpSetMdt(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetMdt, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetMdt, self)._write__seq(io)
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))


        def _check(self):
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            self._dirty = False


    class EvpSetOm(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetOm, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.name_tpl = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetOm, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))
            self._io.write_bytes((self.name_tpl).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            if len((self.name_tpl).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_tpl", 48, len((self.name_tpl).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpSetParts(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetParts, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_oya = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.name_tpl = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetParts, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes((self.name_oya).encode(u"UTF-8"))
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))
            self._io.write_bytes((self.name_tpl).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len((self.name_oya).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_oya", 12, len((self.name_oya).encode(u"UTF-8")))
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            if len((self.name_tpl).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_tpl", 48, len((self.name_tpl).encode(u"UTF-8")))
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class EvpSetPl(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpSetPl, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpSetPl, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpShp(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpShp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.name_mod = (self._io.read_bytes(12)).decode(u"UTF-8")
            self.name_bin = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.filler = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpShp, self)._write__seq(io)
            self._io.write_bytes((self.name_mod).encode(u"UTF-8"))
            self._io.write_bytes((self.name_bin).encode(u"UTF-8"))
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_mod).encode(u"UTF-8")) != 12:
                raise kaitaistruct.ConsistencyError(u"name_mod", 12, len((self.name_mod).encode(u"UTF-8")))
            if len((self.name_bin).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_bin", 48, len((self.name_bin).encode(u"UTF-8")))
            if len(self.filler) != 4:
                raise kaitaistruct.ConsistencyError(u"filler", 4, len(self.filler))
            self._dirty = False


    class EvpStr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.EvpStr, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.no_tar = self._io.read_u4le()
            self.no_str = self._io.read_u4le()
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Evd.EvpStr, self)._write__seq(io)
            self._io.write_u4le(self.no_tar)
            self._io.write_u4le(self.no_str)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            self._dirty = False


    class FileEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.FileEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_raw_data = False
            self.raw_data__enabled = True

        def _read(self):
            self.name_file = (self._io.read_bytes(48)).decode(u"UTF-8")
            self.offset = self._io.read_u4le()
            self.size = self._io.read_u4le()
            self.filler = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.raw_data
            if hasattr(self, '_m_raw_data'):
                pass



        def _write__seq(self, io=None):
            super(Evd.FileEntry, self)._write__seq(io)
            self._should_write_raw_data = self.raw_data__enabled
            self._io.write_bytes((self.name_file).encode(u"UTF-8"))
            self._io.write_u4le(self.offset)
            self._io.write_u4le(self.size)
            self._io.write_bytes(self.filler)


        def _check(self):
            if len((self.name_file).encode(u"UTF-8")) != 48:
                raise kaitaistruct.ConsistencyError(u"name_file", 48, len((self.name_file).encode(u"UTF-8")))
            if len(self.filler) != 8:
                raise kaitaistruct.ConsistencyError(u"filler", 8, len(self.filler))
            if self.raw_data__enabled:
                pass
                if len(self._m_raw_data) != self.size:
                    raise kaitaistruct.ConsistencyError(u"raw_data", self.size, len(self._m_raw_data))

            self._dirty = False

        @property
        def raw_data(self):
            if self._should_write_raw_data:
                self._write_raw_data()
            if hasattr(self, '_m_raw_data'):
                return self._m_raw_data

            if not self.raw_data__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_raw_data = self._io.read_bytes(self.size)
            self._io.seek(_pos)
            return getattr(self, '_m_raw_data', None)

        @raw_data.setter
        def raw_data(self, v):
            self._dirty = True
            self._m_raw_data = v

        def _write_raw_data(self):
            self._should_write_raw_data = False
            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._io.write_bytes(self._m_raw_data)
            self._io.seek(_pos)


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Evd.Vec3, self).__init__(_io)
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
            super(Evd.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    @property
    def file_entries(self):
        if self._should_write_file_entries:
            self._write_file_entries()
        if hasattr(self, '_m_file_entries'):
            return self._m_file_entries

        if not self.file_entries__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offst_bin_tbl)
        self._m_file_entries = []
        for i in range(self.header.num_bin_tbl):
            _t__m_file_entries = Evd.FileEntry(self._io, self, self._root)
            try:
                _t__m_file_entries._read()
            finally:
                self._m_file_entries.append(_t__m_file_entries)

        self._io.seek(_pos)
        return getattr(self, '_m_file_entries', None)

    @file_entries.setter
    def file_entries(self, v):
        self._dirty = True
        self._m_file_entries = v

    def _write_file_entries(self):
        self._should_write_file_entries = False
        _pos = self._io.pos()
        self._io.seek(self.header.offst_bin_tbl)
        for i in range(len(self._m_file_entries)):
            pass
            self._m_file_entries[i]._write__seq(self._io)

        self._io.seek(_pos)

    @property
    def packets(self):
        if self._should_write_packets:
            self._write_packets()
        if hasattr(self, '_m_packets'):
            return self._m_packets

        if not self.packets__enabled:
            return None

        _pos = self._io.pos()
        self._io.seek(self.header.offset_pac)
        self._m_packets = []
        i = 0
        while True:
            _t__m_packets = Evd.EvpHeader(self._io, self, self._root)
            try:
                _t__m_packets._read()
            finally:
                _ = _t__m_packets
                self._m_packets.append(_)
            if self._io.pos() >= self.header.offset_pac + self.header.size_pac:
                break
            i += 1
        self._io.seek(_pos)
        return getattr(self, '_m_packets', None)

    @packets.setter
    def packets(self, v):
        self._dirty = True
        self._m_packets = v

    def _write_packets(self):
        self._should_write_packets = False
        _pos = self._io.pos()
        self._io.seek(self.header.offset_pac)
        for i in range(len(self._m_packets)):
            pass
            self._m_packets[i]._write__seq(self._io)
            _ = self._m_packets[i]
            if (self._io.pos() >= self.header.offset_pac + self.header.size_pac) != (i == len(self._m_packets) - 1):
                raise kaitaistruct.ConsistencyError(u"packets", i == len(self._m_packets) - 1, self._io.pos() >= self.header.offset_pac + self.header.size_pac)

        self._io.seek(_pos)


