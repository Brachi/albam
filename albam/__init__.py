import importlib
import os

import bpy

from . import _pkg_resources_warning  # noqa: F401  (filters before `fs` is imported)
from .blender_ui.data import AlbamDataFactory
from .blender_ui.asset import AlbamAsset
from .blender_ui.custom_properties import AlbamCustomPropertiesFactory
from .data_loading import populate_albam_data
from .lib import fs_registry
from .registry import blender_registry
from .vfs import reconnect_fs_roots
from .__version__ import __version__ as version

__version__ = version


# AlbamCustomPropertiesFactory() builds these fresh on every register() call
# (unlike blender_registry.props/.types, which are only populated once, at
# module import time, by decorators). They're not tracked anywhere else, so
# unregister() needs its own reference to tear them down symmetrically.
_CUSTOM_PROPERTIES_CLASSES = []

# Functions appended to bpy.app.handlers.load_post by register(), tracked here
# so unregister() can remove exactly what was added - mirrors how
# blender_registry.props/types already track what to unregister.
# populate_albam_data loads data from the user's config files;
# reconnect_fs_roots rebuilds fs_registry's process-lifetime entries for VFS
# roots restored from the loaded .blend file.
LOAD_POST_HANDLERS = [populate_albam_data, reconnect_fs_roots]


def register():
    # Load registered functions into the blender_registry
    importlib.import_module(".blender_ui.import_panel", __package__)
    importlib.import_module(".blender_ui.export_panel", __package__)
    importlib.import_module(".engines.mtfw.animation", __package__)
    importlib.import_module(".engines.mtfw.collision", __package__)
    importlib.import_module(".engines.mtfw.archive", __package__)
    importlib.import_module(".engines.mtfw.mesh", __package__)
    importlib.import_module(".engines.mtfw.navmesh", __package__)
    importlib.import_module(".engines.cie.archive", __package__)
    importlib.import_module(".engines.cie.mesh", __package__)
    importlib.import_module(".engines.cie.scenario", __package__)
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
    AlbamCustomPropertiesBone = AlbamCustomPropertiesFactory("bone")
    bpy.utils.register_class(AlbamData)
    _CUSTOM_PROPERTIES_CLASSES[:] = [
        AlbamCustomPropertiesMaterial,
        AlbamCustomPropertiesMesh,
        AlbamCustomPropertiesImage,
        AlbamCustomPropertiesObject,
        AlbamCustomPropertiesBone,
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
    # PoseBone, not Bone: see BlenderRegistry.register_custom_properties_bone
    bpy.types.PoseBone.albam_custom_properties = bpy.props.PointerProperty(type=AlbamCustomPropertiesBone)

    for handler in LOAD_POST_HANDLERS:
        bpy.app.handlers.load_post.append(handler)


def unregister():
    for handler in LOAD_POST_HANDLERS:
        try:
            bpy.app.handlers.load_post.remove(handler)
        except ValueError:
            pass  # already removed, e.g. a previous unregister() call

    fs_registry.clear()

    for _, cls in reversed(blender_registry.props):
        bpy.utils.unregister_class(cls)

    for cls in reversed(blender_registry.types):
        bpy.utils.unregister_class(cls)

    for cls in reversed(_CUSTOM_PROPERTIES_CLASSES):
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(type(bpy.context.scene.albam))
