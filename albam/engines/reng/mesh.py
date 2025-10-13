import ctypes
import io
import struct
import time

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix
import numpy as np

from ...lib.misc import chunks
from ...registry import blender_registry
from .material import build_blender_materials
from .structs.reengine_mesh import ReengineMesh


@blender_registry.register_import_function("re2", extension="mesh.2109108288", albam_asset_type="MODEL")
@blender_registry.register_import_function("re2_non_rt", extension="mesh.1808312334",
                                           albam_asset_type="MODEL")
@blender_registry.register_import_function("re3", extension="mesh.2109108288", albam_asset_type="MODEL")
@blender_registry.register_import_function("re3_non_rt", extension="mesh.1902042334",
                                           albam_asset_type="MODEL")
@blender_registry.register_import_function("re8", extension="mesh.2101050001", albam_asset_type="MODEL")
def build_blender_model(file_list_item, context: bpy.types.Context) -> bpy.types.Object:

    mesh_bytes = file_list_item.get_bytes()
    re_mesh = ReengineMesh(KaitaiStream(io.BytesIO(mesh_bytes)))

    bl_object_name = file_list_item.display_name
    skeleton = None if not re_mesh.header.offset_bones else build_blender_armature(re_mesh, bl_object_name)
    bl_object = skeleton or bpy.data.objects.new(bl_object_name, None)
    start = time.time()
    materials = build_blender_materials(file_list_item, context)
    print("materials build took:", time.time() - start)

    start = time.time()
    for mesh_group in re_mesh.model_info.model_offsets[0].model.mesh_groups:
        for sub_mesh in mesh_group.mesh_group.meshes:
            bl_mesh_ob = build_blender_mesh(re_mesh, sub_mesh)
            bl_mesh_ob.parent = bl_object
            if skeleton:
                modifier = bl_mesh_ob.modifiers.new(type="ARMATURE", name="armature")
                modifier.object = skeleton
                modifier.use_vertex_groups = True
            try:
                material_name_index = re_mesh.id_to_names_remap[sub_mesh.material_id]
                material_name = re_mesh.named_nodes[material_name_index].value
                bl_mesh_ob.data.materials.append(materials[material_name])
            except KeyError:
                print(f"WARNING: material '{material_name}' not found")

    print("mesh building took:", time.time() - start)
    return bl_object


def build_blender_mesh(re_mesh, sub_mesh):
    bl_mesh = bpy.data.meshes.new('TMP')
    ob = bpy.data.objects.new('TMP', bl_mesh)

    index_buffer = re_mesh.buffers_data.index_buffer
    index_offset = sub_mesh.pos_index_buffer * 2
    indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(index_buffer, index_offset)

    num_vertices = len(set(indices))
    vertex_buffer = re_mesh.buffers_data.vertex_buffer

    position_accessor = re_mesh.buffers_data.primitive_accessors[0]
    vertex_offset = position_accessor.offset + sub_mesh.pos_vertex_buffer * position_accessor.size
    locations = ((ctypes.c_float * 3) * num_vertices).from_buffer_copy(vertex_buffer, vertex_offset)
    locations = [(x, -z, y) for x, y, z in locations]

    bl_mesh.from_pydata(locations, [], chunks(indices, 3))

    if re_mesh.header.offset_bones:
        _build_weights(re_mesh, sub_mesh, num_vertices, vertex_buffer, ob)

    # UVS ####
    uv_accessor = re_mesh.buffers_data.primitive_accessors[2]
    uv_offset = uv_accessor.offset + sub_mesh.pos_vertex_buffer * uv_accessor.size
    uvs = struct.unpack_from(f"{num_vertices * 2}e", vertex_buffer, uv_offset)
    uv_layer = bl_mesh.uv_layers.new(name='name-me')
    per_loop_list = []
    for loop in bl_mesh.loops:
        offset = loop.vertex_index * 2
        per_loop_list.extend((uvs[offset], uvs[offset + 1]))
    uv_layer.data.foreach_set("uv", per_loop_list)

    # NORMALS ####
    normals_accessor = re_mesh.buffers_data.primitive_accessors[1]
    normals_offset = normals_accessor.offset + sub_mesh.pos_vertex_buffer * normals_accessor.size
    vertex_normals = ((ctypes.c_byte * 8) * num_vertices).from_buffer_copy(vertex_buffer, normals_offset)
    vertex_normals = [(n[0] / 127, n[2] / -127, n[1] / 127) for n in vertex_normals]
    vert_normals = np.array(vertex_normals, dtype=np.float32)
    norms = np.linalg.norm(vert_normals, axis=1, keepdims=True)
    np.divide(vert_normals, norms, out=vert_normals, where=norms != 0)
    bl_mesh.polygons.foreach_set("use_smooth", [True] * len(bl_mesh.polygons))
    bl_mesh.create_normals_split()
    bl_mesh.normals_split_custom_set_from_vertices(vert_normals)
    bl_mesh.use_auto_smooth = True

    return ob


