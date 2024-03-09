import os

import bpy

from albam.apps import APPS
from albam.registry import blender_registry
from albam.vfs import VirtualFileSystem, VirtualFile

NODES_CACHE = {}
# FIXME: store in app data
APP_DIRS_CACHE = {}
# FIXME: store in app data
APP_CONFIG_FILE_CACHE = {}


def update_app_data(self, context):
    current_app = context.scene.albam.file_explorer.app_selected
    cached_dir = APP_DIRS_CACHE.get(current_app)
    cached_file = APP_CONFIG_FILE_CACHE.get(current_app)
    if cached_dir:
        context.scene.albam.file_explorer.app_dir = cached_dir
    else:
        context.scene.albam.file_explorer.app_dir = ""

    if cached_file:
        context.scene.albam.file_explorer.app_config_filepath = cached_file
    else:
        context.scene.albam.file_explorer.app_config_filepath = ""


def update_app_caches(self, context):
    current_app = context.scene.albam.file_explorer.app_selected
    current_dir = context.scene.albam.file_explorer.app_dir
    current_file = context.scene.albam.file_explorer.app_config_filepath

    APP_DIRS_CACHE[current_app] = current_dir
    APP_CONFIG_FILE_CACHE[current_app] = current_file


@blender_registry.register_blender_type
class ALBAM_OT_Import(bpy.types.Operator):
    bl_idname = "albam.import"
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
        if len(context.scene.albam.file_explorer.file_list) == 0:
            return None
        index = context.scene.albam.file_explorer.file_list_selected_index
        try:
            item = context.scene.albam.file_explorer.file_list[index]
        except IndexError:
            # list might have been cleared
            return
        return item


@blender_registry.register_blender_type
class ALBAM_OT_FileItemCollapseToggle(bpy.types.Operator):
    bl_idname = "albam.file_item_collapse_toggle"
    bl_label = "ALBAM_OT_FileItemCollapseToggle"

    button_index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        item_index = self.button_index
        item_list = context.scene.albam.file_explorer.file_list
        item = item_list[item_index]
        item.is_expanded = not item.is_expanded
        NODES_CACHE[item.name] = item.is_expanded

        context.scene.albam.file_explorer.file_list_selected_index = self.button_index

        item_list.update()
        return {"FINISHED"}


@blender_registry.register_blender_prop
class TreeNode(bpy.types.PropertyGroup):
    node_id: bpy.props.StringProperty()
    root_id: bpy.props.StringProperty()
    depth: bpy.props.IntProperty(default=0)


@blender_registry.register_blender_prop
class FileListItem(bpy.types.PropertyGroup):
    display_name: bpy.props.StringProperty()
    file_path: bpy.props.StringProperty()  # FIXME: change to abs
    relative_path: bpy.props.StringProperty()
    is_archive: bpy.props.BoolProperty(default=False)
    is_root: bpy.props.BoolProperty(default=False)
    is_expandable: bpy.props.BoolProperty(default=False)
    is_expanded: bpy.props.BoolProperty(default=False)

    tree_node: bpy.props.PointerProperty(type=TreeNode)  # consider adding the attributes here directly
    # FIXME: consider strings, seems pretty inefficient
    tree_node_ancestors: bpy.props.CollectionProperty(type=TreeNode)

    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    vfs_id: bpy.props.StringProperty()

    data_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821

    @property
    def extension(self):
        """
        Allow up to 2 dots as an extension
        e.g. texname.tex.34 -> tex.34
        """
        SEP = "."
        name , _ , extension = self.display_name.rpartition(SEP)
        if SEP in name:
            _, __, extension0 = name.rpartition(SEP)
            extension = SEP.join((extension0, extension))
        return extension

    def get_bytes(self):
        accessor = self.get_accessor()
        return accessor(self, bpy.context)

    def get_accessor(self):
        if self.file_path:
            return self.real_file_accessor
        if self.data_bytes:
            return lambda _: self.data_bytes
        vfs = getattr(bpy.context.scene.albam, self.vfs_id)
        root = vfs.file_list[self.tree_node.root_id]
        accessor_func = blender_registry.archive_accessor_registry.get(
            (self.app_id, root.extension)
        )
        if not accessor_func:
            raise RuntimeError("Archive item doesn't have an accessor")

        return accessor_func

    @staticmethod
    def real_file_accessor(file_item, context):
        with open(file_item.file_path, 'rb') as f:
            return f.read()

    def get_vfs(self):
        return getattr(bpy.context.scene.albam, self.vfs_id)


@blender_registry.register_blender_prop_albam(name="file_explorer")
class FileExplorerData(bpy.types.PropertyGroup):
    file_list : bpy.props.CollectionProperty(type=FileListItem)
    file_list_selected_index : bpy.props.IntProperty()
    app_selected : bpy.props.EnumProperty(name="", items=APPS, update=update_app_data)
    app_dir : bpy.props.StringProperty(name="", description="", update=update_app_caches)
    app_config_filepath : bpy.props.StringProperty(name="", update=update_app_caches)
    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()

    def get_app_real_root_path(self, app_id):
        return APP_DIRS_CACHE.get(app_id)

    def get_app_config_filepath(self, app_id):
        return APP_CONFIG_FILE_CACHE.get(app_id)


