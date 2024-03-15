import bpy

from albam.registry import blender_registry

def AlbamDataFactory():

    def create_data():
        data = {}
        for name, cls in blender_registry.props:
            if not name:
                continue
            data[name] = bpy.props.PointerProperty(type=cls)
        return data

    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    return type(
        'AlbamData',
        (bpy.types.PropertyGroup, ),
        {'__annotations__' : create_data()}

    )
