import importlib
import os
import sys

import bpy

from albam.blender_ui.data import AlbamDataFactory
from albam.registry import blender_registry


bl_info = {
    "name": "Albam",
    "author": "Sebastian A. Brachi",
    "version": (0, 3, 6),
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
    bpy.utils.register_class(AlbamData)
    bpy.types.Scene.albam = bpy.props.PointerProperty(type=AlbamData)


def unregister():
    for _, cls in reversed(blender_registry.props):
        bpy.utils.unregister_class(cls)

    for cls in reversed(blender_registry.types):
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(type(bpy.context.scene.albam))

    sys.path.remove(VENDOR_DIR)
