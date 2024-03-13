import importlib
import os
import sys

import bpy

from albam.blender_ui.data import (
    AlbamDataFactory,
    AlbamAsset,
    AlbamCustomPropertiesMaterialFactory,
    AlbamCustomPropertiesMeshFactory,
    AlbamCustomPropertiesImageFactory,
)
from albam.registry import blender_registry
from albam.__version__ import __version__
from albam.blender_ui.custom_properties import CopyPasterBuff

bl_info = {
    "name": "Albam",
    "author": "Sebastian A. Brachi",
    "version": tuple(__version__.split(".")),
    "blender": (2, 80, 0),
    "location": "Properties Panel",
    "description": "Import-Export multiple video-game formats",
    "category": "Import-Export",
}

ALBAM_DIR = os.path.dirname(__file__)
VENDOR_DIR = os.path.join(ALBAM_DIR, "albam_vendor")


def register():
    sys.path.insert(0, VENDOR_DIR)
    # Load registered functions into the blender_registry
    importlib.import_module("albam.blender_ui.import_panel")
    importlib.import_module("albam.blender_ui.export_panel")
    importlib.import_module("albam.engines.mtfw.animation")
    importlib.import_module("albam.engines.mtfw.archive")
    importlib.import_module("albam.engines.mtfw.mesh")
    if os.getenv("ALBAM_ENABLE_REEN"):
        importlib.import_module("albam.engines.reng.archive")
        importlib.import_module("albam.engines.reng.mesh")
        importlib.import_module("albam.engines.reng.texture")

    for _, cls in blender_registry.props:
        bpy.utils.register_class(cls)

    for cls in blender_registry.types:
        bpy.utils.register_class(cls)

    AlbamData = AlbamDataFactory()
    AlbamCustomPropertiesMaterial = AlbamCustomPropertiesMaterialFactory()
    AlbamCustomPropertiesMesh = AlbamCustomPropertiesMeshFactory()
    AlbamCustomPropertiesImage = AlbamCustomPropertiesImageFactory()
    bpy.utils.register_class(AlbamData)
    bpy.utils.register_class(AlbamCustomPropertiesMaterial)
    bpy.utils.register_class(AlbamCustomPropertiesMesh)
    bpy.utils.register_class(AlbamCustomPropertiesImage)

    bpy.types.Scene.albam = bpy.props.PointerProperty(type=AlbamData)
    bpy.types.Scene.albam_copypaster = bpy.props.PointerProperty(type=CopyPasterBuff)
    bpy.types.Object.albam_asset = bpy.props.PointerProperty(type=AlbamAsset)
    bpy.types.Image.albam_asset = bpy.props.PointerProperty(type=AlbamAsset)

    bpy.types.Material.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesMaterial)
    bpy.types.Mesh.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesMesh)
    bpy.types.Image.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesImage)


def unregister():
    for _, cls in reversed(blender_registry.props):
        bpy.utils.unregister_class(cls)

    for cls in reversed(blender_registry.types):
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(type(bpy.context.scene.albam))

    sys.path.remove(VENDOR_DIR)
