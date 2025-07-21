from binascii import crc32
from collections import namedtuple, OrderedDict
import ctypes
from itertools import chain
from io import BytesIO
from struct import pack, unpack
import math
try:
    from math import dist as get_dist
except ImportError:
    from albam.lib.blender import get_dist

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix
import numpy as np

from albam.apps import get_app_description
from albam.lib.blender import (
    get_bone_indices_and_weights_per_vertex,
    get_mesh_vertex_groups,
    get_model_bounding_box,
    get_model_bounding_sphere,
    get_normals_per_vertex,
    get_tangents_per_vertex,
    get_uvs_per_vertex,
    strip_triangles_to_triangles_list,
    triangles_list_to_triangles_strip,
)
from albam.lib.misc import chunks
from albam.lib.export_checks import check_all_objects_have_materials
from albam.registry import blender_registry
from albam.vfs import VirtualFileData
from albam.exceptions import AlbamCheckFailure
from .material import (
    build_blender_materials,
    serialize_materials_data,
    check_mtfw_shader_group,
)
from .texture import check_dds_textures
from .structs.mod_156 import Mod156
from .structs.mod_21 import Mod21


MOD_CLASS_MAPPER = {
    156: Mod156,
    210: Mod21,
    211: Mod21,
    212: Mod21,
}
APPID_CLASS_MAPPER = {
    "re0": Mod21,
    "re1": Mod21,
    "re5": Mod156,
    "re6": Mod21,
    "rev1": Mod21,
    "rev2": Mod21,
    "dd": Mod21,
}

MOD_VERSION_APPID_MAPPER = {
    156: {"re5"},
    210: {"re0", "re1", "rev1", "rev2"},
    211: {"re6"},
    212: {"dd"},
}

DEFAULT_VERTEX_FORMAT_SKIN = 0x14D40020
DEFAULT_VERTEX_FORMAT_NONSKIN = 0xa7d7d036

VERTEX_FORMATS_MAPPER = {
    0x0: Mod156.VfSkin,
    0x1: Mod156.VfSkinEx,
    0x2: Mod156.VfNonSkin,
    0x3: Mod156.VfNonSkinCol,
    0x4: Mod156.VfSkin,  # placeholder shape
    0x5: Mod156.VfSkin,  # placeholder skin_col
    # 0x4325a03e: Mod21.Vertex4325,  # IANonSkinTBN_4M shape keys not implemented yet
    # 0x2f55c03d: Mod21.Vertex2f55,  # IASkinOTB_4WT_4M shape keys not implemented yet
    0xa14e003c: Mod21.VertexA14e,  # IANonSkinBCA
    0x2082f03b: Mod21.Vertex2082,  # IANonSkinBLA
    0xc66fa03a: Mod21.VertexC66f,  # IANonSkinBA
    0xd1a47038: Mod21.VertexD1a4,  # IANonSkinBL
    0x207d6037: Mod21.Vertex207d,  # IANonSkinBC
    0xa7d7d036: Mod21.VertexA7d7,  # IANonSkinB
    0x37a4e035: Mod21.Vertex37a4,  # IANonSkinTBNLA
    0xb6681034: Mod21.VertexB668,  # IANonSkinTBNCA
    0x9399c033: Mod21.Vertex9399,  # IANonSkinTBCA
    0x12553032: Mod21.Vertex1255,  # IANonSkinTBLA
    0x747d1031: Mod21.Vertex747d,  # IANonSkinTBNA
    0x63b6c02f: Mod21.Vertex63b6,  # IANonSkinTBNL vertex alpha
    0x926fd02e: Mod21.Vertex926f,  # IANonSkinTBNC
    0xafa6302d: Mod21.VertexAfa6,  # IANonSkinTBA
    0x5e7f202c: Mod21.Vertex5e7f,  # IANonSkinTBN
    0xb86de02a: Mod21.VertexB86d,  # IANonSkinTBL vertex alpha
    0x49b4f029: Mod21.Vertex49b4,  # IANonSkinTBC
    0xd8297028: Mod21.Vertex8297,  # IANonSkinTB
    0xcbcf7027: Mod21.VertexCbcf,  # IASkinTBNLA8wt
    0xd84e3026: Mod21.VertexD84e,  # IASkinTBC8wt
    0x75c3e025: Mod21.Vertex75c3,  # IASkinTBN8wt
    0xbb424024: Mod21.VertexBb42,  # IASkinTB8wt
    0x64593023: Mod21.Vertex6459,  # IASkinTBNLA4wt
    0x77d87022: Mod21.Vertex77d8,  # IASkinTBC4wt
    0xdA55a021: Mod21.VertexDa55,  # IASkinTBN4wt
    0x14d40020: Mod21.Vertex14d4,  # IASkinTB4wt
    0xb392101f: Mod21.VertexB392,  # IASkinTBNLA2wt
    0xa013501e: Mod21.VertexA013,  # IASkinTBC2wt
    0xd9e801d: Mod21.VertexD9e8,  # IASkinTBN2wt
    0xc31f201c: Mod21.VertexC31f,  # IASkinTB2wt
    0xd877801b: Mod21.VertexD877,  # IASkinTBNLA1wt
    0xcbf6c01a: Mod21.VertexCbf6,  # IASkinTBC1wt
    0x667b1019: Mod21.Vertex667b,  # IASkinTBN1wt
    0xa8fab018: Mod21.VertexA8fa,  # IASkinTB1wt
    0xa320c016: Mod21.VertexA320,  # IASkinBridge8wt
    0xcb68015: Mod21.VertexCb68,  # IASkinBridge4wt
    0xdb7da014: Mod21.VertexDb7d,  # IASkinBridge2wt
    0xb0983013: Mod21.VertexB098,  # IASkinBridge1wt
}

VERTEX_FORMATS_RGBA = (
    0x3,
    0xa14e003c,
    0x207d6037,
    0xb6681034,
    0x9399c033,
    0x926fd02e,
    0x49b4f029,
    0xd84e3026,
    0x77d87022,
    0xa013501e,
    0xcbf6c01a,
)

VERTEX_FORMATS_VERTEX_ALPHA = (
    0x63b6c02f,
    0xb86de02a,
)

VERTEX_FORMATS_TANGENT = (
    0x0,
    0x2,
    0x3,
    0x4,
    0x5,
    0x4325a03e,
    0x2f55c03d,
    0x37a4e035,
    0xb6681034,
    0x9399c033,
    0x12553032,
    0x747d1031,
    0x63b6c02f,
    0x926fd02e,
    0xafa6302d,
    0x5e7f202c,
    0xb86de02a,
    0x49b4f029,
    0xd8297028,
    0xcbcf7027,
    0xd84e3026,
    0x75c3e025,
    0xbb424024,
    0x64593023,
    0x77d87022,
    0xdA55a021,
    0x14d40020,
    0xb392101f,
    0xa013501e,
    0xd9e801d,
    0xc31f201c,
    0xd877801b,
    0xcbf6c01a,
    0x667b1019,
    0xa8fab018,
)

VERTEX_FORMATS_UV2 = (
    0x0,
    0x2,
    0x3,
    0x4,
    0x5,
    0x4325a03e,
    0xa14e003c,
    0x2082f03b,
    0xc66fa03a,
    0xd1a47038,
    0x37a4e035,
    0xb6681034,
    0x9399c033,
    0x12553032,
    0x747d1031,
    0x63b6c02f,
    0x926fd02e,
    0xafa6302d,
    0x5e7f202c,
    0xb86de02a,
    0xcbcf7027,
    0x75c3e025,
    0x64593023,
    0xdA55a021,
    0xb392101f,
    0xd877801b,
    0x667b1019,
)

VERTEX_FORMATS_UV3 = (
    0x2,
    0x2082f03b,
    0x37a4e035,
    0xb6681034,
    0x12553032,
    0x747d1031,
    0x63b6c02f,
    0xcbcf7027,
    0x64593023,
    0xb392101f,
    0xd877801b,
)

VERTEX_FORMATS_UV4 = (
    0x37a4e035,
    0xcbcf7027,
    0x64593023,
    0xb392101f,
    0xd877801b,
)

VERTEX_FORMATS_BRIDGE = (
    0xa320c016,
    0xcb68015,
    0xdb7da014,
    0xb0983013,
)

VERTEX_FORMATS_NORMAL4 = (
    0xa14e003c,
    0x2082f03b,
    0xc66fa03a,
    0xd1a47038,
    0x207d6037,
    0xa7d7d036,
    0xa320c016,
    0xcb68015,
    0xdb7da014,
    0xb0983013,
)
VERTEX_FORMATS_BONE_LIMIT = {
    0x1: 8,
    0x0: 4,
    0x4: 4,
    0x5: 4,
    0xcbcf7027: 8,  # IASkinTBNLA8wt
    0xd84e3026: 8,  # IASkinTBC8wt
    0x75c3e025: 8,  # IASkinTBN8wt
    0xbb424024: 8,  # IASkinTB8wt
    0x64593023: 4,  # IASkinTBNLA4wt
    0x77d87022: 4,  # IASkinTBC4wt
    0xdA55a021: 4,  # IASkinTBN4wt
    0x14d40020: 4,  # IASkinTB4wt
    0xb392101f: 2,  # IASkinTBNLA2wt
    0xa013501e: 2,  # IASkinTBC2wt
    0xd9e801d: 2,  # IASkinTBN2wt
    0xc31f201c: 2,  # IASkinTB2wt
    0xd877801b: 1,  # IASkinTBNLA1wt
    0xcbf6c01a: 1,  # IASkinTBC1wt
    0x667b1019: 1,  # IASkinTBN1wt
    0xa8fab018: 1,  # IASkinTB1wt
    0xa320c016: 8,  # IASkinBridge8wt
    0xcb68015: 4,  # IASkinBridge4wt
    0xdb7da014: 2,  # IASkinBridge2wt
    0xb0983013: 1,  # IASkinBridge1wt
}

VERTEX_FORMAT_POS3S2 = [
    0xd877801b,
    0xcbf6c01a,
    0x667b1019,
    0xb0983013,
    0xa8fab018,
]

BBOX_AFFECTED = [
    0x667B1019,
    0xCBF6C01A,
    0xB0983013,
    0xA8FAB018,
    0xD877801B,
]

VERSIONS_USE_BONE_PALETTES = {156}
VERSIONS_BONES_BBOX_AFFECTED = {210, 211, 212}
VERSIONS_USE_TRISTRIPS = {156, 212}
MAIN_LODS = {
    "re0": [1, 255],
    "re1": [1, 255],
    "re5": [1, 255],
    "re6": [1, 3, 255],
    "rev1": [1, 255],
    "rev2": [1, 255],
    "dd": [1, 255],
}


def _validate_app_id_for_mod(app_id, mod_bytes):
    id_magic = mod_bytes[0:3]
    version = mod_bytes[4]

    app_desc = get_app_description(app_id)

    if id_magic != b'MOD':
        raise AlbamCheckFailure(
            "The file to import doesn't seem to be valid for "
            f"the app '{app_desc}'",
            details=f"The file has an incorrect ID Magic: {id_magic}",
            solution=f"Double check that this is a file from {app_desc}"
        )
    try:
        app_ids = MOD_VERSION_APPID_MAPPER[version]
        if app_id not in app_ids:
            raise AlbamCheckFailure(
                "The file to import doesn't seem to be valid for "
                f"the app '{app_desc}'",
                details=f"The file has an invalid version ({version}) for {app_desc}",
                solution="Double check that you selected the correct App and re-import"
            )
    except KeyError:
        raise AlbamCheckFailure(
            f"The version of this file ({version}) is not supported",
            details=f"The file has an invalid version ({version}) for {app_desc}",
            solution=f"Double check that this is a file from {app_desc}"
        )


