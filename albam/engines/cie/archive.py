"""Reading and writing RE4 UHD archives.

Reading is the fs_root_loader below, which hands the VFS an LfsFS (see fs.py).
Writing is update_lfs(): an archive with some of its files replaced by what
albam exported, rebuilt and recompressed into a file the game can load.

Nothing here compresses. The .lfs container flags each chunk as compressed or
stored and the game reads both, so albam writes stored chunks (see
lfs_decompress.xcompress_compress_re4hd). The archive is larger than the one
it replaces and otherwise equivalent.
"""
import os
import struct

from .fs import LfsFS, split_archive_name
from .lfs_decompress import xcompress_compress_re4hd, xcompress_decompress_re4hd
from .structs.lfs import Lfs
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
    be any size - which it will be, since albam writes triangle lists where
    the original used strips.
    """
    count = len(entries)
    body_start = _align(DAT_HEADER_SIZE + count * 8)

    body = bytearray()
    offsets = []
    for _extension, data in entries:
        offsets.append(body_start + len(body))
        body += data
        body += b"\x00" * (_align(len(body)) - len(body))

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
    shift = len(block) - header.file_size
    for descriptor in descriptors:
        if descriptor[0] == BLOCK_TERMINATOR:
            continue
        if descriptor[0] == BLOCK_TYPE_DAT:
            descriptor[1] = len(block)
        elif descriptor[3] > data_offset:
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
    elif len(replacements) == 1 and extension not in (".dat", ".pack", ".evd"):
        # A single-file archive: the payload is the file.
        payload = next(iter(replacements.values()))
    else:
        raise NotImplementedError(
            f"writing a {extension} archive isn't supported yet - only .udas "
            f"containers and single-file archives"
        )

    return xcompress_compress_re4hd(payload)
