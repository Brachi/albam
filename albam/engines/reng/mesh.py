import ctypes
import io
import re
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

    app_id = file_list_item.app_id
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
            bl_mesh_ob = build_blender_mesh(re_mesh, sub_mesh, app_id)
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


def build_blender_mesh(re_mesh, sub_mesh, app_id):
    bl_mesh = bpy.data.meshes.new('TMP')
    ob = bpy.data.objects.new('TMP', bl_mesh)

    custom_properties = bl_mesh.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_properties.copy_custom_properties_from(sub_mesh)

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
    # verbatim, as export's only way back to them byte-exact. Per-vertex
    # data has no equivalent in albam's per-datablock custom-properties
    # system (see ReengineSubMeshCustomProperties below for the kind of
    # value that system does fit) - a real mesh attribute is the actual
    # right tool for a value that varies per vertex.
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


# albam's per-datablock custom-properties system (see
# albam/blender_ui/custom_properties.py) is the established, UI-visible
# way to carry a format-specific scalar value that has no native Blender
# mesh-object equivalent, across import/export - the same mechanism MTFW
# uses (e.g. Mod156MeshCustomProperties in albam/engines/mtfw/mesh.py).
# is_quad/vertex_buffer_index are exactly that kind of value for reng:
# real, per-submesh, meaningful on their own (not just round-trip
# plumbing), and small enough to expose directly. copy_custom_properties_
# from/to (defined below) match Kaitai's own attribute names 1:1, so they
# work generically against a real `mesh` struct instance with no
# per-field mapping code, the same trick MTFW's own custom-properties
# classes use against their own parsed structs.
@blender_registry.register_custom_properties_mesh("reengine_submesh", ("re2", "re3", "re8"))
@blender_registry.register_blender_prop
class ReengineSubMeshCustomProperties(bpy.types.PropertyGroup):
    is_quad: bpy.props.BoolProperty(name="Quad Topology", default=False, options=set())  # noqa: F821
    vertex_buffer_index: bpy.props.IntProperty(name="Vertex Buffer Index", default=0, options=set())  # noqa: F821

    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            setattr(self, attr_name, getattr(src_obj, attr_name))


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


def _export_submesh(vertex_buffer, index_buffer, buffers, sub_mesh, bl_mesh_ob, bone_name_to_slot):
    """
    Writes into vertex_buffer/index_buffer - mutable copies of
    buffers_data.vertex_buffer/index_buffer's own bytes, local to those
    buffers (no file-absolute offsets involved) - which the caller then
    assigns back onto the live, already-parsed ReengineMesh object graph,
    for _write() to serialize for real. Everything else about the file
    (header, name tables, bone data, other LOD levels) is never touched
    here at all - it stays exactly what _read() populated.
    """
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

    pos_off = pos_acc.offset + sub_mesh.pos_vertex_buffer * pos_acc.size
    nor_tan_off = nor_tan_acc.offset + sub_mesh.pos_vertex_buffer * nor_tan_acc.size
    uv_off = uv_acc.offset + sub_mesh.pos_vertex_buffer * uv_acc.size

    for i, v in enumerate(bl_mesh.vertices):
        bx, by, bz = v.co
        struct.pack_into("<3f", vertex_buffer, pos_off + i * pos_acc.size, bx, bz, -by)
        struct.pack_into(
            "<ii", vertex_buffer, nor_tan_off + i * nor_tan_acc.size,
            lo_attr.data[i].value, hi_attr.data[i].value,
        )
        u, uv_v = vertex_uvs[i]
        struct.pack_into("<2e", vertex_buffer, uv_off + i * uv_acc.size, u, uv_v)

    if weight_acc:
        weight_off = weight_acc.offset + sub_mesh.pos_vertex_buffer * weight_acc.size
        for i in range(num_vertices):
            struct.pack_into(
                "<16B", vertex_buffer, weight_off + i * weight_acc.size,
                *_encode_vertex_weights(bl_mesh_ob, i, bone_name_to_slot),
            )

    ib_off = sub_mesh.pos_index_buffer * 2
    struct.pack_into(f"<{len(indices)}H", index_buffer, ib_off, *indices)


_BLENDER_DEDUP_SUFFIX_RE = re.compile(r"\.\d{3}$")


def _export_submesh_fields(sub_mesh, bl_mesh_ob, material_name_to_index, app_id):
    """
    Sets sub_mesh.material_index/is_quad/vertex_buffer_index directly on
    the live, already-parsed Kaitai object - these are plain attributes on
    it, not file offsets to compute, so there's no hand-maintained layout
    math here at all (contrast _mesh_entry_offsets, which this replaced -
    see git history). _write() picks up whatever's sitting on sub_mesh at
    call time, same as every other untouched field on it.
    """
    materials = bl_mesh_ob.data.materials
    if not materials or materials[0] is None:
        raise AlbamCheckFailure(
            "Mesh has no material assigned",
            f"'{bl_mesh_ob.name}' has no material in its first material slot.",
            "Assign the material this submesh should reference before exporting.",
        )
    material_name = materials[0].name
    if material_name not in material_name_to_index:
        # bpy.data.materials disambiguates same-named materials within one
        # Blender session (e.g. importing the same file's materials twice)
        # by appending ".001" etc. - strip that back off before giving up,
        # since it's a Blender-side rename, not evidence of a genuinely
        # different/new material.
        deduped = _BLENDER_DEDUP_SUFFIX_RE.sub("", material_name)
        if deduped in material_name_to_index:
            material_name = deduped
        else:
            raise AlbamCheckFailure(
                "Mesh material isn't one of this file's materials",
                f"'{material_name}' isn't in this .mesh file's material name table.",
                "Only referencing one of the file's existing materials is supported - "
                ".mdf2 export isn't implemented yet.",
            )
    sub_mesh.material_index = material_name_to_index[material_name]

    custom_properties = bl_mesh_ob.data.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_properties.copy_custom_properties_to(sub_mesh)


