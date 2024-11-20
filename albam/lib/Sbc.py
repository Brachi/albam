try:
    from construct import Struct
    for t in [8, 16, 24, 32, 64]:
        for s in ["u", "s"]:
            exec("from construct import Int%d%sl" % (t, s))
    for t in [32, 64]:
        exec("from construct import Float%dl" % (t))
    from construct import PaddedString, CString, Flag
    from construct import this
    from construct import Byte, Int, Single, Double
    import sys
    sys.path.insert(1, '..\geometry')
    import albam.lib.primitive_geometry as geo
    import bvh_construction as bvh
except:
    from albam.lib.construct_plugin import Struct, Int8ul, Int16ul, Int24ul, Int32sl, Int32ul, Int64ul
    # for t in [8, 16, 24, 32, 64]:
    #    for s in ["u", "s"]:
    #        exec("from albam.lib.construct_plugin  Int%d%sl" % (t, s))
    # for t in [32, 64]:
    #    exec("from albam.lib.construct_plugin  Float%dl" % (t))
    from albam.lib.construct_plugin import Float16l, Float32l
    from albam.lib.construct_plugin import PaddedString, CString, Flag
    from albam.lib.construct_plugin import this
    from albam.lib.construct_plugin import Byte, Int, Single, Double
    import albam.lib.primitive_geometry as geo
    import albam.lib.bvh_construction as bvh
from collections import OrderedDict


class StructClass():
    def __init__(self, data=None):
        if data:
            if type(data) is dict:
                self.construct(data)
            else:
                raise ValueError("Cannot Marshall yet.")

    def construct(self, data):
        for field in self.innerStruct.subcons:
            setattr(self, field.name, data[field.name])
        return self

    def serialize(self):
        return self.innerStruct.build({getattr(self, field.name) for field in self.innerStruct.subcons})

    def __eq__(self, sc):
        if self.innerStruct != sc.innerStruct:
            return False
        for field in self.innerStruct.subcons:
            if getattr(sc, field.name) != getattr(self, field.name):
                return False
        return True


# DataType
Vector4 = Struct(
    "x" / Float32l,
    "y" / Float32l,
    "z" / Float32l,
    "w" / Float32l,
)

# Bounding Box
BoundingBox = Struct(
    "minPos" / Vector4,
    "maxPos" / Vector4,
)

# Header
Header = Struct(
    "type" / Int32ul,
    "version" / Int32ul,
    "null0" / Int64ul,
    "objectCount" / Int16ul,
    "stageCount" / Int16ul,
    "pairCount" / Int32ul,
    "faceCount" / Int32ul,
    "vertexCount" / Int32ul,
    "null1" / Int64ul[2],  # uint64  NULL1[2];
    "boundingBox" / BoundingBox,
    # ABBArray[112 bytes] * cBVHCollsion.ConfigCount[Total Count]
    "boundingBoxSize" / Int32ul,
)

# SbcInfo (Objects)
SbcInfo = Struct(
    "boundingBox" / BoundingBox,
    "null0" / Int32ul[6],
    "pairsStart" / Int32ul,
    "pairsCount" / Int32ul,
    "facesStart" / Int32ul,
    "facesCount" / Int32ul,
    "vertexStart" / Int32ul,
    "vertexCount" / Int32ul,
    "indexID" / Int32sl,
    "null1" / Int32ul[3],
)

AABBBlock = Struct(
    "xArray" / Float32l[4],
    "yArray" / Float32l[4],
    "zArray" / Float32l[4],
)

# AABB Array Bounding Points
AABBArray = AABB = cSbcArrayBP = Struct(
    "nodeType" / Byte[4],
    # Byte XY, X is facepair on obj, y is sbvc node on obj
    # 0100 1011 is read as 0010 1101 meaning Id 3 is a facepair and 1,2,4 is an obj
    "nodeId" / Int16ul[4],
    "unkn5" / Byte[4],  # Can be set to 0 without crashes
    # "sb == \"hkAabb{ min=[ 1, 2, 3, 4 ], max=[ 11, 12, 13, 14 ] }\""  14356f0f0 string  64
    # AABB Min Pos Matrix
    "minAABB" / AABBBlock,
    "maxAABB" / AABBBlock,
)

