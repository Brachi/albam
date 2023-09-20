from binascii import crc32
from collections import namedtuple
from struct import unpack

import bpy
from mathutils import Matrix

from albam.lib.blender import strip_triangles_to_triangles_list
from albam.lib.misc import chunks
from albam.registry import blender_registry
from .material import build_blender_materials
from .structs.mod_156 import Mod156
from .structs.mod_21 import Mod21


MOD_CLASS_MAPPER = {
    156: Mod156,
    210: Mod21,
    211: Mod21,
}

BBOX_AFFECTED = [
    0xcbf6c01a,
    0xb0983013,
    0xA8FAB018,
    0xd877801b,
]


@blender_registry.register_import_function(app_id="re0", extension="mod")
@blender_registry.register_import_function(app_id="re1", extension="mod")
@blender_registry.register_import_function(app_id="re5", extension="mod")
def build_blender_model(file_list_item, context):
    LODS_TO_IMPORT = (1, 255)

    mod_bytes = file_list_item.get_bytes()
    mod_version = mod_bytes[4]
    assert mod_version in MOD_CLASS_MAPPER, f"Unsupported version: {mod_version}"
    ModCls = MOD_CLASS_MAPPER[mod_version]
    mod = ModCls.from_bytes(mod_bytes)

    bl_object_name = file_list_item.display_name
    bbox_data = _create_bbox_data(mod)
    skeleton = None if mod.header.num_bones == 0 else build_blender_armature(mod, bl_object_name, bbox_data)
    bl_object = skeleton or bpy.data.objects.new(bl_object_name, None)
    materials = build_blender_materials(file_list_item, context, mod, bl_object_name)

    for i, mesh in enumerate(m for m in mod.meshes if m.level_of_detail in LODS_TO_IMPORT):
        try:
            name = f"{bl_object_name}_{str(i).zfill(2)}"
            bl_mesh_ob = build_blender_mesh(mod, mesh, name, bbox_data, mod_version == 156)
            bl_mesh_ob.parent = bl_object
            if skeleton:
                modifier = bl_mesh_ob.modifiers.new(type="ARMATURE", name="armature")
                modifier.object = skeleton
                modifier.use_vertex_groups = True
            material_hash = _get_material_hash(mod, mesh)
            if materials.get(material_hash):
                bl_mesh_ob.data.materials.append(materials[material_hash])
            else:
                print(f"[{bl_object_name}] material {material_hash} not found")

        except Exception as err:
            print(f"[{bl_object_name}] error building mesh {i} {err}")
            continue

    return bl_object


def build_blender_mesh(mod, mesh, name, bbox_data, use_tri_strips=False):
    me_ob = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me_ob)

    locations = []
    normals = []
    uvs_1 = []
    uvs_2 = []
    uvs_3 = []
    vertex_colors = []
    weights_per_bone = {}

    for vertex_index, vertex in enumerate(mesh.vertices):
        _process_locations(mod.header.version, mesh, vertex, locations, bbox_data)
        _process_normals(vertex, normals)
        _process_uvs(vertex, uvs_1, uvs_2, uvs_3)
        _process_vertex_colors(mod.header.version, vertex, vertex_colors)
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
    _build_vertex_colors(me_ob, vertex_colors, "vc")
    _build_weights(ob, weights_per_bone)

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

    elif (w is not None and mod_version == 210) or (mod_version == 210 and mesh.vertex_format in BBOX_AFFECTED):
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


def _process_uvs(vertex, uvs_1_out, uvs_2_out, uvs_3_out):
    if not hasattr(vertex, "uv"):
        return
    u = unpack("e", bytes(vertex.uv.u))[0]
    v = unpack("e", bytes(vertex.uv.v))[0]
    uvs_1_out.extend((u, 1-v))

    if not hasattr(vertex, "uv2"):
        return
    u = unpack("e", bytes(vertex.uv2.u))[0]
    v = unpack("e", bytes(vertex.uv2.v))[0]
    uvs_2_out.extend((u, 1-v))

    if not hasattr(vertex, "uv3"):
        return
    u = unpack("e", bytes(vertex.uv3.u))[0]
    v = unpack("e", bytes(vertex.uv3.v))[0]
    uvs_3_out.extend((u, 1-v))


def _process_vertex_colors(mod_version, vertex, rgba_out):
    if not hasattr(vertex, "rgba"):
        return
    if mod_version == 210:
        b = vertex.rgba.x/225
        g = vertex.rgba.y/225
        r = vertex.rgba.z/255
        a = vertex.rgba.w/255
        rgba_out.append((r, g, b, a))


