import bpy
import bmesh
from kaitaistruct import KaitaiStream
import colorsys
import numpy as np
from mathutils import Vector
from io import BytesIO


from albam.registry import blender_registry
from albam.vfs import VirtualFileData
from .structs.sbc_156 import Sbc156
from .structs.sbc_21 import Sbc21
from albam.lib.primitive_geometry import eps, Tri
import albam.lib.primitive_geometry as geo
import albam.lib.bvh_construction as bvh
import albam.lib.common_op as common

SBC_CLASS_MAPPER = {
    49: Sbc156,
    255: Sbc21,
}


class TriangulationRequiredError(Exception):
    pass


class ExportingFailedError(Exception):
    pass


class MaterialMissingError(Exception):
    pass


class SBCObject():
    def __init__(self, info, BVHTree, faces, vertices, pairs):
        self.sbcinfo = info
        self.bvhtree = BVHTree
        self.faces = bvh.indexize_ob(
            [geo.Tri(face, vertices) for face in faces])
        self.vertices = vertices
        self.pairs = bvh.indexize_ob([geo.QuadPair(self.faces[pair.face_01], self.faces[pair.face_02])
                                         if pair.face_02 != 0xFFFF else
                                         self.faces[pair.face_01]
                                         for pair in pairs])


# Very smartass way to dynamically create a list with 44 colors
class counter():
    def __init__(self):
        self.i = 0

    def count(self):
        self.i += 1
        return self.i


i = counter()
def cycle(): return [0.4, 0.6, 0.8, 1.0][i.count() % 4]
palette = [colorsys.hsv_to_rgb(c/55, 1.0, cycle()) for c in range(44)]
palette = [(i[0], i[1], i[2], 1.0) for i in palette]


