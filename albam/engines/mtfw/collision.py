import bpy
import bmesh
from kaitaistruct import KaitaiStream
import colorsys
import numpy as np
from mathutils import Vector
from io import BytesIO
import traceback


from ...registry import blender_registry
from ...vfs import VirtualFileData
from .structs.sbc_156 import Sbc156
from .structs.sbc_21 import Sbc21
from .structs.sbc_211 import Sbc211
from ...lib.primitive_geometry import EPS, Tri
from ...lib import primitive_geometry as geo
from ...lib import bvh_construction as bvh
from ...lib import common_op as common

SBC_CLASS_MAPPER = {
    49: Sbc156,
    255: Sbc21,
}

APPID_SBC_CLASS_MAPPER = {
    "re0": Sbc21,
    "re1": Sbc21,
    "re5": Sbc156,
    "dmc4": Sbc156,
    "re6": Sbc211,
    "rev1": Sbc21,
    "rev2": Sbc21,
    "dd": Sbc21,
}

SBC_VERSION = {
    "re5:": 22,
    "dmc4": 18,
}

DEBUG_DRAW = False

KNOWN_RUNTIME_ATTR = [256, 512, 1024, 2048, 3072, 3584, 4096, 4352, 5120, 7168, 9216, 8192,
                      11264, 11776, 16384, 17408, 32768, 33280, 33792, 34304, 34816, 35840,
                      40960, 40448, 41984, 42496, 42752, 44032, 44288, 49152, 65536, 131072,
                      1048576, 2097152, 262144, 524288, 134217728, 33554432, 67108864
                      ]


CLUSTERING = {
    "hybrid": bvh.hybrid_clustering,
    "kdtree": bvh.kd_tree_split,
    "split": bvh.spatial_splits,
    "aproxcluster": bvh.aproximate_agglomerative_clustering,
    "exactcluster": bvh.exact_agglomerative_clustering
}
# Surface Area Heuristic (SAH)
METRIC = {
    "sah": bvh.Cluster.SAHMetric,
    "epo": bvh.Cluster.EPOMetric
}
PARTITION = {
    "morton": bvh.morton_partition,
    "metric": bvh.linear_split
}
MODE = {
    "capcom": bvh.CAPCOM,
    "normal": bvh.TRADITIONAL
}


class TriangulationRequiredError(Exception):
    pass


class ExportingFailedError(Exception):
    pass


class MaterialMissingError(Exception):
    pass


class SBCObject21():
    def __init__(self, info, BVHTree, faces, vertices, pairs):
        self.sbcinfo = info
        self.bvhtree = BVHTree
        self.faces = bvh.indexize_ob([geo.Tri(face, vertices) for face in faces])
        self.vertices = vertices
        for pair in pairs:
            try:
                self.faces[pair.face_01]
            except IndexError:
                print("Index {} face01 doesn't exists in face list".format(pair.face_01))
            if pair.face_02 != 0xFFFF:
                try:
                    self.faces[pair.face_02]
                except IndexError:
                    print("Index {} face02 doesn't exists in face list".format(pair.face_02))

        self.pairs = bvh.indexize_ob([geo.QuadPair(self.faces[pair.face_01], self.faces[pair.face_02])
                                     if pair.face_02 != 0xFFFF else
                                     self.faces[pair.face_01]
                                     for pair in pairs])


class SBCObject156():
    def __init__(self, info, faces, vertices):
        self.sbcinfo = info
        self.faces = bvh.indexize_ob([geo.Tri(face, vertices) for face in faces])
        self.attr = [{'unk_00': f.unk_00,
                      'unk_01': f.unk_01,
                      'runtime_attr': f.runtime_attr,
                      'type': f.type,
                      'special_attr': f.special_attr,
                      'surface_attr': f.surface_attr} for f in faces]
        self.vertices = vertices


# Very smartass(?) way to dynamically create a list with 44 colors
class counter():
    def __init__(self):
        self.i = 0

    def count(self):
        self.i += 1
        return self.i


i = counter()


def cycle():
    return [0.4, 0.6, 0.8, 1.0][i.count() % 4]


palette = [colorsys.hsv_to_rgb(c / 55, 1.0, cycle()) for c in range(44)]
palette = [(i[0], i[1], i[2], 1.0) for i in palette]


