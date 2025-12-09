import bmesh
import bpy
import re
from mathutils import Vector, bvhtree


from ..registry import blender_registry
from ..lib.bone_names import BONES_BODY, BONES_HEAD, NAME_FIXES
from ..lib.handshaker import handshake, dump_frames, frames_path

BONE_NAMES = {
    "Body": BONES_BODY,
    "Head": BONES_HEAD
}


def show_message_box(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def mesh_filter(self, object):
    return object.type == 'MESH'


@blender_registry.register_blender_prop_albam(name="meshes")
class AlbamMeshes(bpy.types.PropertyGroup):
    all_meshes: bpy.props.PointerProperty(type=bpy.types.Object, poll=mesh_filter)


@blender_registry.register_blender_prop_albam(name="tools_settings")
class ToolsSettings(bpy.types.PropertyGroup):
    split_uv_seams_transfer_normals: bpy.props.BoolProperty(default=True)
    default_path = "path\\to_textures\\"
    relative_path_to_textures: bpy.props.StringProperty(default=default_path)
    bone_names_enum = bpy.props.EnumProperty(
        name="",
        description="select surface",
        items=[
            ("Body", "Body", "Preset for regular ingame models", 1),
            ("Head", "Head", "Preset for cut-scene heads", 2),
        ],
        default="Body"
    )
    bone_names_preset: bone_names_enum
    vg_a: bpy.props.StringProperty()
    vg_b: bpy.props.StringProperty()


@blender_registry.register_blender_type
class ALBAM_PT_ToolsPanel(bpy.types.Panel):
    '''UI Tool subpanel in 3D view'''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_ToolsPanel"
    bl_label = "Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        op = row.operator('albam.split_uv_seams', text="Split UV Seams")
        op.transfer_normals = context.scene.albam.tools_settings.split_uv_seams_transfer_normals
        row.prop(
            context.scene.albam.tools_settings,
            "split_uv_seams_transfer_normals",
            text="Transfer Normals",
        )
        row = layout.row()
        row.operator('albam.transfer_normals', text="Transfer normals from")
        row.prop(context.scene.albam.meshes, "all_meshes", text="")
        row = layout.row()
        row.operator('albam.autoset_tex_params', text="Autoset texture params")
        row.prop(
            context.scene.albam.tools_settings,
            "relative_path_to_textures",
            text="",)
        row = layout.row()
        row.operator('albam.autorename_bones', text="Autorename bones")
        row.prop(
            context.scene.albam.tools_settings,
            "bone_names_preset",
            text="",)
        row = layout.row()
        row.operator('albam.remove_empty_vertex_groups', text="Remove empty vertex groups")
        row = layout.row()
        row.operator('albam.sort_hair_cards', text="Sort hair cards by distance")
        row = layout.row()
        row.operator('albam.separate_by_material', text="Separate by material")
        row.operator('albam.remove_unused_material_slots', text="Remove unused material slots")
        row = layout.row()
        row.operator('albam.batch_props_paste', text="Batch paste mesh props").prop_type = "mesh"
        row.operator('albam.batch_props_paste', text="Batch paste material props").prop_type = "material"


@blender_registry.register_blender_type
class ALBAM_PT_VGMerger(bpy.types.Panel):
    '''UI Tool for merging vertex'''
    bl_label = "Vertex Groups Merger"
    bl_idname = "ALBAM_PT_VGMerger"
    bl_parent_id = "ALBAM_PT_ToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        scn = context.scene.albam.tools_settings
        row = layout.row()
        row.prop_search(scn, "vg_a", context.active_object, "vertex_groups", text="Group A")
        row = layout.row()
        row.prop_search(scn, "vg_b", context.active_object, "vertex_groups", text="Group B")
        row = layout.row()
        row.operator("albam.vg_merge")

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if selection:
            if selected_meshes:
                return True
        else:
            return False


@blender_registry.register_blender_type
class ALBAM_PT_Handshaker(bpy.types.Panel):
    '''UI Tool for creating posed hands'''
    bl_label = "Handshaker"
    bl_idname = "ALBAM_PT_Handshaker"
    bl_parent_id = "ALBAM_PT_ToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("albam.handshake").filepath = frames_path
        row.prop(context.scene.albam.meshes, "all_meshes", text="")
        # row = layout.row()
        # row.label(text="Dump frames to json files")
        # row = layout.row()
        # row.operator("albam.dump_anim_frames", text="Dump frames for left side").side = "left"
        # row.operator("albam.dump_anim_frames", text="Dump frames for right side").side = "right"

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'ARMATURE']
        if selection:
            if selected_meshes:
                return True
        else:
            return False


