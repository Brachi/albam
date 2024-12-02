import copy
import os
import glob
from pathlib import PureWindowsPath

import bpy

from albam.apps import APPS
from albam.registry import blender_registry
from albam.vfs import (VirtualFile, VirtualFileSystem, Tree, TreeNode,
                        ALBAM_OT_VirtualFileSystemCollapseToggleBase,
                        ALBAM_OT_VirtualFileSystemRemoveRootVFileBase,
                        VirtualFileSystemBase)
@blender_registry.register_blender_prop
class RealFile(bpy.types.PropertyGroup):
    # FIXME: consider strings, seems pretty inefficient

    display_name: bpy.props.StringProperty()
    absolute_path: bpy.props.StringProperty()
    relative_path: bpy.props.StringProperty()  # posix style
    is_archive: bpy.props.BoolProperty(default=False)
    is_root: bpy.props.BoolProperty(default=False)
    is_expandable: bpy.props.BoolProperty(default=False)
    is_expanded: bpy.props.BoolProperty(default=False)
    category: bpy.props.StringProperty()
    tree_node: bpy.props.PointerProperty(type=TreeNode)  # consider adding the attributes here directly
    # FIXME: consider strings, seems pretty inefficient
    tree_node_ancestors: bpy.props.CollectionProperty(type=TreeNode)

    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    vfs_id: bpy.props.StringProperty()

    data_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821

    @property
    def relative_path_windows(self):
        return self._get_relative_path_windows()

    @property
    def relative_path_windows_no_ext(self):
        return self._get_relative_path_windows(include_extension=False)

    @property
    def root_vfile(self):
        rfs = self.get_vfs()
        try:
            return rfs.file_list[self.tree_node.root_id]
        except KeyError:
            return None

    def get_bytes(self):
        return self.real_file_accessor(self, None)

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

    def get_accessor(self):
        if self.absolute_path:
            return self.real_file_accessor
        if self.data_bytes:
            return lambda vfile, context: self.data_bytes
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
        with open(file_item.absolute_path, 'rb') as f:
            return f.read()

    def get_vfs(self):
        return getattr(bpy.context.scene.albam, self.vfs_id)

    def _get_relative_path_windows(self, include_extension=True):
        p = PureWindowsPath(self.relative_path)
        if not include_extension:
            return PureWindowsPath(*p.parts[:-1] + (p.stem,))
        return p

