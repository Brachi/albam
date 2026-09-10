"""
PyFilesystem2 adapter for Hexane Engine (RE:ORC) .ssg archives.

An .ssg bundles every file's bytes into one contiguous "solid" compressed
stream (see structs/ssg.ksy): fixed-size file-info entries record each
file's name and *uncompressed* size, but not its own compressed range -
only the whole `buffer_chunks` blob (itself split into independently
zlib-compressed chunks) decompresses to a stream that files are sliced out
of. That solid layout means - unlike ArcFS/PakFS, where openbin() seeks
straight to one entry's own compressed range - resolving any single file's
bytes means decompressing the *whole* archive's `buffer_chunks` together.
`SsgFS` defers that to the first file actually requested from a given
archive rather than doing it in __init__ (see `_ensure_decompressed()`) - a
real game install has ~2000 .ssg, and a typical session only ever touches a
handful of them.

Where in that stream a given entry lands depends on the archive's
`id_magic`: 6 slices them out sequentially, each padded up to
`size_padding`, while 5 gives every entry its own `ofs_in_buffer_chunks`
and is read by that instead (structs/ssg.ksy documents both layouts;
SSG_V5_CONTENT_TYPES below covers which id_magic 5 archives are mounted at
all).

`SsgFS` exposes a single .ssg as a read-only PyFilesystem2 filesystem;
`HexnFS` overlays every .ssg under a game root - plus loose files - into one
MultiFS, mirroring `albam.engines.mtfw.arc_fs.MTFW_FS`.

`SsgFS` also transparently handles `Animation/Projects/*.anims.ssg` (see
structs/anims.ksy) - a structurally-similar but big-endian, differently-
packed container - rather than that getting its own FS class: the
registry's `fs_root_loader_registry` is keyed by (app_id, extension), and
`.anims.ssg` shares the literal "ssg" extension with the regular,
little-endian format already registered here (archive.py), so there's no
second registry slot to hang a separate `AnimsFS` off of. `_parse_header()`
tries the regular little-endian `HexaneSsg` first (matches every real
non-anims .ssg) and only falls back to the big-endian `HexaneAnims` if
that raises (a big-endian archive can't be mistaken for a little-endian
one - `HexaneSsg` accepts an `id_magic` of only 5 or 6, and a big-endian
archive's own 5 or 6 reads back little-endian as 0x05000000/0x06000000).
Each clip entry is exposed as its own virtual leaf file, named
`<file_info.name>.animclip` - a synthetic extension (no real file on disk
ever has one) so the import registry can key an
`albam.engines.hexn.animation` import function off of it, the same way
every other importable leaf here is dispatched by extension.
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

# file_info.file_type is a fourcc stored as a little-endian word, so the
# readable tag is its big-endian view - see structs/ssg.ksy.
#
# The content types an id_magic 5 archive is read as. A full install's 130
# such archives (all under dlc/pack1/Weapons/) carry exactly these five and
# nothing else: MODL (.edgemodel), MATB (.matb), HAVK (.hkx), and the
# TPKH/TPKD pair a .dds is filed as - TPKH being a 4-byte stub holding just
# the "DDS " magic, TPKD the real texture under the same name.
#
# Mounting one makes its files readable, which is not the same as
# importable: their 108 .edgemodel entries are all format version 15, and
# structs/edgemodel.ksy models 17/18 (the only versions the current
# archives hold). Version 15 is a pre-existing gap, not one mounting these
# opens - 129 more of them are already reachable as loose files on disk,
# and parsing any of the 189 runs off the end of the file today. Their
# .matb/.dds/.hkx entries do read normally.
#
# An allowlist rather than a denylist because the offsets an id_magic 5
# archive is read by are only as trustworthy as the census that established
# them (see structs/ssg.ksy): a content type never seen in one gets refused
# and reported instead of mounted on the assumption it behaves like these.
# What it refuses today is the other id_magic 5 family - 5 archives under
# NIS/ holding cutscene/mocap streams (STMH, MCPH, SANM, SCAM, LAYO), which
# no part of albam parses and whose entry names repeat within one archive
# (31 entries under 7 names in one), so mounting them would file several
# entries' bytes under one path and serve whichever won.
SSG_V5_CONTENT_TYPES = frozenset({b"MODL", b"MATB", b"HAVK", b"TPKH", b"TPKD"})


def _local_opener(path):
    return open(path, "rb")


def _content_type(file_info):
    """`file_info.file_type` as its readable fourcc - the field is a signed
    word holding a fourcc stored little-endian, so the tag is its
    big-endian view (0x4d4f444c -> b"MODL"). See SSG_V5_CONTENT_TYPES."""
    return (file_info.file_type & 0xFFFFFFFF).to_bytes(4, "big")


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
    handful of them - constructing one doesn't mean decompressing every
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

        ssg, self._struct_cls, archive_size = self._parse_header()
        self._sizes = {}
        self._offsets = {}
        # Paths whose content is the whole raw file rather than a
        # buffer_chunks slice - see the file_type == 4 branch below.
        self._raw_file_paths = set()
        # dir path -> set of immediate child names; built directly instead
        # of via fs.memoryfs.MemoryFS - its makedirs()/create() per file
        # dominated SsgFS construction cost by far more than the actual
        # file read or Kaitai parse.
        self._dir_children = defaultdict(set)
        self._known_dirs = {"/"}
        offset = 0
        # HexaneAnims is the shared big-endian container both .anims.ssg
        # and the unrelated skel/*.ssg use structurally (same 32-byte
        # header/file-table/buffer_chunks shape - see structs/anims.ksy's
        # own doc) - file_info.file_type (5 for an animation clip, 4 for a
        # skeleton) distinguishes a clip entry from a skeleton one. Only a
        # real clip entry gets the synthetic ANIM_CLIP_EXTENSION suffix.
        #
        # A skeleton entry's own file_info.size/offset bookkeeping in this
        # outer container doesn't actually delimit skel.ksy's own payload,
        # though: skel.ksy models its own outer header starting from this
        # same file's absolute byte 0 (see structs/skel.ksy), overlapping
        # the very bytes this outer parse just consumed as its own header
        # - so a skeleton entry's real content is the whole raw file, not
        # a buffer_chunks slice (confirmed empirically: slicing per
        # file_info.size/offset here yields bytes that don't even start at
        # skel.ksy's own magic).
        is_be_container = self._struct_cls is HexaneAnims
        # This archive's own layout version, exposed for _ssg_priority() -
        # None for the big-endian container, whose id_magic is 5 or 6 too
        # but means nothing comparable (see structs/anims.ksy).
        self.id_magic = None if is_be_container else ssg.id_magic
        # An id_magic 5 archive stores each entry's own offset rather than
        # laying them out end to end, so the sequential walk below never
        # applies to it - see _check_v5_supported() and structs/ssg.ksy.
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
            # A raw entry's content is the whole archive (see the comment
            # above), so that is its size from the start - reporting
            # file_info.size until the first read and the real size after
            # would make getinfo() answer differently depending on whether
            # anything had been read yet.
            # A .dds is filed as a TPKH/TPKD pair sharing one entry name
            # (see SSG_V5_CONTENT_TYPES): the stub never wins the path off
            # the real texture, whichever order the two are stored in.
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
                # Both formats sharing the big-endian container pack their
                # entries with no padding at all, unlike the regular
                # little-endian format's size_padding-driven gaps (see
                # structs/anims.ksy). An id_magic 5 archive looks unpadded
                # by the same test - it carries size_padding == 0 - while
                # really padding to 16, which is why it is read by its own
                # stored offsets instead of by this walk.
                padding = (0 if is_be_container or not ssg.size_padding
                           else -file_info.size % ssg.size_padding)
                offset += file_info.size + padding

        self._data = None  # populated lazily - see _ensure_decompressed()
        self._decompress_lock = threading.Lock()

    def _check_v5_supported(self, ssg):
        """Refuse an id_magic 5 archive this reader has no evidence it can
        serve correctly, before any of it is exposed as files.

        Every condition below holds for every id_magic 5 archive on a full
        install (135 of them, 881 entries), and each one failing would mean
        `file_info.ofs_in_buffer_chunks` no longer points where this class
        reads from:

        * `size_chunks_info` == 0, i.e. `buffer_chunks` is stored
          uncompressed. That offset is a position in the *stored* buffer;
          for a chunk-compressed archive it is a zlib chunk boundary rather
          than a position in the decompressed stream (see structs/ssg.ksy),
          so it would slice the wrong bytes out.
        * every entry's `file_type` is one of SSG_V5_CONTENT_TYPES, which is
          what tells the model-data family apart from the cutscene/mocap one
          sharing this id_magic - see that constant.
        * no entry runs past the end of `buffer_chunks`. Slicing one that
          does yields short bytes with nothing raised, i.e. the wrong
          content served silently.

        Raises rather than mounting what it can: `HexnFS` collects the
        failure per-archive and surfaces it (see HexnFS.skipped_archives()),
        so an archive left out says so instead of just going missing.
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
        """Open the archive and read everything up to (not including)
        `buffer_chunks`, which is a lazily-computed Kaitai instance: it
        only seeks/reads its own region of the stream when something
        actually accesses `ssg.buffer_chunks`, and stays untouched
        otherwise. Returns the still-open file handle along with the
        parsed struct - the caller owns closing it, and must do so only
        after it's done touching anything that isn't a plain seq field
        (buffer_chunks itself; file_info.name is also a lazy instance, but
        _parse_header() below avoids it entirely).
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
        """Parse just the header + file table (names + sizes) - cheap even
        for a large, heavily-compressed .ssg, since `buffer_chunks` (the
        actual bulk of the archive) is never touched here.

        Names are sliced directly out of ssg.file_names (already a fully-
        read bytes value) instead of via file_info.name, a lazy Kaitai
        instance that would otherwise re-seek the stream per file - a real
        cost across a real install's ~2000 archives and ~40k files.

        Tries the regular little-endian HexaneSsg first (every real
        non-anims .ssg); HexaneAnims (big-endian - see this module's own
        doc) only on failure, since that's the rare case (a small minority
        of real .ssg archives). Returns (ssg, struct_cls) - the caller
        needs struct_cls again for _ensure_decompressed().
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
        """Decompress the whole archive once, on the first read of any file
        in it, and keep the result for the life of this instance. Returns
        the cache dict directly - see openbin()'s own comment on why a
        caller should read from that return value, not self._data again.

        The cache is built locally and published at the end: a failure
        part-way through (a corrupt chunk, a truncated read) would
        otherwise leave a non-None, half-filled cache behind, and every
        later read of this archive would raise KeyError for a file that is
        perfectly readable rather than retrying or reporting the real
        error. The lock keeps two threads from doing the work twice or
        from seeing the cache mid-build, which is what this class's own
        _meta["thread_safe"] promises.

        Memory: the archives here decompress to 8.7 GB across a whole
        install, hundreds of MB for the largest single one, and nothing
        evicts. Reading one small file out of a big archive therefore
        holds that archive's whole uncompressed size until the FS instance
        goes away - close() drops it.
        """
        with self._decompress_lock:
            if self._data is not None:
                return self._data
            data = {}

            # A skeleton entry's content is the whole raw file (see
            # __init__'s own comment on _raw_file_paths) - read it directly
            # rather than through the outer container's buffer_chunks
            # slicing, which this file only coincidentally also parses as.
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
                        # No chunk table (size_chunks_info == 0): buffer_chunks
                        # is stored raw, not zlib-compressed - zlib.decompress
                        # on it fails outright, an entry's expected magic reads
                        # correctly straight out of it at its computed offset,
                        # and the total size every files_info entry needs
                        # matches size_chunks_buffer exactly. Always the case
                        # for HexaneAnims too (see this module's own doc).
                        uncompressed = buffer_chunks
                finally:
                    f.close()

                for path in remaining:
                    offset = self._offsets[path]
                    data[path] = bytes(uncompressed[offset:offset + self._sizes[path]])

            self._data = data
            return data

    def close(self):
        """Drop the decompressed archive (see _ensure_decompressed) along
        with the usual fs.base.FS teardown, so a caller done with an
        archive isn't holding its uncompressed bytes."""
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
        # Read from _ensure_decompressed()'s own return value, not
        # self._data again: a concurrent close() between the two statements
        # (this class declares _meta["thread_safe"] = True) could otherwise
        # null self._data out from under this line. The returned dict is
        # the same object close() would drop, so holding this local
        # reference to it keeps it alive for this call regardless.
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


