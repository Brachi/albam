"""
Self-contained tests for the Hexane Engine (RE:ORC) .ssg PyFilesystem2
adapter. `HexaneSsg` (structs/hexane_ssg.py) is a read-only Kaitai-generated
parser with no `_write` counterpart (unlike e.g. mtfw's Arc), so fixture
bytes are hand-built here (see _build_ssg_bytes) following structs/ssg.ksy
directly, rather than read from real game data - tests/data/ is gitignored
and never holds real game asset bytes anyway (see tests/mtfw/test_arc_fs_s3.py
for the same rationale).
"""
import os
import struct
import zlib

import pytest
from fs.errors import ResourceNotFound

from albam.engines.hexn.fs import HexnFS, SsgFS

SIZE_PADDING = 4


def _build_ssg_bytes(entries, size_padding=SIZE_PADDING, chunk_size=None, raw=False):
    """entries: list of (name, content) tuples. Packs `content` for every
    entry into one contiguous buffer (each entry padded up to a
    `size_padding` boundary, matching how SsgFS/the old SSGWrapper slice
    files back out of it), compressed as one or more independently
    zlib-compressed chunks of at most `chunk_size` uncompressed bytes each
    (defaults to the whole buffer in a single chunk).

    raw=True builds the no-chunk-table variant instead (real files exist
    with size_chunks_info == 0 - see SsgFS.__init__'s comment): the
    "compressed" blob is just the uncompressed buffer verbatim, and
    chunk_sizes is empty.
    """
    uncompressed = bytearray()
    file_infos = []  # (name, size)
    for name, content in entries:
        offset_in_buffer = len(uncompressed)
        uncompressed.extend(content)
        padding = (-len(content)) % size_padding
        uncompressed.extend(b"\x00" * padding)
        file_infos.append((name, len(content), offset_in_buffer))

    if raw:
        chunk_sizes = []
        compressed_chunks = bytes(uncompressed)
    else:
        chunk_size = chunk_size or (len(uncompressed) or 1)
        chunk_sizes = []
        compressed_chunks = bytearray()
        for start in range(0, len(uncompressed), chunk_size):
            raw_chunk = bytes(uncompressed[start:start + chunk_size])
            compressed = zlib.compress(raw_chunk)
            chunk_sizes.append(len(compressed))
            compressed_chunks.extend(compressed)
        if not uncompressed:
            chunk_sizes = []

    file_names = bytearray()
    name_offsets = []
    for name, _size, _offset in file_infos:
        name_offsets.append(len(file_names))
        file_names.extend(name.encode("ascii") + b"\x00")

    files_info_bytes = bytearray()
    for (name, size, _offset), name_offset in zip(file_infos, name_offsets):
        files_info_bytes.extend(struct.pack(
            "<IIIIIiII",
            0,              # ident
            name_offset,    # name_offset_rel
            size,           # size (uncompressed)
            0,              # reserved_01
            0,              # reserved_02
            0,              # file_type
            0,              # unk_01
            0,              # unk_02
        ))

    header = struct.pack(
        "<4sIIIIIII",
        b"\x06\x00\x00\x00",
        0,                                  # reserved_01
        len(files_info_bytes),              # size_files_info
        len(file_names),                    # size_file_names
        len(compressed_chunks),             # size_chunks_buffer
        0,                                  # reserverd_01
        len(chunk_sizes) * 4,               # size_chunks_info
        size_padding,
    )
    chunk_sizes_bytes = b"".join(struct.pack("<I", s) for s in chunk_sizes)

    return bytes(header) + bytes(files_info_bytes) + chunk_sizes_bytes + bytes(file_names) + bytes(
        compressed_chunks)


ENTRIES = [
    ("test/foo.matb", b"HELLO-MATERIAL-DATA"),
    ("test/bar.tex", b"WORLD"),
    ("baz.edgemodel", b"SOME-MESH-BYTES-" + os.urandom(64)),
]


@pytest.fixture
def ssg_bytes():
    return _build_ssg_bytes(ENTRIES)


def test_ssg_fs_reads_back_every_entry(tmp_path, ssg_bytes):
    ssg_path = tmp_path / "model.ssg"
    ssg_path.write_bytes(ssg_bytes)

    ssg_fs = SsgFS(str(ssg_path))
    for name, content in ENTRIES:
        assert ssg_fs.readbytes("/" + name) == content