class RealFileSystemBase:
    file_list : bpy.props.CollectionProperty(type=RealFile)
    file_list_selected_index: bpy.props.IntProperty()

    SEPARATOR = "::"
    VFS_ID = "rfs"

    def get_vfile(self, app_id, relative_path):
        path = PureWindowsPath(relative_path)
        file_id = self.SEPARATOR.join((app_id,) + path.parts)
        return self.file_list[file_id]

    def select_vfile(self, app_id, relative_path):
        path = PureWindowsPath(relative_path)
        file_id = self.SEPARATOR.join((app_id,) + path.parts)
        self.file_list_selected_index = self.file_list.find(file_id)
        return self.file_list[file_id]

    def add_root_folder(self, app_id, absolute_path):
        path = PureWindowsPath(absolute_path)
        f = self.file_list.add()
        f.is_root = True
        f.name = path.name
        f.vfs_id = self.VFS_ID
        f.app_id = app_id
        f.display_name = path.name
        f.absolute_path = absolute_path
        f.is_expandable = True
        self._expand_archive(app_id, f)

    def add_vfile(self, vfile_data):
        vf = self.file_list.add()
        vf.vfs_id = self.VFS_ID
        vf.app_id = vfile_data.app_id
        vf.name = f"{vfile_data.app_id}::{vfile_data.name}"
        vf.display_name = vfile_data.name
        vf.absolute_path = vfile_data.absolute_path
        if not vfile_data.is_folder:
            vf.data_bytes = vfile_data.data_bytes or b""

        return vf

    def add_folder(self, app_id, absolute_path):
        f = self.file_list.add()
        f.vfs_id = self.VFS_ID
        f.app_id = app_id
        f.display_name = os.path.basename(os.path.normpath(absolute_path))
        f.name = f"{app_id}::{f.display_name}"
        f.is_expandable = True
        return f

    def add_file(self, app_id, absolute_path):
        f = self.file_list.add()
        f.vfs_id = self.VFS_ID
        f.app_id = app_id
        f.absolute_path = absolute_path
        f.display_name = os.path.basename(os.path.normpath(absolute_path))
        f.name = f"{app_id}::{f.display_name}"
        f.data_bytes = f.get_bytes()
        return f

    def add_vfiles_as_tree(self, app_id, root_vfile_data, vfiles_data):
        root_id = f"{app_id}::{root_vfile_data.name}"
        tree = Tree(root_id, app_id)
        bl_vf = self.add_vfile(root_vfile_data)
        bl_vf.is_expandable = True
        bl_vf.is_root = True

        for vfile_data in vfiles_data:
            tree.add_node_from_path(vfile_data.relative_path, vfile_data)

        for node in tree.flatten():
            self._add_vf_from_treenode(bl_vf.app_id, root_id, node)

        return bl_vf

    def _expand_archive(self, app_id, rf):
        # Beware of chaning this, it was observed the reference
        # is lost in the middle of the loop below if using vf.name directly,
        # we get an empty string instead! Don't know why
        root_id = rf.name
        root_path = rf.absolute_path
        tree = RealTree(root_id=rf.name, app_id=app_id, root_path = root_path)
        # TODO: popup if calling failed. Known exceptions + unexpected
        for p in glob.glob(os.path.join(rf.absolute_path,"*")):
            tree.add_node_from_path(p)
        for node in tree.flatten():
            self._add_vf_from_treenode(app_id, root_id, node)


    def _add_vf_from_treenode(self, app_id, root_id, node):
        child_vf = self.file_list.add()
        child_vf.vfs_id = self.VFS_ID
        child_vf.app_id = app_id
        child_vf.name = node["node_id"]
        child_vf.relative_path = node["relative_path"]
        child_vf.absolute_path = node["full_path"]
        child_vf.display_name = node["name"]
        child_vf.is_expandable = os.path.isdir(child_vf.absolute_path)
        child_vf.category = blender_registry.file_categories.get((app_id, child_vf.extension), "")
        if not child_vf.is_expandable:
            child_vf.data_bytes = child_vf.get_bytes()
        else:
            self._expand_archive(app_id, child_vf)
        child_vf.tree_node.depth = node["depth"] + 1
        child_vf.tree_node.root_id = root_id
        for ancestor_id in node["ancestors_ids"]:
            ancestor_node = child_vf.tree_node_ancestors.add()
            ancestor_node.node_id = ancestor_id

    @property
    def selected_vfile(self):
        if len(self.file_list) == 0:
            return None
        index = self.file_list_selected_index
        try:
            vfile = self.file_list[index]
        except IndexError:
            # list might have been cleared
            return
        if not vfile.is_root and vfile.is_expandable:
            return None
        return vfile


@blender_registry.register_blender_prop_albam(name="rfs")
class RealFileSystem(RealFileSystemBase, bpy.types.PropertyGroup):
    pass


@blender_registry.register_blender_type
class ALBAM_OT_RealFileSystemAddRootFolder(bpy.types.Operator):
    bl_idname = "albam.add_real_root_folder"
    bl_label = "Add Real Root Files"
    directory: bpy.props.StringProperty(subtype="DIR_PATH")  # NOQA
    files: bpy.props.CollectionProperty(name="added_files", type=bpy.types.OperatorFileListElement)  # NOQA
    filter_folder = bpy.props.BoolProperty(
        default=True,
        options={"HIDDEN"}
        )
    # FIXME: use registry, un-hardcode
    #filter_glob: bpy.props.StringProperty(default="*.arc;*.pak", options={"HIDDEN"})  # NOQA

    def invoke(self, context, event):  # pragma: no cover
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):  # pragma: no cover
        self._execute(context, self.directory, self.files)
        context.scene.albam.rfs.file_list.update()
        return {"FINISHED"}

    @staticmethod
    def _execute(context, directory, files):
        app_id = context.scene.albam.apps.app_selected
        rfs = context.scene.albam.rfs
        for f in files:
            absolute_path = os.path.join(directory, f.name)
            rfs.add_root_folder(app_id, absolute_path)

class ALBAM_OT_RealFileSystemCollapseToggleBase:

    button_index: bpy.props.IntProperty(default=0)
    VFS_ID = None
    NODES_CACHE = None

    def execute(self, context):
        item_index = self.button_index
        rfs = getattr(context.scene.albam, self.VFS_ID)
        item_list = rfs.file_list
        item = item_list[item_index]
        item.is_expanded = not item.is_expanded
        self.NODES_CACHE[item.name] = item.is_expanded

        rfs.file_list_selected_index = self.button_index
        item_list.update()
        return {"FINISHED"}

