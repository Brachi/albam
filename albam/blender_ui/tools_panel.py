import bmesh
import bpy
import re
import gpu
import blf
from pathlib import Path
from bpy_extras import view3d_utils
from mathutils.bvhtree import BVHTree
from gpu_extras.batch import batch_for_shader


from ..registry import blender_registry
from ..engines.mtfw.bone import get_anim_retarget, get_mirror, guess_mirrors, set_mirror
from ..lib.bone_names import BONES_BODY, BONES_HEAD, NAME_FIXES
from ..lib.tools.handshaker import handshake, dump_frames, frames_path
from ..lib.tools.bake_of_light import bake_light
from ..lib.tools.card_sorter import sort_hair_cards
from ..lib.common_op import _get_mesh_albam_props
from ..lib.tools.face_painter import SBC_COLOR_PALETTE, NAV_FACE_FLAGS_DESC, SBC_RUNTIME_ATTR_DESC
from ..lib.misc import number_to_color

BONE_NAMES = {
    "Body": BONES_BODY,
    "Head": BONES_HEAD
}

DEV_MODE = False
WORKSPACE_TOOLS = []
FACE_PAINTER_TOOL_ID = "albam.material_painter_tool"
FACE_PAINTER_TIMER_INTERVAL = 0.1
_FACE_PAINTER_SHADING_STATES = {}
_FACE_PAINTER_BVH_CACHE = {}


def _restore_face_painter_shading(state):
    try:
        state["space"].shading.type = state["shading_type"]
    except (AttributeError, ReferenceError):
        pass


def _track_face_painter_area(area):
    area_key = area.as_pointer()
    state = _FACE_PAINTER_SHADING_STATES.get(area_key)
    if state:
        try:
            if state["area"] == area:
                return
        except ReferenceError:
            pass
        _restore_face_painter_shading(state)

    space = area.spaces.active
    _FACE_PAINTER_SHADING_STATES[area_key] = {
        "area": area,
        "space": space,
        "shading_type": space.shading.type,
    }
    space.shading.type = 'SOLID'


def _get_face_painter_bvh(mesh_data, edit_mesh):
    """Reuse the BVH while the tool is active and mesh geometry is unchanged."""
    mesh_key = mesh_data.as_pointer()
    cached_bvh = _FACE_PAINTER_BVH_CACHE.get(mesh_key)
    if cached_bvh:
        try:
            if cached_bvh["mesh_data"] == mesh_data:
                return cached_bvh["bvh"]
        except ReferenceError:
            pass

    edit_mesh.faces.ensure_lookup_table()
    bvh = BVHTree.FromBMesh(edit_mesh)
    _FACE_PAINTER_BVH_CACHE[mesh_key] = {
        "mesh_data": mesh_data,
        "bvh": bvh,
    }
    return bvh


def _face_painter_lifecycle_timer():
    active_area_keys = set()
    window_manager = bpy.context.window_manager
    if window_manager:
        for window in window_manager.windows:
            try:
                active_object = window.view_layer.objects.active
                if (
                    not active_object or
                    active_object.type != 'MESH' or
                    active_object.mode != 'EDIT'
                ):
                    continue

                tool = window.workspace.tools.from_space_view3d_mode(
                    'EDIT_MESH',
                    create=False,
                )
                if not tool or tool.idname != FACE_PAINTER_TOOL_ID:
                    continue

                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        active_area_keys.add(area.as_pointer())
                        _track_face_painter_area(area)
            except (AttributeError, ReferenceError):
                continue

    for area_key, state in list(_FACE_PAINTER_SHADING_STATES.items()):
        if area_key not in active_area_keys:
            _restore_face_painter_shading(state)
            del _FACE_PAINTER_SHADING_STATES[area_key]

    if not active_area_keys:
        _FACE_PAINTER_BVH_CACHE.clear()

    return FACE_PAINTER_TIMER_INTERVAL


def _ensure_face_painter_lifecycle_timer():
    if not bpy.app.timers.is_registered(_face_painter_lifecycle_timer):
        bpy.app.timers.register(
            _face_painter_lifecycle_timer,
            first_interval=FACE_PAINTER_TIMER_INTERVAL,
            persistent=True,
        )


def _stop_face_painter_lifecycle_timer():
    if bpy.app.timers.is_registered(_face_painter_lifecycle_timer):
        bpy.app.timers.unregister(_face_painter_lifecycle_timer)

    for state in _FACE_PAINTER_SHADING_STATES.values():
        _restore_face_painter_shading(state)
    _FACE_PAINTER_SHADING_STATES.clear()
    _FACE_PAINTER_BVH_CACHE.clear()


def register_workspace_tools():
    for tool_cls in WORKSPACE_TOOLS:
        bpy.utils.register_tool(
            tool_cls,
            after=(tool_cls.after,) if tool_cls.after != "" else None,
            group=(tool_cls.after == ""),
        )
    _ensure_face_painter_lifecycle_timer()


def unregister_workspace_tools():
    _stop_face_painter_lifecycle_timer()
    for tool_cls in reversed(WORKSPACE_TOOLS):
        bpy.utils.unregister_tool(tool_cls)


