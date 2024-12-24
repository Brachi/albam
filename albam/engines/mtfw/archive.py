import io
import ntpath
import zlib

from kaitaistruct import KaitaiStream

from albam.registry import blender_registry
from . import EXTENSION_TO_FILE_ID, FILE_ID_TO_EXTENSION
from .structs.arc import Arc


@blender_registry.register_archive_loader(app_id="re0", extension="arc")
@blender_registry.register_archive_loader(app_id="re1", extension="arc")
@blender_registry.register_archive_loader(app_id="re5", extension="arc")
@blender_registry.register_archive_loader(app_id="re6", extension="arc")
@blender_registry.register_archive_loader(app_id="rev1", extension="arc")
@blender_registry.register_archive_loader(app_id="rev2", extension="arc")
@blender_registry.register_archive_loader(app_id="dd", extension="arc")
def arc_loader(vfile, context=None):  # XXX context DEPRECATED
    arc = ArcWrapper(file_path=vfile.absolute_path)
    for file_entry in arc.get_file_entries():
        yield file_entry.file_path_with_ext


@blender_registry.register_archive_accessor(app_id="re0", extension="arc")
@blender_registry.register_archive_accessor(app_id="re1", extension="arc")
@blender_registry.register_archive_accessor(app_id="re5", extension="arc")
@blender_registry.register_archive_accessor(app_id="re6", extension="arc")
@blender_registry.register_archive_accessor(app_id="rev1", extension="arc")
@blender_registry.register_archive_accessor(app_id="rev2", extension="arc")
@blender_registry.register_archive_accessor(app_id="dd", extension="arc")
def arc_accessor(vfile, context):
    arc = ArcWrapper(vfile.root_vfile.absolute_path)

    path = vfile.relative_path_windows
    path_no_ext = str(vfile.relative_path_windows_no_ext)
    ext = path.suffix.replace(".", "")

    # TODO: error handling, e.g. when file_path doesn't exist
    try:
        file_type = EXTENSION_TO_FILE_ID[ext]
    except KeyError:
        file_type = int(ext)
    file_bytes = arc.get_file(path_no_ext, file_type)

    return file_bytes


class ArcWrapper:
    PATH_SEPARATOR = "\\"

    def __init__(self, file_path):
        self.file_path = file_path
        self.parsed = Arc.from_file(file_path)
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
            t = (file_entry.file_path, self.get_file(
                file_entry.file_path, file_type))
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
                    print(
                        f"Requested to read out of bounds. Offset: {fe.offset}")
                    raise
        return file_


def update_arc(filepath, vfiles):
    file_ = None
    arc = Arc()
    imported = {}
    exported = {}
    # sort exported
    vf_sorted = []
    vf_mrl = []
    vf_mod = []
    vf_tail = []
    for vf in vfiles:
        if vf.extension == "tex":
            vf_sorted.append(vf)
        elif vf.extension == "mrl":
            vf_mrl.append(vf)
        elif vf.extension == "mod":
            vf_mod.append(vf)
        else:
            vf_tail.append(vf)
    vf_sorted.extend(vf_mrl)
    vf_sorted.extend(vf_mod)
    vf_sorted.extend(vf_tail)

    # build a dictionary for imported arc
    with open(filepath, 'rb') as f:
        parsed = Arc.from_bytes(f.read())
        parsed._read()
    for fe in parsed.file_entries:
        path = fe.file_path
        try:
            extension = FILE_ID_TO_EXTENSION[fe.file_type]
        except KeyError:
            extension = str(fe.file_type)
        relative_path = (path + "." + extension)
        imported[relative_path] = fe

    # patch dictionary with imported files
    for vf in vf_sorted:
        vf_data = vf.data_bytes
        chunk = zlib.compress(vf_data)
        path = ntpath.normpath(vf.relative_path)
        file_path = ntpath.splitext(path)[0]
        try:
            file_type = EXTENSION_TO_FILE_ID[vf.extension]
        except KeyError:
            file_type = int(vf.extension)

        if imported.get(path):
            item = imported.get(path)
            item.zsize = len(chunk)
            item.size = len(vf_data)
            item.raw_data = chunk
            imported[path] = item
        else:
            item = Arc.FileEntry(None, _parent=None, _root=None)
            item.file_path = file_path
            item.file_type = file_type
            item.zsize = len(chunk)
            item.size = len(vf_data)
            item.flags = 2
            item.offset = 0
            item.raw_data = chunk
            exported[path] = item

    exported.update(imported)
    return _serialize_arc(exported)


def find_and_replace_in_arc(filepath, vfile, file_name):
    print("Filepath is ", filepath)
    print("File is ", vfile)
    print("New name  is ", file_name)
    with open(filepath, 'rb') as f:
        parsed = Arc.from_bytes(f.read())
        parsed._read()
    file_entries = {}
    found = False
    for fe in parsed.file_entries:
        path = fe.file_path
        name = ntpath.basename(path)

        try:
            extension = FILE_ID_TO_EXTENSION[fe.file_type]
        except KeyError:
            extension = str(fe.file_type)
        if name == file_name and vfile.extension == extension:
            print("FILE FOUND")
            vf_data = vfile.data_bytes
            chunk = zlib.compress(vf_data)
            fe.zsize = len(chunk)
            fe.size = len(vf_data)
            fe.raw_data = chunk
        file_entries[fe.file_path] = fe
    if not found:
        print("FILE NOT FOUND")
    return _serialize_arc(file_entries)


def _serialize_arc(exported):
    # set header
    arc = Arc()
    header = Arc.ArcHeader(None, arc, arc._root)
    header.ident = b"ARC\00"
    header.version = 7
    header.num_files = len(exported)
    header._check()
    arc.header = header
    file_offset = header.num_files * 80 + -(header.num_files * 80) % 32768

    arc.file_entries = []
    for _, fe in enumerate(exported.values()):
        file_entry = Arc.FileEntry(None, _parent=arc, _root=arc._root)
        file_entry.file_path = fe.file_path
        file_entry.file_type = fe.file_type
        file_entry.zsize = fe.zsize
        file_entry.size = fe.size
        file_entry.flags = 2
        file_entry.offset = file_offset
        file_entry.raw_data = fe.raw_data
        file_entry._check()
        arc.file_entries.append(file_entry)
        file_offset += file_entry.zsize

    arc.padding = bytearray(32760 - (header.num_files * 80) % 32768)
    arc._check()

    stream = KaitaiStream(io.BytesIO(bytearray(file_offset)))
    arc._write(stream)
    file_ = stream.to_byte_array()
    return file_
