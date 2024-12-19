# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 10:51:36 2019

@author: aguevara
"""
from mathutils import Vector
from math import sin, cos
from math import pi as Pi
import random
import numpy as np

try:
    from vec_op import vec_mult
except ImportError:
    from albam.lib.vec_op import vec_mult


class Ray():
    kEpsilon = 0.0001

    def __init__(self, orig, direction):
        self.origin = orig
        self.direction = direction
        self.inv_direction = self.invertDirection()

    def invertDirection(self):
        return Vector([np.inf if var == 0 else 1 / var for var in self.direction])

    def triIntersect(self, tri):
        orig, direction = self.origin, self.direction
        v0, v1, v2 = tri.vertices
        v0v1 = v1 - v0
        v0v2 = v2 - v0
        pvec = direction.crossProduct(v0v2)
        det = v0v1.dotProduct(pvec)
        # if the determinant is negative the triangle is backfacing
        # if the determinant is close to 0, the ray misses the triangle
        if (det < Ray.kEpsilon):
            return False
        # ray and triangle are parallel if det is close to 0
        if (abs(det) < Ray.kEpsilon):
            return False
        invDet = 1 / det
        tvec = orig - v0
        u = tvec.dotProduct(pvec) * invDet
        if (u < 0 or u > 1):
            return False
        qvec = tvec.crossProduct(v0v1)
        v = direction.dotProduct(qvec) * invDet
        if (v < 0 or u + v > 1):
            return False
        # t = v0v2.dotProduct(qvec) * invDet;
        return True

    def intersectBox(self, bb):
        x0 = self.origin
        n_inv = self.inv_direction
        bmin, bmax = bb.minPos, bb.maxPos
        tmin = np.inf
        tmax = -np.inf
        for dim in range(3):
            t1 = (bmin[dim] - x0[dim]) * n_inv[dim]
            t2 = (bmax[dim] - x0[dim]) * n_inv[dim]
            tmin = max(tmin, min(t1, t2))
            tmax = min(tmax, max(t1, t2))
        if tmax < 0:
            return False
        return tmax >= tmin

    @staticmethod
    def randomRay(sceneBounds=None):
        theta, phi = random.random() * 2 * Pi, random.random() * 2 * Pi
        direction = (sin(phi) * cos(theta), sin(phi) * sin(theta), cos(theta))
        origin = Vector([random.random(), random.random(), random.random()])
        if sceneBounds:
            m, M = sceneBounds.minPos, sceneBounds.maxPos
            origin = vec_mult(M - m, origin)
        return Ray(origin, direction)
