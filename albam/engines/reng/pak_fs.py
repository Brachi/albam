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
import os
import re
import struct
import zlib

import pymmh3 as mmh3
import zstd
from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.memoryfs import MemoryFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.path import dirname
from kaitaistruct import KaitaiStream

from .structs.pak import Pak
from ...lib.s3 import build_s3_client, s3_opener

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

    @classmethod
    def from_s3(
        cls,
        bucket,
        key,
        path_list_path,
        *,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        endpoint_url=None,
        region_name="auto",
    ):
        """Alternate constructor: source the .pak from an S3-compatible
        bucket (R2 works as-is, just pass R2's account-specific
        endpoint_url and an R2 API token as access key/secret) instead of a
        local file. `key` is the .pak's own key in the bucket (e.g.
        "re3/re_chunk_000.pak") - unlike MTFW_FS.from_s3, there's only ever
        one file here, so no key discovery/listing is needed, just the
        exact key.

        `path_list_path` still always reads from a real local file - it's a
        small (few-MB) plaintext community path list, not worth fetching
        over the network the way the (possibly tens-of-GB) .pak itself is.

        Reads are real HTTP Range requests (via smart_open, see
        albam.lib.s3.s3_opener) - constructing this and reading individual
        files never downloads the whole .pak. __init__ already only reads
        the header + fixed-size file-entry table regardless of source; over
        S3 that's one small bounded GET, not the whole file.
        """
        client = build_s3_client(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )
        opener = s3_opener(client, bucket)
        return cls(key, path_list_path, opener=opener)

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


PATCH_PAK_RE = re.compile(r"^(.+)\.patch_(\d+)\.pak$", re.IGNORECASE)


def find_pak_files(game_root, pak_stem="re_chunk_000.pak"):
    """Find `pak_stem` and every `<pak_stem>.patch_NNN.pak` sibling directly
    under `game_root` - RE Engine's own patches sit right in the install
    root (unlike MT Framework's .arc files, which are nested a few levels
    down), so this is a plain directory listing, not a recursive walk.

    Returned in ascending priority order (base first, highest patch number
    last) for ReenFS.__init__ to add_fs() in that order: Capcom's own patch
    convention is that a higher patch number overrides a lower one/the base
    for any path it touches, falling through to an earlier layer for a path
    a later patch doesn't happen to include (confirmed via community
    modding documentation - Capcom doesn't publish this - not just assumed).
    """
    base = os.path.join(game_root, pak_stem)
    patches = []
    for name in os.listdir(game_root):
        match = PATCH_PAK_RE.match(name)
        if match and match.group(1).lower() == pak_stem.lower():
            patches.append((int(match.group(2)), os.path.join(game_root, name)))
    patches.sort(key=lambda entry: entry[0])

    paths = []
    if os.path.isfile(base):
        paths.append(base)
    paths.extend(path for _patch_num, path in patches)
    return paths


class ReenFS(MultiFS):
    """One RE Engine game install: `pak_stem` (default "re_chunk_000.pak")
    plus every `<pak_stem>.patch_NNN.pak` sibling found directly under
    `game_root` (see find_pak_files), layered highest-patch-first via
    MultiFS - falls through to an earlier/lower-patch layer for any path
    that particular layer doesn't have. All pak layers share the same
    path_list_path, since a hash's candidate-path match doesn't depend on
    which physical pak layer actually contains it.

    Also layers game_root's own loose files (config/exe/dll/etc.) on top,
    for convenience browsing - NOT an attempt at RE Engine's "loose mod
    file" runtime override mechanism, which appears to require an injected
    loader (REFramework) rather than being default engine behavior, and
    isn't replicated here (see PakFS module docstring / PR discussion).
    Pak-derived paths live under "natives/...", so in practice there's no
    real overlap with root-level loose files either way.
    """

    def __init__(self, game_root, path_list_path, pak_stem="re_chunk_000.pak", auto_close=True):
        super().__init__(auto_close=auto_close)
        game_root = str(game_root)
        if not os.path.isdir(game_root):
            raise CreateFailed(f"game_root does not exist or is not a directory: {game_root!r}")
        self.game_root = game_root

        pak_paths = find_pak_files(game_root, pak_stem)
        if not pak_paths:
            raise CreateFailed(f"no {pak_stem!r} (or patches) found under game_root {game_root!r}")
        for pak_path in pak_paths:
            self.add_fs(pak_path, PakFS(pak_path, path_list_path))

        # added last -> highest default priority, same convention as
        # MTFW_FS's own loose OSFS layer
        self.add_fs("<loose>", OSFS(game_root))