# Offsets header names but has no instance/type modeling the data they
# point to at all (see RESULTS.md) - a fresh _write() leaves these regions
# zeroed, since nothing in the object graph ever reads (or therefore
# writes back) them. This export is geometry-only and never intends to
# touch any of them, so they're restored byte-for-byte from the source
# after _write() - not reconstructed, just not silently destroyed.
_UNMODELED_HEADER_OFFSETS = (
    "offset_shadow_mesh_group", "offset_normal_recalc", "offset_blend_shapes",
    "offset_bone_aabb", "offset_floats",
)
_ALL_HEADER_OFFSETS = _UNMODELED_HEADER_OFFSETS + (
    "offset_data", "offset_occlusion_mesh_group", "offset_bones", "offset_buffers_header",
    "offset_material_name_remap", "offset_bone_name_remap", "offset_blend_shape_name_remap",
    "offset_names",
)


def _restore_unmodeled_regions(data, src_bytes, header):
    known_offsets = sorted({getattr(header, name) for name in _ALL_HEADER_OFFSETS if getattr(header, name)})
    for name in _UNMODELED_HEADER_OFFSETS:
        start = getattr(header, name)
        if not start:
            continue
        end = next((o for o in known_offsets if o > start), len(data))
        data[start:end] = src_bytes[start:end]


@blender_registry.register_export_function(app_id="re2", extension="mesh.2109108288")
@blender_registry.register_export_function(app_id="re3", extension="mesh.2109108288")
def export_reengine_mesh(bl_obj):
    """
    Parses the original file into a real ReengineMesh, mutates vertex/
    index buffer bytes and each submesh's material_index/is_quad/
    vertex_buffer_index directly on that live object graph, then lets
    Kaitai's own _write() serialize the whole thing - the same idiom
    MTFW's real .mod export already uses (see albam/engines/mtfw/mesh.py),
    rather than hand-computing absolute file offsets into a raw byte copy
    (the previous approach here - see git history).

    This only supports the same vertex/index/submesh counts as the source
    (see the AlbamCheckFailure messages below), not general remeshing -
    every submesh field this doesn't explicitly touch (num_indices,
    pos_index_buffer, pos_vertex_buffer, unk_01, ...) is left exactly as
    _read() populated it, and every LOD level other than LOD 0 (the only
    one ever imported) round-trips untouched through the same mechanism.

    mesh.ksy doesn't model every byte of the real file yet - two header
    offsets (bone AABBs, and a shadow-mesh LOD tree on some files) are
    identified but have no instance reading their pointed-to data, so a
    plain _write() would zero them. _restore_unmodeled_regions patches
    those specific, known regions back in from the source afterward -
    everything else is reproduced by the real mechanism, not patched.
    """
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    src_bytes = asset.original_bytes

    src_mesh = ReengineMesh(KaitaiStream(io.BytesIO(src_bytes)))
    src_mesh._read()
    # _write() reassigns src_mesh's _io to the destination stream before
    # its own _fetch_instances() call would otherwise lazily populate
    # every not-yet-accessed instance from the source - by then it's too
    # late (the source bytes are gone). Force every lazy instance in the
    # whole tree to be read/cached now, while _io still points at the
    # source (same fix tests/reng/test_tex_serialization.py needed for
    # the same reason).
    src_mesh._fetch_instances()

    if src_mesh.model_info is None:
        raise AlbamCheckFailure(
            "This .mesh file has no main model to export",
            "header.offset_data == 0 - e.g. an occlusion-culling mesh, which has no "
            "renderable mesh-group tree at all (see RESULTS.md).",
            "Only meshes with a real model tree can be exported.",
        )

    lod_group = src_mesh.model_info.lod_group_offsets[0].lod_group
    sub_meshes = [sm for mg in lod_group.mesh_groups for sm in mg.mesh_group.meshes]

    bl_meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    if len(bl_meshes) != len(sub_meshes):
        raise AlbamCheckFailure(
            "Number of mesh objects doesn't match the original file",
            f"{len(bl_meshes)} mesh object(s) under '{bl_obj.name}', the original file's "
            f"LOD 0 has {len(sub_meshes)} submesh(es).",
            "Adding or removing submeshes isn't supported yet - only re-exporting an "
            "unmodified (or attribute-only edited) import is.",
        )

    material_name_to_index = _build_material_name_to_index(src_mesh)
    bone_name_to_slot = _build_bone_name_to_slot(src_mesh) if src_mesh.header.offset_bones else {}

    buffers = src_mesh.buffers_data
    vertex_buffer = bytearray(buffers.vertex_buffer)
    index_buffer = bytearray(buffers.index_buffer)
    for bl_mesh_ob, sub_mesh in zip(bl_meshes, sub_meshes):
        _export_submesh(vertex_buffer, index_buffer, buffers, sub_mesh, bl_mesh_ob, bone_name_to_slot)
        _export_submesh_fields(sub_mesh, bl_mesh_ob, material_name_to_index, app_id)
    buffers.vertex_buffer = bytes(vertex_buffer)
    buffers.index_buffer = bytes(index_buffer)

    out_stream = KaitaiStream(io.BytesIO(bytearray(len(src_bytes))))
    src_mesh._check()
    src_mesh._write(out_stream)
    data = bytearray(out_stream.to_byte_array())

    _restore_unmodeled_regions(data, src_bytes, src_mesh.header)

    return [VirtualFileData(app_id, asset.relative_path, data_bytes=bytes(data))]
