import bpy
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile
from .structs.re4_uhd_bin import Re4UhdBin


@blender_registry.register_import_function(app_id="re4uhd", extension="BIN", albam_asset_type="MODEL")
def build_blender_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    print("importing model from bin")
