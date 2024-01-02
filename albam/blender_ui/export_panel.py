import time

import bpy

from albam.registry import blender_registry
from albam.vfs import VirtualFileSystem, VirtualFile
from .import_panel import FileListItem
from albam.engines.mtfw.archive import serialize_arc


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
    file_list: bpy.props.CollectionProperty(type=FileListItem)
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
class ALBAM_OT_SaveFile2(bpy.types.Operator):
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
class ALBAM_OT_FileItemCollapseToggle2(bpy.types.Operator):  # XXX super dirty, quick copy paste
    bl_idname = "albam.file_item_collapse_toggle_2"
    bl_label = "ALBAM_OT_FileItemCollapseToggle2"

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
        self._execute(item)
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

    def execute(self, context):  # pragma: no cover
        vfs_i = context.scene.albam.file_explorer
        vfs_e = context.scene.albam.exported
        index = vfs_i.file_list_selected_index
        item = vfs_i.file_list[index]
        parent_node = ""
        #print("selected item name {}".format(item.name))
        #print ("selected intem extension is {}".format(item.extension))
        # get parent name 
        if item.is_archive:
            parent_node = item.name
        else:
            parent_node = item.tree_node_ancestors[0].node_id
        #get only files from the virtual file system
        imported = [item for item in vfs_i.file_list if item.is_expandable == False]
        arc_files ={}
        #add only files the belong to selected arc parent to the dictionary
        for i in imported:
            try:
                parent = i.tree_node_ancestors[0].node_id
            except:
                continue
            if parent == parent_node:
                arc_files[i.relative_path] = i

        e_index = vfs_e.file_list_selected_index
        e_item = vfs_e.file_list[e_index]
        # get all exported files and add them to the dictionray
        exported = [item for item in vfs_e.file_list if item.is_expandable == False]
        for e in exported:
            try:
                parent = e.tree_node_ancestors[0].node_id
            except:
                continue
            if parent == e_item.name:
                arc_files[e.relative_path] = e
        files = list(arc_files.values())
        # sorting
        f_sorted = []
        f_mrl = []
        f_mod = []
        f_tail = []
        for f in files:
            if f.extension == "tex":
                f_sorted.append(f)
            elif f.extension == "mrl":
                f_mrl.append(f)
            elif f.extension == "mod":
                f_mod.append(f)
            else:
                f_tail.append(f)
        f_sorted.extend(f_mrl)
        f_sorted.extend(f_mod)
        f_sorted.extend(f_tail)

        arc = serialize_arc(f_sorted)
        with open(self.filepath, "wb") as f:
            f.write(arc)
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        # TODO
        #return False
        vfs = context.scene.albam.exported
        current_item = vfs.__class__.get_selected_item()
        return current_item and current_item.is_root


@blender_registry.register_blender_type
class ALBAM_PT_AssetObject(bpy.types.Panel):
    bl_label = "Albam Asset"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):  # pragma: no cover
        obj = context.object
        self.layout.row().prop(obj.albam_asset, "app_id")
        self.layout.row().prop(obj.albam_asset, "relative_path")

    @classmethod
    def poll(cls, context):  # pragma: no cover
        obj = context.object
        return obj and obj.albam_asset.relative_path


@blender_registry.register_blender_type
class ALBAM_PT_AssetImage(bpy.types.Panel):
    bl_label = "Albam Asset"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Albam"  # TODO: global option to hide it by default

    def draw(self, context):  # pragma: no cover
        im = context.space_data.image

        self.layout.row().prop(im.albam_asset, "app_id")
        self.layout.row().prop(im.albam_asset, "relative_path")

        app_id = im.albam_asset.app_id
        custom_props = im.albam_custom_properties.get_appid_custom_properties(app_id)
        for k in custom_props.__annotations__:
            self.layout.prop(custom_props, k)

    @classmethod
    def poll(cls, context):  # pragma: no cover
        return bool(context.space_data.image)
