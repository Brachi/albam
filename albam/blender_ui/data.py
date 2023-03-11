import bpy

from albam.registry import blender_registry


def create_data():
    data = {}
    for name, cls in blender_registry.props:
        if not name:
            continue
        data[name] = bpy.props.PointerProperty(type=cls)
    return data


def AlbamDataFactory():
    return type(
        'AlbamData',
        (bpy.types.PropertyGroup, ),
        {'__annotations__' : create_data()}

    )