# cBHVCollision (Bounding Box Tree)
cBVHCollision = Struct(
    "BVHC" / Int64ul,  # Bound Volume Hierarchy Collision Identifier 0x77B17B2443485642
    "SOH" / Int64ul,  # Start of Header 0x1
    "boundingBox" / BoundingBox,  # BoundingBox of First Node
    "nodeCount" / Int32ul,
    "null" / Int32ul[3],
    "AABBArray" / AABBArray[this.nodeCount]
)

# Faces
Face = Struct(
    "normal" / Float32l[3],
    "vert" / Int16ul[3],
    "type" / Int16ul,  # wall, ceiling, etc
    "null1" / Int32ul,
    "adjacent" / Byte[3],
    # "nearby1" / Byte,#v1-v2 Edge Angle with neighbor (0 = 90°, 1 = 0°, 2 > 180°, 3<180°)
    # "nearby2" / Byte,#v2-v3
    # "nearby3" / Byte,#v3-v1
    "null2" / Byte,
    "null3" / Int32ul,
)

Vertex = Vector4

# SBC Stage Link
CollisionType = Struct(
    "unkn1" / Float32l,
    "unkn3" / Int16ul,
    "unkn4" / Int16ul,
    "unkn5" / Int32ul[3],
    "jpPath" / Byte[12],  # 0xAB 0xE5 0x90 0x8D 0x3A
)

# Pair Faces/Types
SFacePair = Struct(  # When a face bounding box contains another face
    "face1" / Int16ul,
    "face2" / Int16ul,
    # CommonEdge1(f1),CommonEdge2(f1),NoncommonEdge(f1),NoncommonEdge(f2)
    "quadOrder" / Byte[4],
    "type" / Int16ul,  # 0 floor, 1 wall, 2 airwall
)


class FacePair(StructClass):
    innerStruct = SFacePair


SBCStruct = Struct(
    "header" / Header,
    "sbcinfo" / SbcInfo[this.header.objectCount],
    "cBVH" / cBVHCollision[this.header.objectCount],
    "cBVHCollision" / cBVHCollision,
    # sum over this.header.objectCount and then sbcinfo[j].facesCount
    "faceCollection" / Face[this.header.faceCount],
    # sum over this.header.objectCount and then sbcinfo[j].vertexCount
    "vertexCollection" / Vertex[this.header.vertexCount],
    "collisionTypes" / CollisionType[this.header.stageCount],
    # sum over this.header.objectCount and then sbcinfo[j].pairCount
    "pairCollection" / SFacePair[this.header.pairCount]
)


class SBC():
    def __init__(self, data=None):
        if data:
            if type(data) is dict:
                self.construct(data)
            else:
                self.marshall(data)

    def marshall(self, data):
        content = SBCStruct.parse(data)
        self.header = content.header
        self.objects = []
        for ix, objectInfo in enumerate(content.sbcinfo):
            ps, pc = objectInfo.pairsStart, objectInfo.pairsCount
            fs, fc = objectInfo.facesStart, objectInfo.facesCount
            vs, vc = objectInfo.vertexStart, objectInfo.vertexCount
            obj = SBCObject(objectInfo, content.cBVH[ix], content.faceCollection[fs:fs+fc],
                            content.vertexCollection[vs:vs+vc], content.pairCollection[ps:ps+pc])
            self.objects.append(obj)
        self.cBVHCollision = content.cBVHCollision
        self.collisionTypes = content.collisionTypes
        return self

    def construct(self, data):
        pass

    def serialize(self):
        pass


class SBCObject():
    def __init__(self, info, BVHTree, faces, vertices, pairs):
        self.sbcinfo = info
        self.bvhtree = BVHTree
        self.faces = bvh.indexizeObject(
            [geo.Tri(face, vertices) for face in faces])
        self.vertices = vertices
        self.pairs = bvh.indexizeObject([geo.QuadPair(self.faces[pair.face1], self.faces[pair.face2])
                                         if pair.face2 != 0xFFFF else
                                         self.faces[pair.face1]
                                         for pair in pairs])


