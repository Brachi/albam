"""
PyFilesystem2 adapter for Hexane Engine (RE:ORC) .ssg archives.

An .ssg bundles every file's bytes into one contiguous "solid" compressed
stream (see structs/ssg.ksy): fixed-size file-info entries record each
file's name and *uncompressed* size, but not its own compressed range - only
the whole `buffer_chunks` blob (itself split into independently
zlib-compressed chunks) decompresses to a stream that files are sliced out
of sequentially, each padded up to `size_padding`. That solid layout means -
unlike ArcFS/PakFS, where openbin() seeks straight to one entry's own
compressed range - resolving any single file's bytes means decompressing
the *whole* archive's `buffer_chunks` together. `SsgFS` defers that to the
first file actually requested from a given archive rather than doing it in
__init__ (see `_ensure_decompressed()`) - a real game install has ~2000
.ssg, and a typical session only ever touches a handful of them.

`SsgFS` exposes a single .ssg as a read-only PyFilesystem2 filesystem;
`HexnFS` overlays every .ssg under a game root - plus loose files - into one
MultiFS, mirroring `albam.engines.mtfw.arc_fs.MTFW_FS`.
"""
import io
import os
import zlib
from collections import OrderedDict

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, DirectoryExpected, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.memoryfs import MemoryFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.path import dirname
from kaitaistruct import KaitaiStream

from .structs.hexane_ssg import HexaneSsg
from ...lib.s3 import S3LooseFS, build_s3_client, s3_opener


def _local_opener(path):
    return open(path, "rb")


