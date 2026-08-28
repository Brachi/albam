from typing import Type
from struct import pack, unpack
from functools import partial
from kaitaistruct import KaitaiStream

class XmlPropSerializer:
    def __init__(self):
        pass

    def read(self, src):
        for i in self.__annotations__:
            setattr(self, i, getattr(src, i))


class Float2(XmlPropSerializer):
    x: float
    y: float


class Float3(XmlPropSerializer):
    x: float
    y: float
    z: float


class Float4(XmlPropSerializer):
    x: float
    y: float
    z: float
    w: float

class Color(XmlPropSerializer):
    r: float
    g: float
    b: float
    a: float

class Vector3(XmlPropSerializer):
    x: float
    y: float
    z: float
    padding: float

class Vector4(Float4):
    pass

class Quaternion(Float4):
    pass

class Float3x3(XmlPropSerializer):
    r0: Float3
    r1: Float3
    r2: Float3

class Float4x4(XmlPropSerializer):
    r0: Float4
    r1: Float4
    r2: Float4
    r3: Float4

class Matrix(Float4x4):
    pass

class Float3x4(XmlPropSerializer):
    r0: Float4
    r1: Float4
    r2: Float4

class EaseCurve(XmlPropSerializer):
    p1: float
    p2: float

class Line(XmlPropSerializer): #TODO: reflect in template
    origin: Vector3
    dir: Vector3

class LineSegment(XmlPropSerializer):
    p1: Vector3
    p2: Vector3

class Ray(Line):
    pass

class Plane(XmlPropSerializer):
    normal: Float3
    dist: float

class Sphere(XmlPropSerializer):
    pos: Float3
    r: float

class Capsule(LineSegment):
    r: float

class AABB(XmlPropSerializer):
    minpos: Vector3
    maxpos: Vector3

class OBB(XmlPropSerializer):
    coord: Matrix
    extent: Vector3

class Cylinder(LineSegment):
    r: float
    pad: float

class Range(XmlPropSerializer):
    s: int
    r: int

class RangeF(XmlPropSerializer):
    s: float
    r: float

type_to_class = {
    0xF: Color,
    0x14: Vector3,
    0x15: Vector4,
    0x16: Quaternion,
    0x22: Float2,
    0x23: Float3,
    0x24: Float4,
    0x25: Float3x3,
    0x27: Matrix,  # Float4x4 is inherited by Matrix
    0x26: Float3x4,
    0x28: EaseCurve,
    0x29: Line,
    0x2A: LineSegment,
    0x2B: Ray,  # Line is inherited by Ray
    0x2C: Plane,
    0x2D: Sphere,
    0x2E: Capsule,
    0x2F: AABB,
    0x30: OBB,
    0x31: Cylinder,
    0x36: Range,
    0x37: RangeF,
}

type_to_class_name = {
    0xF: 'Color',
    0x22: "Float2",
    0x23: "Float3",
    0x24: "Float4",
    0x14: "Vector3",
    0x15: "Vector4",
    0x16: "Quaternion",
    0x25: "Float3x3",
    0x27: "Matrix",  # Float4x4 is inherited by Matrix
    0x26: "Float3x4",
    0x28: "EaseCurve",
    0x29: "Line",
    0x2A: "LineSegment",
    0x2B: "Ray",  # Line is inherited by Ray
    0x2C: "Plane",
    0x2D: "Sphere",
    0x2E: "Capsule",
    0x2F: "AABB",
    0x30: "OBB",
    0x31: "Cylinder",
    0x36: "Range",
    0x37: "RangeF"
}

scalar_type_map = {
    0x3: KaitaiStream.read_u1,
    0x4: KaitaiStream.read_u1,
    0x5: KaitaiStream.read_u2le,
    0x6: KaitaiStream.read_u4le,
    0x7: KaitaiStream.read_u8le,
    0x8: KaitaiStream.read_s1,
    0x9: KaitaiStream.read_s2le,
    0xA: KaitaiStream.read_s4le,
    0xB: KaitaiStream.read_s8le,
    0xC: KaitaiStream.read_f4le,
    0xD: KaitaiStream.read_f8le
}

scalar_write_map = {
    0x3: partial(pack, 'B'),
    0x4: partial(pack, 'B'),
    0x5: partial(pack, 'H'),
    0x6: partial(pack, 'I'),
    0x7: partial(pack, 'Q'),
    0x8: partial(pack, 'b'),
    0x9: partial(pack, 'h'),
    0xA: partial(pack, 'i'),
    0xB: partial(pack, 'q'),
    0xC: partial(pack, 'f'),
    0xD: partial(pack, 'd')
}

# scalar_write_map = {
#     0x3: KaitaiStream.write_u1,
#     0x4: KaitaiStream.write_u1,
#     0x5: KaitaiStream.write_u2le,
#     0x6: KaitaiStream.write_u4le,
#     0x7: KaitaiStream.write_u8le,
#     0x8: KaitaiStream.write_s1,
#     0x9: KaitaiStream.write_s2le,
#     0xA: KaitaiStream.write_s4le,
#     0xB: KaitaiStream.write_s8le,
#     0xC: KaitaiStream.write_f4le,
#     0xD: KaitaiStream.write_f8le
# }

scalar_bytes_num = {
    0x3: 1,
    0x4: 1,
    0x5: 2,
    0x6: 4,
    0x7: 8,
    0x8: 1,
    0x9: 2,
    0xA: 4,
    0xB: 8,
    0xC: 4,
    0xD: 8
}