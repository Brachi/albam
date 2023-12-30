import os
import zlib
import io
from kaitaistruct import KaitaiStream

from albam.registry import blender_registry
from . import EXTENSION_TO_FILE_ID, FILE_ID_TO_EXTENSION
from .structs.arc import Arc


@blender_registry.register_archive_loader(app_id="re1", extension="arc")
@blender_registry.register_archive_loader(app_id="re5", extension="arc")
@blender_registry.register_archive_loader(app_id="rev2", extension="arc")
def arc_loader(vfile, context=None):  # XXX context DEPRECATED
    arc = ArcWrapper(file_path=vfile.absolute_path)
    for file_entry in arc.get_file_entries():
        yield file_entry.file_path_with_ext


@blender_registry.register_archive_accessor(app_id="re1", extension="arc")
@blender_registry.register_archive_accessor(app_id="re5", extension="arc")
@blender_registry.register_archive_accessor(app_id="rev2", extension="arc")
def arc_accessor(file_item, context):
    app_id = file_item.app_id
    vfs = file_item.get_vfs()
    item_list = vfs.file_list
    root = item_list[file_item.tree_node.root_id]

    # TODO: error handling, e.g. when file_path doesn't exist
    arc = ArcWrapper(root.file_path)
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

    def __init__(self, file_path):
        self.file_path = file_path
        #self.parsed = Arc.from_file(file_path)
        #with KaitaiStream(open(file_path, 'rb')) as _io:
        #    self.parsed = Arc(_io)
        #    self.parsed._read()
        with open(file_path, 'rb') as f:
            self.parsed  = Arc.from_bytes(f.read())
            self.parsed._read()

    def get_file_entries_by_type(self, file_type):
        filtered = []
        for fe in self.parsed.file_entries:
            if fe.file_type == file_type:
                filtered.append(fe)
        return filtered

    def get_file_entries_by_extension(self, extension):
        try:
            file_type = EXTENSION_TO_FILE_ID[extension]
        except KeyError:
            raise RuntimeError(f"Extension {extension} unknown")
        return self.get_file_entries_by_type(file_type)

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


def serialize_arc(filepath, files):
    '''Curently hardcoded'''
    arc = Arc()
    # set header
    header = Arc.ArcHeader(None, arc, arc._root)
    header.ident = b"ARC\00"
    header.version = 7
    header.num_files = len(files)
    header._check
    arc.header = header
    arc.file_entries = []

    file_offset = 32768
    data_size = 0

    #set file entry
    for f in files:
        chunk = zlib.compress(f.get_bytes())
        file_entry = Arc.FileEntry(None, _parent=arc, _root=arc._root)
        path = os.path.normpath(f.relative_path)
        file_entry.file_path = os.path.splitext (path)[0]
        file_entry.file_type =  EXTENSION_TO_FILE_ID[f.extension]
        file_entry.zsize = len(chunk)
        file_entry.size = len(f.get_bytes())
        file_entry.flags = 2
        file_entry.offset = file_offset
        file_entry.raw_data = chunk
        file_entry._check
        arc.file_entries.append(file_entry)
        file_offset += file_entry.zsize
        data_size += file_entry.zsize

    arc.padding = bytearray(32760 - header.num_files * 80)
    arc._check

    stream = KaitaiStream(io.BytesIO(bytearray(32768 + data_size)))
    arc._write(stream)
    output = stream.to_byte_array()

    #write
    with open(filepath, "wb") as f:
        f.write(output)