"""
PyFilesystem2 adapter for RE4UHD .lfs archives.

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
have one: a real RE4UHD install ships ~4500 .lfs archives, and mounting
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
  Two .udas archives of an install are a big-endian variant whose DAT block
  is YZ2 compressed (see yz2.py); they are listed the same way.
- evd entries do carry names, nested paths included ("event/r332/s20/cam/
  cam_s20_000.fcv"), and are exposed under them.
- every other extension (bin, rel, tpl, fix, fnt, esl, fcv, tga, eff, uwf)
  is a single file compressed on its own, exposed as "<stem>.<ext>".
"""
import io
import os
import struct
from collections import defaultdict

from fs.base import FS
from fs.enums import ResourceType
from fs.errors import CreateFailed, ResourceNotFound, ResourceReadOnly
from fs.info import Info
from kaitaistruct import KaitaiStream

from . import lfs_decompress, yz2
from .structs.dat import Dat
from .structs.evd import Evd
from .structs.lfs import Lfs
from .structs.pack import Pack
from .structs.udas import Udas
from .yz2 import YZ2_HEADER_SIZE

# Container extensions, mapped to the struct parsing that container's own
# decompressed bytes. Anything not listed here is a single file compressed
# on its own (see this module's docstring).
CONTAINER_STRUCTS = {
    ".udas": Udas,
    ".dat": Dat,
    ".pack": Pack,
    ".evd": Evd,
}

# A UDAS's block table: eight signature words, then a 32-byte descriptor per
# block from 0x20 on, ending at one whose type is 0xFFFFFFFF (see
# structs/udas.ksy). Udas reads the descriptors little-endian; a variant
# writes them big-endian, which is what udas_byte_order() tells apart.
UDAS_BLOCK_TABLE_OFFSET = 0x20
UDAS_BLOCK_DESCRIPTOR_SIZE = 32
UDAS_BLOCK_TERMINATOR = 0xFFFFFFFF
# The big-endian variant's DAT block, once out of its YZ2 stream (see
# _split_big_endian_udas): an entry count, then the offset and extension
# tables either after three zero words or straight after it.
BIG_ENDIAN_DAT_TABLE_OFFSET = 0x10
BIG_ENDIAN_DAT_EARLY_TABLE_OFFSET = 0x04


def pack_entry_extension(entry):
    """The extension one pack entry is exposed under.

    A pack names nothing, so this and the entry's index are the whole of the
    name a caller ever sees it by (see LfsFS._split_container), which is also
    what the writer matches a replacement against (see
    albam.engines.cie.archive._rebuild_pack).

    The flag it reads is not a reliable statement about the bytes: 6650 of the
    9882 entries holding a DDS across the uncompressed packs of an install
    leave it clear, so a DDS is often exposed under a ".tga" name. Reader and
    writer agree on the name anyway by both asking here.
    """
    return "dds" if entry.data.is_dds else "tga"


def read_udas_block_table(payload, byte_order):
    """The block descriptors of `payload` as [(type, size, offset)], read in
    `byte_order` ("<" or ">"), or None when it holds no table in that order.

    A descriptor whose `unused` word is set, or whose block runs past the end
    of the payload, is what says the order is the wrong one: read the other
    way round, the words of a real table come out as huge values that fail
    both checks (verified across every .udas archive of an install, each of
    which reads as a table in exactly one order, bar a handful whose second
    order happens to be valid too).
    """
    blocks = []
    offset = UDAS_BLOCK_TABLE_OFFSET
    while offset + UDAS_BLOCK_DESCRIPTOR_SIZE <= len(payload):
        block_type, size, unused, block_offset = struct.unpack_from(
            byte_order + "4I", payload, offset)
        offset += UDAS_BLOCK_DESCRIPTOR_SIZE
        if block_type == UDAS_BLOCK_TERMINATOR:
            return blocks or None
        if unused or not offset <= block_offset <= len(payload):
            return None
        if size > len(payload) - block_offset:
            return None
        blocks.append((block_type, size, block_offset))
    return None


def udas_byte_order(payload):
    """The byte order a UDAS's block table is written in - "<" or ">" - or
    None for a payload that holds no block table at all.

    The eight repeated words in front of the table are not a byte-order mark,
    despite reading as one value or its byte-reverse: both values occur in
    archives whose fields are little-endian, and no reader validates them.
    The table itself is the only thing that says which order an archive uses.
    """
    for byte_order in ("<", ">"):
        if read_udas_block_table(payload, byte_order):
            return byte_order
    return None


def is_yz2_block(payload, offset):
    """Whether the block at `offset` is a YZ2 compressed stream rather than a
    file table, which is what a big-endian UDAS holds its DAT block as."""
    return yz2.parse_header(payload[offset:offset + YZ2_HEADER_SIZE]) is not None