@blender_registry.register_blender_type
class ALBAM_OT_SplitUVSeams(bpy.types.Operator):
    '''
    Split vertices that are part of a UV seam (edges of a UV island).
    This is a workaround for a bug in the exporter[1] and necessary to avoid
    artifacts in UV textures displayed in-game.
    [1] https://github.com/Brachi/albam/issues/78
    '''
    bl_idname = "albam.split_uv_seams"
    bl_label = "Split UV seams"

    transfer_normals: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(self, context):
        if not bpy.context.selected_objects:
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if selected_meshes:
            self.split_UV_seams_operator(selected_meshes)
        else:
            show_message_box(message="There is no mesh in the selection")
        return {'FINISHED'}

    def split_UV_seams_operator(self, selected_meshes):
        for mesh in selected_meshes:
            me = mesh.data
            if (self.transfer_normals):
                # create temporal mesh for normal transfer
                temp_list = []
                temp_data = me.copy()
                temp_mesh = mesh.copy()
                temp_mesh.data = temp_data
            # in order to select edges, you need to make sure that
            # previously you deselected everything in the Edit Mode
            # and set the select_mode to 'EDGE'
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_all(action='SELECT')
            split_seams(me)
            bpy.ops.mesh.select_all(action='DESELECT')

            # we need to return back to the OBJECT mode,
            # otherwise, the result won't be seen,
            # see https://blender.stackexchange.com/questions/43127 for info
            bpy.ops.object.mode_set(mode='OBJECT')
            if self.transfer_normals:
                # transfer normals and remove temporal mesh
                temp_list.append(mesh)
                transfer_normals(temp_mesh, temp_list)
                objs = bpy.data.objects
                objs.remove(temp_mesh, do_unlink=True)


@blender_registry.register_blender_type
class ALBAM_OT_TransferNormal(bpy.types.Operator):
    '''Transfer normals from a unified mesh to its parts'''
    bl_idname = "albam.transfer_normals"
    bl_label = "Transfer normals"

    @classmethod
    def poll(self, context):
        source_obj = context.scene.albam.meshes.all_meshes
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if source_obj is None or not bpy.context.selected_objects:
            return False
        if not selected_meshes:
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        source_obj = context.scene.albam.meshes.all_meshes
        target_objs = [obj for obj in selection if obj.type == 'MESH']
        if target_objs and source_obj:
            transfer_normals(source_obj, target_objs)
        else:
            show_message_box(message="There is no mesh in selection")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_AutoSetTexParams(bpy.types.Operator):
    '''Set custom properties for new textures automaticly'''
    bl_idname = "albam.autoset_tex_params"
    bl_label = "Autoset texture params"

    @classmethod
    def poll(self, context):  # pragma: no cover
        if not bpy.context.selected_objects:
            return False
        return True

    def execute(self, context):
        app_id = context.scene.albam.apps.app_selected
        local_path = bpy.context.scene.albam.tools_settings.relative_path_to_textures
        meshes = {ob.data for ob in bpy.context.selected_objects if ob.type == 'MESH'}
        if not meshes:
            meshes = {child.data for child in bpy.context.selected_objects[0].children
                      if child.type == 'MESH'}
        for ob in meshes:
            mat = ob.materials[0]
            set_image_albam_attr(mat, app_id, local_path)

        return {'FINISHED'}


