import bpy
import bmesh
from kaitaistruct import KaitaiStream
import colorsys
import numpy as np

from albam.registry import blender_registry
from .structs.sbc_156 import Sbc156
from .structs.sbc_21 import Sbc21
from mathutils import Vector

from albam.lib.primitiveGeometry import eps,Tri
import albam.lib.primitiveGeometry as geo
import albam.lib.bvhConstruction as bvh
import albam.lib.CommonOperations as Common

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
        self.faces = bvh.indexizeObject([geo.Tri(face, vertices) for face in faces])
        self.vertices = vertices
        self.pairs = bvh.indexizeObject([geo.QuadPair(self.faces[pair.face_01], self.faces[pair.face_02])
                        if pair.face_02 != 0xFFFF else
                        self.faces[pair.face_01]
                        for pair in pairs])


class counter():
    def __init__(self):
        self.i = 0

    def count(self):
        self.i += 1
        return self.i


i = counter()
cycle = lambda: [0.4, 0.6, 0.8, 1.0][i.count() % 4]
palette = [colorsys.hsv_to_rgb(c/55, 1.0, cycle()) for c in range(44)]
palette = [(i[0], i[1], i[2], 1.0) for i in palette]


@blender_registry.register_import_function(app_id="re0", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re1", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re5", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re6", extension='sbc', file_category="COLLISION")
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


def createLinkObject(linkObject):
    sbcEmpty = Common.createRootNub("SBC Stage Link.000")
    sbcEmpty["Type"] = "SBC_Link"
    sbcEmpty["{Unkn1}"] = linkObject.unkn_01
    sbcEmpty["{Unkn3}"] = linkObject.unkn_02
    sbcEmpty["{Unkn4}"] = linkObject.unkn_03
    sbcEmpty["{Unkn5}"] = linkObject.unkn_04
    sbcEmpty["jpPath"] = linkObject.jp_path
    return sbcEmpty


def decomposeSBCObject(sbcObject):
    sbcGeom = {}
    sbcGeom["vertices"] = [(vert.x/100, vert.z/100, vert.y/100) for vert in sbcObject.vertices]
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
    #bpy.context.scene.objects.link(blenderObject)
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
    meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    links = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    clones = [Common.cloneMesh(mesh) for mesh in meshes]
    vertList = []
    trisList = []
    quadList = []
    sbcsList = []
    meshmetadata = []
    options = {"clusteringFunction": bvh.HybridClustering,
               "metric": bvh.Cluster.SAHMetric,
               "partition": bvh.mortonPartition,
               "mode": bvh.CAPCOM}
    vfiles = []
    print("Initiate export")
    for mesh in clones:
        vertices, tris = meshToTri(mesh)
        print("Mesh processed")
        quads, sbc = bvh.primitiveToSBC(tris, **options)
        vertList.append(vertices)
        trisList.append(tris)
        quadList.append(quads)
        sbcsList.append(sbc)
        meshmetadata.append({"indexID": mesh["indexID"]})
    return vfiles


class semiTri():
    def __init__(self, face, matType):
        if not len(face.verts) == 3: raise TriangulationRequiredError()
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
        v = Vector(np.cross(face1.verts[1].co-face1.verts[0].co, face1.verts[2].co-face1.verts[0].co))
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
            return 0  # Not exactly correct but correct most of the time (1.5% fail rate)

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


def meshToTri(mesh):
    bm = bmesh.new()
    # bm.from_object(mesh, bpy.context.scene)
    bm.from_mesh(mesh.data)
    vertices = [Vector(v.co) for v in bm.verts]
    faces = [Tri(semiTri(face, semiTri.getMaterial(face, mesh)), vertices) for face in bm.faces]
    bm.free()
    return vertices, faces
