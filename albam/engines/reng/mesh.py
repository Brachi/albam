import ctypes
import io
import struct
import time

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix
import numpy as np

from ...exceptions import AlbamCheckFailure
from ...lib.misc import chunks
from ...registry import blender_registry
from ...vfs import VirtualFileData
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
    re_mesh._read()

    bl_object_name = file_list_item.display_name
    skeleton = None if not re_mesh.header.offset_bones else build_blender_armature(re_mesh, bl_object_name)
    bl_object = skeleton or bpy.data.objects.new(bl_object_name, None)
    start = time.time()
    materials = build_blender_materials(file_list_item, context)
    print("materials build took:", time.time() - start)

    start = time.time()
    model_info = re_mesh.model_info
    mesh_groups = model_info.lod_group_offsets[0].lod_group.mesh_groups if model_info else []
    for mesh_group in mesh_groups:
        for sub_mesh in mesh_group.mesh_group.meshes:
            bl_mesh_ob = build_blender_mesh(re_mesh, sub_mesh)
            bl_mesh_ob.parent = bl_object
            if skeleton:
                modifier = bl_mesh_ob.modifiers.new(type="ARMATURE", name="armature")
                modifier.object = skeleton
                modifier.use_vertex_groups = True
            try:
                material_name_index = re_mesh.material_name_remap[sub_mesh.material_index]
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
    nor_tan_raw = ((ctypes.c_byte * 8) * num_vertices).from_buffer_copy(vertex_buffer, normals_offset)

    # nor_tan packs normal.xyz + an unused/padding byte, then tangent.xyz +
    # a handedness-sign byte (see mesh.ksy's primitive_type enum) - only
    # the normal.xyz is decoded below (tangent isn't reconstructed from
    # Blender's own state anywhere), so the raw 8 bytes are stashed here,
    # verbatim, as export's only way back to them byte-exact.
    _stash_nor_tan_raw(bl_mesh, nor_tan_raw)

    vertex_normals = [(n[0] / 127, n[2] / -127, n[1] / 127) for n in nor_tan_raw]
    vert_normals = np.array(vertex_normals, dtype=np.float32)
    norms = np.linalg.norm(vert_normals, axis=1, keepdims=True)
    np.divide(vert_normals, norms, out=vert_normals, where=norms != 0)
    bl_mesh.polygons.foreach_set("use_smooth", [True] * len(bl_mesh.polygons))
    try:
        bl_mesh.create_normals_split()
    except AttributeError:
        # blender 4.1+
        pass
    bl_mesh.normals_split_custom_set_from_vertices(vert_normals)
    try:
        bl_mesh.use_auto_smooth = True
    except AttributeError:
        # blender 4.1+
        pass

    return ob


NOR_TAN_LO_ATTR = "albam_nor_tan_lo"
NOR_TAN_HI_ATTR = "albam_nor_tan_hi"


def _stash_nor_tan_raw(bl_mesh, nor_tan_raw):
    lo_attr = bl_mesh.attributes.new(NOR_TAN_LO_ATTR, "INT", "POINT")
    hi_attr = bl_mesh.attributes.new(NOR_TAN_HI_ATTR, "INT", "POINT")
    lo_attr.data.foreach_set("value", [struct.unpack("<i", struct.pack("<4b", *n[0:4]))[0] for n in nor_tan_raw])
    hi_attr.data.foreach_set("value", [struct.unpack("<i", struct.pack("<4b", *n[4:8]))[0] for n in nor_tan_raw])


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
        valid_parent = bone.parent_idx != -1
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


# mesh_group's own header (type/num_meshes/unk_01/unk_02/num_vertices/
# num_indices) is 16 bytes, immediately followed by its `meshes` array -
# see mesh.ksy. Not exposed as an instance/offset anywhere in the parsed
# struct, so export re-derives each submesh's own absolute file offset
# from this (needed to patch material_index in place without touching
# anything else in the entry).
MESH_GROUP_HEADER_SIZE = 16
MESH_ENTRY_SIZE = 16


def _mesh_entry_offsets(src_mesh, lod_group):
    entry_size = MESH_ENTRY_SIZE + (8 if src_mesh.version != 386270720 else 0)
    entries = []
    for mesh_group_offset in lod_group.mesh_groups:
        base = mesh_group_offset.offset + MESH_GROUP_HEADER_SIZE
        for i, sub_mesh in enumerate(mesh_group_offset.mesh_group.meshes):
            entries.append((sub_mesh, base + i * entry_size))
    return entries


