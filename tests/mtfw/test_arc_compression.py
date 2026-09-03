"""The two things that differ between an .arc's versions: how an entry's
payload is compressed, and which table names its file type.

Nothing here needs game data. The stream these tests decode is built by
hand out of one uncompressed LZX block, which exercises the frame header,
the block header and the bit reader's alignment, but not the Huffman path -
that is what the dataset-driven tests over real archives cover.
"""
import struct
import zlib

import pytest

from albam.engines.mtfw import FILE_ID_TO_EXTENSION, FILE_ID_TO_EXTENSION_DMC4
from albam.engines.mtfw.archive import update_arc
from albam.engines.mtfw.arc_fs import (
    ARC_VERSION_DMC4,
    decompress_entry,
    file_type_extensions,
)
from albam.lib.xcompress import xmem_decompress

ARC_VERSION_ZLIB = 7


def stored_frame(payload, first=True):
    """An XMemCompress frame holding `payload` in one uncompressed block.

    Only the first frame of a stream carries the x86 call-transform header
    bit, so `first` decides whether it is written; either way the block
    header pads out to the same 16-bit boundary the reader aligns to.
    """
    bits = []

    def put(value, num_bits):
        for i in range(num_bits - 1, -1, -1):
            bits.append((value >> i) & 1)

    if first:
        put(0, 1)  # no x86 call transform
    put(3, 3)  # LZX_BLOCKTYPE_UNCOMPRESSED
    put(len(payload), 24)
    put(0, 4 if first else 5)

    body = bytearray()
    for i in range(0, len(bits), 16):
        word = 0
        for bit in bits[i:i + 16]:
            word = (word << 1) | bit
        body += struct.pack("<H", word)
    for _ in range(3):  # the three match offsets, low half first
        body += struct.pack("<HH", 1, 0)
    body += payload
    return b"\xff" + struct.pack(">HH", len(payload), len(body)) + bytes(body)


def test_stored_frame_decodes():
    payload = bytes(range(256)) * 3 + b"albam"
    assert xmem_decompress(stored_frame(payload), len(payload)) == payload


def test_consecutive_frames_concatenate():
    first, second = b"a" * 100, b"b" * 50
    stream = stored_frame(first) + stored_frame(second, first=False)
    assert xmem_decompress(stream, len(first) + len(second)) == first + second


def test_short_stream_raises():
    payload = b"albam" * 10
    with pytest.raises(RuntimeError):
        xmem_decompress(stored_frame(payload), len(payload) + 1)


def test_decompress_entry_picks_the_codec_by_version():
    payload = b"albam" * 40
    assert decompress_entry(ARC_VERSION_ZLIB, zlib.compress(payload), len(payload)) == payload
    assert decompress_entry(
        ARC_VERSION_DMC4, stored_frame(payload), len(payload)) == payload


def test_file_type_extensions_picks_the_table_by_version():
    assert file_type_extensions(ARC_VERSION_ZLIB) is FILE_ID_TO_EXTENSION
    assert file_type_extensions(ARC_VERSION_DMC4) is FILE_ID_TO_EXTENSION_DMC4


def test_the_two_tables_number_the_same_types_differently():
    """The ids are a hash of the same resource class names either way, but
    not the same hash - so a table lookup is only meaningful against the
    version that produced the id."""
    for extension in ("mod", "tex", "lmt", "sbc"):
        shared = [k for k, v in FILE_ID_TO_EXTENSION.items() if v == extension]
        dmc4 = [k for k, v in FILE_ID_TO_EXTENSION_DMC4.items() if v == extension]
        assert len(shared) == 1 and len(dmc4) == 1, extension
        assert shared[0] != dmc4[0], extension
        assert FILE_ID_TO_EXTENSION.get(dmc4[0]) is None, extension


def test_writing_refuses_an_archive_it_can_only_read(tmp_path):
    """albam has a decoder for these entries but no encoder, so packing into
    one has to fail rather than write an archive the game cannot read."""
    path = tmp_path / "test.arc"
    # the smallest well-formed .arc: a header, no entries, and the padding
    # arc.ksy expects before what would be the first payload
    path.write_bytes(struct.pack("<4shh", b"ARC\x00", ARC_VERSION_DMC4, 0) + b"\x00" * 32760)

    with pytest.raises(ValueError, match="cannot be written back"):
        update_arc(str(path), [])
