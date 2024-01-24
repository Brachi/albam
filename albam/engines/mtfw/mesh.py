from binascii import crc32
from collections import namedtuple, OrderedDict
import ctypes
from itertools import chain
from io import BytesIO
from struct import pack, unpack
try:
    from math import dist as get_dist
except ImportError:
    from albam.lib.blender import get_dist

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix
import numpy as np

from albam.lib.blender import (
    get_bone_indices_and_weights_per_vertex,
    get_model_bounding_box,
    get_model_bounding_sphere,
    get_normals_per_vertex,
    get_tangents_per_vertex,
    get_uvs_per_vertex,
    strip_triangles_to_triangles_list,
    triangles_list_to_triangles_strip,
)
from albam.lib.misc import chunks
from albam.registry import blender_registry
from albam.vfs import VirtualFile
from .material import build_blender_materials, serialize_materials_data
from .structs.mod_156 import Mod156
from .structs.mod_21 import Mod21


MOD_CLASS_MAPPER = {
    156: Mod156,
    210: Mod21,
    211: Mod21,
}
APPID_CLASS_MAPPER = {
    "re1": Mod21,
    "re5": Mod156,
    "rev2": Mod21,
}

VERTEX_FORMATS_MAPPER = {
    0: Mod156.Vertex0,
    1: Mod156.Vertex,
    2: Mod156.Vertex,
    3: Mod156.Vertex,
    4: Mod156.Vertex,
    5: Mod156.Vertex5,
    6: Mod156.Vertex5,
    7: Mod156.Vertex5,
    8: Mod156.Vertex5,
}

