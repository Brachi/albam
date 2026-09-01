"""
PyFilesystem2 adapter for Capcom Internal Engine (RE4 UHD) .lfs archives.

An .lfs is an LZX ("xcompress") stream split into fixed-size chunks (see
structs/lfs.ksy): the header records each chunk's compressed and
decompressed size, but nothing about what the decompressed bytes contain.
The file table - when there is one at all - lives *inside* that stream, so
unlike ArcFS or PakFS, whose entries can be listed straight out of a cheap
header read, listing an .lfs means decompressing the whole thing first
(seconds per archive with the pure-Python decompressor in
lfs_decompress.py). `LfsFS` therefore does that once in __init__ and keeps
the resulting bytes for the life of the instance; close() drops them.

That cost is also why there is no whole-game-root loader here, the way
albam.engines.mtfw.arc_fs.MTFW_FS and albam.engines.hexn.fs.HexnFS both
have one: a real RE4 UHD install ships ~4500 .lfs archives, and mounting
the game folder would have to decompress every one of them up front just
to know what is inside. Archives are mounted one at a time instead ("Add
Files" in the VFS panel - see archive.py).

What the decompressed stream holds is decided by the extension the archive
name carries *before* ".lfs" - "r20d.udas.lfs" is a UDAS, "icon_u.tpl.lfs"
is a TPL:

- udas / dat / pack (including the "*.pack.yz2.lfs" texture packs, which
  are plain packs despite the extra segment) are containers of their own.
  Their entries carry no names, only an index and - for udas/dat - a
  4-character extension, so each is exposed as "<stem>_NNN.<ext>", keeping
  the numbering the container itself uses. Nothing else identifies a texture
  inside a pack: a .tpl refers to one by its index (see textures.py).
- evd entries do carry names, nested paths included ("event/r332/s20/cam/
  cam_s20_000.fcv"), and are exposed under them.
- every other extension (bin, rel, tpl, fix, fnt, esl, fcv, tga, eff, uwf)
  is a single file compressed on its own, exposed as "<stem>.<ext>".
"""
import io
import os
from collections import defaultdict

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, ResourceNotFound, ResourceReadOnly
from fs.info import Info

from . import lfs_decompress
from .structs.dat import Dat
from .structs.evd import Evd
from .structs.lfs import Lfs
from .structs.pack import Pack
from .structs.udas import Udas

# Container extensions, mapped to the struct parsing that container's own
# decompressed bytes. Anything not listed here is a single file compressed
# on its own (see this module's docstring).
CONTAINER_STRUCTS = {
    ".udas": Udas,
    ".dat": Dat,
    ".pack": Pack,
    ".evd": Evd,
}


def split_archive_name(file_name):
    """(stem, payload extension) for an .lfs archive's file name - the
    extension being the one right after the stem, which is what decides how
    the decompressed bytes are read: "0d104000.pack.yz2.lfs" ->
    ("0d104000", ".pack"), "r20d.udas.lfs" -> ("r20d", ".udas").

    Raises ValueError for a name carrying no extension before ".lfs", which
    leaves nothing to say what the archive holds.
    """
    extensions = []
    stem = file_name
    while True:
        stem, extension = os.path.splitext(stem)
        if not extension:
            break
        extensions.insert(0, extension)
    if len(extensions) < 2:
        raise ValueError(
            f"{file_name!r} carries no extension before '.lfs', so there is no way to "
            f"tell what it holds"
        )
    return stem, extensions[0]


