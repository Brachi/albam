import time

import bpy

from albam.registry import blender_registry
from albam.vfs import (
        VirtualFileSystem,
        VirtualFile,
        VirtualFileBlender
)
from albam.engines.mtfw.archive import update_arc


NODES_CACHE = {}


@blender_registry.register_blender_prop
class ExportableItem(bpy.types.PropertyGroup):
    # FIXME: hook to remove from list when object is deleted
    bl_object : bpy.props.PointerProperty(type=bpy.types.ID)

    @property
    def display_name(self):
        if not self.bl_object:
            return "Object missing"
        return self.bl_object.name


@blender_registry.register_blender_prop_albam(name="exportable")
class ExportableItems(bpy.types.PropertyGroup):
    file_list: bpy.props.CollectionProperty(type=ExportableItem)
    file_list_selected_index: bpy.props.IntProperty()


@blender_registry.register_blender_prop_albam(name="exported")
class ExportedItems(bpy.types.PropertyGroup):
    file_list: bpy.props.CollectionProperty(type=VirtualFileBlender)
    file_list_selected_index: bpy.props.IntProperty()

    @staticmethod
    def get_selected_item():
        vfs = bpy.context.scene.albam.exported

        if len(vfs.file_list) == 0:
            return None
        index = vfs.file_list_selected_index
        try:
            item = vfs.file_list[index]
        except IndexError:
            # list might have been cleared
            return
        return item


@blender_registry.register_blender_type
class ALBAM_UL_ExportableObjects(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.display_name)


