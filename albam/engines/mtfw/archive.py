import io
import ntpath

from kaitaistruct import KaitaiStream

from ...registry import blender_registry
from ...lib.kaitai_utils import check_recursive, parse
from .arc_fs import (
    ArcFS,
    MTFW_FS,
    compress_entry,
    decompress_entry,
    file_type_extensions,
    new_entry_file_type,
)
from .structs.arc import Arc
from ...blender_ui.tools import show_message_box


@blender_registry.register_fs_root_loader(app_id="re0", extension="arc")
@blender_registry.register_fs_root_loader(app_id="re1", extension="arc")
@blender_registry.register_fs_root_loader(app_id="re5", extension="arc")
@blender_registry.register_fs_root_loader(app_id="re6", extension="arc")
@blender_registry.register_fs_root_loader(app_id="rev1", extension="arc")
@blender_registry.register_fs_root_loader(app_id="rev2", extension="arc")
@blender_registry.register_fs_root_loader(app_id="dd", extension="arc")
@blender_registry.register_fs_root_loader(app_id="dmc4", extension="arc")
@blender_registry.register_fs_root_loader(app_id="umvc3", extension="arc")
def arc_fs_root_loader(absolute_path):
    return ArcFS(absolute_path)


@blender_registry.register_fs_root_loader(app_id="re0", extension=None)
@blender_registry.register_fs_root_loader(app_id="re1", extension=None)
@blender_registry.register_fs_root_loader(app_id="re5", extension=None)
@blender_registry.register_fs_root_loader(app_id="re6", extension=None)
@blender_registry.register_fs_root_loader(app_id="rev1", extension=None)
@blender_registry.register_fs_root_loader(app_id="rev2", extension=None)
@blender_registry.register_fs_root_loader(app_id="dd", extension=None)
@blender_registry.register_fs_root_loader(app_id="dmc4", extension=None)
@blender_registry.register_fs_root_loader(app_id="umvc3", extension=None)
def game_fs_root_loader(absolute_path):
    return MTFW_FS(absolute_path)


def _sort_arc_entries(entries, arc_version=None):
    """`entries` in the order an archive lists them: textures, then mrl, mod,
    then everything else.

    `arc_version` says what `entries` are: None for vfiles, which name their
    own extension, and an archive's version for file entries, whose type ids
    only mean anything against the table that version numbers them with.
    """
    sorted = []
    mrl = []
    mod = []
    tail = []
    for entry in entries:
        if arc_version is None:
            extension = getattr(entry, "extension")
        else:
            extension = _file_entry_extension(entry, arc_version)

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


def _get_file_entry(vfile, arc_version):
    vf_data = vfile.get_bytes()
    path = ntpath.normpath(vfile.relative_path)
    chunk = compress_entry(arc_version, vf_data, path)
    file_path = ntpath.splitext(path)[0]
    try:
        file_type = new_entry_file_type(arc_version, vfile.extension)
    except KeyError:
        file_type = int(vfile.extension)
    item = Arc.FileEntry(None, _parent=None, _root=None)
    item.file_path = file_path
    item.file_type = file_type
    item.zsize = len(chunk)
    item.size = len(vf_data)
    # Unverified for DMC4, whose own textures are observed carrying 0 and 1
    # as well; there is nothing to carry over for an entry the archive does
    # not already have. See the comment in _serialize_arc.
    item.flags = 2
    item.offset = 0
    item.raw_data = chunk
    return item


