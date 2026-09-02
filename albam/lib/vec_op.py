# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 01:13:36 2019

@author: AsteriskAmpersand
"""
from mathutils import Vector


def vect_int(vec):
    return (int(i) for i in vec)


def vec_mult(vec1, vec2):
    return Vector(x / y for x, y in zip(vec1, vec2))


def vec_div(vec1, vec2):
    return Vector(x / y for x, y in zip(vec1, vec2))


def vec_unfold(vec):
    return {"x": vec.x, "y": vec.y, "z": vec.z, "w": 0}
