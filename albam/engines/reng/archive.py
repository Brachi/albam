import io
import os
import struct

from kaitaistruct import KaitaiStream
import pymmh3 as mmh3
import zlib
import zstd

from albam.lib.tree import Tree
from albam.registry import blender_registry
from .structs.pak import Pak


@blender_registry.register_archive_loader(app_id="re2", extension='pak')
@blender_registry.register_archive_loader(app_id="re3", extension='pak')
@blender_registry.register_archive_loader(app_id="re8", extension='pak')
@blender_registry.register_archive_loader(app_id="re2_non_rt", extension='pak')
@blender_registry.register_archive_loader(app_id="re3_non_rt", extension='pak')
def pak_loader(file_item, context):
    item_list = context.scene.albam.file_explorer.file_list
    app_config_filepath = context.scene.albam.file_explorer.app_config_filepath
    app_id = file_item.app_id  # blender bug, needs reference or might mutate
    if not app_config_filepath:
        # TODO: custom exception that will result in informative popup
        print("WARNING: no app_config_filepath")
        return
    pak = PakWrapper(app_id, file_item.file_path, app_config_filepath)
    for node in pak.tree.flatten():
        new_item = item_list.add()
        new_item.name = node["node_id"]
        new_item.display_name = node["name"]
        new_item.is_expandable = bool(node["children"])
        new_item.app_id = app_id

        new_item.tree_node.depth = node["depth"] + 1
        new_item.tree_node.root_id = pak.tree.root_id
        for ancestor_id in node["ancestors_ids"]:
            ancestor_node = new_item.tree_node_ancestors.add()
            ancestor_node.node_id = ancestor_id


@blender_registry.register_archive_accessor(app_id="re2", extension="pak")
@blender_registry.register_archive_accessor(app_id="re2_non_rt", extension="pak")
@blender_registry.register_archive_accessor(app_id="re3", extension="pak")
@blender_registry.register_archive_accessor(app_id="re3_non_rt", extension="pak")
@blender_registry.register_archive_accessor(app_id="re8", extension="pak")
def pak_accessor(file_item, context):
    item_list = context.scene.albam.file_explorer.file_list
    root = item_list[file_item.tree_node.root_id]

    # XXX hacky quicky begins
    file_virtual_path = file_item.name.replace(root.name + "::", "").replace("::", "/")
    # XXX hacky quicky ends
    app_config_filepath = context.scene.albam.file_explorer.get_app_config_filepath(file_item.app_id)
    if not app_config_filepath:
        # TODO: custom exception that will result in informative popup, with solution
        raise RuntimeError(f'App "{file_item.app_id}" doesn\'t have its file config loaded')
    pak = PakWrapper(file_item.app_id, root.file_path, app_config_filepath)
    return pak.get_file(file_virtual_path)


class PakWrapper:
    PATH_SEPARATOR = "/"
    HEADER_SIZE = 16
    NUM_FILES_OFFSET = 8
    FILE_ENTRY_SIZE = 48
    SEED = 0xFFFFFFFF

    def __init__(self, app_id, file_path, file_list_path):
        self.app_id = app_id
        self.file_path = file_path
        self.file_list_path = file_list_path
        self._tree = None
        with open(file_path, "rb") as f:
            f.seek(8)
            num_file_entries = struct.unpack("I", f.read(4))[0]
            f.seek(0)
            read_size = self.HEADER_SIZE + self.FILE_ENTRY_SIZE * num_file_entries
            self.parsed = Pak(KaitaiStream(io.BytesIO(f.read(read_size))))

    def get_file(self, file_path):
        file_entry = None
        file_bytes = None
        file_path_hash = mmh3.hash(file_path.encode('utf-16')[2:], self.SEED) & self.SEED

        for fe in self.parsed.file_entries:
            if fe.file_path_hash_case_insensitive == file_path_hash:
                file_entry = fe
                break
        else:
            print("[PakWrapper] WARNING:file path not found:", file_path, file_path_hash)

        # FIXME: proper exception when the path is not found or avoid it (warning in UI)
        with open(self.file_path, "rb") as f:
            f.seek(file_entry.offset)
            if file_entry.flags & 1:
                file_bytes = zlib.decompress(f.read(file_entry.zsize), -15)
            elif file_entry.flags & 2:
                file_bytes = zstd.decompress(f.read(file_entry.zsize))
            else:
                file_bytes = f.read(file_entry.zsize)
        return file_bytes

    @property
    def tree(self):
        if self._tree is not None:
            return self._tree

        pak_filename = os.path.basename(self.file_path)
        root_id = self.app_id + "::" + pak_filename
        tree = Tree(root_id=root_id)
        with open(self.file_list_path) as f:
            for path in f:
                tree.add_node_from_path(path.strip(), path_separator="/")
        self._tree = tree
        return self._tree