@blender_registry.register_blender_type
class MergeVertexGroups(bpy.types.Operator):
    '''
    Merges weights from groups A and B to group A
    The B group will be removed
    '''
    bl_idname = "albam.vg_merge"
    bl_label = "Merge vertex groups"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = bpy.context.active_object
        scn = bpy.context.scene.albam.tools_settings
        if scn.vg_a == "" or scn.vg_b == "":
            return False
        elif scn.vg_a == scn.vg_b:
            return False
        elif not (scn.vg_a in ob.vertex_groups and scn.vg_b in ob.vertex_groups):
            return False
        else:
            return True

    def execute(self, context):
        scn = bpy.context.scene.albam.tools_settings
        merge_vgroups(scn.vg_a, scn.vg_b)
        scn.vg_b = ""
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_AutoRenameBones(bpy.types.Operator):
    '''Rename bones in the characters armature'''
    bl_idname = "albam.autorename_bones"
    bl_label = "rename character bones"

    @classmethod
    def poll(self, context):
        selection = bpy.context.selected_objects
        armature = [obj for obj in selection if obj.type == 'ARMATURE']
        if not armature:
            return False
        return True

    def execute(self, context):
        app_id = context.scene.albam.apps.app_selected
        bone_names_preset = context.scene.albam.tools_settings.bone_names_preset
        selection = bpy.context.selected_objects
        armature_ob = [obj for obj in selection if obj.type == 'ARMATURE']
        rename_bones(armature_ob[0], app_id, bone_names_preset)
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_DumpFrames(bpy.types.Operator):
    '''Dump Animation frames to json'''
    bl_idname = "albam.dump_anim_frames"
    bl_label = "Dump animation frames"
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath to dumped frames",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    filepath: FILEPATH
    HAND_SIDE = bpy.props.EnumProperty(
        name="Side",
        description="Side of the character to dump frames for",
        default="left",
        options={'SKIP_SAVE'},
        items=[
            ('left', "Left", "Dump frames for left side"),
            ('right', "Right", "Dump frames for right side"),
        ],
    )
    EXTENSION_FILTER = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
    )
    side: HAND_SIDE
    filter_glob: EXTENSION_FILTER
    filename = bpy.props.StringProperty(default="")

    def invoke(self, context, event):  # pragma: no cover
        self.filepath = context.active_object.name + ".json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ob_armature = self.get_selected_armature(context)
        app_id = context.scene.albam.apps.app_selected
        print(self.filepath)
        dump_frames(self.filepath, ob_armature, 10, self.side, app_id)
        return {'FINISHED'}

    def get_selected_armature(self, context):
        selection = bpy.context.selected_objects
        armatures = [obj for obj in selection if obj.type == 'ARMATURE']
        try:
            ob = armatures[0]
        except KeyError:
            ob = None
        return ob


