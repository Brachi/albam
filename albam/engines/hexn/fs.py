"""
PyFilesystem2 adapter for Hexane Engine (RE:ORC) .ssg archives.

An .ssg bundles every file's bytes into one contiguous "solid" compressed
stream (see structs/ssg.ksy): fixed-size file-info entries record each
file's name and *uncompressed* size, but not its own compressed range - only
the whole `buffer_chunks` blob (itself split into independently
zlib-compressed chunks) decompresses to a stream that files are sliced out
of sequentially, each padded up to `size_padding`. That solid layout means -
unlike ArcFS/PakFS, where openbin() seeks straight to one entry's own
compressed range - an .ssg has to be fully decompressed up front to resolve
any single file's bytes. Not a large concern: one .ssg is one model's worth
of embedded assets, not a whole game's archive set.

`SsgFS` exposes a single .ssg as a read-only PyFilesystem2 filesystem;
`HexnFS` overlays every .ssg under a game root - plus loose files - into one
MultiFS, mirroring `albam.engines.mtfw.arc_fs.MTFW_FS`.
"""
import io
import os
import zlib

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.memoryfs import MemoryFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.path import dirname
from kaitaistruct import KaitaiStream

from .structs.hexane_ssg import HexaneSsg


def _local_opener(path):
    return open(path, "rb")


class SsgFS(FS):
    """Read-only PyFilesystem2 view of a single Hexane .ssg archive."""

    _meta = {
        "case_insensitive": False,
        "network": False,
        "read_only": True,
        "supports_rename": False,
        "thread_safe": True,
        "unicode_paths": True,
        "virtual": False,
    }

    def __init__(self, ssg_path, opener=None):
        super().__init__()
        self.ssg_path = str(ssg_path)
        self._opener = opener or _local_opener

        f = self._opener(self.ssg_path)
        try:
            data = f.read()
        finally:
            f.close()
        # `file_info.name` (below) is a lazily-computed Kaitai instance that
        # re-seeks/reads the stream on first access, not during _read() -
        # parse from an in-memory buffer rather than `f` itself, since `f`
        # is closed by the time each entry's name gets resolved.
        ssg = HexaneSsg(KaitaiStream(io.BytesIO(data)))
        ssg._read()

        uncompressed = bytearray()
        compressed_pos = 0
        for chunk_size in ssg.chunk_sizes:
            if not chunk_size:
                continue
            chunk = ssg.buffer_chunks[compressed_pos:compressed_pos + chunk_size]
            uncompressed.extend(zlib.decompress(chunk))
            compressed_pos += chunk_size

        self._data = {}
        self._directory = MemoryFS()
        offset = 0
        for file_info in ssg.files_info:
            path = "/" + file_info.name.replace("\\", "/").lstrip("/")
            self._data[path] = bytes(uncompressed[offset:offset + file_info.size])
            self._directory.makedirs(dirname(path), recreate=True)
            self._directory.create(path)
            offset += file_info.size + (-file_info.size % ssg.size_padding)

    def __repr__(self):
        return f"SsgFS({self.ssg_path!r})"

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        basic_info = self._directory.getinfo(_path)
        raw_info = {"basic": {"name": basic_info.name, "is_dir": basic_info.is_dir}}

        if "details" in namespaces:
            data = self._data.get(_path)
            resource_type = ResourceType.directory if basic_info.is_dir else ResourceType.file
            raw_info["details"] = {
                "type": int(resource_type),
                "size": len(data) if data is not None else 0,
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
        data = self._data.get(_path)
        if data is None:
            raise ResourceNotFound(path)
        return io.BytesIO(data)

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)


def find_ssg_files(game_root):
    """Recursively find every .ssg under `game_root`, case-insensitively -
    same shape as albam.engines.mtfw.arc_fs.find_arc_files()."""
    for current_dir, _dirs, files in os.walk(game_root):
        for name in files:
            if name.lower().endswith(".ssg"):
                yield os.path.join(current_dir, name)


class HexnFS(MultiFS):
    """Virtual filesystem for one RE:ORC game install.

    Given the game's root folder, finds every .ssg recursively and overlays
    them into a single filesystem, keyed by the path each entry decodes to.
    Loose files living directly on disk under `game_root` are layered on top
    with the highest priority - same convention as
    albam.engines.mtfw.arc_fs.MTFW_FS.
    """

    def __init__(self, game_root, auto_close=True):
        super().__init__(auto_close=auto_close)
        self.failed_ssgs = []

        game_root = str(game_root)
        if not os.path.isdir(game_root):
            raise CreateFailed(f"game_root does not exist or is not a directory: {game_root!r}")
        self.game_root = game_root

        for ssg_path in sorted(find_ssg_files(game_root)):
            try:
                ssg_fs = SsgFS(ssg_path)
            except Exception as e:
                self.failed_ssgs.append((ssg_path, e))
                continue
            self.add_fs(ssg_path, ssg_fs)

        # added last -> highest default priority -> wins over packed archives
        self.add_fs("<loose>", OSFS(game_root))