@blender_registry.register_import_function(app_id="re0", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="re1", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="re5", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="dmc4", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="re6", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="rev1", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="rev2", extension='sbc', albam_asset_type="COLLISION")
@blender_registry.register_import_function(app_id="dd", extension='sbc', albam_asset_type="COLLISION")
def load_sbc(file_item, context):
    app_id = file_item.app_id
    sbc_bytes = file_item.get_bytes()
    sbc_version = sbc_bytes[3]
    assert sbc_version in SBC_CLASS_MAPPER, f"Unsupported version: {sbc_version}"
    SbcCls = APPID_SBC_CLASS_MAPPER[app_id]
    sbc = SbcCls.from_bytes(sbc_bytes)
    sbc._read()

    bl_object_name = file_item.display_name
    bl_object = bpy.data.objects.new(bl_object_name, None)
    sbc_objects = []

    if sbc_version == 255:
        bvh_collection = [b for i, b in enumerate(sbc.sbc_bvhc)]
        face_collection = [fc for i, fc in enumerate(sbc.faces)]
        vertex_collection = [vc for i, vc in enumerate(sbc.vertices)]
        pair_collection = [pc for i, pc in enumerate(sbc.pairs_collections)]

        for ix, ob_info in enumerate(sbc.sbc_info):
            ps, pc = ob_info.start_pairs, ob_info.num_pairs
            fs, fc = ob_info.start_faces, ob_info.num_faces
            vs, vc = ob_info.start_vertices, ob_info.num_vertices
            sbc_obj = SBCObject21(ob_info, bvh_collection[ix], face_collection[fs:fs + fc],
                                  vertex_collection[vs:vs + vc], pair_collection[ps:ps + pc])
            sbc_objects.append(sbc_obj)
    else:
        bvh_collection = [b for i, b in enumerate(sbc.nodes)]
        face_collection = [fc for i, fc in enumerate(sbc.faces)]
        vertex_collection = [fc for i, fc in enumerate(sbc.vertices)]

        for ix, ob_info in enumerate(sbc.sbc_info):
            if ix < (len(sbc.sbc_info) - 1):
                try:
                    fs, fc = ob_info.start_faces, (
                        sbc.sbc_info[ix + 1].start_faces - sbc.sbc_info[ix].start_faces)
                    vs, vc = ob_info.start_vertices, (
                        sbc.sbc_info[ix + 1].start_vertices - sbc.sbc_info[ix].start_vertices)
                    obj = SBCObject156(ob_info, face_collection[fs:fs + fc], vertex_collection[vs:vs + vc])
                except Exception:
                    print(traceback.format_exc())
                    print(f'Error at group {ix}, Tri {fs}, Vert {vs}')
            else:
                fs = ob_info.start_faces
                vs = ob_info.start_vertices
                obj = SBCObject156(ob_info, face_collection[fs:], vertex_collection[vs:])
            sbc_objects.append(obj)

    print("num SBC objects {}".format(len(sbc_objects)))
    for i, obj in enumerate(sbc_objects):
        mesh_name = f"{bl_object_name}_{str(i).zfill(4)}"
        mesh, ob = create_collision_mesh(obj, app_id, mesh_name)
        if DEBUG_DRAW:
            debug_create_bbox(obj)  # sbc_info
        ob.parent = bl_object

    if sbc_version == 255:
        for i, typing in enumerate(sbc.collision_types):
            link_name = f"{bl_object_name}_stage_link_{str(i).zfill(4)}"
            empty_ob = create_link_ob(typing, app_id, link_name)
            empty_ob.parent = bl_object

    if DEBUG_DRAW:
        for i, node in enumerate(bvh_collection):
            if i >= sbc.header.num_groups:
                break
            debug_create_sbcinfo_nodes(node)

    return bl_object


def create_collision_mesh(sbc_object, app_id, mesh_name):
    mesh, obj = create_sbc_mesh(mesh_name, decompose_sbc_ob(sbc_object, app_id), app_id)
    # Add custom attributes to an object
    if app_id not in ("re5", "dmc4"):
        sbc_mesh_props = obj.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
            "sbc_21_mesh"]
        sbc_mesh_props.index_id = str(sbc_object.sbcinfo.index_id)
    return mesh, obj


def create_link_ob(link_ob, app_id, link_name):
    # Add custom attributes from collision_types to an empty object
    sbc_empty = common.create_root_nub(link_name)
    sbc_link_proprs = sbc_empty.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
        "sbc_21_link"]
    sbc_link_proprs.unk_01 = link_ob.unk_01
    sbc_link_proprs.unk_02 = link_ob.unk_02
    sbc_link_proprs.unk_03 = link_ob.unk_03
    sbc_link_proprs.unk_04 = link_ob.unk_04
    sbc_link_proprs.jp_path = link_ob.jp_path
    return sbc_empty


def decompose_sbc_ob(sbc_ob, app_id):
    # Extract data needed for building meshes form SBCObject
    sbc_geom = {}
    sbc_geom["vertices"] = [(vert.x * 0.01, vert.z * -0.01, vert.y * 0.01)
                            for vert in sbc_ob.vertices]
    sbc_geom["faces"] = [face.dataFace.vert for face in sbc_ob.faces]
    sbc_geom["materials"] = materials_from_sbc(sbc_ob, app_id)
    if app_id in ("re5", "dmc4"):
        sbc_geom['attr'] = sbc_ob.attr
    return sbc_geom


def materials_from_sbc(sbc_ob, app_id):
    materials = {}
    if app_id not in ("re5", "dmc4"):
        for ix, face in enumerate(sbc_ob.faces):
            if face.type not in materials:
                materials[face.type] = []
            materials[face.type].append(ix)
    else:
        for ix, face in enumerate(sbc_ob.attr):
            if face['runtime_attr'] not in materials:
                materials[face['runtime_attr']] = []
            materials[face['runtime_attr']].append(ix)
    return materials


def create_sbc_mesh(name, meshpart, app_id):
    bl_mesh = bpy.data.meshes.new(name)
    bl_mesh.from_pydata(meshpart["vertices"], [], meshpart["faces"])
    bl_mesh.update()
    bl_obj = bpy.data.objects.new(name, bl_mesh)
    # bpy.context.collection.objects.link(bl_obj)  # pytest screams it's re-add
    bm = bmesh.new()
    bm.from_mesh(bl_mesh)
    bm.faces.ensure_lookup_table()

    # Unloaded stores custom attributes in the mesh faces, not the best idea
    if app_id in ("re5", "dmc4"):
        unk_00 = bm.faces.layers.int.new('unk_00')
        unk_01 = bm.faces.layers.int.new('unk_01')
        type = bm.faces.layers.int.new('type')
        surface_attr = bm.faces.layers.int.new('surface_attr')
        special_attr = bm.faces.layers.int.new('special_attr')

        for i, val in enumerate(meshpart['attr']):
            bm.faces[i][unk_00] = val['unk_00']
            bm.faces[i][unk_01] = val['unk_01']
            bm.faces[i][type] = val['type']
            bm.faces[i][surface_attr] = val['surface_attr']
            bm.faces[i][special_attr] = val['special_attr']

    # Store type/runtime_attr as material indices
    for ix, material in enumerate(meshpart["materials"]):
        mat = bpy.data.materials.get("Type %03d" % material)
        if not mat:
            mat = bpy.data.materials.new(name="Type %03d" % material)
        try:
            if app_id in ("re5", "dmc4"):
                mat.diffuse_color = palette[KNOWN_RUNTIME_ATTR.index(material)]
            else:
                mat.diffuse_color = palette[material]
        except IndexError:
            colorsys.hsv_to_rgb(0, 0, 0)
            print("Unknown colision type: %d" % material)
        bl_mesh.materials.append(mat)
        for face in meshpart["materials"][material]:
            bm.faces[face].material_index = ix

    bm.to_mesh(bl_mesh)
    return bl_mesh, bl_obj


