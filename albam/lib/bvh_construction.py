# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 00:07:04 2019

@author: AsteriskAmpersand
"""
import numpy as np
from functools import reduce
try:
    from albam.lib.primitive_geometry import mortonLength, QuadPair, PrimitiveTree, BoundingBox
    from albam.lib.low_level_op import radix_sort
except:
    from .primitive_geometry import mortonLength, QuadPair, PrimitiveTree, BoundingBox
    from .low_level_op import radix_sort


def setRemove(poset, val):
    poset.remove(val)
    return poset


def isIterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class Cluster():
    EMPTY = 0
    PRIMITIVE = 1
    NODE = 2
    typeMap = {EMPTY: "Empty", PRIMITIVE: "Primitive", NODE: "Node"}
    clusterID = 0

    def __init__(self, element):
        self.id = Cluster.clusterID
        Cluster.clusterID += 1
        self.content = element
        if not isIterable(element):
            self.type = Cluster.PRIMITIVE
            self.aabb = element.boundingBox()
            self.count = 1
        else:
            self.type = Cluster.NODE
            elements = iter(element)
            self.aabb = next(elements).boundingBox()
            while True:
                try:
                    self.aabb = self.aabb.merge(next(elements).boundingBox())
                except:
                    break
            self.count = sum(
                [i.count if hasattr(i, "count") else 1 for i in element])
        self.closest = None

    def isNode(self):
        return self.type == Cluster.NODE

    def isPrimitive(self):
        return self.type == Cluster.PRIMITIVE

    def boundingBox(self):
        return self.aabb

    def encode(self):
        if self.type == Cluster.PRIMITIVE:
            return self.content.encode()
        else:
            raise ValueError("Non primitive cannot be morton encoded.")

    def __iter__(self):
        try:
            return iter(self.content)
        except:
            return iter([self.content])

    def __hash__(self):
        return self.id

    def surfaceArea(self):
        return self.aabb.surfaceArea()

    def __eq__(self, cluster):
        return hash(self) == hash(cluster)

    def index(self):
        return self._index

    def setIndex(self, value):
        self._index = value
        return self

    def __repr__(self):
        return self.tabbedString()

    def tabbedString(self, level=0):
        selfstring = "\t"*level+Cluster.typeMap[self.type]+"\n"
        children = "".join((i.tabbedString(level+1)
                           for i in self.content if i)) if self.isNode() else ""
        return selfstring+children

    @staticmethod
    def SAHMetric(s1, s2):
        s = Cluster((s1, s2))
        def ratio(x): return x.surfaceArea()/s.surfaceArea()*x.count
        T = ratio(s1)+ratio(s2)
        return T  # cluster1.aabb.merge(cluster2.aabb).sah()

    @staticmethod
    def EPOMetric(s1, s2):
        s = Cluster((s1, s2))
        return s1.boundingBox().intersect(s2.boundingBox()).surfaceArea()/s.surfaceArea()

    @staticmethod
    def SAH_EPOMetric(s1, s2):
        return Cluster.SAHMetric(s1, s2)+Cluster.EPOMetric(s1, s2)


class BinaryCluster(Cluster):
    def __init__(self, element):
        super().__init__(element)
        if self.type == Cluster.NODE:
            assert len(self.content) == 2
            self.l = self.content[0]
            self.r = self.content[1]

    def merge(self):
        d1 = self.l.content
        d2 = self.r.content
        if d1.mergeable(d2):
            newQuad = QuadPair(d1, d2)
            self.type = Cluster.PRIMITIVE
            self.content = newQuad
            self.count = 1
            return True
        if d2.mergeable(d1):
            newQuad = QuadPair(d2, d1)
            self.type = Cluster.PRIMITIVE
            self.content = newQuad
            self.count = 1
            return True
        return False

    def exactCollision(self, ray):
        if self.type == Cluster.PRIMITIVE:
            return self.content.exactCollision(ray)

    def mergeCompatible(self):
        # Merges compatible Tris into QuadPair
        if self.isNode():
            if self.l:
                self.l.mergeCompatible()
            if self.r:
                self.r.mergeCompatible()
            if self.l and self.l.isPrimitive() and \
                    self.r and self.r.isPrimitive():
                self.merge()
        return

    def collapse(self):
        if self.isPrimitive():
            return QBVH(self)
        children = []

        def checkAddSide(side):
            if side:
                if side.isPrimitive():
                    children.append(QBVH(side))
                    children.append(QBVH(None))
                else:
                    children.append(side.l.collapse())
                    children.append(side.r.collapse())
        checkAddSide(self.l)
        checkAddSide(self.r)
        children += [QBVH(None) for i in range(4-len(children))]
        # print(children)
        qnode = QBVH(self, *children)
        return qnode


class QBVH():
    def __init__(self, binaryCluster, ll=None, lr=None, rl=None, rr=None):
        self.parent = None
        if binaryCluster is None:
            self.type = Cluster.EMPTY
            self.node = None
        else:
            self.type = binaryCluster.type
            self.node = binaryCluster
            if not self.isPrimitive():
                def check(x): return QBVH(None) if x is None else x
                self.ll = check(ll)
                self.lr = check(lr)
                self.rl = check(rl)
                self.rr = check(rr)

    def typePair(self):
        matrix = {Cluster.EMPTY: (0, 0), Cluster.PRIMITIVE: (
            1, 0), Cluster.NODE: (0, 1)}
        return matrix[self.type]

    def boundingBox(self):
        if not self.isEmpty():
            return self.node.boundingBox()
        else:
            raise ValueError("Empty has no bounding box")

    def index(self):
        if self.isEmpty():
            return 0
        if self.isPrimitive():
            return self.node.content.index()
        if self.isNode():
            return self._index

    def setIndex(self, val):
        self._index = val
        return self

    def isEmpty(self):
        return self.type == Cluster.EMPTY

    def isNode(self):
        return self.type == Cluster.NODE

    def isPrimitive(self):
        return self.type == Cluster.PRIMITIVE

    def typeMask(self):
        if not self.isNode():
            raise NotImplementedError(
                "Empties and Primitives don't have a type mask.")
        else:
            primitive, node = list(map(list, map(reversed, zip(
                *[subnode.typePair() for subnode in [self.ll, self.lr, self.rl, self.rr]]))))

            def lshiftOr(x, y): return (x << 1) | y
            return [reduce(lshiftOr, primitive+node)]*4

    def nodeId(self):
        if not self.isNode():
            raise NotImplementedError(
                "Empties and Primitives don't have subnodes.")
        else:
            return [self.ll.index(), self.lr.index(), self.rl.index(), self.rr.index()]

    def unkn5(self):
        return [0]*4

    def AABB(self):
        return self.node.boundingBox()

    def childBoxes(self):
        boxes = []
        default = self.parent.childBoxes() if self.parent else [
            self.node.boundingBox()]*4
        for ix, child in enumerate(self.children()):
            boxes.append(child.AABB() if child.isNode()
                         or child.isPrimitive() else default[ix])
        return boxes

    def extremaAABB(self, bbFunctor):
        boxes = self.childBoxes()
        def intersped(w): return [bbFunctor(entry)[w] for entry in boxes]
        x, y, z = intersped(0), intersped(1), intersped(2)
        return {"xArray": x, "yArray": y, "zArray": z}

    def minAABB(self):
        return self.extremaAABB(lambda x: x.minPos)

    def maxAABB(self):
        return self.extremaAABB(lambda x: x.maxPos)

    def serialize(self):
        return {"nodeType": self.typeMask(),
                "nodeId": self.nodeId(),
                "unkn5": self.unkn5(),
                "minAABB": self.minAABB(),
                "maxAABB": self.maxAABB()
                }

    def setParent(self, parent):
        self.parent = parent

    def indexize(self, start=0, primitive=0, parent=None):
        self.setParent(parent)
        self.setIndex(start)
        last = start
        plast = primitive
        if self.isNode():
            for child in self.children():
                if child.isNode():
                    last, plast = child.indexize(last+1, plast, self)
                elif child.isPrimitive():
                    child.setIndex(plast+1)
                    child.setParent(self)
                    plast += 1
        return last, plast

    def __contains__(self, ray):
        if self.isEmpty():
            return False
        if self.isPrimitive():
            return self.node.exactCollision(ray)
        if self.isNode():
            if ray in self.node.boundingBox():
                return any([ray in c for c in self.children()])
            else:
                return False

    def children(self):
        if self.isNode():
            return [self.ll, self.lr, self.rl, self.rr]
        else:
            return []

    def traverse(self):
        if self.isNode():
            return [self]+sum([c.traverse() for c in self.children()], [])
        else:
            return [self]

    def separateTraverse(self):
        if not hasattr(self, "traversalBuffer"):
            if self.isNode():
                childElements = [c.separateTraverse() for c in self.children()]
                self.traversalBuffer = (
                    [self]+sum([c[0] for c in childElements], []), sum([c[1] for c in childElements], []))
            elif self.isPrimitive():
                self.traversalBuffer = ([], [self])
            else:
                self.traversalBuffer = ([], [])
        return self.traversalBuffer

    def __repr__(self):
        return self.tabbedString()

    def tabbedString(self, level=0):
        return "\t"*level+Cluster.typeMap[self.type]+'\n'+''.join([child.tabbedString(level+1) for child in self.children()])

    def __len__(self):
        if not hasattr(self, "traversalBuffer"):
            self.separateTraverse()
        return len(self.traversalBuffer[0])

    def subnodes(self):
        if not hasattr(self, "traversalBuffer"):
            self.separateTraverse()
        return self.traversalBuffer[0]

    def subprimitives(self):
        if not hasattr(self, "traversalBuffer"):
            self.separateTraverse()
        return self.traversalBuffer[1]


# =============================================================================
# Exact Agglomerative Clustering O(N^3)
# =============================================================================
def exactAgglomerativeClustering(primitives, metric=Cluster.SAHMetric, **kwargs):
    clusters = set((BinaryCluster(p) for p in primitives))
    while len(clusters) > 1:
        best = np.inf
        for ci in clusters:
            for cj in clusters:
                if ci != cj:
                    m = metric(ci, cj)
                    if m < best:
                        best = metric(ci, cj)
                        left = ci
                        right = cj
        setRemove(setRemove(clusters, left), right).add(
            BinaryCluster((left, right)))
    return clusters


# =============================================================================
# Approximate Agglomerative Clustering
# Efficient BVH Construction via Approximate Agglomerative Clustering - Gu, et al
# =============================================================================
def expRedFactory(c, alpha):
    def reductionFunction(x):
        return max(c*x**alpha, 1)
    return reductionFunction


def aproximateAgglomerativeClustering(primitives, metric=Cluster.SAHMetric, reduction=expRedFactory(1, 0.5), threshold=1, **kwargs):
    clusters = [BinaryCluster(p) for p in mortonSort(primitives)]
    return combineClusters(buildTree(clusters, metric, reduction, threshold), 1, metric)


def combineClusters(clusters, n, metric):
    c = set(clusters)
    if len(c) == 1:
        return c
    for ci in clusters:
        ci.closest = findBestMatch(c, ci, metric)
    while len(c) > n:
        best = np.inf
        for ci in c:
            if metric(ci, ci.closest) < best:
                best = metric(ci, ci.closest)
                left = ci
                right = ci.closest
        cp = BinaryCluster((left, right))
        setRemove(setRemove(c, left), right).add(cp)
        cp.closest = findBestMatch(c, cp, metric)
        for ci in c:
            if ci.closest in [left, right]:
                ci.closest = findBestMatch(c, ci, metric)
    return c


def buildTree(primitives, metric, countReduction, threshold):
    if len(primitives) <= threshold:
        return combineClusters(primitives, countReduction(threshold), metric)
    l, r = mortonPartition(primitives)
    def build(x): return buildTree(x, metric, countReduction, threshold)
    return combineClusters(build(l).union(build(r)), countReduction(len(primitives)), metric)


def mortonPartition(encodableList, metric=None, mortonPoint=0):
    bit = mortonLength-1-mortonPoint
    if bit == -1 or len(encodableList) < 3:
        return encodableList[:(len(encodableList)+1)//2], encodableList[(len(encodableList)+1)//2:]

    def key(x): return ((2 << bit) & encodableList[x].encode())  # >>32
    left = 0
    right = len(encodableList)-1
    if key(left) == key(right):
        return mortonPartition(encodableList, metric, mortonPoint+1)
    while right-left > 1:
        middlePoint = (left+right+1)//2
        if key(left) == key(middlePoint):
            left = middlePoint
        elif key(right) == key(middlePoint):
            right = middlePoint
        else:
            raise ValueError("Mathematical Impossibility")
    return encodableList[:right], encodableList[right:]


def findBestMatch(clusterList, ci, metric):
    best = np.inf
    match = None
    for cj in clusterList:
        if ci != cj:
            m = metric(ci, cj)
            if m < best:
                best = metric(ci, cj)
                match = cj
    return match


# =============================================================================
#  KD-Tree
# =============================================================================
def coordinateFunction(primitives):
    return lambda x: primitives[x].barycenter()


def firstPermutation(w, coordinate):
    return coordinate(w).x, coordinate(w).y, coordinate(w).z


def secondPermutation(w, coordinate):
    return coordinate(w).y, coordinate(w).z, coordinate(w).x


def thirdPermutation(w, coordinate):
    return coordinate(w).z, coordinate(w).x, coordinate(w).y


def firstCompactPermutation(w, coordinate):
    return coordinate(w).x, coordinate(w).z, coordinate(w).y


def secondCompactPermutation(w, coordinate):
    return coordinate(w).z, coordinate(w).x, coordinate(w).y


def partialPerm(f, c):
    return lambda x: f(x, c)


TRADITIONAL = [firstPermutation, secondPermutation, thirdPermutation]
CAPCOM = [firstCompactPermutation, secondCompactPermutation]


def deferredTripleSort(primitives, mode=CAPCOM):
    indices = np.array(range(len(primitives)))
    coordinate = coordinateFunction(primitives)
    return [sorted(indices.copy(), key=partialPerm(perm, coordinate)) for perm in mode]


def _kdTreeSplit(indices, access, axis, mode):
    if len(indices[axis]) < 2:
        return BinaryCluster(access(indices[axis][0]))
    dimension = indices[axis]
    median = (len(dimension)+1)//2 - 1
    lindices, rindices = [], []
    lset = set(dimension[:median+1])
    for ax, dim in enumerate(indices):
        if ax == axis:
            lindices.append(dim[:median+1])
            rindices.append(dim[median+1:])
        else:
            l, r = [ix for ix in dim if ix in lset], [
                ix for ix in dim if ix not in lset]
            lindices.append(l)
            rindices.append(r)
    return BinaryCluster((_kdTreeSplit(lindices, access, (axis+1) % len(mode), mode),
                          _kdTreeSplit(rindices, access, (axis+1) % len(mode), mode)))


def kdTreeSplit(primitives, ordering=deferredTripleSort, mode=CAPCOM, **kwargs):
    indices = deferredTripleSort(primitives, mode)
    coordinate = coordinateFunction(primitives)
    activatedModes = [partialPerm(perm, coordinate) for perm in mode]
    def access(x): return primitives[x]
    return [_kdTreeSplit(indices, access, 0, activatedModes)]


# =============================================================================
#  Naive Spatial Splits
# =============================================================================
def mortonSort(primitives):
    def unpack(x): return [x.minPos, x.maxPos]
    def mergeOp(x, y): return x.merge(y)
    primitiveBoxes = [BoundingBox(unpack(p.boundingBox())) for p in primitives]
    minima, maxima = unpack(reduce(mergeOp, primitiveBoxes, primitiveBoxes[0]))
    mapping = {p.setBounds(minima, maxima).encode(): p for p in primitives}
    return [mapping[key] for key in radix_sort(list(mapping.keys()), 8)]
    # return sorted(primitives,key = lambda x: x.setBounds(minima,maxima).encode())


def linearSplit(cluster, metric):
    if len(cluster) == 1:
        return [c for c in cluster], []
    best = np.inf
    currentBest = None
    elements = iter(cluster)
    elementList = [l for l in elements]
    if len(elementList) == 2:
        return elementList[:1], elementList[1:]
    left = elementList[0]
    right = Cluster(elementList[-1])
    clusterList = [right]
    for ele in reversed(elementList[-2:0:-1]):
        right = Cluster((right, ele))
        clusterList.append(right)
    for ix in range(1, len(elementList)):
        m = metric(left, clusterList[-ix])
        try:
            left = Cluster((left, elementList[ix]))
        except:
            print("FAIL")
            raise
        if m < best:
            best = m
            currentBest = ix
    return elementList[:currentBest], elementList[currentBest:]


def spatialSplits(primitives, *args, **kwargs):

    clusters = [BinaryCluster(p) for p in mortonSort(primitives)]
    return [_spatialSplits(clusters, *args, **kwargs)]


def _spatialSplits(clusters, metric=Cluster.SAH_EPOMetric, partition=linearSplit, **kwargs):
    if len(clusters) == 1:
        return clusters[0]
    l, r = partition(clusters, metric)
    if l and r:
        lcluster, rcluster = _spatialSplits(
            l, metric, partition), _spatialSplits(r, metric, partition)
        return BinaryCluster((lcluster, rcluster))
    elif l:
        lcluster = _spatialSplits(l, metric, partition)
        return lcluster
    elif r:
        rcluster = _spatialSplits(r, metric, partition)
        return rcluster
    else:
        raise ValueError("Cannot parse empty cluster list.")


# =============================================================================
#  Hybrid method depending on length of primitives
# =============================================================================
def HybridClustering(primitives, *args, **kwargs):
    # TODO - pick method based on length etc...
    return aproximateAgglomerativeClustering(primitives, *args, **kwargs)


# =============================================================================
# Final constructor functions
# =============================================================================
def indexize_ob(listing, key=None):
    for ix, obj in enumerate(listing):
        if key is not None:
            key(obj).setIndex(ix)
        else:
            obj.setIndex(ix)
    return listing


def mergerReindex(primitives, qprimitives):
    tally = 0
    qpIndices = {}
    mergeset = set()
    pairPrimitiveList = []
    for qp in qprimitives:
        if type(qp.node.content) is QuadPair:
            qpIndices[min(qp.node.content.dataFaces[0].index(),
                          qp.node.content.dataFaces[1].index())] = qp.node.content
            mergeset.add(qp.node.content.dataFaces[0].index())
            mergeset.add(qp.node.content.dataFaces[1].index())
    for obj in primitives:
        if obj.index() in mergeset:
            if obj.index() in qpIndices:
                qpIndices[obj.index()].setIndex(tally)
                pairPrimitiveList.append(qpIndices[obj.index()])
                tally += 1
        else:
            obj.setIndex(tally)
            pairPrimitiveList.append(obj)
            tally += 1
    return pairPrimitiveList


def primitiveToSBC(primitives, clusteringFunction=spatialSplits, **kwargs):
    indexize_ob(primitives, lambda x: x.dataFace)
    indexize_ob(primitives)
    btree = next(iter(clusteringFunction(primitives, **kwargs)))
    btree.mergeCompatible()
    qtree = btree.collapse()
    indexize_ob(qtree.subnodes())
    npairPrimitives = mergerReindex(primitives, qtree.subprimitives())
    nodes, pairPrimitives = qtree.separateTraverse()
    indexize_ob(nodes)
    return npairPrimitives, PrimitiveTree(qtree).refine([vert for p in primitives for vert in p.vertices])


def treesToSBCCol(treeList, clusteringFunction=spatialSplits, **kwargs):
    indexize_ob(treeList)
    qtree = next(iter(clusteringFunction(treeList, **kwargs))).collapse()
    indexize_ob(qtree.subnodes())
    return PrimitiveTree(qtree)