@blender_registry.register_import_function(app_id="re0", extension="mod", file_category="MESH")
@blender_registry.register_import_function(app_id="re1", extension="mod", file_category="MESH")
@blender_registry.register_import_function(app_id="re5", extension="mod", file_category="MESH")
@blender_registry.register_import_function(app_id="re6", extension="mod", file_category="MESH")
@blender_registry.register_import_function(app_id="rev1", extension="mod", file_category="MESH")
@blender_registry.register_import_function(app_id="rev2", extension="mod", file_category="MESH")
@blender_registry.register_import_function(app_id="dd", extension="mod", file_category="MESH")
def build_blender_model(file_list_item, context):
    app_id = file_list_item.app_id
    mod_bytes = file_list_item.get_bytes()
    _validate_app_id_for_mod(app_id, mod_bytes)
    mod_version = mod_bytes[4]
    assert mod_version in MOD_CLASS_MAPPER, f"Unsupported version: {mod_version}"

    ModCls = MOD_CLASS_MAPPER[mod_version]
    mod = ModCls.from_bytes(mod_bytes)
    mod._read()

    import_settings = context.scene.albam.import_settings

    bl_object_name = file_list_item.display_name
    bbox_data = _create_bbox_data(mod)
    skeleton = None if mod.header.num_bones == 0 else build_blender_armature(
        mod, bl_object_name, bbox_data)
    bl_object = skeleton or bpy.data.objects.new(bl_object_name, None)
    materials = build_blender_materials(
        file_list_item, context, mod, bl_object_name)
    imported_lods = MAIN_LODS.get(app_id)

    for i, mesh in enumerate(mod.meshes_data.meshes):
        if import_settings.import_only_main_lods and mesh.level_of_detail not in imported_lods:
            continue
        try:
            name = f"{bl_object_name}_{str(i).zfill(4)}"
            material_hash = _get_material_hash(mod, mesh)

            bl_mesh_ob = build_blender_mesh(
                app_id, mod, mesh, name, bbox_data, mod_version in VERSIONS_USE_TRISTRIPS
            )
            bl_mesh_ob.parent = bl_object
            if skeleton:
                modifier = bl_mesh_ob.modifiers.new(
                    type="ARMATURE", name="armature")
                modifier.object = skeleton
                modifier.use_vertex_groups = True

            if materials.get(material_hash):
                bl_mesh_ob.data.materials.append(materials[material_hash])
            else:
                print(f"[{bl_object_name}] material {material_hash} not found")

        except Exception as err:
            print(f"[{bl_object_name}] error building mesh {i} {err}")
            continue

    bl_object.albam_asset.original_bytes = mod_bytes
    bl_object.albam_asset.app_id = app_id
    bl_object.albam_asset.relative_path = file_list_item.relative_path
    bl_object.albam_asset.extension = file_list_item.extension

    exportable = context.scene.albam.exportable.file_list.add()
    exportable.bl_object = bl_object

    context.scene.albam.exportable.file_list.update()

    return bl_object


def build_blender_mesh(app_id, mod, mesh, name, bbox_data, use_tri_strips=False):
    me_ob = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me_ob)

    locations = []
    normals = []
    uvs_1 = []
    uvs_2 = []
    uvs_3 = []
    uvs_4 = []
    vertex_colors = []
    weights_per_bone = {}

    for vertex_index, vertex in enumerate(mesh.vertices):
        _process_locations(mod.header.version, mesh, vertex, locations, bbox_data)
        _process_normals(vertex, normals)
        _process_uvs(vertex, uvs_1, uvs_2, uvs_3, uvs_4)
        _process_vertex_colors(mod.header.version, vertex, vertex_colors)
        _process_weights(mod, mesh, vertex, vertex_index, weights_per_bone)

    indices = strip_triangles_to_triangles_list(
        mesh.indices) if use_tri_strips else mesh.indices

    if min(indices) >= mesh.min_index:  # backwards compability workaround
        # convert indices for this mesh only, so they start at zero
        indices = [tri_idx - mesh.min_index for tri_idx in indices]
    # Blender crashes with corrrupt indices
    assert min(indices) >= 0, "Bad face indices"
    # Blender crashes with an empty sequence
    assert locations, "No vertices could be processed"

    me_ob.from_pydata(locations, [], chunks(indices, 3))

    _build_normals(me_ob, normals)
    _build_uvs(me_ob, uvs_1, "uv1")
    _build_uvs(me_ob, uvs_2, "uv2")
    _build_uvs(me_ob, uvs_3, "uv3")
    _build_uvs(me_ob, uvs_4, "uv4")
    _build_vertex_colors(me_ob, vertex_colors, "vc")
    _build_weights(ob, weights_per_bone)

    custom_properties = me_ob.albam_custom_properties.get_custom_properties_for_appid(
        app_id)
    custom_properties.copy_custom_properties_from(mesh)
    # XXX TMP hack, TODO convert vertex formats to enums
    if app_id != "re5":
        custom_properties.vertex_format = str(mesh.vertex_format)
    return ob


def _process_locations(mod_version, mesh, vertex, vertices_out, bbox_data):
    x = vertex.position.x
    y = vertex.position.y
    z = vertex.position.z

    w = getattr(vertex.position, "w", None)
    if w is not None and mod_version == 156:
        x = x / 32767 * bbox_data.width + bbox_data.min_x
        y = y / 32767 * bbox_data.height + bbox_data.min_y
        z = z / 32767 * bbox_data.depth + bbox_data.min_z

    elif (w is not None and mod_version in (210, 211, 212)) or (
            mod_version in (210, 211, 212) and mesh.vertex_format in BBOX_AFFECTED):
        x = x / 32767 * bbox_data.dimension + bbox_data.min_x
        y = y / 32767 * bbox_data.dimension + bbox_data.min_y
        z = z / 32767 * bbox_data.dimension + bbox_data.min_z

    # Y-up to z-up and cm to m
    vertices_out.append((x * 0.01, -z * 0.01, y * 0.01))


def _process_normals(vertex, normals_out):
    if not hasattr(vertex, "normal"):
        return
    # from [0, 255] o [-1, 1]
    x = ((vertex.normal.x / 255) * 2) - 1
    y = ((vertex.normal.y / 255) * 2) - 1
    z = ((vertex.normal.z / 255) * 2) - 1
    # y up to z up
    normals_out.append((x, -z, y))


def _process_uvs(vertex, uvs_1_out, uvs_2_out, uvs_3_out, uvs_4_out):
    if not hasattr(vertex, "uv"):
        return
    u = unpack("e", bytes(vertex.uv.u))[0]
    v = unpack("e", bytes(vertex.uv.v))[0]
    uvs_1_out.extend((u, 1 - v))

    if not hasattr(vertex, "uv2"):
        return
    u = unpack("e", bytes(vertex.uv2.u))[0]
    v = unpack("e", bytes(vertex.uv2.v))[0]
    uvs_2_out.extend((u, 1 - v))

    if not hasattr(vertex, "uv3"):
        return
    u = unpack("e", bytes(vertex.uv3.u))[0]
    v = unpack("e", bytes(vertex.uv3.v))[0]
    uvs_3_out.extend((u, 1 - v))

    if not hasattr(vertex, "uv4"):
        return
    u = unpack("e", bytes(vertex.uv4.u))[0]
    v = unpack("e", bytes(vertex.uv4.v))[0]
    uvs_4_out.extend((u, 1 - v))


def _process_vertex_colors(mod_version, vertex, rgba_out):
    if not hasattr(vertex, "rgba"):
        return
    b = vertex.rgba.x / 225
    g = vertex.rgba.y / 225
    r = vertex.rgba.z / 255
    a = vertex.rgba.w / 255
    rgba_out.append((r, g, b, a))


def _process_weights(mod, mesh, vertex, vertex_index, weights_per_bone):
    if not hasattr(vertex, "bone_indices"):
        return
    bone_indices = _get_bone_indices(mod, mesh, vertex.bone_indices)
    weights = _get_weights(mod, mesh, vertex)

    for bi, bone_index in enumerate(bone_indices):
        weight = weights[bi]
        if not weight:
            continue
        bone_data = weights_per_bone.setdefault(bone_index, [])
        bone_data.append((vertex_index, weights[bi]))

    return weights_per_bone


def _get_bone_indices(mod, mesh, bone_indices):
    mapped_bone_indices = []

    if mod.header.version in VERSIONS_USE_BONE_PALETTES:
        bone_palette = mod.bones_data.bone_palettes[mesh.idx_bone_palette]
        for bi, bone_index in enumerate(bone_indices):
            if bone_index >= bone_palette.unk_01:
                real_bone_index = mod.bones_data.bone_map[bone_index]
            else:
                try:
                    real_bone_index = mod.bones_data.bone_palettes[
                        mesh.idx_bone_palette].indices[bone_index]
                except IndexError:
                    # Behaviour not observed in original files so far
                    real_bone_index = bone_index
            mapped_bone_indices.append(real_bone_index)
    elif mesh.vertex_format in (
        0xC31F201C,
        0xB392101F,
    ):
        b1 = int(unpack("e", bone_indices[0])[0])
        b2 = int(unpack("e", bone_indices[1])[0])
        mapped_bone_indices.extend((b1, b2))
    elif mesh.vertex_format == 0xdb7da014:
        b1 = bone_indices[0]
        b2 = bone_indices[2]
        mapped_bone_indices.extend((b1, b2))
    else:
        mapped_bone_indices = bone_indices

    return mapped_bone_indices


def _get_weights(mod, mesh, vertex):
    if mod.header.version == 156 or mesh.vertex_format in (0xCB68015, 0xa320c016):
        return tuple([w / 255 for w in vertex.weight_values])

    # Assuming all vertex formats share this pattern.
    # TODO: verify
    if len(vertex.bone_indices) == 1:
        return (1.0,)
    # 2w
    elif mesh.vertex_format in (
        0xC31F201C,
        0xDB7DA014,
        0xb392101f,
    ):
        w1 = vertex.position.w / 32767
        w2 = 1.0 - w1
        return (w1, w2)
    # 4w
    elif mesh.vertex_format in (
        0x14D40020,
        0x2F55C03D,
        0x64593023,
        0xDA55A021,
        0x77D87022,
    ):
        w1 = vertex.position.w / 32767
        w2 = unpack("e", bytes(vertex.weight_values[0]))[0]
        w3 = unpack("e", bytes(vertex.weight_values[1]))[0]
        w4 = round(1.0 - w1 - w2 - w3, 3)
        return (w1, w2, w3, w4)
    # 8w
    elif mesh.vertex_format in (
        0x75C3E025,
        0xCBCF7027,
        0xBB424024,
        0xD84E3026,
    ):
        w1 = vertex.position.w / 32767
        w2 = vertex.weight_values[0] / 255
        w3 = vertex.weight_values[1] / 255
        w4 = vertex.weight_values[2] / 255
        w5 = vertex.weight_values[3] / 255
        w6 = unpack("e", bytes(vertex.weight_values2[0]))[0]
        w7 = unpack("e", bytes(vertex.weight_values2[1]))[0]
        w8 = 1.0 - w1 - w2 - w3 - w4 - w5 - w6 - w7
        return (w1, w2, w3, w4, w5, w6, w7, w8)
    else:
        print(
            f"Can't get weights for vertex_format '{hex(mesh.vertex_format)}'")
        return (0, 0, 0, 0)