def build_blender_armature(re_mesh, armature_name):
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
    # TODO: do it at blender level
    # non_deform_bone_indices = get_non_deform_bone_indices(mod)
    scale = 1
    name_offset = re_mesh.model_info.num_materials
    for i, bone in enumerate(re_mesh.bones_header.bones):
        bone_name = re_mesh.named_nodes[name_offset + i].value
        blender_bone = armature.edit_bones.new(bone_name)
        valid_parent = bone.parent_idx != 0xFFFF
        blender_bone.parent = blender_bones[bone.parent_idx] if valid_parent else None
        # blender_bone.use_deform = False if i in non_deform_bone_indices else True
        head = _name_me(re_mesh.bones_header.inverse_bind_matrices[i])
        blender_bone.head = [head[0] * scale, -head[2] * scale, head[1] * scale]
        blender_bone.tail = [head[0] * scale, -head[2] * scale, (head[1] * scale) + 0.01]
        blender_bones.append(blender_bone)

    bpy.ops.object.mode_set(mode="OBJECT")
    return armature_ob


def _name_me(matrix):
    m = matrix
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


def _build_weights(re_mesh, sub_mesh, num_vertices, vertex_buffer, bl_mesh_ob):
    weights_per_bone = {}
    skin_accessor = [acc for acc in re_mesh.buffers_data.primitive_accessors if acc.primitive_type == 4]
    assert skin_accessor, "No skin accessor but bones_offset?!"
    skin_accessor = skin_accessor[0]
    skin_offset = skin_accessor.offset + sub_mesh.pos_vertex_buffer * skin_accessor.size
    skin = ((ctypes.c_ubyte * 16) * num_vertices).from_buffer_copy(vertex_buffer, skin_offset)
    name_offset = re_mesh.model_info.num_materials

    for vertex_index, data in enumerate(skin):
        joints_0 = data[0:4]
        joints_1 = data[4:8]
        weights_0 = data[8:12]
        weights_1 = data[12:16]

        for j, w in ((j, w) for j, w in zip(joints_0, weights_0) if w):
            real_bone_index = re_mesh.bones_header.bone_maps[j]
            bone_name = re_mesh.named_nodes[name_offset + real_bone_index].value
            bone_data = weights_per_bone.setdefault(bone_name, [])
            bone_data.append((vertex_index, w / 255))
        for j, w in ((j, w) for j, w in zip(joints_1, weights_1) if w):
            real_bone_index = re_mesh.bones_header.bone_maps[j]
            bone_name = re_mesh.named_nodes[name_offset + real_bone_index].value
            bone_data = weights_per_bone.setdefault(bone_name, [])
            bone_data.append((vertex_index, w / 255))

    for bone_index, data in weights_per_bone.items():
        vg = bl_mesh_ob.vertex_groups.new(name=str(bone_index))
        for vertex_index, weight_value in data:
            vg.add((vertex_index,), weight_value, "ADD")
