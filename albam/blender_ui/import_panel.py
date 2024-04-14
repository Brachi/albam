import os

import bpy

from albam.apps import APPS
from albam.registry import blender_registry
from albam.vfs import ALBAM_OT_VirtualFileSystemCollapseToggle

# FIXME: store in app data
APP_DIRS_CACHE = {}
# FIXME: store in app data
APP_CONFIG_FILE_CACHE = {}


def update_app_data(self, context):
    current_app = context.scene.albam.apps.app_selected
    cached_dir = APP_DIRS_CACHE.get(current_app)
    cached_file = APP_CONFIG_FILE_CACHE.get(current_app)
    if cached_dir:
        context.scene.albam.apps.app_dir = cached_dir
    else:
        context.scene.albam.apps.app_dir = ""

    if cached_file:
        context.scene.albam.apps.app_config_filepath = cached_file
    else:
        context.scene.albam.apps.app_config_filepath = ""


def update_app_caches(self, context):
    current_app = context.scene.albam.apps.app_selected
    current_dir = context.scene.albam.apps.app_dir
    current_file = context.scene.albam.apps.app_config_filepath

    APP_DIRS_CACHE[current_app] = current_dir
    APP_CONFIG_FILE_CACHE[current_app] = current_file


@blender_registry.register_blender_prop_albam(name="apps")
class AlbamApps(bpy.types.PropertyGroup):
    app_selected : bpy.props.EnumProperty(name="", items=APPS, update=update_app_data)
    app_dir : bpy.props.StringProperty(name="", description="", update=update_app_caches)
    app_config_filepath : bpy.props.StringProperty(name="", update=update_app_caches)
    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()

    def get_app_config_filepath(self, app_id):
        return APP_CONFIG_FILE_CACHE.get(app_id)


@blender_registry.register_blender_prop_albam(name="import_settings")
class AlbamImportSettings(bpy.types.PropertyGroup):
    import_only_main_lods : bpy.props.BoolProperty(default=True)


@blender_registry.register_blender_type
class ALBAM_OT_Import(bpy.types.Operator):
    bl_idname = "albam.import_vfile"
    bl_label = "import item"

    def execute(self, context):  # pragma: no cover
        item = self.get_selected_item(context)
        try:
            self._execute(item, context)
        except Exception:
            bpy.ops.albam.error_handler_popup("INVOKE_DEFAULT")
        return {"FINISHED"}

    @staticmethod
    def _execute(item, context):
        import_function = blender_registry.import_registry[(item.app_id, item.extension)]

        bl_container = import_function(item, context)
        if not bl_container:
            return

        if bl_container.type != "ARMATURE":
            # armature building needs it linked to for building
            bpy.context.collection.objects.link(bl_container)
        for child in bl_container.children_recursive:
            try:
                # already linked
                bpy.context.collection.objects.link(child)
            except RuntimeError:
                pass

    @classmethod
    def poll(cls, context):
        item = cls.get_selected_item(context)
        if not item or (item.app_id, item.extension) not in blender_registry.importable_extensions:
            return False
        custom_poll_func = blender_registry.import_operator_poll_funcs.get(item.extension)
        if custom_poll_func:
            return custom_poll_func(cls, context)
        return True

    @staticmethod
    def get_selected_item(context):
        # TODO: delete
        if len(context.scene.albam.vfs.file_list) == 0:
            return None
        index = context.scene.albam.vfs.file_list_selected_index
        try:
            item = context.scene.albam.vfs.file_list[index]
        except IndexError:
            # list might have been cleared
            return
        return item


class ALBAM_UL_VirtualFileSystemUIBase:
    EXPAND_ICONS = {
        False: "TRIA_RIGHT",
        True: "TRIA_DOWN",
    }
    collapse_toggle_operator_cls = None

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        for _ in range(item.tree_node.depth):
            layout.split(factor=0.01)

        if item.is_expandable:
            icon = self.EXPAND_ICONS[item.is_expanded]
        elif item.category == "MESH":
            icon = "OUTLINER_OB_MESH"
        elif item.category == "ANIMATION":
            icon = "ACTION"
        elif item.category == "MATERIAL":
            icon = "MATERIAL"
        elif item.category == "TEXTURE":
            icon = "TEXTURE"
        else:
            icon = "DOT"
        col = layout.column()
        col.enabled = item.is_expandable
        op = col.operator(self.collapse_toggle_operator_cls.bl_idname, text="", icon=icon)
        op.button_index = index

        layout.column().label(text=item.display_name)

    def filter_items(self, context, data, propname):
        filtered_items = []
        # TODO: self.filter_name
        cache = self.collapse_toggle_operator_cls.NODES_CACHE

        item_list = getattr(data, propname)
        for item in item_list:
            if item.is_archive:
                filtered_items.append(self.bitflag_filter_item)

            elif all(cache.get(anc.node_id, False) for anc in item.tree_node_ancestors):
                filtered_items.append(self.bitflag_filter_item)

            else:
                filtered_items.append(0)

        return filtered_items, []


