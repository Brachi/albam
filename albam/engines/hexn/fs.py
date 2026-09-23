"""
PyFilesystem2 adapter for Hexane Engine (RE:ORC) .ssg archives.

An .ssg is a solid archive: every entry's bytes live in one `buffer_chunks`
blob, zlib-compressed in chunks, so reading any entry means decompressing
the whole blob. `SsgFS` defers that to the first read (see
`_ensure_decompressed()`), since a session touches few of the ~2000
archives. Entry layout by `id_magic` is documented in structs/ssg.ksy.

`SsgFS` exposes one .ssg; `HexnFS` overlays every .ssg under a game root,
plus loose files, into one MultiFS, like `albam.engines.mtfw.arc_fs.MTFW_FS`.

`SsgFS` also reads the big-endian `.anims.ssg` container (structs/anims.ksy),
since it shares the "ssg" extension the fs root loader is keyed by. Its
animation clips are exposed as `<name>.animclip` so the import registry can
dispatch on that extension.
"""
import io
import os
import threading
import zlib
from collections import OrderedDict, defaultdict

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, DirectoryExpected, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from fs.multifs import MultiFS
from fs.osfs import OSFS
from kaitaistruct import KaitaiStream

from .structs.hexane_anims import HexaneAnims
from .structs.hexane_ssg import HexaneSsg
from ...lib.s3 import S3LooseFS, build_s3_client, s3_opener

ANIM_CLIP_EXTENSION = ".animclip"

# The content types an id_magic 5 archive may hold to be mounted: .edgemodel,
# .matb, .hkx and a .dds's TPKH/TPKD pair. An allowlist, so the cutscene/mocap
# archives sharing that id_magic (whose entry names repeat) are refused.
SSG_V5_CONTENT_TYPES = frozenset({b"MODL", b"MATB", b"HAVK", b"TPKH", b"TPKD"})


def _local_opener(path):
    return open(path, "rb")


def _content_type(file_info):
    """`file_info.file_type` as its fourcc, e.g. b"MODL"."""
    return (file_info.file_type & 0xFFFFFFFF).to_bytes(4, "big")


