from albam import blender   # noqa , used by register_module

try:
    import bpy
except ImportError:
    pass

import albam.mtframework.blender_import  # noqa
import albam.mtframework.blender_export  # noqa
from albam.registry import blender_registry


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

    # workaround for error running tests: 'module albam defines no classes'
    class Dummy(bpy.types.PropertyGroup):
        name = bpy.props.StringProperty()

    # Setting custom material properties
    for prop_name, prop_cls_name in blender_registry.bpy_props.get('material', []):
        prop_cls = getattr(bpy.props, prop_cls_name)
        prop_instance = prop_cls()
        setattr(bpy.types.Material, prop_name, prop_instance)

    # Setting custom texture properties
    for prop_name, prop_cls_name in blender_registry.bpy_props.get('texture', []):
        prop_cls = getattr(bpy.props, prop_cls_name)
        prop_instance = prop_cls()
        setattr(bpy.types.Texture, prop_name, prop_instance)

    # Setting custom mesh properties
    for prop_name, prop_cls_name in blender_registry.bpy_props.get('mesh', []):
        prop_cls = getattr(bpy.props, prop_cls_name)
        prop_instance = prop_cls()
        setattr(bpy.types.Mesh, prop_name, prop_instance)

    bpy.utils.register_module(__name__)

    bpy.types.Scene.albam_item_to_export = bpy.props.StringProperty()
    bpy.types.Scene.albam_items_imported = bpy.props.CollectionProperty(type=blender.AlbamImportedItemName)

    bpy.types.Object.albam_imported_item = bpy.props.PointerProperty(type=blender.AlbamImportedItem)


def unregister():
    bpy.utils.unregister_module(__name__)