def _build_normals(bl_mesh, normals):
    if not normals:
        return
    try:
        bl_mesh.create_normals_split()
    except AttributeError:
        # blender 4.1+
        pass
    bl_mesh.validate(clean_customdata=False)
    bl_mesh.update(calc_edges=True)
    # bl_mesh.polygons.foreach_set("use_smooth", [True] * len(bl_mesh.polygons))

    vert_normals = np.array(normals, dtype=np.float32)
    norms = np.linalg.norm(vert_normals, axis=1, keepdims=True)
    np.divide(vert_normals, norms, out=vert_normals, where=norms != 0)

    bl_mesh.normals_split_custom_set_from_vertices(vert_normals)
    try:
        bl_mesh.use_auto_smooth = True
    except AttributeError:
        # blender 4.1+
        pass


def _build_uvs(bl_mesh, uvs, name="uv"):
    if not uvs:
        return
    uv_layer = bl_mesh.uv_layers.new(name=name)
    per_loop_list = []
    for loop in bl_mesh.loops:
        offset = loop.vertex_index * 2
        per_loop_list.extend((uvs[offset], uvs[offset + 1]))
    uv_layer.data.foreach_set("uv", per_loop_list)


def _build_vertex_colors(bl_mesh, vertex_colors, name="imported_colors"):
    if len(vertex_colors) > 0:
        bl_mesh.vertex_colors.new(name=name)
        color_layer = bl_mesh.vertex_colors[name]
        for poly in bl_mesh.polygons:
            for loop_index in poly.loop_indices:
                loop = bl_mesh.loops[loop_index]
                if vertex_colors[loop.vertex_index]:
                    color_layer.data[loop_index].color = vertex_colors[loop.vertex_index]


def _build_weights(bl_obj, weights_per_bone):
    if not weights_per_bone:
        return
    for bone_index, data in weights_per_bone.items():
        vg = bl_obj.vertex_groups.new(name=str(bone_index))
        for vertex_index, weight_value in data:
            vg.add((vertex_index,), weight_value, "ADD")


def build_blender_armature(mod, armature_name, bbox_data):
    armature = bpy.data.armatures.new(armature_name)
    armature_ob = bpy.data.objects.new(armature_name, armature)
    armature_ob.show_in_front = True

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for i in bpy.context.scene.objects:
        i.select_set(False)
    bpy.context.collection.objects.link(armature_ob)
    bpy.context.view_layer.objects.active = armature_ob
    armature_ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    blender_bones = []
    scale = 0.01
    # TODO: do it at blender level
    # non_deform_bone_indices = get_non_deform_bone_indices(mod)
    for i, bone in enumerate(mod.bones_data.bones_hierarchy):
        blender_bone = armature.edit_bones.new(str(i))
        valid_parent = bone.idx_parent < 255
        blender_bone.parent = blender_bones[bone.idx_parent] if valid_parent else None
        # blender_bone.use_deform = False if i in non_deform_bone_indices else True
        m = mod.bones_data.inverse_bind_matrices[i]
        head = _transform_inverse_bind_matrix(mod, m, bbox_data)
        blender_bone.head = [head[0] * scale, -head[2] * scale, head[1] * scale]
        blender_bone.tail = [head[0] * scale, -head[2] * scale, (head[1] * scale) + 0.01]
        blender_bone['mtfw.anim_retarget'] = str(bone.idx_anim_map)
        blender_bones.append(blender_bone)

    bpy.ops.object.mode_set(mode="OBJECT")
    return armature_ob


def _transform_inverse_bind_matrix(mod, matrix, bbox_data):
    m = matrix
    bl_matrix = Matrix((
        (m.row_1.x, m.row_1.y, m.row_1.z, m.row_1.w),
        (m.row_2.x, m.row_2.y, m.row_2.z, m.row_2.w),
        (m.row_3.x, m.row_3.y, m.row_3.z, m.row_3.w),
        (m.row_4.x, m.row_4.y, m.row_4.z, m.row_4.w),
    )).transposed()  # directx to opengl style

    if mod.header.version in VERSIONS_BONES_BBOX_AFFECTED:
        # bbox-space to global-space
        scale_matrix = Matrix.Scale(bbox_data.dimension, 4)
        # create a translation matrix that doesn't affect scale component
        translation_matrix = (
            Matrix.Translation((bbox_data.min_x, bbox_data.min_y, bbox_data.min_z)) - Matrix.Scale(1, 4)
        )
        rot_x, rot_y, rot_z = bl_matrix.to_euler("XYZ")
        rotation_matrix = (
            Matrix.Rotation(rot_x, 4, "X")
            @ Matrix.Rotation(rot_y, 4, "Y")
            @ Matrix.Rotation(rot_z, 4, "Z")
        )

        bl_matrix = ((bl_matrix @ scale_matrix.inverted()) @ rotation_matrix.inverted()) - translation_matrix

    return bl_matrix.inverted().to_translation()


def _create_bbox_data(mod):
    BboxData = namedtuple(
        "BboxData",
        (
            "min_x",
            "min_y",
            "min_z",
            "max_x",
            "max_y",
            "max_z",
            "width",
            "height",
            "depth",
            "dimension",
        ),
    )
    min_length = abs(min(mod.bbox_min.x, mod.bbox_min.y, mod.bbox_min.z))
    max_length = max(abs(mod.bbox_max.x), abs(
        mod.bbox_max.y), abs(mod.bbox_max.z))
    dimension = min_length + max_length

    bbox_data = BboxData(
        min_x=mod.bbox_min.x,
        min_y=mod.bbox_min.y,
        min_z=mod.bbox_min.z,
        max_x=mod.bbox_max.x,
        max_y=mod.bbox_max.y,
        max_z=mod.bbox_max.z,
        width=mod.bbox_max.x - mod.bbox_min.x,
        height=mod.bbox_max.y - mod.bbox_min.y,
        depth=mod.bbox_max.z - mod.bbox_min.z,
        dimension=dimension,
    )

    return bbox_data


def _get_material_hash(mod, mesh):
    material_hash = None
    if mod.header.version == 156:
        material_hash = mesh.idx_material
    elif mod.header.version == 210 or mod.header.version == 212:
        material_name = mod.materials_data.material_names[mesh.idx_material]
        material_hash = crc32(material_name.encode()) ^ 0xFFFFFFFF
    elif mod.header.version == 211:
        material_hash = mod.materials_data.material_hashes[mesh.idx_material]
    return material_hash