class BVHTreeNode():
    typeMap = {"Tri": "RoyalBlue", "Pair": "DarkTurquoise", "BVH Node": "Goldenrod", "BVH SBC": "DarkSeaGreen",
               "BVH SBC Node": "Goldenrod", "BVH Root": "DarkSeaGreen",
               "Empty": "black"}
    primaryMap = {"BVH SBC Node": "BVH SBC",
                  "BVH Node": "Geometry"}

    def __init__(self, node, typing, ix):
        self.name = "%s-%05d" % (typing, ix) + ("" if typing not in [
            "BVH Node", "BVH SBC Node"] else "\nUnkn:%s" % str(node.unkn5))
        self.color = self.typeMap[typing]
        self.type = typing
        self.node = node
        self._children = []

    def children(self):
        return self._children

    def name(self):
        return self.name

    def color(self):
        return self.color

    def calculateChildren(self, PrimaryArray, SecondaryArray):
        children = []
        idmap = self.node.nodeId
        if self.type == "Empty" or self.type == "Geometry":
            return
        typebin = bin(self.node.nodeType[0])[2:].zfill(8)
        face = [int(b) for b in reversed(typebin[0:4])]
        geom = [int(b) for b in reversed(typebin[4:8])]
        for f, g, ix in zip(face, geom, range(4)):
            if f and g:
                raise ValueError("Can't be Node and Geometry")
            if f:
                children.append(PrimaryArray[idmap[ix]])
            elif g:
                children.append(SecondaryArray[idmap[ix]])
            else:
                children.append(BVHTreeNode(None, "Empty", idmap[ix]))
        self._children = children

    def __hash__(self):
        return (self.name).__hash__()

    def makeString(self, level=0):
        return "\t"*level+self.name+"\n"+'\n'.join([child.makeString(level+1) for child in self.children()])

    def __repr__(self):
        return self.makeString()

    def boundingBox(self):
        if self.type == "Tri" or self.type == "Pair":
            return self.node.boundingBox()
        elif self.type == "Empty":
            return None
        else:
            prev = None
            for child in self.children():
                if child.type != "Empty":
                    prev = prev.merge(child.boundingBox()
                                      ) if prev else child.boundingBox()
            return prev

    def convertNodeBox(self, nodebox, ix):
        if not hasattr(self, "nodeboxes"):
            def decompile(xyz):
                x, y, z = xyz.xArray, xyz.yArray, xyz.zArray
                return zip(x, y, z)
            self.nodeboxes = [geo.BoundingBox([Vector(m), Vector(M)])
                              for m, M in zip(decompile(nodebox.minAABB), decompile(nodebox.maxAABB))]
        return self.nodeboxes[ix]

    def compareBoundingBox(self):
        if self.type == "Tri" or self.type == "Pair" or self.type == "Empty":
            return True
        elif self.type == "BVH Root" or self.type == "BVH SBC":
            geobox = geo.BoundingBox(
                [self.node.boundingBox.minPos, self.node.boundingBox.maxPos])
            equal = True
            for child in self.children():
                comparison = child.compareBoundingBox()
                equal &= comparison
                if not comparison:
                    print("Inherited Failure")
            return self.boundingBox() == geobox and equal
        else:
            equal = True
            for ix, child in enumerate(self.children()):
                # print(ix)
                child.compareBoundingBox()
                childbox = child.boundingBox()
                if childbox:
                    comparison = self.convertNodeBox(self.node, ix) == childbox
                    equal &= comparison
                    if not comparison:
                        print(self.convertNodeBox(self.node, ix))
                        print(childbox)
                        print("%d Failed" % ix)
            return equal

# =============================================================================
#  Serialization Code
# =============================================================================
def buildHeader(headerData):
    return Header.build(headerData)


def formHeader(objCount, vertCount, triCount, pairCount, stageCount, aabbCount, parentTree):
    return {"type": 0xFF434253,  # TODO
            "version": 0x781ACA20,
            "null0": 0,
            "objectCount": objCount,
            "stageCount": stageCount,
            "pairCount": pairCount,
            "faceCount": triCount,
            "vertexCount": vertCount,
            "null1": [0]*2,
            "boundingBox": parentTree.boundingBox().serialize(),
            "boundingBoxSize": 0x70*(aabbCount)  # TODO
            }


def getVertexBox(v):
    return geo.BoundingBox(v)