def cycles(verts):
    return [(verts[i % 3].index, verts[(i + 1) % 3].index) for i in range(len(verts))]


@blender_registry.register_export_function(app_id="re0", extension="sbc")
@blender_registry.register_export_function(app_id="re1", extension="sbc")
@blender_registry.register_export_function(app_id="rev1", extension="sbc")
@blender_registry.register_export_function(app_id="rev2", extension="sbc")
@blender_registry.register_export_function(app_id="re6", extension="sbc")
@blender_registry.register_export_function(app_id="re5", extension="sbc")
@blender_registry.register_export_function(app_id="dd", extension="sbc")
def export_sbc(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    Sbc = APPID_SBC_CLASS_MAPPER[app_id]

    src_sbc = Sbc.from_bytes(asset.original_bytes)
    src_sbc._read()
    dst_sbc = Sbc()

    meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    links = [c for c in bl_obj.children_recursive if c.type == "EMPTY"]
    mesh_clones = [common.clone_mesh(mesh) for mesh in meshes]
    mesh_clones = [mesh_rescale(clone) for clone in mesh_clones]
    export_settings = bpy.context.scene.albam.export_settings
    vertList = []
    trisList = []
    quadList = []
    sbcsList = []
    mesh_metadata = []
    attrList = []
    errors = []
    options = {"clusteringFunction": CLUSTERING[export_settings.algorithm],
               "metric": METRIC[export_settings.metric],
               "partition": PARTITION[export_settings.partition],
               "mode": MODE[export_settings.mode]}
    vfiles = []
    print("Initiate SBC export")
    for mesh in mesh_clones:
        if app_id not in ("re5", "dmc4"):
            custom_props = mesh.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)[
                "sbc_21_mesh"]
        # get list of Tri objects from faces of the mesh and vertices
        try:
            if app_id in ("re5", "dmc4"):
                vertices, tris, attr = mesh_to_tri156(mesh)
                attrList.append(attr)
            else:
                vertices, tris = mesh_to_tri(mesh)
        except TriangulationRequiredError:
            errors.append("%s requires triangulating." % mesh.name)
        # pairs, bvhc
        if app_id in ("re5", "dmc4"):
            quads, sbc = bvh.primitive_to_sbc156(tris, **options)
        else:
            quads, sbc = bvh.primitive_to_sbc(tris, **options)
        vertList.append(vertices)
        trisList.append(tris)  # tris primitive objects not faces
        quadList.append(quads)
        sbcsList.append(sbc)
        if app_id not in ("re5", "dmc4"):
            mesh_metadata.append({"indexID": custom_props.index_id})
    for clone in mesh_clones:
        common.delete_ob(clone)
    if errors:
        print(errors)
        raise ExportingFailedError
    if app_id in ("re5", "dmc4"):
        parent_tree = bvh.trees_to_sbc_col156(sbcsList, **options)
        # version = SBC_VERSION[app_id]
        version = 22 if app_id == "re5" else 18
        final_size = build_sbc156(
            bl_obj, dst_sbc, version, vertList, trisList, sbcsList, attrList, parent_tree)
    else:
        parent_tree = bvh.trees_to_sbc_col(sbcsList, **options)
        final_size = build_sbc(bl_obj, src_sbc, dst_sbc, vertList, trisList, quadList, sbcsList,
                               links, parent_tree, mesh_metadata, app_id)
    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_sbc._check()
    dst_sbc._write(stream)
    sbc_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
    vfiles.append(sbc_vf)
    return vfiles


def build_sbc(bl_obj, src_sbc, dst_sbc, verts, tris, quads, sbcs, links, parent_tree, mesh_metadata, app_id):
    def tally(x):
        return sum(map(len, x))
    # headerData = formHeader(len(verts), tally(verts), tally(tris), tally(
    #    quads), len(links), tally(sbcs+[parentTree]), parentTree)
    _init_sbc_header(bl_obj, src_sbc, dst_sbc, len(verts), len(links), tally(quads), tally(tris),
                     tally(verts), parent_tree, tally(sbcs + [parent_tree]))
    # header = buildHeader(headerData)
    # cBVH = list(map(buildCollision,sbcs))
    dst_sbc.sbc_bvhc = [_serialize_bvhc(dst_sbc, sbc) for sbc in sbcs]

    # cBVHCollision = buildCollision(parentTree)
    dst_sbc.bvh = _serialize_bvhc(dst_sbc, parent_tree)

    # faceCollection = list(map(buildFaces, tris))
    dst_sbc.faces = build_faces(dst_sbc, tris)

    # vertexCollection = list(map(buildVertices, verts))
    dst_sbc.vertices = build_vertices(dst_sbc, verts)

    # collisionTypes = list(map(buildTypes, links))
    dst_sbc.collision_types = [_serialize_col_types(dst_sbc, link, app_id) for link in links]

    # pairCollection = list(map(buildPairs, quads))
    dst_sbc.pairs_collections = build_pairs(dst_sbc, quads)
    # dst_sbc.pairs_collections = _serialize_pairs(dst_sbc, quads)

    # infoCollection = buildInfo(
    #    header, tris, verts, collisionTypes, quads, cBVH, cBVHCollision, meshmetadata)
    dst_sbc.sbc_info = _serialize_infos(dst_sbc, tris, verts, dst_sbc.collision_types,
                                        quads, dst_sbc.sbc_bvhc, dst_sbc.bvh, mesh_metadata)

    bvhc_size = 0
    for i, bvhc in enumerate(dst_sbc.sbc_bvhc):
        bvhc_size += 64 + bvhc.num_nodes * 112

    bvh_size = 64 + dst_sbc.bvh.num_nodes * 112
    SBC_HEADER_SIZE = {
        "rev1": 84,
        "rev2": 84,
        "dd": 84,
        "re6": 80,
    }
    final_size = sum((
        SBC_HEADER_SIZE[app_id],
        dst_sbc.header.num_objects * 80,
        bvhc_size,
        bvh_size,
        dst_sbc.header.num_faces * 32,
        dst_sbc.header.num_vertices * 16,
        dst_sbc.header.num_stages * 32,
        dst_sbc.header.num_pairs * 10,
    ))

    return final_size


