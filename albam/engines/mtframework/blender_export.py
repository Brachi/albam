from collections import OrderedDict, namedtuple
import ctypes
from io import BytesIO
from itertools import chain
import ntpath
import os
import tempfile
import re
import struct
try:
    import bpy
except ImportError:
    pass

from albam.registry import blender_registry
from albam.exceptions import ExportError
from albam.engines.mtframework.mod_156 import (
    Mesh156,
    MaterialData,
    BonePalette,
    CLASSES_TO_VERTEX_FORMATS,
    VERTEX_FORMATS_TO_CLASSES,
    )
from albam.engines.mtframework import Arc, Mod156, Tex112
from albam.engines.mtframework.utils import (
    vertices_export_locations,
    blender_texture_to_texture_code,
    get_texture_dirs,
    get_default_texture_dir,
    )
from albam.lib.half_float import pack_half_float
from albam.lib.structure import get_offset
from albam.lib.geometry import z_up_to_y_up
from albam.lib.misc import ntpath_to_os_path
from albam.lib.blender import (
    triangles_list_to_triangles_strip,
    get_bounding_box_positions_from_blender_objects,
    get_textures_from_blender_objects,
    get_materials_from_blender_objects,
    get_vertex_count_from_blender_objects,
    get_bone_indices_and_weights_per_vertex,
    get_uvs_per_vertex,
    )


# Taken from: RE5->uOm0000Damage.arc->/pawn/om/om0000/model/om0000.mod
# Not entirely sure what it represents (a bounding box + a matrix?), but it works in all models so far
CUBE_BBOX = [0.0, 0.0, 0.0, 0.0,
             0.0, 50.0, 0.0, 86.6025390625,
             -50.0, 0.0, -50.0, 0.0,
             50.0, 100.0, 50.0, 0.0,
             1.0, 0.0, 0.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 1.0, 0.0,
             0.0, 50.0, 0.0, 1.0,
             50.0, 50.0, 50.0, 0.0]


ExportedMeshes = namedtuple('ExportedMeshes', ('meshes_array', 'vertex_buffer', 'index_buffer'))
ExportedMaterials = namedtuple('ExportedMaterials', ('textures_array', 'materials_data_array',
                                                     'materials_mapping', 'blender_textures',
                                                     'texture_dirs'))
ExportedMod = namedtuple('ExportedMod', ('mod', 'exported_materials'))


@blender_registry.register_function('export', b'ARC\x00')
def export_arc(blender_object, file_path):
    saved_arc = Arc(file_path=BytesIO(blender_object.albam_imported_item.data))
    mods = {}
    texture_dirs = {}
    textures_to_export = []

    for child in blender_object.children:
        exportable = hasattr(child, 'albam_imported_item')
        if not exportable:
            continue

        exported_mod = export_mod156(child)
        mods[child.name] = exported_mod
        texture_dirs.update(exported_mod.exported_materials.texture_dirs)
        textures_to_export.extend(exported_mod.exported_materials.blender_textures)

    with tempfile.TemporaryDirectory() as tmpdir:
        saved_arc.unpack(tmpdir)

        mod_files = [os.path.join(root, f) for root, _, files in os.walk(tmpdir)
                     for f in files if f.endswith('.mod')]

        # overwriting the original mod files with the exported ones
        for modf in mod_files:
            filename = os.path.basename(modf)
            try:
                # TODO: mods with the same name in different folders
                exported_mod = mods[filename]
            except KeyError:
                raise ExportError("Can't export to arc, a mod file is missing: {}. "
                                  "Was it deleted before exporting?. "
                                  "mods.items(): {}".format(filename, mods.items()))

            with open(modf, 'wb') as w:
                w.write(exported_mod.mod)

        for blender_texture in textures_to_export:
            texture_name = blender_texture.name
            resolved_path = ntpath_to_os_path(texture_dirs[texture_name])
            tex_file_path = bpy.path.abspath(blender_texture.image.filepath)
            tex_filename_no_ext = os.path.splitext(os.path.basename(tex_file_path))[0]
            destination_path = os.path.join(tmpdir, resolved_path, tex_filename_no_ext + '.tex')
            tex = Tex112.from_dds(file_path=bpy.path.abspath(blender_texture.image.filepath))
            # metadata saved
            # TODO: use an util function
            for field in tex._fields_:
                attr_name = field[0]
                if not attr_name.startswith('unk_'):
                    continue
                setattr(tex, attr_name, getattr(blender_texture, attr_name))

            with open(destination_path, 'wb') as w:
                w.write(tex)

        # Once the textures and the mods have been replaced, repack.
        new_arc = Arc.from_dir(tmpdir)

    with open(file_path, 'wb') as w:
        w.write(new_arc)


