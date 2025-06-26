import struct

import bpy

from albam.lib.misc import chunks
from albam.registry import blender_registry
from .structs.hexane_edgemodel import HexaneEdgemodel


@blender_registry.register_import_function(app_id="reorc", extension="edgemodel", file_category="MESH")
def build_blender_model(vfile, context):
    edgemodel_bytes = vfile.get_bytes()

    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    skeleton = None
    bl_object = skeleton or bpy.data.objects.new(vfile.display_name, None)

    for mesh_header in edgemodel.meshes_header:
        if mesh_header.lod != 0:
            continue
        bl_mesh_ob = build_blender_mesh(mesh_header)
        bl_mesh_ob.parent = bl_object

    return bl_object


def build_blender_mesh(mesh_header):
    vertices = []
    vertex_stride = 52  # TODO: compute
    edge_mesh = mesh_header.mesh
    me_ob = bpy.data.meshes.new("MESH-TODO")
    ob = bpy.data.objects.new("MESH-TODO", me_ob)

    current_offset = 0
    for vi in range(edge_mesh.num_vertices):
        pos_x = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset)
        pos_y = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset + 4)
        pos_z = struct.unpack_from('f', edge_mesh.buffer_vertices, current_offset + 8)

        vertices.append((pos_x[0], -pos_z[0], pos_y[0]))
        current_offset += vertex_stride

    indices = struct.unpack_from(f'{edge_mesh.size_buffer_indices // 2}H', edge_mesh.buffer_indices)
    assert min(indices) >= 0, "Bad face indices"
    indices = chunks(indices, 3)
    indices = [triplet for triplet in indices if (triplet != (0, 0) and triplet != (0, 0, 0) and triplet != (0, ))]

    me_ob.from_pydata(vertices, [], indices)

    return ob