def build_sbc156(bl_obj, dst_sbc, version, verts, tris, sbcs, attr, parent_tree):
    def tally(x):
        return sum(map(len, x))
    nodes = []
    groups = []
    vertices = []
    faces = []
    node_num = (len(sbcs) - 1) or 1
    _init_sbc156_header(dst_sbc, version, parent_tree, len(sbcs), tally(
        tris) - 1 + len(sbcs) - 1, tally(verts), tally(tris))
    for i, sbc in enumerate(sbcs):
        node_list, sbc_info = _serialize_bvhc156(dst_sbc, sbc, len(faces), len(vertices), node_num)
        nodes.extend(node_list)
        node_num += len(node_list)
        groups.append(sbc_info)
        faces.extend(_serialize_faces156(dst_sbc, tris[i], attr[i]))
        vertices.extend(_serialize_vertices(dst_sbc, verts[i]))

    final_node_list = _serialize_top_bvh(dst_sbc, parent_tree, groups)
    final_node_list.extend(nodes)
    dst_sbc.header.num_boxes = len(final_node_list)
    dst_sbc.nodes = final_node_list
    dst_sbc.sbc_info = groups
    dst_sbc.faces = faces
    dst_sbc.vertices = vertices
    final_size = sum((
        0x30,
        dst_sbc.header.num_boxes * 0x50,
        dst_sbc.header.num_objects * 0x60,
        dst_sbc.header.num_faces * 0x28,
        dst_sbc.header.num_vertices * 16
    ))
    return final_size


def _init_sbc_header(bl_obj, src_sbc, dst_sbc, num_objects, num_stages, num_pairs, num_faces,
                     num_vertices, parent_tree, aabb_count):
    dst_sbc_header = dst_sbc.SbcHeader(_parent=dst_sbc, _root=dst_sbc._root)
    bbox_data = parent_tree.boundingBox().serialize()
    bbox = dst_sbc.Bbox4(_parent=dst_sbc_header, _root=dst_sbc._root)
    bbox.min = [v for v in bbox_data["minPos"].values()]
    bbox.max = [v for v in bbox_data["maxPos"].values()]
    dst_sbc_header.__dict__.update(dict(
        indent=b"SBC\xFF",
        unk_00=src_sbc.header.unk_00,
        unk_02=0,
        unk_03=0,
        num_objects=num_objects,
        num_stages=num_stages,
        num_pairs=num_pairs,
        num_faces=num_faces,
        num_vertices=num_vertices,
        nulls=[0, 0, 0, 0],
        bounding_box=bbox,
        bb_size=0x70 * (aabb_count),
    ))

    dst_sbc_header._check()
    dst_sbc.header = dst_sbc_header
    return dst_sbc_header


def _init_sbc156_header(dst_sbc, version, parent_tree, num_objects, num_nodes, num_verts, num_faces):
    dst_sbc_header = dst_sbc.SbcHeader(_parent=dst_sbc, _root=dst_sbc._root)
    bbox_data = parent_tree.boundingBox().serialize()
    bbox = dst_sbc.Bbox3(_parent=dst_sbc_header, _root=dst_sbc._root)
    bbox.min = [v for v in bbox_data["minPos"].values()][:3]
    bbox.max = [v for v in bbox_data["maxPos"].values()][:3]
    dst_sbc_header.__dict__.update(dict(
        indent=b'SBC\x31',
        version=version,
        num_objects=num_objects,
        num_objects_nodes=num_objects - 1,
        num_max_objects_nest=0,
        num_max_nest=0,
        num_boxes=num_nodes,
        num_faces=num_faces,
        num_vertices=num_verts,
        bounding_box=bbox
    ))

    dst_sbc_header._check()
    dst_sbc.header = dst_sbc_header


def _serialize_bvhc(dst_sbc, bvhc_data):
    bvh_col = dst_sbc.BvhCollision(_parent=dst_sbc, _root=dst_sbc._root)
    bbox = dst_sbc.Bbox4(_parent=bvh_col, _root=dst_sbc._root)
    bvhc_raw = bvhc_data.primitiveSerialize()

    bvh_col.bvhc = [1128814146, 2008120100]  # Bound Volume Hierarchy Collision Identifier
    bvh_col.soh = bvhc_raw["SOH"]
    bvh_col.unk_01 = 0
    bbox_data = bvhc_raw["boundingBox"]
    bbox.min = [v for v in bbox_data["minPos"].values()]
    bbox.max = [v for v in bbox_data["maxPos"].values()]
    bvh_col.bounding_box = bbox
    bvh_col.num_nodes = bvhc_raw["nodeCount"]
    bvh_col.nulls = [0, 0, 0]
    bvh_nodes = []
    for bvnode in bvhc_raw["AABBArray"]:
        bvh_node = dst_sbc.BvhNode(_parent=bvh_col, _root=dst_sbc._root)
        bvh_node.node_type = bvnode["nodeType"]
        bvh_node.node_id = bvnode["nodeId"]
        bvh_node.unk_05 = 3452816845  # 0xCDCDCDCD
        min_aabb = bvnode["minAABB"]
        aabb = dst_sbc.AabbBlock(_parent=bvh_node, _root=dst_sbc._root)
        aabb.x = min_aabb["xArray"]
        aabb.y = min_aabb["yArray"]
        aabb.z = min_aabb["zArray"]
        bvh_node.min_aabb = aabb
        max_aabb = bvnode["maxAABB"]
        aabb = dst_sbc.AabbBlock(_parent=bvh_node, _root=dst_sbc._root)
        aabb.x = max_aabb["xArray"]
        aabb.y = max_aabb["yArray"]
        aabb.z = max_aabb["zArray"]
        bvh_node.max_aabb = aabb
        bvh_node._check()
        bvh_nodes.append(bvh_node)
    bvh_col.nodes = bvh_nodes
    bvh_col._check()
    return bvh_col


