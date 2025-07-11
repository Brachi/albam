import bmesh
import bpy
import ntpath

from albam.registry import blender_registry
from albam.lib.bone_names import BONES_BODY, BONES_HEAD, NAME_FIXES
from albam.lib.handshaker import handshake, dump_frames, frames_path

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
        row = layout.row()
        row.label(text="Dump frames to json files")
        row = layout.row()
        row.operator("albam.dump_anim_frames", text="Dump frames for left side").side = "left"
        row.operator("albam.dump_anim_frames", text="Dump frames for right side").side = "right"

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
        print(self.filepath)
        dump_frames(self.filepath, ob_armature, 10, self.side)
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
    except ValueError:
        print("the texture has no connections")
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


def set_image_albam_attr(blender_material, app_id, local_path):
    TEX_COMPRESSION = {
        "re0": (24, 20, 25, 31),  # BM alpha, BM no alpha, MM, NM
        "re1": (24, 20, 19, 31),
        "rev1": (23, 19, 25, 31),
        "rev2": (24, 20, 25, 31),
        "re6": (24, 20, 25, 31),
    }

    UNKNOWN_TYPE = {
        "re0": "0x209d",
        "re1": "0x209d",
        "rev1": "0xa09d",
        "rev2": "0x209d",
        "re6": "0x9a",
    }

    if not blender_material or not blender_material.node_tree:
        return
    for tn in blender_material.node_tree.nodes:
        if not tn.type == "TEX_IMAGE":
            continue
        type = blender_texture_to_texture_code(tn)
        if tn.image:
            name = ntpath.splitext(tn.image.name)[0]
        else:
            continue
        if not tn.image.albam_asset.relative_path:
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
        if app_id in UNKNOWN_TYPE:
            tex_157_props.unk_type = UNKNOWN_TYPE.get(app_id)


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
