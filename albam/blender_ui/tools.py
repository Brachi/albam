import bmesh
import bpy
import os

from albam.registry import blender_registry


def show_message_box(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


@blender_registry.register_blender_prop_albam(name="tools_settings")
class ToolsSettings(bpy.types.PropertyGroup):
    split_uv_seams_transfer_normals: bpy.props.BoolProperty(default=False)
    local_path_to_textures: bpy.props.StringProperty(default="path\\to_textures\\")


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
        row.prop(context.scene, "albam_meshes", text="")
        row = layout.row()
        row.operator('albam.autoset_tex_params', text="Autoset texture params")
        row.prop(
            context.scene.albam.tools_settings,
            "local_path_to_textures",
            text="",)


@blender_registry.register_blender_type
class ALBAM_OT_SplitUVSeams(bpy.types.Operator):
    """
    Split vertices that are part of a UV seam (edges of a UV island).
    This is a workaround for a bug in the exporter[1] and necessary to avoid
    artifacts in UV textures displayed in-game.
    [1] https://github.com/Brachi/albam/issues/78
    """
    bl_idname = "albam.split_uv_seams"
    bl_label = "Split UV seams"

    transfer_normals : bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(self, context):  # pragma: no cover
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
    """Transfer normals from a unified mesh to its parts"""
    bl_idname = "albam.transfer_normals"
    bl_label = "Transfer normals"

    @classmethod
    def poll(self, context):
        source_obj = context.scene.albam_meshes
        if source_obj is None or not bpy.context.selected_objects:
            return False
        if source_obj.type != 'MESH':
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        source_obj = context.scene.albam_meshes
        target_objs = [obj for obj in selection if obj.type == 'MESH']
        if target_objs and source_obj:
            transfer_normals(source_obj, target_objs)
        else:
            show_message_box(message="There is no mesh in selection")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_AutoSetTexParams(bpy.types.Operator):
    """Set custom properties for new textures automaticly"""
    bl_idname = "albam.autoset_tex_params"
    bl_label = "Autoset texture params"

    @classmethod
    def poll(self, context):  # pragma: no cover
        if not bpy.context.selected_objects:
            return False
        return True

    def execute(self, context):
        app_id = context.scene.albam.file_explorer.app_selected
        local_path = bpy.context.scene.albam.tools_settings.local_path_to_textures
        meshes = {ob.data for ob in bpy.context.selected_objects if ob.type == 'MESH'}
        if not meshes:
            meshes = {child.data for child in bpy.context.selected_objects[0].children if child.type == 'MESH'}
        for ob in meshes:
            mat = ob.materials[0]
            set_image_albam_attr(mat, app_id, local_path)

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
    This function return a type ID of the image texture node dependind of node connetion
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
    if blender_material:
        if blender_material.node_tree:
            for tn in blender_material.node_tree.nodes:
                if tn.type == 'TEX_IMAGE':
                    type = blender_texture_to_texture_code(tn)
                    name = os.path.splitext(tn.image.name)[0]
                    if not tn.image.albam_asset.relative_path:
                        tn.image.albam_asset.relative_path = local_path + name + '.tex'
                    tn.image.albam_asset.app_id = app_id
                    if app_id in ["re0", "re1", "rev1", "rev2"]:
                        diff_comp = 20
                        if type == 0:
                            if app_id == "re1":
                                diff_comp = 19
                            tn.image.albam_custom_properties.tex_157.compression_format = diff_comp
                        if type == 1:
                            tn.image.albam_custom_properties.tex_157.compression_format = 31
                        if type == 2:
                            tn.image.albam_custom_properties.tex_157.compression_format = 25
                        if type == 7:
                            tn.image.albam_custom_properties.tex_157.compression_format = 31