def _serialize_arc(exported, version=7):
    arc = Arc()
    header = Arc.ArcHeader(None, arc, arc._root)
    header.ident = b"ARC\00"
    header.version = version
    header.num_files = len(exported)
    arc.header = header
    file_offset = header.num_files * 80 + -(header.num_files * 80) % 32768

    arc.file_entries = []
    for _, fe in enumerate(exported.values()):
        file_entry = Arc.FileEntry(None, _parent=arc, _root=arc._root)
        file_entry.file_path = fe.file_path
        file_entry.file_type = fe.file_type
        file_entry.zsize = fe.zsize
        file_entry.size = fe.size
        # Carried over rather than fixed at 2. Measured over every .arc of
        # the seven version 7 games on hand (Dragon's Dogma, Resident Evil
        # Revelations, Resident Evil 0, Resident Evil 5, Resident Evil 6,
        # Resident Evil HD Remaster, Ultimate Marvel vs. Capcom 3): 29690
        # archives, 788014 entries, 788013 of them carrying 2 and exactly one
        # carrying 4 - "dlc\model\chara\wp\wp1070\wp1070" in Revelations'
        # wp21.arc. That one entry is why carrying the parsed value through is
        # the fix and writing a fixed 2 was the bug: its own value now
        # survives a repack instead of being replaced by a guess. DMC4 makes
        # the same point louder, using 0 and 1 as well - only ever on a tex,
        # so it says something about the texture the engine is being handed.
        file_entry.flags = fe.flags
        file_entry.offset = file_offset
        file_entry.raw_data = fe.raw_data
        arc.file_entries.append(file_entry)
        file_offset += file_entry.zsize

    arc.padding = bytearray(32760 - (header.num_files * 80) % 32768)
    check_recursive(arc)

    stream = KaitaiStream(io.BytesIO(bytearray(file_offset)))
    arc._write(stream)
    file_ = stream.to_byte_array()
    return file_


def _to_dict(file_entries, arc_version):
    imported = {}
    for fe in file_entries:
        path = fe.file_path
        relative_path = (path + "." + _file_entry_extension(fe, arc_version))
        imported[relative_path] = fe
    return imported


TEXTURE_EXTENSIONS = ("tex", "rtex")


def _file_entry_extension(file_entry, arc_version):
    """The extension an entry's file type id stands for in its own archive.

    Which table that is depends on the archive's version: the two number the
    same resource class names from different hashes, so a DMC4 id read
    through the shared table is not a miss, it is a wrong answer.
    """
    try:
        return file_type_extensions(arc_version)[file_entry.file_type]
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
        mod = parse(mod_cls, mod_bytes, app_id)
    except Exception:
        return None
    materials_data = getattr(mod, "materials_data", None)
    textures = getattr(materials_data, "textures", None)
    if not textures:
        return set()
    return {_normalize_texture_key(t) for t in textures if t}


def _texture_paths_from_mrl(mrl_bytes, app_id):
    from .structs.mrl import Mrl
    try:
        mrl = parse(Mrl, mrl_bytes, app_id)
    except Exception:
        return None
    return {_normalize_texture_key(t.texture_path) for t in mrl.textures if t.texture_path}


def _get_texture_paths_from_arc_entry(fe, app_id, arc_version):
    ext = _file_entry_extension(fe, arc_version)
    try:
        data = decompress_entry(arc_version, fe.raw_data, fe.size)
    except Exception:
        return None
    if ext == "mod":
        return _texture_paths_from_mod(data, app_id)
    elif ext == "mrl":
        return _texture_paths_from_mrl(data, app_id)
    return None


def _find_orphaned_textures(file_entries, app_id, old_texture_paths, new_texture_paths,
                            arc_version):
    """
    Only considers textures that the exported model USED TO reference but
    NO LONGER does. Checks if any OTHER model in the arc still uses them.
    Safe for cross-arc shared textures.
    """
    candidates = old_texture_paths - new_texture_paths
    if not candidates:
        return file_entries, []

    for fe in file_entries.values():
        ext = _file_entry_extension(fe, arc_version)
        if ext not in ("mod", "mrl"):
            continue
        paths = _get_texture_paths_from_arc_entry(fe, app_id, arc_version)
        if paths is None:
            return file_entries, []  # can't parse → abort for safety
        candidates -= paths
        if not candidates:
            return file_entries, []

    cleaned = {}
    removed = []
    for path_with_ext, fe in file_entries.items():
        if _file_entry_extension(fe, arc_version) in TEXTURE_EXTENSIONS:
            if _normalize_texture_key(fe.file_path) in candidates:
                removed.append(path_with_ext)
                continue
        cleaned[path_with_ext] = fe
    return cleaned, removed