def show_message_box(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def mesh_filter(self, object):
    return object.type == 'MESH'


def armature_filter(self, object):
    return object.type == 'ARMATURE'


def face_preset_update(self, context):
    presets = {
        'PhysWall': (0x10, 0),
        'IntWall': (0x13, 0),
        'SpecWall': (0x0, 0x20000000),
        'Ground': (0x20, 0),
        'Leap': (0x0, 0x10000000),
        'Auto': (0, 0)
    }
    id = context.scene.albam.tools_settings.face_preset
    sur, spec = presets[id]
    context.scene.albam.tools_settings.surface_attr = sur
    context.scene.albam.tools_settings.special_attr = spec


def get_active_face_paint_mode(context):
    obj = context.active_object
    if obj and obj.type == 'MESH':
        try:
            albam_asset = obj.data.albam_custom_properties.get_parent_albam_asset()
        except Exception:
            albam_asset = None
        if albam_asset is not None:
            asset_type = str(getattr(albam_asset, 'asset_type', '')).upper()
            mode_map = {
                'COLLISION': 'SBC',
                'NAVMESH': 'Nav',
            }
            if asset_type in mode_map:
                return mode_map[asset_type]

    return context.scene.albam.tools_settings.face_paint_mode


def extract_material_id_from_name(material_name, paint_mode):
    material_name = material_name.replace("_", ".").split(".", 1)[0]
    mode_prefix = f"{paint_mode} "
    if not material_name.startswith(mode_prefix):
        return None

    material_id_text = material_name[len(mode_prefix):]
    if not material_id_text.isdecimal():
        return None

    return int(material_id_text)


def get_material_purpose(material_id, paint_mode):
    purpose_descriptions = (
        SBC_RUNTIME_ATTR_DESC
        if paint_mode == "SBC"
        else NAV_FACE_FLAGS_DESC
    )
    return purpose_descriptions.get(material_id, "Unregistered")


@blender_registry.register_blender_type
class MergeVGItem(bpy.types.PropertyGroup):
    vertex_group_index: bpy.props.IntProperty()
    vertex_group_name: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty()


@blender_registry.register_blender_type
class ALBAM_UL_MergeVertexGroups(bpy.types.UIList):
    bl_idname = "ALBAM_UL_MergeVertexGroups"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "selected", text="")
        row.label(text=item.vertex_group_name)

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        if self.filter_name:
            flags = bpy.types.UI_UL_list.filter_items_by_name(
                self.filter_name,
                self.bitflag_filter_item,
                items,
                "vertex_group_name",
                reverse=self.use_filter_sort_reverse,
            )
        else:
            flags = []
        return flags, []


@blender_registry.register_blender_prop_albam(name="meshes")
class AlbamMeshes(bpy.types.PropertyGroup):
    all_meshes: bpy.props.PointerProperty(type=bpy.types.Object, poll=mesh_filter)


@blender_registry.register_blender_prop_albam(name="armatures")
class AlbamArmatures(bpy.types.PropertyGroup):
    all_armatures: bpy.props.PointerProperty(type=bpy.types.Object, poll=armature_filter)


@blender_registry.register_blender_prop_albam(name="tools_settings")
class ToolsSettings(bpy.types.PropertyGroup):
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
    use_clones: bpy.props.BoolProperty(default=False)
    overwrite_tex_path: bpy.props.BoolProperty(default=False)
    sorting_dbg_draw: bpy.props.BoolProperty(default=False)
    face_group: bpy.props.IntProperty(name='Type')  # noqa: F821
    surface_attr: bpy.props.IntProperty(name='Surface attributes')  # noqa: F821
    special_attr: bpy.props.IntProperty(name='Behavior attributes')  # noqa: F821
    face_preset_enum = bpy.props.EnumProperty(
        name="",
        description="Select face property",
        items=[
            ("PhysWall", "Physical Wall", "Stops bullets, can be jumped, etc.", 1),
            ("IntWall", "Intangible Wall", "E.g. BP walls", 2),
            ("SpecWall", "Special Wall", "Blocks camera, trigger effects, etc.", 3),
            ("Ground", "Ground", "Ground", 4),
            ("Leap", "Leapable Ledge", "Boundary for triggering leaps", 5),
            ('Auto', 'Auto', 'Automatically assigns attributes, also used for ceiling', 6)
        ],
        default="Ground",
        update=face_preset_update
    )
    face_preset: face_preset_enum
    lm_resolution_enum = bpy.props.EnumProperty(
        name="Lightmap Resolution",
        description="Set the side of the baked lightmap",
        items=[
            ('512', "512", "", 1),
            ('1024', "1024", "", 2),
            ('2048', "2048", "", 3),
            ('4096', "4096", "", 4),
        ]
    )
    lm_resolution: lm_resolution_enum
    lm_mode_enum = bpy.props.EnumProperty(
        name="Mode",
        description="The method of adding lightmaps to the material",
        items=[
            ("0", "Single lightmap per .mod file", "One lightmap for all meshes in the .mod file", 1),
            ("1", "Update exsting", "Update existing lightmaps in the material", 2),
            ("2", "One for selected", "One lightmap for all selected meshes", 3),
        ],
        default="0"
    )
    lm_mode: lm_mode_enum
    lm_name: bpy.props.StringProperty(default='generic_LM')  # noqa: F821
    face_paint_mode_enum = bpy.props.EnumProperty(
        name="Face Paint Mode",
        description="Mode for painting face properties",
        items=[
            ("SBC", "Collision", "Paint with collision materials", 1),
            ("Nav", "Navmesh", "Paint with navmesh materials", 2),
        ],
        default="SBC",
    )
    face_paint_mode: face_paint_mode_enum


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
        row.label(text="Active Mesh")
        row = layout.row()
        row.prop(context.scene.albam.meshes, "all_meshes", text="")
        layout.separator()
        row = layout.row()
        row.operator('albam.transfer_normals', text="Transfer normals from Active mesh")
        row = layout.row()
        row.operator('albam.batch_transfer_weights', text="Transfer skinweights from Active mesh")
        layout.separator()
        row = layout.row()
        row.operator('albam.autoset_tex_params', text="Autoset texture params")
        row.prop(
            context.scene.albam.tools_settings,
            "overwrite_tex_path",
            text="Overwrite path if exists",
        )
        row = layout.row()
        row.prop(
            context.scene.albam.tools_settings,
            "relative_path_to_textures",
            text="",
        )
        layout.separator()
        row = layout.row()
        row.operator('albam.autorename_bones', text="Autorename bones")
        row.prop(
            context.scene.albam.tools_settings,
            "bone_names_preset",
            text="",
        )
        row = layout.row()
        row.operator('albam.guess_bone_mirrors', text="Guess bone mirrors")
        layout.separator()
        row = layout.row()
        row.operator('albam.separate_by_material', text="Separate by material")
        row.prop(
            context.scene.albam.tools_settings,
            "use_clones",
            text="Use clones for separation",
        )
        row = layout.row()
        row.operator('albam.batch_props_paste', text="Batch paste material props").prop_type = "material"
        row.operator('albam.batch_props_paste', text="Batch paste mesh props").prop_type = "mesh"
        row = layout.row()
        row.operator('albam.remove_empty_vertex_groups', text="Remove empty vertex groups")
        row = layout.row()
        row.operator('albam.remove_unused_material_slots', text="Remove unused material slots")
        row = layout.row()
        row.operator('albam.vf_guesser', text="Guess vertex format")
        layout.separator()
        row = layout.row()
        row.operator('albam.sort_hair_cards', text="Sort hair cards by distance")
        row = layout.row()
        row.prop(
            context.scene.albam.tools_settings,
            "sorting_dbg_draw",
            text="Sorting debug draw",
        )
        row = layout.row()
        row.label(text="Active Armature")
        row = layout.row()
        row.prop(context.scene.albam.armatures, "all_armatures", text="")
        row = layout.row()
        row.operator('albam.set_armature_object', text="Set armature object")


