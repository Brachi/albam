import time

import bpy

from albam.registry import blender_registry
from albam.vfs import (
    ALBAM_OT_VirtualFileSystemSaveFileBase,
    ALBAM_OT_VirtualFileSystemCollapseToggleBase,
    ALBAM_OT_VirtualFileSystemRemoveRootVFileBase,
    VirtualFileSystemBase,
    VirtualFileData,
)
from .import_panel import ALBAM_UL_VirtualFileSystemUIBase


@blender_registry.register_blender_prop_albam(name="export_settings")
class AlbamExportSettings(bpy.types.PropertyGroup):
    # remove suffix added by blender when there are duplicate material names.
    # e.g. rename pl_skin.001 to pl_skin at export time.
    # Mostly useful for import-export tests to be able to compare exported vs original,
    # since many models can share a name and the blender database
    # is not cleaned in each test.
    remove_duplicate_materials_suffix : bpy.props.BoolProperty(default=True)
    export_visible : bpy.props.BoolProperty(default=False)
    force_lod255 : bpy.props.BoolProperty(default=False)


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
class ExportedItems(VirtualFileSystemBase, bpy.types.PropertyGroup):
    VFS_ID = "exported"


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
        row = self.layout.row()
        row.operator("albam.export", text="Export")
        row.operator("wm.export_options", icon="OPTIONS", text="")


@blender_registry.register_blender_type
class ALBAM_WM_OT_ExportOptions(bpy.types.Operator):
    """Set settings for exporting"""
    bl_label = "Export Options"
    bl_idname = "wm.export_options"

    export_visible: bpy.props.BoolProperty(name="Export only visible meshes", default=False)
    force_lod255: bpy.props.BoolProperty(name="Set LOD=255 for exported meshes", default=False)

    def execute(self, context):
        export_settings = context.scene.albam.export_settings
        export_settings.export_visible = self.export_visible
        export_settings.force_lod255 = self.force_lod255
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


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
        col.operator("albam.save_file_exported", icon="SORT_ASC", text="")
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
class ALBAM_OT_VirtualFileSystemSaveFileExported(
        ALBAM_OT_VirtualFileSystemSaveFileBase, bpy.types.Operator):
    bl_idname = "albam.save_file_exported"
    bl_label = "Save files"
    VFS_ID = "exported"


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemExportedCollapseToggle(
        ALBAM_OT_VirtualFileSystemCollapseToggleBase, bpy.types.Operator):
    bl_idname = "albam.file_item_exported_collapse_toggle"
    bl_label = "ALBAM_OT_VirtualFileSystemExportedCollapseToggle"
    VFS_ID = "exported"
    NODES_CACHE = {}


@blender_registry.register_blender_type
class ALBAM_UL_ExportedFileList(ALBAM_UL_VirtualFileSystemUIBase, bpy.types.UIList):
    collapse_toggle_operator_cls = ALBAM_OT_VirtualFileSystemExportedCollapseToggle


@blender_registry.register_blender_type
class ALBAM_OT_Export(bpy.types.Operator):
    bl_idname = "albam.export"
    bl_label = "Export item"

    def execute(self, context):  # pragma: no cover
        item = self.get_selected_item(context)
        try:
            self._execute(context, item)
        except Exception:
            bpy.ops.albam.error_handler_popup("INVOKE_DEFAULT")

        return {"FINISHED"}

    @staticmethod
    def _execute(context, item):
        asset = item.bl_object.albam_asset
        bl_obj = item.bl_object
        app_id = asset.app_id
        export_function = blender_registry.export_registry[(asset.app_id, asset.extension)]
        vfiles = export_function(item.bl_object)

        root_id = f"{app_id}-{bl_obj.name}-{round(time.time())}"
        vfile_root = VirtualFileData(app_id, root_id)
        vfs = context.scene.albam.exported
        vfs.add_vfiles_as_tree(app_id, vfile_root, vfiles)

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
        vfs = context.scene.albam.vfs
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
        vfs_i = context.scene.albam.vfs
        index_i = vfs_i.file_list_selected_index
        item_i = vfs_i.file_list[index_i]
        if item_i.is_archive:
            path_i = item_i.absolute_path
        else:
            arc_name = (item_i.tree_node_ancestors[0].node_id).split("::")[1]
            arc_node = [item for item in vfs_i.file_list
                        if item.is_archive is True and item.display_name == arc_name]
            path_i = arc_node[0].absolute_path
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
        vfs_i = context.scene.albam.vfs
        # TODO: simplify this mess
        if len(vfs_e.file_list) == 0 or len(vfs_i.file_list) == 0:
            return False
        index_e = vfs_e.file_list_selected_index
        index_i = vfs_i.file_list_selected_index
        if index_e < (len(vfs_e.file_list)):
            exported_item = vfs_e.file_list[index_e]
        else:
            return False
        if index_i < (len(vfs_i.file_list)):
            imported_item = vfs_i.file_list[index_i]
        else:
            return False
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
        current_item = vfs.selected_vfile
        return current_item and current_item.is_root


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemRemoveRootVFileExported(
        ALBAM_OT_VirtualFileSystemRemoveRootVFileBase, bpy.types.Operator):
    bl_idname = "albam.remove_exported"
    bl_label = "Remove exported files"
    VFS_ID = "exported"
