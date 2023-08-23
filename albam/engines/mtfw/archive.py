import io
import os
import zlib

from kaitaistruct import KaitaiStream

from albam.lib.tree import Tree
from albam.registry import blender_registry
from . import EXTENSION_TO_FILE_ID, FILE_ID_TO_EXTENSION
from .structs.arc import Arc


@blender_registry.register_archive_loader(app_id="re0", extension="arc")
@blender_registry.register_archive_loader(app_id="re1", extension="arc")
@blender_registry.register_archive_loader(app_id="re5", extension="arc")
def arc_loader(file_item, context):
    item_list = context.scene.albam.file_explorer.file_list
    arc = ArcWrapper(file_item.app_id, file_item.file_path)

    for node in arc.tree.flatten():
        new_item = item_list.add()
        new_item.name = node["node_id"]
        new_item.display_name = node["name"]
        new_item.is_expandable = bool(node["children"])
        new_item.app_id = file_item.app_id

        new_item.tree_node.depth = node["depth"] + 1
        new_item.tree_node.root_id = arc.tree.root_id
        for ancestor_id in node["ancestors_ids"]:
            ancestor_node = new_item.tree_node_ancestors.add()
            ancestor_node.node_id = ancestor_id


@blender_registry.register_archive_accessor(app_id="re0", extension="arc")
@blender_registry.register_archive_accessor(app_id="re1", extension="arc")
@blender_registry.register_archive_accessor(app_id="re5", extension="arc")
def arc_accessor(file_item, context):
    item_list = context.scene.albam.file_explorer.file_list
    app_id = file_item.app_id
    root = item_list[file_item.tree_node.root_id]

    # TODO: error handling, e.g. when file_path doesn't exist
    arc = ArcWrapper(app_id, file_path=root.file_path)
    arc_filename = os.path.basename(root.file_path)

    prefix = f"{app_id}::{arc_filename}::"
    canonical_name = file_item.name.replace(prefix, "").replace("::", arc.PATH_SEPARATOR)
    file_path, ext = os.path.splitext(canonical_name)
    ext = ext.replace(".", "")
    file_type = EXTENSION_TO_FILE_ID[ext]
    file_bytes = arc.get_file(file_path, file_type)

    return file_bytes


class ArcWrapper:
    PATH_SEPARATOR = "\\"

    def __init__(self, app_id, file_path):
        self.file_path = file_path
        self.app_id = app_id
        with open(file_path, "rb") as f:
            self.parsed = Arc(KaitaiStream(io.BytesIO(f.read())))
            self._tree = None

    def get_file_entries_by_type(self, file_type):
        filtered = []
        for fe in self.parsed.file_entries:
            if fe.file_type == file_type:
                filtered.append(fe)
        return filtered

    def get_files_by_extension(self, extension):
        try:
            file_type = EXTENSION_TO_FILE_ID[extension]
        except KeyError:
            raise RuntimeError(f"Extension {extension} unknown")
        files = []
        for file_entry in self.get_file_entries_by_type(file_type):
            t = (file_entry.file_path, self.get_file(file_entry.file_path, file_type))
            files.append(t)
        return files

    def get_file_entries(self):
        file_entries = []
        for fe in self.parsed.file_entries:
            ext = FILE_ID_TO_EXTENSION.get(fe.file_type, fe.file_type)
            fe.file_path_with_ext = f"{fe.file_path}.{ext}"
            file_entries.append(fe)
        return file_entries

    def get_file(self, file_path, file_type):
        file_ = None

        for fe in self.parsed.file_entries:
            if fe.file_path == file_path and fe.file_type == file_type:
                try:
                    file_ = zlib.decompress(fe.raw_data)
                    break
                except EOFError:
                    print(f"Requested to read out of bounds. Offset: {fe.offset}")
                    raise
        return file_

    @property
    def tree(self):
        if self._tree is not None:
            return self._tree

        root_id = self.app_id + "::" + os.path.basename(self.file_path)
        tree = Tree(root_id=root_id)
        for file_entry in self.get_file_entries():
            tree.add_node_from_path(file_entry.file_path_with_ext)
        self._tree = tree

        return self._tree
