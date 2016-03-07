import binascii
from collections import namedtuple, deque, OrderedDict
from copy import copy
import ctypes
from ctypes import c_float
import os
import struct


def get_offset(struct_ob, name):
    return getattr(struct_ob.__class__, name).offset


def get_size(struct_ob, name):
    return getattr(struct_ob.__class__, name).size


def print_structure(ctypes_structure_ob):
    for attr_tuple in ctypes_structure_ob._fields_:
        attr_name = attr_tuple[0]
        attr_type = attr_tuple[1]
        attr_value = getattr(ctypes_structure_ob, attr_name)
        attr_desc = str(getattr(ctypes_structure_ob.__class__, attr_name))

        pretty_attr_value = attr_value
        try:
            pretty_attr_value = str(bytearray().extend(*list(copy(attr_value))))
        except TypeError:
            pass

        if not isinstance(pretty_attr_value, bytes):
            try:
                # TODO: speed this up, too many copies
                pretty_attr_value = str(list(copy(attr_value))[:5])
            except TypeError:
                pass
        try:
            if attr_type == c_float:
                template = '{:<20} -- {:<20.2f} {}'
            else:
                template = '{:<20} -- {:<20} {}'
            out = template.format(attr_name, pretty_attr_value, attr_desc)
            print(out)
        except Exception as err:
            print('error printint struct: "{}"'.format(attr_name), err)


def as_dict(obj):
    obj_type = type(obj)

    if issubclass(obj_type, ctypes.Array):
        if type(obj[:]) == bytes:
            return obj[:].decode('ascii')
        return [as_dict(item) for item in obj]

    elif issubclass(obj_type, ctypes.Structure):
        final = OrderedDict()
        for attr_tuple in obj._fields_:
            attr_name = attr_tuple[0]
            attr_type = attr_tuple[1]
            attr_value = getattr(obj, attr_name)
            value_type = type(attr_value)
            final_value = attr_value
            if issubclass(value_type, ctypes.Array):
                # Improve this?
                if type(attr_value[:]) == bytes:
                    final_value = attr_value[:]
                else:
                    final_value = [as_dict(item) for item in attr_value]
            try:
                final[attr_name] = final_value.decode('ascii')
            except AttributeError:
                final[attr_name] = final_value
        return final
    else:
        return obj



def parse_fields(sequence_of_tuples, file_path_or_buffer=None, **kwargs):
    ready_fields = []
    try:
        os.path.isfile(file_path_or_buffer)
        is_file = True
        buff = open(file_path_or_buffer, 'rb')
    except TypeError:
        buff = file_path_or_buffer
        is_file = False

    for t in sequence_of_tuples:
        attr_name = t[0]
        ctype_or_callable = t[1]
        try:
            ctypes.sizeof(ctype_or_callable)
            ready_fields.append(t)
        except TypeError:
            class TmpStruct(ctypes.Structure):
                _fields_ = ready_fields
                _pack_ = 1
            if buff:
                tmp_struct = TmpStruct()
                buff.readinto(tmp_struct)
                buff.seek(0)
            else:
                tmp_struct = TmpStruct(**kwargs)
            try:
                c_type = ctype_or_callable(tmp_struct)
            except TypeError:
                c_type = ctype_or_callable(tmp_struct, file_path_or_buffer)

            ready_fields.append((attr_name, c_type))

    if file_path_or_buffer and is_file:
        buff.close()

    return tuple(ready_fields)


class BaseStructure:

    _fields_ = None

    # TODO: change signature to make it clear that 'file_path' can be also a buffer
    def __new__(cls, file_path=None, *args, **kwargs):
        cls_dict = {'_pack_': 1}
        for k, v in cls.__dict__.items():
            if k != '_fields_':
                cls_dict[k] = v

        cls_dict['_fields_'] = parse_fields(cls._fields_, file_path, **kwargs)
        try:
            generated_cls = type('Gen{}'.format(cls.__name__), (ctypes.Structure,), cls_dict)
        except TypeError:
            raise RuntimeError('Error generating class. Fields: {}'.format(cls_dict['_fields_']))

        if file_path:
            instance = generated_cls()
            try:
                with open(file_path, 'rb') as f:
                    f.readinto(instance)
            except TypeError:
                file_path.readinto(instance)
                file_path.close()
        else:
            instance = generated_cls(**kwargs)

        return instance