@blender_registry.register_blender_type
class ALBAM_OT_ApplyFrames(bpy.types.Operator):
    '''Apply Animation frames to an armature'''
    bl_idname = "albam.handshake"
    bl_label = "Apply animation frames"
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath to dumped frames",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    filepath: FILEPATH

    def invoke(self, context, event):  # pragma: no cover
        # self.filepath = self.FILEPATH # frames_dir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        source_obj = context.scene.albam.meshes.all_meshes
        handshake(self.filepath, source_obj)
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_RemoveEmptyVertexGroups(bpy.types.Operator):
    '''Remove vertex groups with 0 skin weighs'''
    bl_idname = "albam.remove_empty_vertex_groups"
    bl_label = "remove empty vertex groups"

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if not selected_meshes:
            return False
        return True

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        selection = bpy.context.scene.objects
        scene_meshes = [obj for obj in selection if obj.type == 'MESH']

        for ob in scene_meshes:
            ob.update_from_editmode()

            vgroup_used = {i: False for i, k in enumerate(ob.vertex_groups)}

            for v in ob.data.vertices:
                for g in v.groups:
                    if g.weight > 0.0:
                        vgroup_used[g.group] = True

            for i, used in sorted(vgroup_used.items(), reverse=True):
                if not used:
                    ob.vertex_groups.remove(ob.vertex_groups[i])
        show_message_box(message="Removing complete")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_SeparateByMaterial(bpy.types.Operator):
    '''Separate selected mesh by material'''
    bl_idname = "albam.separate_by_material"
    bl_label = "Separate by material"
    bl_options = {'UNDO'}
    bl_description = "Separate selected mesh by material"

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if not selected_meshes:
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if selected_meshes:
            bpy.ops.object.select_all(action='DESELECT')
            for mesh_ob in selected_meshes:
                try:
                    target_collection = mesh_ob.users_collection[0]
                except IndexError:
                    target_collection = bpy.context.collection
                duplicate = mesh_ob.copy()
                duplicate.data = mesh_ob.data.copy()
                target_collection.objects.link(duplicate)
                bpy.ops.object.select_all(action='DESELECT')
                duplicate.select_set(True)

                # Make the clone active
                bpy.context.view_layer.objects.active = duplicate
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='MATERIAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                show_message_box(message=f"Mesh {mesh_ob.name} was separated")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_RemoveUnusedMaterialSlots(bpy.types.Operator):
    ''''Remove unused material slots from selected meshes'''
    bl_idname = "albam.remove_unused_material_slots"
    bl_label = "Remove unused material slots"
    bl_options = {'UNDO'}
    bl_description = "Remove unused material slots from selected meshes"

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if not selected_meshes:
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if selected_meshes:
            for mesh_ob in selected_meshes:
                mesh = mesh_ob.data
                used_materials = set()
                for poly in mesh.polygons:
                    used_materials.add(poly.material_index)
                for i in reversed(range(len(mesh.materials))):
                    if i not in used_materials:
                        mesh.materials.pop(index=i)
            show_message_box(message="Removing complete")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_BatchPropsPaste(bpy.types.Operator):
    '''Batch paste Albam custom properties'''
    bl_idname = "albam.batch_props_paste"
    bl_label = "Batch paste Albam custom properties"
    bl_options = {'UNDO'}

    prop_type: bpy.props.StringProperty(
        name="Property Type",
        description="Type of the property to paste",
        default="",
    )

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if not selected_meshes:
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if selected_meshes:
            for mesh_ob in selected_meshes:
                if self.prop_type == "mesh":
                    prop = mesh_ob.data
                else:
                    prop = mesh_ob.material_slots[0].material
                paste_props(prop)
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_SortHairCards(bpy.types.Operator):
    '''Sort hair cards by distance'''
    bl_idname = "albam.sort_hair_cards"
    bl_label = "sort hair cards by distance"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if not selected_meshes or context.scene.albam.meshes.all_meshes is None:
            return False
        return True

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        source_obj = context.scene.albam.meshes.all_meshes
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH' and obj != source_obj]
        sort_hair_cards(source_obj, selected_meshes, debug_draw=True)
        # merge_hair_cards(selected_meshes)
        return {'FINISHED'}


def split_seams(me):
    bm = bmesh.from_edit_mesh(me)
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    # old seams
    old_seams = [e for e in bm.edges if e.seam]
    # unmark
    for e in old_seams:
        e.seam = False
    # mark seams from uv islands
    bpy.ops.uv.seams_from_islands()
    seams = [e for e in bm.edges if e.seam]
    # split on seams
    bmesh.ops.split_edges(bm, edges=seams)
    # re instate old seams.. could clear new seams.
    for e in old_seams:
        e.seam = True
    bmesh.update_edit_mesh(me)


def transfer_normals(source_obj, target_objs):
    for obj in target_objs:
        if obj != source_obj:
            modifier = obj.modifiers.new(name="Transfer Normals", type='DATA_TRANSFER')
            modifier.use_loop_data = True
            modifier.data_types_loops = {'CUSTOM_NORMAL'}
            modifier.object = source_obj
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=modifier.name)


