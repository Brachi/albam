from albam import blender   # noqa , used by register_module

try:
    import bpy
except ImportError:
    pass

import albam.mtframework.blender_import  # noqa
import albam.mtframework.blender_export  # noqa


bl_info = {
    "name": "Albam",
    "author": "Sebastian Brachi",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "Properties Panel",
    "description": "Import-Export multiple video-bame formats",
    "wiki_url": "https://github.com/Brachi/albam",
    "tracker_url": "https://github.com/Brachi/albam/issues",
    "category": "Import-Export"}


def register():

    class Dummy(bpy.types.PropertyGroup):
        name = bpy.props.StringProperty()

    bpy.utils.register_module(__name__)

    bpy.types.Scene.albam_item_to_export = bpy.props.StringProperty()
    bpy.types.Scene.albam_items_imported = bpy.props.CollectionProperty(type=blender.AlbamImportedItemName)

    bpy.types.Object.albam_imported_item = bpy.props.PointerProperty(type=blender.AlbamImportedItem)

    for key, value in blender.ALBAM_MATERIAL_SETTINGS.items():
        setattr(bpy.types.Material, key, value)

    for key, value in blender.ALBAM_TEXTURE_SETTINGS.items():
        setattr(bpy.types.Texture, key, value)


def unregister():
    bpy.utils.unregister_module(__name__)
