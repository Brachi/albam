import bpy
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile
from ...lib.misc import chunks
from .structs.re4_uhd_bin import Re4UhdBin
from ...lib.blender import strip_triangles_to_triangles_list


@blender_registry.register_import_function(app_id="re4uhd", extension="BIN", albam_asset_type="MODEL")
def build_blender_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    bin_bytes = vfile.get_bytes()
    bin = Re4UhdBin.from_bytes(bin_bytes)
    bin._read()
    bl_object_name = vfile.display_name

    locations = [_process_locations(vertex) for vertex in bin.vertex_positions]
    indices = bin.indexes
    faces = []
    buffer = {}
    lookup_indices = {
        0: [],
        1: [],
        2: [],
    }
    # for vindex, findex in enumerate(indices):
    #    lookup_indices[findex].append(vindex)


    for vindex, findex in enumerate(indices):
        buffer[findex] = vindex
        if len(buffer) == 3:
            tri = (buffer[0], buffer[1], buffer[2])
            faces.append(tri)
            buffer = {}

    bl_object = bpy.data.objects.new(bl_object_name, None)

    name = f"{bl_object_name}_test "
    me_ob = bpy.data.meshes.new(vfile.display_name)
    me_ob.from_pydata(locations, [], faces)
    ob = bpy.data.objects.new(name, me_ob)

    ob.parent = bl_object
    return bl_object


def _process_locations(vertex):
    x = vertex.x
    y = vertex.y
    z = vertex.z

    # Y-up to z-up and cm to m
    return (x * 0.01, -z * 0.01, y * 0.01)