# sbc_info 156
def _serialize_bvhc156(dst_sbc, bvhc_data, start_tri, start_vert, start_node):
    def vec4to3(x):
        return write_vec3([x.x, x.y, x.z], dst_sbc)

    bvhc_raw = bvhc_data.primitiveSerialize()
    sbc_info = dst_sbc.Info(_parent=dst_sbc, _root=dst_sbc._root)
    bbox_data = bvhc_raw['boundingBox']
    sbci_bbox = dst_sbc.Bbox3(_parent=sbc_info, _root=dst_sbc._root)
    sbci_bbox.min = [v for v in bbox_data['minPos'].values()][:3]
    sbci_bbox.max = [v for v in bbox_data['maxPos'].values()][:3]
    sbc_info.bounding_box = sbci_bbox
    sbc_info.index_id = 0xffffffff  # was 0
    sbc_info.base = 0
    sbc_info.start_nodes = start_node
    sbc_info.start_faces = start_tri if start_tri >= 0 else 0
    sbc_info.start_vertices = start_vert if start_vert >= 0 else 0
    sbc_info.child_index = [0, 0]
    node_list = []

    for bvnode in bvhc_raw["AABBArray"]:
        node = dst_sbc.BvhNode(_parent=dst_sbc, _root=dst_sbc._root)
        node.bit = bvnode['nodeType']
        node.child_index = bvnode['nodeId']
        boxes = []
        for i in range(2):
            bbox = dst_sbc.Bbox4(_parent=node, _root=dst_sbc._root)
            min_aabb = bvnode["minAABB"]
            bbox
            # box.min.x = min_aabb["xArray"][i]
            # box.min.y = min_aabb["yArray"][i]
            # box.min.z = min_aabb["zArray"][i]
            # bbox.min = write_vec4(
            #    [min_aabb["xArray"][i], min_aabb["yArray"][i], min_aabb["zArray"][i], 0.0], dst_sbc)
            bbox.min = [min_aabb["xArray"][i], min_aabb["yArray"][i], min_aabb["zArray"][i], 0.0]
            max_aabb = bvnode["maxAABB"]
            # box.max.x = max_aabb["xArray"][i]
            # box.max.y = max_aabb["yArray"][i]
            # box.max.z = max_aabb["zArray"][i]
            # bbox.max = write_vec4(
            #    [max_aabb["xArray"][i], max_aabb["yArray"][i], max_aabb["zArray"][i], 0.0], dst_sbc)
            bbox.max = [max_aabb["xArray"][i], max_aabb["yArray"][i], max_aabb["zArray"][i], 0.0]
            # box._check()
            boxes.append(bbox)
        node.boxes = boxes
        node.nulls = [0] * 10
        node_list.append(node)
    # sbc_info.vmin = [vec4to3(node_list[0].boxes[0].min), vec4to3(node_list[0].boxes[1].min)]
    sbc_info.vmin = [write_vec3(node_list[0].boxes[0].min[:3], dst_sbc),
                     write_vec3(node_list[0].boxes[1].min[:3], dst_sbc)]
    # sbc_info.vmax = [vec4to3(node_list[0].boxes[0].max), vec4to3(node_list[0].boxes[1].max)]
    sbc_info.vmax = [write_vec3(node_list[0].boxes[0].max[:3], dst_sbc),
                     write_vec3(node_list[0].boxes[1].max[:3], dst_sbc)]
    return node_list, sbc_info


def build_faces(dst_sbc, tris):
    stris = []
    for t in tris:
        stris.extend(_serialize_faces(dst_sbc, t))
    return stris


def _serialize_faces(dst_sbc, face_data):
    faces = []
    print("lenght of face data is {}".format(len(face_data)))
    for f in face_data:
        face = dst_sbc.Face(_parent=dst_sbc, _root=dst_sbc._root)
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


def _serialize_faces156(dst_sbc, face_data, attr):
    faces = []
    for i, f in enumerate(face_data):
        face = dst_sbc.Face(_parent=dst_sbc, _root=dst_sbc._root)
        face.vert = f.dataFace.vert
        face.unk_00 = 0
        face.unk_01 = 0
        face.runtime_attr = attr[i]['runtime_attr']
        face.type = attr[i]['type']
        face.surface_attr = attr[i]['surface_attr']
        face.special_attr = attr[i]['special_attr']
        face.unk_02 = 0
        face._check()
        faces.append(face)
    return faces


def build_vertices(dst_sbc, verts):
    svertices = []
    for v in verts:
        svertices.extend(_serialize_vertices(dst_sbc, v))
    return svertices


def _serialize_vertices(dst_sbc, vertex_data):
    vertices = []
    for v in vertex_data:
        dst_vertex = dst_sbc.Vertex(_parent=dst_sbc, _root=dst_sbc._root)
        vertex_raw = geo.vec_unfold(v)
        dst_vertex.x = vertex_raw["x"]
        dst_vertex.y = vertex_raw["y"]
        dst_vertex.z = vertex_raw["z"]
        dst_vertex.w = vertex_raw["w"]
        dst_vertex._check()
        vertices.append(dst_vertex)
    return vertices


