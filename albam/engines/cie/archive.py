"""Reading and writing RE4UHD archives.

Reading is the fs_root_loader below, which hands the VFS an LfsFS (see fs.py).
Writing is update_lfs(): an archive with some of its files replaced by what
albam exported, rebuilt and recompressed into a file the game can load.

Two containers are rebuilt - a .udas, which is what a model archive is, and a
.pack, which is what a texture archive is. A pack lives in its own archive
(ImagePack/ImagePackHD) rather than beside the model that uses it, so
replacing a texture repacks that archive and nothing else: the .tpl naming the
slot keeps pointing at the same pack id and index.

Compression is lfs_compress's, by way of lfs_decompress.xcompress_compress_re4hd:
chunks are LZX compressed, bar any that would grow, which the container can
flag as stored instead.
"""
import os
import struct

from .fs import LfsFS, pack_entry_extension, split_archive_name, udas_byte_order
from .lfs_decompress import xcompress_compress_re4hd, xcompress_decompress_re4hd
from .structs.lfs import Lfs
from .structs.pack import Pack
from .structs.udas import Udas
from ...registry import blender_registry

# The DAT block: a count, three unused words, then an offset and a
# 4-character extension per entry, then the entries themselves. Offsets are
# relative to the block, and entries are aligned.
DAT_HEADER_SIZE = 16
ENTRY_ALIGNMENT = 16
BLOCK_DESCRIPTOR_SIZE = 32
BLOCK_TABLE_OFFSET = 0x20
BLOCK_TYPE_DAT = 0
BLOCK_TERMINATOR = 0xFFFFFFFF

# A pack: an id, a file count, then a u4 offset per file. Each entry is a
# 16-byte header - the size of what follows, a word every shipped entry sets to
# 0xFFFFFFFF, the pack's own id split over two u2 fields, and a DDS flag -
# followed by the file's raw bytes (see structs/pack.ksy).
PACK_HEADER_SIZE = 8
PACK_ENTRY_HEADER_SIZE = 16
# Where a file's raw bytes go. Every one of the 644 uncompressed packs of an
# install starts the first file's bytes on a 128-byte boundary, at the smallest
# offset clearing the offset table, and 604 of them put every later file's
# bytes on one too - the other 40 leave a constant gap between entries instead.
# So this is both what a shipped layout looks like and what a rebuilt entry is
# laid out by.
PACK_DATA_ALIGNMENT = 128
DDS_MAGIC = b"DDS "


@blender_registry.register_fs_root_loader(app_id="re4uhd", extension="lfs")
def lfs_fs_root_loader(absolute_path):
    return LfsFS(absolute_path)


def _align(size, alignment=ENTRY_ALIGNMENT):
    return (size + alignment - 1) // alignment * alignment


def _read_payload(archive_path):
    """The decompressed payload of an .lfs, and what it holds."""
    lfs = Lfs.from_file(archive_path)
    lfs._read()
    payload = bytes(xcompress_decompress_re4hd(lfs.chunks))
    _stem, extension = split_archive_name(os.path.basename(archive_path))
    return payload, extension


def _build_dat_block(entries):
    """A DAT block from `entries`, a list of (extension, bytes).

    The offset table and the data are both rebuilt, so a replacement file may
    be any size, which an edited one generally is.
    """
    count = len(entries)
    body_start = _align(DAT_HEADER_SIZE + count * 8)

    body = bytearray()
    offsets = []
    for index, (_extension, data) in enumerate(entries):
        if index:
            # Padding goes between entries, never after the last one: the
            # final entry's length is whatever is left of the block, so
            # trailing padding would become part of that file.
            body += b"\x00" * (_align(len(body)) - len(body))
        offsets.append(body_start + len(body))
        body += data

    block = bytearray()
    block += struct.pack("<4I", count, 0, 0, 0)
    for entry_offset in offsets:
        block += struct.pack("<I", entry_offset)
    for extension, _data in entries:
        name = extension.encode("ascii", "replace")[:4]
        block += name + b"\x00" * (4 - len(name))
    block += b"\x00" * (body_start - len(block))
    return bytes(block) + bytes(body)


