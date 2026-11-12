# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ccl156(ReadWriteKaitaiStruct):
    """Chain collision resource: a table of collision primitives, each bound to one
    or two bones of the skeleton
    
      rChainCol / nChain           : cResource
      rChainCol::Header / nChain   : magic, version, colinfo_num, data_size   (0x10)
      rChainCol::ColInfo           : 0x40 = 64 bytes per collision
      nChain::ColInfo              : same fields, offsets 0x00..0x3c
      rChainCol::DATA_VERSION      : 0x80618
    
    The old version of this template read 68 bytes per record (an extra u4 after
    the 12 "payload" values), which shifts every record after the first one and
    overruns the file.  The record is 64 bytes:
    
      0x00 u4 attr             0x04 u2 ref_joint_no    0x06 u2 pair_joint_no
      0x08 u1 shape            0x09 3 bytes reserve    0x0c f4 reserve1
      0x10 f3 position         0x1c u4 id              0x20 f3 extent
      0x2c f4 radius           0x30 f3 angle           0x3c f4 reserve2
    
    Units: centimetres, angles in radians.  File size = 16 + 64 * colinfo_num and
    the header's data_size is 64 * colinfo_num.
    """

    class Shape(IntEnum):
        sphere = 0
        capsule = 1
        aabb = 2
        obb = 3
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Ccl156, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x43\x43\x4C\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x43\x43\x4C\x00", self.magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        if not self.version == 525848:
            raise kaitaistruct.ValidationNotEqualError(525848, self.version, self._io, u"/seq/1")
        self.num_col_infos = self._io.read_u4le()
        self.data_size = self._io.read_u4le()
        self.col_infos = []
        for i in range(self.num_col_infos):
            _t_col_infos = Ccl156.ColInfo(self._io, self, self._root)
            try:
                _t_col_infos._read()
            finally:
                self.col_infos.append(_t_col_infos)

        self._dirty = False


    def _fetch_instances(self):
        pass
        for i in range(len(self.col_infos)):
            pass
            self.col_infos[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Ccl156, self)._write__seq(io)
        self._io.write_bytes(self.magic)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.num_col_infos)
        self._io.write_u4le(self.data_size)
        for i in range(len(self.col_infos)):
            pass
            self.col_infos[i]._write__seq(self._io)



    def _check(self):
        if len(self.magic) != 4:
            raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
        if not self.magic == b"\x43\x43\x4C\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x43\x43\x4C\x00", self.magic, None, u"/seq/0")
        if not self.version == 525848:
            raise kaitaistruct.ValidationNotEqualError(525848, self.version, None, u"/seq/1")
        if len(self.col_infos) != self.num_col_infos:
            raise kaitaistruct.ConsistencyError(u"col_infos", self.num_col_infos, len(self.col_infos))
        for i in range(len(self.col_infos)):
            pass
            if self.col_infos[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"col_infos", self._root, self.col_infos[i]._root)
            if self.col_infos[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"col_infos", self, self.col_infos[i]._parent)

        self._dirty = False

    class ColInfo(ReadWriteKaitaiStruct):
        """ref_joint_no is the bone function id of the .mod bone table; pair_joint_no
        is the second bone for a capsule, otherwise NO_REF_PAIRJOINT (the enum
        declares 0xfff, retail files write 0xffff).
        
        position / extent / radius / angle are in the bone's local space:
          sphere  (0): position = centre, radius = radius
          capsule (1): position = head, extent = tail, radius = radius
          aabb    (2): position = centre, extent = half size
          obb     (3): position = centre, extent = half size, angle = rotation
        In many sphere records extent is (1,1,1) or (0,0,0), so for spheres its
        meaning is not certain.
        
        The game does not write reserve / reserve1 / reserve2: retail files hold
        0xcd filler, zeroes or leftover heap bytes there.  Keep them as is.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Ccl156.ColInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.attr = self._io.read_u4le()
            self.ref_joint_no = self._io.read_u2le()
            self.pair_joint_no = self._io.read_u2le()
            self.shape = KaitaiStream.resolve_enum(Ccl156.Shape, self._io.read_u1())
            self.reserve = self._io.read_bytes(3)
            self.reserve1 = self._io.read_f4le()
            self.position = Ccl156.Vec3(self._io, self, self._root)
            self.position._read()
            self.id = self._io.read_u4le()
            self.extent = Ccl156.Vec3(self._io, self, self._root)
            self.extent._read()
            self.radius = self._io.read_f4le()
            self.angle = Ccl156.Vec3(self._io, self, self._root)
            self.angle._read()
            self.reserve2 = self._io.read_f4le()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.position._fetch_instances()
            self.extent._fetch_instances()
            self.angle._fetch_instances()


        def _write__seq(self, io=None):
            super(Ccl156.ColInfo, self)._write__seq(io)
            self._io.write_u4le(self.attr)
            self._io.write_u2le(self.ref_joint_no)
            self._io.write_u2le(self.pair_joint_no)
            self._io.write_u1(int(self.shape))
            self._io.write_bytes(self.reserve)
            self._io.write_f4le(self.reserve1)
            self.position._write__seq(self._io)
            self._io.write_u4le(self.id)
            self.extent._write__seq(self._io)
            self._io.write_f4le(self.radius)
            self.angle._write__seq(self._io)
            self._io.write_f4le(self.reserve2)


        def _check(self):
            if len(self.reserve) != 3:
                raise kaitaistruct.ConsistencyError(u"reserve", 3, len(self.reserve))
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self._root, self.position._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self, self.position._parent)
            if self.extent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"extent", self._root, self.extent._root)
            if self.extent._parent != self:
                raise kaitaistruct.ConsistencyError(u"extent", self, self.extent._parent)
            if self.angle._root != self._root:
                raise kaitaistruct.ConsistencyError(u"angle", self._root, self.angle._root)
            if self.angle._parent != self:
                raise kaitaistruct.ConsistencyError(u"angle", self, self.angle._parent)
            self._dirty = False


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Ccl156.Vec3, self).__init__(_io)
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
            super(Ccl156.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            self._dirty = False


    @property
    def expected_data_size(self):
        if hasattr(self, '_m_expected_data_size'):
            return self._m_expected_data_size

        self._m_expected_data_size = 64 * self.num_col_infos
        return getattr(self, '_m_expected_data_size', None)

    def _invalidate_expected_data_size(self):
        del self._m_expected_data_size
    @property
    def expected_size(self):
        if hasattr(self, '_m_expected_size'):
            return self._m_expected_size

        self._m_expected_size = 16 + 64 * self.num_col_infos
        return getattr(self, '_m_expected_size', None)

    def _invalidate_expected_size(self):
        del self._m_expected_size