def _serialize_top_bvh(dst_sbc, tree, sbc_groups):
    def vec4to3(x):
        return write_vec3([x.x, x.y, x.z], dst_sbc)

    bvhc_raw = tree.primitiveSerialize()
    node_list = []
    for i, bvnode in enumerate(bvhc_raw["AABBArray"]):
        node = dst_sbc.BvhNode(_parent=dst_sbc, _root=dst_sbc._root)
        node.bit = bvnode['nodeType']
        node.child_index = bvnode['nodeId']
        boxes = []
        for j in range(2):
            bbox = dst_sbc.Bbox4(_parent=dst_sbc, _root=dst_sbc._root)
            min_aabb = bvnode["minAABB"]
            bbox.min = [min_aabb["xArray"][j], min_aabb["yArray"][j], min_aabb["zArray"][j], 0.0]
            # box.min.x = min_aabb["xArray"]
            # box.min.y = min_aabb["yArray"]
            # box.min.z = min_aabb["zArray"]
            # bbox.min = write_vec4(
            #    [min_aabb["xArray"][j], min_aabb["yArray"][j], min_aabb["zArray"][j], 0.0], dst_sbc)
            max_aabb = bvnode["maxAABB"]
            # box.max.x = max_aabb["xArray"]
            # box.max.y = max_aabb["yArray"]
            # box.max.z = max_aabb["zArray"]
            bbox.max = [max_aabb["xArray"][j], max_aabb["yArray"][j], max_aabb["zArray"][j], 0.0]
            # bbox.max = write_vec4(
            #    [max_aabb["xArray"][j], max_aabb["yArray"][j], max_aabb["zArray"][j], 0.0], dst_sbc)
            # box._check()
            boxes.append(bbox)
        node.boxes = boxes
        node.nulls = [0] * 10
        node_list.append(node)
        # sbc_groups[i].vmin = [vec4to3(node.boxes[0].min), vec4to3(node.boxes[1].min)]
        sbc_groups[i].vmin = [write_vec3(node.boxes[0].min[:3], dst_sbc),
                              write_vec3(node.boxes[1].min[:3], dst_sbc)]
        # sbc_groups[i].vmax = [vec4to3(node.boxes[0].max), vec4to3(node.boxes[1].max)]
        sbc_groups[i].vmax = [write_vec3(node.boxes[0].max[:3], dst_sbc),
                              write_vec3(node.boxes[1].max[:3], dst_sbc)]
    return node_list


def build_pairs(dst_sbc, quads):
    spairs = []
    for p in quads:
        spairs.extend(_serialize_pairs(dst_sbc, p))
    return spairs


def _serialize_col_types(dst_sbc, link_ob, app_id):
    # Gets custom attributes from empty objects
    sbc_link_props = link_ob.albam_custom_properties.get_custom_properties_secondary_for_appid(
        app_id)["sbc_21_link"]
    coltype = dst_sbc.CollisionType(_parent=dst_sbc, _root=dst_sbc._root)
    coltype.unk_01 = sbc_link_props.unk_01  # link_ob["unk_01"]
    coltype.unk_02 = sbc_link_props.unk_02  # link_ob["unk_02"]
    coltype.unk_03 = sbc_link_props.unk_03  # link_ob["unk_03"]
    coltype.unk_04 = sbc_link_props.unk_04  # [v for v in link_ob["unk_04"]]
    coltype.jp_path = sbc_link_props.jp_path  # link_ob["jp_path"]
    coltype._check()
    return coltype


def _serialize_pairs(dst_sbc, pairs_data):
    pairs = []
    for pd in pairs_data:
        pair = dst_sbc.SFacePair(_parent=dst_sbc, _root=dst_sbc._root)
        pair_raw = pd.primitiveSerialize()
        pair.face_01 = pair_raw["face1"]
        pair.face_02 = pair_raw["face2"]
        pair.quad_order = pair_raw["quadOrder"]
        pair.type = pair_raw["type"]
        pair._check()
        pairs.append(pair)
    return pairs


def _serialize_infos(dst_sbc, faces, vertices, stages, pairs, sbcs, sbcC, metadata):
    f0, v0, p0 = 0, 0, 0,
    infos = []
    for f, v, p, s, m in zip(faces, vertices, pairs, sbcs, metadata):
        info = dst_sbc.Info(_parent=dst_sbc, _root=dst_sbc._root)
        bbox = dst_sbc.Bbox4(_parent=info, _root=dst_sbc._root)
        bbox_data = get_vertex_box(v).serialize()
        bbox.min = [v for v in bbox_data["minPos"].values()]
        bbox.max = [v for v in bbox_data["maxPos"].values()]
        info.unk_01 = 0  # not really, looks like a hash
        info.nulls_01 = [0, 0]
        info.bounding_box = bbox
        info.start_pairs = p0
        info.num_pairs = len(p)
        info.start_faces = f0
        info.num_faces = len(f)
        info.start_vertices = v0
        info.num_vertices = len(v)
        info.index_id = int(m["indexID"])  # something wrong
        info.nulls_02 = [0, 0]
        info._check()
        f0 += len(f)
        v0 += len(v)
        p0 += len(p)
        infos.append(info)
        print("Vertex start {}".format(info.start_vertices))
    return infos


def get_vertex_box(v):
    return geo.BoundingBox(v)


class SemiTri():
    def __init__(self, face, mat_type=None):
        if not len(face.verts) == 3:
            raise TriangulationRequiredError()
        self.vert = [int(v.index) for v in face.verts]
        self.adjacent = self.getAdjacent(face)
        self.normal = SemiTri.calcNormal(face)
        # numeric id extracted form mat name
        self.type = mat_type
        # (0 = 90°, 1 = 0°, 2 > 180°, 3<180°)

    def getAdjacent(self, face):
        adjacents = []
        for edge in face.edges:
            bA = None
            # get faces linked edges of the give face
            for lf in edge.link_faces:
                if lf != face:
                    bA = SemiTri.byteAngle(face, lf)
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
            face1.verts[1].co - face1.verts[0].co, face1.verts[2].co - face1.verts[0].co))
        v.normalize()
        return v

    @staticmethod
    def edges(face):
        e1 = cycles(face.verts)
        return e1

    @staticmethod
    def barycenter(face):
        return sum([v.co for v in face.verts], Vector([0, 0, 0])) / len(face.verts)

    @staticmethod
    def byteAngle(face1, face2):
        # calculated angles between two faces
        n1 = SemiTri.calcNormal(face1)
        n2 = SemiTri.calcNormal(face2)
        fv1 = [v.co for v in face1.verts]
        e1 = SemiTri.edges(face1)
        e2 = SemiTri.edges(face2)
        facing = None
        for ix, e in enumerate(e1):
            if tuple(reversed(e)) in e2:
                edgem = (fv1[ix] + fv1[(ix + 1) % 3]) / 2
                bary = (SemiTri.barycenter(face1) + SemiTri.barycenter(face2)) / 2
                facing = bary - edgem
                facing.normalize()
        if facing is None:
            # Not exactly correct but correct most of the time (1.5% fail rate)
            return 0

        # eps = 0.0001
        if (n1 - n2).magnitude < EPS:
            return 1
        if (n1 + n2).magnitude < EPS:
            return 4
        n = (n1 + n2)
        n.normalize()
        signum = (n1 + n2).dot(facing) > 0
        if not signum:
            if n1.dot(n2) < EPS:
                return 0
            return 2
        else:
            return 4

    @staticmethod
    def getMaterial(face, mesh):
        try:
            ix = face.material_index
            slot = mesh.material_slots[ix]
            mat_name = slot.material.name
            #  extract id from mat name, clamp Type prefix and possible suffix and then converto to int
            mat_name = mat_name.replace("_", ".").split(".")[0]
            return int(mat_name[len("Type "):])
        except IndexError:
            raise MaterialMissingError


