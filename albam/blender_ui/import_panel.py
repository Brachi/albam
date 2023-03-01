import os

import bpy

from albam.registry import blender_registry


class ALBAM_OT_Import(bpy.types.Operator):
    bl_idname = "albam_import.item"
    bl_label = "import item"

    def execute(self, context):  # pragma: no cover
        item = self.get_selected_item(context)
        self._execute(item, context)
        return {"FINISHED"}

    @staticmethod
    def _execute(item, context):
        import_function = blender_registry.import_registry[item.extension]

        bl_container = import_function(item, context)

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
        if not item or item.extension not in blender_registry.importable_extensions:
            return False
        return True

    @staticmethod
    def get_selected_item(context):
        if len(context.scene.albam.file_explorer.file_list) == 0:
            return None
        index = context.scene.albam.file_explorer.file_list_selected_index
        return context.scene.albam.file_explorer.file_list[index]


class ALBAM_OT_FileItemCollapseToggle(bpy.types.Operator):
    bl_idname = "albam.file_item_collapse_toggle"
    bl_label = "ALBAM_OT_FileItemCollapseToggle"

    button_index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        item_index = self.button_index
        item_list = context.scene.albam.file_explorer.file_list
        item = item_list[item_index]
        item.is_expanded = not item.is_expanded
        context.scene.albam.file_explorer.file_list_selected_index = self.button_index

        item_list.update()
        return {"FINISHED"}


class TreeNode(bpy.types.PropertyGroup):
    node_id: bpy.props.StringProperty()
    root_id: bpy.props.StringProperty()
    depth: bpy.props.IntProperty(default=0)


class FileListItem(bpy.types.PropertyGroup):
    display_name: bpy.props.StringProperty()
    file_path: bpy.props.StringProperty()
    extension: bpy.props.StringProperty()
    is_archive: bpy.props.BoolProperty(default=False)
    is_expandable: bpy.props.BoolProperty(default=False)
    is_expanded: bpy.props.BoolProperty(default=False)

    tree_node: bpy.props.PointerProperty(type=TreeNode)
    tree_node_ancestors: bpy.props.CollectionProperty(type=TreeNode)

    def get_buffer(self, context):
        file_list = context.scene.albam.file_explorer.file_list
        root = file_list[self.tree_node.root_id]
        archive_accessor_func = blender_registry.archive_accessor_registry.get(root.extension)
        if not archive_accessor_func:
            return
        return archive_accessor_func(self, context)


class FileExplorerData(bpy.types.PropertyGroup):
    file_list: bpy.props.CollectionProperty(type=FileListItem)
    file_list_selected_index: bpy.props.IntProperty()


class ALBAM_OT_AddFiles(bpy.types.Operator):
    DIRECTORY = bpy.props.StringProperty(subtype="DIR_PATH")
    FILES = bpy.props.CollectionProperty(name="added_files", type=bpy.types.OperatorFileListElement)
    # TODO: use registry, un-hardcode
    FILTER_GLOB = bpy.props.StringProperty(default="*.arc", options={"HIDDEN"})

    bl_idname = "albam.add_files"
    bl_label = "Add File(s)"
    directory: DIRECTORY
    files: FILES
    filter_glob: FILTER_GLOB

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
        for f in files:
            file_item = context.scene.albam.file_explorer.file_list.add()
            file_item.name = f.name
            file_item.display_name = f.name
            file_item.file_path = os.path.join(directory, f.name)
            file_item.extension = os.path.splitext(file_item.file_path)[1].replace(".", "")

            archive_loader_func = blender_registry.archive_loader_registry.get(file_item.extension)
            if archive_loader_func:
                file_item.is_expandable = True
                file_item.is_archive = True
                archive_loader_func(file_item, context)


class ALBAM_UL_FileList(bpy.types.UIList):
    EXPAND_ICONS = {
        False: "TRIA_RIGHT",
        True: "TRIA_DOWN",
    }

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        for _ in range(item.tree_node.depth):
            layout.split(factor=0.1)

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

        item_list = getattr(data, propname)
        for item in item_list:
            if item.is_archive:
                filtered_items.append(self.bitflag_filter_item)
                continue
            ancestors = [item_list[anc.node_id] for anc in item.tree_node_ancestors]
            is_visible = all(a.is_expanded for a in ancestors)
            if is_visible:
                filtered_items.append(self.bitflag_filter_item)
            else:
                filtered_items.append(0)

        return filtered_items, []


class ALBAM_PT_FileExplorer(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_FileExplorer"
    bl_label = "Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        self.layout.operator("albam.add_files", icon="FILE_NEW", text="Add File(s)")
        self.layout.row()
        self.layout.row()
        row = self.layout.row()
        row.template_list(
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
        self.layout.operator("albam_import.item", text="Import")
        self.layout.row()
        self.layout.row()
