import importlib
import os
import sys

import bpy

from .blender_ui.data import AlbamDataFactory
from .blender_ui.asset import AlbamAsset
from .blender_ui.custom_properties import AlbamCustomPropertiesFactory
from .data_loading import populate_albam_data
from .lib import fs_registry
from .registry import blender_registry
from .__version__ import __version__ as version

__version__ = version


ALBAM_DIR = os.path.dirname(__file__)
VENDOR_DIR = os.path.join(ALBAM_DIR, "albam_vendor")

# AlbamCustomPropertiesFactory() builds these fresh on every register() call
# (unlike blender_registry.props/.types, which are only populated once, at
# module import time, by decorators). They're not tracked anywhere else, so
# unregister() needs its own reference to tear them down symmetrically.
_CUSTOM_PROPERTIES_CLASSES = []


def register():
    sys.path.insert(0, VENDOR_DIR)
    # Load registered functions into the blender_registry
    importlib.import_module(".blender_ui.import_panel", __package__)
    importlib.import_module(".blender_ui.export_panel", __package__)
    importlib.import_module(".engines.mtfw.animation", __package__)
    importlib.import_module(".engines.mtfw.collision", __package__)
    importlib.import_module(".engines.mtfw.archive", __package__)
    importlib.import_module(".engines.mtfw.mesh", __package__)
    importlib.import_module(".engines.mtfw.navmesh", __package__)
    if os.getenv("ALBAM_ENABLE_REEN"):
        importlib.import_module(".engines.reng.archive", __package__)
        importlib.import_module(".engines.reng.mesh", __package__)
        importlib.import_module(".engines.reng.texture", __package__)

    for _, cls in blender_registry.props:
        bpy.utils.register_class(cls)

    for cls in blender_registry.types:
        bpy.utils.register_class(cls)

    AlbamData = AlbamDataFactory()
    AlbamCustomPropertiesMaterial = AlbamCustomPropertiesFactory("material")
    AlbamCustomPropertiesMesh = AlbamCustomPropertiesFactory("mesh")
    AlbamCustomPropertiesImage = AlbamCustomPropertiesFactory("image")
    AlbamCustomPropertiesObject = AlbamCustomPropertiesFactory("object")
    bpy.utils.register_class(AlbamData)
    _CUSTOM_PROPERTIES_CLASSES[:] = [
        AlbamCustomPropertiesMaterial,
        AlbamCustomPropertiesMesh,
        AlbamCustomPropertiesImage,
        AlbamCustomPropertiesObject,
    ]
    for cls in _CUSTOM_PROPERTIES_CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.albam = bpy.props.PointerProperty(type=AlbamData)

    bpy.types.Object.albam_asset = bpy.props.PointerProperty(type=AlbamAsset)
    bpy.types.Image.albam_asset = bpy.props.PointerProperty(type=AlbamAsset)

    bpy.types.Material.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesMaterial)
    bpy.types.Mesh.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesMesh)
    bpy.types.Image.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesImage)
    bpy.types.Object.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesObject)

    # Load data from user's config files
    bpy.app.handlers.load_post.append(populate_albam_data)


def unregister():
    fs_registry.clear()

    for _, cls in reversed(blender_registry.props):
        bpy.utils.unregister_class(cls)

    for cls in reversed(blender_registry.types):
        bpy.utils.unregister_class(cls)

    for cls in reversed(_CUSTOM_PROPERTIES_CLASSES):
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(type(bpy.context.scene.albam))

    sys.path.remove(VENDOR_DIR)
