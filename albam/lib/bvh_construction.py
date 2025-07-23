# bounding volume hierarchy
"""
Created on Fri Dec 13 00:07:04 2019

@author: AsteriskAmpersand
"""
import numpy as np
from functools import reduce
try:
    from primitive_geometry import MORTONLENGHT, QuadPair, PrimitiveTree, BoundingBox
    from low_level_op import radix_sort
except ImportError:
    from albam.lib.primitive_geometry import MORTONLENGHT, QuadPair, PrimitiveTree, BoundingBox
    from albam.lib.low_level_op import radix_sort


def set_remove(poset, val):
    poset.remove(val)
    return poset


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


# Generic node for building hierarchical spatial structures
# Represents either a single primitive (leaf) or a group of clusters/primitives (internal node).
# Determines its type (PRIMITIVE or NODE) based on whether its content is iterable
# Provides static methods for different clustering metrics (e.g., SAHMetric, EPOMetric)
# used to evaluate the cost of combining clusters.
class Cluster():
    # Constants for typization during clasterization
    EMPTY = 0
    PRIMITIVE = 1
    NODE = 2
    TYPEMAP = {EMPTY: "Empty", PRIMITIVE: "Primitive", NODE: "Node"}
    clusterID = 0

    def __init__(self, element):
        self.id = Cluster.clusterID
        Cluster.clusterID += 1
        self.content = element
        if not is_iterable(element):
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
                except StopIteration:
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
        except RuntimeError:
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
        selfstring = "\t" * level + Cluster.TYPEMAP[self.type] + "\n"
        children = "".join((i.tabbedString(level + 1)
                           for i in self.content if i)) if self.isNode() else ""
        return selfstring + children

    @staticmethod
    def SAHMetric(s1, s2):
        s = Cluster((s1, s2))

        def ratio(x):
            return x.surfaceArea() / s.surfaceArea() * x.count
        T = ratio(s1) + ratio(s2)
        return T  # cluster1.aabb.merge(cluster2.aabb).sah()

    @staticmethod
    def EPOMetric(s1, s2):
        s = Cluster((s1, s2))
        return s1.boundingBox().intersect(s2.boundingBox()).surfaceArea() / s.surfaceArea()

    @staticmethod
    def SAH_EPOMetric(s1, s2):
        return Cluster.SAHMetric(s1, s2) + Cluster.EPOMetric(s1, s2)


class BinaryCluster(Cluster):
    def __init__(self, element):
        super().__init__(element)
        if self.type == Cluster.NODE:
            assert len(self.content) == 2
            self.left = self.content[0]
            self.right = self.content[1]

    def merge(self):
        d1 = self.left.content
        d2 = self.right.content
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
            if self.left:
                self.left.mergeCompatible()
            if self.right:
                self.right.mergeCompatible()
            if self.left and self.left.isPrimitive() and \
                    self.right and self.right.isPrimitive():
                self.merge()
        return

    def collapse(self):
        # Collapses the tree into a Quad Bounding Volume Hierarchy
        # Checks is leaf(Primitive), method from Cluster
        if self.isPrimitive():
            # return QBVH(self)
            # collision for re6 didn't work with 0 nodes
            children = [QBVH(self)] + [QBVH(None) for _ in range(3)]
            return QBVH(Cluster((self,)), *children)
        # children of a quad node
        children = []

        def checkAddSide(side):
            if side:
                # if child is leaf(Prmitive)
                if side.isPrimitive():
                    children.append(QBVH(side))
                    children.append(QBVH(None))
                else:
                    children.append(side.left.collapse())
                    children.append(side.right.collapse())
        checkAddSide(self.left)
        checkAddSide(self.right)
        children += [QBVH(None) for i in range(4 - len(children))]
        # print(children)
        qnode = QBVH(self, *children)
        return qnode