def unpack_half_float(float16):
    # A function useful to read half-float (used in the uv coords), not supported by the struct module
    # http://davidejones.com/blog/1413-python-precision-floating-point/

    # TODO: check limitations on the input and raise exceptions
    # http://read.pudn.com/downloads95/sourcecode/graph/385756/1/BaseLib/float16.h__.htm
    # https://en.wikipedia.org/wiki/Half-precision_floating-point_format
    s = int((float16 >> 15) & 0x00000001)  # sign
    e = int((float16 >> 10) & 0x0000001f)  # exponent
    f = int(float16 & 0x000003ff)  # fraction
    if e == 0:
        if f == 0:
            return float(s << 31)
        else:
            while not (f & 0x00000400):
                f = f << 1
                e -= 1
            e += 1
            f &= ~0x00000400
    elif e == 31:
        if f == 0:
            return int((s << 31) | 0x7f800000)
        else:
            return int((s << 31) | 0x7f800000 | (f << 13))
    e = e + (127 - 15)
    f = f << 13
    short_int = int((s << 31) | (e << 23) | f)
    return struct.unpack('f', struct.pack('I', short_int))[0]


def pack_half_float(float32):
    F16_EXPONENT_BITS = 0x1F
    F16_EXPONENT_SHIFT = 10
    F16_EXPONENT_BIAS = 15
    F16_MANTISSA_BITS = 0x3ff
    F16_MANTISSA_SHIFT = 23 - F16_EXPONENT_SHIFT
    F16_MAX_EXPONENT = (F16_EXPONENT_BITS << F16_EXPONENT_SHIFT)

    a = struct.pack('>f', float32)
    b = binascii.hexlify(a)

    f32 = int(b, 16)
    f16 = 0
    sign = (f32 >> 16) & 0x8000
    exponent = ((f32 >> 23) & 0xff) - 127
    mantissa = f32 & 0x007fffff

    if exponent == 128:
        f16 = sign | F16_MAX_EXPONENT
        if mantissa:
            f16 |= (mantissa & F16_MANTISSA_BITS)
    elif exponent > 15:
        f16 = sign | F16_MAX_EXPONENT
    elif exponent > -15:
        exponent += F16_EXPONENT_BIAS
        mantissa >>= F16_MANTISSA_SHIFT
        f16 = sign | exponent << F16_EXPONENT_SHIFT | mantissa
    else:
        f16 = sign

    return f16


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def strip_triangles_to_triangles_list(strip_indices_array):
    indices = []
    offset = min(strip_indices_array[:3])

    for i in range(2, len(strip_indices_array)):
        a = strip_indices_array[i - 2]
        b = strip_indices_array[i - 1]
        c = strip_indices_array[i]
        if a != b and a != c and b != c:
            if i % 2 == 0:
                indices.extend((a - offset, b - offset, c - offset))
            else:
                indices.extend((c - offset, b - offset, a - offset))
    if not indices:
        return list(strip_indices_array)
    return indices


def y_up_to_z_up(x_y_z_tuple):
    x, y, z = x_y_z_tuple
    return x, z * -1, y


def z_up_to_y_up(x_y_z_tuple):
    x, y, z = x_y_z_tuple
    return x, z, y * -1


def get_bounding_box_positions_from_blender_objects(blender_objects):
    bounding_box = namedtuple('bounding_box', ('max_x', 'max_y', 'max_z', 'max_w',
                                               'min_x', 'min_y', 'min_z', 'min_w',))
    meshes = [ob.data for ob in blender_objects if ob.type == 'MESH']
    max_x = -99999999
    max_y = -99999999
    max_z = -99999999
    max_w = 0
    min_x = 99999999
    min_y = 99999999
    min_z = 99999999
    min_w = 0
    for mesh in meshes:
        for vert in mesh.vertices:
            x, y, z = vert.co
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if z > max_z:
                max_z = z
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if z < min_z:
                min_z = z
    return bounding_box(max_x, max_y, max_z, max_w, min_x, min_y, min_z, min_w)


def create_mesh_name(mesh, index, file_path):
    return '{}_{}_LOD_{}'.format(os.path.basename(file_path),
                                 str(index).zfill(4),
                                 mesh.level_of_detail)


def get_bone_count_from_blender_objects(blender_objects):
    bone_count = 0
    for ob in blender_objects:
        if ob.type == 'ARMATURE':
            bone_count += len(ob.data.bones)
    return bone_count


def get_textures_from_blender_objects(blender_objects):
    """
    Only counting the first material of the mesh
    """
    textures = set()
    meshes = {ob.data for ob in blender_objects if ob.type == 'MESH'}
    for ob in meshes:
        if not ob.materials:
            continue
        for ts in ob.materials[0].texture_slots:
            if ts and ts.texture and ts.texture.image:
                textures.add(ts.texture)
    return sorted(textures, key=lambda t: t.name)


def get_materials_from_blender_objects(blender_objects):
    """
    Only counting the first material of the mesh
    """
    materials = set()
    meshes = {ob.data for ob in blender_objects if ob.type == 'MESH'}
    for ob in meshes:
        if not ob.materials:
            continue
        materials.add(ob.materials[0])
    return sorted(materials, key=lambda m: m.name)


