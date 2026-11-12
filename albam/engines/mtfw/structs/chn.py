# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Chn(ReadWriteKaitaiStruct):
    """Chain (cloth / hair "chain" simulation) resource of the older MT Framework
    generation: Resident Evil 5 and DMC4 Special Edition (both expose
    rChain::getExt -> "chn").  DMC4 (2008) does not have this class - its cloth
    chain is rCnsChain, extension "clt".
    
      rChain::Header      0x10  magic, version, data_size, chain_info_num, reserve[3]
      rChain::ChainInfo   0x20  joint_info_num, chain_type, reserve, joint_info_offset,
                                      reserve1[2], grav_scaler, time_scaler, dump_scaler, freserve
      rChain::JointInfo   0x60  attr, ref_joint_no, node_num, reserve0, reserve1[2],
                                      min_angle, spring_coef, max_angle, dumping_coef, mass,
                                      restrict_flag, col_shape, reserve2[2], col_radius,
                                      air_regist, node_joint_no[8], friction, soft_coef,
                                      bend_regist, reserve[3]
    
    rChain::DATA_VERSION = 0x80618 (rChain::load compares the header version with
    it).  rChain::load reads 16 header bytes, allocates data_size bytes and reads
    them; getExt returns "chn".
    
    Layout: the 16-byte header is followed by a table of chain_info_num ChainInfo
    records (32 bytes each, all of them first), then the JointInfo records
    (96 bytes each).  A chain's joints start at
    
        chain_info_position + joint_info_offset      (chain_info_position = 16 + 32 * index)
    
    and data_size = 32 * chain_info_num + 96 * sum(joint_info_num).
    File size = 16 + data_size
    """

    class ChainType(IntEnum):
        chain = 1
        shake = 2

    class ColShape(IntEnum):
        sphere = 1
        capsule = 2
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Chn, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x43\x48\x4E\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x43\x48\x4E\x00", self.magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        if not self.version == 525848:
            raise kaitaistruct.ValidationNotEqualError(525848, self.version, self._io, u"/seq/1")
        self.data_size = self._io.read_u4le()
        self.num_chain_infos = self._io.read_u1()
        self.reserve = self._io.read_bytes(3)
        self.chain_infos = []
        for i in range(self.num_chain_infos):
            _t_chain_infos = Chn.ChainInfo(i, self._io, self, self._root)
            try:
                _t_chain_infos._read()
            finally:
                self.chain_infos.append(_t_chain_infos)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.chain_infos)):
            pass
            self.chain_infos[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Chn, self)._write__seq(io)
        self._io.write_bytes(self.magic)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.data_size)
        self._io.write_u1(self.num_chain_infos)
        self._io.write_bytes(self.reserve)
        for i in range(len(self.chain_infos)):
            pass
            self.chain_infos[i]._write__seq(self._io)



    def _check(self):
        if len(self.magic) != 4:
            raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
        if not self.magic == b"\x43\x48\x4E\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x43\x48\x4E\x00", self.magic, None, u"/seq/0")
        if not self.version == 525848:
            raise kaitaistruct.ValidationNotEqualError(525848, self.version, None, u"/seq/1")
        if len(self.reserve) != 3:
            raise kaitaistruct.ConsistencyError(u"reserve", 3, len(self.reserve))
        if len(self.chain_infos) != self.num_chain_infos:
            raise kaitaistruct.ConsistencyError(u"chain_infos", self.num_chain_infos, len(self.chain_infos))
        for i in range(len(self.chain_infos)):
            pass
            if self.chain_infos[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"chain_infos", self._root, self.chain_infos[i]._root)
            if self.chain_infos[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"chain_infos", self, self.chain_infos[i]._parent)
            if self.chain_infos[i].index != i:
                raise kaitaistruct.ConsistencyError(u"chain_infos", i, self.chain_infos[i].index)

        self._dirty = False

    class ChainInfo(ReadWriteKaitaiStruct):
        """joint_info_offset is relative to the start of this ChainInfo record, so the
        joints of chain `i` live at 16 + 32 * i + joint_info_offset.
        """
        def __init__(self, index, _io=None, _parent=None, _root=None):
            super(Chn.ChainInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.index = index
            self._should_write_joints = False
            self.joints__enabled = True

        def _read(self):
            self.num_joints = self._io.read_u1()
            self.chain_type = KaitaiStream.resolve_enum(Chn.ChainType, self._io.read_u1())
            self.reserve = self._io.read_u2le()
            self.joint_info_offset = self._io.read_u4le()
            self.reserve1 = []
            for i in range(2):
                self.reserve1.append(self._io.read_u4le())

            self.grav_scaler = self._io.read_f4le()
            self.time_scaler = self._io.read_f4le()
            self.dump_scaler = self._io.read_f4le()
            self.freserve = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.reserve1)):
                pass

            _ = self.joints
            if hasattr(self, '_m_joints'):
                pass
                for i in range(len(self._m_joints)):
                    pass
                    self._m_joints[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Chn.ChainInfo, self)._write__seq(io)
            self._should_write_joints = self.joints__enabled
            self._io.write_u1(self.num_joints)
            self._io.write_u1(int(self.chain_type))
            self._io.write_u2le(self.reserve)
            self._io.write_u4le(self.joint_info_offset)
            for i in range(len(self.reserve1)):
                pass
                self._io.write_u4le(self.reserve1[i])

            self._io.write_f4le(self.grav_scaler)
            self._io.write_f4le(self.time_scaler)
            self._io.write_f4le(self.dump_scaler)
            self._io.write_f4le(self.freserve)


        def _check(self):
            if len(self.reserve1) != 2:
                raise kaitaistruct.ConsistencyError(u"reserve1", 2, len(self.reserve1))
            for i in range(len(self.reserve1)):
                pass

            if self.joints__enabled:
                pass
                if len(self._m_joints) != self.num_joints:
                    raise kaitaistruct.ConsistencyError(u"joints", self.num_joints, len(self._m_joints))
                for i in range(len(self._m_joints)):
                    pass
                    if self._m_joints[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"joints", self._root, self._m_joints[i]._root)
                    if self._m_joints[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"joints", self, self._m_joints[i]._parent)


            self._dirty = False

        @property
        def joints(self):
            if self._should_write_joints:
                self._write_joints()
            if hasattr(self, '_m_joints'):
                return self._m_joints

            if not self.joints__enabled:
                return None

            _pos = self._io.pos()
            self._io.seek(self.joints_pos)
            self._m_joints = []
            for i in range(self.num_joints):
                _t__m_joints = Chn.JointInfo(self._io, self, self._root)
                try:
                    _t__m_joints._read()
                finally:
                    self._m_joints.append(_t__m_joints)

            self._io.seek(_pos)
            return getattr(self, '_m_joints', None)

        @joints.setter
        def joints(self, v):
            self._dirty = True
            self._m_joints = v

        def _write_joints(self):
            self._should_write_joints = False
            _pos = self._io.pos()
            self._io.seek(self.joints_pos)
            for i in range(len(self._m_joints)):
                pass
                self._m_joints[i]._write__seq(self._io)

            self._io.seek(_pos)

        @property
        def joints_pos(self):
            if hasattr(self, '_m_joints_pos'):
                return self._m_joints_pos

            self._m_joints_pos = self.position + self.joint_info_offset
            return getattr(self, '_m_joints_pos', None)

        def _invalidate_joints_pos(self):
            del self._m_joints_pos
        @property
        def position(self):
            if hasattr(self, '_m_position'):
                return self._m_position

            self._m_position = 16 + 32 * self.index
            return getattr(self, '_m_position', None)

        def _invalidate_position(self):
            del self._m_position

    class JointInfo(ReadWriteKaitaiStruct):
        """attr is a bit set of JOINT_ATTRIBUTE (1 constraint, 2 attached, 4 no rotate);
        col_shape is a JOINT_COL_SHAPE (1 sphere, 2 capsule).  node_joint_no holds
        up to JOINT_NODE_MAX (8) bone ids of the nodes this joint drags, node_num is
        how many of them are used.  min_angle / max_angle are the angle limits.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Chn.JointInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.attr = self._io.read_u4le()
            self.ref_joint_no = self._io.read_u2le()
            self.node_num = self._io.read_u1()
            self.reserve0 = self._io.read_u1()
            self.reserve1 = []
            for i in range(2):
                self.reserve1.append(self._io.read_u4le())

            self.min_angle = Chn.Vec3(self._io, self, self._root)
            self.min_angle._read()
            self.spring_coef = self._io.read_f4le()
            self.max_angle = Chn.Vec3(self._io, self, self._root)
            self.max_angle._read()
            self.dumping_coef = self._io.read_f4le()
            self.mass = self._io.read_f4le()
            self.restrict_flag = self._io.read_u1()
            self.col_shape = KaitaiStream.resolve_enum(Chn.ColShape, self._io.read_u1())
            self.reserve2 = self._io.read_bytes(2)
            self.col_radius = self._io.read_f4le()
            self.air_regist = self._io.read_f4le()
            self.node_joint_no = []
            for i in range(8):
                self.node_joint_no.append(self._io.read_u1())

            self.friction = self._io.read_f4le()
            self.soft_coef = self._io.read_f4le()
            self.bend_regist = self._io.read_f4le()
            self.reserve = []
            for i in range(3):
                self.reserve.append(self._io.read_u4le())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.reserve1)):
                pass

            self.min_angle._fetch_instances()
            self.max_angle._fetch_instances()
            for i in range(len(self.node_joint_no)):
                pass

            for i in range(len(self.reserve)):
                pass



        def _write__seq(self, io=None):
            super(Chn.JointInfo, self)._write__seq(io)
            self._io.write_u4le(self.attr)
            self._io.write_u2le(self.ref_joint_no)
            self._io.write_u1(self.node_num)
            self._io.write_u1(self.reserve0)
            for i in range(len(self.reserve1)):
                pass
                self._io.write_u4le(self.reserve1[i])

            self.min_angle._write__seq(self._io)
            self._io.write_f4le(self.spring_coef)
            self.max_angle._write__seq(self._io)
            self._io.write_f4le(self.dumping_coef)
            self._io.write_f4le(self.mass)
            self._io.write_u1(self.restrict_flag)
            self._io.write_u1(int(self.col_shape))
            self._io.write_bytes(self.reserve2)
            self._io.write_f4le(self.col_radius)
            self._io.write_f4le(self.air_regist)
            for i in range(len(self.node_joint_no)):
                pass
                self._io.write_u1(self.node_joint_no[i])

            self._io.write_f4le(self.friction)
            self._io.write_f4le(self.soft_coef)
            self._io.write_f4le(self.bend_regist)
            for i in range(len(self.reserve)):
                pass
                self._io.write_u4le(self.reserve[i])



        def _check(self):
            if len(self.reserve1) != 2:
                raise kaitaistruct.ConsistencyError(u"reserve1", 2, len(self.reserve1))
            for i in range(len(self.reserve1)):
                pass

            if self.min_angle._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min_angle", self._root, self.min_angle._root)
            if self.min_angle._parent != self:
                raise kaitaistruct.ConsistencyError(u"min_angle", self, self.min_angle._parent)
            if self.max_angle._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max_angle", self._root, self.max_angle._root)
            if self.max_angle._parent != self:
                raise kaitaistruct.ConsistencyError(u"max_angle", self, self.max_angle._parent)
            if len(self.reserve2) != 2:
                raise kaitaistruct.ConsistencyError(u"reserve2", 2, len(self.reserve2))
            if len(self.node_joint_no) != 8:
                raise kaitaistruct.ConsistencyError(u"node_joint_no", 8, len(self.node_joint_no))
            for i in range(len(self.node_joint_no)):
                pass

            if len(self.reserve) != 3:
                raise kaitaistruct.ConsistencyError(u"reserve", 3, len(self.reserve))
            for i in range(len(self.reserve)):
                pass

            self._dirty = False


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Chn.Vec3, self).__init__(_io)
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
            super(Chn.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    @property
    def expected_size(self):
        if hasattr(self, '_m_expected_size'):
            return self._m_expected_size

        self._m_expected_size = 16 + self.data_size
        return getattr(self, '_m_expected_size', None)

    def _invalidate_expected_size(self):
        del self._m_expected_size

