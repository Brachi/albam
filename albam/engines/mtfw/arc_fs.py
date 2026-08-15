"""
Prototype: PyFilesystem2 adapter for MTFramework .arc archives.

An .arc is a flat, zip-like container (see structs/arc.ksy): a header followed
by fixed-size file entries (path, type-hash, sizes, offset), each pointing to
a zlib-compressed blob later in the file. `ArcFS` exposes a single .arc as a
read-only PyFilesystem2 filesystem; `MTFW_FS` represents one game install:
given the game's root folder, it finds every .arc recursively and overlays
them - plus the loose files sitting directly on disk - into a single `MultiFS`,
so callers can ask for a relative path without knowing which archive (or
whether an unpacked/modded loose file) it actually comes from.
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


def _entry_path(file_entry):
    ext = FILE_ID_TO_EXTENSION.get(file_entry.file_type, str(file_entry.file_type))
    posix_path = file_entry.file_path.replace("\\", "/").lstrip("/")
    return f"/{posix_path}.{ext}"


def _local_opener(path):
    return open(path, "rb")


class ArcFS(FS):
    """Read-only PyFilesystem2 view of a single .arc file.

    `arc_path` is just an opaque identifier passed to `opener(arc_path)` to
    get a seekable, readable file-like object - it doesn't have to be a local
    filesystem path. Defaults to plain `open()`, so local usage is unchanged;
    `MTFW_FS.from_s3()` passes an S3/R2-backed opener instead (see there).
    """

    _meta = {
        "case_insensitive": False,  # TODO: arc paths are effectively case-insensitive
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

        # entries indexed the same way they're exposed as paths, so getinfo/
        # openbin don't need to recompute _entry_path or re-scan file_entries.
        # Only the plain fields read below (offset/zsize/size) are kept -
        # openbin() re-opens/re-fetches per read (see there) rather than
        # holding a persistent handle. Locally that avoids exhausting the
        # process's file descriptor limit when a game install layers ~1200 of
        # these at once; over S3/R2 it means __init__ only ever fetches the
        # small header+table region, never the whole (possibly huge) archive.
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
    """Which .arc `path` resolves to under `fs_instance`, or None if it's a
    loose/real file (or `fs_instance` doesn't track archive origins at all).

    `ArcFS` always resolves to its own single arc; `MTFW_FS` may overlay many,
    so it defers to its own `origin_of()`. Used by callers (e.g. Pack/Patch)
    that need to write back into the specific archive a file came from,
    without caring whether the VFS root behind it was a single `.arc` or a
    whole recursively-scanned game folder.
    """
    if isinstance(fs_instance, MTFW_FS):
        return fs_instance.origin_of(path)
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


def _s3_opener(client, bucket, range_chunk_size=1024 * 1024):
    """Build an ArcFS `opener` backed by an S3-compatible bucket (R2 works
    here too - just point `client` at R2's endpoint, see MTFW_FS.from_s3).
    Uses smart_open so seek()/read() become real HTTP Range requests instead
    of downloading the whole (possibly huge) archive: `defer_seek=True` means
    opening the file doesn't even issue a request until the first read.

    range_chunk_size matters more than it looks: smart_open's default
    (`None`) issues an *open-ended* Range request (`bytes=N-`) whose
    Content-Length covers everything from N to EOF - i.e. reading 8 bytes
    from the start of a 40MB archive asks the server for the full remaining
    40MB (confirmed against real fixture .arc files, not just guessed).
    Setting range_chunk_size bounds every underlying GET to that span;
    reads larger than one chunk transparently issue more (still bounded)
    requests. 1MiB is a reasonable default for this format - large enough
    that a typical archive's whole header+file-table fits in one request,
    small enough that reading one compressed entry only costs a handful of
    requests instead of one that could be tens of MB.
    """
    import smart_open

    def opener(key):
        return smart_open.open(
            f"s3://{bucket}/{key}",
            "rb",
            transport_params={
                "client": client,
                "defer_seek": True,
                "range_chunk_size": range_chunk_size,
            },
        )

    return opener


class S3LooseFS(FS):
    """Loose-file layer for MTFW_FS.from_s3 - the remote equivalent of the
    local OSFS(game_root) layer, reusing the same boto3 `client` as the arc
    layer (no separate credentials needed, unlike fs_s3fs.S3FS).

    Deliberately matches local MTFW_FS behavior in one easy-to-miss way:
    .arc keys are NOT filtered out here. A game install's .arc files remain
    reachable as raw whole blobs at their own key, same as they are locally
    through OSFS - alongside, and independent from, their unpacked content
    exposed through the arc layer at completely different paths. This is
    harmless (the two views never collide - see MTFW_FS.from_s3's docstring
    for why) and is what makes e.g. re-uploading/backing up an archive
    unchanged possible through this same filesystem.

    Reads fetch whole objects, not ranges - unlike ArcFS, a loose file's
    entire content is needed anyway, there's no "one entry out of a huge
    archive" situation to be careful about.

    Assumes a plain folder-sync-style bucket (a straight upload/mirror of a
    real directory tree): "directories" are inferred purely from key
    prefixes via list_objects_v2's Delimiter, not from explicit zero-byte
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
        bucket instead of a local game install - tested against a mocked S3
        (moto); works against Cloudflare R2 as-is, just pass R2's
        account-specific endpoint_url and an R2 API token as access key/secret:

            game_fs = MTFW_FS.from_s3(
                bucket="my-bucket",
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=...,
                aws_secret_access_key=...,
            )

        Credential params default to None/"auto" and are forwarded straight
        to boto3.client("s3", ...) - leave them unset to fall back to
        boto3's normal credential resolution (env vars, ~/.aws/credentials,
        etc.) instead of passing secrets explicitly. One client gets built
        internally and reused for both the arc layer and (when enabled) the
        loose layer, so there's only one place credentials are handled.

        Reads are real HTTP Range requests (via smart_open) - constructing
        this and reading individual files never downloads a whole .arc.

        IMPORTANT: `prefix` must be the game *root*, not the folder your
        .arc files happen to live in. It's used both to find arcs (recursive
        key listing, like local find_arc_files()/os.walk - arcs nested a few
        levels down under `prefix`, e.g. "nativePC_MT/Image/Archive/*.arc",
        are found fine) and, when `include_loose` is on, as the root loose
        file paths are resolved relative to. Narrowing `prefix` down to just
        the archive folder (an easy mistake - it looks like a reasonable
        "scope arc discovery tighter" optimization) silently breaks loose
        resolution instead: every loose lookup gets `prefix` prepended twice
        or resolves under the wrong root and just won't be found. If your
        bucket mirrors the whole game root exactly, `prefix=""` is what you
        want, exactly like `game_root` locally.

        Separately: the paths MTFW_FS *exposes* for content inside an arc
        (e.g. "/pawn/pl/pl00/model/pl0000.mod") come entirely from the arc's
        own internal file table - nothing to do with the arc's own key or
        `prefix` at all.

        `include_loose=True` (default) layers an S3LooseFS over `bucket`/
        `prefix` on top, with the same highest-priority-wins semantics the
        local OSFS layer has - assumes the bucket mirrors a real game root
        exactly (see S3LooseFS's docstring for what that assumes away: no
        explicit directory-marker objects, and everything under `prefix`,
        including .arc files themselves, is legitimately part of the game
        data). Uses the same internally-built client as the arc layer, so
        no separate credentials are needed for it. An unpacked/override
        loose file needs its own key equal to the exposed path itself (e.g.
        a key literally named "pawn/pl/pl00/model/pl0000.mod", not inside
        the Archive/ prefix) to actually shadow the packed copy of that path.
        """
        import boto3

        client = boto3.client(
            "s3",
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

        opener = _s3_opener(client, bucket)
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
        layered filesystem per directory it visits - O(directories x
        filesystems), ~9.5M calls / ~70s for a full RE5 walk over ~1200
        archives. This replaces that with one upfront O(total entries) pass
        (a few seconds) and O(1) lookups after, for listdir/scandir/walk only.
        Point lookups (openbin/getinfo on a known path) already go through
        MultiFS's own _delegate and stay fast without this, so they don't
        trigger it.
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

    def origin_of(self, path):
        """The .arc path `path` resolves to, or None if it's a loose/real
        file (or doesn't resolve at all). Uses the lazy index (O(1)) if it's
        already been built by a prior listdir/scandir/walk call; otherwise
        falls back to MultiFS.which()'s linear scan rather than forcing the
        index build itself, keeping point lookups index-free.
        """
        self.check()
        _path = self.validatepath(path)
        if self._owner is not None:
            owner_fs = self._owner.get(_path)
        else:
            _name, owner_fs = self.which(_path)
        return owner_fs.arc_path if isinstance(owner_fs, ArcFS) else None