@blender_registry.register_blender_type
class ALBAM_OT_AddFiles(bpy.types.Operator):

    bl_idname = "albam.add_files"
    bl_label = "Add Files"
    directory: bpy.props.StringProperty(subtype="DIR_PATH")  # NOQA
    files: bpy.props.CollectionProperty(name="added_files", type=bpy.types.OperatorFileListElement)  # NOQA
    # FIXME: use registry, un-hardcode
    filter_glob: bpy.props.StringProperty(default="*.arc;*.pak", options={"HIDDEN"})  # NOQA

    def invoke(self, context, event):  # pragma: no cover
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):  # pragma: no cover
        self._execute(context, self.directory, self.files)
        context.scene.albam.file_explorer.file_list.update()
        return {"FINISHED"}

    @staticmethod
    def _execute(context, directory, files):
        app_id = context.scene.albam.file_explorer.app_selected
        vfs_id = "file_explorer"
        vfs = VirtualFileSystem(vfs_id)
        for f in files:
            file_path = os.path.join(directory, f.name)
            virtual_file = VirtualFile.from_real_file(app_id, file_path)
            vfs.append(virtual_file)

        vfs.commit()


@blender_registry.register_blender_type
class ALBAM_OT_SaveFile(bpy.types.Operator):
    CHECK_EXISTING = bpy.props.BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    bl_idname = "albam.save_file"
    bl_label = "Save files"
    check_existing: CHECK_EXISTING
    filepath: FILEPATH

    def invoke(self, context, event):  # pragma: no cover
        current_item = ALBAM_OT_Import.get_selected_item(context)
        self.filepath = current_item.display_name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        current_item = ALBAM_OT_Import.get_selected_item(context)
        with open(self.filepath, 'wb') as w:
            w.write(current_item.get_bytes())
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        current_item = ALBAM_OT_Import.get_selected_item(context)
        if not current_item or current_item.is_expandable is True:
            return False
        return True


@blender_registry.register_blender_type
class ALBAM_UL_FileList(bpy.types.UIList):
    EXPAND_ICONS = {
        False: "TRIA_RIGHT",
        True: "TRIA_DOWN",
    }

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        for _ in range(item.tree_node.depth):
            layout.split(factor=0.01)

        if item.is_expandable:
            icon = self.EXPAND_ICONS[item.is_expanded]
        else:
            icon = "DOT"
        col = layout.column()
        col.enabled = item.is_expandable
        op = col.operator("albam.file_item_collapse_toggle", text="", icon=icon)
        op.button_index = index

        layout.column().label(text=item.display_name)

    def filter_items(self, context, data, propname):
        filtered_items = []
        # TODO: self.filter_name

        item_list = getattr(data, propname)
        for item in item_list:
            if item.is_archive:
                filtered_items.append(self.bitflag_filter_item)

            elif all(NODES_CACHE.get(anc.node_id, False) for anc in item.tree_node_ancestors):
                filtered_items.append(self.bitflag_filter_item)

            else:
                filtered_items.append(0)

        return filtered_items, []


@blender_registry.register_blender_type
class ALBAM_PT_ImportSection(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_ImportSection"
    bl_label = "Import"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene.albam.file_explorer, "app_selected")
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
            "ALBAM_UL_FileList",
            "",
            context.scene.albam.file_explorer,
            "file_list",
            context.scene.albam.file_explorer,
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
        x = context.scene.albam.file_explorer.mouse_x
        y = context.scene.albam.file_explorer.mouse_y
        if x and y:
            context.window.cursor_warp(x, y)
        else:
            context.scene.albam.file_explorer.mouse_x = event.mouse_x
            context.scene.albam.file_explorer.mouse_y = event.mouse_y
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        context.scene.albam.file_explorer.mouse_x = 0
        context.scene.albam.file_explorer.mouse_y = 0
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        file_explorer = context.scene.albam.file_explorer
        try:
            app_index = file_explorer["app_selected"]
        except KeyError:
            # default, before actually selecting
            app_index = 0
        app_selected_name = file_explorer.bl_rna.properties["app_selected"].enum_items[app_index].name
        layout.label(text=f"{app_selected_name}")
        layout.row()

        row = self.layout.row(heading="App Folder:", align=True)
        row.prop(context.scene.albam.file_explorer, "app_dir")
        row.operator("albam.app_dir_setter", text="", icon="FILEBROWSER")

        row = self.layout.row(heading="App Config:", align=True)
        row.prop(context.scene.albam.file_explorer, "app_config_filepath")
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
        context.scene.albam.file_explorer.app_dir = self.directory
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
        context.scene.albam.file_explorer.app_config_filepath = self.filepath
        bpy.ops.albam.app_config_popup("INVOKE_DEFAULT")
        return {"FINISHED"}

    def cancel(self, context):
        bpy.ops.albam.app_config_popup("INVOKE_DEFAULT")


@blender_registry.register_blender_type
class ALBAM_OT_Remove_Imported(bpy.types.Operator):
    bl_idname = "albam.remove_imported"
    bl_label = "Remove imported files"

    def execute(self, context):
        vfiles_to_remove = []
        vfs_i = context.scene.albam.file_explorer
        root_node_index = vfs_i.file_list_selected_index
        archive_node = vfs_i.file_list[root_node_index]
        for i in range(len(vfs_i.file_list)):
            parent = vfs_i.file_list[i].tree_node.root_id
            if parent == archive_node.name:
                vfiles_to_remove.append(i)

        vfiles_to_remove.reverse()
        for i in range(len(vfiles_to_remove)):
            vfs_i.file_list.remove(vfiles_to_remove[i])
        vfs_i.file_list.remove(root_node_index)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        current_item = ALBAM_OT_Import.get_selected_item(context)
        return current_item and current_item.is_archive


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
        row.operator("albam.import", text="Import")
        self.layout.row()
