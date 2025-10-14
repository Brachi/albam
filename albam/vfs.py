import copy
import os
from pathlib import PureWindowsPath, Path

import bpy

from .apps import APPS
from .registry import blender_registry


@blender_registry.register_blender_prop
class TreeNode(bpy.types.PropertyGroup):
    node_id: bpy.props.StringProperty()
    root_id: bpy.props.StringProperty()
    depth: bpy.props.IntProperty(default=0)


@blender_registry.register_blender_prop
class VirtualFile(bpy.types.PropertyGroup):
    display_name: bpy.props.StringProperty()
    absolute_path: bpy.props.StringProperty()
    relative_path: bpy.props.StringProperty()  # posix style
    is_archive: bpy.props.BoolProperty(default=False)
    is_root: bpy.props.BoolProperty(default=False)
    is_expandable: bpy.props.BoolProperty(default=False)
    is_expanded: bpy.props.BoolProperty(default=False)
    albam_asset_type: bpy.props.StringProperty()  # TODO: enum albam.asset.AlbamAssetType
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
        vfs = self.get_vfs()
        try:
            return vfs.file_list[self.tree_node.root_id]
        except KeyError:
            return None

    @property
    def extension(self):
        """
        Allow up to 2 dots as an extension
        e.g. texname.tex.34 -> tex.34
        """
        SEP = "."
        name, _, extension = self.display_name.rpartition(SEP)
        if SEP in name:
            _, __, extension0 = name.rpartition(SEP)
            extension = SEP.join((extension0, extension))
        return extension

    def get_bytes(self):
        accessor = self.get_accessor()
        return accessor(self, bpy.context)

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


class VirtualFileSystemBase:
    file_list: bpy.props.CollectionProperty(type=VirtualFile)
    file_list_selected_index: bpy.props.IntProperty()

    SEPARATOR = "::"
    VFS_ID = "vfs"

    def get_vfile(self, app_id, relative_path):
        path = PureWindowsPath(relative_path)
        file_id = self.SEPARATOR.join((app_id,) + path.parts)
        return self.file_list[file_id]

    def select_vfile(self, app_id, relative_path):
        path = PureWindowsPath(relative_path)
        file_id = self.SEPARATOR.join((app_id,) + path.parts)
        self.file_list_selected_index = self.file_list.find(file_id)
        return self.file_list[file_id]

    def add_real_file(self, app_id, absolute_path):
        path = PureWindowsPath(absolute_path)
        vf = self.file_list.add()
        vf.is_root = True
        vf.name = f"{app_id}::{path.name}"
        vf.vfs_id = self.VFS_ID
        vf.app_id = app_id
        vf.display_name = path.name
        vf.absolute_path = absolute_path

        archive_loader_func = blender_registry.archive_loader_registry.get(
            (vf.app_id, vf.extension)
        )
        if archive_loader_func:
            vf.is_expandable = True
            vf.is_archive = True
            self._expand_archive(archive_loader_func, vf, app_id)
        else:
            vf.is_expandable = True
            vf.is_archive = False
            self._expand_directory(absolute_path, vf, app_id)

    def add_vfile(self, vfile_data):
        vf = self.file_list.add()
        vf.vfs_id = self.VFS_ID
        vf.app_id = vfile_data.app_id
        vf.name = f"{vfile_data.app_id}::{vfile_data.name}"
        vf.display_name = vfile_data.name
        vf.data_bytes = vfile_data.data_bytes or b""

        return vf

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

    def _expand_archive(self, archive_loader_func, vf, app_id):
        # Beware of chaning this, it was observed the reference
        # is lost in the middle of the loop below if using vf.name directly,
        # we get an empty string instead! Don't know why
        root_id = vf.name
        tree = Tree(root_id=vf.name, app_id=app_id)
        # TODO: popup if calling failed. Known exceptions + unexpected
        for rel_path in archive_loader_func(vf):
            tree.add_node_from_path(rel_path)
        for node in tree.flatten():
            self._add_vf_from_treenode(app_id, root_id, node)

    def _abs_to_rel_path(self, path_to_file, root_path):
        abs_path = Path(path_to_file)
        root_path = Path(root_path)
        return abs_path.relative_to(root_path)

    def _expand_directory(self, root_folder, vf, app_id):
        root_id = vf.name
        tree = Tree(root_id=vf.name, app_id=app_id)
        for files_folder, dirs, files in os.walk(root_folder):
            for file in files:
                rel_path = os.path.join(self._abs_to_rel_path(files_folder, root_folder), file)
                abs_path = os.path.join(files_folder, file)
                tree.add_node_from_path(rel_path, absolute_path=abs_path)
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
        child_vf.is_expandable = bool(node["children"])
        child_vf.albam_asset_type = blender_registry.albam_asset_types.get((app_id, child_vf.extension), "")
        vfile = node["vfile"]
        if vfile:
            child_vf.data_bytes = vfile.data_bytes
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