def _process_weights(mod, mesh, vertex, vertex_index, weights_per_bone):
    if not hasattr(vertex, "bone_indices"):
        return

    bone_indices = _get_bone_indices(mod, mesh, vertex.bone_indices)
    weights = _get_weights(mod, mesh, vertex)

    for bi, bone_index in enumerate(bone_indices):
        bone_data = weights_per_bone.setdefault(bone_index, [])
        bone_data.append((vertex_index, weights[bi]))

    return weights_per_bone


def _get_bone_indices(mod, mesh, bone_indices):
    mapped_bone_indices = []

    if mod.header.version == 156:
        bone_palette = mod.bones_mapping[mesh.bone_map_index]
        for bi, bone_index in enumerate(bone_indices):
            if bone_index >= bone_palette.unk_01:
                real_bone_index = mod.bone_map[bone_index]
            else:
                try:
                    real_bone_index = mod.bones_mapping[mesh.bone_map_index].indices[bone_index]
                except IndexError:
                    # Behaviour not observed in original files so far
                    real_bone_index = bone_index
            mapped_bone_indices.append(real_bone_index)
    elif mesh.vertex_format in (
        0xC31F201C,
    ):
        b1 = int(unpack("e", bone_indices[0])[0])
        b2 = int(unpack("e", bone_indices[0])[0])
        mapped_bone_indices.extend((b1, b2))
    elif mesh.vertex_format == 0xdb7da014:
        b1 = bone_indices[0]
        b2 = bone_indices[2]
        mapped_bone_indices.extend((b1, b2))
    else:
        mapped_bone_indices = bone_indices

    return mapped_bone_indices


def _get_weights(mod, mesh, vertex):
    if mod.header.version == 156 or mesh.vertex_format == 0xcb68015:
        return [w / 255 for w in vertex.weight_values]

    # Assuming all vertex formats share this pattern.
    # TODO: verify
    if len(vertex.bone_indices) == 1:
        return (1.0,)

    elif mesh.vertex_format in (
        0x14D40020,
        0x2F55C03D,
    ):
        w1 = vertex.position.w / 32767
        w2 = unpack("e", bytes(vertex.weight_values[0]))[0]
        w3 = unpack("e", bytes(vertex.weight_values[1]))[0]
        w4 = 1.0 - w1 - w2 - w3
        return (w1, w2, w3, w4)

    elif mesh.vertex_format in (
        0xC31F201C,
        0xdb7da014,
     ):
        w1 = vertex.position.w / 32767
        w2 = 1.0 - w1
        return (w1, w2)
    else:
        print(f"Can't get weights for vertex_format '{mesh.vertex_format}'")
        return (0, 0, 0, 0)


def _build_normals(bl_mesh, normals):
    if not normals:
        return
    loop_normals = []
    bl_mesh.create_normals_split()
    bl_mesh.validate(clean_customdata=False)
    bl_mesh.update(calc_edges=True)
    bl_mesh.polygons.foreach_set("use_smooth", [True] * len(bl_mesh.polygons))

    for loop in bl_mesh.loops:
        loop_normals.append(normals[loop.vertex_index])
    bl_mesh.normals_split_custom_set_from_vertices(normals)
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
    if len(vertex_colors)>0:
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
    for i, bone in enumerate(mod.bones):
        blender_bone = armature.edit_bones.new(str(i))
        valid_parent = bone.idx_parent < 255
        blender_bone.parent = blender_bones[bone.idx_parent] if valid_parent else None
        # blender_bone.use_deform = False if i in non_deform_bone_indices else True
        m = mod.inverse_bind_matrices[i]
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
    dimension = max(
        abs(mod.header.bbox_min.x), abs(mod.header.bbox_min.y), abs(mod.header.bbox_min.z)
    ) + max(abs(mod.header.bbox_max.x), abs(mod.header.bbox_max.y), abs(mod.header.bbox_max.z))

    bbox_data = BboxData(
        min_x=mod.header.bbox_min.x,
        min_y=mod.header.bbox_min.y,
        min_z=mod.header.bbox_min.z,
        max_x=mod.header.bbox_max.x,
        max_y=mod.header.bbox_max.y,
        max_z=mod.header.bbox_max.z,
        width=mod.header.bbox_max.x - mod.header.bbox_min.x,
        height=mod.header.bbox_max.y - mod.header.bbox_min.y,
        depth=mod.header.bbox_max.z - mod.header.bbox_min.z,
        dimension=dimension,
    )

    return bbox_data


def _get_material_hash(mod, mesh):
    material_hash = None
    if mod.header.version == 156:
        material_hash = mesh.idx_material
    elif mod.header.version == 210:
        material_name = mod.material_names[mesh.idx_material // 16]
        material_hash = crc32(material_name.encode()) ^ 0xFFFFFFFF
    return material_hash