# A real RE:ORC install ships two families of info-only .ssg archives -
# per-pack "ModelInfos.ssg" (4 on a full install) and per-level
# "<name>.minfo.ssg" (36) - each holding small per-model metadata records
# (distinct magic "IM6S", ~1-2KB) filed under the *same* virtual paths as
# the real, full-geometry .edgemodel files (magic "FM6S") that live in
# separate content archives - e.g. dlc/pack1/Characters/ModelInfos.ssg has
# an "IM6S" stub at .../<model>.edgemodel, while the real ~1.2MB "FM6S"
# mesh for that same path lives in dlc/pack1/Characters/<model>.ssg.
# Nothing in this codebase parses the "IM6S" format - see _ssg_priority().
# A random 300-archive sample of the full install found no third pattern
# of info-only archive beyond these two.
def _is_info_only_ssg(ssg_path):
    basename = os.path.basename(ssg_path).lower()
    return basename == "modelinfos.ssg" or basename.endswith(".minfo.ssg")


def _ssg_priority(ssg_path, ssg_fs):
    """MultiFS priority for one discovered .ssg (see HexnFS.__init__).

    Current-content archives share the default priority (0), resolved by
    MultiFS's own reverse-add-order tie-break - fine on its own, except
    two kinds of archive re-use the very same virtual paths and would
    otherwise shadow the real thing depending on nothing but where they
    sorted:

    * an info-only archive (see _is_info_only_ssg() above), whose entry at
      a shared path is a tiny "IM6S" metadata stub rather than the mesh.
      Confirmed on a real install: without this ordering, across the 4
      ModelInfos.ssg archives alone, 103 of 171 virtual paths they share
      with a real content archive would resolve to the wrong stub (the 36
      per-level .minfo.ssg archives add more of the same, unquantified).
    * an id_magic 5 archive, which holds a superseded revision of what it
      shares with the current archives - the 130 on a real install are all
      per-weapon copies under dlc/pack1/Weapons/, and where one shares a
      path with the shipped aggregate dlc/pack1/Weapons/weapons.ssg, its
      .edgemodel is format version 15 against that one's 17/18. Left at
      the same priority they win 141 of the 469 virtual paths they claim,
      29 of those .edgemodel paths that resolve to a version-18 mesh
      today - a straight downgrade of what is already there.

    Ordering them strictly below current content means one only ever
    resolves a path no higher-priority archive already claims, so nothing
    that resolves today changes and a path that exists *only* in one still
    resolves instead of disappearing. id_magic 5 outranks info-only in
    turn: both can claim the same path, and a superseded-but-real mesh
    beats a metadata stub.
    """
    if _is_info_only_ssg(ssg_path):
        return -2
    if ssg_fs.id_magic == 5:
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
            self.add_fs(ssg_key, ssg_fs, priority=_ssg_priority(ssg_key, ssg_fs))

        if include_loose:
            # added last -> highest default priority -> wins over packed archives
            self.add_fs("<loose>", S3LooseFS(client, bucket, prefix))
        return self

    def skipped_archives(self):
        """(path relative to the game root, reason) for every .ssg found
        under it that could not be mounted - the readable form of
        `failed_ssgs`.

        Construction deliberately keeps going past an archive it can't
        read, so one unreadable .ssg out of ~2000 doesn't cost the user
        every other one. Nothing said so, though: the failures were
        collected here and never read by anything, leaving a silently
        incomplete tree - files simply absent, with no hint they were ever
        there. albam.vfs surfaces this list when a root is added (see
        skipped_source_warnings() there); the same shape works for any FS
        that overlays many sources.
        """
        return [
            (self._display_path(path), str(exc) or type(exc).__name__)
            for path, exc in self.failed_ssgs
        ]

    def _display_path(self, ssg_path):
        """`ssg_path` as origin_of() would report it - relative to the game
        root locally, to `prefix` for a from_s3() instance."""
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
        """The .ssg `path` resolves to - its own path relative to game_root
        for a local instance, or relative to `prefix` for a
        HexnFS.from_s3() instance (forward slashes either way) - or None if
        it's a loose/real file (or doesn't resolve at all). Mirrors
        albam.engines.mtfw.arc_fs.MTFW_FS.origin_of(). No index/caching like
        MTFW_FS's - a real install here has ~2000 .ssg, so a linear which()
        scan per lookup is fine.
        """
        owner_fs = self._owning_ssg_fs(path)
        if owner_fs is None:
            return None
        return self._display_path(owner_fs.ssg_path)

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