def _rebuild_udas(payload, replacements):
    """A UDAS with `replacements` ({entry name: bytes}) substituted.

    Everything before the first block is kept as-is: the signature words are
    not constant between archives and nothing here decodes them, so they are
    carried rather than rewritten. The block descriptors are updated, since
    the DAT block changes size and anything after it moves.
    """
    if udas_byte_order(payload) != "<":
        # The big-endian variant, or something that is not a UDAS at all (see
        # fs.udas_byte_order). Rewriting either through the little-endian
        # reader below would emit a container the game cannot load, silently.
        raise NotImplementedError(
            "this .udas is not the little-endian variant albam reads, so it cannot be "
            "written back - see albam.engines.cie.fs.udas_byte_order"
        )

    udas = Udas.from_bytes(payload)
    udas._read()
    header = udas.header
    data = header.data_blocks

    replaced = 0
    rebuilt = []
    for i, entry in enumerate(data.file_entries):
        extension = data.file_extension[i].ext
        # The suffix LfsFS numbered this entry with, which is the only name a
        # caller can have seen it under.
        suffix = f"_{i:03d}.{extension.lower() or 'null'}"
        data_bytes = bytes(entry.raw_data)
        for name, new_bytes in replacements.items():
            if name.lower().endswith(suffix):
                data_bytes = new_bytes
                replaced += 1
                break
        rebuilt.append((extension, data_bytes))
    if not replaced:
        raise ValueError(
            f"none of {sorted(replacements)} matched an entry in this archive - a "
            f"replacement is matched by the numbered name it was imported under"
        )

    block = _build_dat_block(rebuilt)

    descriptors = [[d.block_type, d.size, d.unused, d.offset] for d in header.blocks]
    data_offset = header.data_offset
    out = bytearray(payload[:data_offset])
    out += block

    # Blocks after the DAT one move with it. Their sizes are unchanged: only
    # the DAT block is rebuilt.
    #
    # The DAT block is descriptors[0], not "whichever descriptor has type 0" -
    # data_offset above is blocks[0].offset, so resizing a different
    # descriptor would describe bytes that are not there. Position is also
    # the rule every reader of this format follows (see structs/udas.ksy).
    shift = len(block) - header.file_size
    if descriptors[0][0] != BLOCK_TYPE_DAT:
        # Never seen, and the whole rebuild rests on it: data_offset,
        # file_size and the block written above all come from blocks[0].
        raise ValueError(
            f"the first block of this archive is type {descriptors[0][0]:#x}, not the DAT "
            f"block every reader of this format expects there"
        )
    descriptors[0][1] = len(block)
    for descriptor in descriptors[1:]:
        if descriptor[0] == BLOCK_TERMINATOR:
            continue
        if descriptor[3] > data_offset:
            descriptor[3] += shift

    for i, descriptor in enumerate(descriptors):
        struct.pack_into("<4I", out, BLOCK_TABLE_OFFSET + i * BLOCK_DESCRIPTOR_SIZE,
                         descriptor[0] & 0xFFFFFFFF, descriptor[1],
                         descriptor[2], descriptor[3])

    # Anything the original had after its DAT block - a sound block - carried
    # over unchanged.
    trailing_start = data_offset + header.file_size
    if trailing_start < len(payload):
        out += payload[trailing_start:]
    return bytes(out)


def _read_pack(payload):
    """The Pack in `payload`, with what the rebuild rests on checked first.

    An .lfs named for a container does not always hold one (see
    fs.LfsFS._split), and a payload that is not a pack can still read as one -
    a plausible count, offsets pointing anywhere. Each entry is carried over as
    the byte range between its own offset and the next one, so ascending,
    distinct offsets clearing the table are what makes that range the entry;
    saying so beats emitting a container built over nonsense.

    The file count is checked before the container is parsed at all: the
    generated reader reads one offset per file the count claims, so a payload
    claiming four billion of them would spin rather than fail.
    """
    if len(payload) < PACK_HEADER_SIZE:
        raise ValueError(
            f"this payload is {len(payload)} bytes, too short to be a pack's own header"
        )
    _pack_id, num_files = struct.unpack_from("<II", payload)
    if PACK_HEADER_SIZE + 4 * num_files > len(payload):
        raise ValueError(
            f"this payload claims {num_files} files, more than its {len(payload)} bytes "
            f"can hold an offset for, so it is not a pack"
        )

    pack = Pack.from_bytes(payload)
    pack._read()

    offsets = [entry.offset for entry in pack.file_entries]
    if not offsets:
        raise ValueError("this pack lists no files, so there is nothing to replace in it")
    table_end = PACK_HEADER_SIZE + 4 * len(offsets)
    if offsets[0] < table_end:
        raise ValueError(
            f"this pack puts its first file at {offsets[0]}, inside its own "
            f"{table_end}-byte offset table, so the payload is not a pack"
        )
    if sorted(set(offsets)) != offsets:
        raise ValueError(
            "this pack's offsets are not ascending and distinct, so a file does not "
            "run from its own offset to the next one and albam cannot rebuild it"
        )
    return pack


def _build_pack_entry(entry, data):
    """One pack entry: its 16-byte header, and `data`.

    Every header word but the size is the entry's own. `unk_00` is 0xFFFFFFFF
    in all 12416 entries of an install's uncompressed packs, and `unk_01` /
    `unk_02` are that pack's own id split over two u2 fields in every one of
    them - so neither is guessed here, both are simply kept.

    The DDS flag is kept too, and only cleared for a replacement that is not a
    DDS. A shipped pack never flags an entry that isn't one, but it does leave
    the flag clear over DDS bytes - 6650 of the 9882 such entries - so setting
    it from the replacement's own magic would rewrite what those entries say
    while nothing suggests the game reads it that way.
    """
    body = entry.data
    is_dds = body.is_dds if data[:4] == DDS_MAGIC else 0
    return struct.pack("<IIHHI", len(data), body.unk_00, body.unk_01, body.unk_02,
                       is_dds) + bytes(data)


