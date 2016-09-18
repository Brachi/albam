from itertools import chain
import ntpath
import os

try:
    import bpy
    from mathutils import Matrix, Vector
except ImportError:
    pass

from albam.exceptions import BuildMeshError, TextureError
from albam.mtframework import Arc, Mod156, Tex112, KNOWN_ARC_BLENDER_CRASH, CORRUPTED_ARCS
from albam.mtframework.utils import (
    get_vertices_array,
    get_indices_array,
    get_bone_parents_from_mod,
    transform_vertices_from_bbox,
    texture_code_to_blender_texture,

    )
from albam.utils import (
    chunks,
    unpack_half_float,
    strip_triangles_to_triangles_list,
    y_up_to_z_up,
    create_mesh_name,
    )
from albam.registry import blender_registry


@blender_registry.register_function('import', identifier=b'ARC\x00')
def import_arc(blender_object, file_path, **kwargs):
    """Imports an arc file (Resident Evil 5 for only for now) into blender,
    extracting all files to a tmp dir and saving unknown/unused data
    to the armature (if any) for using in exporting
    """

    unpack_dir = kwargs.get('unpack_dir')

    if file_path.endswith(tuple(KNOWN_ARC_BLENDER_CRASH) + tuple(CORRUPTED_ARCS)):
        raise ValueError('The arc file provided is not supported yet, it might crash Blender')

    base_dir = os.path.basename(file_path).replace('.arc', '_arc_extracted')
    out = unpack_dir or os.path.join(os.path.expanduser('~'), '.albam', 're5', base_dir)
    if not os.path.isdir(out):
        os.makedirs(out)
    if not out.endswith(os.path.sep):
        out = out + os.path.sep

    arc = Arc(file_path=file_path)
    arc.unpack(out)

    mod_files = [os.path.join(root, f) for root, _, files in os.walk(out)
                 for f in files if f.endswith('.mod')]
    mod_folders = [os.path.dirname(mod_file.split(out)[-1]) for mod_file in mod_files]

    return {'files': mod_files,
            'kwargs': {'parent': blender_object,
                       'mod_folder': mod_folders[0],  # XXX will break if mods are in different folders
                       'base_dir': out,
                       },
            }


@blender_registry.register_function('import', identifier=b'MOD\x00')
def import_mod(blender_object, file_path, **kwargs):
    base_dir = kwargs.get('base_dir')

    mod = Mod156(file_path=file_path)
    textures = _create_blender_textures_from_mod(mod, base_dir)
    materials = _create_blender_materials_from_mod(mod, blender_object.name, textures)

    meshes = []
    for i, mesh in enumerate(mod.meshes_array):
        name = create_mesh_name(mesh, i, file_path)
        try:
            m = _build_blender_mesh_from_mod(mod, mesh, i, name, materials)
            meshes.append(m)
        except BuildMeshError as err:
            # TODO: logging
            print('Error building mesh {0} for mod {1}'.format(i, file_path))
            print('Details:', err)

    if mod.bone_count:
        armature_name = 'skel_{}'.format(blender_object.name)
        root = _create_blender_armature_from_mod(blender_object, mod, armature_name)
        root.show_x_ray = True
    else:
        root = blender_object

    for i, mesh in enumerate(meshes):
        bpy.context.scene.objects.link(mesh)
        mesh.parent = root
        if mod.bone_count:
            modifier = mesh.modifiers.new(type="ARMATURE", name=blender_object.name)
            modifier.object = root
            modifier.use_vertex_groups = True


def _build_blender_mesh_from_mod(mod, mesh, mesh_index, name, materials):
    imported_vertices = _import_vertices(mod, mesh)
    vertex_locations = imported_vertices['locations']
    indices = get_indices_array(mod, mesh)
    if mod.version == 156:
        indices = strip_triangles_to_triangles_list(indices)
    else:
        start_face = min(indices)
        indices = [i - start_face for i in indices]
    uvs_per_vertex = imported_vertices['uvs']
    weights_per_bone = imported_vertices['weights_per_bone']

    me_ob = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me_ob)

    assert min(indices) >= 0  # Blender crashes if not
    me_ob.from_pydata(vertex_locations, [], chunks(indices, 3))
    me_ob.update(calc_edges=True)
    me_ob.polygons.foreach_set("use_smooth", [True] * len(me_ob.polygons))
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
    # Hiding non main level of detail meshes if they have more than one.
    # For now, assuming that if the mesh has no bones, then it has only one level of detail
    if weights_per_bone and mesh.level_of_detail in (2, 252):
        ob.hide = True
        ob.hide_render = True
    return ob


