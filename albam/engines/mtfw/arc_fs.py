"""
PyFilesystem2 adapter for MTFramework .arc archives.

An .arc is a flat, zip-like container (see structs/arc.ksy): a header
followed by fixed-size file entries (path, type-hash, sizes, offset), each
pointing to a zlib-compressed blob later in the file. `ArcFS` exposes a
single .arc as a read-only PyFilesystem2 filesystem; `MTFW_FS` overlays every
.arc under a game root - plus its loose files - into one `MultiFS`, so
callers can ask for a relative path without knowing which archive (or loose
file) it comes from.
"""
import os
import zlib

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, DirectoryExpected, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.memoryfs import MemoryFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.path import basename, dirname, join
from kaitaistruct import KaitaiStream

from . import FILE_ID_TO_EXTENSION
from .structs.arc import Arc
from ...lib.s3 import build_s3_client, s3_opener


def _entry_path(file_entry):
    ext = FILE_ID_TO_EXTENSION.get(file_entry.file_type, str(file_entry.file_type))
    posix_path = file_entry.file_path.replace("\\", "/").lstrip("/")
    return f"/{posix_path}.{ext}"


def _local_opener(path):
    return open(path, "rb")


class ArcFS(FS):
    """Read-only PyFilesystem2 view of a single .arc file.

    `arc_path` is an opaque identifier passed to `opener(arc_path)` to get a
    seekable, readable file-like object - not necessarily a local path.
    Defaults to plain `open()`; `MTFW_FS.from_s3()` passes an S3/R2-backed
    opener instead.
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

    def __init__(self, arc_path, opener=None):
        super().__init__()
        self.arc_path = str(arc_path)
        self._opener = opener or _local_opener

        # entries indexed by their exposed path, so getinfo/openbin don't
        # rescan file_entries. openbin() re-opens/re-fetches per read rather
        # than holding a persistent handle - avoids exhausting fd limits
        # locally (~1200 arcs in a full game install) and, over S3/R2, keeps
        # __init__ to just the small header+table region.
        f = self._opener(self.arc_path)
        try:
            arc = Arc(KaitaiStream(f))
            arc._read()
            self._entries = {}
            self._directory = MemoryFS()
            for file_entry in arc.file_entries:
                path = _entry_path(file_entry)
                self._entries[path] = file_entry
                self._directory.makedirs(dirname(path), recreate=True)
                self._directory.create(path)
        finally:
            f.close()

    def __repr__(self):
        return f"ArcFS({self.arc_path!r})"

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

        f = self._opener(self.arc_path)
        try:
            f.seek(file_entry.offset)
            raw = f.read(file_entry.zsize)
        finally:
            f.close()
        data = zlib.decompress(raw)
        return _BytesFile(data)

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)


def _BytesFile(data):
    import io

    return io.BytesIO(data)


def origin_arc_path(fs_instance, path):
    """The real, directly-openable .arc path `path` resolves to under
    `fs_instance`, or None if it's a loose/real file (or `fs_instance`
    doesn't track archive origins).

    `ArcFS` always resolves to its own single arc; `MTFW_FS` defers to its
    own `origin_absolute_path()` (not `origin_of()`, which returns a
    game-root-relative identity meant for display/hashing, not I/O). Lets
    callers (e.g. Pack/Patch) write back into the right archive without
    caring whether the VFS root was a single `.arc` or a whole game folder.
    """
    if isinstance(fs_instance, MTFW_FS):
        return fs_instance.origin_absolute_path(path)
    if isinstance(fs_instance, ArcFS):
        return fs_instance.arc_path
    return None


def find_arc_files(game_root):
    """Recursively find every .arc under `game_root`, case-insensitively.

    os.walk already uses os.scandir under the hood, so this is a single
    scandir-based traversal - no extra stat() calls per file.
    """
    for current_dir, _dirs, files in os.walk(game_root):
        for name in files:
            if name.lower().endswith(".arc"):
                yield os.path.join(current_dir, name)


def find_arc_keys_s3(client, bucket, prefix=""):
    """S3/R2 equivalent of find_arc_files(): paginated key listing under
    `prefix`, filtered to .arc keys, case-insensitively."""
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".arc"):
                yield key


class S3LooseFS(FS):
    """Loose-file layer for MTFW_FS.from_s3 - the remote equivalent of the
    local OSFS(game_root) layer, reusing the same boto3 `client` as the arc
    layer (no separate credentials needed, unlike fs_s3fs.S3FS).

    Matches local MTFW_FS behavior in one easy-to-miss way: .arc keys are
    NOT filtered out here, so they stay reachable as raw blobs at their own
    key alongside their unpacked content exposed through the arc layer -
    harmless since the two views never collide (see MTFW_FS.from_s3).

    Reads fetch whole objects, not ranges - a loose file's entire content is
    needed anyway, unlike one entry out of a huge archive.

    Assumes a plain folder-sync-style bucket: "directories" come from key
    prefixes via list_objects_v2's Delimiter, not explicit zero-byte
    directory-marker objects some other S3 tooling creates.
    """

    _meta = {
        "case_insensitive": False,
        "network": True,
        "read_only": True,
        "supports_rename": False,
        "thread_safe": True,
        "unicode_paths": True,
        "virtual": False,
    }

    def __init__(self, client, bucket, prefix=""):
        super().__init__()
        self.client = client
        self.bucket = bucket
        self.prefix = prefix.strip("/")

    def __repr__(self):
        return f"S3LooseFS({self.bucket!r}, prefix={self.prefix!r})"

    def _key(self, path):
        _path = self.validatepath(path).strip("/")
        if self.prefix:
            return f"{self.prefix}/{_path}" if _path else self.prefix
        return _path

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()

        if _path == "/":
            return Info({"basic": {"name": "", "is_dir": True}})

        key = self._key(_path)
        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception:
            head = None

        if head is not None:
            raw_info = {"basic": {"name": basename(_path), "is_dir": False}}
            if "details" in namespaces:
                raw_info["details"] = {"type": int(ResourceType.file), "size": head["ContentLength"]}
            return Info(raw_info)

        # not a real object at this exact key - does anything live "under" it?
        resp = self.client.list_objects_v2(Bucket=self.bucket, Prefix=key + "/", MaxKeys=1)
        if resp.get("KeyCount", 0) > 0:
            raw_info = {"basic": {"name": basename(_path), "is_dir": True}}
            if "details" in namespaces:
                raw_info["details"] = {"type": int(ResourceType.directory), "size": 0}
            return Info(raw_info)

        raise ResourceNotFound(path)

    def listdir(self, path):
        return [info.name for info in self.scandir(path)]

    def scandir(self, path, namespaces=None, page=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()

        if not self.getinfo(_path).is_dir:
            raise DirectoryExpected(path)

        key_prefix = self._key(_path)
        if key_prefix and not key_prefix.endswith("/"):
            key_prefix += "/"

        entries = []
        paginator = self.client.get_paginator("list_objects_v2")
        for result in paginator.paginate(Bucket=self.bucket, Prefix=key_prefix, Delimiter="/"):
            for common_prefix in result.get("CommonPrefixes", ()):
                name = common_prefix["Prefix"][len(key_prefix):].rstrip("/")
                if name:
                    entries.append(Info({"basic": {"name": name, "is_dir": True}}))
            for obj in result.get("Contents", ()):
                name = obj["Key"][len(key_prefix):]
                if name:
                    raw_info = {"basic": {"name": name, "is_dir": False}}
                    if "details" in namespaces:
                        raw_info["details"] = {"type": int(ResourceType.file), "size": obj["Size"]}
                    entries.append(Info(raw_info))

        if page is not None:
            start, end = page
            entries = entries[start:end]
        return iter(entries)

    def openbin(self, path, mode="r", buffering=-1, **options):
        self.check()
        if "w" in mode or "+" in mode or "a" in mode:
            raise ResourceReadOnly(path)

        _path = self.validatepath(path)
        key = self._key(_path)
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except Exception:
            raise ResourceNotFound(path)
        return _BytesFile(response["Body"].read())

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)


class MTFW_FS(MultiFS):
    """Virtual filesystem for one MTFW game install.

    Given the game's root folder, finds every .arc recursively and overlays
    them into a single filesystem, keyed by the path each entry decodes to.
    Loose files living directly on disk under `game_root` are layered on top
    with the highest priority, since that's how the engine's own patch/mod
    loading works (an unpacked file shadows the packed one).
    """

    def __init__(self, game_root, auto_close=True):
        # super().__init__() first: FS.__del__ calls close() unconditionally
        # on GC, and MultiFS.close() needs self._auto_close/_filesystems to
        # already exist. Raising CreateFailed before this would leave a
        # half-initialized object that errors on garbage collection.
        super().__init__(auto_close=auto_close)
        self._init_common()

        game_root = str(game_root)
        if not os.path.isdir(game_root):
            raise CreateFailed(f"game_root does not exist or is not a directory: {game_root!r}")
        self.game_root = game_root

        arc_specs = ((p, _local_opener) for p in sorted(find_arc_files(game_root)))
        self._load_arcs(arc_specs)

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
        """Alternate constructor: source .arc files from an S3-compatible
        bucket instead of a local game install. Works against Cloudflare R2
        as-is - pass R2's account-specific endpoint_url and an R2 API token
        as access key/secret:

            game_fs = MTFW_FS.from_s3(
                bucket="my-bucket",
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=...,
                aws_secret_access_key=...,
            )

        Credential params forward straight to boto3.client("s3", ...) -
        leave unset to fall back to boto3's normal credential resolution.
        One client is built internally and reused for both the arc and
        loose layers.

        Reads are real HTTP Range requests (via smart_open) - never a full
        .arc download.

        IMPORTANT: `prefix` must be the game *root*, not the archive folder.
        It's used both to find arcs (recursive key listing, so arcs nested
        under `prefix` are found fine) and, when `include_loose` is on, as
        the root loose paths resolve relative to - narrowing it to just the
        archive folder silently breaks loose resolution. `prefix=""` if
        your bucket mirrors the whole game root, same as `game_root`
        locally. The paths MTFW_FS exposes for arc content come entirely
        from the arc's own internal file table, independent of `prefix`.

        `include_loose=True` (default) layers an S3LooseFS over `bucket`/
        `prefix`, same highest-priority-wins semantics as the local OSFS
        layer (see S3LooseFS's docstring for what it assumes about the
        bucket). An override loose file needs its own key equal to the
        exposed path itself (not inside the Archive/ prefix) to shadow the
        packed copy.
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
        self._init_common()
        self.game_root = f"s3://{bucket}/{prefix}"
        # keys come back from find_arc_keys_s3 already rooted under prefix
        # (e.g. "game/nativePC_MT/.../foo.arc") - origin_of() strips this
        # against the key directly, not game_root (an "s3://bucket/prefix"
        # sentinel, not a real path os.path.relpath could use meaningfully).
        self._s3_prefix = prefix.strip("/")

        opener = s3_opener(client, bucket)
        arc_specs = ((key, opener) for key in sorted(find_arc_keys_s3(client, bucket, prefix)))
        self._load_arcs(arc_specs)

        if include_loose:
            # added last -> highest default priority -> wins over packed archives
            self.add_fs("<loose>", S3LooseFS(client, bucket, prefix))
        return self

    def _init_common(self):
        # (arc_path, exception) for archives that didn't parse - a handful of
        # RE5's .arc files use a different/unsupported layout (see arc.ksy);
        # skipped rather than failing the whole game filesystem.
        self.failed_arcs = []
        # lazily built - see _ensure_index()
        self._owner = None
        self._topology = None
        # None for a local instance; set by from_s3() - see origin_of()
        self._s3_prefix = None

    def _load_arcs(self, arc_specs):
        for arc_path, opener in arc_specs:
            try:
                arc_fs = ArcFS(arc_path, opener=opener)
            except Exception as e:
                self.failed_arcs.append((arc_path, e))
                continue
            self.add_fs(arc_path, arc_fs)

    def _ensure_index(self):
        """Build a flat path->owner index plus a directory-topology-only
        MemoryFS, on first use. MultiFS's own listdir/scandir ask every
        layered filesystem per directory visited - O(directories x
        filesystems), ~9.5M calls / ~70s for a full RE5 walk over ~1200
        archives. Replaced with one upfront O(total entries) pass and O(1)
        lookups after, for listdir/scandir/walk only - point lookups already
        go through MultiFS's own _delegate and stay fast without this.
        """
        if self._owner is not None:
            return

        owner = {}
        topology = MemoryFS()
        # iterate_fs() yields (name, fs) in priority order, highest first;
        # first writer for a path wins, matching MultiFS's own semantics.
        for _name, fs_ in self.iterate_fs():
            for path in fs_.walk.files():
                if path in owner:
                    continue
                owner[path] = fs_
                topology.makedirs(dirname(path), recreate=True)
                topology.create(path)

        self._owner = owner
        self._topology = topology

    def listdir(self, path):
        self.check()
        self._ensure_index()
        return self._topology.listdir(path)

    def scandir(self, path, namespaces=None, page=None):
        self.check()
        self._ensure_index()
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        for info in self._topology.scandir(_path, namespaces=("basic",), page=page):
            if info.is_dir or not namespaces:
                yield info
                continue
            # topology only knows the name/is_dir placeholder; fetch real
            # info (size, etc.) from whichever filesystem actually owns it.
            child_path = join(_path, info.name)
            yield self._owner[child_path].getinfo(child_path, namespaces=namespaces)

    def _owning_arc_fs(self, path):
        """The ArcFS `path` resolves to, or None if it's a loose/real file.
        Uses the lazy index (O(1)) if already built by a prior
        listdir/scandir/walk; otherwise falls back to MultiFS.which()'s
        linear scan rather than forcing an index build, keeping point
        lookups index-free.
        """
        self.check()
        _path = self.validatepath(path)
        if self._owner is not None:
            owner_fs = self._owner.get(_path)
        else:
            _name, owner_fs = self.which(_path)
        return owner_fs if isinstance(owner_fs, ArcFS) else None

    def origin_of(self, path):
        """Portable identity of the .arc `path` resolves to - its own path
        relative to game_root for a local instance, or relative to `prefix`
        for an MTFW_FS.from_s3() instance (forward slashes either way,
        original casing preserved) - or None if it's a loose/real file (or
        doesn't resolve at all).

        This is meant for display/hashing (see tests/mtfw/scripts/
        catalog_paths.py): it deliberately doesn't leak where game_root
        happens to sit on this disk (or which bucket, for S3/R2). It is NOT
        directly openable - use origin_absolute_path() for that.
        """
        owner_fs = self._owning_arc_fs(path)
        if owner_fs is None:
            return None
        arc_path = owner_fs.arc_path
        if self._s3_prefix is not None:
            if self._s3_prefix and arc_path.startswith(self._s3_prefix + "/"):
                return arc_path[len(self._s3_prefix) + 1:]
            return arc_path
        return os.path.relpath(arc_path, self.game_root).replace(os.sep, "/")

    def origin_absolute_path(self, path):
        """The real, directly-openable identifier (ArcFS.arc_path - a local
        filesystem path for a local MTFW_FS, or an S3 key for
        MTFW_FS.from_s3) of the .arc `path` resolves to, or None. Use this
        (not origin_of()) when the caller actually needs to open/write the
        archive - e.g. Pack/Patch, via origin_arc_path() below.
        """
        owner_fs = self._owning_arc_fs(path)
        return owner_fs.arc_path if owner_fs is not None else None