@blender_registry.register_blender_type
class ALBAM_OT_ApplyFaceProps(bpy.types.Operator):
    bl_idname = "albam.apply_face_props"
    bl_label = "Apply Face Properties"

    @classmethod
    def poll(self, context):
        ob = context.edit_object
        if not ob:
            return False
        return True

    def execute(self, context):
        ob = context.edit_object
        bm = bmesh.from_edit_mesh(ob.data)

        group = bm.faces.layers.int.get('type', None)
        surface_attr = bm.faces.layers.int.get('surface_attr', None)
        special_attr = bm.faces.layers.int.get('special_attr', None)

        new_group = context.scene.albam.tools_settings.face_group
        new_surface_attr = context.scene.albam.tools_settings.surface_attr
        new_special_attr = context.scene.albam.tools_settings.special_attr
        if group and surface_attr and special_attr:
            for f in bm.faces:
                if f.select:
                    f[group] = new_group
                    f[surface_attr] = new_surface_attr
                    f[special_attr] = new_special_attr
        else:
            group = bm.faces.layers.int.new('type')
            surface_attr = bm.faces.layers.int.new('surface_attr')
            special_attr = bm.faces.layers.int.new('special_attr')
            for f in bm.faces:
                if f.select:
                    f[group] = new_group
                    f[surface_attr] = new_surface_attr
                    f[special_attr] = new_special_attr

        bmesh.update_edit_mesh(ob.data)
        return {'FINISHED'}


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
            show_message_box(message=f"Normals were transferred for {len(target_objs)} meshes")
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
        show_message_box(message=f"Texture params were autoset for {len(meshes)} meshes")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_MergeVertexGroups(bpy.types.Operator):
    '''
    Merges weights from groups A and B to group A
    The B group will be removed
    '''
    bl_idname = "albam.vg_merge"
    bl_label = "Merge vertex groups"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        bl_ob = bpy.context.active_object
        if bl_ob is None or bl_ob.type != 'MESH':
            return False
        albam_settings = bpy.context.scene.albam.tools_settings
        if albam_settings.vg_a == "" or albam_settings.vg_b == "":
            return False
        elif albam_settings.vg_a == albam_settings.vg_b:
            return False
        elif not (albam_settings.vg_a in bl_ob.vertex_groups and albam_settings.vg_b in bl_ob.vertex_groups):
            return False
        else:
            return True

    def execute(self, context):
        albam_settings = bpy.context.scene.albam.tools_settings
        merge_vgroups(albam_settings.vg_a, albam_settings.vg_b)
        albam_settings.vg_b = ""
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_BatchMergeVertexGroups(bpy.types.Operator):
    bl_idname = "albam.batch_vg_merge"
    bl_label = "Batch Merge Vertex Groups"
    bl_options = {'UNDO'}
    vertex_groups: bpy.props.CollectionProperty(type=MergeVGItem)
    active_index: bpy.props.IntProperty(default=0)

    @classmethod
    def poll(cls, context):
        bl_ob = context.object
        if bl_ob is None or bl_ob.type != 'MESH':
            return False
        albam_settings = bpy.context.scene.albam.tools_settings
        if albam_settings.vg_a == "":
            return False
        return True

    def invoke(self, context, event):
        bl_ob = context.object
        albam_settings = bpy.context.scene.albam.tools_settings
        group_a = albam_settings.vg_a
        group_b = albam_settings.vg_b
        self.vertex_groups.clear()
        for vg in bl_ob.vertex_groups:
            if vg.name == group_a:
                continue
            item = self.vertex_groups.add()
            item.vertex_group_index = vg.index
            item.vertex_group_name = vg.name
            item.selected = False
            if vg.name == group_b:
                item.selected = True

        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        albam_settings = bpy.context.scene.albam.tools_settings
        layout = self.layout
        layout.label(text=f"Merge selected groups to {albam_settings.vg_a}")
        layout.template_list(
            "ALBAM_UL_MergeVertexGroups",
            "",
            self,
            "vertex_groups",
            self,
            "active_index",
            rows=8,
            maxrows=8,
        )

    def execute(self, context):
        vg_a = context.scene.albam.tools_settings.vg_a
        selected_vgroups = [item.vertex_group_name for item in self.vertex_groups if item.selected]
        if len(selected_vgroups) < 1:
            self.report({'WARNING'}, "Select at least one vertex groups")
            return {'CANCELLED'}

        batch_merge_vgroups(vg_a, selected_vgroups)
        show_message_box(message=f"Merged {len(selected_vgroups)} vertex groups to {vg_a}")
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
        show_message_box(message="Armature bones were renamed")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_GuessBoneMirrors(bpy.types.Operator):
    '''Fill in each bone's Mirror Bone from the rest pose'''
    bl_idname = "albam.guess_bone_mirrors"
    bl_label = "guess bone mirrors"

    @classmethod
    def poll(self, context):
        return any(obj.type == 'ARMATURE' for obj in bpy.context.selected_objects)

    def execute(self, context):
        app_id = context.scene.albam.apps.app_selected
        armature_ob = next(obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE')
        guessed = guess_mirrors(armature_ob)
        for bone_name, mirror_name in guessed.items():
            set_mirror(armature_ob.pose.bones[bone_name], app_id, mirror_name)
        # Whatever it could not place keeps whatever it had, which for a rig
        # straight out of an import is the value the file shipped.
        show_message_box(
            message=f"Guessed a mirror for {len(guessed)} of {len(armature_ob.data.bones)} bones. "
                    f"About one in twenty is wrong, so check them before exporting"
        )
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

    @classmethod
    def poll(self, context):
        selection = bpy.context.selected_objects
        armature = [obj for obj in selection if obj.type == 'ARMATURE']
        selected_mesh = context.scene.albam.meshes.all_meshes
        if not armature or not selected_mesh:
            return False
        return True

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
        use_clones = context.scene.albam.tools_settings.use_clones
        if selected_meshes:
            bpy.ops.object.select_all(action='DESELECT')
            for mesh_ob in selected_meshes:
                try:
                    target_collection = mesh_ob.users_collection[0]
                except IndexError:
                    target_collection = bpy.context.collection
                active_ob = mesh_ob
                if use_clones:
                    duplicate = mesh_ob.copy()
                    duplicate.data = mesh_ob.data.copy()
                    target_collection.objects.link(duplicate)
                    bpy.ops.object.select_all(action='DESELECT')
                    duplicate.select_set(True)
                    active_ob = duplicate
                bpy.context.view_layer.objects.active = active_ob
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
class ALBAM_OT_BatchTransferWeights(bpy.types.Operator):
    '''Transfer weights from Active mesh to selected meshes'''
    bl_idname = "albam.batch_transfer_weights"
    bl_label = "Batch transfer skin weights"
    bl_options = {'UNDO'}

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
        src_obj = context.scene.albam.meshes.all_meshes
        dst_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        for dst_obj in dst_objs:
            if dst_obj != src_obj:
                # create vertex groups in destination object
                for vg in src_obj.vertex_groups:
                    if vg.name not in dst_obj.vertex_groups.keys():
                        dst_obj.vertex_groups.new(name=vg.name)

                mod = dst_obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
                mod.object = src_obj
                mod.use_vert_data = True
                mod.data_types_verts = {'VGROUP_WEIGHTS'}
                mod.vert_mapping = 'NEAREST'

                # apply modifier
                bpy.context.view_layer.objects.active = dst_obj
                bpy.ops.object.modifier_apply(modifier=mod.name)
        show_message_box(message="Skin weights were transferred")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_SetArmatureObject(bpy.types.Operator):
    '''Set armature object for selected meshes'''
    bl_idname = "albam.set_armature_object"
    bl_label = "Set armature object"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        armature_obj = context.scene.albam.armatures.all_armatures
        if armature_obj is None:
            return False
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        if not selected_meshes:
            return False
        return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        selected_meshes = [obj for obj in selection if obj.type == 'MESH']
        new_arm_obj = context.scene.albam.armatures.all_armatures
        for mesh_ob in selected_meshes:
            arm_modifier = None
            for modifier in mesh_ob.modifiers:
                if modifier.type == 'ARMATURE':
                    arm_modifier = modifier
                    break
            if not arm_modifier:
                arm_modifier = mesh_ob.modifiers.new(name="Armature", type='ARMATURE')
            arm_modifier.object = new_arm_obj
        show_message_box(
            message=f"Armature object {new_arm_obj.name} was set for {len(selected_meshes)} meshes")
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
        sort_hair_cards(source_obj, selected_meshes)
        show_message_box(message=f"{len(selected_meshes)} hair cards were sorted")
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_BakeLighting(bpy.types.Operator):
    bl_idname = "albam.bake_lighting"
    bl_label = "Bake Lighting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        selected_objects = [ob for ob in selected_objects if ob.type == 'MESH']
        custom_props = context.scene.albam.tools_settings
        lm_size = int(custom_props.lm_resolution)
        lm_mode = custom_props.lm_mode
        app_id = context.scene.albam.apps.app_selected
        assert app_id == "re5", "Bake of Light is only supported for RE5 for now"
        bake_light(selected_objects, lm_size, lm_mode, app_id)

        for ob in selected_objects:
            ob.select_set(True)
        self.report({'INFO'}, "Baking completed")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        selected_objects = context.selected_objects
        selected_objects = [ob for ob in selected_objects if ob.type == 'MESH']
        light = [ob for ob in context.scene.objects if ob.type == 'LIGHT']
        if selected_objects and light:
            return True
        else:
            return False


@blender_registry.register_blender_type
class VIEW3D_OT_material_paint_modal(bpy.types.Operator):
    """Modal operator for face painter"""
    bl_idname = "albam.material_paint_modal"
    bl_label = "Paint Material ID"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D' or context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "The tool works only in Edit Mode!")
            return {'CANCELLED'}

        # Keep solid shading for the full time this workspace tool is active.
        _ensure_face_painter_lifecycle_timer()
        _track_face_painter_area(context.area)

        context.tool_settings.mesh_select_mode = (False, False, True)

        if context.active_object.data.total_face_sel:
            bpy.ops.mesh.select_all(action='DESELECT')

        mode = get_active_face_paint_mode(context)
        context.scene.albam.tools_settings.face_paint_mode = mode

        self.mesh_object = context.active_object
        self.edit_mesh = bmesh.from_edit_mesh(self.mesh_object.data)
        self.bvh = _get_face_painter_bvh(self.mesh_object.data, self.edit_mesh)

        # paint on LMB press
        self.paint_face(context, event)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def paint_face(self, context, event):
        """Raycast with BVHTree to BMesh"""
        bl_ob = self.mesh_object
        if not bl_ob or bl_ob.type != 'MESH':
            return

        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)

        # Covert 2D mouse coordinates to 3D ray
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_dir = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)

        # Get local coordinates of the ray in the object's space
        inv_matrix = bl_ob.matrix_world.inverted()
        origin_local = inv_matrix @ ray_origin
        dir_local = inv_matrix.to_3x3() @ ray_dir

        location, normal, face_index, distance = self.bvh.ray_cast(origin_local, dir_local)

        if face_index is not None:
            active_mat_idx = bl_ob.active_material_index

            if not bl_ob.data.materials:
                self.report({'WARNING'}, "The object has no materials assigned!")
                return

            if self.edit_mesh.faces[face_index].material_index != active_mat_idx:
                self.edit_mesh.faces[face_index].material_index = active_mat_idx
                bmesh.update_edit_mesh(bl_ob.data)
                context.area.tag_redraw()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.paint_face(context, event)
            return {'RUNNING_MODAL'}

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return {'FINISHED'}

        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}

        # Allows to use camera navigation while the tool is active
        return {'PASS_THROUGH'}