def mesh_to_tri(mesh):
    """ Get triangulated mesh, return list of Tri objects and vertices"""
    bm = bmesh.new()
    # bm.from_object(mesh, bpy.context.scene)
    bm.from_mesh(mesh.data)
    vertices = [Vector(v.co) for v in bm.verts]
    # classmethod .getMaterial of SemiTri gets material ID for each faces
    # SemiTri class stores face indices, mat ID and calculates a normal and adjacent faces
    # Tri is child of geometry primitive class stores SemiTri as dataFace and vertices
    faces = [Tri(SemiTri(face, SemiTri.getMaterial(face, mesh)), vertices)
             for face in bm.faces]
    bm.free()
    return vertices, faces


def mesh_to_tri156(mesh):
    bm = bmesh.new()
    # bm.from_object(mesh, bpy.context.scene)
    bm.from_mesh(mesh.data)
    unk_00 = bm.faces.layers.int.get('unk_00')
    unk_01 = bm.faces.layers.int.get('unk_01')
    type = bm.faces.layers.int.get('type')
    surface_attr = bm.faces.layers.int.get('surface_attr')
    special_attr = bm.faces.layers.int.get('special_attr')
    attr = []
    faces = []
    vertices = [Vector(v.co) for v in bm.verts]
    for face in bm.faces:
        faces.append(Tri(SemiTri(face), vertices))
        attr.append({'unk_00': face[unk_00] if unk_00 else 0,
                     'unk_01': face[unk_01] if unk_01 else 0,
                     'runtime_attr': SemiTri.getMaterial(face, mesh),
                     'type': face[type] if type else 0,
                     'surface_attr': face[surface_attr] if surface_attr else 0,
                     'special_attr': face[special_attr] if special_attr else 0})
    bm.free()
    return vertices, faces, attr


def mesh_rescale(ob):
    '''Meshes should be transformed back to the game's up axis and scale'''
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = ob.data

    # Swap Y and Z coordinates for each vertex and rescale
    for vert in mesh.vertices:
        x = vert.co.x * 100
        y = vert.co.y * -100
        z = vert.co.z * 100
        vert.co.x = x
        vert.co.y = z
        vert.co.z = y
    return ob


def write_vec3(data, dst_sbc):
    vec = dst_sbc.Vec3()
    vec.x = data[0]
    vec.y = data[1]
    vec.z = data[2]
    return vec


def write_vec4(data, dst_sbc):
    vec = dst_sbc.Vec4()
    vec.x = data[0]
    vec.y = data[1]
    vec.z = data[2]
    vec.w = data[3]
    return vec


class BaseSBCProperties(bpy.types.PropertyGroup):
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except TypeError:
                pass
                # print(f"Type mismatch {attr_name}, {src_obj}")


@blender_registry.register_custom_properties_object("sbc_156_collision", ("re5",), asset_type="COLLISION")
@blender_registry.register_blender_prop
class SBC156CollisionCustomProperties(bpy.types.PropertyGroup):
    pass


@blender_registry.register_custom_properties_object("sbc_21_collision", ("re0", "re1", "re6", "rev1",
                                                    "rev2", "dd",), asset_type="COLLISION")
@blender_registry.register_blender_prop
class SBC21CollisionCustomProperties(bpy.types.PropertyGroup):
    pass


@blender_registry.register_custom_properties_object(
    "sbc_21_link",
    ("re0", "re1", "re6", "rev1", "rev2", "dd",),
    is_secondary=True, display_name="SBC Link", asset_type="COLLISION")
@blender_registry.register_blender_prop
class SBC21LinkCustomProperties(BaseSBCProperties):
    unk_01: bpy.props.FloatProperty(name="Unknown 01", default=0.0, options=set())  # noqa: F821
    unk_02: bpy.props.IntProperty(name="Unknown 02", default=0, options=set())  # noqa: F821
    unk_03: bpy.props.IntProperty(name="Unknown 03", default=0, options=set())  # noqa: F821
    unk_04: bpy.props.IntVectorProperty(name="Unknown 04", size=3, default=(0, 0, 0),
                                        options=set())  # noqa: F821
    jp_path: bpy.props.IntVectorProperty(name="Japanese Path", size=12,
                                         default=(0, 0, 0, 0, 0, 0,
                                                  0, 0, 0, 0, 0, 0),
                                         options=set())  # noqa: F821


@blender_registry.register_custom_properties_object(
    "sbc_21_mesh",
    ("re0", "re1", "re6", "rev1", "rev2", "dd",),
    is_secondary=True, display_name="SBC Mesh", asset_type="COLLISION")
@blender_registry.register_blender_prop
class SBC21MeshCustomProperties(BaseSBCProperties):
    index_id: bpy.props.StringProperty(name="Index Id", default="4294967295", options=set())


# Code for debug visualization #

def _unpack_bbox(min, max):
    min_x, min_y, min_z = min[0], min[1], min[2]
    max_x, max_y, max_z = max[0], max[1], max[2]
    unpack_bbox = [
        (max_x, max_y, max_z),
        (min_x, max_y, max_z),
        (min_x, min_y, max_z),
        (max_x, min_y, max_z),
        (max_x, min_y, min_z),
        (max_x, max_y, min_z),
        (min_x, max_y, min_z),
        (min_x, min_y, min_z),
    ]
    return unpack_bbox


def _scale_bbox(box):
    scaled = []
    scaled = (box.x / 100, box.z / -100, box.y / 100)
    return scaled


