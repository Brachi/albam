import ctypes
from itertools import chain
import ntpath
import os

from albam.exceptions import BuildMeshError, TextureError
from albam.mtframework.mod import VertexFormat, VertexFormat5, VertexFormat0, Mesh156
from albam.mtframework import Arc, Mod156, Tex112
from albam.utils import (
    unpack_half_float, pack_half_float,
    chunks,
    get_offset, get_size,
    strip_triangles_to_triangles_list, triangles_list_to_triangles_strip,
    y_up_to_z_up, z_up_to_y_up,
    get_bounding_box_positions_from_blender_objects,
    create_mesh_name,
    get_bone_count_from_blender_objects,
    get_texture_count_from_blender_objects,
    get_materials_from_blender_objects,
    get_mesh_count_from_blender_objects,
    get_vertex_count_from_blender_objects,
    get_weights_per_vertex,
    get_uvs_per_vertex,
    )
try:
    import bpy
    from mathutils import Matrix, Vector
except ImportError:
    pass


def _get_vertex_array_from_vertex_buffer(mod, mesh):
    if mesh.vertex_format == 0:
        VF = VertexFormat0
    elif mesh.vertex_format in (1, 2, 3, 4):
        VF = VertexFormat
    else:
        VF = VertexFormat5
    position = max(mesh.vertex_index_start_1, mesh.vertex_index_start_2) * mesh.vertex_stride
    offset = ctypes.addressof(mod.vertex_buffer)
    offset += mesh.vertex_offset
    offset += position
    if mesh.vertex_index_start_2 > mesh.vertex_index_start_1:
        vertex_count = mesh.vertex_index_end - mesh.vertex_index_start_2 + 1
        # TODO: research the content of mesh.vertex_index_start_1 and what it means in this case
        # So far it looks it contains only garbage; all vertices have the same values.
        # It's unknown why they exist for, and why they count for mesh.vertex_count
        # The imported meshes here will have a different mesh count than the original.
    else:
        vertex_count = mesh.vertex_count
    return (VF * vertex_count).from_address(offset)


def _get_indices_array(mod, mesh):
    offset = ctypes.addressof(mod.index_buffer)
    position = mesh.face_offset * 2 + mesh.face_position * 2
    if position > get_size(mod, 'index_buffer'):
        raise BuildMeshError('Error building mesh in get_indices_array.'
                             'mesh.face_offset: {}, mesh.face_position: {}'
                             .format(mesh.face_offset, mesh.face_position))
    offset += position
    return (ctypes.c_ushort * mesh.face_count).from_address(offset)


def _vertices_export_locations(xyz_tuple, bounding_box_width, bounding_box_height, bounding_box_length):
    x, y, z = xyz_tuple

    x += bounding_box_width / 2
    x /= bounding_box_width
    x *= 32767

    y /= bounding_box_height
    y *= 32767

    z += bounding_box_length / 2
    z /= bounding_box_length
    z *= 32767

    return (round(x), round(y), round(z))


def _vertices_import_locations(vertex_format, bounding_box_width, bounding_box_height, bounding_box_length):
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


def _get_weights_per_bone(mod, mesh, vertices_array):
    weights_per_bone = {}
    if not mod.bone_count or not hasattr(vertices_array[0], 'bone_indices'):
        return weights_per_bone
    bone_palette = mod.bone_palette_array[mesh.bone_palette_index]
    for vertex_index, vertex in enumerate(vertices_array):
        for bi, bone_index in enumerate(vertex.bone_indices):
            if bone_index >= bone_palette.unk_01:
                real_bone_index = mod.unk_13[bone_index]
            else:
                real_bone_index = bone_palette.values[bone_index]
            if bone_index + vertex.weight_values[bi] == 0:
                continue
            bone_data = weights_per_bone.setdefault(real_bone_index, [])
            bone_data.append((vertex_index, vertex.weight_values[bi] / 255))
    return weights_per_bone