@blender_registry.register_blender_prop_albam(name="vfs")
class VirtualFileSystem(VirtualFileSystemBase, bpy.types.PropertyGroup):
    pass


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemAddFiles(bpy.types.Operator):
    """Add files to the virtual file system"""
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
        context.scene.albam.vfs.file_list.update()
        return {"FINISHED"}

    @staticmethod
    def _execute(context, directory, files):
        app_id = context.scene.albam.apps.app_selected
        vfs = context.scene.albam.vfs
        for f in files:
            absolute_path = os.path.join(directory, f.name)
            vfs.add_real_file(app_id, absolute_path)


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemAddFolder(bpy.types.Operator):
    """Add folder to the virtual file system"""
    bl_idname = "albam.add_folder"
    bl_label = "Add Folder"
    directory: bpy.props.StringProperty(subtype='DIR_PATH')  # NOQA
    files: bpy.props.CollectionProperty(name="added_files", type=bpy.types.OperatorFileListElement)  # NOQA

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        self.report({'INFO'}, f"Selected directory: {self.directory}")
        self._execute(context, self.directory, self.files)
        # context.scene.albam.vfs.file_list.update()
        return {"FINISHED"}

    @staticmethod
    def _execute(context, directory, files):
        app_id = context.scene.albam.apps.app_selected
        vfs = context.scene.albam.vfs
        # for f in files:
        # absolute_path = os.path.join(directory, "unpacked")
        vfs.add_real_file(app_id, directory)


class ALBAM_OT_VirtualFileSystemSaveFileBase:
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
    bl_description = "Save selected item as a new file"
    check_existing: CHECK_EXISTING
    filepath: FILEPATH

    VFS_ID = "vfs"

    def invoke(self, context, event):  # pragma: no cover
        vfs = self.get_vfs(self, context)
        vfile = vfs.selected_vfile
        self.filepath = vfile.display_name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        vfile = self.get_vfs(self, context).selected_vfile
        with open(self.filepath, 'wb') as w:
            w.write(vfile.get_bytes())
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        selected = cls.get_vfs(cls, context).selected_vfile
        is_root = False
        if selected:
            is_root = getattr(selected, "is_root")
        return selected and not is_root

    @staticmethod
    def get_vfs(cls_or_self, context):
        return getattr(context.scene.albam, cls_or_self.VFS_ID)


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemSaveFile(
        ALBAM_OT_VirtualFileSystemSaveFileBase, bpy.types.Operator):
    VFS_ID = "vfs"