def blender_texture_to_texture_code(blender_texture_image_node):
    '''
    This function returns a type ID of the image texture node depending on node connection
    '''
    texture_code = None
    color_out = blender_texture_image_node.outputs['Color']
    try:
        socket_name = color_out.links[0].to_socket.name
    except IndexError:
        print("The texture node {} has no connections".format(blender_texture_image_node))
        return None

    tex_codes_mapper = {
        'Diffuse BM': 0,
        'Normal NM': 1,
        'Specular MM': 2,
        'Lightmap LM': 3,
        'Alpha Mask AM': 5,
        'Environment CM': 6,
        'Detail DNM': 7
    }

    texture_code = tex_codes_mapper.get(socket_name)
    if texture_code is None:
        return None

    return texture_code


def strict_sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)


def set_image_albam_attr(blender_material, app_id, local_path):
    TEX_COMPRESSION = {
        "re0": (24, 20, 25, 31),  # BM alpha, BM no alpha, MM, NM
        "re1": (24, 20, 19, 31),
        "rev1": (23, 19, 25, 31),
        "rev2": (24, 20, 25, 31),
        "re6": (24, 20, 25, 31),
        "dd": (24, 20, 25, 31),
    }

    VERSION = {
        "re0": "0x9d",
        "re1": "0x9d",
        "rev1": "0x9d",
        "rev2": "0x9d",
        "re6": "0x9a",
        "dd": "0x99",
    }

    UNK = {
        "re0": 32,
        "re1": 32,
        "rev1": 160,
        "rev2": 32,
        "re6": 0,
    }

    if not blender_material or not blender_material.node_tree:
        return
    for tn in blender_material.node_tree.nodes:
        if not tn.type == "TEX_IMAGE":
            continue
        type = blender_texture_to_texture_code(tn)
        if tn.image:
            name = tn.image.name.split(".")[0]
            name = strict_sanitize(name)
        else:
            continue
        tn.image.albam_asset.relative_path = local_path + name + '.tex'
        tn.image.albam_asset.app_id = app_id
        tex_157_props = tn.image.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if app_id in TEX_COMPRESSION:
            tex_compr_preset = TEX_COMPRESSION.get(app_id)
            if type == 0:
                tex_157_props.compression_format = tex_compr_preset[1]
            if type == 1:
                tex_157_props.compression_format = tex_compr_preset[3]
            if type == 2:
                tex_157_props.compression_format = tex_compr_preset[2]
            if type == 7:
                tex_157_props.compression_format = tex_compr_preset[3]
        if app_id in UNK:
            tex_157_props.unk = UNK.get(app_id)
        if app_id in VERSION:
            tex_157_props.version = VERSION.get(app_id)


def rename_bones(armature_ob, app_id, body_type):
    names_preset = BONE_NAMES.get(body_type)
    fixes_preset = NAME_FIXES.get(body_type)
    fixed_name = fixes_preset.get(app_id, None)
    bone_name = None
    if fixed_name:
        for k, v in fixed_name.items():
            names_preset[k] = v
    armature = armature_ob.data
    bones = armature.bones
    for bone in bones:
        reference_bone_id = bone.get('mtfw.anim_retarget')
        if reference_bone_id:
            bone_name = names_preset.get(int(reference_bone_id), None)
        else:
            continue
        if bone_name:
            bone.name = bone_name


def merge_vgroups(vg_a, vg_b):
    # based on https://blender.stackexchange.com/a/42779

    # Get both groups and add them into third
    ob = bpy.context.active_object
    if (vg_a in ob.vertex_groups and vg_b in ob.vertex_groups):

        vg_merged = ob.vertex_groups.new(name=vg_a + "+" + vg_b)

        for id, vert in enumerate(ob.data.vertices):
            available_groups = [v_group_elem.group for v_group_elem in vert.groups]
            A = B = 0
            if ob.vertex_groups[vg_a].index in available_groups:
                A = ob.vertex_groups[vg_a].weight(id)
            if ob.vertex_groups[vg_b].index in available_groups:
                B = ob.vertex_groups[vg_b].weight(id)

            # only add to vertex group is weight is > 0
            sum = A + B
            if sum > 0:
                vg_merged.add([id], sum, 'REPLACE')
        # remove two vertex groups and rename the third as Group A
        ob.vertex_groups.remove(ob.vertex_groups[vg_a])
        ob.vertex_groups.remove(ob.vertex_groups[vg_b])
        vg_merged.name = vg_a