class SsgFS(FS):
    """Read-only view of one .ssg. Only the file table is read up front."""

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

        ssg, self._struct_cls, archive_size = self._parse_header()
        self._sizes = {}
        self._offsets = {}
        # Skeleton paths, read as the whole raw file.
        self._raw_file_paths = set()
        # dir path -> immediate child names; cheaper than a MemoryFS.
        self._dir_children = defaultdict(set)
        self._known_dirs = {"/"}
        offset = 0
        # In the big-endian container, file_type 5 is an animation clip and 4
        # a skeleton, which skel.ksy parses from byte 0 of the file.
        is_be_container = self._struct_cls is HexaneAnims
        # Used by _ssg_priority(); not comparable for the big-endian container.
        self.id_magic = None if is_be_container else ssg.id_magic
        is_v5 = self.id_magic == 5
        if is_v5:
            self._check_v5_supported(ssg)
        for file_info in ssg.files_info:
            name = file_info.name.replace("\\", "/").lstrip("/")
            is_anim_clip = is_be_container and file_info.file_type == 5
            is_skeleton = is_be_container and file_info.file_type == 4
            path = "/" + (name + ANIM_CLIP_EXTENSION if is_anim_clip else name)
            if is_skeleton:
                self._raw_file_paths.add(path)
            # The TPKH stub of a .dds never takes the path from its TPKD.
            if not (path in self._sizes and _content_type(file_info) == b"TPKH"):
                self._sizes[path] = archive_size if is_skeleton else file_info.size
                self._offsets[path] = file_info.ofs_in_buffer_chunks if is_v5 else offset

            parts = path.strip("/").split("/")
            for i in range(len(parts)):
                parent = "/" + "/".join(parts[:i])
                self._dir_children[parent].add(parts[i])
                if i < len(parts) - 1:
                    self._known_dirs.add(parent.rstrip("/") + "/" + parts[i])

            if not is_v5:
                # The big-endian container packs entries without padding.
                padding = (0 if is_be_container or not ssg.size_padding
                           else -file_info.size % ssg.size_padding)
                offset += file_info.size + padding

        self._data = None  # populated lazily - see _ensure_decompressed()
        self._decompress_lock = threading.Lock()

    def _check_v5_supported(self, ssg):
        """Refuse an id_magic 5 archive whose entry offsets can't be trusted:
        chunk-compressed (the offsets index the stored buffer), holding a
        content type outside SSG_V5_CONTENT_TYPES, or with an entry running
        past the buffer. HexnFS reports the refusal (skipped_archives()).
        """
        if ssg.size_chunks_info:
            raise CreateFailed(
                f"id_magic 5 archive is chunk-compressed "
                f"(size_chunks_info={ssg.size_chunks_info}), which no known one is - its "
                f"file_info offsets index the stored buffer, not the decompressed stream"
            )
        unsupported = sorted(
            {_content_type(fi) for fi in ssg.files_info} - SSG_V5_CONTENT_TYPES)
        if unsupported:
            tags = ", ".join(t.decode("ascii", "replace") for t in unsupported)
            raise CreateFailed(
                f"id_magic 5 archive holds content types this reader doesn't model "
                f"({tags}) - not mounted rather than served on the model-data layout's "
                f"assumptions"
            )
        overrun = max(
            (fi.ofs_in_buffer_chunks + fi.size for fi in ssg.files_info), default=0)
        if overrun > ssg.size_chunks_buffer:
            raise CreateFailed(
                f"id_magic 5 archive has an entry running past the end of its buffer "
                f"({overrun} > size_chunks_buffer={ssg.size_chunks_buffer}), which no "
                f"known one does - its file_info offsets would slice short bytes"
            )

    def _open_and_parse(self, struct_cls):
        """Open the archive and parse it, leaving the lazy `buffer_chunks`
        unread. Returns the open file handle with the struct; the caller
        closes it once done with any lazy instance.
        """
        f = self._opener(self.ssg_path)
        try:
            ssg = struct_cls(KaitaiStream(f))
            ssg._read()
        except Exception:
            f.close()  # the caller only owns the handle once it gets one
            raise
        return f, ssg

    def _parse_header(self):
        """Parse the header and file table, trying the little-endian format
        first and the big-endian one on failure. Names are sliced from
        `file_names` directly, avoiding a lazy seek per entry.
        Returns (ssg, struct_cls, archive_size).
        """
        try:
            f, ssg = self._open_and_parse(HexaneSsg)
            struct_cls = HexaneSsg
        except Exception:
            f, ssg = self._open_and_parse(HexaneAnims)
            struct_cls = HexaneAnims
        f.seek(0, os.SEEK_END)
        archive_size = f.tell()
        f.close()
        file_names = ssg.file_names
        for file_info in ssg.files_info:
            end = file_names.index(b"\x00", file_info.name_offset_rel)
            file_info.name = file_names[file_info.name_offset_rel:end].decode("ascii")
        return ssg, struct_cls, archive_size

    def _ensure_decompressed(self):
        """Decompress the whole archive once and cache it until close().
        The cache is published only when complete, under a lock, so a failed
        or concurrent read never sees it half-built.
        """
        with self._decompress_lock:
            if self._data is not None:
                return self._data
            data = {}

            for path in self._raw_file_paths:
                f = self._opener(self.ssg_path)
                try:
                    raw = f.read()
                finally:
                    f.close()
                data[path] = raw

            remaining = self._offsets.keys() - self._raw_file_paths
            if remaining:
                f, ssg = self._open_and_parse(self._struct_cls)
                try:
                    buffer_chunks = ssg.buffer_chunks  # triggers the lazy seek+read
                    if ssg.chunk_sizes:
                        uncompressed = bytearray()
                        compressed_pos = 0
                        for chunk_size in ssg.chunk_sizes:
                            if not chunk_size:
                                continue
                            chunk = buffer_chunks[compressed_pos:compressed_pos + chunk_size]
                            uncompressed.extend(zlib.decompress(chunk))
                            compressed_pos += chunk_size
                    else:
                        # No chunk table: buffer_chunks is stored uncompressed.
                        uncompressed = buffer_chunks
                finally:
                    f.close()

                for path in remaining:
                    offset = self._offsets[path]
                    data[path] = bytes(uncompressed[offset:offset + self._sizes[path]])

            self._data = data
            return data

    def close(self):
        """Also drop the decompressed archive."""
        self._data = None
        super().close()

    def __repr__(self):
        return f"SsgFS({self.ssg_path!r})"

    def getinfo(self, path, namespaces=None):
        self.check()
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        is_dir = _path == "/" or _path in self._known_dirs
        if not is_dir and _path not in self._sizes:
            raise ResourceNotFound(path)
        name = _path.rsplit("/", 1)[-1] or "/"
        raw_info = {"basic": {"name": name, "is_dir": is_dir}}

        if "details" in namespaces:
            resource_type = ResourceType.directory if is_dir else ResourceType.file
            raw_info["details"] = {
                "type": int(resource_type),
                "size": self._sizes.get(_path, 0),
            }
        return Info(raw_info)

    def listdir(self, path):
        self.check()
        _path = self.validatepath(path)
        if _path != "/" and _path not in self._known_dirs:
            raise ResourceNotFound(path)
        return sorted(self._dir_children.get(_path, ()))

    def openbin(self, path, mode="r", buffering=-1, **options):
        self.check()
        if "w" in mode or "+" in mode or "a" in mode:
            raise ResourceReadOnly(path)

        _path = self.validatepath(path)
        if _path not in self._sizes:
            raise ResourceNotFound(path)
        # Use the returned dict, not self._data: a concurrent close() may
        # clear the attribute.
        data = self._ensure_decompressed()
        return io.BytesIO(data[_path])

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)