def buildInfo(header, faces, vertices, stages, pairs, sbcs, sbcC, metadata):
    f0, v0, p0 = 0, 0, 0,
    infos = []
    for f, v, p, s, m in zip(faces, vertices, pairs, sbcs, metadata):
        info = {"boundingBox": getVertexBox(v).serialize(),
                "null0": [0]*6,
                "pairsStart": p0,
                "pairsCount": len(p),
                "facesStart": f0,
                "facesCount": len(f),
                "vertexStart": v0,
                "vertexCount": len(v),
                "indexID": m["indexID"],
                "null1": [0]*3}
        f0 += len(f)
        v0 += len(v)
        p0 += len(p)
        infos.append(SbcInfo.build(info))
    return infos


def buildCollision(sbcTree):
    return cBVHCollision.build(sbcTree.primitiveSerialize())


def buildFaces(faces):
    return b''.join([Face.build(f.triSerialize()) for f in faces])


typeNameMapping = {"unkn1": "{Unkn1}",
                   "unkn3": "{Unkn3}",
                   "unkn4": "{Unkn4}",
                   "unkn5": "{Unkn5}",
                   "jpPath": "jpPath",
                   }


def formTypes(typing):
    return {typingName: typing[typeNameMapping[typingName]] for typingName in typeNameMapping}


def buildTypes(typing):
    return CollisionType.build(formTypes(typing))


def buildPairs(pairs):
    return b''.join([SFacePair.build(p.primitiveSerialize()) for p in pairs])


def buildVertices(vertices):
    return b''.join([Vertex.build(geo.vec_unfold(v)) for v in vertices])


def buildSBC(verts, tris, quads, sbcs, links, parentTree, meshmetadata):
    def tally(x): return sum(map(len, x))
    headerData = formHeader(len(verts), tally(verts), tally(tris), tally(
        quads), len(links), tally(sbcs+[parentTree]), parentTree)
    header = buildHeader(headerData)
    cBVH = list(map(buildCollision, sbcs))
    cBVHCollision = buildCollision(parentTree)
    faceCollection = list(map(buildFaces, tris))
    vertexCollection = list(map(buildVertices, verts))
    collisionTypes = list(map(buildTypes, links))
    pairCollection = list(map(buildPairs, quads))
    infoCollection = buildInfo(
        header, tris, verts, collisionTypes, quads, cBVH, cBVHCollision, meshmetadata)

    def flatten(x): return b''.join(x)
    return (header +
            flatten(infoCollection) +
            flatten(cBVH) +
            cBVHCollision +
            flatten(faceCollection) +
            flatten(vertexCollection) +
            flatten(collisionTypes) +
            flatten(pairCollection))


# =============================================================================
# Utility Code
# =============================================================================
def unparented(nodeList):
    unparentedSet = set(nodeList)
    for node in nodeList:
        for child in node.children():
            if child in unparentedSet:
                unparentedSet.remove(child)
    return list(unparentedSet)


EMPTY = 0
PRIMITIVE = 1
NODE = 2


def calculateChildren(node):
    typebin = bin(node.nodeType[0])[2:].zfill(8)
    prim = [int(b) for b in reversed(typebin[0:4])]
    sec = [int(b) for b in reversed(typebin[4:8])]
    return [p+s*2 for p, s in zip(prim, sec)]


def nodeChild(node):
    sons = calculateChildren(node)
    return [node.nodeId[ix] for ix, son in enumerate(sons) if son == 2]


def recursiveParseTree(nodeList, hierarchy, nid, level=0):
    if level >= len(hierarchy):
        hierarchy.append([])
    hierarchy[level].append(nid)
    for subnode in nodeChild(nodeList[nid]):
        recursiveParseTree(nodeList, hierarchy, subnode, level+1)
    return


def dependencyStructure(nodeList):
    hierarchy = []
    childlink = {}
    recursiveParseTree(nodeList, hierarchy, 0)
    return childlink, hierarchy


def makeBinData(typings, ids, basic, nodes):
    lt, rt = typings
    l, r = ids
    if not any(typings):
        return None
    else:
        if lt == 1:
            ln = basic[l]
        elif lt == 2:
            ln = nodes[l]
        if not rt:
            return ln
        elif rt == 1:
            rn = basic[r]
        elif rt == 2:
            rn = nodes[r]
        return bvh.BinaryCluster((ln, rn))


