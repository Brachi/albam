import bpy

from albam.registry import blender_registry
from albam.apps import APPS


@blender_registry.register_blender_prop
class AlbamAsset(bpy.types.PropertyGroup):
    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    original_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821
    relative_path: bpy.props.StringProperty()
    extension: bpy.props.StringProperty()


@blender_registry.register_blender_type
class ALBAM_PT_AssetObject(bpy.types.Panel):
    bl_label = "Albam Asset"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):  # pragma: no cover
        obj = context.object
        self.layout.row().prop(obj.albam_asset, "app_id")
        self.layout.row().prop(obj.albam_asset, "relative_path")

    @classmethod
    def poll(cls, context):  # pragma: no cover
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