def paste_props(context_item):
    albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
    app_id = albam_asset.app_id
    custom_props = context_item.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_props_sec = context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)

    props_name = context_item.albam_custom_properties.APPID_MAP[app_id]
    buff = bpy.context.scene.albam.clipboard.get_buffer()
    to_paste = buff.get(app_id, {}).get(props_name, {})

    for k, v in to_paste.items():
        setattr(custom_props, k, v)

    for sec_prop_name, sec_prop in custom_props_sec.items():
        to_paste = buff.get(app_id, {}).get(sec_prop_name, {})
        for k, v in to_paste.items():
            setattr(sec_prop, k, v)


def _debug_draw_bvh_rays(rays, ob_name):
    rvis_name = ob_name + "_rays_viz"
    rviz_ob = bpy.data.objects.get(rvis_name, None)
    debug_collection = bpy.data.collections.get("DebugDraw")
    if debug_collection is None:
        debug_collection = bpy.data.collections.new("DebugDraw")
        bpy.context.scene.collection.children.link(debug_collection)

    if rviz_ob:
        rvis_mesh = rviz_ob.data
    else:
        rvis_mesh = bpy.data.meshes.new(rvis_name)
        rviz_ob = bpy.data.objects.new(rvis_name, rvis_mesh)
        debug_collection.objects.link(rviz_ob)

    bm_vis = bmesh.new()

    for origin, hit_loc in rays:
        v1 = bm_vis.verts.new(origin)
        v2 = bm_vis.verts.new(hit_loc)
        bm_vis.edges.new((v1, v2))

    bm_vis.to_mesh(rvis_mesh)
    bm_vis.free()


# Get minimal distance to the head
def min_distance_to_target(obj, target_bvh):
    bm = bmesh.new()
    bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
    bm.verts.ensure_lookup_table()
    min_dist = float('inf')
    for v in bm.verts:
        world_v = obj.matrix_world @ v.co
        hit = target_bvh.find_nearest(world_v)
        if hit:
            loc, normal, index, dist = hit
            min_dist = min(min_dist, dist)
    return min_dist


# Check overlaping
def is_blocked(card_ob, v_from, v_to, bvh_list):
    direction = (v_to - v_from).normalized()
    length = (v_to - v_from).length
    hit_objs = set()
    exclude_obj = []
    exclude_obj.append(card_ob)
    # Check if the ray the goes from card to body is blocked by other cards
    for bvh, target_ob in bvh_list:
        if target_ob in exclude_obj:
            continue
        hit = bvh.ray_cast(v_from, direction, length)
        if hit[0]:
            hit_objs.add(target_ob)
            exclude_obj.append(target_ob)
            # The index increments even if rays hit 2 objects with the same alpha priority, this should fix it
            #emitter_props = _get_mesh_albam_props(card_ob)
            #emitter_ap = emitter_props.alpha_priority if emitter_props else card_ob.get('order', 0)
            #target_props = _get_mesh_albam_props(target_ob)
            ##target_ap = target_props.alpha_priority if target_props else target_ob.get('order', 0)
            #if emitter_ap <= target_ap or target_ap == 0:
            #    try:
            #        emitter_props.alpha_priority = target_ap + 1
            #    except AttributeError:
            #        print("Object {} has no Albam custom properties".format(card_ob.name))
            #    card_ob["order"] = target_ap + 1
    #if card_ob.name == "helgast_winter_fur.092":
    #    print("Card {} blocked by {}".format(card_ob.name, [ob.name for ob in hit_objs]))
    return hit_objs


