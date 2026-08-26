import struct
from collections import defaultdict
from itertools import chain

import bpy

from ...lib.misc import chunks
from ...registry import blender_registry
from .structs.hexane_edgemodel import HexaneEdgemodel
from .material import build_blender_materials
from .skeleton import build_blender_skeleton

# One vertex's weight record: four 0-255 weights, then their four bone indices.
WEIGHT = struct.Struct("8B")

# Vertex strides whose UV pair is confirmed to sit at offset 24 - see
# build_blender_mesh.
UV_STRIDES = (28, 52)


@blender_registry.register_import_function(app_id="reorc", extension="edgemodel", albam_asset_type="MODEL")
def build_blender_model(vfile, context):
    edgemodel_bytes = vfile.get_bytes()

    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    edgemodel._read()
    bl_object_name = vfile.display_name
    skeleton, bone_names = build_blender_skeleton(vfile, context)
    bl_object = skeleton or bpy.data.objects.new(bl_object_name, None)
    bl_materials = build_blender_materials(edgemodel, context)

    for i, mesh_header in enumerate(edgemodel.meshes_header):
        if mesh_header.lod != 0:
            continue
        # Same naming as albam.engines.mtfw.mesh.build_blender_model: the
        # model's own name plus the mesh's index in the file, kept even for
        # the lod-0-only subset imported here, so a mesh's name still points
        # at where it came from.
        name = f"{bl_object_name}_{str(i).zfill(4)}"
        bl_mesh_ob = build_blender_mesh(mesh_header, name, bl_materials, bone_names)
        bl_mesh_ob.parent = bl_object
        if skeleton:
            modifier = bl_mesh_ob.modifiers.new(type="ARMATURE", name="armature")
            modifier.object = skeleton
            modifier.use_vertex_groups = True

    return bl_object


def build_blender_mesh(mesh_header, name, bl_materials, bone_names=None):
    vertices = []
    normals = []
    tangents = []
    uvs = []
    edge_mesh = mesh_header.mesh
    # Not a fixed 52 bytes - a full-game sweep found 11 distinct real
    # strides (12, 16, 24, 28, 32, 40, 44, 52, 56, 60, 64), 52 being only
    # ~76% of meshes.
    vertex_stride = (
        edge_mesh.size_buffer_vertices // edge_mesh.num_vertices if edge_mesh.num_vertices else 0
    )
    me_ob = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me_ob)

    # UV is a half2 pair at offset 24, for these two strides. Every other
    # stride with room for one there decodes to nonsense at that offset -
    # across a real dataset, 99.6% (28) and 99.4% (52) of decoded pairs
    # land in a plausible range, against 0% (32), 36% (56) and 27% (60) -
    # so those meshes keep their UVs somewhere else, or don't have any. A
    # per-stride offset sweep finds no consistent answer for them (the
    # best candidate differs per stride, with nothing corroborating it),
    # so they import without UVs rather than with garbage ones.
    has_uvs = vertex_stride in UV_STRIDES
    # Normal is a plain, uncompressed float32 xyz right after position - not
    # some packed/quantized format, confirmed against real geometry (single-
    # triangle/quad props spanning strides 24/28/32/52): decoded vector is
    # unit-length to float32 precision and its face-normal alignment is ~1.0.
    has_normal = vertex_stride >= 24
    # Tangent (and a bitangent right after it, not imported - Blender
    # derives it from normal+tangent+a handedness sign it computes itself)
    # only confirmed at this exact stride: three float32 triples in a row
    # (position, normal, tangent) all read back as unit vectors, tangent
    # orthogonal to normal to 6+ decimal places. Larger strides (56, 60)
    # do NOT reproduce this at the same offset - real data there fails the
    # unit-length/orthogonality check, meaning something else (uncomodeled)
    # is interleaved before tangent for those, so this stays gated to the
    # one stride it's actually confirmed for rather than guessed at.
    has_tangent = vertex_stride == 52
    current_offset = 0
    for vi in range(edge_mesh.num_vertices):
        pos_x = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset)[0]
        pos_y = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset + 4)[0]
        pos_z = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset + 8)[0]

        vertices.append((pos_x, -pos_z, pos_y))

        if has_normal:
            nx, ny, nz = struct.unpack_from('fff', edge_mesh.buffer_vertices, current_offset + 12)
            normals.append((nx, -nz, ny))

        if has_uvs:
            uv_x = struct.unpack_from('e', edge_mesh.buffer_vertices, current_offset + 24)[0]
            uv_y = struct.unpack_from('e', edge_mesh.buffer_vertices, current_offset + 26)[0]
            uvs.extend((uv_x, 1 - uv_y))

        if has_tangent:
            tx, ty, tz = struct.unpack_from('fff', edge_mesh.buffer_vertices, current_offset + 28)
            tangents.append((tx, -tz, ty))

        current_offset += vertex_stride

    indices = struct.unpack_from(f'{edge_mesh.size_buffer_indices // 2}H', edge_mesh.buffer_indices)
    assert min(indices) >= 0, "Bad face indices"
    indices = chunks(indices, 3)
    indices = [triplet for triplet in indices
               if (triplet != (0, 0) and triplet != (0, 0, 0) and triplet != (0, ))]
    me_ob.from_pydata(vertices, [], indices)
    _build_normals(me_ob, normals)
    _build_tangents(me_ob, tangents)
    _build_uvs(me_ob, uvs)
    _build_weights(ob, edge_mesh, bone_names)
    mesh_material_path = mesh_header.materials.first_material
    if bl_materials.get(mesh_material_path):
        me_ob.materials.append(bl_materials[mesh_material_path])

    return ob