# The QBVH class represents a Quad Bounding Volume Hierarchy
# The QBVH class distinguishes between three types of nodes:
# Primitive: A leaf node containing a single primitive (e.g., a triangle or quad).
# Node: An internal node with up to four children.
# Empty: A placeholder node with no content.
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
                def check(x):
                    return QBVH(None) if x is None else x
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

            def lshiftOr(x, y):
                return (x << 1) | y
            return [reduce(lshiftOr, primitive + node)] * 4

    def nodeId(self):
        if not self.isNode():
            raise NotImplementedError(
                "Empties and Primitives don't have subnodes.")
        else:
            return [self.ll.index(), self.lr.index(), self.rl.index(), self.rr.index()]

    def unkn5(self):
        return [0] * 4

    def AABB(self):
        return self.node.boundingBox()

    def childBoxes(self):
        boxes = []
        default = self.parent.childBoxes() if self.parent else [
            self.node.boundingBox()] * 4
        for ix, child in enumerate(self.children()):
            boxes.append(child.AABB() if child.isNode() or
                         child.isPrimitive() else default[ix])
        return boxes

    def extremaAABB(self, bbFunctor):
        boxes = self.childBoxes()

        def intersped(w):
            return [bbFunctor(entry)[w] for entry in boxes]
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
                    last, plast = child.indexize(last + 1, plast, self)
                elif child.isPrimitive():
                    child.setIndex(plast + 1)
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
            return [self] + sum([c.traverse() for c in self.children()], [])
        else:
            return [self]

    def separateTraverse(self):
        if not hasattr(self, "traversalBuffer"):
            if self.isNode():
                childElements = [c.separateTraverse() for c in self.children()]
                self.traversalBuffer = (
                    [self] + sum([c[0] for c in childElements], []), sum([c[1] for c in childElements], []))
            elif self.isPrimitive():
                self.traversalBuffer = ([], [self])
            else:
                self.traversalBuffer = ([], [])
        return self.traversalBuffer

    # returns tabbed string on print()
    def __repr__(self):
        return self.tabbedString()

    # Creates a string representation of the cluster for visualization
    # with indentation based on the level in the hierarchy
    def tabbedString(self, level=0):
        return ("\t" * level + Cluster.TYPEMAP[self.type] +
                '\n' +
                ''.join([child.tabbedString(level + 1) for child in self.children()]))

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
def exact_agglomerative_clustering(primitives, metric=Cluster.SAHMetric, **kwargs):
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
        set_remove(set_remove(clusters, left), right).add(
            BinaryCluster((left, right)))
    return clusters


# =============================================================================
# Approximate Agglomerative Clustering
# Efficient BVH Construction via Approximate Agglomerative Clustering - Gu, et al
# =============================================================================
def expRedFactory(c, alpha):
    def reductionFunction(x):
        return max(c * x**alpha, 1)
    return reductionFunction


def aproximate_agglomerative_clustering(primitives, metric=Cluster.SAHMetric, reduction=expRedFactory(1, 0.5),
                                        threshold=1, **kwargs):
    # BinaryCluster(Cluster) is a node that stores left and right children(?)
    # Convert primitives to BinaryClusters after sorting them by their bounding boxes
    clusters = [BinaryCluster(p) for p in morton_sort(primitives)]
    return combine_clusters(build_tree(clusters, metric, reduction, threshold), 1, metric)


def combine_clusters(clusters, n, metric):
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
        set_remove(set_remove(c, left), right).add(cp)
        cp.closest = findBestMatch(c, cp, metric)
        for ci in c:
            if ci.closest in [left, right]:
                ci.closest = findBestMatch(c, ci, metric)
    return c


def build_tree(primitives, metric, countReduction, threshold):
    if len(primitives) <= threshold:
        return combine_clusters(primitives, countReduction(threshold), metric)
    # The morton_partition function splits the list of primitives into two groups (l and r)
    # based on their Morton codes. This ensures spatial locality, as primitives close in space will
    # be grouped together.
    l, r = morton_partition(primitives)

    def build(x):
        return build_tree(x, metric, countReduction, threshold)
    return combine_clusters(build(l).union(build(r)), countReduction(len(primitives)), metric)


def morton_partition(encodable_list, metric=None, morton_point=0):
    """
    encountable_list: Primitive
    """
    # mortonLenght hardcoded to 32(number of bits in the Morton code)
    # bit determines which bit of the Morton code is currently being used to partition the list.
    bit = MORTONLENGHT - 1 - morton_point
    # if all bits processed or less than 3 primitives returns split list on two
    if bit == -1 or len(encodable_list) < 3:
        split = (len(encodable_list) + 1) // 2
        return encodable_list[:split], encodable_list[split:]

    # The key function extracts the value of the current bit (bit) from the Morton code of the element
    # at index x.
    # encodable_list[x].encode() computes the Morton code for the element.
    # The bitwise operation ((2 << bit) & ...) isolates the value of the current bit.
    def key(x):
        return ((2 << bit) & encodable_list[x].encode())  # >>32
    # If all elements in the list have the same value for the current bit
    # the function moves to the next bit (mortonPoint + 1) and tries again.
    left = 0
    right = len(encodable_list) - 1
    if key(left) == key(right):
        return morton_partition(encodable_list, metric, morton_point + 1)
    # The function uses a binary search approach to find the partition point.
    # it compares the Morton code values at left, right, and middlePoint to determine
    # whether to move left or right closer to the middle.
    while right - left > 1:
        middle_point = (left + right + 1) // 2
        if key(left) == key(middle_point):
            left = middle_point
        elif key(right) == key(middle_point):
            right = middle_point
        else:
            raise ValueError("Mathematical Impossibility")
    return encodable_list[:right], encodable_list[right:]


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
    median = (len(dimension) + 1) // 2 - 1
    lindices, rindices = [], []
    lset = set(dimension[:median + 1])
    for ax, dim in enumerate(indices):
        if ax == axis:
            lindices.append(dim[:median + 1])
            rindices.append(dim[median + 1:])
        else:
            l, r = [ix for ix in dim if ix in lset], [
                ix for ix in dim if ix not in lset]
            lindices.append(l)
            rindices.append(r)
    return BinaryCluster((_kdTreeSplit(lindices, access, (axis + 1) % len(mode), mode),
                          _kdTreeSplit(rindices, access, (axis + 1) % len(mode), mode)))