def _import_vertices(mod, mesh):
    box_width = abs(mod.box_min_x) + abs(mod.box_max_x)
    box_height = abs(mod.box_min_y) + abs(mod.box_max_y)
    box_length = abs(mod.box_min_z) + abs(mod.box_max_z)

    vertices_array = _get_vertex_array_from_vertex_buffer(mod, mesh)

    if mesh.vertex_format != 0:
        vertices = (_vertices_import_locations(vf, box_width, box_height, box_length)
                    for vf in vertices_array)
    else:
        vertices = ((vf.position_x, vf.position_y, vf.position_z) for vf in vertices_array)
    vertices = (y_up_to_z_up(vertex_tuple) for vertex_tuple in vertices)
    vertices = ((x / 100, y / 100, z / 100) for x, y, z in vertices)

    # TODO: investigate why uvs don't appear above the image in the UV editor
    list_of_tuples = [(unpack_half_float(v.uv_x), unpack_half_float(v.uv_y) * -1) for v in vertices_array]
    return {'locations': list(vertices),
            'uvs': list(chain.from_iterable(list_of_tuples)),
            'weights_per_bone': _get_weights_per_bone(mod, mesh, vertices_array)
            }


def _export_vertices(blender_mesh_object, position, bounding_box):
    blender_mesh = blender_mesh_object.data
    vertex_count = len(blender_mesh.vertices)
    weights_per_vertex = get_weights_per_vertex(blender_mesh_object)
    # TODO: check the number of uv layers
    uvs_per_vertex = get_uvs_per_vertex(blender_mesh_object.data, blender_mesh_object.data.uv_layers[0])
    if weights_per_vertex:
        max_bones_per_vertex = max({len(data) for data in weights_per_vertex.values()})
        if max_bones_per_vertex <= 4:
            weights_array_size = 4
            VF = VertexFormat
        elif max_bones_per_vertex <= 8:
            weights_array_size = 8
            VF = VertexFormat5
        else:
            raise RuntimeError("The mesh '{}' contains some vertex that are weighted by "
                               "more than 8 bones, which is not supported. Fix it and try again"
                               .format(blender_mesh.name))

    else:
        max_bones_per_vertex = 0
        weights_array_size = 0
        VF = VertexFormat0

    for vertex_index, (uv_x, uv_y) in uvs_per_vertex.items():
        # flipping for dds textures
        uv_y *= -1
        uv_x = pack_half_float(uv_x)
        uv_y = pack_half_float(uv_y)
        uvs_per_vertex[vertex_index] = (uv_x, uv_y)

    vertices_array = (VF * vertex_count)()
    if uvs_per_vertex and len(uvs_per_vertex) != vertex_count:
        raise BuildMeshError('There are some vertices with no uvs in mesh in {}'.format(blender_mesh.name))

    box_width = abs(bounding_box.min_x * 100) + abs(bounding_box.max_x * 100)
    box_height = abs(bounding_box.min_y * 100) + abs(bounding_box.max_y * 100)
    box_length = abs(bounding_box.min_z * 100) + abs(bounding_box.max_z * 100)

    for vertex_index, vertex in enumerate(blender_mesh.vertices):
        vertex_format = vertices_array[vertex_index]
        if max_bones_per_vertex:
            weights_data = weights_per_vertex[vertex_index]   # list of (str(bone_index), value)
        else:
            weights_data = []
        # FIXME: Assumming vertex groups were named after the bone index,
        # should get the bone and get the index
        bone_indices = [int(vg_name) for vg_name, _ in weights_data]
        weight_values = [round(weight_value * 255) for _, weight_value in weights_data]

        xyz = (vertex.co[0] * 100, vertex.co[1] * 100, vertex.co[2] * 100)
        xyz = z_up_to_y_up(xyz)
        if VF != VertexFormat0:
            xyz = _vertices_export_locations(xyz, box_width, box_length, box_height)
        vertex_format.position_x = xyz[0]
        vertex_format.position_y = xyz[1]
        vertex_format.position_z = xyz[2]
        vertex_format.position_w = 32767
        vertex_format.bone_indices = (ctypes.c_ubyte * weights_array_size)(*bone_indices)
        vertex_format.weight_values = (ctypes.c_ubyte * weights_array_size)(*weight_values)
        vertex_format.normal_x = 127
        vertex_format.normal_y = 127
        vertex_format.normal_z = 127
        vertex_format.normal_w = 127
        if VF == VertexFormat:
            vertex_format.tangent_x = 127
            vertex_format.tangent_y = 127
            vertex_format.tangent_z = 127
            vertex_format.tangent_w = 127
        vertex_format.uv_x = uvs_per_vertex[vertex_index][0] if uvs_per_vertex else 0
        vertex_format.uv_y = uvs_per_vertex[vertex_index][1] if uvs_per_vertex else 0
        if VF == VertexFormat:
            vertex_format.uv2_x = 0
            vertex_format.uv2_y = 0

    return VF, vertices_array


