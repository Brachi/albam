import copy
import os
from pathlib import PureWindowsPath

import bpy
from albam.registry import blender_registry


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