@blender_registry.register_import_function(app_id="re0", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re1", extension='sbc', file_category="COLLISION")
# @blender_registry.register_import_function(app_id="re5", extension='sbc', file_category="COLLISION")
# @blender_registry.register_import_function(app_id="re6", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="rev1", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="rev2", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="dd", extension='sbc', file_category="COLLISION")
def load_sbc(file_item, context):
    app_id = file_item.app_id
    sbc_bytes = file_item.get_bytes()
    sbc_version = sbc_bytes[3]
    assert sbc_version in SBC_CLASS_MAPPER, f"Unsupported version: {sbc_version}"
    SbcCls = SBC_CLASS_MAPPER[sbc_version]
    sbc = SbcCls.from_bytes(sbc_bytes)
    sbc._read()

    bl_object_name = file_item.display_name
    bl_object = bpy.data.objects.new(bl_object_name, None)

    cBVH = [b for i, b in enumerate(sbc.sbc_bvhc)]
    faceCollection = [fc for i, fc in enumerate(sbc.faces)]
    vertexCollection = [vc for i, vc in enumerate(sbc.vertices)]
    pairCollection = [pc for i, pc in enumerate(sbc.pairs_collections)]
    objects = []

    print("sbc type {}".format(sbc_version))
    for ix, ob_info in enumerate(sbc.sbc_info):
        ps, pc = ob_info.pairs_start, ob_info.pairs_count
        fs, fc = ob_info.faces_start, ob_info.face_count
        vs, vc = ob_info.vertex_start, ob_info.vertex_count
        obj = SBCObject(ob_info, cBVH[ix], faceCollection[fs:fs+fc],
                        vertexCollection[vs:vs+vc], pairCollection[ps:ps+pc])
        objects.append(obj)

    print("num sbc objects {}".format(len(objects)))
    for obj in objects:
        mesh, ob = create_collision_mesh(obj)
        ob.parent = bl_object
    for i, typing in enumerate(sbc.collision_types):
        empty = createLinkObject(typing)
        empty.parent = bl_object

    bl_object.albam_asset.original_bytes = sbc_bytes
    bl_object.albam_asset.app_id = app_id
    bl_object.albam_asset.relative_path = file_item.relative_path
    bl_object.albam_asset.extension = file_item.extension

    exportable = context.scene.albam.exportable.file_list.add()
    exportable.bl_object = bl_object

    context.scene.albam.exportable.file_list.update()
    return bl_object


def create_collision_mesh(sbcObject):
    mesh, obj = createMesh("CollisionMesh.000", decomposeSBCObject(sbcObject))
    obj["Type"] = "SBC_Mesh"
    obj["indexID"] = str(sbcObject.sbcinfo.index_id)
    return mesh, obj


def createLinkObject(link_ob):
    sbcEmpty = common.createRootNub("SBC Stage Link.000")
    sbcEmpty["Type"] = "SBC_Link"
    sbcEmpty["unk_01"] = link_ob.unk_01
    sbcEmpty["unk_02"] = link_ob.unk_02
    sbcEmpty["unk_03"] = link_ob.unk_03
    sbcEmpty["unk_04"] = link_ob.unk_04
    sbcEmpty["jp_path"] = link_ob.jp_path
    return sbcEmpty


def decomposeSBCObject(sbcObject):
    sbcGeom = {}
    sbcGeom["vertices"] = [(vert.x/100, vert.z/100, vert.y/100)
                           for vert in sbcObject.vertices]
    sbcGeom["faces"] = [face.dataFace.vert for face in sbcObject.faces]
    sbcGeom["materials"] = materialsFromSBC(sbcObject)
    return sbcGeom


def materialsFromSBC(sbcObject):
    materials = {}
    for ix, face in enumerate(sbcObject.faces):
        if face.type not in materials:
            materials[face.type] = []
        materials[face.type].append(ix)
    return materials


def createMesh(name, meshpart):
    blenderMesh = bpy.data.meshes.new(name)
    blenderMesh.from_pydata(meshpart["vertices"], [], meshpart["faces"])
    blenderMesh.update()
    blenderObject = bpy.data.objects.new(name, blenderMesh)
    # bpy.context.scene.objects.link(blenderObject)
    bpy.context.collection.objects.link(blenderObject)

    bm = bmesh.new()
    bm.from_mesh(blenderMesh)
    bm.faces.ensure_lookup_table()
    for ix, material in enumerate(meshpart["materials"]):
        mat = bpy.data.materials.new(name="Type %03d" % material)
        try:
            mat.diffuse_color = palette[material]
        except IndexError:
            colorsys.hsv_to_rgb(0, 0, 0)
            print("Unknown colision type: %d" % material)
        blenderMesh.materials.append(mat)
        for face in meshpart["materials"][material]:
            bm.faces[face].material_index = ix

    bm.to_mesh(blenderMesh)
    return blenderMesh, blenderObject


def cycles(verts):
    return [(verts[i % 3].index, verts[(i+1) % 3].index) for i in range(len(verts))]


@blender_registry.register_export_function(app_id="re1", extension="sbc")
def export_sbc(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    Sbc = Sbc21

    src_sbc = Sbc.from_bytes(asset.original_bytes)
    src_sbc._read()
    dst_sbc = Sbc()

    meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    links = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    clones = [common.cloneMesh(mesh) for mesh in meshes]
    vertList = []
    trisList = []
    quadList = []
    sbcsList = []
    meshmetadata = []
    errors = []
    options = {"clusteringFunction": bvh.HybridClustering,
               "metric": bvh.Cluster.SAHMetric,
               "partition": bvh.mortonPartition,
               "mode": bvh.CAPCOM}
    vfiles = []
    print("Initiate export")
    for mesh in clones:
        try:
            vertices, tris = mesh_to_tri(mesh)
        except TriangulationRequiredError:
            errors.append("%s requires triangulating." % mesh.name)
        print("Mesh processed")
        quads, sbc = bvh.primitiveToSBC(tris, **options)
        vertList.append(vertices)
        trisList.append(tris)
        quadList.append(quads)
        sbcsList.append(sbc)
        meshmetadata.append({"indexID": mesh["indexID"]})
        parentTree = bvh.treesToSBCCol(sbcsList, **options)
        final_size, serialized = build_sbc(bl_obj, src_sbc, dst_sbc, vertList, trisList, quadList, sbcsList,
                              links, parentTree, meshmetadata)
        stream = KaitaiStream(BytesIO(bytearray(final_size)))
        dst_sbc._check()
        dst_sbc._write(stream)
        sbc_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
        vfiles.append(sbc_vf)
    for clone in clones:
        common.delete_ob(clone)
    return vfiles


def build_sbc(bl_obj, src_sbc, dst_sbc, verts, tris, quads, sbcs, links, parentTree, meshmetadata):
    def tally(x): return sum(map(len, x))
    # headerData = formHeader(len(verts), tally(verts), tally(tris), tally(
    #    quads), len(links), tally(sbcs+[parentTree]), parentTree)
    _init_sbc_header(bl_obj, src_sbc, dst_sbc, len(verts), len(links), tally(quads), tally(tris),
                     tally(verts), parentTree, tally(sbcs+[parentTree]))
    # header = buildHeader(headerData)
    # cBVH = list(map(buildCollision,sbcs))
    dst_sbc.sbc_bvhc = [_serialize_bvhc(dst_sbc, sbc) for sbc in sbcs]

    # cBVHCollision = buildCollision(parentTree)
    dst_sbc.bvh = _serialize_bvhc(dst_sbc, parentTree)

    # faceCollection = list(map(buildFaces, tris))
    dst_sbc.faces = [_serialize_faces(dst_sbc, face) for face in tris][0]

    # vertexCollection = list(map(buildVertices, verts))
    dst_sbc.vertices = [_serialize_vertices(dst_sbc, v) for v in verts][0]

    # collisionTypes = list(map(buildTypes, links))
    dst_sbc.collision_types = [_serialize_col_types(dst_sbc, link) for link in links]

    # pairCollection = list(map(buildPairs, quads))
    dst_sbc.pairs_collections = [_serialize_pairs(dst_sbc, p) for p in quads][0]

    # infoCollection = buildInfo(
    #    header, tris, verts, collisionTypes, quads, cBVH, cBVHCollision, meshmetadata)
    dst_sbc.sbc_info = _serialize_infos(dst_sbc, tris, verts, dst_sbc.collision_types,
                                        quads, dst_sbc.sbc_bvhc, dst_sbc.bvh, meshmetadata)

    bvhc_size = 0
    for i, bvhc in enumerate(dst_sbc.sbc_bvhc):
        bvhc_size += 64 + bvhc.node_count * 112

    bvh_size = 64 + dst_sbc.bvh.node_count * 112

    final_size = sum((
        84,
        dst_sbc.header.object_count * 80,
        bvhc_size,
        bvh_size,
        dst_sbc.header.face_count * 32,
        dst_sbc.header.vertex_count * 16,
        dst_sbc.header.stage_count * 32,
        dst_sbc.header.pair_count * 10,
    ))

    #def flatten(x): return b''.join(x)
    #return (header +
    #        flatten(infoCollection) +
    #        flatten(cBVH) +
    #        cBVHCollision +
    #        flatten(faceCollection) +
    #        flatten(vertexCollection) +
    #        flatten(collisionTypes) +
    #        flatten(pairCollection))
    return final_size, dst_sbc


def _init_sbc_header(bl_obj, src_sbc, dst_sbc, object_count, stage_count, pair_count, face_count,
                      vertex_count, parent_tree, aabb_count):
    dst_sbc_header = dst_sbc.SbcHeader(_parent=dst_sbc, _root=dst_sbc._root)
    bbox_data = parent_tree.boundingBox().serialize()
    bbox = dst_sbc.Bbox(_parent=dst_sbc_header, _root=dst_sbc._root)
    bbox.min = [v for v in bbox_data["minPos"].values()]
    bbox.max = [v for v in bbox_data["maxPos"].values()]
    dst_sbc_header.__dict__.update(dict(
        magic=b"SBC\xFF",
        unk_00=src_sbc.header.unk_00,
        unk_02=0,
        unk_03=0,
        object_count=object_count,
        stage_count=stage_count,
        pair_count=pair_count,
        face_count=face_count,
        vertex_count=vertex_count,
        nulls=[0, 0, 0, 0],
        box=bbox,
        bb_size=0x70*(aabb_count),
    ))

    dst_sbc_header._check()
    dst_sbc.header = dst_sbc_header
    return dst_sbc_header


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


def _serialize_bvhc(dst_sbc, bvhc_data):
    bvh_col = dst_sbc.BvhCollision(_parent=dst_sbc, _root=dst_sbc._root)
    bbox = dst_sbc.Bbox(_parent=bvh_col, _root=dst_sbc._root)
    bvh_node = dst_sbc.BvhNode(_parent=bvh_col, _root=dst_sbc._root)
    aabb = dst_sbc.AabbBlock(_parent=bvh_node, _root=dst_sbc._root)
    bvhc_raw = bvhc_data.primitiveSerialize()

    bvh_col.bvhc = [1128814146, 2008120100]  # Bound Volume Hierarchy Collision Identifier
    bvh_col.soh = bvhc_raw["SOH"]
    bvh_col.unk_01 = 0
    bbox_data = bvhc_raw["boundingBox"]
    bbox.min = [v for v in bbox_data["minPos"].values()]
    bbox.max = [v for v in bbox_data["maxPos"].values()]
    bvh_col.bounding_box = bbox
    bvh_col.node_count = bvhc_raw["nodeCount"]
    bvh_col.nulls = [0, 0, 0]
    bvh_nodes = []
    for bvnode in bvhc_raw["AABBArray"]:
        bvh_node.node_type = bvnode["nodeType"]
        bvh_node.node_id = bvnode["nodeId"]
        bvh_node.unk_05 = 0  # 0xCDCDCDCD
        min_aabb = bvnode["minAABB"]
        aabb.x = min_aabb["xArray"]
        aabb.y = min_aabb["yArray"]
        aabb.z = min_aabb["zArray"]
        bvh_node.min_aabb = aabb
        max_aabb = bvnode["maxAABB"]
        aabb.x = max_aabb["xArray"]
        aabb.y = max_aabb["yArray"]
        aabb.z = max_aabb["zArray"]
        bvh_node.max_aabb = aabb
        bvh_nodes.append(bvh_node)
    bvh_col.nodes = bvh_nodes
    bvh_col._check()
    print("SBC BVH started")
    return bvh_col


def buildCollision(sbcTree):
    return cBVHCollision.build(sbcTree.primitiveSerialize())


def buildFaces(faces):
    return b''.join([Face.build(f.triSerialize()) for f in faces])


def _serialize_faces(dst_sbc, face_data):
    faces = []
    face = dst_sbc.Face(_parent=dst_sbc, _root=dst_sbc._root)
    print("lenght of face data is {}".format(len(face_data)))
    for f in face_data:
        face_raw = f.triSerialize()
        face.normal = face_raw["normal"]
        face.vert = face_raw["vert"]
        face.type = face_raw["type"]
        face.nulls = face_raw["null1"]
        face.adjacent = face_raw["adjacent"]
        face.nulls_01 = face_raw["null2"]
        face.nulls_02 = face_raw["null3"]
        face._check()
        faces.append(face)
    return faces


def buildVertices(vertices):
    return b''.join([Vertex.build(geo.vec_unfold(v)) for v in vertices])


def _serialize_vertices(dst_sbc, vertex_data):
    vertices = []
    dst_vertex = dst_sbc.Vertex(_parent=dst_sbc, _root=dst_sbc._root)
    for v in vertex_data:
        vertex_raw = geo.vec_unfold(v)
        dst_vertex.x = vertex_raw["x"]
        dst_vertex.y = vertex_raw["y"]
        dst_vertex.z = vertex_raw["z"]
        dst_vertex.w = vertex_raw["w"]
        dst_vertex._check()
        vertices.append(dst_vertex)
    return vertices


def buildTypes(typing):
    return CollisionType.build(formTypes(typing))


def formTypes(typing):
    return {typingName: typing[typeNameMapping[typingName]] for typingName in typeNameMapping}


def _serialize_col_types(dst_sbc, col_types_data):
    coltype = dst_sbc.CollisionType(_parent=dst_sbc, _root=dst_sbc._root)
    coltype.unk_01 = col_types_data["unk_01"]
    coltype.unk_02 = col_types_data["unk_02"]
    coltype.unk_03 = col_types_data["unk_03"]
    coltype.unk_04 = [v for v in col_types_data["unk_04"]]
    coltype.jp_path = col_types_data["jp_path"]
    coltype._check()
    return coltype


def _serialize_pairs(dst_sbc, pairs_data):
    pairs = []
    pair = dst_sbc.SFacePair(_parent=dst_sbc, _root=dst_sbc._root)
    for pd in pairs_data:
        pair_raw = pd.primitiveSerialize()
        pair.face_01 = pair_raw["face1"]
        pair.face_02 = pair_raw["face2"]
        pair.quad_order = pair_raw["quadOrder"]
        pair.type = pair_raw["type"]
        pair._check()
        pairs.append(pair)
    return pairs


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


def _serialize_infos(dst_sbc, faces, vertices, stages, pairs, sbcs, sbcC, metadata):
    f0, v0, p0 = 0, 0, 0,
    infos = []
    info = dst_sbc.Info(_parent=dst_sbc, _root=dst_sbc._root)
    bbox = dst_sbc.Bbox(_parent=info, _root=dst_sbc._root)
    for f, v, p, s, m in zip(faces, vertices, pairs, sbcs, metadata):
        bbox_data = getVertexBox(v).serialize()
        bbox.min = [v for v in bbox_data["minPos"].values()]
        bbox.max = [v for v in bbox_data["maxPos"].values()]
        info.unk_01 = 0  # not really, looks like a hash
        info.nulls_01 = [0, 0]
        info.bounding_box = bbox
        info.pairs_start = f0
        info.pairs_count = len(p)
        info.faces_start = f0
        info.face_count = len(f)
        info.vertex_start = v0
        info.vertex_count = len(v)
        info.index_id = int(m["indexID"])  # something wrong
        info.nulls_02 = [0, 0]
        info._check()
        f0 += len(f)
        v0 += len(v)
        p0 += len(p)
        infos.append(info)
    return infos


def getVertexBox(v):
    return geo.BoundingBox(v)
'''
# cBHVCollision (Bounding Box Tree)
cBVHCollision = Struct(
    "BVHC" / Int64ul,  # Bound Volume Hierarchy Collision Identifier 0x77B17B2443485642
    "SOH" / Int64ul,  # Start of Header 0x1
    "boundingBox" / BoundingBox,  # BoundingBox of First Node
    "nodeCount" / Int32ul,
    "null" / Int32ul[3],
    "AABBArray" / AABBArray[this.nodeCount]
)
'''


class semiTri():
    def __init__(self, face, matType):
        if not len(face.verts) == 3:
            raise TriangulationRequiredError()
        self.vert = [int(v.index) for v in face.verts]
        self.adjacent = self.getAdjacent(face)
        self.normal = semiTri.calcNormal(face)
        self.type = matType
        # (0 = 90°, 1 = 0°, 2 > 180°, 3<180°)

    def getAdjacent(self, face):
        adjacents = []
        for edge in face.edges:
            bA = None
            for lf in edge.link_faces:
                if lf != face:
                    bA = semiTri.byteAngle(face, lf)
            if bA is None:
                bA = 0
            adjacents.append(bA)
        return adjacents

    def setIndex(self, value):
        self._index = value
        return self

    def index(self):
        return self._index

    @staticmethod
    def calcNormal(face1):
        v = Vector(np.cross(
            face1.verts[1].co-face1.verts[0].co, face1.verts[2].co-face1.verts[0].co))
        v.normalize()
        return v

    @staticmethod
    def edges(face):
        e1 = cycles(face.verts)
        return e1

    @staticmethod
    def barycenter(face):
        return sum([v.co for v in face.verts], Vector([0, 0, 0]))/len(face.verts)

    @staticmethod
    def byteAngle(face1, face2):
        n1 = semiTri.calcNormal(face1)
        n2 = semiTri.calcNormal(face2)
        fv1 = [v.co for v in face1.verts]
        e1 = semiTri.edges(face1)
        e2 = semiTri.edges(face2)
        facing = None
        for ix, e in enumerate(e1):
            if tuple(reversed(e)) in e2:
                edgem = (fv1[ix]+fv1[(ix+1) % 3])/2
                bary = (semiTri.barycenter(face1)+semiTri.barycenter(face2))/2
                facing = bary - edgem
                facing.normalize()
        if facing is None:
            # Not exactly correct but correct most of the time (1.5% fail rate)
            return 0

        if (n1-n2).magnitude < eps:
            return 1
        if (n1+n2).magnitude < eps:
            return 4
        n = (n1+n2)
        n.normalize()
        signum = (n1+n2).dot(facing) > 0
        if not signum:
            if n1.dot(n2) < eps:
                return 0
            return 2
        else:
            return 4

    @staticmethod
    def getMaterial(face, mesh):
        try:
            ix = face.material_index
            slot = mesh.material_slots[ix]
            mat = slot.material.name
            return int(mat[len("Type "):len("Type 000")])
        except:
            raise MaterialMissingError


def mesh_to_tri(mesh):
    bm = bmesh.new()
    # bm.from_object(mesh, bpy.context.scene)
    bm.from_mesh(mesh.data)
    vertices = [Vector(v.co) for v in bm.verts]
    faces = [Tri(semiTri(face, semiTri.getMaterial(face, mesh)), vertices)
             for face in bm.faces]
    bm.free()
    return vertices, faces

