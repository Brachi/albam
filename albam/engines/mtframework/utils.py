import ctypes
from collections import Counter
import ntpath

from albam.exceptions import BuildMeshError
from albam.engines.mtframework.mod_156 import (
    VERTEX_FORMATS_TO_CLASSES,
    )
from albam.lib.structure import get_size


def get_vertices_array(mod, mesh):
    try:
        VF = VERTEX_FORMATS_TO_CLASSES[mesh.vertex_format]
    except KeyError:
        raise TypeError('Unrecognized vertex format: {}'.format(hex(mesh.vertex_format)))
    if mod.version == 156:
        position = max(mesh.vertex_index_start_1, mesh.vertex_index_start_2) * mesh.vertex_stride
        if mesh.vertex_index_start_2 > mesh.vertex_index_start_1:
            vertex_count = mesh.vertex_index_end - mesh.vertex_index_start_2 + 1
            # TODO: research the content of mesh.vertex_index_start_1 and what it means in this case
            # So far it looks it contains only garbage; all vertices have the same values.
            # It's unknown why they exist for, and why they count for mesh.vertex_count
            # The imported meshes here will have a different mesh count than the original.
        else:
            vertex_count = mesh.vertex_count
    elif mod.version == 210:
        position = mesh.vertex_index * ctypes.sizeof(VF)
        vertex_count = mesh.vertex_count
    else:
        raise TypeError('Unsupported mod version: {}'.format(mod.version))
    offset = ctypes.addressof(mod.vertex_buffer)
    offset += mesh.vertex_offset
    offset += position
    return (VF * vertex_count).from_address(offset)


def get_indices_array(mod, mesh):
    offset = ctypes.addressof(mod.index_buffer)
    position = mesh.face_offset * 2 + mesh.face_position * 2
    index_buffer_size = get_size(mod, 'index_buffer')
    if position > index_buffer_size:
        raise BuildMeshError('Error building mesh in get_indices_array (out of bounds reference)'
                             'Size of mod.indices_buffer: {} mesh.face_offset: {}, mesh.face_position: {}'
                             .format(index_buffer_size, mesh.face_offset, mesh.face_position))
    offset += position
    return (ctypes.c_ushort * mesh.face_count).from_address(offset)


def vertices_export_locations(xyz_tuple, bounding_box_width, bounding_box_height, bounding_box_length):
    x, y, z = xyz_tuple

    x += bounding_box_width / 2
    try:
        x /= bounding_box_width
    except ZeroDivisionError:
        pass
    if x > 1.0:
        x = 32767
    else:
        x *= 32767

    try:
        y /= bounding_box_height
    except ZeroDivisionError:
        pass
    if y > 1.0:
        y = 32767
    else:
        y *= 32767

    z += bounding_box_length / 2
    try:
        z /= bounding_box_length
    except ZeroDivisionError:
        pass
    if z > 1.0:
        z = 32767
    else:
        z *= 32767

    return (round(x), round(y), round(z))


def transform_vertices_from_bbox(vertex_format, bounding_box_width, bounding_box_height, bounding_box_length):
    x = vertex_format.position_x
    y = vertex_format.position_y
    z = vertex_format.position_z

    x *= bounding_box_width
    x /= 32767
    x -= bounding_box_width / 2

    y *= bounding_box_height
    y /= 32767

    z *= bounding_box_length
    z /= 32767
    z -= bounding_box_length / 2

    return (x, y, z)


def get_bone_parents_from_mod(bone, bones_array):
    parents = []
    parent_index = bone.parent_index
    child_bone = bone
    if parent_index != 255:
        parents.append(parent_index)
    while parent_index != 255:
        child_bone = bones_array[child_bone.parent_index]
        parent_index = child_bone.parent_index
        if parent_index != 255:
            parents.append(parent_index)
    return parents


def texture_code_to_blender_texture(texture_code, blender_texture_slot, blender_material):
    blender_texture_slot.use_map_alpha = True
    if texture_code == 0:
        # Diffuse
        blender_texture_slot.use_map_color_diffuse = True
    elif texture_code == 1:
        # Normal
        blender_texture_slot.use_map_color_diffuse = False
        blender_texture_slot.use_map_normal = True
        blender_texture_slot.normal_factor = 0.05
    elif texture_code == 2:
        # Specular
        blender_texture_slot.use_map_color_diffuse = False
        blender_texture_slot.use_map_specular = True
        blender_material.specular_intensity = 0.0
    elif texture_code == 7:
        # cube map normal
        blender_texture_slot.use_map_color_diffuse = False
        blender_texture_slot.use_map_normal = True
        blender_texture_slot.normal_factor = 0.05
        blender_texture_slot.texture_coords = 'GLOBAL'
        blender_texture_slot.mapping = 'CUBE'
    else:
        print('texture_code not supported', texture_code)
        blender_texture_slot.use_map_color_diffuse = False
        # TODO: 3, 4, 5, 6,


def blender_texture_to_texture_code(blender_texture_slot):
    texture_code = 0

    # Diffuse
    if blender_texture_slot.use_map_color_diffuse:
        texture_code = 0

    # Normal
    elif blender_texture_slot.use_map_normal and blender_texture_slot.texture_coords == 'UV':
        texture_code = 1

    # Specular
    elif blender_texture_slot.use_map_specular:
        texture_code = 2

    # Cube normal
    elif (blender_texture_slot.use_map_normal and
          blender_texture_slot.texture_coords == 'GLOBAL' and
          blender_texture_slot.mapping == 'CUBE'):
        texture_code = 7

    return texture_code


def get_texture_dirs(mod):
    """Returns a dict of <texture_name>: <texture_dir>"""
    texture_dirs = {}
    for texture_path in mod.textures_array:
        texture_path = texture_path[:].decode('ascii').partition('\x00')[0]
        texture_dir, texture_name_no_ext = ntpath.split(texture_path)
        texture_dirs[texture_name_no_ext] = texture_dir
    return texture_dirs


def get_default_texture_dir(mod):
    if not mod.textures_array:
        return None
    texture_dirs = []
    for texture_path in mod.textures_array:
        texture_path = texture_path[:].decode('ascii').partition('\x00')[0]
        texture_dir = ntpath.split(texture_path)[0]
        texture_dirs.append(texture_dir)

    return Counter(texture_dirs).most_common(1)[0][0]
