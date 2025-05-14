# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 23:44:04 2019

@author: AsteriskAmpersand
"""
try:
    from pymorton import interleave as morton_encode
    from rays import Ray
    from vec_op import vect_int, vec_div, vec_unfold
except ImportError:
    from albam.lib.pymorton import interleave as morton_encode
    from albam.lib.rays import Ray
    from albam.lib.vec_op import vect_int, vec_div, vec_unfold

from mathutils import Vector
from functools import total_ordering
import numpy as np

MORTONLIMIT = 0x3FF
MORTONLENGHT = 32
EPS = 0.0001


class BoundingBox():
    def __init__(self, vectorList):
        self.minPos = Vector([min([v.x for v in vectorList]),
                              min([v.y for v in vectorList]),
                              min([v.z for v in vectorList])])
        self.maxPos = Vector([max([v.x for v in vectorList]),
                              max([v.y for v in vectorList]),
                              max([v.z for v in vectorList])])
        self.capcom()

    def capcom(self):
        x, y, z = (self.maxPos - self.minPos)
        self.minPos -= Vector([x == 0, y == 0, z == 0])
        self.maxPos += Vector([x == 0, y == 0, z == 0])
        # Correction for flat bounding boxes

    def __contains__(self, bb):
        if isinstance(bb, BoundingBox):
            return self.minPos.x <= bb.minPos.x and \
                bb.maxPos.x <= self.maxPos.x and \
                self.minPos.y <= bb.minPos.y and \
                bb.maxPos.y <= self.maxPos.y and \
                self.minPos.z <= bb.minPos.z and \
                bb.maxPos.z <= self.maxPos.z
        if type(bb) is Ray:
            return bb.intersectBox(self)
        return self.minPos.x <= bb.x <= self.maxPos.x and \
            self.minPos.y <= bb.y <= self.maxPos.y and \
            self.minPos.z <= bb.z <= self.maxPos.z

    def __eq__(self, bb):
        return self in bb and bb in self

    def __add__(self, bb):
        return self.merge(bb)

    def merge(self, bb):
        return BoundingBox([self.minPos, self.maxPos, bb.minPos, bb.maxPos])

    def intersect(self, bb):
        minima = Vector([max(w0, w1)
                        for w0, w1 in zip(self.minPos, bb.minPos)])
        maxima = Vector([min(w0, w1)
                        for w0, w1 in zip(self.maxPos, bb.maxPos)])
        if any([m >= M for m, M in zip(minima, maxima)]):
            minima = maxima = Vector([0, 0, 0])
        return BoundingBox([minima, maxima])

    def surfaceArea(self):
        if not hasattr(self, "_surfaceArea"):
            x, y, z = self.maxPos - self.minPos
            self._surfaceArea = 2 * (x * y + y * z + z * x)
        return self._surfaceArea

    def barycenter(self):
        return (self.minPos + self.maxPos) / 2

    def serialize(self):
        return {"minPos": vec_unfold(self.minPos), "maxPos": vec_unfold(self.maxPos)}


@total_ordering
class GeometryPrimitive():
    def __eq__(self, gp):
        return self.encode() == gp.encode()

    def __lt__(self, gp):
        return self.encode() < gp.encode()

    def boundingBox(self):
        raise NotImplementedError

    def barycenter(self):
        raise NotImplementedError

    def isPrimitive(self):
        return True

    def setBounds(self, minPos, maxPos):
        self.sceneSize = maxPos - minPos
        self.sceneStart = minPos
        self.encodable = True
        return self

    def encode(self):
        if self.encodable:
            if hasattr(self, "mortonCode"):
                return self.mortonCode
            else:
                normalized = vec_div(
                    (self.barycenter() - self.sceneStart), self.sceneSize)
                self.mortonCode = morton_encode(
                    * (vect_int(MORTONLIMIT * normalized)))
                return self.mortonCode
        else:
            raise ValueError("No scene information to normalize the point")

    def __contains__(self, gp):
        return gp.boundingBox() in self.boundingBox()

    def setIndex(self, value):
        self._index = value
        return self

    def index(self):
        return self._index


def decontainer(vec):
    return vec.x, vec.y, vec.z


class Tri(GeometryPrimitive):
    def __init__(self, triface, vertList):
        self.dataFace = triface
        self.vertices = [
            Vector(decontainer(vertList[triface.vert[i]])) for i in range(3)]
        self.type = triface.type
        self.encodable = False

    def boundingBox(self):
        if not hasattr(self, "_boundingBox"):
            self._boundingBox = BoundingBox(self.vertices)
        return self._boundingBox

    def barycenter(self):
        if not hasattr(self, "_barycenter"):
            self._barycenter = sum(
                self.vertices[1:], self.vertices[0]) / len(self.vertices)
        return self._barycenter

    def quad(self, tri2):
        return self.sbcquad(tri2)

    def sbcquad(self, tri2):
        assert self.parallel(tri2)
        d1 = self.dataFace
        d2 = tri2.dataFace

        v = set()
        for vert in d1.vert:
            v.add(vert)
        for vert in d2.vert:
            v.add(vert)
        assert len(v) == 4
        results = []
        for vert in v:
            if vert in d1.vert:
                results.append(self.vertices[d1.vert.index(vert)])
            elif vert in d2.vert:
                results.append(tri2.vertices[d2.vert.index(vert)])
        return results

    def normal(self):
        if not hasattr(self, "normalVector"):
            self.normalVector = Vector(
                np.cross(self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[0]))
            self.normalVector.normalize()
        return self.normalVector

    def parallel(self, tri2):
        n1 = self.normal()
        n2 = tri2.normal()
        return np.dot(n1, n2) > 1 - EPS

    def __repr__(self):
        return str(self.vertices)

    @staticmethod
    def cycles(face):
        return [(face.vert[i % 3], face.vert[(i + 1) % 3]) for i in range(3)]

    def compatibleType(self, tri2):
        f1 = self.dataFace
        f2 = tri2.dataFace
        return f1.type == f2.type

    def adjacent(self, tri2):
        d1 = self.dataFace
        d2 = tri2.dataFace
        e1 = self.cycles(d1)
        e2 = self.cycles(d2)
        return any(tuple(reversed(c)) in e2 for c in e1)

    def contention(self, tri2):
        return tri2 in self

    def mergeable(self, tri2):
        if type(self) is not Tri or type(tri2) is not Tri:
            return False
        return self.parallel(tri2) and \
            self.adjacent(tri2) and \
            self.compatibleType(tri2) and \
            self.contention(tri2)

    def primitiveSerialize(self):
        return {"face1": self.dataFace.index(), "face2": 0xFFFF, "type": self.dataFace.type,
                "quadOrder": [0xFF, 0xFF, 0xFF, 0xFF]}

    def triSerialize(self):
        return {"normal": list(self.dataFace.normal)[:3],
                "vert": self.dataFace.vert,
                "type": self.dataFace.type,
                "null1": 0, "null2": 0, "null3": 0,
                "adjacent": self.dataFace.adjacent}

    def exactCollision(self, exactObject):
        return exactObject.triIntersect(self)


class QuadPair(Tri):
    def __init__(self, tri1, tri2):
        if tri2 not in tri1:
            raise ValueError("Tri2 must be contained on Tri1 bounding box")
        self.dataFaces = [tri1, tri2]
        self.vertices = tri1.quad(tri2)

    def boundingBox(self):
        if not hasattr(self, "_boundingBox"):
            self._boundingBox = self.dataFaces[0].boundingBox().merge(
                self.dataFaces[1].boundingBox())
        return self._boundingBox

    def quad(self, tri2):
        raise NotImplementedError("Quads cannot be merged with other tris.")

    def mergeable(self, tri2):
        return False

    def quadOrder(self):
        d1 = self.dataFaces[0].dataFace
        d2 = self.dataFaces[1].dataFace
        e1 = self.cycles(d1)
        e2 = self.cycles(d2)
        for ix, c in enumerate(e1):
            cs = tuple(reversed(c))
            if cs in e2:
                lix = e2.index(cs)
        return [ix, (ix + 1) % 3, (ix + 2) % 3, (lix + 2) % 3]

    def type(self):
        return self.dataFaces[0].dataFace.type

    def primitiveSerialize(self):
        d1 = self.dataFaces[0]
        d2 = self.dataFaces[1]
        return {"face1": d1.dataFace.index(), "face2": d2.dataFace.index(), "type": self.type(),
                "quadOrder": self.quadOrder()}

    def exactCollision(self, exactObject):
        return any([exactObject.triIntersect(f) for f in self.dataFaces])


class PrimitiveTree(GeometryPrimitive):
    def __init__(self, QBVH):
        self.content = QBVH
        bb = self.boundingBox()
        self.setBounds(bb.minPos, bb.maxPos)
        self.encodable = True

    def boundingBox(self):
        if not hasattr(self, "refined"):
            return self.content.boundingBox()
        else:
            return self.refined

    def refine(self, vertices):
        self.refined = BoundingBox(vertices)
        return self

    def barycenter(self):
        return self.boundingBox().barycenter()

    def primitiveSerialize(self):
        return {
            "BVHC": 0x77B17B2443485642,
            "SOH": 0x1,
            "boundingBox": self.content.boundingBox().serialize(),
            "nodeCount": len(self.content),
            "null": [0] * 3,
            "AABBArray": [sn.serialize() for sn in self.content.subnodes()]
        }

    def __len__(self):
        return len(self.content)

    def exactCollision(self, exactObject):
        # print(type(self.content))
        return exactObject in self.content

    def serialize(self):
        return {"BVHC": 0x77B17B2443485642,
                "SOH": 0x1,
                "boundingBox": self.content.boundingBox().serialize(),
                "nodeCount": len(self.content),
                "null": [0] * 3,
                "AABBArray": [n.serialize() for n in self.content.subnodes()]
                }
