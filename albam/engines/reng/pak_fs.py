"""
PyFilesystem2 adapter for RE Engine .pak archives.

Unlike MT Framework's .arc (paths stored plaintext in the header - see
../mtfw/arc_fs.py), a .pak's file entries carry only murmurhash3 hashes of
their virtual path (see structs/pak.ksy) - there is no way to enumerate a
pak's contents from the file alone. `PakFS` is built from a .pak plus an
external plaintext list of *candidate* paths (one per line, forward-slash,
no leading "/") - typically a community-maintained file list for the game.
Each candidate is hashed and kept only if it matches an actual entry in this
specific pak, so paths absent from this pak never show up as browsable
(unlike the old PakWrapper-based archive_loader it replaces, which listed
every candidate from the list unconditionally, regardless of whether this
particular pak actually contained it).

A real .pak can be tens of GB; __init__ only ever reads the header + the
fixed-size file-entry table (like the old PakWrapper did), and openbin()
seeks straight to one entry's offset - the file's bulk data is never read
except for the single entry being opened.
"""
import io
import struct
import zlib

import pymmh3 as mmh3
import zstd
from fs.base import FS
from fs.enums import ResourceType
from fs.errors import ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.memoryfs import MemoryFS
from fs.path import dirname
from kaitaistruct import KaitaiStream

from .structs.pak import Pak

HEADER_SIZE = 16
NUM_FILES_OFFSET = 8
FILE_ENTRY_SIZE = 48
HASH_SEED = 0xFFFFFFFF


def _local_opener(path):
    return open(path, "rb")


def _hash_path(path):
    # Matches the previous PakWrapper.get_file's exact computation - not
    # independently verified against RE Engine's own hashing beyond that.
    return mmh3.hash(path.encode("utf-16")[2:], HASH_SEED) & HASH_SEED


class PakFS(FS):
    """Read-only PyFilesystem2 view of a single RE Engine .pak file.

    `path_list_path` is required - a plaintext file of candidate virtual
    paths, since a .pak's own file entries carry only hashes (see module
    docstring).
    """

    _meta = {
        "case_insensitive": False,  # TODO: paths are effectively case-insensitive
        "network": False,
        "read_only": True,
        "supports_rename": False,
        "thread_safe": True,
        "unicode_paths": True,
        "virtual": False,
    }

    def __init__(self, pak_path, path_list_path, opener=None):
        super().__init__()
        self.pak_path = str(pak_path)
        self.path_list_path = str(path_list_path)
        self._opener = opener or _local_opener

        f = self._opener(self.pak_path)
        try:
            f.seek(NUM_FILES_OFFSET)
            num_file_entries = struct.unpack("I", f.read(4))[0]
            f.seek(0)
            read_size = HEADER_SIZE + FILE_ENTRY_SIZE * num_file_entries
            parsed = Pak(KaitaiStream(io.BytesIO(f.read(read_size))))
        finally:
            f.close()

        entries_by_hash = {fe.file_path_hash_case_insensitive: fe for fe in parsed.file_entries}

        self._entries = {}
        self._directory = MemoryFS()
        with open(self.path_list_path) as list_file:
            for line in list_file:
                candidate = line.strip()
                if not candidate:
                    continue
                file_entry = entries_by_hash.get(_hash_path(candidate))
                if file_entry is None:
                    continue
                path = "/" + candidate.replace("\\", "/").lstrip("/")
                if path in self._entries:
                    continue
                self._entries[path] = file_entry
                self._directory.makedirs(dirname(path), recreate=True)
                self._directory.create(path)

    def __repr__(self):
        return f"PakFS({self.pak_path!r})"

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        basic_info = self._directory.getinfo(_path)
        raw_info = {"basic": {"name": basic_info.name, "is_dir": basic_info.is_dir}}

        if "details" in namespaces:
            file_entry = self._entries.get(_path)
            resource_type = ResourceType.directory if basic_info.is_dir else ResourceType.file
            raw_info["details"] = {
                "type": int(resource_type),
                "size": file_entry.size if file_entry else 0,
            }
        return Info(raw_info)

    def listdir(self, path):
        self.check()
        return self._directory.listdir(path)

    def openbin(self, path, mode="r", buffering=-1, **options):
        self.check()
        if "w" in mode or "+" in mode or "a" in mode:
            raise ResourceReadOnly(path)

        _path = self.validatepath(path)
        file_entry = self._entries.get(_path)
        if file_entry is None:
            raise ResourceNotFound(path)

        f = self._opener(self.pak_path)
        try:
            f.seek(file_entry.offset)
            raw = f.read(file_entry.zsize)
        finally:
            f.close()

        if file_entry.flags & 1:
            data = zlib.decompress(raw, -15)
        elif file_entry.flags & 2:
            data = zstd.decompress(raw)
        else:
            data = raw
        return io.BytesIO(data)

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)