class LfsFS(FS):
    """Read-only PyFilesystem2 view of a single RE4 UHD .lfs archive.

    __init__ decompresses the whole archive and slices every file out of it
    (see this module's docstring for why it can't be deferred or made
    partial), so constructing one is seconds of work and holds the archive's
    decompressed size until close().
    """

    _meta = {
        "case_insensitive": False,
        "network": False,
        "read_only": True,
        "supports_rename": False,
        "thread_safe": True,
        "unicode_paths": True,
        "virtual": False,
    }

    def __init__(self, lfs_path):
        super().__init__()
        self.lfs_path = str(lfs_path)

        file_name = os.path.basename(self.lfs_path)
        try:
            self._stem, self.payload_extension = split_archive_name(file_name)
        except ValueError as error:
            raise CreateFailed(str(error))

        lfs = Lfs.from_file(self.lfs_path)
        lfs._read()
        decompressed = bytes(lfs_decompress.xcompress_decompress_re4hd(lfs.file_entries))

        # Set when an archive named after a container extension turns out not
        # to hold one after all - see _split().
        self.container_error = None
        # path -> bytes, in the order the archive itself lists them, which is
        # the order the "<stem>_NNN" numbering follows.
        self._data = self._split(decompressed)
        # Only evd entries are ever nested (see this module's docstring), but
        # the directory bookkeeping is built the same way for every archive so
        # walk()/scandir() work uniformly. Built directly rather than via
        # fs.memoryfs.MemoryFS, same as albam.engines.hexn.fs.SsgFS.
        self._dir_children = defaultdict(list)
        self._known_dirs = {"/"}
        for path in self._data:
            parts = path.strip("/").split("/")
            for i, part in enumerate(parts):
                parent = "/" + "/".join(parts[:i])
                if part not in self._dir_children[parent]:
                    self._dir_children[parent].append(part)
                if i < len(parts) - 1:
                    self._known_dirs.add(parent.rstrip("/") + "/" + part)

    def _split(self, decompressed):
        struct_cls = CONTAINER_STRUCTS.get(self.payload_extension)
        single_file = {f"/{self._stem}{self.payload_extension}": decompressed}
        if struct_cls is None:
            return single_file

        # The extension only says what the archive is *named*, and a real
        # install has files it's wrong about - "SizeTbl.dat.lfs" is a plain
        # table, not a .dat container, and reads as one claiming ten million
        # files. Falling back to the whole payload as a single file keeps such
        # an archive mountable and readable (which is all the VFS needs of it)
        # instead of failing to mount at all. The entry reads are inside the
        # same guard because they're lazy: a container whose header parses can
        # still turn out not to be one when an entry's own offset/size is read.
        try:
            container = struct_cls.from_bytes(decompressed)
            container._read()
            return self._split_container(struct_cls, container, decompressed)
        except Exception as error:
            self.container_error = error
            return single_file

    def _split_container(self, struct_cls, container, decompressed):
        if struct_cls is Evd:
            return self._split_evd(container, decompressed)
        if struct_cls is Udas:
            entries = container.header.data_blocks.file_entries
            extensions = container.header.data_blocks.file_extension
        elif struct_cls is Dat:
            entries = container.header.file_entries
            extensions = container.header.file_extension
        else:
            entries = container.file_entries
            extensions = None

        data = {}
        for i, entry in enumerate(entries):
            if extensions is not None:
                # A blank extension is a real entry the container doesn't name
                # a format for - keep it listed rather than dropping it, under
                # a name no import function is registered for.
                extension = extensions[i].ext.lower() or "null"
                raw_data = entry.raw_data
            else:
                extension = "dds" if entry.data.is_dds else "tga"
                raw_data = entry.data.raw_data
            data[f"/{self._stem}_{i:03d}.{extension}"] = raw_data
        return data

    def _split_evd(self, container, decompressed):
        """An .evd entry's content runs from its own offset to whichever
        entry's offset comes next, in ascending-offset order - the file table
        itself is not sorted by offset (it groups shared model files before
        the scene's own), so table order can't be used, and the entry's `size`
        field doesn't measure the span either (see structs/evd.ksy).

        Verified against every .evd in a real install: sliced this way, each
        entry's bytes start with the magic its extension calls for and every
        .bin/.tpl parses through to the end of the slice, while `size` leaves
        every model .bin short of its own vertex data.
        """
        by_offset = sorted(container.file_entries, key=lambda entry: entry.offset)
        data = {}
        for i, entry in enumerate(by_offset):
            end = by_offset[i + 1].offset if i + 1 < len(by_offset) else len(decompressed)
            name = "/" + entry.name_file.replace("\\", "/").lstrip("/")
            data[name] = decompressed[entry.offset:end]
        return data

    def close(self):
        """Drop the decompressed archive along with the usual fs.base.FS
        teardown, so a caller done with an archive isn't holding its
        uncompressed bytes."""
        self._data = {}
        self._dir_children = defaultdict(list)
        self._known_dirs = {"/"}
        super().close()

    def __repr__(self):
        return f"LfsFS({self.lfs_path!r})"

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        is_dir = _path == "/" or _path in self._known_dirs
        if not is_dir and _path not in self._data:
            raise ResourceNotFound(path)
        name = _path.rsplit("/", 1)[-1] or "/"
        raw_info = {"basic": {"name": name, "is_dir": is_dir}}

        if "details" in namespaces:
            resource_type = ResourceType.directory if is_dir else ResourceType.file
            raw_info["details"] = {
                "type": int(resource_type),
                "size": 0 if is_dir else len(self._data[_path]),
            }
        return Info(raw_info)

    def listdir(self, path):
        self.check()
        _path = self.validatepath(path)
        if _path not in self._known_dirs:
            raise ResourceNotFound(path)
        # Insertion order, not sorted: it's the order the container lists its
        # own entries in, which is what the "<stem>_NNN" numbering follows.
        return list(self._dir_children.get(_path, ()))

    def openbin(self, path, mode="r", buffering=-1, **options):
        self.check()
        if "w" in mode or "+" in mode or "a" in mode:
            raise ResourceReadOnly(path)

        _path = self.validatepath(path)
        if _path not in self._data:
            raise ResourceNotFound(path)
        return io.BytesIO(self._data[_path])

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)