HEADER_H = 40
FOOTER_H = 60
GRID_COLUMNS = 8
CELL_SIZE = 20
GAP = 4
PANEL_W = 196
PANEL_BG = (0.08, 0.08, 0.08, 0.97)
PANEL_BORDER = (0.25, 0.25, 0.25, 1.0)


def _gpu_draw_rect(x, y, w, h, color):
    """
    Draw a rectangle in the 3D view using GPU shader.
    x, y: bottom-left corner coordinates
    w, h: width and height of the rectangle
    color: RGBA tuple for the rectangle color
    """
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    vertices = (
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h),
    )
    indices = (
        (0, 1, 2),
        (0, 2, 3),
    )
    batch = batch_for_shader(
        shader,
        'TRIS',
        {"pos": vertices},
        indices=indices,
    )
    shader.bind()
    shader.uniform_float("color", color)

    batch.draw(shader)


def _blf_draw_text(font_id, x, y, text, size=12):
    """Draw text in the 3D view using BLF."""
    blf.position(font_id, x, y, 0)
    blf.size(font_id, size)
    blf.draw(font_id, text)


@blender_registry.register_blender_type
class ALBAM_OT_MaterialPalette(bpy.types.Operator):
    bl_idname = "albam.mat_palette_popup"
    bl_label = "Material Palette"

    _draw_handler = None

    def invoke(self, context, event):
        self.palette_origin_x = event.mouse_region_x
        self.palette_origin_y = event.mouse_region_y
        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y
        self.hovered_palette_index = -1
        self.mesh_object = context.active_object
        self.face_paint_mode = get_active_face_paint_mode(context)
        context.scene.albam.tools_settings.face_paint_mode = self.face_paint_mode
        self.palette_material_ids = self.get_palette_material_ids()

        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_palette,
            (),
            'WINDOW',
            'POST_PIXEL',
        )

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def extract_mat_id(self, material_name):
        """Return this paint mode's numeric material ID, or None if it doesn't match."""
        return extract_material_id_from_name(material_name, self.face_paint_mode)

    def get_palette_material_ids(self):
        """Get numeric IDs parsed from the object's material names."""
        if not self.mesh_object or self.mesh_object.type != 'MESH':
            return []

        palette_material_ids = []
        for material in self.mesh_object.data.materials:
            if not material:
                continue

            material_id = self.extract_mat_id(material.name)
            if material_id is not None:
                palette_material_ids.append(material_id)

        return palette_material_ids

    def modal(self, context, event):
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self.palette_origin_x = event.mouse_region_x
            self.palette_origin_y = event.mouse_region_y
            self.mouse_region_x = event.mouse_region_x
            self.mouse_region_y = event.mouse_region_y
            self.hovered_palette_index = -1
            context.area.tag_redraw()

        elif event.type == 'MOUSEMOVE':
            self.mouse_region_x = event.mouse_region_x
            self.mouse_region_y = event.mouse_region_y
            self.update_hover()
            context.area.tag_redraw()

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hovered_palette_index >= 0:
                self.select_material(self.hovered_palette_index)

            self.finish(context)
            return {'FINISHED'}

        elif event.type in {'ESC', }:
            self.finish(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def finish(self, context):
        if self._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(
                self._draw_handler,
                'WINDOW',
            )

            self._draw_handler = None

        context.area.tag_redraw()

    def cell_position(self, palette_index):
        column = palette_index % GRID_COLUMNS
        row = palette_index // GRID_COLUMNS
        cell_x = self.palette_origin_x + GAP + column * (CELL_SIZE + GAP)
        panel_top = self.palette_origin_y + HEADER_H + CELL_SIZE
        cell_y = panel_top - HEADER_H - CELL_SIZE - row * (CELL_SIZE + GAP)
        return cell_x, cell_y

    def update_hover(self):
        self.hovered_palette_index = -1
        for palette_index in range(len(self.palette_material_ids)):
            cell_x, cell_y = self.cell_position(palette_index)
            if (
                cell_x <= self.mouse_region_x <= cell_x + CELL_SIZE and
                cell_y <= self.mouse_region_y <= cell_y + CELL_SIZE
            ):
                self.hovered_palette_index = palette_index
                break

    def select_material(self, palette_index):
        selected_material_id = self.palette_material_ids[palette_index]
        if not self.mesh_object or self.mesh_object.type != 'MESH':
            return

        for material_slot_index, material in enumerate(self.mesh_object.data.materials):
            if not material:
                continue

            material_id = self.extract_mat_id(material.name)
            if selected_material_id == material_id:
                self.mesh_object.active_material_index = material_slot_index
                break

    def panel_geometry(self):
        row_count = max(1, (len(self.palette_material_ids) + GRID_COLUMNS - 1) // GRID_COLUMNS)
        grid_height = row_count * CELL_SIZE + (row_count - 1) * GAP
        panel_height = HEADER_H + grid_height + FOOTER_H
        panel_top = self.palette_origin_y + HEADER_H + CELL_SIZE
        return panel_top, panel_top - panel_height, panel_height

    def draw_palette(self):
        panel_top, panel_bottom, panel_height = self.panel_geometry()
        self.panel_x = self.palette_origin_x
        self.panel_y = panel_bottom

        _gpu_draw_rect(
            self.panel_x - 2,
            panel_bottom - 2,
            PANEL_W + 4,
            panel_height + 4,
            PANEL_BORDER,
        )
        _gpu_draw_rect(self.panel_x, panel_bottom, PANEL_W, panel_height, PANEL_BG)
        self.draw_header(panel_top)
        self.draw_cells()
        self.draw_footer()

    def draw_header(self, panel_top):
        _blf_draw_text(
            0,
            self.panel_x + 12,
            panel_top - 24,
            "Albam Material Palette",
            13,
        )

    def draw_cells(self):
        if self.hovered_palette_index >= 0:
            cell_x, cell_y = self.cell_position(self.hovered_palette_index)
            _gpu_draw_rect(
                cell_x - 2,
                cell_y - 2,
                CELL_SIZE + 4,
                CELL_SIZE + 4,
                (1.0, 1.0, 1.0, 1.0),
            )

        for palette_index, material_id in enumerate(self.palette_material_ids):
            cell_x, cell_y = self.cell_position(palette_index)
            if self.face_paint_mode == "SBC":
                color = SBC_COLOR_PALETTE.get(material_id, number_to_color(material_id))
            else:
                color = number_to_color(material_id)
            _gpu_draw_rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE, color)

    def draw_footer(self):
        if self.hovered_palette_index >= 0:
            hovered_material_id = self.palette_material_ids[self.hovered_palette_index]
            _blf_draw_text(0, self.panel_x + 12, self.panel_y + 36, f"Material ID: {hovered_material_id}", 12)
            purpose = get_material_purpose(hovered_material_id, self.face_paint_mode)
            _blf_draw_text(0, self.panel_x + 12, self.panel_y + 12, f"Purpose: {purpose}", 12)


class ALBAM_WT_Handshaker(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "albam.handshaker"
    bl_label = "Handshaker"
    bl_description = "Apply animation frames to a mesh"
    bl_icon = str(
        Path(__file__).parent.parent / "lib" / "icons" / "ops.generic.albam_handshake")
    after = "albam.vg_merger"

    @staticmethod
    def draw_settings(context, layout, tool):
        selected = [ob for ob in context.selected_objects if ob.type == "ARMATURE"]
        hand_ob = context.scene.albam.meshes.all_meshes
        row = layout.row()
        op = row.operator("albam.handshake", text="Apply animation frames")
        op.filepath = frames_path
        row.prop(context.scene.albam.meshes, "all_meshes", text="")
        if not selected:
            row = layout.row()
            row.label(text="No armature selected")
        if not hand_ob:
            row = layout.row()
            row.label(text="No hand mesh selected")
        if DEV_MODE:
            row = layout.row()
            row.label(text="Dump frames to json files")
            row = layout.row()
            row.operator("albam.dump_anim_frames", text="Dump frames for left side").side = "left"
            row.operator("albam.dump_anim_frames", text="Dump frames for right side").side = "right"


class ALBAM_WT_FacePropEdit(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'
    bl_idname = "albam.face_prop_edit"
    bl_label = "Face properties"
    bl_description = "Edit mesh face properties"
    bl_icon = str(
        Path(__file__).parent.parent / "lib" / "icons" / "ops.generic.albam_face_props")
    after = ""

    @classmethod
    def poll(cls, context):
        return context.edit_object is not None

    @staticmethod
    def draw_settings(context, layout, tool):
        scn = context.scene.albam.tools_settings
        layout.prop(scn, 'face_preset')
        layout.prop(scn, 'face_group')
        layout.prop(scn, 'surface_attr')
        layout.prop(scn, 'special_attr')
        layout.operator("albam.apply_face_props")


class ALBAM_WT_FacePainter(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'
    bl_idname = "albam.material_painter_tool"
    bl_label = "Face Painter"
    bl_description = "Paint Active Material ID on faces"
    bl_icon = str(
        Path(__file__).parent.parent / "lib" / "icons" / "ops.generic.albam_face_paint")
    bl_keymap = (
        ("albam.material_paint_modal", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("albam.mat_palette_popup", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
    )
    after = "albam.face_prop_edit"

    @staticmethod
    def draw_settings(context, layout, tool):
        paint_mode = get_active_face_paint_mode(context)
        settings_row = layout.row(align=True)
        settings_row.label(text=f"Painting mode: {paint_mode}")

        active_object = context.active_object
        active_material = (
            active_object.active_material
            if active_object and active_object.type == 'MESH'
            else None
        )
        if active_material:
            settings_row.label(text=active_material.name, icon='MATERIAL')
            color_swatch = settings_row.row(align=True)
            color_swatch.ui_units_x = 3.0
            color_swatch.enabled = False
            color_swatch.prop(
                active_material,
                "diffuse_color",
                text="",
                emboss=True,
            )
            material_id = extract_material_id_from_name(
                active_material.name,
                paint_mode,
            )
            purpose = get_material_purpose(material_id, paint_mode)
            purpose_row = layout.row(align=True)
            purpose_row.label(text=f"Purpose: {purpose}")
        else:
            settings_row.label(text="No active material", icon='MATERIAL')


class ALBAM_WT_VGMerger(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "albam.vg_merger"
    bl_label = "Vertex groups merger"
    bl_description = "Merge selected vertex groups"
    bl_icon = str(
        Path(__file__).parent.parent / "lib" / "icons" / "ops.generic.albam_vgmerge"
    )
    after = ""

    @staticmethod
    def draw_settings(context, layout, tool):
        scn = context.scene.albam.tools_settings
        obj = context.active_object
        row = layout.row()
        if obj:
            row = layout.row()
            row.prop_search(scn, "vg_a", context.active_object, "vertex_groups", text="Merge to")
            row = layout.row()
            row.prop_search(scn, "vg_b", context.active_object, "vertex_groups", text="Merge from")
        row.operator("albam.vg_merge")
        row.operator("albam.batch_vg_merge", text="Batch merge vertex groups")
        if not obj:
            row = layout.row()
            row.label(text="No active object selected")


class ALBAM_WT_BakeOfLight(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "albam.bake_of_light"
    bl_label = "Bake of Light"
    bl_description = "Simplifies baking the light for"
    bl_icon = str(
        Path(__file__).parent.parent / "lib" / "icons" / "ops.generic.albam_bake_of_light"
    )
    after = "albam.vg_merger"

    @staticmethod
    def draw_settings(context, layout, tool):
        light_objects = [ob for ob in context.scene.objects if ob.type == 'LIGHT']
        selected_objects = [ob for ob in context.selected_objects if ob.type == 'MESH']
        lm_mode = context.scene.albam.tools_settings.lm_mode
        settings = context.scene.albam.tools_settings
        layout.operator('albam.bake_lighting', text="Bake Lighting")
        layout.prop(settings, "lm_resolution", text="Resolution",)
        layout.prop(settings, "lm_mode", text="How to update")
        row = layout.row()
        row.enabled = True if lm_mode == "2" else False
        row.prop(settings, "lm_name", text="Lightmap name")
        if not light_objects:
            row = layout.row()
            row.label(text="No light source in the scene")
        if not selected_objects:
            row = layout.row()
            row.label(text="No mesh selected")


WORKSPACE_TOOLS.extend([
    ALBAM_WT_VGMerger,
    ALBAM_WT_Handshaker,
    ALBAM_WT_BakeOfLight,
    ALBAM_WT_FacePropEdit,
    ALBAM_WT_FacePainter,
])


@blender_registry.register_blender_type
class ALBAM_OT_VFGuesser(bpy.types.Operator):
    '''Guess vertex format for selected meshes'''
    bl_idname = "albam.vf_guesser"
    bl_label = "guess vertex format"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        selected_objects = context.selected_objects
        selected_objects = [ob for ob in selected_objects if ob.type == 'MESH']
        if selected_objects:
            return True
        else:
            return False

    def execute(self, context):
        selected_objects = context.selected_objects
        selected_objects = [ob for ob in selected_objects if ob.type == 'MESH']
        for bl_ob in selected_objects:
            armature_modifier = None
            for modifier in bl_ob.modifiers:
                if modifier.type == 'ARMATURE':
                    armature_modifier = modifier
                    break
            if armature_modifier is None:
                print(f"Can't guess vertex format for object {bl_ob.name} without armature modifier")
                continue
            albam_mesh_props = _get_mesh_albam_props(bl_ob)
            if not albam_mesh_props:
                print(f"The object {bl_ob.name} has no Albam properties")
                continue
            albam_asset = bl_ob.data.albam_custom_properties.get_parent_albam_asset()
            app_id = albam_asset.app_id

            max_bones = 0
            for v in bl_ob.data.vertices:
                cur_bones = sum(1 for g in v.groups if g.weight > 0)
                if cur_bones > max_bones:
                    max_bones = cur_bones

            if app_id in ("re0", "re1", "re6", "rev1", "rev2", "dd"):

                if max_bones == 1:
                    vf = "0xa8fab018"  # "SkinTB1wt"
                elif max_bones == 2:
                    vf = "0xc31f201c"  # "SkinTB2wt"
                elif max_bones <= 4:
                    vf = "0x14d40020"  # "SkinTB4wt"
                elif max_bones > 4:
                    vf = "0xbb424024"  # "SkinTB8wt"
                else:
                    raise RuntimeError(
                        f"Can't find vertex format for {bl_ob.name} max bone infuences: {max_bones}")
                albam_mesh_props.vertex_format = vf
            elif app_id == "re5":
                try:
                    bl_mat = bl_ob.data.materials[0]
                except IndexError:
                    print(f"The object {bl_ob.name} has no materials")
                    continue
                albam_mat_props = bl_mat.albam_custom_properties.get_custom_properties_for_appid(app_id)
                albam_mat_props.vtype = "0x0"
                if max_bones == 1:
                    albam_mat_props.func_skin = "0x1"
                elif max_bones == 2:
                    albam_mat_props.func_skin = "0x2"
                elif max_bones <= 4:
                    albam_mat_props.func_skin = "0x3"
                elif max_bones > 4:
                    albam_mat_props.vtype = "0x1"
                    albam_mat_props.func_skin = "0x4"
                    albam_mesh_props.vdeclbase = "0x7"
                    albam_mesh_props.vdecl = "0x2"
                else:
                    raise RuntimeError(
                        f"Can't find vertex format for {bl_ob.name} max bone infuences: {max_bones}")
        show_message_box(message=f"Vertex format was set for {len(selected_objects)} meshes")
        return {'FINISHED'}


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
    overwrite_tex_path = bpy.context.scene.albam.tools_settings.overwrite_tex_path
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
        if not tn.image.albam_asset.relative_path or overwrite_tex_path:
            tn.image.albam_asset.relative_path = local_path + name + '.tex'
        tn.image.albam_asset.app_id = app_id
        if type in (1, 2, 7):
            # The shader reads these as data; an sRGB image tilts the preview normals
            tn.image.colorspace_settings.name = "Non-Color"
        tex_props = tn.image.albam_custom_properties.get_custom_properties_for_appid(app_id)
        if app_id in TEX_COMPRESSION:
            tex_compr_preset = TEX_COMPRESSION.get(app_id)
            if type == 0:
                tex_props.compression_format = tex_compr_preset[1]
            if type == 1:
                tex_props.compression_format = tex_compr_preset[3]
            if type == 2:
                tex_props.compression_format = tex_compr_preset[2]
            if type == 7:
                tex_props.compression_format = tex_compr_preset[3]
        else:
            if type == 0:
                tex_props.encoded_type = '0x2'
            if type == 1:
                tex_props.encoded_type = '0x3'
            if type == 2:
                tex_props.encoded_type = '0x0'
            if type == 7:
                tex_props.encoded_type = '0x3'
        if app_id in UNK:
            tex_props.unk = UNK.get(app_id)
        if app_id in VERSION:
            tex_props.version = VERSION.get(app_id)


def rename_bones(armature_ob, app_id, body_type):
    # A copy: BONE_NAMES holds the module-level BONES_BODY/BONES_HEAD dicts
    # themselves, and a game's NAME_FIXES entry reassigns ids rather than just
    # respelling them, so merging in place would corrupt the tables for every other
    # game renamed later in the same session (see #245).
    names_preset = dict(BONE_NAMES.get(body_type))
    fixed_name = NAME_FIXES.get(body_type, {}).get(app_id)
    bone_name = None
    if fixed_name:
        names_preset.update(fixed_name)
    renamed = {}
    for pose_bone in armature_ob.pose.bones:
        reference_bone_id = get_anim_retarget(pose_bone, app_id)
        # a control bone carries "<id>_<n>", and is no body part
        if not reference_bone_id.isdigit():
            continue
        bone_name = names_preset.get(int(reference_bone_id), None)
        if bone_name:
            renamed[pose_bone.name] = bone_name
            pose_bone.name = bone_name
    # Mirror Bone is held by name (see bone.py), so a rename here would
    # otherwise leave it pointing at a name that no longer exists.
    for pose_bone in armature_ob.pose.bones:
        mirror = get_mirror(pose_bone, app_id)
        if mirror in renamed:
            set_mirror(pose_bone, app_id, renamed[mirror])


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


def batch_merge_vgroups(vg_a, selected_vgs):
    ob = bpy.context.active_object
    if vg_a not in ob.vertex_groups:
        return

    for vg_b in selected_vgs:
        if vg_b != vg_a and vg_b in ob.vertex_groups:
            merge_vgroups(vg_a, vg_b)


def paste_props(context_item):
    albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
    app_id = albam_asset.app_id
    custom_props = context_item.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_props_sec = context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)

    props_name = context_item.albam_custom_properties.APPID_MAP[app_id]
    props_name = props_name.get("custom_props_name")
    buff = bpy.context.scene.albam.clipboard.get_buffer()
    to_paste = buff.get(app_id, {}).get(props_name, {})

    for k, v in to_paste.items():
        setattr(custom_props, k, v)

    for sec_prop_name, sec_prop in custom_props_sec.items():
        to_paste = buff.get(app_id, {}).get(sec_prop_name, {})
        for k, v in to_paste.items():
            setattr(sec_prop, k, v)