class SsgFS(FS):
    """Read-only PyFilesystem2 view of a single Hexane .ssg archive.

    __init__ only reads the file table (names + sizes, cheap) - mirrors
    ArcFS.__init__ in spirit. Unlike .arc though, .ssg is a solid archive
    (every file's bytes are concatenated into one continuous stream before
    being chunk-compressed, not each independently seekable like .arc's own
    entries), so a single file's bytes still can't be resolved without
    decompressing the *whole* archive's `buffer_chunks` together - that
    work is just deferred to the first file actually requested from this
    archive instead of happening unconditionally in __init__
    (_ensure_decompressed(), cached from then on). Real payoff: a game
    install has ~2000 .ssg, and any one HexnFS session only ever touches a
    handful of them - constructing one no longer means decompressing every
    archive in the game up front.

    openbin() re-reads+re-parses the archive fresh on first access rather
    than __init__ keeping a reference to what it already read - same
    reasoning as ArcFS's own re-open-per-read (see its docstring): holding
    every constructed instance's compressed bytes resident "just in case"
    would give back most of the memory savings for the ~2000 archives that
    end up never being touched at all.
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

    def __init__(self, ssg_path, opener=None):
        super().__init__()
        self.ssg_path = str(ssg_path)
        self._opener = opener or _local_opener

        ssg = self._read_and_parse()
        self._sizes = {}
        self._offsets = {}
        self._directory = MemoryFS()
        offset = 0
        for file_info in ssg.files_info:
            path = "/" + file_info.name.replace("\\", "/").lstrip("/")
            self._sizes[path] = file_info.size
            self._offsets[path] = offset
            self._directory.makedirs(dirname(path), recreate=True)
            self._directory.create(path)
            offset += file_info.size + (-file_info.size % ssg.size_padding)

        self._data = None  # populated lazily - see _ensure_decompressed()

    def _read_and_parse(self):
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
        return ssg

    def _ensure_decompressed(self):
        if self._data is not None:
            return

        ssg = self._read_and_parse()
        if ssg.chunk_sizes:
            uncompressed = bytearray()
            compressed_pos = 0
            for chunk_size in ssg.chunk_sizes:
                if not chunk_size:
                    continue
                chunk = ssg.buffer_chunks[compressed_pos:compressed_pos + chunk_size]
                uncompressed.extend(zlib.decompress(chunk))
                compressed_pos += chunk_size
        else:
            # No chunk table (size_chunks_info == 0, seen on some smaller
            # .ssg) - buffer_chunks is stored raw/uncompressed in this
            # case, not zlib-compressed
            # at all. Confirmed by decoding a known entry's expected magic
            # (b"FM6S") directly out of the raw bytes at its computed
            # offset - zlib.decompress on the whole blob fails outright
            # ("incorrect header check"), and the total uncompressed size
            # every files_info entry needs matches size_chunks_buffer
            # exactly, consistent with "no compression happened here".
            uncompressed = ssg.buffer_chunks

        self._data = {
            path: bytes(uncompressed[offset:offset + self._sizes[path]])
            for path, offset in self._offsets.items()
        }

    def __repr__(self):
        return f"SsgFS({self.ssg_path!r})"

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        basic_info = self._directory.getinfo(_path)
        raw_info = {"basic": {"name": basic_info.name, "is_dir": basic_info.is_dir}}

        if "details" in namespaces:
            resource_type = ResourceType.directory if basic_info.is_dir else ResourceType.file
            raw_info["details"] = {
                "type": int(resource_type),
                "size": self._sizes.get(_path, 0),
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
        if _path not in self._sizes:
            raise ResourceNotFound(path)
        self._ensure_decompressed()
        return io.BytesIO(self._data[_path])

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)


# A real RE:ORC install ships two families of info-only .ssg archives -
# per-pack "ModelInfos.ssg" (4 on a full install) and per-level
# "<name>.minfo.ssg" (36) - each holding small per-model metadata records
# (distinct magic "IM6S", ~1-2KB) filed under the *same* virtual paths as
# the real, full-geometry .edgemodel files (magic "FM6S") that live in
# separate content archives - e.g. dlc/pack1/Characters/ModelInfos.ssg has
# an "IM6S" stub at .../vector.edgemodel, while the real ~1.2MB "FM6S"
# mesh for that same path lives in dlc/pack1/Characters/vector.ssg.
# Nothing in this codebase parses the "IM6S" format - see _ssg_priority().
# A random 300-archive sample of the full install found no third pattern
# of info-only archive beyond these two.
def _is_info_only_ssg(ssg_path):
    basename = os.path.basename(ssg_path).lower()
    return basename == "modelinfos.ssg" or basename.endswith(".minfo.ssg")


def _ssg_priority(ssg_path):
    """MultiFS priority for one discovered .ssg (see HexnFS.__init__).

    All real content archives share the default priority (0), resolved by
    MultiFS's own reverse-add-order tie-break - fine on its own, except an
    info-only archive (see _is_info_only_ssg() above) sorts alphabetically
    after some real content archives too, so with everything at the same
    priority it can silently shadow them: a lookup for a shared path
    returns the tiny info stub instead of the real mesh. Confirmed on a
    real install: across the 4 ModelInfos.ssg archives alone, 103 of 171
    virtual paths they share with a real content archive resolved to the
    wrong stub before this fix (the 36 per-level .minfo.ssg archives add
    more of the same, unquantified).

    Giving info-only archives a strictly lower priority means one only
    ever resolves a path no other (real-priority) archive already claims -
    real content always wins on a shared path, while any path that turns
    out to exist *only* inside an info-only archive still resolves
    instead of disappearing outright (confirmed real on this install: some
    weapon .edgemodel paths, e.g. wep_railgun, exist only as an "IM6S"
    stub with no real-content archive backing them at all).
    """
    if _is_info_only_ssg(ssg_path):
        return -1
    return 0


def find_ssg_files(game_root):
    """Recursively find every .ssg under `game_root`, case-insensitively -
    same shape as albam.engines.mtfw.arc_fs.find_arc_files()."""
    for current_dir, _dirs, files in os.walk(game_root):
        for name in files:
            if name.lower().endswith(".ssg"):
                yield os.path.join(current_dir, name)


def find_ssg_keys_s3(client, bucket, prefix=""):
    """S3/R2 equivalent of find_ssg_files(): paginated key listing under
    `prefix`, filtered to .ssg keys, case-insensitively - mirrors
    albam.engines.mtfw.arc_fs.find_arc_keys_s3()."""
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".ssg"):
                yield key


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
        # None for a local instance; set by from_s3() - see origin_of()
        self._s3_prefix = None

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
            self.add_fs(ssg_path, ssg_fs, priority=_ssg_priority(ssg_path))

        # added last -> highest default priority -> wins over packed archives
        self.add_fs("<loose>", OSFS(game_root))

    @classmethod
    def from_s3(
        cls,
        bucket,
        prefix="",
        *,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        endpoint_url=None,
        region_name="auto",
        auto_close=True,
        include_loose=True,
    ):
        """Alternate constructor: source .ssg files from an S3-compatible
        bucket (R2 works as-is - pass R2's endpoint_url + API token as
        access key/secret). Credential params fall back to boto3's normal
        resolution (env vars, etc.) when unset. Mirrors
        albam.engines.mtfw.arc_fs.MTFW_FS.from_s3() - see there for the
        `prefix`/`include_loose` semantics, identical here.

            game_fs = HexnFS.from_s3(
                bucket="my-bucket",
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=..., aws_secret_access_key=...,
            )
        """
        client = build_s3_client(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )

        self = cls.__new__(cls)
        MultiFS.__init__(self, auto_close=auto_close)
        self.failed_ssgs = []
        self.game_root = f"s3://{bucket}/{prefix}"
        # keys come back from find_ssg_keys_s3 already rooted under prefix -
        # origin_of() strips this against the key directly, not game_root
        # (an "s3://bucket/prefix" sentinel, not a real path os.path.relpath
        # could use meaningfully).
        self._s3_prefix = prefix.strip("/")

        opener = s3_opener(client, bucket)
        for ssg_key in sorted(find_ssg_keys_s3(client, bucket, prefix)):
            try:
                ssg_fs = SsgFS(ssg_key, opener=opener)
            except Exception as e:
                self.failed_ssgs.append((ssg_key, e))
                continue
            self.add_fs(ssg_key, ssg_fs, priority=_ssg_priority(ssg_key))

        if include_loose:
            # added last -> highest default priority -> wins over packed archives
            self.add_fs("<loose>", S3LooseFS(client, bucket, prefix))
        return self

    def _owning_ssg_fs(self, path):
        self.check()
        _path = self.validatepath(path)
        _name, owner_fs = self.which(_path)
        return owner_fs if isinstance(owner_fs, SsgFS) else None

    def origin_of(self, path):
        """The .ssg `path` resolves to - its own path relative to game_root
        for a local instance, or relative to `prefix` for a
        HexnFS.from_s3() instance (forward slashes either way) - or None if
        it's a loose/real file (or doesn't resolve at all). Mirrors
        albam.engines.mtfw.arc_fs.MTFW_FS.origin_of(). No index/caching like
        MTFW_FS's - a real install here is on the order of hundreds of .ssg
        files, not ~1000+ .arc, so a linear which() scan per lookup is fine.
        """
        owner_fs = self._owning_ssg_fs(path)
        if owner_fs is None:
            return None
        ssg_path = owner_fs.ssg_path
        if self._s3_prefix is not None:
            if self._s3_prefix and ssg_path.startswith(self._s3_prefix + "/"):
                return ssg_path[len(self._s3_prefix) + 1:]
            return ssg_path
        return os.path.relpath(ssg_path, self.game_root).replace(os.sep, "/")

    # listdir()/scandir(): MultiFS's own versions (see fs.multifs.MultiFS)
    # aggregate every overlaid sub-filesystem's listing for `path` and only
    # guard against `ResourceNotFound` per sub-fs - if any one of them
    # raises `DirectoryExpected` (because it has `path` as a plain file
    # instead), the whole aggregate call crashes instead of just skipping
    # that sub-fs. That's reachable with real, unmodified game data: a real
    # RE:ORC install has at least one .ssg packing a bare file entry named
    # "abilities" while the loose files also have a real "abilities/"
    # directory - same name, different type, in two different overlaid
    # filesystems. Both overrides below catch that too, so a sub-fs that
    # disagrees about a path's type is just skipped for that path (its
    # entries never contributed) rather than aborting the whole call -
    # consistent with "loosely layered on top, archives underneath" already
    # meaning a name can be shadowed outright, not just re-typed.
    def listdir(self, path):
        self.check()
        directory = []
        exists = False
        for _name, sub_fs in self.iterate_fs():
            try:
                directory.extend(sub_fs.listdir(path))
            except (ResourceNotFound, DirectoryExpected):
                pass
            else:
                exists = True
        if not exists:
            raise ResourceNotFound(path)
        return list(OrderedDict.fromkeys(directory))

    def scandir(self, path, namespaces=None, page=None):
        self.check()
        seen = set()
        exists = False
        for _name, sub_fs in self.iterate_fs():
            try:
                for info in sub_fs.scandir(path, namespaces=namespaces, page=page):
                    if info.name not in seen:
                        yield info
                        seen.add(info.name)
            except (ResourceNotFound, DirectoryExpected):
                pass
            else:
                exists = True
        if not exists:
            raise ResourceNotFound(path)