def kd_tree_split(primitives, ordering=deferredTripleSort, mode=CAPCOM, **kwargs):
    indices = deferredTripleSort(primitives, mode)
    coordinate = coordinateFunction(primitives)
    activatedModes = [partialPerm(perm, coordinate) for perm in mode]

    def access(x):
        return primitives[x]
    return [_kdTreeSplit(indices, access, 0, activatedModes)]


# =============================================================================
#  Naive Spatial Splits
# =============================================================================
def morton_sort(primitives):
    """
    Sorts primitives by their bounding boxes using morton codes
    primitives: list of SemiTri objects that stores face indices or other objects
    """
    def unpack(x):
        return [x.minPos, x.maxPos]

    def merge_op(x, y):
        return x.merge(y)
    # Create a list of bounding boxes unpacked from primitives(Tri)
    primitiveBoxes = [BoundingBox(unpack(p.boundingBox())) for p in primitives]
    # Run merge_op trough the list of bounding boxes starting with [0](why?)
    # combine two bounding boxes into a single bounding box that encompasses both
    # until all boxes are merged into one
    minima, maxima = unpack(reduce(merge_op, primitiveBoxes, primitiveBoxes[0]))
    # setBounds normalizes(?) bounding boxes towards minima and maxima and
    # encodes them into a single number by morton code then sorts them and returns sorted
    mapping = {p.setBounds(minima, maxima).encode(): p for p in primitives}
    return [mapping[key] for key in radix_sort(list(mapping.keys()), 8)]
    # return sorted(primitives,key = lambda x: x.setBounds(minima,maxima).encode())


def linear_split(cluster, metric):
    if len(cluster) == 1:
        return [c for c in cluster], []
    best = np.inf
    currentBest = None
    elements = iter(cluster)
    elementList = [element for element in elements]
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
        except RuntimeError:
            print("FAIL")
            raise
        if m < best:
            best = m
            currentBest = ix
    return elementList[:currentBest], elementList[currentBest:]


def spatial_splits(primitives, *args, **kwargs):

    clusters = [BinaryCluster(p) for p in morton_sort(primitives)]
    return [_spatialSplits(clusters, *args, **kwargs)]


def _spatialSplits(clusters, metric=Cluster.SAH_EPOMetric, partition=linear_split, **kwargs):
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
def hybrid_clustering(primitives, *args, **kwargs):
    # TODO - pick method based on length etc...
    return aproximate_agglomerative_clustering(primitives, *args, **kwargs)


# =============================================================================
# Final constructor functions
# =============================================================================
def indexize_ob(listing, key=None):
    for i, obj in enumerate(listing):
        if key is not None:
            key(obj).setIndex(i)
        else:
            obj.setIndex(i)
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


def primitive_to_sbc(primitives, clusteringFunction=spatial_splits, **kwargs):
    """
    Get a list of Tri objects and dictionary of options, sort them by their bounding boxes
    using morton codes, cluster them (BinaryCluster) and merge close ones
    primivtives: list of Tri(Primitive) objects stores a face indices in dataFace
    """
    # Adds _index attribute to primitive.dataFace and sets index
    indexize_ob(primitives, lambda x: x.dataFace)
    # Adds _index attribute to primitive and sets index
    indexize_ob(primitives)

    # Use morton codes to sort primitives by their bounding boxes
    # Then cluster them (BinaryCluster) and merge close ones
    # btree - binary tree
    btree = next(iter(clusteringFunction(primitives, **kwargs)))
    # Merges compatible Tris into QuadPair
    # qtree - quad tree
    btree.mergeCompatible()
    # Converting btree to Quad Bounding Volume Hierarchy
    qtree = btree.collapse()
    indexize_ob(qtree.subnodes())
    # The mergerReindex function is responsible for reindexing and merging primitives after the BVH
    # has been collapsed into a QBVH and compatible triangles have been merged into quads
    npair_primitives = mergerReindex(primitives, qtree.subprimitives())
    # nodes - list of nodes in the quad tree
    # pairPrimitives - list of primitives in the quad tree
    nodes, pairPrimitives = qtree.separateTraverse()
    indexize_ob(nodes)
    return npair_primitives, PrimitiveTree(qtree).refine([vert for p in primitives for vert in p.vertices])


# Spatial Bounding Cluster (SBC)
def trees_to_sbc_col(tree_list, clusteringFunction=spatial_splits, **kwargs):
    """
    tree_list: list of primitive geometry PrimitiveTree objects
    """
    indexize_ob(tree_list)
    qtree = next(iter(clusteringFunction(tree_list, **kwargs))).collapse()
    indexize_ob(qtree.subnodes())
    return PrimitiveTree(qtree)