def _import_vertices(mod, mesh):
    if mod.version == 156:
        return _import_vertices_mod156(mod, mesh)
    elif mod.version == 210:
        return _import_vertices_mod210(mod, mesh)


def _import_vertices_mod210(mod, mesh):
    vertices_array = get_vertices_array(mod, mesh)
    vertices = ((vf.position_x / 32767, vf.position_y / 32767, vf.position_z / 32767)
                for vf in vertices_array)
    vertices = (y_up_to_z_up(vertex_tuple) for vertex_tuple in vertices)

    # TODO: investigate why uvs don't appear above the image in the UV editor
    list_of_tuples = [(unpack_half_float(v.uv_x), unpack_half_float(v.uv_y) * -1) for v in vertices_array]
    return {'locations': list(vertices),
            'uvs': list(chain.from_iterable(list_of_tuples)),
            'weights_per_bone': {}
            }


def _import_vertices_mod156(mod, mesh):
    box_width = abs(mod.box_min_x) + abs(mod.box_max_x)
    box_height = abs(mod.box_min_y) + abs(mod.box_max_y)
    box_length = abs(mod.box_min_z) + abs(mod.box_max_z)

    vertices_array = get_vertices_array(mod, mesh)

    if mesh.vertex_format != 0:
        vertices = (transform_vertices_from_bbox(vf, box_width, box_height, box_length)
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
            print('path {} does not exist'.format(path))
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
        texture_name_no_extension = os.path.splitext(os.path.basename(path))[0]
        texture = bpy.data.textures.new(texture_name_no_extension, type='IMAGE')
        texture.image = image
        textures.append(texture)
        # saving meta data for export
        texture.albam_imported_texture_value_1 = tex.unk_float_1
        texture.albam_imported_texture_value_2 = tex.unk_float_2
        texture.albam_imported_texture_value_3 = tex.unk_float_3
        texture.albam_imported_texture_value_4 = tex.unk_float_4
    return textures


def _create_blender_materials_from_mod(mod, model_name, textures):
    materials = []
    for i, material in enumerate(mod.materials_data_array):
        blender_material = bpy.data.materials.new('{}_{}'.format(model_name, str(i).zfill(2)))
        blender_material.use_transparency = True
        blender_material.alpha = 0.0
        blender_material.specular_intensity = 0.2  # would be nice to get this info from the mod
        materials.append(blender_material)
        for texture_code, tex_index in enumerate(material.texture_indices):
            if not tex_index:
                continue
            try:
                texture_target = textures[tex_index]
            except IndexError:
                # TODO
                print('tex_index {} not found. Texture len(): {}'.format(tex_index, len(textures)))
                continue
            slot = blender_material.texture_slots.add()
            if not texture_target:
                # This means the conversion failed before
                # TODO: logging
                continue
            texture_code_to_blender_texture(texture_code, slot, blender_material)
            slot.texture = texture_target

    return materials


def _create_blender_armature_from_mod(blender_object, mod, armature_name):
    armature = bpy.data.armatures.new(armature_name)
    armature_ob = bpy.data.objects.new(armature_name, armature)
    armature_ob.parent = blender_object

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # deselect all objects
    for i in bpy.context.scene.objects:
        i.select = False
    bpy.context.scene.objects.link(armature_ob)
    bpy.context.scene.objects.active = armature_ob
    armature_ob.select = True
    bpy.ops.object.mode_set(mode='EDIT')

    blender_bones = []
    for i, bone in enumerate(mod.bones_array):
        blender_bone = armature.edit_bones.new(str(i))
        blender_bones.append(blender_bone)
        parents = get_bone_parents_from_mod(bone, mod.bones_array)
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
        # Some very small numbers won't be equal without rounding, but blender will
        # later treat them as equal, so using rounding here
        if round(bone.tail[0], 10) == round(bone.head[0], 10):
            bone.tail[0] += 0.01
        if round(bone.tail[1], 10) == round(bone.head[1], 10):
            bone.tail[1] += 0.01
        if round(bone.tail[2], 10) == round(bone.head[2], 10):
            bone.tail[2] += 0.01

    bpy.ops.object.mode_set(mode='OBJECT')
    assert len(armature.bones) == len(mod.bones_array)
    return armature_ob


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
