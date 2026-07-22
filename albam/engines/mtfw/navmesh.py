import bpy
import bmesh
from .structs.nav_156 import Nav156
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile
from .collision import palette

KNOWN_FACE_FLAGS = [0, 256, 2048, 2049, 2050, 2560, 3072, 3584, 4096, 4098, 4608, 5120, 5124, 6144, 6145,
                    6146, 6656, 7168, 7172, 7176, 7680, 8448, 8452, 8456, 24832, 41216, 134144, 134656,
                    138240, 138752, 145664, 155904, 172288, 175872, 179968, 8390656, 8391168, 8397056,
                    8528128, 12591360]


@blender_registry.register_import_function(app_id="re5", extension="nav", albam_asset_type="NAVMESH")
def build_navmesh_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    assert app_id == "re5", f"The game {app_id} is not supported yet"
    nav_bytes = vfile.get_bytes()
    ModCls = Nav156
    nav = ModCls.from_bytes(nav_bytes)
    nav._read()

    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(bl_object_name, None)

    me_ob = bpy.data.meshes.new(bl_object_name)
    ob = bpy.data.objects.new(bl_object_name, me_ob)

    vertices = []
    faces = []
    face_flags = {}
    for i, vtx in enumerate(nav.vertices):
        vertices.append((vtx.x/100, -vtx.z/100, vtx.y/100))
    for i, face in enumerate(nav.faces):
        faces.append((face.v1, face.v2, face.v3))
        face_flags[face.index] = face.unk2
    me_ob.from_pydata(vertices, [], faces)
    _set_flags_as_mat(me_ob, face_flags)
    ob.parent = bl_object

    return bl_object


def _set_flags_as_mat(mesh, flags):
    unique_flags = []
    for flag in flags.values():
        if flag not in unique_flags:
            unique_flags.append(flag)

    mat_cache = {}
    for i, uf in enumerate(unique_flags):
        mat = bpy.data.materials.new(name="Nav %03d" % uf)
        try:
            mat.diffuse_color = palette[KNOWN_FACE_FLAGS.index(uf)]
        except (IndexError, ValueError):
            mat.diffuse_color = (0, 0, 0, 1)
            print("Unknown nav type: %d" % uf)
        mesh.materials.append(mat)
        mat_cache[uf] = i
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for face in bm.faces:
        face.material_index = mat_cache.get(flags[face.index], 0)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    # print(sorted(unique_flags))