def readTree(primitives, treeData):
    childLink, hierarchy = dependencyStructure(treeData.AABBArray)
    results = [None]*len(treeData.AABBArray)
    for nodes in reversed(hierarchy):
        for node in nodes:
            nodeIndex = node
            nodeData = treeData.AABBArray[nodeIndex]
            children = calculateChildren(nodeData)
            ld, rd = children[:2], children[2:]
            l, r = nodeData.nodeId[:2], nodeData.nodeId[2:]
            ltree = makeBinData(ld, l, primitives, results)
            rtree = makeBinData(rd, r, primitives, results)
            t = bvh.BinaryCluster((ltree, rtree))
            results[nodeIndex] = t
    tree = results[0].collapse()
    # print(tree)
    bvh.indexizeObject(results)
    # print(tree)
    return geo.PrimitiveTree(tree)


def readCollisionTree(objList, parentTree):
    treePrimitives = [readTree([bvh.BinaryCluster(p)
                               for p in obj.pairs], obj.bvhtree) for obj in objList]
    superTree = readTree([bvh.BinaryCluster(p)
                         for p in bvh.indexizeObject(treePrimitives)], parentTree)
    return superTree


def ObjToBVHTree(obj, i=0):
    objNodes = []
    pairNodes = []
    for ix, pair in enumerate(obj.pairs):
        try:
            pairNodes.append(BVHTreeNode(
                pair, "Tri" if pair.face2 == 0xFFFF else "Pair", ix))
        except:
            pairNodes.append(BVHTreeNode(pair, "Pair" if type(
                pair) is geo.QuadPair else "Tri", ix))
    for ix, node in enumerate(obj.bvhtree.AABBArray):
        objNodes.append(BVHTreeNode(node, "BVH Node", ix))
    for node in objNodes:
        node.calculateChildren(pairNodes, objNodes)
    objRoot = BVHTreeNode(obj.bvhtree, "BVH SBC", i)
    objRoot._children = unparented(objNodes)
    return objRoot


def SBCToBVHTrees(sbc, sbcpath=""):
    objNodeCollection = []
    for i, obj in enumerate(sbc.objects):
        objRoot = ObjToBVHTree(obj, i)
        objNodeCollection.append(objRoot)
    superNodes = []
    for ix, superNode in enumerate(sbc.cBVHCollision.AABBArray):
        superNodes.append(BVHTreeNode(superNode, "BVH SBC Node", ix))
    root = BVHTreeNode(sbc.cBVHCollision, "BVH Root", 0)
    root._children = unparented(superNodes)
    for snode in superNodes:
        snode.calculateChildren(objNodeCollection, superNodes)
    # if len(root.children()) > 1 or any([len(top.children()) > 1 for top in objNodeCollection]):
    #    print(str(sbcpath))
    return root


