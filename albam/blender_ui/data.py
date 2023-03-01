import bpy

from .import_panel import FileExplorerData


class AlbamData(bpy.types.PropertyGroup):
    file_explorer: bpy.props.PointerProperty(type=FileExplorerData)