@blender_registry.register_blender_type
class ALBAM_PT_ExportSection(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_ExportSection"
    bl_label = "Export"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        row = self.layout.row()
        row.template_list(
            "ALBAM_UL_ExportableObjects",
            "",
            context.scene.albam.exportable,
            "file_list",
            context.scene.albam.exportable,
            "file_list_selected_index",
            sort_lock=True,
            rows=1,
            maxrows=3,
        )
        self.layout.row().operator("albam.export", text="Export")


@blender_registry.register_blender_type
class ALBAM_PT_FileExplorer2(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_FileExplorer2"
    bl_label = "File Explorer2"
    bl_options = {"HIDE_HEADER"}
    bl_parent_id = "ALBAM_PT_ExportSection"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        self.layout.separator()
        self.layout.separator()
        split = self.layout.split(factor=0.1)
        col = split.column()
        col.operator("albam.save_file2", icon="SORT_ASC", text="")
        col.operator("albam.pack", icon="PACKAGE", text="")
        col.operator("albam.patch", icon="FILE_REFRESH", text="")
        col.operator("albam.remove_exported", icon="X", text="")
        col = split.column()
        col.template_list(
            "ALBAM_UL_ExportedFileList",
            "",
            context.scene.albam.exported,
            "file_list",
            context.scene.albam.exported,
            "file_list_selected_index",
            sort_lock=True,
            rows=8,
        )
        self.layout.row()
        self.layout.row()


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemBlenderSaveFile2(bpy.types.Operator):
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

    bl_idname = "albam.save_file2"
    bl_label = "Save files"
    check_existing: CHECK_EXISTING
    filepath: FILEPATH

    def invoke(self, context, event):  # pragma: no cover
        current_item = ExportedItems.get_selected_item()
        self.filepath = current_item.display_name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        current_item = ExportedItems.get_selected_item()
        with open(self.filepath, 'wb') as w:
            w.write(current_item.data_bytes)
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        current_item = ExportedItems.get_selected_item()
        if not current_item or current_item.is_expandable is True:
            return False
        return True


# XXX copy/paste much?
@blender_registry.register_blender_type
class ALBAM_UL_ExportedFileList(bpy.types.UIList):
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
        op = col.operator("albam.file_item_collapse_toggle_2", text="", icon=icon)
        op.button_index = index

        layout.column().label(text=item.display_name)

    def filter_items(self, context, data, propname):
        filtered_items = []
        # TODO: self.filter_name

        item_list = getattr(data, propname)
        for item in item_list:
            if item.is_root:
                filtered_items.append(self.bitflag_filter_item)

            elif all(NODES_CACHE.get(anc.node_id, False) for anc in item.tree_node_ancestors):
                filtered_items.append(self.bitflag_filter_item)

            else:
                filtered_items.append(0)

        return filtered_items, []


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemBlenderCollapseToggle2(bpy.types.Operator):
    # XXX super dirty, quick copy paste
    bl_idname = "albam.file_item_collapse_toggle_2"
    bl_label = "ALBAM_OT_VirtualFileSystemBlenderCollapseToggle2"

    button_index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        item_index = self.button_index
        item_list = context.scene.albam.exported.file_list  # XXX change
        item = item_list[item_index]
        item.is_expanded = not item.is_expanded
        NODES_CACHE[item.name] = item.is_expanded

        context.scene.albam.exported.file_list_selected_index = self.button_index

        item_list.update()
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_Export(bpy.types.Operator):
    bl_idname = "albam.export"
    bl_label = "Export item"

    def execute(self, context):  # pragma: no cover
        item = self.get_selected_item(context)
        try:
            self._execute(item)
        except Exception:
            bpy.ops.albam.error_handler_popup("INVOKE_DEFAULT")

        return {"FINISHED"}

    @staticmethod
    def _execute(item):
        asset = item.bl_object.albam_asset
        bl_obj = item.bl_object
        app_id = asset.app_id
        vfs_id = "exported"
        export_function = blender_registry.export_registry[(asset.app_id, asset.extension)]
        vfiles = export_function(item.bl_object)
        vfs = VirtualFileSystem(vfs_id)
        vfs.extend(vfiles)
        root_id = f"{app_id}-{bl_obj.name}-{round(time.time())}"  # TODO
        vfile_root = VirtualFile(app_id, root_id)
        vfs.commit(root_vfile=vfile_root)

    @classmethod
    def poll(cls, context):
        item = cls.get_selected_item(context)
        if not item:
            return False
        albam_asset = item.bl_object.albam_asset
        if (albam_asset.app_id, albam_asset.extension) not in blender_registry.exportable_extensions:
            return False
        return True

    @staticmethod
    def get_selected_item(context):
        if len(context.scene.albam.exportable.file_list) == 0:
            return None
        index = context.scene.albam.exportable.file_list_selected_index
        try:
            item = context.scene.albam.exportable.file_list[index]
        except IndexError:
            # list might have been cleared and index is outdated
            return
        return item


@blender_registry.register_blender_type
class ALBAM_OT_Pack(bpy.types.Operator):
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    bl_idname = "albam.pack"
    bl_label = "Pack item"
    filepath: FILEPATH

    def invoke(self, context, event):  # pragma: no cover
        vfs = context.scene.albam.file_explorer
        index = vfs.file_list_selected_index
        item = vfs.file_list[index]
        parent_node = ""
        if item .is_archive:
            parent_node = item.display_name
        else:
            parent_node = (item.tree_node_ancestors[0].node_id).split("::")[1]
        self.filepath = parent_node
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            self._execute(context)
        except Exception:
            bpy.ops.albam.error_handler_popup("INVOKE_DEFAULT")
        return {"FINISHED"}

    def _execute(self, context):  # pragma: no cover
        # FIXME don't import function here, use method in archive type
        # necessary for kaitaistruct unavailable when registering
        # blender types
        from albam.engines.mtfw.archive import update_arc
        vfs_i = context.scene.albam.file_explorer
        index_i = vfs_i.file_list_selected_index
        item_i = vfs_i.file_list[index_i]
        if item_i.is_archive:
            path_i = item_i.file_path
        else:
            arc_name = (item_i.tree_node_ancestors[0].node_id).split("::")[1]
            arc_node = [item for item in vfs_i.file_list
                        if item.is_archive is True and item.display_name == arc_name]
            path_i = arc_node[0].file_path
        files_e = []
        vfs_e = context.scene.albam.exported
        index_e = vfs_e.file_list_selected_index
        item_e = vfs_e.file_list[index_e]
        exported = [item for item in vfs_e.file_list
                    if item.is_expandable is False]
        for e in exported:
            try:
                parent = e.tree_node_ancestors[0].node_id
            except IndexError:
                continue
            if parent == item_e.name:
                files_e.append(e)
        arc = update_arc(path_i, files_e)
        with open(self.filepath, "wb") as f:
            f.write(arc)

    @classmethod
    def poll(cls, context):
        vfs_e = context.scene.albam.exported
        vfs_i = context.scene.albam.file_explorer
        if len(vfs_e.file_list) == 0 or len(vfs_i.file_list) == 0:
            return False
        index_e = vfs_e.file_list_selected_index
        index_i = vfs_i.file_list_selected_index
        exported_item = vfs_e.file_list[index_e]
        imported_item = vfs_i.file_list[index_i]
        if not exported_item or not imported_item:
            return False
        return imported_item.is_archive and exported_item.is_root


@blender_registry.register_blender_type
class ALBAM_OT_Patch(bpy.types.Operator):
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    bl_idname = "albam.patch"
    bl_label = "Update arc"
    filepath: FILEPATH

    def invoke(self, context, event):  # pragma: no cover
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            self._execute(context)
        except Exception:
            bpy.ops.albam.error_handler_popup("INVOKE_DEFAULT")
        return {"FINISHED"}

    def _execute(self, context):
        # FIXME don't import function here, use method in archive type
        # necessary for kaitaistruct unavailable when registering
        # blender types
        from albam.engines.mtfw.archive import update_arc
        files_e = []
        vfs_e = context.scene.albam.exported
        index_e = vfs_e.file_list_selected_index
        item_e = vfs_e.file_list[index_e]
        exported = [item for item in vfs_e.file_list if item.is_expandable is False]
        for e in exported:
            try:
                parent = e.tree_node_ancestors[0].node_id
            except IndexError:
                continue
            if parent == item_e.name:
                files_e.append(e)
        arc = update_arc(self.filepath, files_e)
        with open(self.filepath, "wb") as f:
            f.write(arc)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        vfs = context.scene.albam.exported
        current_item = vfs.__class__.get_selected_item()
        return current_item and current_item.is_root


@blender_registry.register_blender_type
class ALBAM_OT_Remove_Exported(bpy.types.Operator):
    bl_idname = "albam.remove_exported"
    bl_label = "Remove exported files"

    def execute(self, context):
        vfiles_to_remove = []
        vfs_e = context.scene.albam.exported
        root_node_index = vfs_e.file_list_selected_index
        root_node = vfs_e.file_list[root_node_index]
        for i in range(len(vfs_e.file_list)):
            parent = vfs_e.file_list[i].tree_node.root_id
            if parent == root_node.name:
                vfiles_to_remove.append(i)
        vfiles_to_remove.reverse()
        for i in range(len(vfiles_to_remove)):
            vfs_e.file_list.remove(vfiles_to_remove[i])
        vfs_e.file_list.remove(root_node_index)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        vfs = context.scene.albam.exported
        current_item = vfs.__class__.get_selected_item()
        return current_item and current_item.is_root