# =============================================================================
# Test Code
# =============================================================================
if "__main__" in __name__:
    import numpy as np
    from mathutils import Vector
    from functools import reduce
    import time

    def boxToVec(bb):
        def blow(w): return (w.x, w.y, w.z)
        return Vector(blow(bb.minPos)), Vector(blow(bb.maxPos))

    def categorize(info, tree, vertex):
        x = info != tree
        y = tree != vertex
        z = info != vertex
        print(info)
        print(tree)
        print(vertex)
        print()

    def boxTest(obj):
        infoBB = boxToVec(obj.sbcinfo.boundingBox)
        treeBB = boxToVec(obj.bvhtree.boundingBox)
        progTreeBB = boxToVec(reduce(lambda x, y: x.merge(
            y), [geo.BoundingBox(face.vertices) for face in obj.faces]))
        vertexBB = boxToVec(geo.BoundingBox(obj.vertices))
        # categorize(infoBB,treeBB,vertexBB)
        if progTreeBB != treeBB:
            raise ValueError
        if infoBB != vertexBB:
            raise ValueError

    def treeTest(obj):
        if not ObjToBVHTree(obj).compareBoundingBox():
            raise ValueError("MINI")

    def megaTreeTest(content):
        if not SBCToBVHTrees(content).compareBoundingBox():
            raise ValueError("SUPER")

    def cycles(verts):
        return [(verts[i % 3], verts[(i+1) % 3]) for i in range(len(verts))]

    def edges(face):
        f = face.dataFace
        e1 = cycles(f.vert)
        return e1

    def calcNormal(verts):
        v = Vector(np.cross(verts[1]-verts[0], verts[2]-verts[0]))
        v.normalize()
        return v
    eps = 0.00001

    def doubleFace(face1, face2):
        return False

    def byteAngle(face1, face2):
        n1 = Vector(face1.dataFace.normal)  # calcNormal(face1.vertices)
        n2 = Vector(face2.dataFace.normal)  # calcNormal(face2.vertices)
        if (n1-n2).magnitude < eps:
            return 1
        if (n1+n2).magnitude < eps:
            return 4
        fv1 = face1.vertices
        e1 = edges(face1)
        e2 = edges(face2)
        for ix, e in enumerate(e1):
            if tuple(reversed(e)) in e2:
                edgem = (fv1[ix]+fv1[(ix+1) % 3])/2
                bary = (face1.barycenter()+face2.barycenter())/2
                facing = bary - edgem
                facing.normalize()
        n = (n1+n2)
        n.normalize()
        signum = (n1+n2).dot(facing) > 0
        if not signum:
            if n1.dot(n2) < eps:
                return 0
            return 2
        else:
            return 4

    infinityCounter = 0
    fuckupCounter = 0
    newCounter = 0

    def faceTest(faces, vertices):
        edgeSet = {}
        for f in faces:
            es = edges(f)
            for i, c in enumerate(es):
                edgeSet[c] = (f, i)
                if tuple(reversed(c)) in edgeSet:
                    f0, e = edgeSet[tuple(reversed(c))]
                    a = byteAngle(f0, f)
                    b = byteAngle(f0, f)
                    # if a==0 or a == 1:
                    # print(a)
                    # print(f0.dataFace.adjacent[e])
                    # assert f0.dataFace.adjacent[e] == f.dataFace.adjacent[i]
                    # assert f0.dataFace.adjacent[e] == a
                    # assert f.dataFace.adjacent[i] == b
                    global infinityCounter
                    infinityCounter += 1
                    if not (f0.dataFace.adjacent[e] == f.dataFace.adjacent[i] or
                            f0.dataFace.adjacent[e] == a or
                            f.dataFace.adjacent[i] == b
                            ):
                        if a == 4 and\
                                (f0.dataFace.adjacent[e] != f.dataFace.adjacent[i]):
                            # print ("Known Capcom Fuckup")
                            global fuckupCounter
                            fuckupCounter += 1
                        else:
                            print("--")
                            print(a)
                            print(f0.dataFace.adjacent[e])
                            print(f.dataFace.adjacent[i])
                            print(Vector(f0.dataFace.normal))
                            print(Vector(f.dataFace.normal))
                            print(f0.vertices)
                            print(f.vertices)
                            print("--")
                            global newCounter
                            newCounter += 1
    import math

    def angle(v1, v2):
        return math.acos(max(min((v1.dot(v2))/(v1.magnitude*v2.magnitude), 1), -1))

    failCount = 0
    totalCount = 0

    def faceInverseTest(faces, vertices):
        edgeSet = {}
        for f in faces:
            es = edges(f)
            for i, c in enumerate(es):
                if c in edgeSet:
                    f0, e = edgeSet[c]
                    a, b = f0.dataFace.adjacent[e], f.dataFace.adjacent[i]
                    e1, e2 = c
                    n1, n2 = calcNormal(f0.vertices), calcNormal(f.vertices)
                    def unfold(w): return Vector([w.x, w.y, w.z])
                    def nfold(w): return Vector([w[0], w[1], w[2]])
                    ed = unfold(vertices[e2])-unfold(vertices[e1])
                    i0 = n1.dot(n2) < eps
                    ang = angle(n1, n2)
                    i1 = eps < ang < math.pi/2
                    i2 = math.pi/2 < ang <= math.pi
                    i3 = nfold(f0.dataFace.normal).cross(
                        nfold(f.dataFace.normal)).dot(ed) > eps
                    global totalCount
                    global failCount
                    totalCount += 1
                    if a or b:
                        failCount += 1
                        # print("%d|%d - %d%d%d%d"%(a,b,i0,i1,i2,i3))
                else:
                    edgeSet[c] = (f, i)

    unkn5 = set()
    l = 0
    from pathlib import Path
    from rays import Ray
    chunk = Path(r"E:\MHW\Merged")
    # chunk = Path(r"C:\Users\aguevara\Downloads")
    for sbc in chunk.rglob("*.sbc"):
        # sbc = r"E:\MHW\Merged\stage\st102\st102_A\col\st102_A_col.sbc"
        content = SBC(open(sbc, "rb").read())
        for obj in content.objects:
            faceInverseTest(obj.faces, obj.vertices)
    print("%.5f%%" % (failCount/totalCount*100))
    # print(str(sbc))
    # superTree = readCollisionTree(content.objects,content.cBVHCollision)
    # superTree.serialize()
    # print(superTree.exactCollision(Ray.randomRay()))
    # raise ValueError
