import struct

import bpy

from albam.lib.misc import chunks
from albam.registry import blender_registry
from .structs.hexane_edgemodel import HexaneEdgemodel
from .material import build_blender_materials


@blender_registry.register_import_function(app_id="reorc", extension="edgemodel", albam_asset_type="MESH")
def build_blender_model(vfile, context):
    edgemodel_bytes = vfile.get_bytes()

    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    skeleton = None
    bl_object = skeleton or bpy.data.objects.new(vfile.display_name, None)
    bl_materials = build_blender_materials(edgemodel, context)

    for mesh_header in edgemodel.meshes_header:
        if mesh_header.lod != 0:
            continue
        bl_mesh_ob = build_blender_mesh(mesh_header, bl_materials)
        bl_mesh_ob.parent = bl_object

    return bl_object


def build_blender_mesh(mesh_header, bl_materials):
    vertices = []
    uvs = []
    vertex_stride = 52  # TODO: compute
    edge_mesh = mesh_header.mesh
    me_ob = bpy.data.meshes.new("MESH-TODO")
    ob = bpy.data.objects.new("MESH-TODO", me_ob)

    current_offset = 0
    for vi in range(edge_mesh.num_vertices):
        pos_x = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset)[0]
        pos_y = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset + 4)[0]
        pos_z = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset + 8)[0]

        uv_x = struct.unpack_from('e', edge_mesh.buffer_vertices, current_offset + 24)[0]
        uv_y = struct.unpack_from('e', edge_mesh.buffer_vertices, current_offset + 26)[0]

        vertices.append((pos_x, -pos_z, pos_y))
        uvs.extend((uv_x, 1 - uv_y))
        current_offset += vertex_stride

    indices = struct.unpack_from(f'{edge_mesh.size_buffer_indices // 2}H', edge_mesh.buffer_indices)
    assert min(indices) >= 0, "Bad face indices"
    indices = chunks(indices, 3)
    indices = [triplet for triplet in indices
               if (triplet != (0, 0) and triplet != (0, 0, 0) and triplet != (0, ))]
    me_ob.from_pydata(vertices, [], indices)
    _build_uvs(me_ob, uvs)
    _build_weights(ob, edge_mesh)
    mesh_material_path = mesh_header.materials.first_material
    if bl_materials.get(mesh_material_path):
        me_ob.materials.append(bl_materials[mesh_material_path])

    return ob


def _build_weights(bl_obj, edge_mesh):
    WEIGHT = struct.Struct("8B")
    weights_per_vertex = {}

    for i in range(0, edge_mesh.size_buffer_weights, WEIGHT.size):
        wv_and_bi = WEIGHT.unpack_from(edge_mesh.buffer_weights, i)
        weightsval = wv_and_bi[0:4]
        boneindices = wv_and_bi[4:8]
        test = zip(boneindices, weightsval)
        weights_per_vertex[i // 8] = tuple(test)

    wperbone = {}
    for vertex, tuples in weights_per_vertex.items():
        for bone, value in tuples:
            if value != 0 and bone != 0 and bone not in wperbone:
                wperbone[bone] = []
                wperbone[bone].append((vertex, value))
            elif value != 0 and bone != 0 and bone in wperbone:
                wperbone[bone].append((vertex, value))

    for bone_index, data in wperbone.items():
        vg = bl_obj.vertex_groups.new(name=str(bone_index))
        for vertex_index, weight_value in data:
            vg.add((vertex_index,), weight_value, "ADD")


def _build_uvs(bl_mesh, uvs, name="uv"):
    if not uvs:
        return
    uv_layer = bl_mesh.uv_layers.new(name=name)
    per_loop_list = []
    for loop in bl_mesh.loops:
        offset = loop.vertex_index * 2
        per_loop_list.extend((uvs[offset], uvs[offset + 1]))
    uv_layer.data.foreach_set("uv", per_loop_list)
