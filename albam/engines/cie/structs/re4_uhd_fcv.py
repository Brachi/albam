# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Re4UhdFcv(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Re4UhdFcv, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.max_frame_raw = self._io.read_u2le()
        self.num_joints = self._io.read_u1()
        self.joint_infos = []
        for i in range(self.num_joints):
            _t_joint_infos = Re4UhdFcv.JointInfo(self._io, self, self._root)
            try:
                _t_joint_infos._read()
            finally:
                self.joint_infos.append(_t_joint_infos)

        self.parts_nos = []
        for i in range(self.num_joints):
            self.parts_nos.append(self._io.read_u1())

        self.padding = self._io.read_bytes((4 - (3 + 3 * self.num_joints) % 4) % 4)
        self.size = self._io.read_u4be()
        self.key_offsets = []
        for i in range(self.num_joints):
            self.key_offsets.append(self._io.read_u4le())

        self.joints = []
        for i in range(self.num_joints):
            _t_joints = Re4UhdFcv.Joint(i, self._io, self, self._root)
            try:
                _t_joints._read()
            finally:
                self.joints.append(_t_joints)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.joint_infos)):
            pass
            self.joint_infos[i]._fetch_instances()

        for i in range(len(self.parts_nos)):
            pass

        for i in range(len(self.key_offsets)):
            pass

        for i in range(len(self.joints)):
            pass
            self.joints[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Re4UhdFcv, self)._write__seq(io)
        self._io.write_u2le(self.max_frame_raw)
        self._io.write_u1(self.num_joints)
        for i in range(len(self.joint_infos)):
            pass
            self.joint_infos[i]._write__seq(self._io)

        for i in range(len(self.parts_nos)):
            pass
            self._io.write_u1(self.parts_nos[i])

        self._io.write_bytes(self.padding)
        self._io.write_u4be(self.size)
        for i in range(len(self.key_offsets)):
            pass
            self._io.write_u4le(self.key_offsets[i])

        for i in range(len(self.joints)):
            pass
            self.joints[i]._write__seq(self._io)



    def _check(self):
        if len(self.joint_infos) != self.num_joints:
            raise kaitaistruct.ConsistencyError(u"joint_infos", self.num_joints, len(self.joint_infos))
        for i in range(len(self.joint_infos)):
            pass
            if self.joint_infos[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"joint_infos", self._root, self.joint_infos[i]._root)
            if self.joint_infos[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"joint_infos", self, self.joint_infos[i]._parent)

        if len(self.parts_nos) != self.num_joints:
            raise kaitaistruct.ConsistencyError(u"parts_nos", self.num_joints, len(self.parts_nos))
        for i in range(len(self.parts_nos)):
            pass

        if len(self.padding) != (4 - (3 + 3 * self.num_joints) % 4) % 4:
            raise kaitaistruct.ConsistencyError(u"padding", (4 - (3 + 3 * self.num_joints) % 4) % 4, len(self.padding))
        if len(self.key_offsets) != self.num_joints:
            raise kaitaistruct.ConsistencyError(u"key_offsets", self.num_joints, len(self.key_offsets))
        for i in range(len(self.key_offsets)):
            pass

        if len(self.joints) != self.num_joints:
            raise kaitaistruct.ConsistencyError(u"joints", self.num_joints, len(self.joints))
        for i in range(len(self.joints)):
            pass
            if self.joints[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"joints", self._root, self.joints[i]._root)
            if self.joints[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"joints", self, self.joints[i]._parent)
            if self.joints[i].i != i:
                raise kaitaistruct.ConsistencyError(u"joints", i, self.joints[i].i)

        self._dirty = False

    class Axis(ReadWriteKaitaiStruct):
        def __init__(self, key_type, _io=None, _parent=None, _root=None):
            super(Re4UhdFcv.Axis, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.key_type = key_type

        def _read(self):
            self.num_keys = self._io.read_u2le()
            self.frames = []
            for i in range(self.num_keys):
                self.frames.append(self._io.read_u2le())

            self.keys = []
            for i in range(self.num_keys):
                _t_keys = Re4UhdFcv.Key(self.key_type, self._io, self, self._root)
                try:
                    _t_keys._read()
                finally:
                    self.keys.append(_t_keys)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.frames)):
                pass

            for i in range(len(self.keys)):
                pass
                self.keys[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Re4UhdFcv.Axis, self)._write__seq(io)
            self._io.write_u2le(self.num_keys)
            for i in range(len(self.frames)):
                pass
                self._io.write_u2le(self.frames[i])

            for i in range(len(self.keys)):
                pass
                self.keys[i]._write__seq(self._io)



        def _check(self):
            if len(self.frames) != self.num_keys:
                raise kaitaistruct.ConsistencyError(u"frames", self.num_keys, len(self.frames))
            for i in range(len(self.frames)):
                pass

            if len(self.keys) != self.num_keys:
                raise kaitaistruct.ConsistencyError(u"keys", self.num_keys, len(self.keys))
            for i in range(len(self.keys)):
                pass
                if self.keys[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"keys", self._root, self.keys[i]._root)
                if self.keys[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"keys", self, self.keys[i]._parent)
                if self.keys[i].key_type != self.key_type:
                    raise kaitaistruct.ConsistencyError(u"keys", self.key_type, self.keys[i].key_type)

            self._dirty = False


    class Joint(ReadWriteKaitaiStruct):
        def __init__(self, i, _io=None, _parent=None, _root=None):
            super(Re4UhdFcv.Joint, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.i = i
            self._should_write_axes = False
            self.axes__enabled = True

        def _read(self):
            pass
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.axes
            if hasattr(self, '_m_axes'):
                pass
                for i in range(len(self._m_axes)):
                    pass
                    self._m_axes[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Re4UhdFcv.Joint, self)._write__seq(io)
            self._should_write_axes = self.axes__enabled


        def _check(self):
            if self.axes__enabled:
                pass
                if len(self._m_axes) != 3:
                    raise kaitaistruct.ConsistencyError(u"axes", 3, len(self._m_axes))
                for i in range(len(self._m_axes)):
                    pass
                    if self._m_axes[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"axes", self._root, self._m_axes[i]._root)
                    if self._m_axes[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"axes", self, self._m_axes[i]._parent)
                    if self._m_axes[i].key_type != self.info.key_type:
                        raise kaitaistruct.ConsistencyError(u"axes", self.info.key_type, self._m_axes[i].key_type)


            self._dirty = False

        @property
        def axes(self):
            if self._should_write_axes:
                self._write_axes()
            if hasattr(self, '_m_axes'):
                return self._m_axes

            if not self.axes__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self._parent.key_offsets[self.i])
            self._m_axes = []
            for i in range(3):
                _t__m_axes = Re4UhdFcv.Axis(self.info.key_type, self._io, self, self._root)
                try:
                    _t__m_axes._read()
                finally:
                    self._m_axes.append(_t__m_axes)

            self._io.seek(_pos)
            return getattr(self, '_m_axes', None)

        @axes.setter
        def axes(self, v):
            self._dirty = True
            self._m_axes = v

        def _write_axes(self):
            self._should_write_axes = False
            _pos = self._io.pos()
            self._io.seek(self._parent.key_offsets[self.i])
            for i in range(len(self._m_axes)):
                pass
                self._m_axes[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def info(self):
            if hasattr(self, '_m_info'):
                return self._m_info

            self._m_info = self._parent.joint_infos[self.i]
            return getattr(self, '_m_info', None)

        def _invalidate_info(self):
            del self._m_info
        @property
        def parts_no(self):
            if hasattr(self, '_m_parts_no'):
                return self._m_parts_no

            self._m_parts_no = self._parent.parts_nos[self.i]
            return getattr(self, '_m_parts_no', None)

        def _invalidate_parts_no(self):
            del self._m_parts_no

    class JointInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Re4UhdFcv.JointInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.raw = self._io.read_u2le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Re4UhdFcv.JointInfo, self)._write__seq(io)
            self._io.write_u2le(self.raw)


        def _check(self):
            self._dirty = False

        @property
        def channel(self):
            if hasattr(self, '_m_channel'):
                return self._m_channel

            self._m_channel = self.raw >> 8 & 15
            return getattr(self, '_m_channel', None)

        def _invalidate_channel(self):
            del self._m_channel
        @property
        def is_camera(self):
            if hasattr(self, '_m_is_camera'):
                return self._m_is_camera

            self._m_is_camera =  ((self.channel == 6) or (self.channel == 7)) 
            return getattr(self, '_m_is_camera', None)

        def _invalidate_is_camera(self):
            del self._m_is_camera
        @property
        def is_ik_root(self):
            if hasattr(self, '_m_is_ik_root'):
                return self._m_is_ik_root

            self._m_is_ik_root = self.kind & 48 != 0
            return getattr(self, '_m_is_ik_root', None)

        def _invalidate_is_ik_root(self):
            del self._m_is_ik_root
        @property
        def key_type(self):
            if hasattr(self, '_m_key_type'):
                return self._m_key_type

            self._m_key_type = self.raw >> 12
            return getattr(self, '_m_key_type', None)

        def _invalidate_key_type(self):
            del self._m_key_type
        @property
        def kind(self):
            if hasattr(self, '_m_kind'):
                return self._m_kind

            self._m_kind = self.raw & 255
            return getattr(self, '_m_kind', None)

        def _invalidate_kind(self):
            del self._m_kind

    class Key(ReadWriteKaitaiStruct):
        def __init__(self, key_type, _io=None, _parent=None, _root=None):
            super(Re4UhdFcv.Key, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.key_type = key_type

        def _read(self):
            _on = self.key_type >> 2
            if _on == 1:
                pass
                self.value_raw = self._io.read_s2le()
            elif _on == 2:
                pass
                self.value_raw = self._io.read_s1()
            else:
                pass
                self.value_raw = self._io.read_f4le()
            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                    self.in_tangent_raw = self._io.read_s2le()
                elif _on == 2:
                    pass
                    self.in_tangent_raw = self._io.read_s1()
                else:
                    pass
                    self.in_tangent_raw = self._io.read_f4le()

            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                    self.out_tangent_raw = self._io.read_s2le()
                elif _on == 2:
                    pass
                    self.out_tangent_raw = self._io.read_s1()
                else:
                    pass
                    self.out_tangent_raw = self._io.read_f4le()

            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self.key_type >> 2
            if _on == 1:
                pass
            elif _on == 2:
                pass
            else:
                pass
            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                elif _on == 2:
                    pass
                else:
                    pass

            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                elif _on == 2:
                    pass
                else:
                    pass



        def _write__seq(self, io=None):
            super(Re4UhdFcv.Key, self)._write__seq(io)
            _on = self.key_type >> 2
            if _on == 1:
                pass
                self._io.write_s2le(self.value_raw)
            elif _on == 2:
                pass
                self._io.write_s1(self.value_raw)
            else:
                pass
                self._io.write_f4le(self.value_raw)
            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                    self._io.write_s2le(self.in_tangent_raw)
                elif _on == 2:
                    pass
                    self._io.write_s1(self.in_tangent_raw)
                else:
                    pass
                    self._io.write_f4le(self.in_tangent_raw)

            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                    self._io.write_s2le(self.out_tangent_raw)
                elif _on == 2:
                    pass
                    self._io.write_s1(self.out_tangent_raw)
                else:
                    pass
                    self._io.write_f4le(self.out_tangent_raw)



        def _check(self):
            _on = self.key_type >> 2
            if _on == 1:
                pass
            elif _on == 2:
                pass
            else:
                pass
            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                elif _on == 2:
                    pass
                else:
                    pass

            if self.key_type != 15:
                pass
                _on = self.key_type & 3
                if _on == 1:
                    pass
                elif _on == 2:
                    pass
                else:
                    pass

            self._dirty = False

        @property
        def in_tangent(self):
            if hasattr(self, '_m_in_tangent'):
                return self._m_in_tangent

            self._m_in_tangent = (0.0 if self.key_type == 15 else (self.in_tangent_raw if self.key_type & 3 == 0 else self.in_tangent_raw * 0.0001))
            return getattr(self, '_m_in_tangent', None)

        def _invalidate_in_tangent(self):
            del self._m_in_tangent
        @property
        def out_tangent(self):
            if hasattr(self, '_m_out_tangent'):
                return self._m_out_tangent

            self._m_out_tangent = (0.0 if self.key_type == 15 else (self.out_tangent_raw if self.key_type & 3 == 0 else self.out_tangent_raw * 0.0001))
            return getattr(self, '_m_out_tangent', None)

        def _invalidate_out_tangent(self):
            del self._m_out_tangent
        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.value_raw if  ((self.key_type >> 2 == 0) or (self.key_type >> 2 == 3))  else self.value_raw * 0.0001)
            return getattr(self, '_m_value', None)

        def _invalidate_value(self):
            del self._m_value

    @property
    def max_frame(self):
        if hasattr(self, '_m_max_frame'):
            return self._m_max_frame

        self._m_max_frame = self.max_frame_raw & 16383
        return getattr(self, '_m_max_frame', None)

    def _invalidate_max_frame(self):
        del self._m_max_frame