def _original_submesh_vertex_count(buffers, sub_mesh):
    index_buffer = buffers.index_buffer
    indices = (ctypes.c_ushort * sub_mesh.num_indices).from_buffer_copy(index_buffer, sub_mesh.pos_index_buffer * 2)
    return len(set(indices))


def _build_material_name_to_index(src_mesh):
    return {
        src_mesh.named_nodes[name_index].value: material_index
        for material_index, name_index in enumerate(src_mesh.material_name_remap)
    }


def _build_bone_name_to_slot(src_mesh):
    name_offset = src_mesh.model_info.num_materials
    return {
        src_mesh.named_nodes[name_offset + real_bone_index].value: slot
        for slot, real_bone_index in enumerate(src_mesh.bones_header.bone_maps)
    }


def _vertex_uvs(bl_mesh):
    uv_layer = bl_mesh.uv_layers[0]
    per_vertex = [None] * len(bl_mesh.vertices)
    for loop in bl_mesh.loops:
        per_vertex[loop.vertex_index] = uv_layer.data[loop.index].uv
    return per_vertex


def _encode_vertex_weights(bl_mesh_ob, vertex_index, bone_name_to_slot):
    pairs = []
    for g in bl_mesh_ob.data.vertices[vertex_index].groups:
        if g.weight <= 0:
            continue
        slot = bone_name_to_slot.get(bl_mesh_ob.vertex_groups[g.group].name)
        if slot is None:
            continue
        pairs.append((slot, g.weight))
    # Which of the 8 joint/weight slots a given bone lands in isn't
    # recoverable from a Blender vertex group (it only knows a flat,
    # unordered set of (bone, weight) pairs per vertex - the original
    # file's primary-vs-secondary split isn't preserved anywhere once
    # imported) - sorted by weight descending is a reasonable, deterministic
    # convention, but this is a field-equivalent, not byte-exact, guarantee.
    pairs.sort(key=lambda p: -p[1])
    pairs = pairs[:8]
    joints = [0] * 8
    weights = [0] * 8
    for i, (slot, w) in enumerate(pairs):
        joints[i] = slot
        weights[i] = min(255, round(w * 255))
    return joints[0:4] + joints[4:8] + weights[0:4] + weights[4:8]


def _export_submesh(data, buffers, sub_mesh, bl_mesh_ob, bone_name_to_slot):
    bl_mesh = bl_mesh_ob.data
    num_vertices = len(bl_mesh.vertices)

    lo_attr = bl_mesh.attributes.get(NOR_TAN_LO_ATTR)
    hi_attr = bl_mesh.attributes.get(NOR_TAN_HI_ATTR)
    if lo_attr is None or hi_attr is None:
        raise AlbamCheckFailure(
            "Mesh is missing normal/tangent data needed for export",
            f"'{bl_mesh_ob.name}' has no {NOR_TAN_LO_ATTR}/{NOR_TAN_HI_ATTR} custom attributes.",
            "Only meshes imported by albam, with those attributes still intact, can "
            "currently be exported.",
        )

    bl_mesh.calc_loop_triangles()
    indices = [v for lt in bl_mesh.loop_triangles for v in lt.vertices]

    original_num_vertices = _original_submesh_vertex_count(buffers, sub_mesh)
    if num_vertices != original_num_vertices or len(indices) != sub_mesh.num_indices:
        raise AlbamCheckFailure(
            "Mesh vertex/index count doesn't match the original file",
            f"'{bl_mesh_ob.name}' has {num_vertices} vertices / {len(indices)} indices, "
            f"the original submesh has {original_num_vertices} / {sub_mesh.num_indices}.",
            "Exporting a mesh with a different vertex or triangle count than the imported "
            "file isn't supported yet - only re-exporting an unmodified (or attribute-only "
            "edited) import is.",
        )

    pos_acc, nor_tan_acc, uv_acc = buffers.primitive_accessors[0:3]
    weight_acc = next((a for a in buffers.primitive_accessors if a.primitive_type == 4), None)
    vertex_uvs = _vertex_uvs(bl_mesh)

    pos_off = buffers.offset_vertex_buffer + pos_acc.offset + sub_mesh.pos_vertex_buffer * pos_acc.size
    nor_tan_off = (buffers.offset_vertex_buffer + nor_tan_acc.offset +
                   sub_mesh.pos_vertex_buffer * nor_tan_acc.size)
    uv_off = buffers.offset_vertex_buffer + uv_acc.offset + sub_mesh.pos_vertex_buffer * uv_acc.size

    for i, v in enumerate(bl_mesh.vertices):
        bx, by, bz = v.co
        struct.pack_into("<3f", data, pos_off + i * pos_acc.size, bx, bz, -by)
        struct.pack_into(
            "<ii", data, nor_tan_off + i * nor_tan_acc.size,
            lo_attr.data[i].value, hi_attr.data[i].value,
        )
        u, uv_v = vertex_uvs[i]
        struct.pack_into("<2e", data, uv_off + i * uv_acc.size, u, uv_v)

    if weight_acc:
        weight_off = buffers.offset_vertex_buffer + weight_acc.offset + sub_mesh.pos_vertex_buffer * weight_acc.size
        for i in range(num_vertices):
            struct.pack_into(
                "<16B", data, weight_off + i * weight_acc.size,
                *_encode_vertex_weights(bl_mesh_ob, i, bone_name_to_slot),
            )

    ib_off = buffers.offset_index_buffer + sub_mesh.pos_index_buffer * 2
    struct.pack_into(f"<{len(indices)}H", data, ib_off, *indices)