def export_mod156(parent_blender_object):
    saved_mod = Mod156(file_path=BytesIO(parent_blender_object.albam_imported_item.data))

    first_children = [child for child in parent_blender_object.children]
    blender_meshes = [c for c in first_children if c.type == 'MESH']
    # only going one level deeper
    if not blender_meshes:
        children_objects = list(chain.from_iterable(child.children for child in first_children))
        blender_meshes = [c for c in children_objects if c.type == 'MESH']
    bounding_box = get_bounding_box_positions_from_blender_objects(blender_meshes)

    mesh_count = len(blender_meshes)
    header = struct.unpack('f', struct.pack('4B', mesh_count, 0, 0, 0))[0]
    meshes_array_2 = ctypes.c_float * ((mesh_count * 36) + 1)
    floats = [header] + CUBE_BBOX * mesh_count
    meshes_array_2 = meshes_array_2(*floats)

    if saved_mod.bone_count:
        bone_palettes = _create_bone_palettes(blender_meshes)
        bone_palette_array = (BonePalette * len(bone_palettes))()
        box_min_w = bounding_box.min_w * 100

        if saved_mod.unk_08:
            # Since unk_12 depends on the offset, calculate it early
            bones_array_offset = 176 + len(saved_mod.unk_12)
        else:
            bones_array_offset = 176
        for i, bp in enumerate(bone_palettes.values()):
            bone_palette_array[i].unk_01 = len(bp)
            if len(bp) != 32:
                padding = 32 - len(bp)
                bp = bp + [0] * padding
            bone_palette_array[i].values = (ctypes.c_ubyte * len(bp))(*bp)
    else:
        bones_array_offset = 0
        bone_palettes = {}
        bone_palette_array = (BonePalette * 0)()
        box_min_w = -431602080.0  # thank you tests

    exported_materials = _export_textures_and_materials(blender_meshes, saved_mod)
    exported_meshes = _export_meshes(blender_meshes, bounding_box, bone_palettes, exported_materials)

    mod = Mod156(id_magic=b'MOD',
                 version=156,
                 version_rev=1,
                 bone_count=saved_mod.bone_count,
                 mesh_count=mesh_count,
                 material_count=len(exported_materials.materials_data_array),
                 vertex_count=get_vertex_count_from_blender_objects(blender_meshes),
                 face_count=(ctypes.sizeof(exported_meshes.index_buffer) // 2) + 1,
                 edge_count=0,  # TODO: add edge_count
                 vertex_buffer_size=ctypes.sizeof(exported_meshes.vertex_buffer),
                 vertex_buffer_2_size=len(saved_mod.vertex_buffer_2),
                 texture_count=len(exported_materials.textures_array),
                 group_count=saved_mod.group_count,
                 group_data_array=saved_mod.group_data_array,
                 bone_palette_count=len(bone_palette_array),
                 bones_array_offset=bones_array_offset,
                 sphere_x=saved_mod.sphere_x,
                 sphere_y=saved_mod.sphere_y,
                 sphere_z=saved_mod.sphere_z,
                 sphere_w=saved_mod.sphere_w,
                 # z up to y up
                 box_min_x=bounding_box.min_x * 100,
                 box_min_y=bounding_box.min_z * -100,
                 box_min_z=bounding_box.min_y * 100,
                 box_min_w=box_min_w,
                 box_max_x=bounding_box.max_x * 100,
                 box_max_y=bounding_box.max_z * 100,  # not multiplying by -1, since it's abs
                 box_max_z=bounding_box.max_y * 100,
                 box_max_w=bounding_box.max_w * 100,
                 unk_01=saved_mod.unk_01,
                 unk_02=saved_mod.unk_02,
                 unk_03=saved_mod.unk_03,
                 unk_04=saved_mod.unk_04,
                 unk_05=saved_mod.unk_05,
                 unk_06=saved_mod.unk_06,
                 unk_07=saved_mod.unk_07,
                 unk_08=saved_mod.unk_08,
                 unk_09=saved_mod.unk_09,
                 unk_10=saved_mod.unk_10,
                 unk_11=saved_mod.unk_11,
                 unk_12=saved_mod.unk_12,
                 bones_array=saved_mod.bones_array,
                 bones_unk_matrix_array=saved_mod.bones_unk_matrix_array,
                 bones_world_transform_matrix_array=saved_mod.bones_world_transform_matrix_array,
                 unk_13=saved_mod.unk_13,
                 bone_palette_array=bone_palette_array,
                 textures_array=exported_materials.textures_array,
                 materials_data_array=exported_materials.materials_data_array,
                 meshes_array=exported_meshes.meshes_array,
                 meshes_array_2=meshes_array_2,
                 vertex_buffer=exported_meshes.vertex_buffer,
                 vertex_buffer_2=saved_mod.vertex_buffer_2,
                 index_buffer=exported_meshes.index_buffer
                 )
    mod.group_offset = get_offset(mod, 'group_data_array')
    mod.textures_array_offset = get_offset(mod, 'textures_array')
    mod.meshes_array_offset = get_offset(mod, 'meshes_array')
    mod.vertex_buffer_offset = get_offset(mod, 'vertex_buffer')
    mod.vertex_buffer_2_offset = get_offset(mod, 'vertex_buffer_2')
    mod.index_buffer_offset = get_offset(mod, 'index_buffer')

    return ExportedMod(mod, exported_materials)


def _export_vertices(blender_mesh_object, bounding_box, mesh_index, bone_palette):
    blender_mesh = blender_mesh_object.data
    vertex_count = len(blender_mesh.vertices)
    weights_per_vertex = get_bone_indices_and_weights_per_vertex(blender_mesh_object)
    # TODO: check the number of uv layers
    uvs_per_vertex = get_uvs_per_vertex(blender_mesh_object.data, blender_mesh_object.data.uv_layers[0])
    max_bones_per_vertex = max({len(data) for data in weights_per_vertex.values()}, default=0)
    if max_bones_per_vertex > 8:
        raise RuntimeError("The mesh '{}' contains some vertex that are weighted by "
                           "more than 8 bones, which is not supported. Fix it and try again"
                           .format(blender_mesh.name))
    VF = VERTEX_FORMATS_TO_CLASSES[max_bones_per_vertex]

    for vertex_index, (uv_x, uv_y) in uvs_per_vertex.items():
        # flipping for dds textures
        uv_y *= -1
        uv_x = pack_half_float(uv_x)
        uv_y = pack_half_float(uv_y)
        uvs_per_vertex[vertex_index] = (uv_x, uv_y)

    if uvs_per_vertex and len(uvs_per_vertex) != vertex_count:
        # TODO: logging
        print('There are some vertices with no uvs in mesh in {}.'
              'Vertex count: {} UVs per vertex: {}'.format(blender_mesh.name, vertex_count,
                                                           len(uvs_per_vertex)))

    box_width = abs(bounding_box.min_x * 100) + abs(bounding_box.max_x * 100)
    box_height = abs(bounding_box.min_y * 100) + abs(bounding_box.max_y * 100)
    box_length = abs(bounding_box.min_z * 100) + abs(bounding_box.max_z * 100)

    vertices_array = (VF * vertex_count)()
    has_bones = hasattr(VF, 'bone_indices')
    has_second_uv_layer = hasattr(VF, 'uv2_x')
    has_tangents = hasattr(VF, 'tangent_x')
    for vertex_index, vertex in enumerate(blender_mesh.vertices):
        vertex_struct = vertices_array[vertex_index]

        # list of (bone_index, value)
        weights_data = weights_per_vertex.get(vertex_index, [])
        # TODO: raise warning when vertices don't have weights
        empty = [0] * max_bones_per_vertex
        bone_indices = [bone_palette.index(bone_index) for bone_index, _ in weights_data] or empty
        weight_values = [round(weight_value * 255) for _, weight_value in weights_data] or empty
        total_weight = sum(weight_values)
        # each vertex has to be influenced 100%. Padding if it's not.
        if weights_data and total_weight < 255:
            to_fill = 255 - total_weight
            percentages = [(w / total_weight) * 100 for w in weight_values]
            weight_values = [round(w + ((percentages[i] * to_fill) / 100)) for i, w in enumerate(weight_values)]
            # XXX tmp for 8 bone_indices other hack
            excess = 255 - sum(weight_values)
            if excess:
                weight_values[0] -= 1
            # XXX more quick Saturday hack
            if sum(weight_values) < 255:
                missing = 255 - sum(weight_values)
                weight_values[0] += missing

        xyz = (vertex.co[0] * 100, vertex.co[1] * 100, vertex.co[2] * 100)
        xyz = z_up_to_y_up(xyz)
        if has_bones:
            # applying bounding box constraints
            xyz = vertices_export_locations(xyz, box_width, box_length, box_height)
        vertex_struct.position_x = xyz[0]
        vertex_struct.position_y = xyz[1]
        vertex_struct.position_z = xyz[2]
        vertex_struct.position_w = 32767
        # guessing for now:
        # using Counter([v.normal_<x,y,z,w> for i, mesh in enumerate(mod.meshes_array)
        #               for v in get_vertices_array(original, original.meshes_array[i])]).most_common(10)
        vertex_struct.normal_x = 127
        vertex_struct.normal_y = 127
        vertex_struct.normal_z = 0
        vertex_struct.normal_w = -1
        if has_tangents:
            vertex_struct.tangent_x = 53
            vertex_struct.tangent_y = 53
            vertex_struct.tangent_z = 53
            vertex_struct.tangent_w = -1

        if has_bones:
            array_size = ctypes.sizeof(vertex_struct.bone_indices)
            try:
                vertex_struct.bone_indices = (ctypes.c_ubyte * array_size)(*bone_indices)
                vertex_struct.weight_values = (ctypes.c_ubyte * array_size)(*weight_values)
            except IndexError:
                # TODO: proper logging
                print('bone_indices', bone_indices, 'array_size', array_size)
                print('VF', VF)
                raise
        try:
            vertex_struct.uv_x = uvs_per_vertex.get(vertex_index, (0, 0))[0] if uvs_per_vertex else 0
            vertex_struct.uv_y = uvs_per_vertex.get(vertex_index, (0, 0))[1] if uvs_per_vertex else 0
        except:
            pass
        if has_second_uv_layer:
            vertex_struct.uv2_x = 0
            vertex_struct.uv2_y = 0
    return vertices_array


def _create_bone_palettes(blender_mesh_objects):
    bone_palette_dicts = []
    MAX_BONE_PALETTE_SIZE = 32

    bone_palette = {'mesh_indices': set(), 'bone_indices': set()}
    for i, mesh in enumerate(blender_mesh_objects):
        # XXX case where bone names are not integers
        vertex_group_mapping = {vg.index: int(vg.name) for vg in mesh.vertex_groups}
        bone_indices = {vertex_group_mapping[vgroup.group] for vertex in mesh.data.vertices for vgroup in vertex.groups}

        msg = "Mesh {} is influenced by more than 32 bones, which is not supported".format(mesh.name)
        assert len(bone_indices) <= MAX_BONE_PALETTE_SIZE, msg

        current = bone_palette['bone_indices']
        potential = current.union(bone_indices)
        if len(potential) > MAX_BONE_PALETTE_SIZE:
            bone_palette_dicts.append(bone_palette)
            bone_palette = {'mesh_indices': {i}, 'bone_indices': set(bone_indices)}
        else:
            bone_palette['mesh_indices'].add(i)
            bone_palette['bone_indices'].update(bone_indices)

    bone_palette_dicts.append(bone_palette)

    final = OrderedDict([(frozenset(bp['mesh_indices']), sorted(bp['bone_indices']))
                        for bp in bone_palette_dicts])

    return final


def _infer_level_of_detail(name):
    LEVEL_OF_DETAIL_RE = re.compile(r'.*LOD_(?P<level_of_detail>\d+)$')
    match = LEVEL_OF_DETAIL_RE.match(name)
    if match:
        return int(match.group('level_of_detail'))
    return 1


def _export_meshes(blender_meshes, bounding_box, bone_palettes, exported_materials):
    """
    No weird optimization or sharing of offsets in the vertex buffer.
    All the same offsets, different positions like pl0200.mod from
    uPl01ShebaCos1.arc
    No time to investigate why and how those are decided. I suspect it might have to
    do with location of the meshes
    """
    meshes_156 = (Mesh156 * len(blender_meshes))()
    vertex_buffer = bytearray()
    index_buffer = bytearray()
    materials_mapping = exported_materials.materials_mapping

    vertex_position = 0
    face_position = 0
    for mesh_index, blender_mesh_ob in enumerate(blender_meshes):

        level_of_detail = _infer_level_of_detail(blender_mesh_ob.name)
        bone_palette_index = 0
        bone_palette = []
        for bpi, (meshes_indices, bp) in enumerate(bone_palettes.items()):
            if mesh_index in meshes_indices:
                bone_palette_index = bpi
                bone_palette = bp
                break

        blender_mesh = blender_mesh_ob.data
        vertices_array = _export_vertices(blender_mesh_ob, bounding_box, mesh_index, bone_palette)
        vertex_buffer.extend(vertices_array)

        # TODO: is all this format conversion necessary?
        triangle_strips_python = triangles_list_to_triangles_strip(blender_mesh)
        # mod156 use global indices for verts, in case one only mesh is needed, probably
        triangle_strips_python = [e + vertex_position for e in triangle_strips_python]
        triangle_strips_ctypes = (ctypes.c_ushort * len(triangle_strips_python))(*triangle_strips_python)
        index_buffer.extend(triangle_strips_ctypes)

        vertex_count = len(blender_mesh.vertices)
        index_count = len(triangle_strips_python)

        m156 = meshes_156[mesh_index]
        try:
            m156.material_index = materials_mapping[blender_mesh.materials[0].name]
        except IndexError:
            # TODO: insert an empty generic material in this case
            raise ExportError('Mesh {} has no materials'.format(blender_mesh.name))
        m156.constant = 1
        m156.level_of_detail = level_of_detail
        m156.vertex_format = CLASSES_TO_VERTEX_FORMATS[type(vertices_array[0])]
        m156.vertex_stride = 32
        m156.vertex_count = vertex_count
        m156.vertex_index_end = vertex_position + vertex_count - 1
        m156.vertex_index_start_1 = vertex_position
        m156.vertex_offset = 0
        m156.face_position = face_position
        m156.face_count = index_count
        m156.face_offset = 0
        m156.vertex_index_start_2 = vertex_position
        m156.vertex_group_count = 1  # using 'TEST' bounding box
        m156.bone_palette_index = bone_palette_index
        # Needs research
        m156.group_index = 0

        # metadata saved
        # TODO: use an util function
        for field in m156._fields_:
            attr_name = field[0]
            if not attr_name.startswith('unk_'):
                continue
            setattr(m156, attr_name, getattr(blender_mesh, attr_name))

        vertex_position += vertex_count
        face_position += index_count
    vertex_buffer = (ctypes.c_ubyte * len(vertex_buffer)).from_buffer(vertex_buffer)
    index_buffer = (ctypes.c_ushort * (len(index_buffer) // 2)).from_buffer(index_buffer)

    return ExportedMeshes(meshes_156, vertex_buffer, index_buffer)


def _export_textures_and_materials(blender_objects, saved_mod):
    textures = get_textures_from_blender_objects(blender_objects)
    blender_materials = get_materials_from_blender_objects(blender_objects)

    textures_array = ((ctypes.c_char * 64) * len(textures))()
    materials_data_array = (MaterialData * len(blender_materials))()
    materials_mapping = {}  # blender_material.name: material_id
    texture_dirs = get_texture_dirs(saved_mod)
    default_texture_dir = get_default_texture_dir(saved_mod)

    for i, texture in enumerate(textures):
        texture_dir = texture_dirs.get(texture.name)
        if not texture_dir:
            texture_dir = default_texture_dir
            texture_dirs[texture.name] = texture_dir
        # TODO: no default texture_dir means the original mod had no textures
        file_name = os.path.basename(bpy.path.abspath(texture.image.filepath))
        file_path = ntpath.join(texture_dir, file_name)
        try:
            file_path = file_path.encode('ascii')
        except UnicodeEncodeError:
            raise ExportError('Texture path {} is not in ascii'.format(file_path))
        if len(file_path) > 64:
            # TODO: what if relative path are used?
            raise ExportError('File path to texture {} is longer than 64 characters'
                              .format(file_path))

        file_path, _ = ntpath.splitext(file_path)
        textures_array[i] = (ctypes.c_char * 64)(*file_path)

    for mat_index, mat in enumerate(blender_materials):
        material_data = MaterialData()
        # Setting uknown data
        # TODO: do this with a util function
        for field in material_data._fields_:
            attr_name = field[0]
            if not attr_name.startswith('unk_'):
                continue
            setattr(material_data, attr_name, getattr(mat, attr_name))

        for texture_slot in mat.texture_slots:
            if not texture_slot or not texture_slot.texture:
                continue
            texture = texture_slot.texture
            # texture_indices expects index-1 based
            texture_index = textures.index(texture) + 1
            texture_code = blender_texture_to_texture_code(texture_slot)
            material_data.texture_indices[texture_code] = texture_index
        materials_data_array[mat_index] = material_data
        materials_mapping[mat.name] = mat_index

    return ExportedMaterials(textures_array, materials_data_array, materials_mapping, textures,
                             texture_dirs)