@blender_registry.register_blender_type
class ALBAM_OT_RealFileSystemCollapseToggle(
        ALBAM_OT_RealFileSystemCollapseToggleBase, bpy.types.Operator):

    bl_idname = "albam.real_file_item_collapse_toggle"
    bl_label = "ALBAM_OT_VirtualFileSystemCollapseToggle"
    VFS_ID = "rfs"
    NODES_CACHE = {}

class ALBAM_OT_RealFileSystemRemoveRootBase:
    bl_idname = None
    bl_label = None
    VFS_ID = ""

    def execute(self, context):
        vfs = getattr(context.scene.albam, self.VFS_ID)
        vfiles_to_remove = []
        root_node_index = vfs.file_list_selected_index
        archive_node = vfs.file_list[root_node_index]
        for i in range(len(vfs.file_list)):
            parent = vfs.file_list[i].tree_node.root_id
            if parent == archive_node.name:
                vfiles_to_remove.append(i)

        vfiles_to_remove.reverse()
        for i in range(len(vfiles_to_remove)):
            vfs.file_list.remove(vfiles_to_remove[i])
        vfs.file_list.remove(root_node_index)

        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_RealFileSystemRemoveRoot(
        ALBAM_OT_RealFileSystemRemoveRootBase, bpy.types.Operator):

    bl_idname = "albam.remove_imported_real"
    bl_label = "Remove imported real files"
    VFS_ID = "rfs"


class RealFileData:
    # FIXME: normalize to posix path!

    def __init__(self, app_id, absolute_path, data_bytes=None):
        self.app_id = app_id
        self.absolute_path = absolute_path
        self.is_folder = os.path.isdir(absolute_path)
        self.name = os.path.basename(absolute_path)  # TODO: posix only
        if not self.is_folder:
            self.data_bytes = data_bytes

    @property
    def extension(self):
        """
        Allow up to 2 dots as an extension
        e.g. texname.tex.34 -> tex.34
        """
        SEP = "."
        name , _ , extension = self.absolute_path.rpartition(SEP)
        if SEP in name:
            _, __, extension0 = name.rpartition(SEP)
            extension = SEP.join((extension0, extension))
        return extension


class RealTree(Tree):
    OS_PATH_SEPARATOR = "\\"

    def __init__(self, root_id=None, app_id=None, root_path=None):
        super().__init__(root_id, app_id)
        self.root_path = root_path

    def add_node_from_path(self, full_path, vfile=None):
        p = PureWindowsPath(os.path.relpath(full_path, self.root_path))
        path_parts = p.parts
        # FIXME: adding a single root node doesn't work
        # E.g. when importing a single file mod, it doesn't have
        # albam_asset.relative_path properly set, and when exporting
        # the file will be nameless
        leaf_name = path_parts[-1] if path_parts else p.name

        current_level = 0
        current_dir = self.root
        ancestors_ids = [] if not self.root_id else [self.root_id]
        for i in range(len(path_parts) - 1):
            path_part = path_parts[i]
            existing_node = self._find_node_in_level(node_name=path_part, node_level=current_dir)
            if existing_node:
                new_node = existing_node
            else:
                new_node = {
                    "name": path_part,
                    "children": [],
                    "depth": current_level,
                    "vfile": vfile,
                    "node_id": self.generate_node_id(path_parts[0: i + 1], use_prefix=True),
                    "relative_path": self.generate_node_id(path_parts[0: i + 1], use_prefix=False),
                    "full_path": full_path,
                    "ancestors_ids": copy.copy(ancestors_ids),
                }
                current_dir.append(new_node)
                self.nodes[new_node["node_id"]] = new_node

            ancestors_ids.append(new_node["node_id"])
            current_level += 1
            current_dir = new_node["children"]

        node_id = self.generate_node_id(path_parts, use_prefix=True)
        leaf_node = {
            "name": leaf_name,
            "children": [],
            "depth": current_level,
            "vfile": vfile,
            "node_id": node_id,
            "relative_path": self.generate_node_id(path_parts, use_prefix=False),
            "full_path": full_path,
            "ancestors_ids": ancestors_ids,
        }
        current_dir.append(leaf_node)
        self.nodes[node_id] = leaf_node