@blender_registry.register_archive_writer(app_id="re0", extension="arc")
@blender_registry.register_archive_writer(app_id="re1", extension="arc")
@blender_registry.register_archive_writer(app_id="re5", extension="arc")
@blender_registry.register_archive_writer(app_id="re6", extension="arc")
@blender_registry.register_archive_writer(app_id="rev1", extension="arc")
@blender_registry.register_archive_writer(app_id="rev2", extension="arc")
@blender_registry.register_archive_writer(app_id="dd", extension="arc")
@blender_registry.register_archive_writer(app_id="dmc4", extension="arc")
@blender_registry.register_archive_writer(app_id="umvc3", extension="arc")
def update_arc(filepath, vfiles, remove_unused_textures=False, **_options):
    imported = {}
    exported = {}
    vf_sorted = _sort_arc_entries(vfiles)

    with open(filepath, 'rb') as f:
        parsed = Arc.from_bytes(f.read())
        parsed._read()
    arc_version = parsed.header.version

    imported = _to_dict(parsed.file_entries, arc_version)

    app_id = vf_sorted[0].app_id if vf_sorted else None
    old_texture_paths = set()
    new_texture_paths = set()

    # patch dictionary with imported files
    for vf in vf_sorted:
        vf_data = vf.get_bytes()
        path = ntpath.normpath(vf.relative_path)
        chunk = compress_entry(arc_version, vf_data, path)
        file_path = ntpath.splitext(path)[0]

        if vf.extension in TEXTURE_EXTENSIONS:
            new_texture_paths.add(_normalize_texture_key(file_path))

        # Collect old texture refs before overwriting
        if remove_unused_textures and vf.extension in ("mod", "mrl"):
            old_entry = imported.get(path)
            if old_entry:
                old_paths = _get_texture_paths_from_arc_entry(old_entry, app_id, arc_version)
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
            try:
                file_type = new_entry_file_type(arc_version, vf.extension)
            except KeyError:
                file_type = int(vf.extension)
            item = Arc.FileEntry(None, _parent=None, _root=None)
            item.file_path = file_path
            item.file_type = file_type
            item.zsize = len(chunk)
            item.size = len(vf_data)
            # Unverified for DMC4, whose own textures are observed carrying
            # 0 and 1 as well; there is nothing to carry over for an entry
            # the archive does not already have. See _serialize_arc.
            item.flags = 2
            item.offset = 0
            item.raw_data = chunk
            exported[path] = item

    exported.update(imported)

    if remove_unused_textures and app_id and old_texture_paths:
        exported, removed = _find_orphaned_textures(
            exported, app_id, old_texture_paths, new_texture_paths, arc_version)
        if removed:
            preview = ", ".join(ntpath.basename(p) for p in removed[:8])
            if len(removed) > 8:
                preview += ", ..."
            show_message_box(
                f"Removed {len(removed)} orphaned texture(s): {preview}")

    return _serialize_arc(exported, arc_version)


def find_and_replace_in_arc(filepath, vfile, file_name, add_new):
    file_entries = {}
    imported_entries = []
    found = False

    with open(filepath, 'rb') as f:
        parsed = Arc.from_bytes(f.read())
        parsed._read()
    arc_version = parsed.header.version

    imported_entries = [fe for fe in parsed.file_entries]
    if add_new:
        file_entry = _get_file_entry(vfile, arc_version)
        imported_entries.append(file_entry)
        imported_entries = _sort_arc_entries(imported_entries, arc_version)
        file_entries = _to_dict(imported_entries, arc_version)
    else:
        for fe in imported_entries:
            path = fe.file_path
            name = ntpath.basename(path)
            extension = _file_entry_extension(fe, arc_version)
            if name == file_name and vfile.extension == extension:
                show_message_box("File: {} was found and replaced in the archive".format(file_name))
                found = True
                vf_data = vfile.get_bytes()
                chunk = compress_entry(arc_version, vf_data, path + "." + extension)
                fe.zsize = len(chunk)
                fe.size = len(vf_data)
                fe.raw_data = chunk
            file_entries[(fe.file_path + "." + extension)] = fe
        assert len(file_entries) == len(parsed.file_entries), "File entries size mismatch"
        if not found:
            show_message_box("File: {} was not found in the archive".format(file_name))
            return None
    assert len(parsed.file_entries) <= len(file_entries) <= len(parsed.file_entries) + 1
    return _serialize_arc(file_entries, arc_version)
