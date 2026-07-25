import io
import ntpath
import os
from pathlib import PureWindowsPath, Path
import zlib

from kaitaistruct import KaitaiStream

from ...registry import blender_registry
from . import EXTENSION_TO_FILE_ID, FILE_ID_TO_EXTENSION
from .structs.arc import Arc
from ...blender_ui.tools import show_message_box


@blender_registry.register_archive_loader(app_id="re0", extension="arc")
@blender_registry.register_archive_loader(app_id="re1", extension="arc")
@blender_registry.register_archive_loader(app_id="re5", extension="arc")
@blender_registry.register_archive_loader(app_id="re6", extension="arc")
@blender_registry.register_archive_loader(app_id="rev1", extension="arc")
@blender_registry.register_archive_loader(app_id="rev2", extension="arc")
@blender_registry.register_archive_loader(app_id="dd", extension="arc")
@blender_registry.register_archive_loader(app_id="dmc4", extension="arc")
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
@blender_registry.register_archive_accessor(app_id="dmc4", extension="arc")
def arc_accessor(vfile, context):
    arc = ArcWrapper(vfile.root_vfile.absolute_path)
    arc.app_id = vfile.app_id

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
        self.app_id = None
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
                    if self.app_id == "dmc4":
                        raise RuntimeError("The xcompression algoringm for DMC4 is not implemented yet.")
                    else:
                        file_ = zlib.decompress(fe.raw_data)
                    break
                except EOFError:
                    print(
                        f"Requested to read out of bounds. Offset: {fe.offset}")
                    raise
        return file_

    def unpack(self, out_path):
        arc_path = Path(self.file_path)
        out_path = Path(out_path)

        for fe in self.get_file_entries():
            file_entry_path = PureWindowsPath(fe.file_path_with_ext)
            out_file_path = out_path / arc_path.stem / file_entry_path
            if not out_file_path.parent.exists():
                os.makedirs(str(out_file_path.parent))
            with open(str(out_file_path), "wb") as w:
                data = self.get_file(fe.file_path, fe.file_type)
                w.write(data)


def _sort_arc_entries(entries, vfile=True):
    sorted = []
    mrl = []
    mod = []
    tail = []
    for entry in entries:
        if vfile:
            extension = getattr(entry, "extension")
        else:
            extension = FILE_ID_TO_EXTENSION.get(entry.file_type, entry.file_type)

        if extension == "tex":
            sorted.append(entry)
        elif extension == "mrl":
            mrl.append(entry)
        elif extension == "mod":
            mod.append(entry)
        else:
            tail.append(entry)

    sorted.extend(mrl)
    sorted.extend(mod)
    sorted.extend(tail)
    return sorted


def _get_file_entry(vfile):
    vf_data = vfile.data_bytes
    chunk = zlib.compress(vf_data)
    path = ntpath.normpath(vfile.relative_path)
    file_path = ntpath.splitext(path)[0]
    try:
        file_type = EXTENSION_TO_FILE_ID[vfile.extension]
    except KeyError:
        file_type = int(vfile.extension)
    item = Arc.FileEntry(None, _parent=None, _root=None)
    item.file_path = file_path
    item.file_type = file_type
    item.zsize = len(chunk)
    item.size = len(vf_data)
    item.flags = 2
    item.offset = 0
    item.raw_data = chunk
    return item


def _serialize_arc(exported):
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


def _to_dict(file_entries):
    imported = {}
    for fe in file_entries:
        path = fe.file_path
        try:
            extension = FILE_ID_TO_EXTENSION[fe.file_type]
        except KeyError:
            extension = str(fe.file_type)
        relative_path = (path + "." + extension)
        imported[relative_path] = fe
    return imported


TEXTURE_EXTENSIONS = ("tex", "rtex")


def _file_entry_extension(file_entry):
    try:
        return FILE_ID_TO_EXTENSION[file_entry.file_type]
    except KeyError:
        return str(file_entry.file_type)


def _normalize_texture_key(path):
    return path.replace("/", "\\").strip("\\").lower()


def _texture_paths_from_mod(mod_bytes, app_id):
    from .structs.mod_153 import Mod153
    from .structs.mod_156 import Mod156
    from .structs.mod_21 import Mod21

    mod_cls = {"re5": Mod156, "dmc4": Mod153}.get(app_id, Mod21)
    try:
        mod = mod_cls.from_bytes(mod_bytes)
        mod._read()
    except Exception:
        return None
    materials_data = getattr(mod, "materials_data", None)
    textures = getattr(materials_data, "textures", None)
    if not textures:
        return set()
    return {_normalize_texture_key(t) for t in textures if t}


