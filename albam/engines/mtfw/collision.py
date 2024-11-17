import bpy
import bmesh
from kaitaistruct import KaitaiStream
import colorsys

from albam.registry import blender_registry
from .structs.sbc_156 import Sbc156
from .structs.sbc_21 import Sbc21


import albam.lib.primitiveGeometry as geo
import albam.lib.bvhConstruction as bvh
import albam.lib.CommonOperations as Common

SBC_CLASS_MAPPER = {
    49: Sbc156,
    255: Sbc21,
}


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
    sbc_bytes = file_item.get_bytes()
    sbc_version = sbc_bytes[3]
    assert sbc_version in SBC_CLASS_MAPPER, f"Unsupported version: {sbc_version}"
    SbcCls = SBC_CLASS_MAPPER[sbc_version]
    sbc = SbcCls.from_bytes(sbc_bytes)
    sbc._read()

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
        create_collision_mesh(obj)
    for i, typing in enumerate(sbc.collision_types):
        createLinkObject(typing)


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
