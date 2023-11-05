import bpy

from albam.registry import blender_registry
from .import_panel import APPS


@blender_registry.register_blender_prop
class AlbamAsset(bpy.types.PropertyGroup):
    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    original_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821
    relative_path : bpy.props.StringProperty()
    extension: bpy.props.StringProperty()


def create_data():
    data = {}
    for name, cls in blender_registry.props:
        if not name:
            continue
        data[name] = bpy.props.PointerProperty(type=cls)
    return data


def create_data_custom_properties(registry_name):
    data = {}
    appid_map = {}
    registry = getattr(blender_registry, registry_name)
    for name, (cls, app_ids) in registry.items():
        data[name] = bpy.props.PointerProperty(type=cls)
        appid_map.update({app_id: name for app_id in app_ids})
    return data, appid_map


def AlbamDataFactory():
    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    return type(
        'AlbamData',
        (bpy.types.PropertyGroup, ),
        {'__annotations__' : create_data()}

    )


def get_appid_custom_properties(self, app_id):
    # TODO: error handling
    property_name = self.APPID_MAP[app_id]
    return getattr(self, property_name)


def AlbamCustomPropertiesMaterialFactory():
    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    data, appid_map = create_data_custom_properties("custom_properties_material")

    return type(
        'AlbamCustomPropertyMaterial',
        (bpy.types.PropertyGroup, ),
        {
            '__annotations__' : data,
            'APPID_MAP': appid_map,
            "get_appid_custom_properties": get_appid_custom_properties,
        }
    )


def AlbamCustomPropertiesMeshFactory():
    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    data, appid_map = create_data_custom_properties("custom_properties_mesh")

    return type(
        'AlbamCustomPropertyMesh',
        (bpy.types.PropertyGroup, ),
        {
            '__annotations__' : data,
            'APPID_MAP': appid_map,
            "get_appid_custom_properties": get_appid_custom_properties,
        }
    )


def AlbamCustomPropertiesImageFactory():
    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    data, appid_map = create_data_custom_properties("custom_properties_image")

    return type(
        'AlbamCustomPropertyImage',
        (bpy.types.PropertyGroup, ),
        {
            '__annotations__' : data,
            'APPID_MAP': appid_map,
            "get_appid_custom_properties": get_appid_custom_properties,
        }
    )