@blender_registry.register_export_function(app_id="re0", extension="mod")
@blender_registry.register_export_function(app_id="re1", extension="mod")
@blender_registry.register_export_function(app_id="re5", extension="mod")
@blender_registry.register_export_function(app_id="re6", extension="mod")
@blender_registry.register_export_function(app_id="rev1", extension="mod")
@blender_registry.register_export_function(app_id="rev2", extension="mod")
@blender_registry.register_export_function(app_id="dd", extension="mod")
@check_dds_textures
@check_mtfw_shader_group
@check_all_objects_have_materials
def export_mod(bl_obj):
    export_settings = bpy.context.scene.albam.export_settings
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    Mod = APPID_CLASS_MAPPER[app_id]
    vfiles = []

    src_mod = Mod.from_bytes(asset.original_bytes)
    src_mod._read()
    dst_mod = Mod()
    # TODO: export options like visibility
    bl_meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    if export_settings.export_visible:
        bl_meshes = [mesh for mesh in bl_meshes if mesh.visible_get()]

    _serialize_top_level_mod(bl_meshes, src_mod, dst_mod)
    _init_mod_header(bl_obj, src_mod, dst_mod)

    bone_palettes = _create_bone_palettes(src_mod, bl_obj, bl_meshes)
    dst_mod.bones_data = _serialize_bones_data(bl_obj, bl_meshes, src_mod, dst_mod, bone_palettes)
    dst_mod.groups = _serialize_groups(src_mod, dst_mod)
    materials_map, mrl, vtextures = serialize_materials_data(asset, bl_meshes, src_mod, dst_mod)

    meshes_data, vertex_buffer, vertex_buffer_2, index_buffer = (
        _serialize_meshes_data(bl_obj, bl_meshes, src_mod, dst_mod, materials_map, bone_palettes))
    dst_mod.header.num_vertices = sum(m.num_vertices for m in meshes_data.meshes)
    dst_mod.meshes_data = meshes_data
    dst_mod.vertex_buffer = vertex_buffer
    dst_mod.vertex_buffer_2 = vertex_buffer_2
    dst_mod.index_buffer = index_buffer

    offset = dst_mod.size_top_level_
    dst_mod.header.offset_bones_data = offset
    dst_mod.header.offset_groups = offset + dst_mod.bones_data_size_
    dst_mod.header.offset_materials_data = dst_mod.header.offset_groups + dst_mod.groups_size_
    dst_mod.header.offset_meshes_data = dst_mod.header.offset_materials_data + dst_mod.materials_data.size_
    dst_mod.header.offset_vertex_buffer = dst_mod.header.offset_meshes_data + dst_mod.meshes_data.size_
    dst_mod.header.offset_vertex_buffer_2 = dst_mod.header.offset_vertex_buffer + len(vertex_buffer)
    dst_mod.header.offset_index_buffer = dst_mod.header.offset_vertex_buffer_2 + len(vertex_buffer_2)

    dst_mod.header.size_vertex_buffer = len(vertex_buffer)
    dst_mod.header.size_vertex_buffer_2 = len(vertex_buffer_2)
    # TODO: revise, name accordingly
    dst_mod.header.num_faces = (len(index_buffer) // 2) + 1
    if app_id not in ["re5", "dd"]:
        index_buffer.extend((0, 0))

    final_size = sum((
        offset,
        dst_mod.bones_data_size_,
        dst_mod.groups_size_,
        dst_mod.materials_data.size_,
        dst_mod.meshes_data.size_,
        dst_mod.header.size_vertex_buffer,
        dst_mod.header.size_vertex_buffer_2,
        len(index_buffer) + 4,
    ))

    dst_mod.header.size_file = final_size
    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_mod._check()
    dst_mod._write(stream)

    mod_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
    vfiles.append(mod_vf)
    vfiles.extend(vtextures)
    if mrl:
        vfiles.append(mrl)
    return vfiles


def _init_mod_header(bl_obj, src_mod, dst_mod):
    dst_mod_header = dst_mod.ModHeader(_parent=dst_mod, _root=dst_mod._root)
    dst_mod_header.__dict__.update(dict(
        ident=b"MOD\x00",
        version=src_mod.header.version,
        revision=1,
        num_bones=0,
        num_meshes=0,
        num_materials=0,
        num_vertices=0,
        num_faces=0,
        num_edges=0,
        size_vertex_buffer=0,
        num_groups=src_mod.header.num_groups,
        offset_bones_data=0,
        offset_groups=0,
        offset_materials_data=0,
        offset_meshes_data=0,
        offset_vertex_buffer=0,
        offset_index_buffer=0,
    ))

    if dst_mod_header.version in VERSIONS_USE_BONE_PALETTES:
        dst_mod_header.num_bone_palettes = 0
        dst_mod_header.size_vertex_buffer_2 = 0
        dst_mod_header.num_textures = 0
        dst_mod_header.offset_vertex_buffer_2 = 0
    if dst_mod_header.version in (210, 211, 212):
        dst_mod_header.revision = 0
        dst_mod_header.reserved_01 = 0

    dst_mod_header._check()
    dst_mod.header = dst_mod_header
    return dst_mod_header


def _serialize_top_level_mod(bl_meshes, src_mod, dst_mod):
    SCALE = 100

    bl_bbox = get_model_bounding_box(bl_meshes)
    sphere = get_model_bounding_sphere(bl_meshes)

    dst_mod.bsphere = dst_mod.Vec4(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.bsphere.x = sphere[0] * SCALE
    dst_mod.bsphere.y = sphere[2] * SCALE
    dst_mod.bsphere.z = -sphere[1] * SCALE
    dst_mod.bsphere.w = sphere[3] * SCALE
    dst_mod.bbox_min = dst_mod.Vec4(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.bbox_min.x = bl_bbox.min_x * SCALE
    dst_mod.bbox_min.y = bl_bbox.min_z * SCALE
    dst_mod.bbox_min.z = -bl_bbox.max_y * SCALE
    dst_mod.bbox_min.w = 0  # TODO: research
    dst_mod.bbox_max = dst_mod.Vec4(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.bbox_max.x = bl_bbox.max_x * SCALE
    dst_mod.bbox_max.y = bl_bbox.max_z * SCALE
    dst_mod.bbox_max.z = -bl_bbox.min_y * SCALE
    dst_mod.bbox_max.w = 0  # TODO: research

    dst_mod.model_info = dst_mod.ModelInfo(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.model_info.middist = src_mod.model_info.middist
    dst_mod.model_info.lowdist = src_mod.model_info.lowdist
    dst_mod.model_info.light_group = src_mod.model_info.light_group
    dst_mod.model_info.strip_type = src_mod.model_info.strip_type
    dst_mod.model_info.memory = src_mod.model_info.memory
    dst_mod.model_info.reserved = src_mod.model_info.reserved

    if src_mod.header.version == 156:
        dst_mod.rcn_header = dst_mod.RcnHeader(_parent=dst_mod, _root=dst_mod._root)
        dst_mod.reserved_01 = src_mod.reserved_01
        dst_mod.reserved_02 = src_mod.reserved_02
        dst_mod.rcn_header.ptri = src_mod.rcn_header.ptri
        dst_mod.rcn_header.pvtx = src_mod.rcn_header.pvtx
        dst_mod.rcn_header.ptb = src_mod.rcn_header.ptb
        dst_mod.rcn_header.num_tri = 0
        dst_mod.rcn_header.num_vtx = 0
        dst_mod.rcn_header.num_tbl = 0
        dst_mod.rcn_header.parts = 0
        dst_mod.rcn_header.reserved = 0
        dst_mod.rcn_tables = []
        dst_mod.rcn_vertices = []
        dst_mod.rcn_trianlges = []

    if src_mod.header.version in (210, 212):
        dst_mod.num_weight_bounds = 0


def _serialize_bones_data(bl_obj, bl_meshes, src_mod, dst_mod, bone_palettes=None):
    if bl_obj.type != "ARMATURE":
        return
    export_settings = bpy.context.scene.albam.export_settings
    export_bones = export_settings.export_bones
    bone_magnitudes, bone_transfroms, parent_space_matrix, invert_bind_matix = _get_bone_transforms(
        bl_obj, dst_mod)
    dst_mod.header.num_bones = src_mod.header.num_bones
    bones_data = dst_mod.BonesData(_parent=dst_mod, _root=dst_mod._root)
    bones_data.bone_map = src_mod.bones_data.bone_map
    bones_data.bones_hierarchy = []
    bones_data.parent_space_matrices = []
    bones_data.inverse_bind_matrices = []

    if bone_palettes:
        bones_data.bone_palettes = []
        dst_mod.header.num_bone_palettes = len(bone_palettes)
        for i, bp in enumerate(bone_palettes.values()):
            bone_palette = dst_mod.BonePalette(
                _parent=bones_data, _root=bones_data._root)
            bone_palette.unk_01 = len(bp)
            if len(bp) != 32:
                padding = 32 - len(bp)
                bp = bp + [0] * padding
            bone_palette.indices = bp
            bones_data.bone_palettes.append(bone_palette)
            bone_palette._check()

    for i in range(dst_mod.header.num_bones):
        src_bone = src_mod.bones_data.bones_hierarchy[i]
        bone = dst_mod.Bone(_parent=bones_data, _root=bones_data._root)
        bone.idx_anim_map = src_bone.idx_anim_map
        bone.idx_parent = src_bone.idx_parent
        bone.idx_mirror = src_bone.idx_mirror
        bone.idx_mapping = src_bone.idx_mapping
        bone.unk_01 = src_bone.unk_01
        if export_bones:
            bone.parent_distance = bone_magnitudes[i]
        else:
            bone.parent_distance = src_bone.parent_distance
        loc = dst_mod.Vec3(_parent=bone, _root=bone._root)
        if export_bones:
            loc.x = bone_transfroms[i].x
            loc.y = bone_transfroms[i].y
            loc.z = bone_transfroms[i].z
        else:
            loc.x = src_bone.location.x
            loc.y = src_bone.location.y
            loc.z = src_bone.location.z
        bone.location = loc

        # TODO: be concise with struct (e.g. array of floats)
        m = dst_mod.Matrix4x4(_parent=bones_data, _root=bones_data._root)
        if export_bones:
            src_m = parent_space_matrix[i]
            m.row_1 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_1.x = src_m[0][0]
            m.row_1.y = src_m[0][1]
            m.row_1.z = src_m[0][2]
            m.row_1.w = src_m[0][3]
            m.row_2 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_2.x = src_m[1][0]
            m.row_2.y = src_m[1][1]
            m.row_2.z = src_m[1][2]
            m.row_2.w = src_m[1][3]
            m.row_3 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_3.x = src_m[2][0]
            m.row_3.y = src_m[2][1]
            m.row_3.z = src_m[2][2]
            m.row_3.w = src_m[2][3]
            m.row_4 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_4.x = src_m[3][0]
            m.row_4.y = src_m[3][1]
            m.row_4.z = src_m[3][2]
            m.row_4.w = src_m[3][3]
        else:
            src_m = src_mod.bones_data.parent_space_matrices[i]
            m.row_1 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_1.x = src_m.row_1.x
            m.row_1.y = src_m.row_1.y
            m.row_1.z = src_m.row_1.z
            m.row_1.w = src_m.row_1.w
            m.row_2 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_2.x = src_m.row_2.x
            m.row_2.y = src_m.row_2.y
            m.row_2.z = src_m.row_2.z
            m.row_2.w = src_m.row_2.w
            m.row_3 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_3.x = src_m.row_3.x
            m.row_3.y = src_m.row_3.y
            m.row_3.z = src_m.row_3.z
            m.row_3.w = src_m.row_3.w
            m.row_4 = dst_mod.Vec4(_parent=m, _root=m._root)
            m.row_4.x = src_m.row_4.x
            m.row_4.y = src_m.row_4.y
            m.row_4.z = src_m.row_4.z
            m.row_4.w = src_m.row_4.w

        # TODO: be concise with struct (e.g. array of floats)
        m2 = dst_mod.Matrix4x4(_parent=bones_data, _root=bones_data._root)
        if export_bones:
            src_m2 = invert_bind_matix[i]
        else:
            src_m2 = src_mod.bones_data.inverse_bind_matrices[i]
        m2.row_1 = dst_mod.Vec4(_parent=m2, _root=m._root)
        m2.row_2 = dst_mod.Vec4(_parent=m2, _root=m._root)
        m2.row_3 = dst_mod.Vec4(_parent=m2, _root=m._root)
        m2.row_4 = dst_mod.Vec4(_parent=m2, _root=m._root)

        if dst_mod.header.version in VERSIONS_BONES_BBOX_AFFECTED and not export_bones:
            # unapply transforms and apply the ones from the bbox to export
            # TODO: avoid doing this if bbox didn´t change
            src_bbox_data = _create_bbox_data(src_mod)
            dst_bbox_data = _create_bbox_data(dst_mod)
            r1x = round(src_m2.row_1.x - src_bbox_data.dimension + 1, 1)
            r2y = round(src_m2.row_2.y - src_bbox_data.dimension + 1, 1)
            r3z = round(src_m2.row_3.z - src_bbox_data.dimension + 1, 1)
            r4x = src_m2.row_4.x - src_bbox_data.min_x
            r4y = src_m2.row_4.y - src_bbox_data.min_y
            r4z = src_m2.row_4.z - src_bbox_data.min_z

            m2.row_1.x = round(r1x + dst_bbox_data.dimension - 1, 1)
            m2.row_2.y = round(r2y + dst_bbox_data.dimension - 1, 1)
            m2.row_3.z = round(r3z + dst_bbox_data.dimension - 1, 1)
            m2.row_4.x = r4x + dst_bbox_data.min_x
            m2.row_4.y = r4y + dst_bbox_data.min_y
            m2.row_4.z = r4z + dst_bbox_data.min_z
        else:
            if not export_bones:
                m2.row_1.x = src_m2.row_1.x
                m2.row_2.y = src_m2.row_2.y
                m2.row_3.z = src_m2.row_3.z
                m2.row_4.x = src_m2.row_4.x
                m2.row_4.y = src_m2.row_4.y
                m2.row_4.z = src_m2.row_4.z
        if export_bones:
            m2.row_1.x = src_m2[0][0]
            m2.row_1.y = src_m2[0][1]
            m2.row_1.z = src_m2[0][2]
            m2.row_1.w = src_m2[0][3]

            m2.row_2.x = src_m2[1][0]
            m2.row_2.y = src_m2[1][1]
            m2.row_2.z = src_m2[1][2]
            m2.row_2.w = src_m2[1][3]

            m2.row_3.x = src_m2[2][0]
            m2.row_3.y = src_m2[2][1]
            m2.row_3.z = src_m2[2][2]
            m2.row_3.w = src_m2[2][3]

            m2.row_4.w = src_m2[3][3]
            m2.row_4.x = src_m2[3][0]
            m2.row_4.y = src_m2[3][1]
            m2.row_4.z = src_m2[3][2]
        else:
            m2.row_1.y = src_m2.row_1.y
            m2.row_1.z = src_m2.row_1.z
            m2.row_1.w = src_m2.row_1.w

            m2.row_2.x = src_m2.row_2.x
            m2.row_2.z = src_m2.row_2.z
            m2.row_2.w = src_m2.row_2.w

            m2.row_3.x = src_m2.row_3.x
            m2.row_3.y = src_m2.row_3.y
            m2.row_3.w = src_m2.row_3.w

            m2.row_4.w = src_m2.row_4.w

        bones_data.bones_hierarchy.append(bone)
        bones_data.parent_space_matrices.append(m)
        bones_data.inverse_bind_matrices.append(m2)

    bones_data._check()
    return bones_data


def _restore_martix(m):
    restored_matrix = m.copy()
    restored_matrix.inverted()

    location = restored_matrix.to_translation()
    x, y, z = location
    location.x = x * 100
    location.y = z * -100
    location.z = y * 100
    restored_matrix.translation = location
    return restored_matrix.transposed()


def _get_bone_transforms(armature, mod):
    magnitudes = []
    bone_locations = []
    bone_matrices_local = []
    bone_matrices_inverse = []
    for bone in armature.data.bones:
        parent_bone = bone.parent
        rotation_matrix = Matrix.Rotation(math.radians(-90), 4, 'X')
        if parent_bone:
            parent_space_matrix = parent_bone.matrix_local.inverted() @ bone.matrix_local
            # relative_head_coords = bone.head - parent_bone.head
        else:
            parent_space_matrix = rotation_matrix @ bone.matrix_local
            print("The bone has no parent.")
        print("Bone:", bone.name)
        # inverse space
        inverse_space_matrix = bone.matrix_local
        inverse_space_matrix = rotation_matrix @ inverse_space_matrix
        inverse_translation = inverse_space_matrix.to_translation() * 100
        inverse_space_copy = inverse_space_matrix.copy()
        inverse_space_copy.translation = inverse_translation
        if mod.header.version in VERSIONS_BONES_BBOX_AFFECTED:
            # copied code from _create_bbox_data()
            min_length = abs(min(mod.bbox_min.x, mod.bbox_min.y, mod.bbox_min.z))
            max_length = max(abs(mod.bbox_max.x), abs(
                mod.bbox_max.y), abs(mod.bbox_max.z))
            dimension = min_length + max_length
            # shift the matrix to the bbox space and scale it
            translation_matrix = Matrix.Translation(
                (mod.bbox_min.x, mod.bbox_min.y, mod.bbox_min.z)) - Matrix.Scale(1, 4)
            scale_matrix = Matrix.Scale(dimension, 4)
            ibbox_matrix = inverse_space_copy.inverted()
            ibbox_matrix = ibbox_matrix @ scale_matrix + translation_matrix
            bone_matrices_inverse.append(ibbox_matrix.transposed())
        else:
            bone_matrices_inverse.append(inverse_space_copy.inverted().transposed())

        parent_translation = parent_space_matrix.to_translation() * 100
        bone_locations.append(parent_translation)
        # local space
        parent_space_copy = parent_space_matrix.copy()
        parent_space_copy.translation = parent_translation
        # bone_matrices_local.append(parent_space_matrix.transposed())
        bone_matrices_local.append(parent_space_copy.transposed())

        magnitude = math.sqrt(parent_translation[0]**2 + parent_translation[1]**2 + parent_translation[2]**2)
        magnitudes.append(magnitude)
        print("Parent space Matrix:")
        # print(parent_space_matrix.transposed())
        print(parent_space_copy.transposed())
        print("Translation:", parent_translation)
        print("Magnitude:", magnitude)
        print("Inverse space Matrix:")
        if mod.header.version in VERSIONS_BONES_BBOX_AFFECTED:
            print(ibbox_matrix.transposed())
        else:
            print(inverse_space_copy.inverted().transposed())

    return magnitudes, bone_locations, bone_matrices_local, bone_matrices_inverse


def _normalize_uv(uv_x, uv_y):
    """Flip UV for .dds and replace forbidden for half float -0.0 values"""
    uv_y *= -1
    uv_y += 1
    uv_y = 0.0 if uv_y == -0.0 else uv_y
    uv_x = 0.0 if uv_x == -0.0 else uv_x
    return uv_x, uv_y


def _get_vertex_colors(blender_mesh):
    mesh = blender_mesh.data
    colors = {}
    try:
        color_layer = mesh.vertex_colors[0]
    except IndexError:
        return colors
    mesh_loops = {li: loop.vertex_index for li, loop in enumerate(mesh.loops)}
    vtx_colors = {mesh_loops[li]: data.color for li,
                  data in color_layer.data.items()}
    for idx, color in vtx_colors.items():
        b = round(color[0] * 255)
        g = round(color[1] * 255)
        r = round(color[2] * 255)
        a = round(color[3] * 255)
        colors[idx] = (r, g, b, a)
    return colors


def _create_bone_palettes(src_mod, bl_armature, bl_meshes):
    if src_mod.header.version != 156:
        return {}
    bone_palette_dicts = []
    MAX_BONE_PALETTE_SIZE = 32

    bone_palette = {'mesh_indices': set(), 'bone_indices': set()}
    for i, mesh in enumerate(bl_meshes):

        mesh_vertex_groups = get_mesh_vertex_groups(mesh)
        bone_indices = {
            bl_armature.pose.bones.find(mesh.vertex_groups[vgi].name)
            for vgi, vertices in mesh_vertex_groups.items() if vertices
        }
        bone_indices = {bi for bi in bone_indices if bi != -1}

        # TODO: check at export time for all meshes
        msg = f"Mesh {mesh.name} is influenced by more than 32 bones, which is not supported"
        assert len(bone_indices) <= MAX_BONE_PALETTE_SIZE, msg

        current = bone_palette['bone_indices']
        potential = current.union(bone_indices)
        if len(potential) > MAX_BONE_PALETTE_SIZE:
            bone_palette_dicts.append(bone_palette)
            bone_palette = {'mesh_indices': {i},
                            'bone_indices': set(bone_indices)}
        else:
            bone_palette['mesh_indices'].add(i)
            bone_palette['bone_indices'].update(bone_indices)

    bone_palette_dicts.append(bone_palette)

    final = OrderedDict([(frozenset(bp['mesh_indices']), sorted(bp['bone_indices']))
                        for bp in bone_palette_dicts])

    return final


def _serialize_groups(src_mod, dst_mod):
    groups = []
    for i in range(dst_mod.header.num_groups):
        src_group = src_mod.groups[i]
        g = dst_mod.Group(_parent=dst_mod, _root=dst_mod._root)
        g.group_index = src_group.group_index
        g.reserved = [src_group.reserved[0],
                      src_group.reserved[1],
                      src_group.reserved[2],
                      ]
        g.pos = dst_mod.Vec3(_parent=g, _root=g._root)
        g.pos.x = src_group.pos.x
        g.pos.y = src_group.pos.y
        g.pos.z = src_group.pos.z
        g.radius = src_group.radius

        groups.append(g)
    return groups


def _check_weights(weights, max_weights):
    _weights = []
    i = max_weights - 4
    weights.extend([0] * (max_weights - len(weights)))
    if max_weights in [1, 2]:
        return weights
    _weights.append(round(weights[0] * 32767) / 32767)
    if max_weights == 8:
        _weights.append(round(weights[1] * 255) / 255)
        _weights.append(round(weights[2] * 255) / 255)
        _weights.append(round(weights[3] * 255) / 255)
        _weights.append(round(weights[4] * 255) / 255)
    _weights.append(unpack("e", pack("e", weights[i + 1]))[0])
    _weights.append(unpack("e", pack("e", weights[i + 2]))[0])
    _weights.append(weights[i + 3])
    return _weights


def _check_armature(bl_mesh):
    for modifier in bl_mesh.modifiers:
        if modifier.type == 'ARMATURE' and modifier.object:
            return True
    return False


def _serialize_meshes_data(bl_obj, bl_meshes, src_mod, dst_mod, materials_map, bone_palettes=None):
    export_settings = bpy.context.scene.albam.export_settings
    app_id = bl_obj.albam_asset.app_id
    dst_mod.header.num_meshes = len(bl_meshes)
    meshes_data = dst_mod.MeshesData(_parent=dst_mod, _root=dst_mod._root)
    meshes_data.meshes = []
    meshes_data.weight_bounds = []

    vertex_buffer = bytearray()
    vertex_buffer_2 = bytearray()
    index_buffer = bytearray()
    bbox_data = _create_bbox_data(dst_mod)
    use_strips = dst_mod.header.version in VERSIONS_USE_TRISTRIPS

    current_vertex_position = 0
    current_vertex_offset = 0
    vertex_offset_accumulated = 0
    current_vertex_offset_2 = 0
    vertex_offset_2_accumulated = 0
    current_vertex_format = None
    total_num_vertices = 0

    face_position = 0
    face_offset = 0  # unused for now

    for mesh_index, bl_mesh in enumerate(bl_meshes):
        face_padding = 0 if app_id not in ["re5", "dd"] else 2
        mesh = dst_mod.Mesh(_parent=meshes_data, _root=meshes_data._root)
        mesh.indices__to_write = False
        mesh.vertices__to_write = False
        mesh.vertices2__to_write = False
        mesh_bone_palette = None
        mesh_bone_palette_index = None
        if bone_palettes:
            mesh_bone_palette = None
            for bpi, (meshes_indices, bp) in enumerate(bone_palettes.items()):
                if mesh_index in meshes_indices:
                    mesh_bone_palette_index = bpi
                    mesh_bone_palette = bp
                    break
            else:
                raise ValueError(
                    f"Mesh {mesh_index} doesn't have a bone_palette")

        vertices, vertices2, vertex_format, vertex_stride, vertex_stride_2, max_bones_per_vertex = (
            _export_vertices(app_id, bl_mesh, mesh,
                             mesh_bone_palette, dst_mod, bbox_data)
        )
        vertex_buffer.extend(vertices.to_byte_array())
        if vertices2:
            vertex_buffer_2.extend(vertices2.to_byte_array())
        if vertex_format != current_vertex_format or export_settings.no_vf_grouping:
            current_vertex_offset = vertex_offset_accumulated
            current_vertex_offset_2 = vertex_offset_2_accumulated
            current_vertex_position = 0
            current_vertex_format = vertex_format

        if use_strips:
            triangles = triangles_list_to_triangles_strip(bl_mesh)
        else:
            triangles = list(chain.from_iterable(
                p.vertices for p in bl_mesh.data.polygons))

        triangles = [e + current_vertex_position for e in triangles]
        num_indices = len(triangles)
        if app_id in ["re5", "dd"]:
            # calculate padding for indices
            if ((num_indices * 2) % 4):
                triangles.append(triangles[-1])
                face_padding += 1
            triangles.append(triangles[-1])
            triangles.append(0)

        triangles_ctypes = (ctypes.c_ushort * len(triangles))(*triangles)
        index_buffer.extend(triangles_ctypes)
        num_vertices = len(bl_mesh.data.vertices)

        # Beware of vertex_format being a string type, overriden below
        custom_properties = bl_mesh.data.albam_custom_properties.get_custom_properties_for_appid(
            app_id)
        if export_settings.force_lod255:
            custom_properties.level_of_detail = 255
        custom_properties.copy_custom_properties_to(mesh)

        # TODO: pre-check for no materials
        mesh.idx_material = materials_map[bl_mesh.data.materials[0].name]
        mesh.vertex_format = vertex_format
        mesh.vertex_stride = vertex_stride
        mesh.vertex_stride_2 = vertex_stride_2
        # assert num_vertices == len(vertices_array) // 32
        mesh.num_vertices = num_vertices
        mesh.vertex_position_2 = current_vertex_position
        mesh.vertex_offset = current_vertex_offset
        mesh.face_position = face_position
        mesh.num_indices = num_indices
        mesh.face_offset = face_offset
        mesh.vertex_position = current_vertex_position
        mesh.min_index = current_vertex_position
        mesh.max_index = current_vertex_position + \
            mesh.num_vertices - 1  # XXX only a short!
        mesh.vertex_offset_2 = current_vertex_offset_2
        mesh.idx_bone_palette = mesh_bone_palette_index
        mesh.num_weight_bounds = 1
        # DD original hack, weapon meshes invisible without it
        if export_settings.force_max_num_weights:
            bone_limit = VERTEX_FORMATS_BONE_LIMIT.get(vertex_format)
            if bone_limit == 4 and max_bones_per_vertex < 4:
                max_bones_per_vertex = 4
            elif bone_limit == 8 and max_bones_per_vertex < 5:
                max_bones_per_vertex = 5
        mesh.max_bones_per_vertex = max_bones_per_vertex

        if dst_mod.header.version in (156,):
            mesh.reserved2 = 0
            mesh.connective = 0

        mesh._check()
        meshes_data.meshes.append(mesh)
        mesh_weight_bounds = _calculate_weight_bounds(
            bl_obj, bl_mesh, dst_mod, meshes_data)
        meshes_data.weight_bounds.extend(mesh_weight_bounds)
        mesh.num_weight_bounds = len(mesh_weight_bounds)

        current_vertex_position += num_vertices
        vertex_offset_accumulated += (num_vertices * vertex_stride)
        vertex_offset_2_accumulated += (num_vertices * vertex_stride_2)
        face_position += (num_indices + face_padding)
        total_num_vertices += mesh.num_vertices

    if dst_mod.header.version in (156, 211):
        meshes_data.num_weight_bounds = len(meshes_data.weight_bounds)
    else:
        dst_mod.num_weight_bounds = len(meshes_data.weight_bounds)

    meshes_data._check()
    return meshes_data, vertex_buffer, vertex_buffer_2, index_buffer


def _export_vertices(app_id, bl_mesh, mesh, mesh_bone_palette, dst_mod, bbox_data):
    SCALE = 100
    uvs_per_vertex = get_uvs_per_vertex(bl_mesh, 0)
    uvs_per_vertex_2 = get_uvs_per_vertex(bl_mesh, 1)
    uvs_per_vertex_3 = get_uvs_per_vertex(bl_mesh, 2)
    uvs_per_vertex_4 = get_uvs_per_vertex(bl_mesh, 3)
    color_per_vertex = _get_vertex_colors(bl_mesh)
    weights_per_vertex = get_bone_indices_and_weights_per_vertex(bl_mesh)
    max_bones_per_vertex = max({len(data) for data in weights_per_vertex.values()}, default=0)
    normals = get_normals_per_vertex(bl_mesh.data)
    tangents = get_tangents_per_vertex(bl_mesh.data)
    vtx_stream_2 = None
    vtx_stride_2 = 0
    has_vertex_buffer_2 = False
    has_bones = bool(dst_mod.header.num_bones)

    albam_custom_props = bl_mesh.material_slots[0].material.albam_custom_properties
    mod_156_material_props = albam_custom_props.get_custom_properties_for_appid(app_id)

    vertex_count = len(bl_mesh.data.vertices)
    if dst_mod.header.version == 156:
        vertex_format = int(mod_156_material_props.vtype, 16)
        skin_function = int(mod_156_material_props.func_skin, 16)
        if vertex_format == 0x1 and skin_function == 0x4:
            has_vertex_buffer_2 = True
            vtx_stride_2 = 8
            VertexBuff2Cls = Mod156.Vertex28
        VertexCls = VERTEX_FORMATS_MAPPER[vertex_format]
        vtx_stride = 32
        # vertex_format = max_bones_per_vertex

    elif dst_mod.header.version in (210, 211, 212):
        custom_properties = bl_mesh.data.albam_custom_properties.get_custom_properties_for_appid(app_id)
        try:
            stored_vertex_format = int(custom_properties.get("vertex_format"))
        except (TypeError, ValueError):
            stored_vertex_format = None
        default_vertex_format = DEFAULT_VERTEX_FORMAT_SKIN if has_bones else DEFAULT_VERTEX_FORMAT_NONSKIN
        vertex_format = stored_vertex_format
        if vertex_format not in VERTEX_FORMATS_MAPPER:
            vertex_format = default_vertex_format
        VertexCls = VERTEX_FORMATS_MAPPER.get(vertex_format)
        vtx_stride = VertexCls().size_

    MAX_BONES = VERTEX_FORMATS_BONE_LIMIT.get(vertex_format, 4)
    # It breaks index serealization without clamping
    if max_bones_per_vertex > MAX_BONES:
        max_bones_per_vertex = MAX_BONES
    weight_half_float = (dst_mod.header.version in (210, 211, 212) and
                         vertex_format not in VERTEX_FORMATS_BRIDGE)
    weights_per_vertex = _process_weights_for_export(
        weights_per_vertex, max_bones_per_vertex=MAX_BONES, half_float=weight_half_float)
    vtx_stream = KaitaiStream(
        BytesIO(bytearray(vtx_stride * vertex_count)))
    if has_vertex_buffer_2:
        vtx_stream_2 = KaitaiStream(
            BytesIO(bytearray(8 * vertex_count)))
    bytes_empty = b'\x00\x00'
    for vertex_index, vertex in enumerate(bl_mesh.data.vertices):
        vertex_struct = VertexCls(_parent=mesh, _root=mesh._root)
        if has_vertex_buffer_2:
            vertex_struct_2 = VertexBuff2Cls(_parent=mesh, _root=mesh._root)
            vertex_struct_2.occlusion = dst_mod.Vec4U1(
                _parent=vertex_struct_2, _root=vertex_struct_2._root)
            vertex_struct_2.tangent = dst_mod.Vec4U1(
                _parent=vertex_struct_2, _root=vertex_struct_2._root)
            vertex_struct_2.occlusion.x = 255
            vertex_struct_2.occlusion.y = 255
            vertex_struct_2.occlusion.z = 255
            vertex_struct_2.occlusion.w = 255

            # Tangents
            t = tangents.get(vertex_index, (0, 0, 0))
            try:
                vertex_struct_2.tangent.x = round(((t[0] * 0.5) + 0.5) * 255)
                vertex_struct_2.tangent.y = round(((t[2] * 0.5) + 0.5) * 255)
                vertex_struct_2.tangent.z = round(((t[1] * -0.5) + 0.5) * 255)
                vertex_struct_2.tangent.w = 254
            except ValueError:
                vertex_struct_2.tangent.x = 0
                vertex_struct_2.tangent.y = 0
                vertex_struct_2.tangent.z = 0
                vertex_struct_2.tangent.w = 254
        # Position types
        if has_bones:
            if MAX_BONES == 1:
                vertex_struct.position = dst_mod.Vec3S2(
                    _parent=vertex_struct, _root=vertex_struct._root)
            else:
                vertex_struct.position = dst_mod.Vec4S2(
                    _parent=vertex_struct, _root=vertex_struct._root)
        else:
            vertex_struct.position = dst_mod.Vec3(
                _parent=vertex_struct, _root=vertex_struct._root)
        # Normals types
        if dst_mod.header.version == 156 or vertex_format in VERTEX_FORMATS_NORMAL4:
            vertex_struct.normal = dst_mod.Vec4U1(
                _parent=vertex_struct, _root=vertex_struct._root)
        else:
            vertex_struct.normal = dst_mod.Vec3U1(
                _parent=vertex_struct, _root=vertex_struct._root)
            vertex_struct.occlusion = 254
        # Tangets
        if vertex_format in VERTEX_FORMATS_TANGENT:
            vertex_struct.tangent = dst_mod.Vec4U1(
                _parent=vertex_struct, _root=vertex_struct._root)
            # Tangents
            t = tangents.get(vertex_index, (0, 0, 0))
            try:
                vertex_struct.tangent.x = round(((t[0] * 0.5) + 0.5) * 255)
                vertex_struct.tangent.y = round(((t[2] * 0.5) + 0.5) * 255)
                vertex_struct.tangent.z = round(((t[1] * -0.5) + 0.5) * 255)
                vertex_struct.tangent.w = 254
            except ValueError:
                vertex_struct.tangent.x = 0
                vertex_struct.tangent.y = 0
                vertex_struct.tangent.z = 0
                vertex_struct.tangent.w = 254
        # UV
        if vertex_format not in VERTEX_FORMATS_BRIDGE:
            vertex_struct.uv = dst_mod.Vec2HalfFloat(
                _parent=vertex_struct, _root=vertex_struct._root)
            uv_x, uv_y = uvs_per_vertex.get(vertex_index, (0, 0))
            uv_x, uv_y = _normalize_uv(uv_x, uv_y)
            vertex_struct.uv.u = pack('e', uv_x)
            vertex_struct.uv.v = pack('e', uv_y)
        # UV2
        if vertex_format in VERTEX_FORMATS_UV2:
            vertex_struct.uv2 = dst_mod.Vec2HalfFloat(
                _parent=vertex_struct, _root=vertex_struct._root)
            if uvs_per_vertex_2:
                uv_x, uv_y = uvs_per_vertex_2.get(vertex_index, (0, 0))
                uv_x, uv_y = _normalize_uv(uv_x, uv_y)
                vertex_struct.uv2.u = pack('e', uv_x)
                vertex_struct.uv2.v = pack('e', uv_y)
            else:
                vertex_struct.uv2.u = bytes_empty
                vertex_struct.uv2.v = bytes_empty
        # UV3
        if vertex_format in VERTEX_FORMATS_UV3:
            vertex_struct.uv3 = dst_mod.Vec2HalfFloat(
                _parent=vertex_struct, _root=vertex_struct._root)
            if uvs_per_vertex_3:
                uv_x, uv_y = uvs_per_vertex_3.get(vertex_index, (0, 0))
                uv_x, uv_y = _normalize_uv(uv_x, uv_y)
                vertex_struct.uv3.u = pack('e', uv_x)
                vertex_struct.uv3.v = pack('e', uv_y)
            else:
                vertex_struct.uv3.u = bytes_empty
                vertex_struct.uv3.v = bytes_empty
        # UV4
        if vertex_format in VERTEX_FORMATS_UV4:
            vertex_struct.uv4 = dst_mod.Vec2HalfFloat(
                _parent=vertex_struct, _root=vertex_struct._root)
            if uvs_per_vertex_4:
                uv_x, uv_y = uvs_per_vertex_4.get(vertex_index, (0, 0))
                uv_x, uv_y = _normalize_uv(uv_x, uv_y)
                vertex_struct.uv4.u = pack('e', uv_x)
                vertex_struct.uv4.v = pack('e', uv_y)
            else:
                vertex_struct.uv4.u = bytes_empty
                vertex_struct.uv4.v = bytes_empty
        # Vertex colors
        if vertex_format in VERTEX_FORMATS_RGBA:
            vertex_struct.rgba = dst_mod.Vec4U1(_parent=vertex_struct, _root=vertex_struct._root)
            c = color_per_vertex.get(vertex_index, (0, 0, 0, 0))
            vertex_struct.rgba.x = c[0]
            vertex_struct.rgba.y = c[1]
            vertex_struct.rgba.z = c[2]
            vertex_struct.rgba.w = c[3]
        # Vertex Alpha
        if vertex_format in VERTEX_FORMATS_VERTEX_ALPHA:
            vertex_struct.vertex_alpha = 255
        # Set Position
        xyz = (vertex.co[0] * SCALE, vertex.co[1] * SCALE, vertex.co[2] * SCALE)
        xyz = (xyz[0], xyz[2], -xyz[1])  # z-up to y-up
        xyz = _apply_bbox_transforms(
            xyz, dst_mod, bbox_data) if has_bones else xyz
        vertex_struct.position.x = xyz[0]
        vertex_struct.position.y = xyz[1]
        vertex_struct.position.z = xyz[2]
        vertex_struct.position.w = 32767  # might be changed later
        # Set Normals
        norms = normals.get(vertex_index, (0, 0, 0))
        try:
            # from [-1, 1] to [0, 255], and clipping bad blender normals
            vertex_struct.normal.x = max(
                0, min(255, round(((norms[0] * 0.5) + 0.5) * 255)))
            vertex_struct.normal.y = max(
                0, min(255, round(((norms[2] * 0.5) + 0.5) * 255)))
            vertex_struct.normal.z = max(
                0, min(255, round(((norms[1] * -0.5) + 0.5) * 255)))
        except ValueError as err:
            if "cannot convert float NaN to integer" in str(err):
                vertex_struct.normal.x = 0
                vertex_struct.normal.y = 0
                vertex_struct.normal.z = 0
            else:
                raise
        # Set Weights
        if dst_mod.header.version == 156 or vertex_format in VERTEX_FORMATS_NORMAL4:
            vertex_struct.normal.w = 255  # is this occlusion as well?
        if has_bones:
            if not _check_armature(bl_mesh):
                raise AlbamCheckFailure(
                    "The mesh object has no Armature modifier",
                    details=f"Object: {bl_mesh.name}",
                    solution="Please add Armature modifier and set imported skeleton as Object"
                )
            # applying bounding box constraints
            weights_data = weights_per_vertex.get(vertex_index, [])  # bone index , weight value hfloat
            weight_values = [w for _, w in weights_data]
            if not weight_values:
                raise AlbamCheckFailure(
                    "The mesh object has one or more vertices with zero skin weights",
                    details=f"Object: {bl_mesh.name}",
                    solution="Please move a root bone in Pose mode to detect vertices that stand still"
                    " and use weight paint brush to fix them"
                )

            weight_values.extend([0] * (MAX_BONES - len(weight_values)))  # add nulls if less than bone limit
            if mesh_bone_palette:
                bone_indices = [mesh_bone_palette.index(
                    bone_index) for bone_index, _ in weights_data]
            else:
                bone_indices = [bi for bi, _ in weights_data]
            # minmics ingame files pattern if vertex has less than max_bones_per_vertex influences
            bone_indices.extend([bone_indices[0]] * (max_bones_per_vertex - len(bone_indices)))
            # fill other empty bone indices in vertex format range with 0
            bone_indices.extend([0] * (MAX_BONES - len(bone_indices)))
            if vertex_format == 0xdb7da014:  # very strange bridge format
                bone_indices.insert(1, 128)
                bone_indices.insert(3, 128)
            vertex_struct.bone_indices = bone_indices
            if dst_mod.header.version != 156 and vertex_format not in VERTEX_FORMATS_BRIDGE:
                match MAX_BONES:
                    case 2:
                        vertex_struct.bone_indices = [
                            pack('e', bone_indices[0]), pack('e', bone_indices[1])]
                        vertex_struct.position.w = round(weight_values[0] * 32767)
                    case 4:
                        vertex_struct.position.w = round(weight_values[0] * 32767)
                        vertex_struct.weight_values = [0, 0]
                        vertex_struct.weight_values[0] = pack("e", weight_values[1])
                        vertex_struct.weight_values[1] = pack("e", weight_values[2])
                    case 8:
                        vertex_struct.position.w = round(weight_values[0] * 32767)
                        vertex_struct.weight_values = [0, 0, 0, 0]
                        vertex_struct.weight_values[0] = round(weight_values[1] * 255)
                        vertex_struct.weight_values[1] = round(weight_values[2] * 255)
                        vertex_struct.weight_values[2] = round(weight_values[3] * 255)
                        vertex_struct.weight_values[3] = round(weight_values[4] * 255)
                        vertex_struct.weight_values2 = [0, 0]
                        vertex_struct.weight_values2[0] = pack("e", weight_values[5])
                        vertex_struct.weight_values2[1] = pack("e", weight_values[6])
            else:
                vertex_struct.weight_values = weight_values
        if has_vertex_buffer_2:
            vertex_struct_2._check()
            vertex_struct_2._write(vtx_stream_2)
        vertex_struct._check()
        vertex_struct._write(vtx_stream)

    return vtx_stream, vtx_stream_2, vertex_format, vtx_stride, vtx_stride_2, max_bones_per_vertex


def _apply_bbox_transforms(xyz_tuple, dst_mod, bbox_data):
    x, y, z = xyz_tuple

    if dst_mod.header.version == 156:

        x -= dst_mod.bbox_min.x
        x /= (dst_mod.bbox_max.x - dst_mod.bbox_min.x)
        x *= 32767

        y -= dst_mod.bbox_min.y
        y /= (dst_mod.bbox_max.y - dst_mod.bbox_min.y) or 1
        y *= 32767

        z -= dst_mod.bbox_min.z
        z /= (dst_mod.bbox_max.z - dst_mod.bbox_min.z) or 1
        z *= 32767

    elif dst_mod.header.version in (210, 211, 212):
        x -= bbox_data.min_x
        x /= bbox_data.dimension
        x *= 32767

        y -= bbox_data.min_y
        y /= bbox_data.dimension
        y *= 32767

        z -= bbox_data.min_z
        z /= bbox_data.dimension
        z *= 32767

    return (round(x), round(y), round(z))


def _process_weights_for_export(weights_per_vertex, max_bones_per_vertex=4, half_float=False):
    """
    Given a dict `weights_per_vertex` with vertex_indices as keys and
    a list of tuples (bone_index, weight_value), iterate over values
    and process them to make them mtframework friendly:
    1) Limit bone weights: keep only up to `max_bones` elements, discarding the pairs that have the
       lowest inflUENCE. This is actually a limitation in albam for lack of
       understanding on how the engine treats vertices with more than 4 bone influencing it
    2) Normalize weights: make all weights sum up 1
    3) float to byte: convert the (-1.0, 1.0) to (0, 255)
    """
    # TODO: move to mtframework.utils
    new_weights_per_vertex = {}
    limit = max_bones_per_vertex
    for vertex_index, influence_list in weights_per_vertex.items():
        # limit max bones
        if len(influence_list) > limit:
            influence_list = sorted(
                influence_list, key=lambda t: t[1])[-limit:]

        weight_data = {t[0]: t[1] for t in influence_list}
        wd_sorted = {k: v for k, v in sorted(weight_data.items(), key=lambda item: item[1], reverse=True)}
        bone_indices = [bi for bi in wd_sorted.keys()]
        weights = [w for w in wd_sorted.values()]
        # normalize
        total_weight = sum(weights)
        if total_weight:
            weights = [round((w / total_weight), 4) for w in weights]
        if half_float:
            weights = _check_weights(weights, limit)
        else:
            # can't have zero values
            weights = [round(w * 255) or 1 for w in weights]
            # correct precision
            if not weights:
                # XXX vertex_position_2 research, beware
                continue
            excess = sum(weights) - 255
            if excess:
                max_index, _ = max(enumerate(weights), key=lambda p: p[1])
                weights[max_index] -= excess

        new_weights_per_vertex[vertex_index] = list(zip(bone_indices, weights))

    return new_weights_per_vertex


def _calculate_weight_bounds(bl_obj, bl_mesh, dst_mod, meshes_data):
    unsorted_weight_bounds = []
    if bl_obj.type != "ARMATURE":
        weight_bound = _set_static_mesh_weight_bounds(
            dst_mod, bl_mesh, meshes_data)
        unsorted_weight_bounds.append(weight_bound)
    else:
        mesh_vertex_groups = get_mesh_vertex_groups(bl_mesh)
        for vg in bl_mesh.vertex_groups:
            weight_bound = _calculate_vertex_group_weight_bound(
                mesh_vertex_groups, bl_obj, vg, dst_mod, meshes_data
            )
            if weight_bound:
                unsorted_weight_bounds.append(weight_bound)
    return sorted(unsorted_weight_bounds, key=lambda x: x.bone_id)


def _set_static_mesh_weight_bounds(dst_mod, bl_mesh_ob, meshes_data):
    bl_mesh = bl_mesh_ob.data
    wb = dst_mod.WeightBound(_parent=meshes_data, _root=meshes_data._root)
    bsphere = dst_mod.Vec4(_parent=wb, _root=wb._root)

    bbox_min = dst_mod.Vec4(_parent=wb, _root=wb._root)
    min_x = min((v.co[0] for v in bl_mesh.vertices))
    min_y = min((v.co[1] for v in bl_mesh.vertices))
    min_z = min((v.co[2] for v in bl_mesh.vertices))
    bbox_min.w = 0

    bbox_max = dst_mod.Vec4(_parent=wb, _root=wb._root)
    max_x = max((v.co[0] for v in bl_mesh.vertices))
    max_y = max((v.co[1] for v in bl_mesh.vertices))
    max_z = max((v.co[2] for v in bl_mesh.vertices))

    length_x = (max_x - min_x) / 2
    length_y = (max_y - min_y) / 2
    length_z = (max_z - min_z) / 2

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    center = (center_x, center_y, center_z)
    radius = max(map(lambda vertex: get_dist(
        center, vertex.co[:]), bl_mesh.vertices))
    bsphere_export = (center_x * 100, center_z * 100, -
                      center_y * 100, radius * 100)

    bsphere.x = center_x * 100
    bsphere.y = center_z * 100
    bsphere.z = -center_y * 100
    bsphere.w = radius * 100

    # bbox_min_export = (min_x * 100, min_z * 100, -max_y * 100, 0.0)
    bbox_min.x = min_x * 100
    bbox_min.y = min_z * 100
    bbox_min.z = -max_y * 100
    bbox_min.w = 0.0

    # bbox_max_export = (max_x * 100, max_z * 100, -min_y * 100, 0.0)
    bbox_max.x = max_x * 100
    bbox_max.y = max_z * 100
    bbox_max.z = -min_y * 100
    bbox_max.w = 0.0

    oabb = dst_mod.Matrix4x4(_parent=wb, _root=wb._root)
    oabb.row_1 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_2 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_3 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_4 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_1.x = 1
    oabb.row_1.y = 0
    oabb.row_1.z = 0
    oabb.row_1.w = 0
    oabb.row_2.x = 0
    oabb.row_2.y = 1
    oabb.row_2.z = 0
    oabb.row_2.w = 0
    oabb.row_3.x = 0
    oabb.row_3.y = 0
    oabb.row_3.z = 1
    oabb.row_3.w = 0
    # TODO: dimension/length is wrongly calculated in vertex groups?
    oabb.row_4.x = bsphere_export[0]
    oabb.row_4.y = bsphere_export[1]
    oabb.row_4.z = bsphere_export[2]
    oabb.row_4.w = 1

    oabb_dimension = dst_mod.Vec4(_parent=wb, _root=wb._root)
    # TODO: dimension/length is wrongly calculated in vertex groups?
    oabb_dimension.x = length_x * 100
    oabb_dimension.y = length_z * 100
    oabb_dimension.z = length_y * 100
    oabb_dimension.w = 0

    unk_01 = dst_mod.Vec3(_parent=wb, _root=wb._root)
    unk_01.x = 0.0
    unk_01.y = 0.0
    unk_01.z = 0.0

    wb.bone_id = 255  # since it's static
    wb.unk_01 = unk_01
    wb.bsphere = bsphere
    wb.bbox_min = bbox_min
    wb.bbox_max = bbox_max
    wb.oabb = oabb
    wb.oabb_dimension = oabb_dimension

    wb._check()
    return wb


def _calculate_vertex_group_weight_bound(mesh_vertex_groups, armature, vertex_group, dst_mod, meshes_data):
    vertices_in_group = mesh_vertex_groups.get(vertex_group.index)
    if not vertices_in_group:
        return

    bone_index = armature.pose.bones.find(vertex_group.name)
    pose_bone = armature.pose.bones[bone_index]
    pose_bone_matrix = Matrix.Translation(pose_bone.head).inverted()

    vertices_in_group_bone_space = [
        pose_bone_matrix @ v.co for v in vertices_in_group]

    min_x = min((v[0] for v in vertices_in_group_bone_space))
    min_y = min((v[1] for v in vertices_in_group_bone_space))
    min_z = min((v[2] for v in vertices_in_group_bone_space))
    max_x = max((v[0] for v in vertices_in_group_bone_space))
    max_y = max((v[1] for v in vertices_in_group_bone_space))
    max_z = max((v[2] for v in vertices_in_group_bone_space))

    length_x = (max_x - min_x) / 2
    length_y = (max_y - min_y) / 2
    length_z = (max_z - min_z) / 2

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    center = (center_x, center_y, center_z)
    radius = max(map(lambda vertex: get_dist(
        center, vertex[:]), vertices_in_group_bone_space))
    bsphere_export = (center_x * 100, center_z * 100, -
                      center_y * 100, radius * 100)

    bbox_min_export = (min_x * 100, min_z * 100, -max_y * 100, 0.0)
    bbox_max_export = (max_x * 100, max_z * 100, -min_y * 100, 0.0)

    # TODO: calculate oabb
    # I spotted disappearing meshes (e.g. hands) in some cut-scenes (re5-> "The Wetlands")
    # References:
    # - https://github.com/patmo141/object_bounding_box
    # - https://github.com/AsteriskAmpersand/Mod3-MHW-Importer/tree/master/boundingbox
    # thanks to AsteriskAmpersand for math help
    oabb_export = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        bsphere_export[0], bsphere_export[1], bsphere_export[2], 1
    ]

    oabb_dimension_export = (
        length_x * 100, length_z * 100, length_y * 100, 0.0)

    wb = dst_mod.WeightBound(_parent=meshes_data, _root=meshes_data._root)

    bsphere = dst_mod.Vec4(_parent=wb, _root=wb._root)
    bsphere.x = bsphere_export[0]
    bsphere.y = bsphere_export[1]
    bsphere.z = bsphere_export[2]
    bsphere.w = bsphere_export[3]

    bbox_min = dst_mod.Vec4(_parent=wb, _root=wb._root)
    bbox_min.x = bbox_min_export[0]
    bbox_min.y = bbox_min_export[1]
    bbox_min.z = bbox_min_export[2]
    bbox_min.w = bbox_min_export[3]

    bbox_max = dst_mod.Vec4(_parent=wb, _root=wb._root)
    bbox_max.x = bbox_max_export[0]
    bbox_max.y = bbox_max_export[1]
    bbox_max.z = bbox_max_export[2]
    bbox_max.w = bbox_max_export[3]

    oabb = dst_mod.Matrix4x4(_parent=wb, _root=wb._root)
    oabb.row_1 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_2 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_3 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_4 = dst_mod.Vec4(_parent=oabb, _root=oabb._root)
    oabb.row_1.x = oabb_export[0]
    oabb.row_1.y = oabb_export[1]
    oabb.row_1.z = oabb_export[2]
    oabb.row_1.w = oabb_export[3]
    oabb.row_2.x = oabb_export[4]
    oabb.row_2.y = oabb_export[5]
    oabb.row_2.z = oabb_export[6]
    oabb.row_2.w = oabb_export[7]
    oabb.row_3.x = oabb_export[8]
    oabb.row_3.y = oabb_export[9]
    oabb.row_3.z = oabb_export[10]
    oabb.row_3.w = oabb_export[11]
    oabb.row_4.x = oabb_export[12]
    oabb.row_4.y = oabb_export[13]
    oabb.row_4.z = oabb_export[14]
    oabb.row_4.w = oabb_export[15]

    oabb_dimension = dst_mod.Vec4(_parent=wb, _root=wb._root)
    oabb_dimension.x = oabb_dimension_export[0]
    oabb_dimension.y = oabb_dimension_export[1]
    oabb_dimension.z = oabb_dimension_export[2]
    oabb_dimension.w = 0.0

    unk_01 = dst_mod.Vec3(_parent=wb, _root=wb._root)
    unk_01.x = 0.0
    unk_01.y = 0.0
    unk_01.z = 0.0

    wb.bone_id = bone_index
    wb.unk_01 = unk_01
    wb.bsphere = bsphere
    wb.bbox_min = bbox_min
    wb.bbox_max = bbox_max
    wb.oabb = oabb
    wb.oabb_dimension = oabb_dimension

    wb._check()
    return wb


@blender_registry.register_custom_properties_mesh("mod_156_mesh", ("re5",))
@blender_registry.register_blender_prop
class Mod156MeshCustomProperties(bpy.types.PropertyGroup):
    vdecl_enum = bpy.props.EnumProperty(
        name="",
        description="",
        items=[
            ("0x0", "VDECL_SKIN", "", 1),
            ("0x1", "VDECL_NONSKIN", "", 2),
            ("0x2", "VDECL_SKINEX", "", 3),
            ("0x3", "VDECL_FILTER", "", 4),
            ("0x4", "VDECL_FILTER2", "", 5),
            ("0x5", "VDECL_SKIN_BASE", "", 6),
            ("0x6", "VDECL_NONSKIN_BASE", "", 7),
            ("0x7", "VDECL_SKINEX_BASE", "", 8),
            ("0x8", "VDECL_NONSKIN_COL", "", 9),
            ("0x9", "VDECL_NONSKIN_COLEX", "", 10),
            ("0xa", "VDECL_SHAPE_BASE", "", 11),
            ("0xb", "VDECL_SHAPE", "", 12),
            ("0xc", "VDECL_SKIN_COL", "", 13),
            ("0xd", "VDECL_MATERIAL", "", 14),
            ("0xe", "VDECL_SKINSO", "", 15),
            ("0xf", "VDECL_I2GLINE", "", 16),
            ("0x10", "VDECL_NUM", "", 17),
        ],
        default="0x0",
        options=set()
    )
    level_of_detail: bpy.props.IntProperty(name="Level of Detail", default=255, options=set())  # noqa: F821
    idx_group: bpy.props.IntProperty(name="Group ID", default=0, options=set())  # noqa: F821
    alpha_priority: bpy.props.IntProperty(name="Alpha Transparency Priority",
                                          default=0, options=set())  # noqa: F821
    disp: bpy.props.BoolProperty(name="Display Mesh in Game", default=1, options=set())  # noqa: F821
    shape: bpy.props.BoolProperty(name="Shape", default=0, options=set())   # noqa: F821
    reserved2_flag_1: bpy.props.BoolProperty(name="Reserved 1", default=0, options=set())  # noqa: F821
    reserved2_flag_2: bpy.props.BoolProperty(name="Reserved 2", default=0, options=set())  # noqa: F821
    env: bpy.props.BoolProperty(name="Environment", default=1, options=set())  # noqa: F821
    refrect: bpy.props.BoolProperty(name="Reflect", default=1, options=set())  # noqa: F821
    shadow_cast: bpy.props.BoolProperty(name="Cast Shadow", default=1, options=set())  # noqa: F821
    shadow_receive: bpy.props.BoolProperty(name="Receive Shadow", default=1, options=set())  # noqa: F821
    sort: bpy.props.BoolProperty(name="Sorting", default=0, options=set())  # noqa: F821
    vdeclbase: vdecl_enum
    vdecl: vdecl_enum
    rcn_base: bpy.props.IntProperty(name="RCN Base", default=0, options=set())  # noqa: F821
    boundary: bpy.props.IntProperty(name="Boundary", default=0, options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            if type(getattr(self, attr_name)) is str:
                setattr(dst_obj, attr_name, int(getattr(self, attr_name), 16))
            else:
                setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except TypeError:
                setattr(self, attr_name, hex(getattr(src_obj, attr_name)))


@blender_registry.register_custom_properties_mesh("mod_21_mesh", ("re0", "re1", "re6", "rev1", "rev2", "dd",))
@blender_registry.register_blender_prop
class Mod21MeshCustomProperties(bpy.types.PropertyGroup):
    level_of_detail: bpy.props.IntProperty(name="Level of Detail", default=255, options=set())  # noqa: F821
    draw_mode: bpy.props.IntProperty(name="Draw Mode", default=0, options=set())  # noqa: F821  TODO: b12
    idx_group: bpy.props.IntProperty(name="Group ID", default=0, options=set())  # noqa: F821
    disp: bpy.props.BoolProperty(name="Display Mesh in Game", default=1, options=set())  # noqa: F821
    shape: bpy.props.BoolProperty(name="Shape", default=0, options=set())  # noqa: F821
    sort: bpy.props.BoolProperty(name="Sorting", default=0, options=set())  # noqa: F821
    alpha_priority: bpy.props.IntProperty(name="Alpha Transparency Priority",  # noqa: F821
                                          default=0, options=set())  # TODO b8
    topology: bpy.props.IntProperty(name="Topology", default=0, options=set())  # noqa: F821  TODO b6
    binormal_flip: bpy.props.BoolProperty(name="Binormal Flip", default=0, options=set())  # noqa: F821
    bridge: bpy.props.BoolProperty(name="Bridge Geometry", default=0, options=set())  # noqa: F821
    bone_id_start: bpy.props.IntProperty(name="Bone ID Start", default=0, options=set())  # noqa: F821
    connect_id: bpy.props.IntProperty(name="Connect ID", default=0, options=set())  # noqa: F821
    boundary: bpy.props.IntProperty(name="Boundary", default=0, options=set())  # noqa: F821
    vertex_format: bpy.props.StringProperty(name="Vertex Format", options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except TypeError:
                pass
                # print(f"Type mismatch {attr_name}, {src_obj}")
