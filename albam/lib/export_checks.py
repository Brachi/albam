import functools

import bpy

from ..exceptions import AlbamCheckFailure


def check_all_objects_have_materials(func):
    """
    Function decorator that checks if all the meshes of a bl_object
    have at least one material.
    The function to be decorated needs the bl_object to be checked to be in the list of args
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bl_objects = [a for a in args if isinstance(a, bpy.types.Object)]
        if not bl_objects:
            result = func(*args, **kwargs)
        # No more than one root object in export functions
        meshes = [c for c in bl_objects[0].children_recursive if c.type == "MESH"]
        meshes_no_materials = [me_ob for me_ob in meshes if not me_ob.data.materials or
                               me_ob.data.materials[0] is None]
        if meshes_no_materials:
            data = sorted(me_ob.name for me_ob in meshes_no_materials)
            raise AlbamCheckFailure(
                "Some meshes have no materials",
                details=f"Meshes: {data}",
                solution="Add one material to the list of meshes listed above")
        result = func(*args, **kwargs)

        return result
    return wrapper