def split_big_endian_dat(block):
    """[(index, extension, bytes)] for the entries of a big-endian DAT block,
    the file table the big-endian UDAS variant holds YZ2 compressed. `index`
    is the entry's position in the table, which is what it is named by.

    Two layouts occur, told apart the way JADERLINK's RE4_DASYZ2_TOOL does:
    the final game's, where three zero words follow the count before the
    tables start (as in the little-endian DAT), and an earlier one (the tool
    calls it the E3 version) where the tables follow the count directly.

    The one archive in the earlier layout also names entries it does not
    hold. Its table opens with three entries whose extensions carry stray
    high bytes ("CA\xe1\x80", "SA\xe8\x80", "LI\xe8\x80"), and their data
    is not in the block: every entry after them sits earlier than its offset
    says, by exactly the span the three would have taken. Read that way, each
    entry opens the way the same type does in the final-layout archive (an
    .eff and a .tex byte for byte, an .aev with its magic), the entries run
    exactly to the end of the block, and most end in the same 0xCD padding;
    taken at face value, the block would end partway through an entry with
    eight more placed past it. So an entry with a damaged extension is
    taken as a leftover of the table: it is not listed, and its span is
    subtracted from every offset after it. That rule rests on this one
    archive; every other DAT seen has clean extensions, which leaves them
    untouched by it.
    """
    count, *words = struct.unpack_from(">4I", block, 0)
    table_offset = BIG_ENDIAN_DAT_EARLY_TABLE_OFFSET if any(words) else BIG_ENDIAN_DAT_TABLE_OFFSET
    if table_offset + count * 8 > len(block):
        raise ValueError(f"a DAT block of {len(block)} bytes cannot hold {count} entries")
    offsets = struct.unpack_from(f">{count}I", block, table_offset)
    names_offset = table_offset + count * 4
    names = [block[names_offset + i * 4:names_offset + i * 4 + 4] for i in range(count)]

    kept = []
    missing = 0
    for i, (offset, name) in enumerate(zip(offsets, names)):
        extension = name.rstrip(b"\x00")
        if not (extension.isascii() and (extension.isalnum() or not extension)):
            missing += offsets[i + 1] - offset if i + 1 < count else 0
            continue
        kept.append((i, extension.decode("ascii"), offset - missing))

    entries = []
    for k, (i, extension, start) in enumerate(kept):
        end = kept[k + 1][2] if k + 1 < len(kept) else len(block)
        if not 0 <= start <= end <= len(block):
            raise ValueError(f"DAT entry {i} lies outside its {len(block)}-byte block")
        entries.append((i, extension, block[start:end]))
    return entries


def _udas_read_error(payload):
    """Why this UDAS payload cannot be listed, as an exception, or None when
    nothing more specific than the parser's own error can be said."""
    byte_order = udas_byte_order(payload)
    if byte_order is None:
        return ValueError(
            "no UDAS block table reads out of this payload in either byte order, so "
            "the archive holds something other than the container its name claims"
        )
    if byte_order == "<":
        return None
    data_offset = read_udas_block_table(payload, byte_order)[0][2]
    if is_yz2_block(payload, data_offset):
        # Only reached when decoding it failed (see LfsFS._split).
        return None
    return NotImplementedError(
        "this is the big-endian UDAS variant, and its data block is not the YZ2 "
        "stream every one seen holds, so albam does not know how to read it"
    )


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
    """Read-only PyFilesystem2 view of a single RE4UHD .lfs archive.

    `lfs_path` is a local path. Unlike ArcFS and SsgFS there is no opener
    hook to read one from S3: those read a header over a range request and
    fetch only what is touched, while an .lfs has to be decompressed whole
    before anything in it can be listed, so reading one remotely would
    fetch the entire object anyway. The tests download instead (see
    tests/cie/conftest.py).

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

        handle = open(self.lfs_path, "rb")
        try:
            lfs = Lfs(KaitaiStream(handle))
            lfs._read()
            decompressed = bytes(lfs_decompress.xcompress_decompress_re4hd(lfs.chunks))
        finally:
            handle.close()

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
        # install has archives it is wrong about: one named for a container
        # holds a plain table instead, and reads as a container claiming ten
        # million files. Falling back to the whole payload as a single file keeps such
        # an archive mountable and readable (which is all the VFS needs of it)
        # instead of failing to mount at all. The entry reads are inside the
        # same guard because they're lazy: a container whose header parses can
        # still turn out not to be one when an entry's own offset/size is read.
        try:
            if struct_cls is Udas and udas_byte_order(decompressed) == ">":
                return self._split_big_endian_udas(decompressed)
            container = struct_cls.from_bytes(decompressed)
            container._read()
            return self._split_container(struct_cls, container, decompressed)
        except Exception as error:
            if struct_cls is Udas:
                # Two variants don't read as the little-endian UDAS: one
                # whose block table is big-endian (read above, so only here
                # when that failed), and one holding no block table at all.
                # Saying which beats handing on the parser's own error, which
                # only ever reports running off the end of the payload.
                error = _udas_read_error(decompressed) or error
            self.container_error = error
            return single_file

    def _split_big_endian_udas(self, decompressed):
        """The entries of the big-endian UDAS variant: its block table read
        big-endian, and its DAT block decompressed out of YZ2 and read
        big-endian too (see split_big_endian_dat).

        Only two archives of an install are this variant, and each holds a
        single block. Entries are named the way the little-endian container's
        are. Their contents are big-endian as well (an .smd's floats, for
        one), so listing and reading them is as far as albam goes: the
        importers expect the little-endian formats the rest of the game uses.
        """
        _block_type, size, offset = read_udas_block_table(decompressed, ">")[0]
        if not is_yz2_block(decompressed, offset):
            raise _udas_read_error(decompressed)
        block = yz2.decompress(decompressed[offset:offset + size])
        return {
            f"/{self._stem}_{i:03d}.{extension.lower() or 'null'}": data
            for i, extension, data in split_big_endian_dat(block)
        }

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
                extension = pack_entry_extension(entry)
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
