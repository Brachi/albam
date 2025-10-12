from enum import Enum

import bpy

from ..registry import blender_registry
from ..apps import APPS


class AlbamAssetType(Enum):
    MODEL = "Model"
    TEXTURE = "Texture"
    ANIMATION = "Animation Bank"
    COLLISION = "Collision"
    MATERIAL = "Material"


# Avoid generating dynamically per Blender issues
ASSET_TYPES_BL_ENUM = [
    ('NONE', "None", "No AlbamAssetType defined", 0),
    (AlbamAssetType.MODEL.name, AlbamAssetType.MODEL.value , "", 1),
    (AlbamAssetType.TEXTURE.name, AlbamAssetType.TEXTURE.value , "", 2),
    (AlbamAssetType.ANIMATION.name, AlbamAssetType.ANIMATION.value , "", 3),
    (AlbamAssetType.COLLISION.name, AlbamAssetType.COLLISION.value , "", 4),
    (AlbamAssetType.MATERIAL.name, AlbamAssetType.MATERIAL.value , "", 5),
]


@blender_registry.register_blender_prop
class AlbamAsset(bpy.types.PropertyGroup):
    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    original_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821
    relative_path: bpy.props.StringProperty()
    extension: bpy.props.StringProperty()
    asset_type: bpy.props.EnumProperty(name="", description="", items=ASSET_TYPES_BL_ENUM, default=None)


@blender_registry.register_blender_type
class ALBAM_PT_AssetObject(bpy.types.Panel):
    bl_label = "Albam Asset"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):  # pragma: no cover
        obj = context.object
        row_1 = self.layout.row()
        row_1.prop(obj.albam_asset, "app_id", text="App")
        row_1.enabled = False
        row_2 = self.layout.row()
        row_2.prop(obj.albam_asset, "relative_path", text="Relative Path")
        row_2.enabled = False
        row_3 = self.layout.row()
        row_3.prop(obj.albam_asset, "asset_type", text="Asset Type")
        row_3.enabled = False

    @classmethod
    def poll(cls, context):  # pragma: no cover
        # Only display if the object it's an albam asset
        # relative_path is not user editable and only
        # filled at import time
        obj = context.object
        return obj and obj.albam_asset.relative_path


@blender_registry.register_blender_type
class ALBAM_PT_AssetImage(bpy.types.Panel):
    bl_label = "Albam Asset"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Albam"  # TODO: global option to hide it by default

    def draw(self, context):  # pragma: no cover
        im = context.space_data.image

        self.layout.row().prop(im.albam_asset, "app_id")
        self.layout.row().prop(im.albam_asset, "relative_path")

        app_id = im.albam_asset.app_id
        custom_props = im.albam_custom_properties.get_custom_properties_for_appid(app_id)
        for k in custom_props.__annotations__:
            self.layout.prop(custom_props, k)

    @classmethod
    def poll(cls, context):  # pragma: no cover
        return bool(context.space_data.image)