def test_ssg_fs_listdir_reflects_directory_structure(tmp_path, ssg_bytes):
    ssg_path = tmp_path / "model.ssg"
    ssg_path.write_bytes(ssg_bytes)

    ssg_fs = SsgFS(str(ssg_path))
    assert sorted(ssg_fs.listdir("/test")) == ["bar.tex", "foo.matb"]
    assert ssg_fs.listdir("/") == ["test", "baz.edgemodel"] or set(
        ssg_fs.listdir("/")) == {"test", "baz.edgemodel"}


def test_ssg_fs_multiple_chunks_reassemble_correctly(tmp_path):
    ssg_path = tmp_path / "model.ssg"
    ssg_path.write_bytes(_build_ssg_bytes(ENTRIES, chunk_size=16))

    ssg_fs = SsgFS(str(ssg_path))
    for name, content in ENTRIES:
        assert ssg_fs.readbytes("/" + name) == content


def test_ssg_fs_no_chunk_table_reads_raw_buffer(tmp_path):
    """Real .ssg exist with size_chunks_info == 0 - buffer_chunks is the
    uncompressed data verbatim in that case, not zlib-compressed at all, so
    SsgFS must read it as raw bytes rather than running it through a
    chunk-decompression loop that has no chunks to iterate.
    """
    ssg_path = tmp_path / "model.ssg"
    ssg_path.write_bytes(_build_ssg_bytes(ENTRIES, raw=True))

    ssg_fs = SsgFS(str(ssg_path))
    for name, content in ENTRIES:
        assert ssg_fs.readbytes("/" + name) == content


def test_ssg_fs_missing_path_raises(tmp_path, ssg_bytes):
    ssg_path = tmp_path / "model.ssg"
    ssg_path.write_bytes(ssg_bytes)

    ssg_fs = SsgFS(str(ssg_path))
    with pytest.raises(ResourceNotFound):
        ssg_fs.readbytes("/does/not/exist.foo")


def test_ssg_fs_is_read_only(tmp_path, ssg_bytes):
    from fs.errors import ResourceReadOnly

    ssg_path = tmp_path / "model.ssg"
    ssg_path.write_bytes(ssg_bytes)

    ssg_fs = SsgFS(str(ssg_path))
    with pytest.raises(ResourceReadOnly):
        ssg_fs.openbin("/test/foo.matb", mode="w")


def test_hexn_fs_overlays_multiple_ssgs_and_loose_files(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.ssg").write_bytes(
        _build_ssg_bytes([("models/a.edgemodel", b"AAAA")]))
    (tmp_path / "b.ssg").write_bytes(
        _build_ssg_bytes([("models/b.edgemodel", b"BBBB")]))
    (tmp_path / "readme.txt").write_bytes(b"loose file")

    game_fs = HexnFS(str(tmp_path))
    assert not game_fs.failed_ssgs
    assert game_fs.readbytes("/models/a.edgemodel") == b"AAAA"
    assert game_fs.readbytes("/models/b.edgemodel") == b"BBBB"
    assert game_fs.readbytes("/readme.txt") == b"loose file"


def test_hexn_fs_loose_file_overrides_packed(tmp_path):
    (tmp_path / "a.ssg").write_bytes(
        _build_ssg_bytes([("models/a.edgemodel", b"PACKED")]))
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "a.edgemodel").write_bytes(b"LOOSE-OVERRIDE")

    game_fs = HexnFS(str(tmp_path))
    assert game_fs.readbytes("/models/a.edgemodel") == b"LOOSE-OVERRIDE"


def test_hexn_fs_missing_game_root_raises():
    from fs.errors import CreateFailed

    with pytest.raises(CreateFailed):
        HexnFS("/this/does/not/exist/at/all")


def test_hexn_fs_origin_of_packed_and_loose(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.ssg").write_bytes(
        _build_ssg_bytes([("models/a.edgemodel", b"AAAA")]))
    (tmp_path / "readme.txt").write_bytes(b"loose file")

    game_fs = HexnFS(str(tmp_path))
    assert game_fs.origin_of("/models/a.edgemodel") == "sub/a.ssg"
    assert game_fs.origin_of("/readme.txt") is None
    assert game_fs.origin_of("/nope/does/not/exist.foo") is None
