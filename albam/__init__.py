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

    class AlbamImportedItemName(bpy.types.PropertyGroup):
        '''All imported object names are saved here to then show them in the
        export list'''
        name = bpy.props.StringProperty(name="Imported Item", default="Unknown")

    class AlbamImportedItem(bpy.types.PropertyGroup):
        name = bpy.props.StringProperty(options={'HIDDEN'})
        source_path = bpy.props.StringProperty(options={'HIDDEN'})
        folder = bpy.props.StringProperty(options={'HIDDEN'})  # Always in posix format
        data = bpy.props.StringProperty(options={'HIDDEN'}, subtype='BYTE_STRING')
        file_type = bpy.props.StringProperty(options={'HIDDEN'})

    bpy.utils.register_module(__name__)
    bpy.types.Scene.albam_item_to_export = bpy.props.StringProperty()
    bpy.types.Scene.albam_items_imported = bpy.props.CollectionProperty(type=AlbamImportedItemName)

    bpy.types.Object.albam_imported_item = bpy.props.PointerProperty(type=AlbamImportedItem)

    # Not using PointerProperty/PropertyGroup since they are not editable from the UI
    # TODO: look if that can be added into blender
    bpy.types.Texture.albam_imported_texture_type = bpy.props.IntProperty(options={'HIDDEN'})
    bpy.types.Texture.albam_imported_texture_folder = bpy.props.StringProperty()
    bpy.types.Texture.albam_imported_texture_value_1 = bpy.props.FloatProperty()
    bpy.types.Texture.albam_imported_texture_value_2 = bpy.props.FloatProperty()
    bpy.types.Texture.albam_imported_texture_value_3 = bpy.props.FloatProperty()
    bpy.types.Texture.albam_imported_texture_value_4 = bpy.props.FloatProperty()


def unregister():
    bpy.utils.unregister_module(__name__)
