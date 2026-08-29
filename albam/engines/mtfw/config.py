import bpy
import io
import xml.etree.ElementTree as ET
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile

from ...lib.xml_parser import from_sdl, to_sdl, from_xfs, to_xfs
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

    xml = from_sdl(sdl)
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object["sdl"] = bl_object_name + ".xml"
    text.from_string(xml_string)

    return bl_object


@blender_registry.register_import_function(app_id="re5", extension="lot", albam_asset_type="CONFIG")
def build_xfs_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    xfs_bytes = vfile.get_bytes()
    xfs = Xfs.from_bytes(xfs_bytes)
    xfs._read()
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(name=bl_object_name, object_data=None)

    xml = from_xfs(xfs, "lot")
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object["lot"] = bl_object_name + ".xml"
    text.from_string(xml_string)

    return bl_object
