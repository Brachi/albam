import copy
import os
from pathlib import PureWindowsPath

import bpy

from albam.apps import APPS
from albam.cache import NODES_CACHE
from albam.registry import blender_registry


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemBlenderCollapseToggle(bpy.types.Operator):
    bl_idname = "albam.file_item_collapse_toggle"
    bl_label = "ALBAM_OT_VirtualFileSystemBlenderCollapseToggle"

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
class VirtualFileBlender(bpy.types.PropertyGroup):
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
class VirtualFileSystemBlender(bpy.types.PropertyGroup):
    file_list : bpy.props.CollectionProperty(type=VirtualFileBlender)
    file_list_selected_index : bpy.props.IntProperty()
    app_selected : bpy.props.EnumProperty(name="", items=APPS)
    # FIXME: update_app_data necessary for reen configuration
    # app_selected : bpy.props.EnumProperty(name="", items=APPS, update=update_app_data)
    # app_dir : bpy.props.StringProperty(name="", description="", update=update_app_caches)
    # app_config_filepath : bpy.props.StringProperty(name="", update=update_app_caches)
    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()

    # FIXME: move out of here, breaking reen
    # def get_app_config_filepath(self, app_id):
    # return APP_CONFIG_FILE_CACHE.get(app_id)

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
        if vfile.is_expandable:
            return None
        return vfile


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemBlenderAddFiles(bpy.types.Operator):

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
class ALBAM_OT_VirtualFileSystemBlenderSaveFile(bpy.types.Operator):
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
        vfile = context.scene.albam.file_explorer.selected_vfile
        self.filepath = vfile.display_name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        vfile = context.scene.albam.file_explorer.selected_vfile
        with open(self.filepath, 'wb') as w:
            w.write(vfile.get_bytes())
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.albam.file_explorer.selected_vfile)


class VirtualFileSystem:

    def __init__(self, vfs_id):
        self.vfs_id = vfs_id
        self.vfiles = []

    def append(self, vfile):  # XXX deprecated, change to append
        self.vfiles.append(vfile)

    def extend(self, vfiles):
        self.vfiles.extend(vfiles)

    @property
    def vfs(self):
        return getattr(bpy.context.scene.albam, self.vfs_id)

    def commit(self, root_vfile=None, vfiles=None):
        # TODO: no archive_loader_func allowed if len(self.vfiles > 1) ?
        vfiles = vfiles or self.vfiles

        if root_vfile:
            root_id = f"{root_vfile.app_id}::{root_vfile.name}"
            tree = Tree(root_id)
            bl_vf = self.vf_to_bl_vf(root_vfile)
            bl_vf.is_expandable = True
            bl_vf.is_root = True

            for vfile in vfiles:
                tree.add_node_from_path(vfile.relative_path, vfile)

            for node in tree.flatten():
                self.node_to_blvf(root_id, bl_vf.app_id, node)

            return bl_vf

        for vf in vfiles:
            bl_vf = self.vf_to_bl_vf(vf)

            archive_loader_func = blender_registry.archive_loader_registry.get(
                (vf.app_id, vf.extension)
            )
            if archive_loader_func:
                root_id = f"{vf.app_id}::{vf.name}"
                tree = Tree(root_id=root_id)
                bl_vf.is_expandable = True
                bl_vf.is_archive = True
                # TODO: popup if calling failed. Known exceptions + unexpected
                for rel_path in archive_loader_func(vf):
                    tree.add_node_from_path(rel_path)
                for node in tree.flatten():
                    self.node_to_blvf(root_id, vf.app_id, node)
        return bl_vf  # XXX only last one!

    def vf_to_bl_vf(self, vf):
        bl_vf = self.vfs.file_list.add()
        bl_vf.vfs_id = self.vfs_id
        bl_vf.app_id = vf.app_id
        bl_vf.name = f"{vf.app_id}::{vf.name}"
        bl_vf.display_name = vf.name
        bl_vf.file_path = vf.absolute_path or ""
        bl_vf.data_bytes = vf.data_bytes or b""

        return bl_vf

    def node_to_blvf(self, root_id, app_id, node):
        bl_vf = self.vfs.file_list.add()
        bl_vf.vfs_id = self.vfs_id
        bl_vf.app_id = app_id

        bl_vf.name = node["node_id"]
        bl_vf.relative_path = node["relative_path"]
        bl_vf.display_name = node["name"]
        bl_vf.is_expandable = bool(node["children"])
        vfile = node["vfile"]
        if vfile:
            bl_vf.data_bytes = vfile.data_bytes

        bl_vf.tree_node.depth = node["depth"] + 1
        bl_vf.tree_node.root_id = root_id
        for ancestor_id in node["ancestors_ids"]:
            ancestor_node = bl_vf.tree_node_ancestors.add()
            ancestor_node.node_id = ancestor_id


class VirtualFile:
    # FIXME: normalize to posix path!

    def __init__(self, app_id, relative_path, data_bytes=None):
        self.app_id = app_id
        self.absolute_path = None
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
        name , _ , extension = self.relative_path.rpartition(SEP)
        if SEP in name:
            _, __, extension0 = name.rpartition(SEP)
            extension = SEP.join((extension0, extension))
        return extension

    @classmethod
    def from_real_file(cls, app_id, file_path):
        relative_path = os.path.basename(file_path)  # TODO: optional prefix to calculate relative_path
        # TODO: error handling
        vf = cls(app_id, relative_path)
        vf.absolute_path = file_path
        return vf


class Tree:
    PATH_SEPARATOR = "::"
    OS_PATH_SEPARATOR = "/"

    def __init__(self, root_id=None):
        self.root = []
        self.root_id = root_id
        self.nodes = {}

    def _find_node_in_level(self, node_name, node_level):
        node_found = None
        for node in node_level:
            if node["name"] == node_name:
                node_found = node
                break
        return node_found

    def add_node_from_path(self, full_path, vfile=None):
        p = PureWindowsPath(full_path)
        path_parts = p.parts
        leaf_name = path_parts[-1]

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
            "ancestors_ids": ancestors_ids,
        }
        current_dir.append(leaf_node)
        self.nodes[node_id] = leaf_node

    def generate_node_id(self, parts, use_prefix=True):
        prefix = (self.root_id or "") + self.PATH_SEPARATOR
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
