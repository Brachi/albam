import ctypes

from albam.exceptions import BuildMeshError
from albam.mtframework.mod import (
    VERTEX_FORMATS_TO_CLASSES,
    )
from albam.utils import (
    get_size,
    )


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
    x *= 32767

    try:
        y /= bounding_box_height
    except ZeroDivisionError:
        pass
    y *= 32767

    z += bounding_box_length / 2
    try:
        z /= bounding_box_length
    except ZeroDivisionError:
        pass
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