VERTEX_FORMATS_RGBA = (
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

VERTEX_FORMATS_TANGENT = (
    0,
    1,
    2,
    3,
    4,
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
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
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
    0,
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

BBOX_AFFECTED = [
    0x667B1019,
    0xCBF6C01A,
    0xB0983013,
    0xA8FAB018,
    0xD877801B,
]

VERSIONS_USE_BONE_PALETTES = {156}
VERSIONS_BONES_BBOX_AFFECTED = {210, 211}
VERSIONS_USE_TRISTRIPS = {156}


@blender_registry.register_import_function(app_id="re1", extension="mod")
@blender_registry.register_import_function(app_id="re5", extension="mod")
@blender_registry.register_import_function(app_id="rev2", extension="mod")
def build_blender_model(file_list_item, context):
    LODS_TO_IMPORT = (1, 255)

    app_id = file_list_item.app_id
    mod_bytes = file_list_item.get_bytes()
    mod_version = mod_bytes[4]
    assert mod_version in MOD_CLASS_MAPPER, f"Unsupported version: {mod_version}"
    ModCls = MOD_CLASS_MAPPER[mod_version]
    mod = ModCls.from_bytes(mod_bytes)
    mod._read()

    bl_object_name = file_list_item.display_name
    bbox_data = _create_bbox_data(mod)
    skeleton = None if mod.header.num_bones == 0 else build_blender_armature(mod, bl_object_name, bbox_data)
    bl_object = skeleton or bpy.data.objects.new(bl_object_name, None)
    materials = build_blender_materials(file_list_item, context, mod, bl_object_name)

    for i, mesh in enumerate(m for m in mod.meshes_data.meshes if m.level_of_detail in LODS_TO_IMPORT):
        try:
            name = f"{bl_object_name}_{str(i).zfill(4)}"
            material_hash = _get_material_hash(mod, mesh)
            use_156rgba = False
            if mod_version == 156:
                if not skeleton:
                    if materials.get(material_hash):
                        use_156rgba = materials[material_hash].albam_custom_properties.mod_156_material.use_8_bones

            bl_mesh_ob = build_blender_mesh(
                app_id, mod, mesh, name, bbox_data, mod_version in VERSIONS_USE_TRISTRIPS, use_156rgba
            )
            bl_mesh_ob.parent = bl_object
            if skeleton:
                modifier = bl_mesh_ob.modifiers.new(type="ARMATURE", name="armature")
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


def build_blender_mesh(app_id, mod, mesh, name, bbox_data, use_tri_strips=False, use_156rgba=False):
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
        _process_vertex_colors(mod.header.version, vertex, vertex_colors, use_156rgba)
        _process_weights(mod, mesh, vertex, vertex_index, weights_per_bone)

    indices = strip_triangles_to_triangles_list(mesh.indices) if use_tri_strips else mesh.indices
    # convert indices for this mesh only, so they start at zero
    indices = [tri_idx - mesh.vertex_position for tri_idx in indices]
    assert min(indices) >= 0, "Bad face indices"  # Blender crashes with corrrupt indices
    assert locations, "No vertices could be processed"  # Blender crashes with an empty sequence

    me_ob.from_pydata(locations, [], chunks(indices, 3))

    _build_normals(me_ob, normals)
    _build_uvs(me_ob, uvs_1, "uv1")
    _build_uvs(me_ob, uvs_2, "uv2")
    _build_uvs(me_ob, uvs_3, "uv3")
    _build_uvs(me_ob, uvs_4, "uv4")
    _build_vertex_colors(me_ob, vertex_colors, "vc")
    _build_weights(ob, weights_per_bone)

    custom_properties = me_ob.albam_custom_properties.get_appid_custom_properties(app_id)
    custom_properties.set_from_source(mesh)
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

    elif (w is not None and mod_version == 210) or (
            mod_version == 210 and mesh.vertex_format in BBOX_AFFECTED):
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


def _process_vertex_colors(mod_version, vertex, rgba_out, use_156rgba):
    if mod_version == 210 and hasattr(vertex, "rgba"):
        b = vertex.rgba.x / 225
        g = vertex.rgba.y / 225
        r = vertex.rgba.z / 255
        a = vertex.rgba.w / 255
        rgba_out.append((r, g, b, a))
    elif use_156rgba:
        r = (unpack("H", vertex.uv3.u)[0] & 0xFF) / 255
        g = (unpack("H", vertex.uv3.u)[0] >> 8 & 0xFF) / 255
        b = (unpack("H", vertex.uv3.v)[0] & 0xFF) / 255
        a = (unpack("H", vertex.uv3.u)[0] >> 8 & 0xFF) / 255
        rgba_out.append((r, g, b, a))
    else:
        return


def _process_weights(mod, mesh, vertex, vertex_index, weights_per_bone):
    if not hasattr(vertex, "bone_indices"):
        return

    bone_indices = _get_bone_indices(mod, mesh, vertex.bone_indices)
    weights = _get_weights(mod, mesh, vertex)

    # TODO: verify in parsing tests that bone_index = 0 is never taken into account
    for bi, bone_index in enumerate(bone_indices):
        if bone_index == 0 and (
            (mesh.vertex_format not in (0xC31F201C,) and mod.header.num_bones != 1)
        ):  # no root bone, 0 is acceptable
            continue
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
                    real_bone_index = mod.bones_data.bone_palettes[mesh.idx_bone_palette].indices[bone_index]
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
        w4 = 1.0 - w1 - w2 - w3
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
        print(f"Can't get weights for vertex_format '{hex(mesh.vertex_format)}'")
        return (0, 0, 0, 0)


def _build_normals(bl_mesh, normals):
    if not normals:
        return
    bl_mesh.create_normals_split()
    bl_mesh.validate(clean_customdata=False)
    bl_mesh.update(calc_edges=True)
    bl_mesh.polygons.foreach_set("use_smooth", [True] * len(bl_mesh.polygons))

    vert_normals = np.array(normals, dtype=np.float32)
    norms = np.linalg.norm(vert_normals, axis=1, keepdims=True)
    np.divide(vert_normals, norms, out=vert_normals, where=norms != 0)

    bl_mesh.normals_split_custom_set_from_vertices(vert_normals)
    bl_mesh.use_auto_smooth = True


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
        head = _name_me(mod, m, bbox_data)
        blender_bone.head = [head[0] * scale, -head[2] * scale, head[1] * scale]
        blender_bone.tail = [head[0] * scale, -head[2] * scale, (head[1] * scale) + 0.01]
        blender_bone['mtfw.anim_retarget'] = str(bone.idx_anim_map)
        blender_bones.append(blender_bone)

    bpy.ops.object.mode_set(mode="OBJECT")
    return armature_ob


def _name_me(mod, matrix, bbox_data):
    m = matrix
    if mod.header.version == 210:
        row_1_x = round(m.row_1.x - bbox_data.dimension + 1, 1)
        row_2_y = round(m.row_2.y - bbox_data.dimension + 1, 1)
        row_3_z = round(m.row_3.z - bbox_data.dimension + 1, 1)
        row_4_x = m.row_4.x - bbox_data.min_x
        row_4_y = m.row_4.y - bbox_data.min_y
        row_4_z = m.row_4.z - bbox_data.min_z

    elif mod.header.version == 156:
        row_1_x = m.row_1.x
        row_2_y = m.row_2.y
        row_3_z = m.row_3.z
        row_4_x = m.row_4.x
        row_4_y = m.row_4.y
        row_4_z = m.row_4.z

    head_vector = (
        Matrix(
            (
                (row_1_x, m.row_1.y, m.row_1.z, m.row_1.w),
                (m.row_2.x, row_2_y, m.row_2.z, m.row_2.w),
                (m.row_3.x, m.row_3.y, row_3_z, m.row_3.w),
                (row_4_x, row_4_y, row_4_z, m.row_4.w),
            )
        )
        .inverted()
        .transposed()
        .to_translation()
    )

    return head_vector


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
    max_length = max(abs(mod.bbox_max.x), abs(mod.bbox_max.y), abs(mod.bbox_max.z))
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
    elif mod.header.version == 210:
        material_name = mod.materials_data.material_names[mesh.idx_material // 16]
        material_hash = crc32(material_name.encode()) ^ 0xFFFFFFFF
    elif mod.header.version == 211:
        material_hash = mod.materials_data.material_hashes[mesh.idx_material // 16]
    return material_hash


@blender_registry.register_export_function(app_id="re1", extension="mod")
@blender_registry.register_export_function(app_id="re5", extension="mod")
@blender_registry.register_export_function(app_id="rev2", extension="mod")
def export_mod(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    Mod = APPID_CLASS_MAPPER[app_id]
    vfiles = []

    src_mod = Mod.from_bytes(asset.original_bytes)
    src_mod._read()
    dst_mod = Mod()
    # TODO: export options like visibility
    bl_meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]

    _serialize_top_level_mod(bl_meshes, src_mod, dst_mod)
    _init_mod_header(bl_obj, src_mod, dst_mod)

    bone_palettes = _create_bone_palettes(src_mod, bl_obj, bl_meshes)
    dst_mod.bones_data = _serialize_bones_data(bl_obj, bl_meshes, src_mod, dst_mod, bone_palettes)
    dst_mod.groups = _serialize_groups(src_mod, dst_mod)
    materials_map, mrl, vtextures = serialize_materials_data(asset, bl_meshes, src_mod, dst_mod)

    meshes_data, vertex_buffer, index_buffer = (
        _serialize_meshes_data(bl_obj, bl_meshes, src_mod, dst_mod, materials_map, bone_palettes))
    dst_mod.header.num_vertices = sum(m.num_vertices for m in meshes_data.meshes)
    dst_mod.meshes_data = meshes_data
    dst_mod.vertex_buffer = vertex_buffer
    dst_mod.index_buffer = index_buffer

    offset = dst_mod.size_top_level_
    dst_mod.header.offset_bones_data = offset
    dst_mod.header.offset_groups = offset + dst_mod.bones_data_size_
    dst_mod.header.offset_materials_data = dst_mod.header.offset_groups + dst_mod.groups_size_
    dst_mod.header.offset_meshes_data = dst_mod.header.offset_materials_data + dst_mod.materials_data.size_
    dst_mod.header.offset_vertex_buffer = dst_mod.header.offset_meshes_data + dst_mod.meshes_data.size_
    dst_mod.header.offset_index_buffer = dst_mod.header.offset_vertex_buffer + len(vertex_buffer)

    dst_mod.header.size_vertex_buffer = len(vertex_buffer)
    dst_mod.header.num_faces = (len(index_buffer) // 2) + 1  # TODO: revise, name accordingly
    index_buffer.extend((0, 0))

    final_size = sum((
        offset,
        dst_mod.bones_data_size_,
        dst_mod.groups_size_,
        dst_mod.materials_data.size_,
        dst_mod.meshes_data.size_,
        dst_mod.header.size_vertex_buffer,
        len(index_buffer) + 4,
    ))

    dst_mod.header.size_file = final_size
    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_mod._check()

    dst_mod.vertex_buffer_2__to_write = False
    dst_mod._write(stream)

    mod_vf = VirtualFile(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
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
    if dst_mod_header.version in (210, 211):
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

    dst_mod.unk_01 = src_mod.unk_01
    dst_mod.unk_02 = src_mod.unk_02
    dst_mod.unk_03 = src_mod.unk_03
    dst_mod.unk_04 = src_mod.unk_04

    if src_mod.header.version == 156:
        dst_mod.unk_05 = src_mod.unk_05
        dst_mod.unk_06 = src_mod.unk_06
        dst_mod.unk_07 = src_mod.unk_07
        dst_mod.unk_08 = src_mod.unk_08
        dst_mod.reserved_01 = 0
        dst_mod.reserved_02 = 0
        dst_mod.reserved_03 = 0
        dst_mod.num_vtx8_unk_faces = 0
        dst_mod.num_vtx8_unk_uv = 0
        dst_mod.num_vtx8_unk_normals = 0
        dst_mod.vtx8_unk_faces = []
        dst_mod.vtx8_unk_uv = []
        dst_mod.vtx8_unk_normals = []

    if src_mod.header.version == 210:
        dst_mod.num_weight_bounds = 0


def _serialize_bones_data(bl_obj, bl_meshes, src_mod, dst_mod, bone_palettes=None):
    if bl_obj.type != "ARMATURE":
        return
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
            bone_palette = dst_mod.BonePalette(_parent=bones_data, _root=bones_data._root)
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
        bone.parent_distance = src_bone.parent_distance
        loc = dst_mod.Vec3(_parent=bone, _root=bone._root)
        loc.x = src_bone.location.x
        loc.y = src_bone.location.y
        loc.z = src_bone.location.z
        bone.location = loc

        # TODO: be concise with struct (e.g. array of floats)
        m = dst_mod.Matrix4x4(_parent=bones_data, _root=bones_data._root)
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
        src_m2 = src_mod.bones_data.inverse_bind_matrices[i]
        m2.row_1 = dst_mod.Vec4(_parent=m2, _root=m._root)
        m2.row_2 = dst_mod.Vec4(_parent=m2, _root=m._root)
        m2.row_3 = dst_mod.Vec4(_parent=m2, _root=m._root)
        m2.row_4 = dst_mod.Vec4(_parent=m2, _root=m._root)

        if dst_mod.header.version in VERSIONS_BONES_BBOX_AFFECTED:
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
            m2.row_1.x = src_m2.row_1.x
            m2.row_2.y = src_m2.row_2.y
            m2.row_3.z = src_m2.row_3.z
            m2.row_4.x = src_m2.row_4.x
            m2.row_4.y = src_m2.row_4.y
            m2.row_4.z = src_m2.row_4.z

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
    except:
        return colors
    mesh_loops = {li: loop.vertex_index for li, loop in enumerate(mesh.loops)}
    vtx_colors = {mesh_loops[li]: data.color for li, data in color_layer.data.items()}
    for idx, color in vtx_colors.items():
        b = round(color[0]*255)
        g = round(color[1]*255)
        r = round(color[2]*255)
        a = round(color[3]*255)
        colors[idx] = (r, g, b, a)
    return colors


def _create_bone_palettes(src_mod, bl_armature, bl_meshes):
    if src_mod.header.version != 156:
        return {}
    bone_palette_dicts = []
    MAX_BONE_PALETTE_SIZE = 32

    bone_palette = {'mesh_indices': set(), 'bone_indices': set()}
    for i, mesh in enumerate(bl_meshes):
        vertex_group_mapping = {vg.index: bl_armature.pose.bones.find(vg.name) for vg in mesh.vertex_groups}
        vertex_group_mapping = {k: v for k, v in vertex_group_mapping.items() if v != -1}
        try:
            bone_indices = (
                {vertex_group_mapping[vgroup.group]
                 for vertex in mesh.data.vertices
                 for vgroup in vertex.groups}
            )
        except Exception:
            print("Can't find vertex group in the armature")

        msg = "Mesh {} is influenced by more than 32 bones, which is not supported".format(mesh.name)
        assert len(bone_indices) <= MAX_BONE_PALETTE_SIZE, msg

        current = bone_palette['bone_indices']
        potential = current.union(bone_indices)
        if len(potential) > MAX_BONE_PALETTE_SIZE:
            bone_palette_dicts.append(bone_palette)
            bone_palette = {'mesh_indices': {i}, 'bone_indices': set(bone_indices)}
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
        g.unk_02 = src_group.unk_02
        g.unk_03 = src_group.unk_03
        g.unk_04 = src_group.unk_04
        g.unk_05 = src_group.unk_05
        g.unk_06 = src_group.unk_06
        g.unk_07 = src_group.unk_07
        g.unk_08 = src_group.unk_08

        groups.append(g)
    return groups


def _serialize_meshes_data(bl_obj, bl_meshes, src_mod, dst_mod, materials_map, bone_palettes=None):
    app_id = bl_obj.albam_asset.app_id
    dst_mod.header.num_meshes = len(bl_meshes)
    meshes_data = dst_mod.MeshesData(_parent=dst_mod, _root=dst_mod._root)
    meshes_data.meshes = []
    meshes_data.weight_bounds = []

    vertex_buffer = bytearray()
    index_buffer = bytearray()
    bbox_data = _create_bbox_data(dst_mod)
    use_strips = dst_mod.header.version == 156
    is_skeletal = dst_mod.header.num_bones > 0

    current_vertex_position = 0
    current_vertex_offset = 0
    vertex_offset_accumulated = 0
    current_vertex_format = None
    total_num_vertices = 0

    face_position = 0
    face_offset = 0  # unused for now

    for mesh_index, bl_mesh in enumerate(bl_meshes):
        mesh = dst_mod.Mesh(_parent=meshes_data, _root=meshes_data._root)
        mesh.indices__to_write = False
        mesh.vertices__to_write = False
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
                raise ValueError(f"Mesh {mesh_index} doesn't have a bone_palette")

        vertices, vertex_format, vertex_stride = (
            _export_vertices(app_id, bl_mesh, mesh, mesh_bone_palette, dst_mod, bbox_data)
        )
        vertex_buffer.extend(vertices.to_byte_array())
        if vertex_format != current_vertex_format:
            current_vertex_offset = vertex_offset_accumulated
            current_vertex_position = 0
            current_vertex_format = vertex_format

        if use_strips:
            triangles = triangles_list_to_triangles_strip(bl_mesh)
        else:
            triangles = list(chain.from_iterable(p.vertices for p in bl_mesh.data.polygons))

        triangles = [e + current_vertex_position for e in triangles]
        triangles_ctypes = (ctypes.c_ushort * len(triangles))(*triangles)
        index_buffer.extend(triangles_ctypes)
        num_vertices = len(bl_mesh.data.vertices)
        num_indices = len(triangles)

        # Beware of vertex_format being a string type, overriden below
        custom_properties = bl_mesh.data.albam_custom_properties.get_appid_custom_properties(app_id)
        custom_properties.set_to_dest(mesh)

        mesh.idx_material = materials_map[bl_mesh.data.materials[0].name]  # TODO: pre-check for no materials
        mesh.constant = 1
        mesh.vertex_format = vertex_format
        mesh.vertex_stride = vertex_stride
        mesh.vertex_stride_2 = 0
        mesh.num_vertices = num_vertices  # assert num_vertices == len(vertices_array) // 32
        mesh.vertex_position_end = current_vertex_position + mesh.num_vertices - 1  # XXX only a short!
        mesh.vertex_position_2 = current_vertex_position
        mesh.vertex_offset = current_vertex_offset
        mesh.face_position = face_position
        mesh.num_indices = num_indices
        mesh.face_offset = face_offset
        mesh.vertex_position = current_vertex_position
        mesh.idx_bone_palette = mesh_bone_palette_index
        mesh.num_unique_bone_ids = len(bl_mesh.vertex_groups) if is_skeletal else 1

        if dst_mod.header.version in (156,):
            mesh.unk_03 = 0

        mesh._check()
        meshes_data.meshes.append(mesh)
        mesh_weight_bounds = _calculate_weight_bounds(bl_obj, bl_mesh, dst_mod, meshes_data)
        meshes_data.weight_bounds.extend(mesh_weight_bounds)

        current_vertex_position += num_vertices
        vertex_offset_accumulated += (num_vertices * vertex_stride)
        face_position += num_indices
        total_num_vertices += mesh.num_vertices

    if dst_mod.header.version != 210:
        meshes_data.num_weight_bounds = len(meshes_data.weight_bounds)
    else:
        dst_mod.num_weight_bounds = len(meshes_data.weight_bounds)

    meshes_data._check()
    return meshes_data, vertex_buffer, index_buffer


def _export_vertices(app_id, bl_mesh, mesh, mesh_bone_palette, dst_mod, bbox_data):
    SCALE = 100
    VERTEX_FORMAT_DEFAULT = 0x14d40020
    VERTEX_FORMAT_HANDS = 0xc31f201c
    uvs_per_vertex = get_uvs_per_vertex(bl_mesh, 0)
    uvs_per_vertex_2 = get_uvs_per_vertex(bl_mesh, 1)
    uvs_per_vertex_3 = get_uvs_per_vertex(bl_mesh, 2)
    uvs_per_vertex_4 = get_uvs_per_vertex(bl_mesh, 3)
    color_per_vertex = {}
    weights_per_vertex = get_bone_indices_and_weights_per_vertex(bl_mesh)
    weight_half_float = dst_mod.header.version == 210
    weights_per_vertex = _process_weights_for_export(weights_per_vertex, half_float=weight_half_float)
    max_bones_per_vertex = max({len(data) for data in weights_per_vertex.values()}, default=0)
    normals = get_normals_per_vertex(bl_mesh.data)
    tangents = get_tangents_per_vertex(bl_mesh.data)
    has_bones = bool(dst_mod.header.num_bones)
    use_special_vf = False

    vertex_count = len(bl_mesh.data.vertices)
    if dst_mod.header.version == 156:
        VertexCls = VERTEX_FORMATS_MAPPER[max_bones_per_vertex]
        vertex_size = 32
        vertex_format = max_bones_per_vertex
        use_special_vf = bl_mesh.material_slots[0].material.albam_custom_properties.mod_156_material.use_8_bones
        if not has_bones and use_special_vf:
            color_per_vertex = _get_vertex_colors(bl_mesh)
    elif dst_mod.header.version == 210:
        custom_properties = bl_mesh.data.albam_custom_properties.get_appid_custom_properties(app_id)
        try:
            stored_vertex_format = int(custom_properties.get("vertex_format"))
        except (TypeError, ValueError):
            stored_vertex_format = None
        if has_bones:
            if stored_vertex_format == VERTEX_FORMAT_HANDS:
                vertex_format = VERTEX_FORMAT_HANDS
                VertexCls = dst_mod.VertexC31f
                vertex_size = 24

            else:
                vertex_format = VERTEX_FORMAT_DEFAULT
                VertexCls = dst_mod.Vertex14d4  # using the most flexible one for now, no optimizations
                vertex_size = 28  # TODO: size_
        else:
            vertex_format = 0x49b4f029
            VertexCls = dst_mod.Vertex49b4
            vertex_size = 28

    MAX_BONES = 4  # enforces in `_process_weights_for_export`
    vertices_stream = KaitaiStream(BytesIO(bytearray(vertex_size * vertex_count)))
    bytes_empty = b'\x00\x00'
    for vertex_index, vertex in enumerate(bl_mesh.data.vertices):
        vertex_struct = VertexCls(_parent=mesh, _root=mesh._root)
        
        if has_bones:
            vertex_struct.position = dst_mod.Vec4S2(_parent=vertex_struct, _root=vertex_struct._root)
        else:
            vertex_struct.position = dst_mod.Vec3(_parent=vertex_struct, _root=vertex_struct._root)

        if vertex_format in VERTEX_FORMATS_TANGENT:
            vertex_struct.tangent = dst_mod.Vec4U1(_parent=vertex_struct, _root=vertex_struct._root)
        if vertex_format not in VERTEX_FORMATS_BRIDGE:
            vertex_struct.uv = dst_mod.Vec2HalfFloat(_parent=vertex_struct, _root=vertex_struct._root)
        if dst_mod.header.version == 156:
            vertex_struct.normal = dst_mod.Vec4U1(_parent=vertex_struct, _root=vertex_struct._root)
        else:
            vertex_struct.normal = dst_mod.Vec3U1(_parent=vertex_struct, _root=vertex_struct._root)
            vertex_struct.occlusion = 254
        if vertex_format in VERTEX_FORMATS_UV2:
            vertex_struct.uv2 = dst_mod.Vec2HalfFloat(_parent=vertex_struct, _root=vertex_struct._root)
        if vertex_format in VERTEX_FORMATS_UV3:
            vertex_struct.uv3 = dst_mod.Vec2HalfFloat(_parent=vertex_struct, _root=vertex_struct._root)
        if vertex_format in VERTEX_FORMATS_UV4:
            vertex_struct.uv3 = dst_mod.Vec2HalfFloat(_parent=vertex_struct, _root=vertex_struct._root)
        if vertex_format in VERTEX_FORMATS_RGBA:
            vertex_struct.rgba = dst_mod.Vec4U1(_parent=vertex_struct, _root=vertex_struct._root)
        # Position
        xyz = (vertex.co[0] * SCALE, vertex.co[1] * SCALE, vertex.co[2] * SCALE)
        xyz = (xyz[0], xyz[2], -xyz[1])  # z-up to y-up
        xyz = _apply_bbox_transforms(xyz, dst_mod, bbox_data) if has_bones else xyz
        vertex_struct.position.x = xyz[0]
        vertex_struct.position.y = xyz[1]
        vertex_struct.position.z = xyz[2]
        vertex_struct.position.w = 32767  # might be changed later
        # Normals
        norms = normals.get(vertex_index, (0, 0, 0))
        try:
            # from [-1, 1] to [0, 255], and clipping bad blender normals
            vertex_struct.normal.x = max(0, min(255, round(((norms[0] * 0.5) + 0.5) * 255)))
            vertex_struct.normal.y = max(0, min(255, round(((norms[2] * 0.5) + 0.5) * 255)))
            vertex_struct.normal.z = max(0, min(255, round(((norms[1] * -0.5) + 0.5) * 255)))
        except ValueError as err:
            if "cannot convert float NaN to integer" in str(err):
                vertex_struct.normal.x = 0
                vertex_struct.normal.y = 0
                vertex_struct.normal.z = 0
            else:
                raise
        if dst_mod.header.version == 156:
            vertex_struct.normal.w = 255  # is this occlusion as well?
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
        # UVS
        uv_x, uv_y = uvs_per_vertex.get(vertex_index, (0, 0))
        uv_x, uv_y = _normalize_uv(uv_x, uv_y)
        vertex_struct.uv.u = pack('e', uv_x)
        vertex_struct.uv.v = pack('e', uv_y)

        if vertex_format in VERTEX_FORMATS_UV2:
            if uvs_per_vertex_2:
                uv_x, uv_y = uvs_per_vertex_2.get(vertex_index, (0, 0))
                uv_x, uv_y = _normalize_uv(uv_x, uv_y)
                vertex_struct.uv2.u = pack('e', uv_x)
                vertex_struct.uv2.v = pack('e', uv_y)
            else:
                vertex_struct.uv2.u = bytes_empty
                vertex_struct.uv2.v = bytes_empty

        if vertex_format in VERTEX_FORMATS_UV3:
            if uvs_per_vertex_3:
                if use_special_vf:  # wacky way in RE5 to store vertex colors in UV3
                    try:
                        color = color_per_vertex[vertex_index]
                    except:
                        color = (255, 255, 255, 255)
                    _uv3_u = (color[1] << 8) | color[0]
                    _uv3_v = (color[3] << 8) | color[2]
                    vertex_struct.uv3.u = pack('H', _uv3_u)
                    vertex_struct.uv3.v = pack('H', _uv3_v)
                else:
                    uv_x, uv_y = uvs_per_vertex_3.get(vertex_index, (0, 0))
                    uv_x, uv_y = _normalize_uv(uv_x, uv_y)
                    vertex_struct.uv3.u = pack('e', uv_x)
                    vertex_struct.uv3.v = pack('e', uv_y)
            else:
                vertex_struct.uv3.u = bytes_empty
                vertex_struct.uv3.v = bytes_empty

        if vertex_format in VERTEX_FORMATS_UV4:
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
            if color_per_vertex:
                c = color_per_vertex.get(vertex_index, (0, 0, 0, 0))
                vertex_struct.rgba.x = c[0]
                vertex_struct.rgba.y = c[1]
                vertex_struct.rgba.z = c[2]
                vertex_struct.rgba.w = c[3]
            else:
                vertex_struct.rgba.x = 128
                vertex_struct.rgba.y = 128
                vertex_struct.rgba.z = 128
                vertex_struct.rgba.w = 255

        if has_bones:
            # applying bounding box constraints
            weights_data = weights_per_vertex.get(vertex_index, [])
            weight_values = [w for _, w in weights_data]
            weight_values.extend([0] * (MAX_BONES - len(weight_values)))
            if mesh_bone_palette:
                bone_indices = [mesh_bone_palette.index(bone_index) for bone_index, _ in weights_data]
            else:
                bone_indices = [bi for bi, _ in weights_data]
            bone_indices.extend([0] * (MAX_BONES - len(bone_indices)))
            vertex_struct.bone_indices = bone_indices

            if vertex_format == VERTEX_FORMAT_HANDS:
                # TODO: validation of only 2 bones being affected
                vertex_struct.bone_indices = [pack('e', bone_indices[0]), pack('e', bone_indices[1])]
                vertex_struct.position.w = round(unpack('e', weight_values[0])[0] * 32767)

            elif dst_mod.header.version != 156:
                # this is still buggy, see left-leg of em09.arc in re1
                vertex_struct.position.w = round(unpack('e', weight_values[0])[0] * 32767)
                vertex_struct.weight_values = [0, 0]
                vertex_struct.weight_values[0] = weight_values[1] if weight_values[1] else bytes_empty
                vertex_struct.weight_values[1] = weight_values[2] if weight_values[2] else bytes_empty
            else:
                vertex_struct.weight_values = weight_values

        vertex_struct._check()
        vertex_struct._write(vertices_stream)

    return vertices_stream, vertex_format, vertex_size


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

    elif dst_mod.header.version in (210, 211):
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
            influence_list = sorted(influence_list, key=lambda t: t[1])[-limit:]

        # normalize
        weights = [t[1] for t in influence_list]
        bone_indices = [t[0] for t in influence_list]
        total_weight = sum(weights)
        if total_weight:
            weights = [(w / total_weight) for w in weights]

        # float to byte
        weights = [round(w * 255) or 1 for w in weights]  # can't have zero values
        # correct precision
        if not weights:
            # XXX vertex_position_2 research, beware
            continue
        excess = sum(weights) - 255
        if excess:
            max_index, _ = max(enumerate(weights), key=lambda p: p[1])
            weights[max_index] -= excess

        if half_float:
            # TODO: do before losing precision
            weights = [pack('e', w / 255) for w in weights]

        new_weights_per_vertex[vertex_index] = list(zip(bone_indices, weights))

    return new_weights_per_vertex


def _calculate_weight_bounds(bl_obj, bl_mesh, dst_mod, meshes_data):
    unsorted_weight_bounds = []
    if bl_obj.type != "ARMATURE":
        weight_bound = _set_static_mesh_weight_bounds(dst_mod, bl_mesh, meshes_data)
        unsorted_weight_bounds.append(weight_bound)
    else:
        for vg in bl_mesh.vertex_groups:
            weight_bound = _calculate_vertex_group_weight_bound(
                bl_mesh.data, bl_obj, vg, dst_mod, meshes_data
            )
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
    radius = max(map(lambda vertex: get_dist(center, vertex.co[:]), bl_mesh.vertices))
    bsphere_export = (center_x * 100, center_z * 100, -center_y * 100, radius * 100)

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


def _calculate_vertex_group_weight_bound(blender_mesh, armature, vertex_group, dst_mod, meshes_data):
    vertices_in_group = []

    bone_index = armature.pose.bones.find(vertex_group.name)
    pose_bone = armature.pose.bones[bone_index]
    pose_bone_matrix = Matrix.Translation(pose_bone.head).inverted()

    for v in blender_mesh.vertices:
        v_groups = {g.group for g in v.groups}
        if vertex_group.index not in v_groups:
            continue
        vertices_in_group.append(v)

    vertices_in_group_bone_space = [pose_bone_matrix @ v.co for v in vertices_in_group]

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
    radius = max(map(lambda vertex: get_dist(center, vertex[:]), vertices_in_group_bone_space))
    bsphere_export = (center_x * 100, center_z * 100, -center_y * 100, radius * 100)

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

    oabb_dimension_export = (length_x * 100, length_z * 100, length_y * 100, 0.0)

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
    level_of_detail: bpy.props.IntProperty(default=255)
    idx_group: bpy.props.IntProperty(default=0)  # TODO: restrictions
    z_buffer_order: bpy.props.IntProperty(default=0)  # TODO: restrictions
    # we set this always to zero
    # unk_03: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_flag_01: bpy.props.BoolProperty(default=0)  # TODO: restrictions
    unk_flag_02: bpy.props.BoolProperty(default=0)
    unk_flag_03: bpy.props.BoolProperty(default=0)
    unk_flag_04: bpy.props.BoolProperty(default=0)
    unk_flag_05: bpy.props.BoolProperty(default=0)
    use_cast_shadows: bpy.props.BoolProperty(default=0)
    use_receive_shadows: bpy.props.BoolProperty(default=0)
    unk_flag_08: bpy.props.BoolProperty(default=0)
    vertex_offset_2: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_06: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_07: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_08: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_09: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_10: bpy.props.IntProperty(default=0)  # TODO: restrictions
    unk_11: bpy.props.IntProperty(default=0)  # TODO: restrictions

    def set_from_source(self, mesh):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            self.copy_attr(mesh, self, attr_name)

    def set_to_dest(self, mesh):
        for attr_name in self.__annotations__:
            self.copy_attr(self, mesh, attr_name)

    @staticmethod
    def copy_attr(src, dst, name):
        # will raise, making sure there's consistency
        src_value = getattr(src, name)
        setattr(dst, name, src_value)


@blender_registry.register_custom_properties_mesh("mod_21_mesh", ("re1", "rev2",))
@blender_registry.register_blender_prop
class Mod21MeshCustomProperties(bpy.types.PropertyGroup):
    level_of_detail: bpy.props.IntProperty(default=255)
    idx_group: bpy.props.IntProperty(default=0)  # TODO: restrictions
    type_mesh: bpy.props.IntProperty(default=0)  # TODO u1
    unk_class_mesh: bpy.props.IntProperty(default=0)  # TODO u1
    unk_render_mode: bpy.props.IntProperty(default=0)  # TODO u1
    bone_id_start: bpy.props.IntProperty(default=0)  # TODO u1
    mesh_index: bpy.props.IntProperty(default=0)  # TODO u2
    min_index: bpy.props.IntProperty(default=0)  # TODO u2
    max_index: bpy.props.IntProperty(default=0)  # TODO u2
    hash: bpy.props.IntProperty(default=0)  # TODO u4
    unk_01: bpy.props.IntProperty(default=0)  # TODO u1
    vertex_format: bpy.props.StringProperty()

    # XXX copy paste above and in material
    def set_from_source(self, mesh):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            try:
                self.copy_attr(mesh, self, attr_name)
            except TypeError:
                # hack for IntProperty apparently only being for signed integers
                self.copy_attr(mesh, self, attr_name, func=str)

    def set_to_dest(self, mesh):
        for attr_name in self.__annotations__:
            self.copy_attr(self, mesh, attr_name)

    @staticmethod
    def copy_attr(src, dst, name, func=None):
        # will raise, making sure there's consistency
        src_value = getattr(src, name)
        if func:
            src_value = func(src_value)
        setattr(dst, name, src_value)