def _transform_coordinates(verts):
    transformed = []
    for v in verts:
        vert = (v.position_x / 100, v.position_z / -100, v.position_y / 100)
        transformed.append(vert)
    return transformed


def _create_bbox(name, min, max):
    box_indices = [(3, 2, 1, 0),
                   (4, 5, 6, 7),
                   (2, 3, 4, 7),
                   (6, 5, 0, 1),
                   (1, 2, 7, 6),
                   (5, 4, 3, 0),
                   ]
    box_min = _scale_bbox(min)
    box_max = _scale_bbox(max)

    box = _unpack_bbox(box_min, box_max)
    b_mesh_data = bpy.data.meshes.new(name)
    b_mesh_data.from_pydata(box, [], box_indices)
    return b_mesh_data


def debug_create_nodes(sbc):
    colors = [(0.8, 0.65, 0, 1), (1, 0.9, 0, 1), (0.35, 0.54, 0.02, 1)]
    box_mats = ["m_node_main", "m_node_left", "m_node_right"]
    for i, m in enumerate(box_mats):
        if not bpy.data.materials.get(m):
            mat = bpy.data.materials.new(name=m)
            mat.diffuse_color = colors[i]
    collection = bpy.data.collections.get("DebugUNKNodes")
    if not collection:
        collection = bpy.data.collections.new("DebugUNKNodes")
        # Link the collection to the scene
        bpy.context.scene.collection.children.link(collection)

    for i, node in enumerate(sbc.nodes):
        if i >= sbc.header.num_parts + 1:
            break
        empty_name = "NodeRoot" + str(i)
        empty = bpy.data.objects.new(name=empty_name, object_data=None)
        collection = bpy.data.collections.get("DebugUNKNodes")
        empty.empty_display_type = 'PLAIN_AXES'
        collection.objects.link(empty)
        a_min = node.aabb_01.min
        a_max = node.aabb_01.max
        b_min = node.aabb_02.min
        b_max = node.aabb_02.max
        boxes = [(a_min, a_max), (b_min, b_max)]
        for j, b in enumerate(boxes):
            name = "bbox_test.001"
            b_mesh_data = _create_bbox(("sbc_unk_nodes_tests" + str(j)), b[0], b[1])
            b_mesh_obj = bpy.data.objects.new(name + "_" + str(j), b_mesh_data)
            b_mesh_obj.active_material = bpy.data.materials.get(box_mats[j])
            b_mesh_obj.parent = empty
            collection.objects.link(b_mesh_obj)


def debug_create_bbox(sbc):
    coll_name = "DebugSBCInfoBBoxes"
    collection = bpy.data.collections.get(coll_name)
    box_mats = ["m_sbc_main", "m_sbc_left", "m_sbc_right"]
    colors = [(0.53, 0.3, 0.73, 1), (1, 0.9, 0, 1), (0.35, 0.54, 0.02, 1)]
    for i, m in enumerate(box_mats):
        if not bpy.data.materials.get(m):
            mat = bpy.data.materials.new(name=m)
            mat.diffuse_color = colors[i]

    if not collection:
        collection = bpy.data.collections.new(coll_name)
        # Link the collection to the scene
        bpy.context.scene.collection.children.link(collection)

    bbox_min = sbc.sbcinfo.bounding_box.min
    bbox_max = sbc.sbcinfo.bounding_box.max

    a_min = sbc.sbcinfo.vmin[0]
    b_min = sbc.sbcinfo.vmin[1]
    a_max = sbc.sbcinfo.vmax[0]
    b_max = sbc.sbcinfo.vmax[1]
    boxes = [(bbox_min, bbox_max), (a_min, a_max), (b_min, b_max)]
    parent = None
    for i, b in enumerate(boxes):
        if i <= 0:
            name = "bounding_box.000"
        else:
            name = "bbox_test.001"
        b_mesh_data = _create_bbox(("sbs_nodes_test" + str(i)), b[0], b[1])
        b_mesh_obj = bpy.data.objects.new(name + "_" + str(i), b_mesh_data)
        b_mesh_obj.active_material = bpy.data.materials.get(box_mats[i])
        if not parent:
            parent = b_mesh_obj
        else:
            b_mesh_obj.parent = parent
        collection.objects.link(b_mesh_obj)


def debug_create_sbcinfo_nodes(node):
    empty = bpy.data.objects.new(name="NodeRoot", object_data=None)
    collection = bpy.data.collections.get("DebugNodes")
    empty.empty_display_type = 'PLAIN_AXES'

    if not collection:
        collection = bpy.data.collections.new("DebugNodes")
        bpy.context.scene.collection.children.link(collection)
    collection.objects.link(empty)

    mat_name = "m_node_debug"
    mat_color = (0.4, 0.75, 0.36, 1)
    if not bpy.data.materials.get(mat_name):
        mat = bpy.data.materials.new(name=mat_name)
        mat.diffuse_color = mat_color
    boxa = node.boxes[0]
    boxb = node.boxes[1]
    a_min = boxa.min
    b_min = boxb.min
    a_max = boxa.max
    b_max = boxb.max
    boxes = [(a_min, a_max), (b_min, b_max)]
    box_indices = [(3, 2, 1, 0),
                   (4, 5, 6, 7),
                   (2, 3, 4, 7),
                   (6, 5, 0, 1),
                   (1, 2, 7, 6),
                   (5, 4, 3, 0),
                   ]
    for i, b in enumerate(boxes):
        # name = _create_mesh_name(i, file_path)
        name = "node_test.001"
        ba_min = _scale_bbox(b[0])
        ba_max = _scale_bbox(b[1])

        box = _unpack_bbox(ba_min, ba_max)
        b_mesh_data = bpy.data.meshes.new("sbs_boxes_test" + str(i))
        b_mesh_data.from_pydata(box, [], box_indices)
        b_mesh_obj = bpy.data.objects.new(name + "_" + str(i), b_mesh_data)
        b_mesh_obj.parent = empty
        b_mesh_obj.active_material = bpy.data.materials.get(mat_name)
        collection.objects.link(b_mesh_obj)
