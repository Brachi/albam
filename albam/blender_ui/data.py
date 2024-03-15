import bpy

from albam.registry import blender_registry
from .import_panel import APPS


@blender_registry.register_blender_prop
class AlbamAsset(bpy.types.PropertyGroup):
    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    original_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821
    relative_path : bpy.props.StringProperty()
    extension: bpy.props.StringProperty()


def AlbamDataFactory():

    def create_data():
        data = {}
        for name, cls in blender_registry.props:
            if not name:
                continue
            data[name] = bpy.props.PointerProperty(type=cls)
        return data

    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    return type(
        'AlbamData',
        (bpy.types.PropertyGroup, ),
        {'__annotations__' : create_data()}

    )
