from base64 import b64encode
from itertools import chain
import ntpath
import os

try:
    import bpy
    from mathutils import Matrix, Vector
    from bpy.props import StringProperty as StrProp, FloatProperty
except ImportError:
    pass

from albam.exceptions import BuildMeshError, TextureError
from albam.mtframework import Arc, Mod156, Mod210, Tex112
from albam.mtframework.utils import (
    get_vertices_array,
    get_indices_array,
    get_bone_parents_from_mod,
    transform_vertices_from_bbox,
    )
from albam.utils import (
    chunks,
    unpack_half_float,
    strip_triangles_to_triangles_list,
    y_up_to_z_up,
    create_mesh_name,
    )


def import_arc(file_path, extraction_dir=None, context_scene=None):
    '''Imports an arc file (Resident Evil 5 for only for now) into blender,
    extracting all files to a tmp dir and saving unknown/unused data
    to the armature (if any) for using in exporting'''

    base_dir = os.path.basename(file_path).replace('.arc', '_arc_extracted')
    out = extraction_dir or os.path.join(os.path.expanduser('~'), '.albam', 're5', base_dir)
    if not os.path.isdir(out):
        os.makedirs(out)
    if not out.endswith(os.path.sep):
        out = out + os.path.sep
    arc = Arc(file_path=file_path)
    arc.unpack(out)

    mod_files = [os.path.join(root, f) for root, _, files in os.walk(out)
                 for f in files if f.endswith('.mod')]
    mod_dirs = [os.path.dirname(mod_file.split(out)[-1]) for mod_file in mod_files]
    parent = bpy.data.objects.new(os.path.basename(file_path), None)
    bpy.context.scene.objects.link(parent)

    # Saving arc to main object
    albam_arc = StrProp(options={'HIDDEN'}, subtype='BYTE_STRING')
    bpy.types.Object.albam_arc = albam_arc
    parent.albam_arc = b64encode(bytes(arc))

    for i, mod_file in enumerate(mod_files):
        mod_dir = mod_dirs[i]
        import_mod(mod_file, out, parent, mod_dir)

    # Addding the name of the imported item so then it can be selected
    # from a list for exporting. Exporting models without a base model,
    # at least for models with skeleton doesn't make much sense, plus
    # the arc files contain a lot of other files that are not imported, but
    # saved in the blend file
    new_albam_imported_item = context_scene.albam_items_imported.add()
    new_albam_imported_item.name = os.path.basename(file_path)


def import_mod(file_path, base_dir, parent=None, mod_dir_path=None):
    model_name = os.path.basename(file_path)
    mod = Mod156(file_path=file_path)
    if mod.version == 156:
        textures = _create_blender_textures_from_mod(mod, base_dir)
        materials = _create_blender_materials_from_mod(mod, model_name, textures)
    elif mod.version == 210:
        mod = Mod210(file_path=file_path)
        textures = []  # TODO: get them from mrl file
        materials = []

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
        _save_mod_data_to_object(mod, armature_ob, mod_dir_path)
    else:
        parent_empty = bpy.data.objects.new(model_name, None)
        parent_empty.parent = parent
        _save_mod_data_to_object(mod, parent_empty, mod_dir_path)
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
    # XXX Quick hack

    albam_texture_unk_01 = FloatProperty(options={'HIDDEN'})
    albam_texture_unk_02 = FloatProperty(options={'HIDDEN'})
    albam_texture_unk_03 = FloatProperty(options={'HIDDEN'})
    albam_texture_unk_04 = FloatProperty(options={'HIDDEN'})

    bpy.types.Texture.albam_texture_unk_01 = albam_texture_unk_01
    bpy.types.Texture.albam_texture_unk_02 = albam_texture_unk_02
    bpy.types.Texture.albam_texture_unk_03 = albam_texture_unk_03
    bpy.types.Texture.albam_texture_unk_04 = albam_texture_unk_04

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
        # saving meta data for export XXX quick hack
        texture.albam_texture_unk_01 = tex.unk_float_1
        texture.albam_texture_unk_02 = tex.unk_float_2
        texture.albam_texture_unk_03 = tex.unk_float_3
        texture.albam_texture_unk_04 = tex.unk_float_4
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
                # TODO: 3, 4, 5, 6,
        materials.append(blender_material)
    return materials


def _save_mod_data_to_object(mod, blender_object, dirpath=None):
    """
    This function should be generalized when more formats are added
    Base64 is used because when saving bytes to a StringProperty, the get
    cut off at the first null byte. That might be a bug.
    """
    albam_mod156 = StrProp(options={'HIDDEN'}, subtype='BYTE_STRING')
    mod156_dirpath = StrProp(options={'HIDDEN'})

    bpy.types.Object.albam_mod156 = albam_mod156
    bpy.types.Object.albam_mod156_dirpath = mod156_dirpath

    blender_object.albam_mod156 = b64encode(bytes(mod))
    blender_object.albam_mod156_dirpath = dirpath if dirpath else ''


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
        if bone.tail == bone.head:
            bone.tail += Vector((0.01, 0.01, 0.01))

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_ob


def _build_blender_mesh_from_mod(mod, mesh, mesh_index, file_path, materials):
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
