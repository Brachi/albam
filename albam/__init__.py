import importlib
import os
import sys

import bpy

from .blender_ui.data import AlbamDataFactory
from .blender_ui.asset import AlbamAsset
from .blender_ui.custom_properties import AlbamCustomPropertiesFactory
from .registry import blender_registry
from .__version__ import __version__ as version

__version__ = version


bl_info = {
    "name": "Albam",
    "author": "Sebastian Aguirre Brachi",
    "version": (0, 5, 0),  # needs to be kept in sync with __version__ manually
    "blender": (4, 2, 0),
    "location": "Properties Panel",
    "description": "Import-Export multiple video-game formats",
    "category": "Import-Export",
}

VENV_PATH = None


def register():

    if os.environ.get("BLENDER_DEV_MODE") == "1":
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        venv_path = os.path.abspath(os.path.join(
            addon_dir, "..", ".venv", "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages"))

        if os.path.exists(venv_path) and venv_path not in sys.path:
            VENV_PATH = venv_path
            sys.path.insert(0, venv_path)

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
    bpy.utils.register_class(AlbamCustomPropertiesMaterial)
    bpy.utils.register_class(AlbamCustomPropertiesMesh)
    bpy.utils.register_class(AlbamCustomPropertiesImage)
    bpy.utils.register_class(AlbamCustomPropertiesObject)

    bpy.types.Scene.albam = bpy.props.PointerProperty(type=AlbamData)

    bpy.types.Object.albam_asset = bpy.props.PointerProperty(type=AlbamAsset)
    bpy.types.Image.albam_asset = bpy.props.PointerProperty(type=AlbamAsset)

    bpy.types.Material.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesMaterial)
    bpy.types.Mesh.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesMesh)
    bpy.types.Image.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesImage)
    bpy.types.Object.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesObject)


def unregister():
    for _, cls in reversed(blender_registry.props):
        bpy.utils.unregister_class(cls)

    for cls in reversed(blender_registry.types):
        bpy.utils.unregister_class(cls)
    if VENV_PATH:
        sys.path.remove(VENV_PATH)

    bpy.utils.unregister_class(type(bpy.context.scene.albam))