#        for obj in content.objects:
#            faceTest(obj.faces,obj.vertices)
#    print(infinityCounter)
#    print(fuckupCounter)
#    print(newCounter)
#    print(infinityCounter/fuckupCounter)
    #    treeTest(obj)
    # megaTreeTest(content)
    # print(sbc)
    # for ix,obj in enumerate(content.objects):
    # print()
    # print (obj.sbcinfo.indexID )
    # boxTest(obj)
    # topBB = boxToVec(content.header.boundingBox)
    # treeBB = boxToVec(content.cBVHCollision.boundingBox)
    # if topBB != treeBB:
    #    raise ValueError
    # raise ValueError
#            for node in obj.bvhtree.AABBArray:
#                #print (node.unkn5)
#                typebin = bin(node.nodeType[0])[2:].zfill(8)
#                face = [int(b) for b in reversed(typebin[0:4])]
#                geom = [int(b) for b in reversed(typebin[4:8])]
#                rel = {(0,0):"E",(1,0):"F",(0,1):"N"}
#                structure = tuple([rel[f,g] for f,g in zip(face,geom)])
#                if structure == ("F","E","E","E"):
#                    unkn5.add(tuple(node.unkn5))
#                    if l != len(unkn5):
#                        l = len(unkn5)
#                        print (list(node.unkn5))
#                #print('|'.join([(str(u)+"/"+rel[(f,g)])for u,f,g in zip(node.unkn5,face,geom)]))
#            #print(ix)
#            #testMerge(obj)

"""
    from queue import Queue
    from TreeUtils import plotTree
    from pathlib import Path
    q = Queue()
    
    def checkPairs(sbc):
        for obj in sbc.objects:
            for pair in obj.pairs:
                if pair.face2 == 0xFFFF:
                    continue
                if pair.face1 > pair.face2:
                    print ("Relationship inversion!")
                if box1InBox2(getBoundingBox(obj,obj.faces[pair.face1]),
                              getBoundingBox(obj,obj.faces[pair.face2])):
                    print ("Face2 contains Face1")
    
    def waitForProcessing(q):
        while 1:
            sbc = q.get()
            content = SBC(open(sbc,"rb").read())
            checkPairs(content)
            q.task_done()
            
    num_threads = 16
    
    for i in range(num_threads):
      worker = Thread(target=waitForProcessing, args=(q,))
      worker.setDaemon(True)
      worker.start()
      
    chunk = Path(r"E:\MHW\Merged")
    for sbc in chunk.rglob("*.sbc"):
        q.put(sbc)
    q.join()
"""
"""
#Threaded plotting
    from threading import Thread
    from queue import Queue
    from TreeUtils import plotTree
    from pathlib import Path
    q = Queue()
    w = Queue()
    def waitForProcessing(q):
        while 1:
            tree,sbc = q.get()
            plotTree(tree,sbc)
            q.task_done()
    
    def generateWork(q,w):
        while 1:
            sbcpath =  w.get()
            content = SBC(open(sbcpath,"rb").read())
            tree = SBCToBVHTrees(content,sbcpath)
            q.put((tree,sbcpath))
            w.task_done()
    
    num_threads = 16
    
    for i in range(num_threads):
      worker = Thread(target=waitForProcessing, args=(q,))
      worker.setDaemon(True)
      worker.start()
    for i in range(num_threads):
      worker = Thread(target=generateWork, args=(q,w,))
      worker.setDaemon(True)
      worker.start()
      
    chunk = Path(r"E:\MHW\Merged")
    for sbc in chunk.rglob("*.sbc"):
        w.put(sbc)
    w.join()
    q.join()
"""
