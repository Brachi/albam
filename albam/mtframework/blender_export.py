import ctypes
from io import BytesIO
import ntpath
import os
import tempfile

try:
    import bpy
except ImportError:
    pass


from albam.exceptions import BuildMeshError, ExportError
from albam.mtframework.mod import (
    Mesh156,
    MaterialData,
    CLASSES_TO_VERTEX_FORMATS,
    VERTEX_FORMATS_TO_CLASSES,
    )
from albam.mtframework import Arc, Mod156, Tex112
from albam.mtframework.utils import (
    vertices_export_locations,
    get_vertices_array,
    )
from albam.utils import (
    pack_half_float,
    get_offset,
    triangles_list_to_triangles_strip,
    z_up_to_y_up,
    get_bounding_box_positions_from_blender_objects,
    get_bone_count_from_blender_objects,
    get_textures_from_blender_objects,
    get_materials_from_blender_objects,
    get_mesh_count_from_blender_objects,
    get_vertex_count_from_blender_objects,
    get_bone_indices_and_weights_per_vertex,
    get_uvs_per_vertex,
    )


def export_arc(blender_object):
    '''Exports an arc file containing mod and tex files, among others from a
    previously imported arc.'''
    mods = {}
    try:
        saved_arc = Arc(file_path=BytesIO(blender_object.albam_imported_item.data))
    except AttributeError:
        raise ExportError('Object {0} did not come from the original arc'.format(blender_object.name))

    for child in blender_object.children:
        try:
            mod_dirpath = child.albam_imported_item.source_path
            # TODO: This could lead to errors if imported in Windows and exported in posix?
            mod_filepath = os.path.join(mod_dirpath, child.name)
        except AttributeError:
            raise ExportError('Object {0} did not come from the original arc'.format(child.name))
        assert child.albam_imported_item.source_path_is_absolute is False
        assert child.albam_imported_item.file_type == 'mtframework.mod'
        mod, textures = export_mod156(child)
        mods[mod_filepath] = (mod, textures)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_slash_ending = tmpdir + os.sep if not tmpdir.endswith(os.sep) else tmpdir
        saved_arc.unpack(tmpdir)
        mod_files = [os.path.join(root, f) for root, _, files in os.walk(tmpdir)
                     for f in files if f.endswith('.mod')]
        # tex_files = {os.path.join(root, f) for root, _, files in os.walk(tmpdir)
        #             for f in files if f.endswith('.tex')}
        new_tex_files = set()
        for modf in mod_files:
            rel_path = modf.split(tmpdir_slash_ending)[1]
            try:
                new_mod = mods[rel_path]
            except KeyError:
                raise ExportError("Can't export to arc, a mod file is missing: {}".format(rel_path))

            with open(modf, 'wb') as w:
                w.write(new_mod[0])
            mod_textures = new_mod[1]
            for texture in mod_textures:
                tex = Tex112.from_dds(file_path=bpy.path.abspath(texture.image.filepath))
                try:
                    tex.unk_float_1 = texture.albam_imported_texture_value_1
                    tex.unk_float_2 = texture.albam_imported_texture_value_2
                    tex.unk_float_3 = texture.albam_imported_texture_value_3
                    tex.unk_float_4 = texture.albam_imported_texture_value_4
                except AttributeError:
                    pass

                tex_name = os.path.basename(texture.image.filepath)
                tex_filepath = os.path.join(os.path.dirname(modf), tex_name.replace('.dds', '.tex'))
                new_tex_files.add(tex_filepath)
                with open(tex_filepath, 'wb') as w:
                    w.write(tex)
        # probably other files can reference textures besides mod, this is in case
        # textures applied have other names.
        # TODO: delete only textures referenced from saved_mods at import time
        # unused_tex_files = tex_files - new_tex_files
        # for utex in unused_tex_files:
        #    os.unlink(utex)
        new_arc = Arc.from_dir(tmpdir)
    return new_arc