def _create_blender_textures_from_mod(mod, base_dir):
    textures = [None]  # materials refer to textures in index-1
    # TODO: check why in Arc.header.file_entries[n].file_path it returns a bytes, and
    # here the whole array of chars
    for i, texture_path in enumerate(mod.textures_array):
        path = texture_path[:].decode('ascii').partition('\x00')[0]
        path = os.path.join(base_dir, *path.split(ntpath.sep))
        path = '.'.join((path, 'tex'))
        if not os.path.isfile(path):
            # TODO: log warnings, figure out 'rtex' format
            continue
        tex = Tex112(path)
        try:
            dds = tex.to_dds()
        except TextureError as err:
            # TODO: log this instead of printing it
            print('Error converting "{}"to dds: {}'.format(path, err))
            textures.append(None)
            continue
        dds_path = path.replace('.tex', '.dds')
        with open(dds_path, 'wb') as w:
            w.write(dds)
        image = bpy.data.images.load(dds_path)
        texture = bpy.data.textures.new(os.path.basename(path), type='IMAGE')
        texture.image = image  # not in constructor!
        textures.append(texture)
    return textures


def _create_blender_materials_from_mod(mod, model_name, textures):
    materials = []

    for i, material in enumerate(mod.materials_data_array):
        blender_material = bpy.data.materials.new('{}_{}'.format(model_name, str(i).zfill(2)))
        for i, tex_index in enumerate(material.texture_indices):
            if tex_index == 0:
                continue
            slot = blender_material.texture_slots.add()
            try:
                texture_target = textures[tex_index]
            except IndexError:
                continue
            if not texture_target:
                continue
            slot.texture = texture_target
            slot.use_map_alpha = True
            if i == 0:
                # Diffuse
                slot.use_map_color_diffuse = True
            elif i == 1:
                # Normal
                slot.use_map_color_diffuse = False
                slot.use_map_normal = True
                slot.normal_factor = 0.05
            elif i == 2:
                slot.use_map_color_diffuse = False
                slot.use_map_specular = True
            elif i == 7:
                # cube map normal
                slot.use_map_color_diffuse = False
                slot.use_map_normal = True
                slot.normal_factor = 0.05
                slot.texture_coords = 'GLOBAL'
                slot.mapping = 'CUBE'
            else:
                slot.use_map_color_diffuse = False
                pass
                # TODO: 3, 4, 5, 6,
        materials.append(blender_material)
    return materials


def _get_bone_parents_from_mod(bone, bones_array):
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


def _create_blender_armature_from_mod(mod, armature_name, parent=None):
    armature = bpy.data.armatures.new(armature_name)
    armature_ob = bpy.data.objects.new(armature_name, armature)
    armature_ob.parent = parent
    bpy.context.scene.objects.link(armature_ob)

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # deselect all objects
    for i in bpy.context.scene.objects:
        i.select = False
    bpy.context.scene.objects.active = armature_ob
    armature_ob.select = True
    bpy.ops.object.mode_set(mode='EDIT')

    blender_bones = []
    for i, bone in enumerate(mod.bones_array):
        blender_bone = armature.edit_bones.new(str(i))
        blender_bones.append(blender_bone)
        parents = _get_bone_parents_from_mod(bone, mod.bones_array)
        if not parents:
            blender_bone.head = Vector((bone.location_x / 100,
                                        bone.location_z * -1 / 100,
                                        bone.location_y / 100))
            continue
        chain = [i] + parents
        wtm = Matrix.Translation((0, 0, 0))
        for bi in reversed(chain):
            b = mod.bones_array[bi]
            wtm *= Matrix.Translation((b.location_x / 100, b.location_z / 100 * -1, b.location_y / 100))
        blender_bone.head = wtm.to_translation()
        blender_bone.parent = blender_bones[bone.parent_index]

    assert len(blender_bones) == len(mod.bones_array)

    # set tails of bone to their children or make them small if they have none
    for i, bone in enumerate(blender_bones):
        children = bone.children_recursive
        non_mirror_children = [b for b in children
                               if mod.bones_array[int(b.name)].mirror_index == int(b.name)]
        mirror_children = [b for b in children
                           if mod.bones_array[int(b.name)].mirror_index != int(b.name)]
        if mod.bones_array[i].mirror_index == i and non_mirror_children:
            bone.tail = non_mirror_children[0].head
        elif mod.bones_array[i].mirror_index != i and mirror_children:
            bone.tail = mirror_children[0].head
        else:
            bone.length = 0.01
        if bone.tail == bone.head:
            bone.tail += Vector((0.01, 0.01, 0.01))

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_ob