def _build_normals(bl_mesh, normals):
    if not normals:
        return
    # Blender 4.1+ only (this engine has no older-Blender compat path
    # anywhere) - custom split normals are automatic once every polygon is
    # marked smooth, no create_normals_split()/use_auto_smooth needed.
    bl_mesh.polygons.foreach_set("use_smooth", [True] * len(bl_mesh.polygons))
    bl_mesh.normals_split_custom_set_from_vertices(normals)


def _build_tangents(bl_mesh, tangents):
    if not tangents:
        return
    # Blender's tangent slot is computed (mesh.calc_tangents()), not
    # settable, so the imported tangent is stored as a plain custom
    # attribute instead, for round-trip/inspection purposes only.
    tangent_attr = bl_mesh.attributes.new(name="tangent", type='FLOAT_VECTOR', domain='POINT')
    tangent_attr.data.foreach_set("vector", list(chain.from_iterable(tangents)))


def _weights_buffer(edge_mesh):
    """The mesh's weight buffer bytes, or None if it has none.

    Some real meshes store a size_buffer_weights far past the end of the
    file - low 16 bits 0xffff, the rest noise - which the parser can only
    read by raising, taking the whole import down with it. The buffer's
    real length is one record per vertex, so that is what gets read when
    the stored size doesn't fit in the file.
    """
    if not edge_mesh.size_buffer_weights:
        return None

    stream = edge_mesh._io
    available = max(stream.size() - edge_mesh.ofs_buffer_weights, 0)
    if edge_mesh.size_buffer_weights <= available:
        return edge_mesh.buffer_weights

    size = min(edge_mesh.num_vertices * WEIGHT.size, available)
    if size <= 0:
        return None
    position = stream.pos()
    try:
        stream.seek(edge_mesh.ofs_buffer_weights)
        return stream.read_bytes(size)
    finally:
        stream.seek(position)


def _build_weights(bl_obj, edge_mesh, bone_names=None):
    buffer_weights = _weights_buffer(edge_mesh)
    if buffer_weights is None:
        return

    # One 8-byte record per vertex: four weights, then the four bone
    # indices they belong to. A zero weight means the slot is unused; the
    # bone index alone says nothing - 0 is the skeleton's root, a real
    # bone that real vertices are weighted to (whole meshes are weighted
    # to it alone).
    weights_per_bone = defaultdict(list)
    for i in range(0, len(buffer_weights) - WEIGHT.size + 1, WEIGHT.size):
        record = WEIGHT.unpack_from(buffer_weights, i)
        for bone_index, weight_value in zip(record[4:8], record[0:4]):
            if weight_value:
                weights_per_bone[bone_index].append((i // WEIGHT.size, weight_value))

    for bone_index, data in weights_per_bone.items():
        # Bone indices range over the skeleton's full node_count (see
        # skel.ksy's node_count), so bone_names[bone_index] is a real bone
        # name whenever a skeleton was found at all.
        if bone_names and bone_index < len(bone_names):
            vg_name = bone_names[bone_index]
        else:
            vg_name = str(bone_index)
        vg = bl_obj.vertex_groups.new(name=vg_name)
        for vertex_index, weight_value in data:
            # Stored as 0-255 fixed point (a vertex's four weights sum to
            # 255); Blender's are 0.0-1.0 and it clamps anything above,
            # which would flatten every real weight to a full 1.0.
            vg.add((vertex_index,), weight_value / 255, "ADD")


def _build_uvs(bl_mesh, uvs, name="uv"):
    if not uvs:
        return
    uv_layer = bl_mesh.uv_layers.new(name=name)
    per_loop_list = []
    for loop in bl_mesh.loops:
        offset = loop.vertex_index * 2
        per_loop_list.extend((uvs[offset], uvs[offset + 1]))
    uv_layer.data.foreach_set("uv", per_loop_list)