def get_mesh_count_from_blender_objects(blender_objects):
    return len({ob for ob in blender_objects if ob.type == 'MESH'})


def get_vertex_count_from_blender_objects(blender_objects):
    return sum([len(ob.data.vertices) for ob in blender_objects if ob.type == 'MESH'])


def get_index_count_from_blender_objects(blender_objects):
    index_count = 0
    meshes = {ob.data for ob in blender_objects if ob.type == 'MESH'}
    for mesh in meshes:
        for poly in mesh.polygons:
            index_count += len(poly.vertices)
    return index_count


def get_weights_per_vertex(blender_object):
    vertex_groups = blender_object.vertex_groups
    if not vertex_groups or blender_object.type != 'MESH':
        return {}
    weights_per_vertex = {i: [] for i in range(len(blender_object.data.vertices))}
    for vertex_index in weights_per_vertex:
        for vg in vertex_groups:
            try:
                weight = vg.weight(vertex_index)
                weights_per_vertex[vertex_index].append((vg.name, weight))
            except RuntimeError:
                pass
    return weights_per_vertex


def get_uvs_per_vertex(blender_mesh, uv_layer):
    uvs_per_loop = uv_layer.data
    vertices = {}  # vertex_index: (uv_x, uv_y)
    for i, loop in enumerate(blender_mesh.loops):
        vertex_index = loop.vertex_index
        if vertex_index in vertices:
            continue
        else:
            uvs = uvs_per_loop[i].uv
            vertices[vertex_index] = (uvs[0], uvs[1])
    return vertices


def triangles_list_to_triangles_strip(blender_mesh):
    """
    Export triangle strips from a blender mesh.
    It assumes the mesh is all triangulated.
    Based on a paper by Pierre Terdiman: http://www.codercorner.com/Strips.htm
    """
    # TODO: Fix changing of face orientation in some cases (see tests)
    edges_faces = {}
    current_strip = []
    strips = []
    joined_strips = []
    faces_indices = deque(p.index for p in blender_mesh.polygons)
    done_faces_indices = set()
    current_face_index = faces_indices.popleft()
    process_faces = True

    for polygon in blender_mesh.polygons:
        for edge in polygon.edge_keys:
            edges_faces.setdefault(edge, set()).add(polygon.index)

    while process_faces:
        current_face = blender_mesh.polygons[current_face_index]
        current_face_verts = current_face.vertices[:]
        strip_indices = [v for v in current_face_verts if v not in current_strip[-2:]]
        if current_strip:
            face_to_add = tuple(current_strip[-2:]) + tuple(strip_indices)
            if face_to_add != current_face_verts and face_to_add != tuple(reversed(current_face_verts)):
                # we arrived here because the current face shares and edge with the face in the strip
                # however, if we just add the verts, we would be changing the direction of the face
                # so we create a degenerate triangle before adding to it to the strip
                current_strip.append(current_strip[-2])
        current_strip.extend(strip_indices)
        done_faces_indices.add(current_face_index)

        next_face_index = None
        possible_face_indices = {}
        for edge in current_face.edge_keys:
            if edge not in edges_faces:
                continue
            checked_edge = {face_index: edge for face_index in edges_faces[edge]
                            if face_index != current_face_index and face_index not in done_faces_indices}
            possible_face_indices.update(checked_edge)
        for face_index, edge in possible_face_indices.items():
            if not current_strip:
                next_face_index = face_index
                break
            elif edge == tuple(current_strip[-2:]) or edge == tuple(reversed(current_strip[-2:])):
                next_face_index = face_index
                break
            elif edge == (current_strip[-1], current_strip[-2]):
                if len(current_strip) % 2 != 0:
                    # create a degenerate triangle to join them
                    current_strip.append(current_strip[-2])
                next_face_index = face_index

        if next_face_index:
            faces_indices.remove(next_face_index)
            current_face_index = next_face_index
        else:
            strips.append(current_strip)
            current_strip = []
            try:
                current_face_index = faces_indices.popleft()
            except IndexError:
                process_faces = False

    prev_strip_len = 0
    # join strips with degenerate triangles
    for strip in strips:
        if not prev_strip_len:
            joined_strips.extend(strip)
            prev_strip_len = len(strip)
        elif prev_strip_len % 2 == 0:
            joined_strips.extend((joined_strips[-1], strip[0]))
            joined_strips.extend(strip)
            prev_strip_len = len(strip)
        else:
            joined_strips.extend((joined_strips[-1], strip[0], strip[0]))
            joined_strips.extend(strip)
            prev_strip_len = len(strip)

    return joined_strips