def _build_blender_mesh_from_mod(mod, mesh, mesh_index, file_path, materials):
    imported_vertices = _import_vertices(mod, mesh)
    vertex_locations = imported_vertices['locations']
    indices = _get_indices_array(mod, mesh)
    indices = strip_triangles_to_triangles_list(indices)
    uvs_per_vertex = imported_vertices['uvs']
    weights_per_bone = imported_vertices['weights_per_bone']

    name = create_mesh_name(mesh, mesh_index, file_path)
    me_ob = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me_ob)
    me_ob.from_pydata(vertex_locations, [], chunks(indices, 3))
    me_ob.update(calc_edges=True)
    me_ob.validate()
    if materials:
        me_ob.materials.append(materials[mesh.material_index])
    for bone_index, data in weights_per_bone.items():
        vg = ob.vertex_groups.new(str(bone_index))
        for vertex_index, weight_value in data:
            vg.add((vertex_index,), weight_value, 'ADD')

    if uvs_per_vertex:
        me_ob.uv_textures.new(name)
        uv_layer = me_ob.uv_layers[-1].data
        per_loop_list = []
        for loop in me_ob.loops:
            offset = loop.vertex_index * 2
            per_loop_list.extend((uvs_per_vertex[offset], uvs_per_vertex[offset + 1]))
        uv_layer.foreach_set('uv', per_loop_list)
    return ob