def _pack_data_offset(end_of_previous):
    """Where the next entry goes for its raw bytes to land on
    PACK_DATA_ALIGNMENT, which is how a shipped pack lays one out."""
    aligned = _align(end_of_previous + PACK_ENTRY_HEADER_SIZE, PACK_DATA_ALIGNMENT)
    return aligned - PACK_ENTRY_HEADER_SIZE


def _assemble_pack(pack_id, bodies):
    """A whole pack payload from `bodies`, a list of (bytes, place aligned).

    A body already the size of the range it came from is placed where the
    previous one ended, which is where it was; one that outgrew that range is
    placed - and followed - by PACK_DATA_ALIGNMENT instead, and everything
    after it moves. A body placed last is never followed by padding: no shipped
    pack has bytes after its final file.
    """
    body_start = _pack_data_offset(PACK_HEADER_SIZE + 4 * len(bodies))
    body = bytearray()
    offsets = []
    for index, (data, place_aligned) in enumerate(bodies):
        offset = body_start + len(body)
        if place_aligned:
            body += b"\x00" * (_pack_data_offset(offset) - offset)
            offset = _pack_data_offset(offset)
        offsets.append(offset)
        body += data
        if place_aligned and index < len(bodies) - 1:
            end = offset + len(data)
            body += b"\x00" * (_pack_data_offset(end) - end)

    out = bytearray(struct.pack("<II", pack_id, len(bodies)))
    for offset in offsets:
        out += struct.pack("<I", offset)
    out += b"\x00" * (body_start - len(out))
    return bytes(out) + bytes(body)


def _rebuild_pack(payload, replacements):
    """A pack with `replacements` ({entry name: bytes}) substituted.

    A pack's entries carry no names either, so a replacement is matched by the
    numbered name albam exposed the entry under, the same way _rebuild_udas
    matches one - see fs.pack_entry_extension for the extension half of it.

    An entry keeps the byte range it occupies here - its own padding included -
    rather than being written out again from the parsed fields, both when
    nothing replaces it and when the replacement still fits. Only an entry that
    outgrew its range is laid out afresh, and only what follows that one moves.
    A pack is 400 textures where a mod changes one, and shipped packs do not all
    pad the same way (40 of the 644 uncompressed ones of an install leave a
    constant gap between entries rather than aligning each), so rebuilding every
    entry would rewrite an archive that only means to have one file substituted.
    """
    pack = _read_pack(payload)
    offsets = [entry.offset for entry in pack.file_entries]
    ends = offsets[1:] + [len(payload)]
    last = len(pack.file_entries) - 1

    bodies = []
    replaced = 0
    for index, entry in enumerate(pack.file_entries):
        original = payload[offsets[index]:ends[index]]
        suffix = f"_{index:03d}.{pack_entry_extension(entry)}"
        new_bytes = None
        for name, candidate in replacements.items():
            if name.lower().endswith(suffix):
                new_bytes = candidate
                break
        if new_bytes is None:
            bodies.append((original, False))
            continue
        replaced += 1
        rebuilt = _build_pack_entry(entry, new_bytes)
        if len(rebuilt) > len(original):
            bodies.append((rebuilt, True))
        else:
            # Padded back out to the range it came from so nothing after it
            # moves - except when it is the last entry, where nothing follows
            # it to hold in place and padding would be bytes after the final
            # file that no shipped pack has.
            padding = 0 if index == last else len(original) - len(rebuilt)
            bodies.append((rebuilt + b"\x00" * padding, False))

    if not replaced:
        raise ValueError(
            f"none of {sorted(replacements)} matched an entry in this pack - a "
            f"replacement is matched by the numbered name it was imported under"
        )
    return _assemble_pack(pack.pack_name, bodies)


@blender_registry.register_archive_writer(app_id="re4uhd", extension="lfs")
def update_lfs(archive_path, exported_vfiles, **options):
    """The archive at `archive_path`, with each exported file substituted for
    the entry it was imported from, compressed back into a whole .lfs.

    Entries in these containers have no names, only positions, so a
    replacement is matched by the numbered name albam imported it under (see
    fs.py) rather than by anything stored in the archive.
    """
    payload, extension = _read_payload(archive_path)
    replacements = {vfile.display_name: vfile.get_bytes() for vfile in exported_vfiles}

    if extension == ".udas":
        payload = _rebuild_udas(payload, replacements)
    elif extension == ".pack":
        payload = _rebuild_pack(payload, replacements)
    elif len(replacements) == 1 and extension not in (".dat", ".evd"):
        # A single-file archive: the payload is the file.
        payload = next(iter(replacements.values()))
    else:
        raise NotImplementedError(
            f"writing a {extension} archive isn't supported yet - only .udas and "
            f".pack containers and single-file archives"
        )

    return xcompress_compress_re4hd(payload)
