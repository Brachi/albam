"""Blender's end of the glTF bridge: a Scene into Blender objects through
Blender's own glTF importer, and Blender objects back into a Scene through
its exporter. Everything game specific happens before or after this, on the
Scene; this module knows only glTF and bpy.
"""
import os
import tempfile

import bpy
import numpy as np

from .gltf import read_glb, write_glb
from .scene import EXTRAS_KEY, VERTEX_ATTRIBUTE

# Options for bpy.ops.import_scene.gltf. Ones a Blender version lacks are
# dropped, so the same call runs on every version albam supports.
IMPORT_OPTIONS = {
    # the file's normals as custom split normals, the way albam's own mesh
    # builder set them
    "import_shading": "NORMALS",
    # one Blender vertex per glTF vertex: a vertex the file splits at a seam
    # stays split, and comes back out as one vertex, so counts round-trip
    "merge_vertices": False,
    # bones from the joint nodes' own transforms, not from inverse bind
    # matrices; the scene writes both to agree
    "guess_original_bind_pose": False,
    # rest matrix = node matrix, the inverse of what the exporter does
    "bone_heuristic": "BLENDER",
    # the BLENDER heuristic otherwise adds a mesh object per armature for
    # the bone display shape, which would count as an imported mesh
    "disable_bone_shape": True,
    "import_pack_images": False,
    "import_scene_as_collection": False,
    "import_select_created_objects": False,
    # errors only
    "loglevel": 40,
}

# Options for bpy.ops.export_scene.gltf, same rule.
EXPORT_OPTIONS = {
    "export_format": "GLB",
    "use_selection": True,
    "use_visible": False,
    "export_apply": False,
    "export_yup": True,
    "export_extras": True,
    "export_normals": True,
    "export_tangents": True,
    "export_texcoords": True,
    # every mesh attribute whose name starts with "_"
    "export_attributes": True,
    "export_skins": True,
    "export_all_influences": True,
    "export_def_bones": False,
    "export_rest_position_armature": True,
    "export_hierarchy_flatten_bones": False,
    "export_hierarchy_flatten_objs": False,
    "export_animations": False,
    "export_morph": False,
    "export_lights": False,
    "export_cameras": False,
    "export_materials": "EXPORT",
    "export_image_format": "NONE",
    "export_unused_images": False,
    "export_unused_textures": False,
    "export_vertex_color": "ACTIVE",
    "export_all_vertex_colors": False,
    "export_active_vertex_color_when_no_material": True,
    "export_shared_accessors": False,
    "export_try_sparse_sk": False,
}


def _supported(operator, options):
    names = {prop.identifier for prop in operator.get_rna_type().properties}
    return {name: value for name, value in options.items() if name in names}


def import_scene(scene, include_materials=False):
    """Create the scene's objects in the current Blender scene and return
    them, the new objects only, in creation order.

    Node extras land as ID custom properties the way Blender's importer
    leaves them; callers that read them should remove them afterwards so
    the scene holds one copy of each value.
    """
    before = set(bpy.data.objects)
    glb = write_glb(scene, include_materials=include_materials)
    fd, path = tempfile.mkstemp(suffix=".glb")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(glb)
        if bpy.context.mode != "OBJECT" and bpy.context.active_object:
            bpy.ops.object.mode_set(mode="OBJECT")
        result = bpy.ops.import_scene.gltf(
            filepath=path, **_supported(bpy.ops.import_scene.gltf, IMPORT_OPTIONS))
    finally:
        os.remove(path)
    if result != {"FINISHED"}:
        raise RuntimeError(f"Blender's glTF importer returned {result}")
    return [ob for ob in bpy.data.objects if ob not in before]


def export_objects(objects):
    """The Scene Blender's glTF exporter makes of `objects` (which have to
    be in the view layer, so they can be selected).

    Every exported vertex carries the index of the Blender vertex it came
    from in the VERTEX_ATTRIBUTE attribute. The exporter makes one vertex
    per distinct set of corner attributes, and Blender's custom normals
    come back from storage a little different per corner, so a vertex that
    was one in the file comes out as several; with the index along, a writer
    can merge them back the way albam's own vertex table did.
    """
    if bpy.context.mode != "OBJECT" and bpy.context.active_object:
        bpy.ops.object.mode_set(mode="OBJECT")
    previous_selection = [ob for ob in bpy.context.view_layer.objects if ob.select_get()]
    previous_active = bpy.context.view_layer.objects.active
    fd, path = tempfile.mkstemp(suffix=".glb")
    os.close(fd)
    tagged = []
    try:
        for ob in objects:
            if ob.type == "MESH" and VERTEX_ATTRIBUTE not in ob.data.attributes:
                attribute = ob.data.attributes.new(VERTEX_ATTRIBUTE, "FLOAT", "POINT")
                attribute.data.foreach_set("value", np.arange(len(ob.data.vertices), dtype=np.float32))
                tagged.append(ob.data)
        for ob in bpy.context.view_layer.objects:
            ob.select_set(False)
        for ob in objects:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        result = bpy.ops.export_scene.gltf(
            filepath=path, **_supported(bpy.ops.export_scene.gltf, EXPORT_OPTIONS))
        if result != {"FINISHED"}:
            raise RuntimeError(f"Blender's glTF exporter returned {result}")
        with open(path, "rb") as f:
            scene = read_glb(f.read())
    finally:
        os.remove(path)
        for bl_mesh in tagged:
            attribute = bl_mesh.attributes.get(VERTEX_ATTRIBUTE)
            if attribute is not None:
                bl_mesh.attributes.remove(attribute)
        for ob in bpy.context.view_layer.objects:
            ob.select_set(ob in previous_selection)
        bpy.context.view_layer.objects.active = previous_active
    return scene


def pop_extras(id_data):
    """Remove and return the ALBAM extras Blender's importer stored on an ID
    (object, mesh, bone) as a custom property.

    Blender keeps a JSON object as a property group, except when a value
    does not fit an ID property (an int past 32 bits, say), in which case
    the importer stores the whole object as its Python repr; that comes
    back empty here, so only small, flat extras can be read this way. A
    caller with more to say puts an index in the extras and keeps the rest
    on its own Scene.
    """
    if id_data is None or EXTRAS_KEY not in id_data.keys():
        return {}
    value = id_data[EXTRAS_KEY]
    if isinstance(value, str):
        extras = {}
    else:
        extras = value.to_dict() if hasattr(value, "to_dict") else dict(value)
    del id_data[EXTRAS_KEY]
    return extras