def _export_material_index(data, entry_offset, bl_mesh_ob, material_name_to_index):
    materials = bl_mesh_ob.data.materials
    if not materials or materials[0] is None:
        raise AlbamCheckFailure(
            "Mesh has no material assigned",
            f"'{bl_mesh_ob.name}' has no material in its first material slot.",
            "Assign the material this submesh should reference before exporting.",
        )
    material_name = materials[0].name
    if material_name not in material_name_to_index:
        raise AlbamCheckFailure(
            "Mesh material isn't one of this file's materials",
            f"'{material_name}' isn't in this .mesh file's material name table.",
            "Only referencing one of the file's existing materials is supported - "
            ".mdf2 export isn't implemented yet.",
        )
    struct.pack_into("<B", data, entry_offset, material_name_to_index[material_name])


@blender_registry.register_export_function(app_id="re2", extension="mesh.2109108288")
@blender_registry.register_export_function(app_id="re3", extension="mesh.2109108288")
def export_reengine_mesh(bl_obj):
    """
    Patches vertex/index buffer bytes and each submesh's material_index
    directly into a mutable copy of the original file bytes, rather than
    rebuilding the whole object graph the way MTFW's exporter does -
    an unmodified _read()/_write() round trip of mesh.ksy isn't byte-exact
    (untracked padding/alignment bytes between sections), so a full
    from-scratch rebuild would already start from a worse baseline than
    "don't touch what didn't change". This only supports the same
    vertex/index/submesh counts as the source (see the AlbamCheckFailure
    messages below) - not general remeshing - which is what makes patching
    in place safe: every byte outside the touched regions, including any
    other LOD level's geometry (only LOD 0 is ever imported/re-exported),
    is guaranteed identical to the source file.
    """
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    src_bytes = asset.original_bytes

    src_mesh = ReengineMesh(KaitaiStream(io.BytesIO(src_bytes)))
    src_mesh._read()

    if src_mesh.model_info is None:
        raise AlbamCheckFailure(
            "This .mesh file has no main model to export",
            "header.offset_data == 0 - e.g. an occlusion-culling mesh, which has no "
            "renderable mesh-group tree at all (see RESULTS.md).",
            "Only meshes with a real model tree can be exported.",
        )

    lod_group = src_mesh.model_info.lod_group_offsets[0].lod_group
    entries = _mesh_entry_offsets(src_mesh, lod_group)

    bl_meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    if len(bl_meshes) != len(entries):
        raise AlbamCheckFailure(
            "Number of mesh objects doesn't match the original file",
            f"{len(bl_meshes)} mesh object(s) under '{bl_obj.name}', the original file's "
            f"LOD 0 has {len(entries)} submesh(es).",
            "Adding or removing submeshes isn't supported yet - only re-exporting an "
            "unmodified (or attribute-only edited) import is.",
        )

    material_name_to_index = _build_material_name_to_index(src_mesh)
    bone_name_to_slot = _build_bone_name_to_slot(src_mesh) if src_mesh.header.offset_bones else {}

    data = bytearray(src_bytes)
    buffers = src_mesh.buffers_data
    for bl_mesh_ob, (sub_mesh, entry_offset) in zip(bl_meshes, entries):
        _export_submesh(data, buffers, sub_mesh, bl_mesh_ob, bone_name_to_slot)
        _export_material_index(data, entry_offset, bl_mesh_ob, material_name_to_index)

    return [VirtualFileData(app_id, asset.relative_path, data_bytes=bytes(data))]