# Info-only archives ("ModelInfos.ssg", "*.minfo.ssg") hold small "IM6S"
# metadata stubs under the same paths as the real "FM6S" .edgemodel files.
def _is_info_only_ssg(ssg_path):
    basename = os.path.basename(ssg_path).lower()
    return basename == "modelinfos.ssg" or basename.endswith(".minfo.ssg")


def _ssg_priority(ssg_path, ssg_fs):
    """MultiFS priority: current content 0, id_magic 5 (superseded weapon
    revisions) -1, info-only stubs -2, so each only fills paths nothing
    better claims."""
    if _is_info_only_ssg(ssg_path):
        return -2
    if ssg_fs.id_magic == 5:
        return -1
    return 0


def find_ssg_files(game_root):
    """Every .ssg under `game_root`, case-insensitively."""
    for current_dir, _dirs, files in os.walk(game_root):
        for name in files:
            if name.lower().endswith(".ssg"):
                yield os.path.join(current_dir, name)


def find_ssg_keys_s3(client, bucket, prefix=""):
    """Every .ssg key under `prefix` in an S3-compatible bucket."""
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".ssg"):
                yield key


class HexnFS(MultiFS):
    """A game install as one filesystem (see the module doc). Archives that
    fail to mount are kept in `failed_ssgs`."""

    def __init__(self, game_root, auto_close=True):
        super().__init__(auto_close=auto_close)
        self.failed_ssgs = []
        # Set by from_s3(); None for a local instance.
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
            self.add_fs(ssg_path, ssg_fs, priority=_ssg_priority(ssg_path, ssg_fs))

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
        """Source the .ssg files from an S3-compatible bucket (R2 included).
        Same `prefix`/`include_loose` semantics as MTFW_FS.from_s3().
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
        # Keys are rooted under prefix; _display_path() strips it.
        self._s3_prefix = prefix.strip("/")

        opener = s3_opener(client, bucket)
        for ssg_key in sorted(find_ssg_keys_s3(client, bucket, prefix)):
            try:
                ssg_fs = SsgFS(ssg_key, opener=opener)
            except Exception as e:
                self.failed_ssgs.append((ssg_key, e))
                continue
            self.add_fs(ssg_key, ssg_fs, priority=_ssg_priority(ssg_key, ssg_fs))

        if include_loose:
            self.add_fs("<loose>", S3LooseFS(client, bucket, prefix))
        return self

    def skipped_archives(self):
        """(path relative to the game root, reason) for every .ssg that
        failed to mount. albam.vfs reports these when a root is added.
        """
        return [
            (self._display_path(path), str(exc) or type(exc).__name__)
            for path, exc in self.failed_ssgs
        ]

    def _display_path(self, ssg_path):
        """`ssg_path` relative to the game root, or to `prefix` on S3."""
        if self._s3_prefix is not None:
            if self._s3_prefix and ssg_path.startswith(self._s3_prefix + "/"):
                return ssg_path[len(self._s3_prefix) + 1:]
            return ssg_path
        return os.path.relpath(ssg_path, self.game_root).replace(os.sep, "/")

    def _owning_ssg_fs(self, path):
        self.check()
        _path = self.validatepath(path)
        _name, owner_fs = self.which(_path)
        return owner_fs if isinstance(owner_fs, SsgFS) else None

    def origin_of(self, path):
        """The .ssg `path` resolves to (as _display_path() gives it), or None
        for a loose or missing file.
        """
        owner_fs = self._owning_ssg_fs(path)
        if owner_fs is None:
            return None
        return self._display_path(owner_fs.ssg_path)

    # Unlike MultiFS's versions, skip a sub-fs that has `path` as a file
    # instead of failing: an archive and the loose files can disagree on
    # whether a name is a file or a directory.
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