def is_point_inside_nearest(point_world: Vector, bvh, eps=1e-6) -> bool:
    """
    Fast heuristic: take nearest surface point and check dot(normal, point - nearest).
    For a closed manifold outward normal, dot < 0 => point is inside.
    """
    res = bvh.find_nearest(point_world)
    if not res:
        return False
    nearest_co, nearest_no, _, _ = res
    vec = point_world - nearest_co
    return nearest_no.dot(vec) < -eps


def _get_mesh_albam_props(obj):
    albam_asset = obj.data.albam_custom_properties.get_parent_albam_asset()
    if not albam_asset:
        return None
    app_id = albam_asset.app_id
    custom_props = obj.data.albam_custom_properties.get_custom_properties_for_appid(app_id)
    return custom_props


def _join_objects(objects_to_join, aprior=None):
    """
    Joins multiple Blender objects into a single new object using bmesh,
    correctly applying all world transformations.
    """
    if not objects_to_join:
        print("No objects provided for joining.")
        return None

    # bmesh instance will hold merged geometry
    bm = bmesh.new()
    # bmesh data should be stored into the mesh
    temp_mesh = bpy.data.meshes.new("temp_mesh_data")
    obj_name = ""
    target_col = None

    for obj in objects_to_join:
        if obj.type == 'MESH':
            if not obj_name:
                obj_name = obj.name
            if target_col is None:
                try:
                    target_col = obj.users_collection[0]
                except IndexError:
                    target_col = bpy.context.collection
            # Get the object's mesh data and world transformation matrix
            mesh = obj.data
            matrix_world = obj.matrix_world

            # Create a temporary bmesh from the object's mesh data
            # The 'from_mesh' method loads local coordinates
            temp_bm = bmesh.new()
            temp_bm.from_mesh(mesh)

            # Apply the object's world matrix to transform vertices to world space
            # This is crucial for robust joining
            temp_bm.transform(matrix_world)

            # Add the transformed geometry to the main BMesh instance
            # bmesh objects are inherently additive
            # bm.from_mesh(temp_bm.to_mesh(temp_mesh))
            temp_bm.to_mesh(temp_mesh)
            bm.from_mesh(temp_mesh)
            temp_bm.free()

    # Create a new mesh data-block and object
    obj_name = obj_name.split(".")[0] + "_ap_" + str(aprior) if aprior else obj_name
    new_mesh = bpy.data.meshes.new(obj_name + "_data")
    bm.to_mesh(new_mesh)
    bm.free()

    new_object = bpy.data.objects.new(obj_name, new_mesh)
    target_col.objects.link(new_object)

    # Remove original objects
    for obj in objects_to_join:
        bpy.data.objects.remove(obj, do_unlink=True)

    return new_object


def _get_max_alpha_priority(cards_objs):
    max_aprior = 0
    for card_ob in cards_objs:
        custom_props = _get_mesh_albam_props(card_ob)
        if custom_props:
            if custom_props.alpha_priority > max_aprior:
                max_aprior = custom_props.alpha_priority
    return max_aprior