def _create_meshes_156_array(blender_objects, group_materials, bounding_box):
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

    vertex_position = 0
    face_position = 0
    for i, blender_mesh_object in enumerate(blender_meshes_objects):
        blender_mesh = blender_mesh_object.data
        vertex_format, vertices_array = _export_vertices(blender_mesh_object, vertex_position, bounding_box)
        vertex_buffer.extend(vertices_array)
        # TODO: is all this format conversion necessary?
        triangle_strips_python = triangles_list_to_triangles_strip(blender_mesh)
        # mod156 use global indices for verts, in case one only mesh is needed, probably
        triangle_strips_python = [e + vertex_position for e in triangle_strips_python]
        triangle_strips_ctypes = (ctypes.c_ushort * len(triangle_strips_python))(*triangle_strips_python)
        index_buffer.extend(triangle_strips_ctypes)

        if vertex_format == VertexFormat0:
            vf = 0
        elif vertex_format == VertexFormat:
            vf = 1
        else:
            vf = 5

        vertex_count = len(blender_mesh.vertices)
        index_count = len(triangle_strips_python)

        m156 = meshes_156[i]
        m156.type = 0  # Needs to be investagated
        m156.unk_01 = 1  # all game models seem to have the value 1
        m156.level_of_detail = 1  # TODO
        m156.unk_02 = 0  # most player models seem to have this value, needs research
        m156.vertex_format = vf
        m156.vertex_stride = 32
        m156.unk_03 = 0  # Most meshes use this value
        m156.unk_04 = 0
        m156.unk_05 = 110
        m156.vertex_count = vertex_count
        m156.vertex_index_end = vertex_position + vertex_count - 1
        m156.vertex_index_start_1 = vertex_position
        m156.vertex_offset = 0
        m156.unk_06 = 0  # Most models have this value
        m156.face_position = face_position
        m156.face_count = index_count
        m156.face_offset = 0
        m156.unk_07 = 0
        m156.unk_08 = 0
        m156.vertex_index_start_2 = vertex_position
        m156.unk_09 = 0
        m156.bone_palette_index = 0  # TODO
        m156.unk_10 = 0
        m156.unk_11 = 0
        m156.unk_12 = 0
        m156.unk_13 = 0

        vertex_position += vertex_count
        face_position += index_count
    vertex_buffer = (ctypes.c_ubyte * len(vertex_buffer)).from_buffer(vertex_buffer)
    index_buffer = (ctypes.c_ushort * (len(index_buffer) // 2)).from_buffer(index_buffer)

    return meshes_156, vertex_buffer, index_buffer


def import_mod156(file_path, base_dir, parent=None):
    mod = Mod156(file_path=file_path)
    model_name = os.path.basename(file_path)
    textures = _create_blender_textures_from_mod(mod, base_dir)
    materials = _create_blender_materials_from_mod(mod, model_name, textures)
    meshes = []
    for i, mesh in enumerate(mod.meshes_array):
        try:
            m = _build_blender_mesh_from_mod(mod, mesh, i, file_path, materials)
            meshes.append(m)
        except BuildMeshError as err:
            print(err)
    if mod.bone_count:
        armature_ob = _create_blender_armature_from_mod(mod, model_name, parent)
        armature_ob.show_x_ray = True
    else:
        parent_empty = bpy.data.objects.new(model_name, None)
        parent_empty.parent = parent
        bpy.context.scene.objects.link(parent_empty)

    for mesh in meshes:
        bpy.context.scene.objects.link(mesh)
        if mod.bone_count:
            mesh.parent = armature_ob
            modifier = mesh.modifiers.new(type="ARMATURE", name=model_name)
            modifier.object = armature_ob
            modifier.use_vertex_groups = True
        else:
            mesh.parent = parent_empty


def import_arc(file_path, extraction_dir=None):
    base_dir = os.path.basename(file_path).replace('.arc', '_arc_extracted')
    if not extraction_dir:
        out = os.path.join(os.path.expanduser('~'), '.albam', 're5', base_dir)
    else:
        out = extraction_dir
    if not os.path.isdir(out):
        os.makedirs(out)
    arc = Arc(file_path=file_path)
    arc.unpack(out)
    mod_files = [os.path.join(root, f) for root, _, files in os.walk(out)
                 for f in files if f.endswith('.mod')]
    parent = bpy.data.objects.new(os.path.basename(file_path), None)
    bpy.context.scene.objects.link(parent)
    for mod_file in mod_files:
        import_mod156(mod_file, out, parent)


def export_mod156(blender_object):
    """
    The blender_object provided should have meshes as children
    """
    objects = [child for child in blender_object.children] + [blender_object]

    bounding_box = get_bounding_box_positions_from_blender_objects(objects)
    mesh_materials = get_materials_from_blender_objects(objects)
    meshes_array, vertex_buffer, index_buffer = _create_meshes_156_array(objects, mesh_materials, bounding_box)

    mod = Mod156(id_magic=b'MOD',
                 version=156,
                 version_rev=1,
                 bone_count=get_bone_count_from_blender_objects(objects),
                 mesh_count=get_mesh_count_from_blender_objects(objects),
                 material_count=len(mesh_materials),
                 vertex_count=get_vertex_count_from_blender_objects(objects),
                 face_count=(ctypes.sizeof(index_buffer) // 2) + 1,
                 edge_count=0,  # TODO: add edge_count
                 vertex_buffer_size=ctypes.sizeof(vertex_buffer),
                 vertex_buffer_2_size=0,
                 texture_count=get_texture_count_from_blender_objects(objects),
                 group_count=6,  # TODO: add group_count
                 bone_palette_count=5,  # TODO add bone_palette_count
                 group_offset=0,
                 sphere_x=0, sphere_y=0, sphere_z=0, sphere_w=0,  # TODO
                 # from Z-up to Y-up, and scaling
                 box_min_x=bounding_box.min_x * 100,
                 box_min_y=bounding_box.min_z * 100 * - 1,
                 box_min_z=bounding_box.min_y * 100,
                 box_min_w=bounding_box.min_w * 100,
                 box_max_x=bounding_box.max_x * 100,
                 box_max_y=bounding_box.max_z * 100 * -1,
                 box_max_z=bounding_box.max_y * 100,
                 box_max_w=bounding_box.max_w * 100,
                 meshes_array=meshes_array,
                 vertex_buffer=vertex_buffer,
                 index_buffer=index_buffer

                 )
    mod.bones_array_offset = get_offset(mod, 'bones_array')
    mod.group_offset = get_offset(mod, 'group_data_array')
    mod.textures_array_offset = get_offset(mod, 'textures_array')
    mod.meshes_array_offset = get_offset(mod, 'meshes_array')
    mod.vertex_buffer_offset = get_offset(mod, 'vertex_buffer')
    mod.vertex_buffer_2_offset = get_offset(mod, 'vertex_buffer')
    mod.index_buffer_offset = get_offset(mod, 'index_buffer')
    return mod