class ALBAM_OT_VirtualFileSystemCollapseToggleBase:

    button_index: bpy.props.IntProperty(default=0)
    VFS_ID = None
    NODES_CACHE = None

    def execute(self, context):
        item_index = self.button_index
        vfs = getattr(context.scene.albam, self.VFS_ID)
        item_list = vfs.file_list
        item = item_list[item_index]
        item.is_expanded = not item.is_expanded
        if item.is_root:
            cache_key = item.name
        else:
            cache_key = item.tree_node.root_id
        if cache_key not in self.NODES_CACHE.keys():
            self.NODES_CACHE[cache_key] = {}
        self.NODES_CACHE[cache_key][item.name] = item.is_expanded

        vfs.file_list_selected_index = self.button_index
        item_list.update()
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemCollapseToggle(
        ALBAM_OT_VirtualFileSystemCollapseToggleBase, bpy.types.Operator):

    bl_idname = "albam.file_item_collapse_toggle"
    bl_label = "ALBAM_OT_VirtualFileSystemCollapseToggle"
    VFS_ID = "vfs"
    NODES_CACHE = {}


class ALBAM_OT_VirtualFileSystemRemoveRootVFileBase:
    bl_idname = "albam.remove_imported"
    bl_label = "Remove imported files"
    bl_description = "Remove files from the virtual file system"
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

    @classmethod
    def poll(cls, context):
        vfs = getattr(context.scene.albam, cls.VFS_ID)
        current_item = vfs.selected_vfile
        return current_item and current_item.is_root


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemRemoveRootVFile(
        ALBAM_OT_VirtualFileSystemRemoveRootVFileBase, bpy.types.Operator):
    """Remove files from vitual files system"""
    bl_idname = "albam.remove_imported"
    bl_label = "Remove imported files"
    VFS_ID = "vfs"


class VirtualFileData:
    # FIXME: normalize to posix path!

    def __init__(self, app_id, relative_path, data_bytes=None):
        self.app_id = app_id
        self.relative_path = relative_path
        self.name = os.path.basename(relative_path)  # TODO: posix only
        self.data_bytes = data_bytes

    @property
    def extension(self):
        """
        Allow up to 2 dots as an extension
        e.g. texname.tex.34 -> tex.34
        """
        SEP = "."
        name, _, extension = self.relative_path.rpartition(SEP)
        if SEP in name:
            _, __, extension0 = name.rpartition(SEP)
            extension = SEP.join((extension0, extension))
        return extension


class Tree:
    PATH_SEPARATOR = "::"
    OS_PATH_SEPARATOR = "/"

    def __init__(self, root_id=None, app_id=None):  # FIXME: make app_id mandatory
        self.root = []
        self.root_id = root_id
        self.nodes = {}
        self.app_id = app_id

    def _find_node_in_level(self, node_name, node_level):
        node_found = None
        for node in node_level:
            if node["name"] == node_name:
                node_found = node
                break
        return node_found

    def add_node_from_path(self, full_path, vfile=None, absolute_path=""):
        p = PureWindowsPath(full_path)
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
                    "node_id": self.generate_node_id(path_parts[0 : i + 1], use_prefix=True),
                    "relative_path": self.generate_node_id(path_parts[0 : i + 1], use_prefix=False),
                    "full_path": absolute_path,
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
            "full_path": absolute_path,
            "ancestors_ids": ancestors_ids,
        }
        current_dir.append(leaf_node)
        self.nodes[node_id] = leaf_node

    def generate_node_id(self, parts, use_prefix=True):
        prefix = (self.app_id or "") + self.PATH_SEPARATOR
        sep = self.PATH_SEPARATOR if use_prefix else self.OS_PATH_SEPARATOR
        body = sep.join(parts)
        if use_prefix:
            return prefix + body
        return body

    @staticmethod
    def sort_node(node):
        """
        Sort expandable items first
        """
        return node['name'] if node['children'] else "zzz" + node['name']

    def flatten(self, flat_tree=None, current_level=None):
        flat_tree = flat_tree or []
        current_level = current_level or self.root

        for node in sorted(current_level, key=self.sort_node):
            flat_tree.append(node)
            if node['children']:
                self.flatten(flat_tree, node['children'])
        return flat_tree