def sort_hair_cards(body_ob, cards_objs, debug_draw=False):
    body_bm = bmesh.new()
    body_bm.from_object(body_ob, bpy.context.evaluated_depsgraph_get())
    body_bm.verts.ensure_lookup_table()
    body_bm.faces.ensure_lookup_table()
    body_bvh = bvhtree.BVHTree.FromBMesh(body_bm)
    body_bm.free()

    # Sorting hair cards by distance, probably unnesessary
    cards_objs_sorted = sorted(cards_objs, key=lambda o: min_distance_to_target(o, body_bvh))
    count = len(cards_objs_sorted)

    # draw distance to cards as a blue-red gradient in vertex colors
    if debug_draw:
        for i, obj in enumerate(cards_objs_sorted):
            mesh = obj.data
            if not mesh.vertex_colors:
                vcol_layer = mesh.vertex_colors.new(name="Col")
            else:
                vcol_layer = mesh.vertex_colors.active
            t = i / (count - 1) if count > 1 else 0
            color = (t, 0.0, 1.0 - t, 1.0)  # RGBA
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    vcol_layer.data[loop_index].color = color

    # Set alpha priority index to 0 for all hair cards
    for card_ob in cards_objs_sorted:
        custom_props = _get_mesh_albam_props(card_ob)
        if custom_props:
            custom_props.alpha_priority = 0
        card_ob['order'] = 0

    # Build the BVH tree for cards
    bvh_list = []
    deps = bpy.context.evaluated_depsgraph_get()
    for card_ob in cards_objs_sorted:
        bm = bmesh.new()
        bm.from_object(card_ob, bpy.context.evaluated_depsgraph_get())
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bvh = bvhtree.BVHTree.FromBMesh(bm)
        bvh_list.append((bvh, card_ob))
        bm.free()

    visited = set()
    processing = set()
    blockers_cache = {}

    def compute_blockers(card_ob, debug_draw=False):
        # cached
        if card_ob in blockers_cache:
            return blockers_cache[card_ob]
        if card_ob not in processing:
            return set()
        # if card_ob in processing:
        #    # cycle detected — return empty set to break cycle
        #    return set()
        # processing.add(card_ob)
        debug_rays = []

        bm = bmesh.new()
        bm.from_object(card_ob, deps)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        sample_points = []
        # Add vertices as sample points
        for v in bm.verts:
            sample_points.append(card_ob.matrix_world @ v.co)
        # Add centers of faces as sample points
        for face in bm.faces:
            center = sum((card_ob.matrix_world @ v.co for v in face.verts), Vector()) / len(face.verts)
            sample_points.append(center)

        blocked_objs = set()
        for world_v in sample_points:
            hit = body_bvh.find_nearest(world_v)
            if hit:
                loc, normal, index, dist = hit
                debug_rays.append((world_v, loc))
                blocked = is_blocked(card_ob, world_v, loc, bvh_list)
                if blocked:
                    blocked_objs.update(blocked)

        bm.free()
        # ensure self not included
        blocked_objs.discard(card_ob)
        blockers_cache[card_ob] = blocked_objs
        processing.remove(card_ob)
        if debug_draw:
            _debug_draw_bvh_rays(debug_rays, card_ob.name)
        return blocked_objs

    def process_card_recursive(card_ob):
        if card_ob in visited:
            return
        # detect and avoid deep cycles
        if card_ob in processing:
            return
        processing.add(card_ob)
        blockers = compute_blockers(card_ob, debug_draw=debug_draw)

        # process blockers first if they are not yet visited
        for b in list(blockers):
            if b not in visited:
                process_card_recursive(b)

        # now assign priority for this card based on blockers and visited set
        card_props = _get_mesh_albam_props(card_ob)
        # if all blockers are already visited -> set priority to max(blockers)+1 else set to len(blockers)
        if blockers.issubset(visited):
            max_ap = _get_max_alpha_priority(blockers) if blockers else 0
            if card_props:
                card_props.alpha_priority = max_ap + 1
            card_ob['order'] = max_ap + 1
        else:
            # some blockers unprocessed (cycle or external) — use fallback count
            if card_props:
                card_props.alpha_priority = len(blockers)
            card_ob['order'] = len(blockers)

        visited.add(card_ob)
        processing.discard(card_ob)

    for i, card_ob in enumerate(cards_objs_sorted):
        if card_ob not in visited:
            process_card_recursive(card_ob)


def merge_hair_cards(objs):
    alpha_prior_groups = {}
    for obj in objs:
        albam_props = _get_mesh_albam_props(obj)
        if alpha_prior_groups.get(albam_props.alpha_priority) is None:
            alpha_prior_groups[albam_props.alpha_priority] = []
        alpha_prior_groups[albam_props.alpha_priority].append(obj)

    for alpha_idx in alpha_prior_groups.keys():
        continue
        _join_objects(alpha_prior_groups[alpha_idx], alpha_idx)
