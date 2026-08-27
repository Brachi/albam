import bpy
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile

from .structs.xfs import Xfs
from .structs.sdl_156 import Sdl156


@blender_registry.register_import_function(app_id="re5", extension="sdl", albam_asset_type="CONFIG")
def build_sheduler_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    sdl_bytes = vfile.get_bytes()
    sdl = Sdl156.from_bytes(sdl_bytes)
    sdl._read()
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(name=bl_object_name, object_data=None)
    print(sdl.header.version)
    return bl_object


@blender_registry.register_import_function(app_id="re5", extension="lot", albam_asset_type="CONFIG")
def build_xfs_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    xfs_bytes = vfile.get_bytes()
    xfs = Xfs.from_bytes(xfs_bytes)
    xfs._read()
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(name=bl_object_name, object_data=None)
    print(xfs.header.major_ver)
    return bl_object