@blender_registry.register_blender_type
class ALBAM_UL_VirtualFileSystemUI(ALBAM_UL_VirtualFileSystemUIBase, bpy.types.UIList):
    collapse_toggle_operator_cls = ALBAM_OT_VirtualFileSystemCollapseToggle


@blender_registry.register_blender_type
class ALBAM_PT_ImportSection(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_ImportSection"
    bl_label = "Import"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene.albam.apps, "app_selected")
        # Experimental for reengine
        if os.getenv("ALBAM_ENABLE_REEN"):
            row.operator("albam.app_config_popup", icon="OPTIONS")


@blender_registry.register_blender_type
class ALBAM_PT_FileExplorer(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_FileExplorer"
    bl_label = "File Explorer"
    bl_options = {"HIDE_HEADER"}
    bl_parent_id = "ALBAM_PT_ImportSection"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        self.layout.separator()
        self.layout.separator()
        split = self.layout.split(factor=0.1)
        col = split.column()
        col.operator("albam.add_files", icon="FILE_NEW", text="")
        col.operator("albam.save_file", icon="SORT_ASC", text="")
        col.operator("albam.remove_imported", icon="X", text="")
        col = split.column()
        col.template_list(
            "ALBAM_UL_VirtualFileSystemUI",
            "",
            context.scene.albam.vfs,
            "file_list",
            context.scene.albam.vfs,
            "file_list_selected_index",
            sort_lock=True,
            rows=8,
        )
        self.layout.row()
        self.layout.row()


@blender_registry.register_blender_type
class ALBAM_PT_ImportOptionsCustom(bpy.types.Panel):
    # TODO: better class name
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_ImportOptionsCustom"
    bl_label = ""
    bl_parent_id = "ALBAM_PT_ImportSection"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        current_item = ALBAM_OT_Import.get_selected_item(context)
        if not current_item:
            return
        ext = current_item.extension
        draw_func = blender_registry.import_options_custom_draw_funcs.get(ext)
        if not draw_func:
            return
        draw_func(self, context)

    @classmethod
    def poll(self, context):
        current_item = ALBAM_OT_Import.get_selected_item(context)
        if not current_item:
            return False
        ext = current_item.extension
        poll_func = blender_registry.import_options_custom_poll_funcs.get(ext)
        if not poll_func:
            return False
        return poll_func(self, context)


@blender_registry.register_blender_type
class ALBAM_OT_AppConfigPopup(bpy.types.Operator):
    bl_label = ""
    bl_idname = "albam.app_config_popup"

    # TODO: warning icon if required settings not present

    def invoke(self, context, event):
        x = context.scene.albam.apps.mouse_x
        y = context.scene.albam.apps.mouse_y
        if x and y:
            context.window.cursor_warp(x, y)
        else:
            context.scene.albam.apps.mouse_x = event.mouse_x
            context.scene.albam.apps.mouse_y = event.mouse_y
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        context.scene.albam.apps.mouse_x = 0
        context.scene.albam.apps.mouse_y = 0
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        apps = context.scene.albam.apps
        try:
            app_index = apps["app_selected"]
        except KeyError:
            # default, before actually selecting
            app_index = 0
        app_selected_name = apps.bl_rna.properties["app_selected"].enum_items[app_index].name
        layout.label(text=f"{app_selected_name}")
        layout.row()

        row = self.layout.row(heading="App Folder:", align=True)
        row.prop(context.scene.albam.apps, "app_dir")
        row.operator("albam.app_dir_setter", text="", icon="FILEBROWSER")

        row = self.layout.row(heading="App Config:", align=True)
        row.prop(context.scene.albam.apps, "app_config_filepath")
        row.operator("albam.app_config_filepath_setter", text="", icon="FILEBROWSER")


@blender_registry.register_blender_type
class ALBAM_OT_AppDirSetter(bpy.types.Operator):
    bl_idname = "albam.app_dir_setter"
    bl_label = "Select App Folder"

    DIRECTORY = bpy.props.StringProperty(subtype="DIR_PATH")
    directory: DIRECTORY

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        context.scene.albam.apps.app_dir = self.directory
        bpy.ops.albam.app_config_popup("INVOKE_DEFAULT")
        return {"FINISHED"}

    def cancel(self, context):
        bpy.ops.albam.app_config_popup("INVOKE_DEFAULT")


@blender_registry.register_blender_type
class ALBAM_OT_SetAppConfigPath(bpy.types.Operator):
    bl_idname = "albam.app_config_filepath_setter"
    bl_label = "Select App Config"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # NOQA

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        context.scene.albam.apps.app_config_filepath = self.filepath
        bpy.ops.albam.app_config_popup("INVOKE_DEFAULT")
        return {"FINISHED"}

    def cancel(self, context):
        bpy.ops.albam.app_config_popup("INVOKE_DEFAULT")


@blender_registry.register_blender_type
class ALBAM_PT_ImportButton(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_ImportButton"
    bl_label = "Import (unused)"
    bl_options = {"HIDE_HEADER"}
    bl_parent_id = "ALBAM_PT_ImportSection"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        self.layout.separator()
        row = self.layout.row()
        row.operator("albam.import_vfile", text="Import")
        self.layout.row()