def export_mod156(blender_object):
    '''The blender_object provided should have meshes as children'''
    try:
        saved_mod = Mod156(file_path=BytesIO(blender_object.albam_imported_item.data))
    except AttributeError:
        raise ExportError("Can't export '{0}' to Mod156, the model to be exported "
                          "wasn't imported using Albam"
                          .format(blender_object.name))

    objects = [child for child in blender_object.children] + [blender_object]
    bounding_box = get_bounding_box_positions_from_blender_objects(objects)

    textures_array, materials_array = _export_textures_and_materials(objects, saved_mod)
    meshes_array, vertex_buffer, index_buffer = _export_meshes(objects, bounding_box, saved_mod)

    bone_count = get_bone_count_from_blender_objects(objects)
    if not bone_count:
        bones_array_offset = 0
    elif bone_count and saved_mod.unk_08:
        bones_array_offset = 176 + len(saved_mod.unk_12)
    else:
        bones_array_offset = 176

    mod = Mod156(id_magic=b'MOD',
                 version=156,
                 version_rev=1,
                 bone_count=bone_count,
                 mesh_count=get_mesh_count_from_blender_objects(objects),
                 material_count=len(materials_array),
                 vertex_count=get_vertex_count_from_blender_objects(objects),
                 face_count=(ctypes.sizeof(index_buffer) // 2) + 1,
                 edge_count=0,  # TODO: add edge_count
                 vertex_buffer_size=ctypes.sizeof(vertex_buffer),
                 vertex_buffer_2_size=len(saved_mod.vertex_buffer_2),
                 texture_count=len(textures_array),
                 group_count=saved_mod.group_count,
                 bones_array_offset=bones_array_offset,
                 group_data_array=saved_mod.group_data_array,
                 bone_palette_count=saved_mod.bone_palette_count,
                 sphere_x=saved_mod.sphere_x,
                 sphere_y=saved_mod.sphere_y,
                 sphere_z=saved_mod.sphere_z,
                 sphere_w=saved_mod.sphere_w,
                 box_min_x=saved_mod.box_min_x,
                 box_min_y=saved_mod.box_min_y,
                 box_min_z=saved_mod.box_min_z,
                 box_min_w=saved_mod.box_min_w,
                 box_max_x=saved_mod.box_max_x,
                 box_max_y=saved_mod.box_max_y,
                 box_max_z=saved_mod.box_max_z,
                 box_max_w=saved_mod.box_max_w,
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
                 bone_palette_array=saved_mod.bone_palette_array,
                 textures_array=textures_array,
                 materials_data_array=materials_array,
                 meshes_array=meshes_array,
                 meshes_array_2=saved_mod.meshes_array_2,
                 vertex_buffer=vertex_buffer,
                 vertex_buffer_2=saved_mod.vertex_buffer_2,
                 index_buffer=index_buffer
                 )
    mod.bones_array_offset = get_offset(mod, 'bones_array') if mod.bone_count else 0
    mod.group_offset = get_offset(mod, 'group_data_array')
    mod.textures_array_offset = get_offset(mod, 'textures_array')
    mod.meshes_array_offset = get_offset(mod, 'meshes_array')
    mod.vertex_buffer_offset = get_offset(mod, 'vertex_buffer')
    mod.vertex_buffer_2_offset = get_offset(mod, 'vertex_buffer_2')
    mod.index_buffer_offset = get_offset(mod, 'index_buffer')
    return mod, get_textures_from_blender_objects(objects)


def _export_vertices(blender_mesh_object, bounding_box, saved_mod, mesh_index):
    saved_mesh = saved_mod.meshes_array[mesh_index]
    if saved_mod.bone_palette_array:
        bone_palette = saved_mod.bone_palette_array[saved_mesh.bone_palette_index].values[:]
    else:
        bone_palette = []
    blender_mesh = blender_mesh_object.data
    vertex_count = len(blender_mesh.vertices)
    weights_per_vertex = get_bone_indices_and_weights_per_vertex(blender_mesh_object)
    # TODO: check the number of uv layers
    uvs_per_vertex = get_uvs_per_vertex(blender_mesh_object.data, blender_mesh_object.data.uv_layers[0])

    VF = VERTEX_FORMATS_TO_CLASSES[saved_mesh.vertex_format]

    '''
    # Unfortunately this fails in some cases and could crash the game; until some mesh unknowns are figured out,
    # relying on saved_mesh data
    # e.g. pl0000.mod from uPl00ChrisNormal.arc, meshes_array[30] has max bones per vertex = 4, but the
    # original file has 5
    if weights_per_vertex:
        max_bones_per_vertex = max({len(data) for data in weights_per_vertex.values()})
        if max_bones_per_vertex > 8:
            raise RuntimeError("The mesh '{}' contains some vertex that are weighted by "
                               "more than 8 bones, which is not supported. Fix it and try again"
                               .format(blender_mesh.name))
        VF = VERTEX_FORMATS_TO_CLASSES[max_bones_per_vertex]
    '''

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
    has_tangents = hasattr(VF, 'tangent_x')
    has_second_uv_layer = hasattr(VF, 'uv2_x')
    original_vertices_array = get_vertices_array(saved_mod, saved_mod.meshes_array[mesh_index])
    for vertex_index, vertex in enumerate(blender_mesh.vertices):
        vertex_struct = vertices_array[vertex_index]
        original_vertex_struct = original_vertices_array[vertex_index]
        if weights_per_vertex:
            weights_data = weights_per_vertex[vertex_index]   # list of (bone_index, value)
            bone_indices = [bone_palette.index(bone_index) for bone_index, _ in weights_data]
            weight_values = [round(weight_value * 255) for _, weight_value in weights_data]
        else:
            bone_indices = []
            weight_values = []

        xyz = (vertex.co[0] * 100, vertex.co[1] * 100, vertex.co[2] * 100)
        xyz = z_up_to_y_up(xyz)
        if has_bones:
            # applying bounding box constraints
            xyz = vertices_export_locations(xyz, box_width, box_length, box_height)
        vertex_struct.position_x = xyz[0]
        vertex_struct.position_y = xyz[1]
        vertex_struct.position_z = xyz[2]
        vertex_struct.position_w = 32767
        if has_bones:
            array_size = ctypes.sizeof(vertex_struct.bone_indices)
            vertex_struct.bone_indices = (ctypes.c_ubyte * array_size)(*bone_indices)
            vertex_struct.weight_values = (ctypes.c_ubyte * array_size)(*weight_values)
        '''
        vertex_struct.normal_x = round(vertex.normal[0] * 127)
        vertex_struct.normal_y = round(vertex.normal[2] * 127) * -1
        vertex_struct.normal_z = round(vertex.normal[1] * 127)
        vertex_struct.normal_w = -1
        '''
        # XXX quick hack until normals can be exported ok in blender (gotta check fbx export or ask Bastien Montagne)
        vertex_struct.normal_x = original_vertex_struct.normal_x
        vertex_struct.normal_y = original_vertex_struct.normal_y
        vertex_struct.normal_z = original_vertex_struct.normal_z
        vertex_struct.normal_w = original_vertex_struct.normal_w
        if has_tangents:
            vertex_struct.tangent_x = original_vertex_struct.tangent_x
            vertex_struct.tangent_y = original_vertex_struct.tangent_x
            vertex_struct.tangent_z = original_vertex_struct.tangent_x
            vertex_struct.tangent_w = original_vertex_struct.tangent_x
            '''
            vertex_struct.tangent_x = -1
            vertex_struct.tangent_y = -1
            vertex_struct.tangent_z = -1
            vertex_struct.tangent_w = -1
            '''
        vertex_struct.uv_x = uvs_per_vertex.get(vertex_index, (0, 0))[0] if uvs_per_vertex else 0
        vertex_struct.uv_y = uvs_per_vertex.get(vertex_index, (0, 0))[1] if uvs_per_vertex else 0
        if has_second_uv_layer:
            vertex_struct.uv2_x = 0
            vertex_struct.uv2_y = 0
    return VF, vertices_array


def _export_meshes(blender_objects, bounding_box, saved_mod):
    """
    No weird optimization or sharing of offsets in the vertex buffer.
    All the same offsets, different positions like pl0200.mod from
    uPl01ShebaCos1.arc
    No time to investigate why and how those are decided. I suspect it might have to
    do with location of the meshes
    """
    blender_meshes_objects = [ob for ob in blender_objects if ob.type == 'MESH']
    meshes_156 = (Mesh156 * len(blender_meshes_objects))()
    vertex_buffer = bytearray()
    index_buffer = bytearray()
    materials = get_materials_from_blender_objects(blender_objects)

    vertex_position = 0
    face_position = 0
    for i, blender_mesh_object in enumerate(blender_meshes_objects):
        # XXX: if a model with more meshes than the original is exported... boom
        # If somehow indices are changed... boom
        try:
            saved_mesh = saved_mod.meshes_array[i]
        except IndexError:
            raise ExportError('Exporting models with more meshes (parts) than the original not supported yet')
        blender_mesh = blender_mesh_object.data

        vertex_format, vertices_array = _export_vertices(blender_mesh_object, bounding_box,
                                                         saved_mod, i)
        vertex_buffer.extend(vertices_array)
        # TODO: is all this format conversion necessary?
        triangle_strips_python = triangles_list_to_triangles_strip(blender_mesh)
        # mod156 use global indices for verts, in case one only mesh is needed, probably
        triangle_strips_python = [e + vertex_position for e in triangle_strips_python]
        triangle_strips_ctypes = (ctypes.c_ushort * len(triangle_strips_python))(*triangle_strips_python)
        index_buffer.extend(triangle_strips_ctypes)

        vertex_count = len(blender_mesh.vertices)
        index_count = len(triangle_strips_python)

        m156 = meshes_156[i]
        try:
            m156.material_index = materials.index(blender_mesh.materials[0])
        except IndexError:
            raise ExportError('Mesh {} has no materials'.format(blender_mesh.name))
        m156.constant = 1
        m156.level_of_detail = saved_mesh.level_of_detail  # TODO
        m156.vertex_format = CLASSES_TO_VERTEX_FORMATS[vertex_format]
        m156.vertex_stride = 32
        m156.vertex_count = vertex_count
        m156.vertex_index_end = vertex_position + vertex_count - 1
        m156.vertex_index_start_1 = vertex_position
        m156.vertex_offset = 0
        m156.face_position = face_position
        m156.face_count = index_count
        m156.face_offset = 0
        m156.vertex_index_start_2 = vertex_position
        m156.vertex_group_count = saved_mesh.vertex_group_count  # len(blender_mesh_object.vertex_groups)
        # XXX: improve, not guaranteed!
        m156.bone_palette_index = saved_mesh.bone_palette_index

        # TODO: not using saved_mesh since it seems these are optional. Needs research
        m156.group_index = saved_mesh.group_index
        m156.unk_01 = saved_mesh.unk_01
        # m156.unk_02 = saved_mesh.unk_02  # crashes if set to saved_mesh.unk_02 in ChrisNormal
        m156.unk_03 = saved_mesh.unk_03
        m156.unk_04 = saved_mesh.unk_04
        m156.unk_05 = saved_mesh.unk_05
        m156.unk_06 = saved_mesh.unk_06
        m156.unk_07 = saved_mesh.unk_07
        m156.unk_08 = saved_mesh.unk_08
        m156.unk_09 = saved_mesh.unk_09
        m156.unk_10 = saved_mesh.unk_10
        m156.unk_11 = saved_mesh.unk_11

        vertex_position += vertex_count
        face_position += index_count
    vertex_buffer = (ctypes.c_ubyte * len(vertex_buffer)).from_buffer(vertex_buffer)
    index_buffer = (ctypes.c_ushort * (len(index_buffer) // 2)).from_buffer(index_buffer)

    return meshes_156, vertex_buffer, index_buffer


def _export_textures_and_materials(blender_objects, saved_mod):
    textures = get_textures_from_blender_objects(blender_objects)
    blender_materials = get_materials_from_blender_objects(blender_objects)
    textures_array = ((ctypes.c_char * 64) * len(textures))()
    materials_data_array = (MaterialData * len(blender_materials))()

    for i, texture in enumerate(textures):
        file_name = os.path.basename(texture.image.filepath)
        try:
            file_path = ntpath.join(texture.albam_imported_texture_folder, file_name)
        except AttributeError:
            raise ExportError('Texture {0} was not imported from an Arc file'.format(texture.name))
        try:
            file_path, _ = ntpath.splitext(file_path)
            textures_array[i] = (ctypes.c_char * 64)(*file_path.encode('ascii'))
        except UnicodeEncodeError:
            raise ExportError('Texture path {} is not in ascii'.format(file_path))
        if len(file_path) > 64:
            # TODO: what if relative path are used?
            raise ExportError('File path to texture {} is longer than 64 characters'
                              .format(file_path))

    for i, mat in enumerate(blender_materials):
        material_data = MaterialData()
        try:
            # TODO: Should use data from actual blender material
            saved_mat = saved_mod.materials_data_array[i]
        except IndexError:
            raise ExportError('Exporting models with more materials than the original not supported yet')
        material_data.unk_01 = saved_mat.unk_01
        material_data.unk_02 = saved_mat.unk_02
        material_data.unk_03 = saved_mat.unk_03
        material_data.unk_04 = saved_mat.unk_04
        material_data.unk_05 = saved_mat.unk_05
        material_data.unk_06 = saved_mat.unk_06
        material_data.unk_07 = saved_mat.unk_07
        for texture_slot in mat.texture_slots:
            if not texture_slot:
                continue
            texture = texture_slot.texture
            if not texture:
                # ?
                continue
            # texture_indices expects index-1 based
            try:
                texture_index = textures.index(texture) + 1
            except ValueError:
                # TODO: logging
                print('error in textures')
            material_data.texture_indices[texture.albam_imported_texture_type] = texture_index
        materials_data_array[i] = material_data

    return textures_array, materials_data_array