def _texture_paths_from_mrl(mrl_bytes, app_id):
    from kaitaistruct import BytesIO, KaitaiStream
    from .structs.mrl import Mrl
    try:
        mrl = Mrl(app_id, KaitaiStream(BytesIO(mrl_bytes)))
        mrl._read()
    except Exception:
        return None
    return {_normalize_texture_key(t.texture_path) for t in mrl.textures if t.texture_path}


def _get_texture_paths_from_arc_entry(fe, app_id):
    ext = _file_entry_extension(fe)
    try:
        data = zlib.decompress(fe.raw_data)
    except Exception:
        return None
    if ext == "mod":
        return _texture_paths_from_mod(data, app_id)
    elif ext == "mrl":
        return _texture_paths_from_mrl(data, app_id)
    return None


def _find_orphaned_textures(file_entries, app_id, old_texture_paths, new_texture_paths):
    """
    Only considers textures that the exported model USED TO reference but
    NO LONGER does. Checks if any OTHER model in the arc still uses them.
    Safe for cross-arc shared textures.
    """
    candidates = old_texture_paths - new_texture_paths
    if not candidates:
        return file_entries, []

    for fe in file_entries.values():
        ext = _file_entry_extension(fe)
        if ext not in ("mod", "mrl"):
            continue
        paths = _get_texture_paths_from_arc_entry(fe, app_id)
        if paths is None:
            return file_entries, []  # can't parse → abort for safety
        candidates -= paths
        if not candidates:
            return file_entries, []

    cleaned = {}
    removed = []
    for path_with_ext, fe in file_entries.items():
        if _file_entry_extension(fe) in TEXTURE_EXTENSIONS:
            if _normalize_texture_key(fe.file_path) in candidates:
                removed.append(path_with_ext)
                continue
        cleaned[path_with_ext] = fe
    return cleaned, removed


def update_arc(filepath, vfiles, remove_unused_textures=False):
    imported = {}
    exported = {}
    vf_sorted = _sort_arc_entries(vfiles)

    with open(filepath, 'rb') as f:
        parsed = Arc.from_bytes(f.read())
        parsed._read()

    imported = _to_dict(parsed.file_entries)

    app_id = vf_sorted[0].app_id if vf_sorted else None
    old_texture_paths = set()
    new_texture_paths = set()

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

        if vf.extension in TEXTURE_EXTENSIONS:
            new_texture_paths.add(_normalize_texture_key(file_path))

        # Collect old texture refs before overwriting
        if remove_unused_textures and vf.extension in ("mod", "mrl"):
            old_entry = imported.get(path)
            if old_entry:
                old_paths = _get_texture_paths_from_arc_entry(old_entry, app_id)
                if old_paths is not None:
                    old_texture_paths |= old_paths
            if vf.extension == "mod":
                new_paths = _texture_paths_from_mod(vf_data, app_id)
            else:
                new_paths = _texture_paths_from_mrl(vf_data, app_id)
            if new_paths is not None:
                new_texture_paths |= new_paths

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

    if remove_unused_textures and app_id and old_texture_paths:
        exported, removed = _find_orphaned_textures(
            exported, app_id, old_texture_paths, new_texture_paths)
        if removed:
            preview = ", ".join(ntpath.basename(p) for p in removed[:8])
            if len(removed) > 8:
                preview += ", ..."
            show_message_box(
                f"Removed {len(removed)} orphaned texture(s): {preview}")

    return _serialize_arc(exported)


def find_and_replace_in_arc(filepath, vfile, file_name, add_new):
    file_entries = {}
    imported_entries = []
    found = False

    with open(filepath, 'rb') as f:
        parsed = Arc.from_bytes(f.read())
        parsed._read()

    imported_entries = [fe for fe in parsed.file_entries]
    if add_new:
        file_entry = _get_file_entry(vfile)
        imported_entries.append(file_entry)
        imported_entries = _sort_arc_entries(imported_entries, False)
        file_entries = _to_dict(imported_entries)
    else:
        for fe in imported_entries:
            path = fe.file_path
            name = ntpath.basename(path)
            try:
                extension = FILE_ID_TO_EXTENSION[fe.file_type]
            except KeyError:
                extension = str(fe.file_type)
            if name == file_name and vfile.extension == extension:
                show_message_box("File: {} was found and replaced in the archive".format(file_name))
                found = True
                vf_data = vfile.data_bytes
                chunk = zlib.compress(vf_data)
                fe.zsize = len(chunk)
                fe.size = len(vf_data)
                fe.raw_data = chunk
            file_entries[(fe.file_path + "." + extension)] = fe
        assert len(file_entries) == len(parsed.file_entries), "File entries size mismatch"
        if not found:
            show_message_box("File: {} was not found in the archive".format(file_name))
            return None
    assert len(parsed.file_entries) <= len(file_entries) <= len(parsed.file_entries) + 1
    return _serialize_arc(file_entries)
