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


# An id_magic 5 archive is laid out differently enough to need its own
# builder - see _build_ssg_v5_bytes.
V5_ALIGNMENT = 16


def _build_ssg_v5_bytes(entries, chunk_size=None):
    """Builds an id_magic 5 archive (see structs/ssg.ksy): every entry
    located by its own `file_info.ofs_in_buffer_chunks` rather than by
    walking sizes, `size_padding` 0 and no chunk table, exactly as every
    real one is.

    `entries` are (name, content, file_type) tuples, `file_type` a 4-byte
    fourcc as it reads (b"MODL"), stored little-endian the way the format
    does. Entries are laid out 16-byte aligned, like the real ones, so the
    gaps that a sizes-only walk would swallow are genuinely there - a
    fixture whose entries happened to pack end to end would pass under
    either reading and prove nothing.

    `chunk_size` builds the chunk-compressed variant instead - not a
    layout any real id_magic 5 archive uses, and one SsgFS refuses (see
    SsgFS._check_v5_supported).
    """
    buffer_ = bytearray()
    file_infos = []  # (name, size, offset, file_type)
    for name, content, file_type in entries:
        offset = len(buffer_)
        buffer_.extend(content)
        buffer_.extend(b"\x00" * (-len(content) % V5_ALIGNMENT))
        file_infos.append((name, len(content), offset, file_type))

    if chunk_size:
        chunk_sizes = []
        chunks = bytearray()
        for start in range(0, len(buffer_), chunk_size):
            compressed = zlib.compress(bytes(buffer_[start:start + chunk_size]))
            chunk_sizes.append(len(compressed))
            chunks.extend(compressed)
    else:
        chunk_sizes = []
        chunks = bytes(buffer_)

    file_names = bytearray()
    files_info_bytes = bytearray()
    for name, size, offset, file_type in file_infos:
        files_info_bytes.extend(struct.pack(
            "<IIIIIiII",
            0,                                          # ident
            len(file_names),                            # name_offset_rel
            size,
            1,                                          # reserved_01
            offset,                                     # ofs_in_buffer_chunks
            int.from_bytes(file_type, "big"),           # file_type
            0,                                          # unk_01
            0,                                          # unk_02
        ))
        file_names.extend(name.encode("ascii") + b"\x00")

    header = struct.pack(
        "<IIIIIIII",
        5,                                  # id_magic
        0,                                  # reserved_01
        len(files_info_bytes),              # size_files_info
        len(file_names),                    # size_file_names
        len(chunks),                        # size_chunks_buffer
        0,                                  # reserverd_01
        len(chunk_sizes) * 4,               # size_chunks_info
        0,                                  # size_padding, always 0 here
    )
    chunk_sizes_bytes = b"".join(struct.pack("<I", s) for s in chunk_sizes)
    return (header + bytes(files_info_bytes) + chunk_sizes_bytes +
            bytes(file_names) + bytes(chunks))


ENTRIES = [
    ("test/foo.matb", b"HELLO-MATERIAL-DATA"),
    ("test/bar.tex", b"WORLD"),
    ("baz.edgemodel", b"SOME-MESH-BYTES-" + os.urandom(64)),
]

# Sized so no entry is a multiple of V5_ALIGNMENT, i.e. every one of them
# sits past where a sizes-only walk would look for it.
V5_ENTRIES = [
    ("weapons/models/gun.edgemodel", b"FM6S" + b"M" * 33, b"MODL"),
    ("weapons/surfaces/gun.matb", b"MAT\x07" + b"A" * 21, b"MATB"),
    ("weapons/textures/gun_d.dds", b"DDS ", b"TPKH"),
    ("weapons/textures/gun_d.dds", b"DDS |" + b"T" * 60, b"TPKD"),
]

# The other family carrying id_magic 5: cutscene/mocap streams, which
# SsgFS refuses rather than mounts - see SSG_V5_CONTENT_TYPES.
V5_MOCAP_ENTRIES = [
    ("StreamHeader", b"\x01\x00\x00\x00" + b"S" * 20, b"STMH"),
    ("MocapHeader", b"\x07\x00\x00\x00" + b"M" * 60, b"MCPH"),
    ("Tyrant", b"C" * 100, b"SANM"),
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


def test_ssg_v5_reads_every_entry_from_its_own_offset(tmp_path):
    """An id_magic 5 archive's entries are not packed end to end the way an
    id_magic 6 archive's are, so the sizes-only walk that reads one of
    those returns another entry's bytes here rather than failing - which is
    why they get read by file_info.ofs_in_buffer_chunks instead. Asserts
    both halves: the right bytes come back, and the walk really would have
    been wrong (a fixture that happened to pack end to end would pass under
    either reading).
    """
    ssg_bytes = _build_ssg_v5_bytes(V5_ENTRIES)
    ssg_path = tmp_path / "weapon.ssg"
    ssg_path.write_bytes(ssg_bytes)

    # What the sizes-only walk would have read for the last entry, taken
    # straight out of the stored (uncompressed) buffer, which this builder
    # leaves at the very end of the archive - the fixture is only
    # meaningful if the two readings really do disagree.
    size_buffer = sum(len(c) + (-len(c) % V5_ALIGNMENT) for _n, c, _t in V5_ENTRIES)
    buffer_ = ssg_bytes[len(ssg_bytes) - size_buffer:]
    walked = sum(len(c) for _n, c, _t in V5_ENTRIES[:-1])
    last_content = V5_ENTRIES[-1][1]
    assert buffer_[walked:walked + len(last_content)] != last_content

    ssg_fs = SsgFS(str(ssg_path))
    # The .dds is filed twice, as a TPKH stub and the real TPKD texture -
    # the later entry is the real one, exactly as in a real archive.
    assert ssg_fs.readbytes("/weapons/models/gun.edgemodel") == V5_ENTRIES[0][1]
    assert ssg_fs.readbytes("/weapons/surfaces/gun.matb") == V5_ENTRIES[1][1]
    assert ssg_fs.readbytes("/weapons/textures/gun_d.dds") == V5_ENTRIES[3][1]


def test_ssg_v5_refuses_content_types_it_does_not_model(tmp_path):
    """The cutscene/mocap archives sharing id_magic 5 parse just as cleanly
    as the weapon ones, so nothing about the header tells them apart -
    file_type does. Refusing beats mounting them: nothing here parses those
    streams, and their entry names repeat within one archive, so several
    entries would end up filed under one path.
    """
    from fs.errors import CreateFailed

    ssg_path = tmp_path / "cutscene.ssg"
    ssg_path.write_bytes(_build_ssg_v5_bytes(V5_MOCAP_ENTRIES))

    with pytest.raises(CreateFailed) as excinfo:
        SsgFS(str(ssg_path))
    assert "MCPH" in str(excinfo.value) and "SANM" in str(excinfo.value)
    assert "STMH" in str(excinfo.value)


def test_ssg_v5_refuses_a_chunk_compressed_archive(tmp_path):
    """ofs_in_buffer_chunks is a position in the *stored* buffer, so it only
    doubles as a position in the data while the archive is uncompressed -
    which every real id_magic 5 archive is. A compressed one would slice
    the wrong bytes out silently, so it is refused instead.
    """
    from fs.errors import CreateFailed

    ssg_path = tmp_path / "compressed.ssg"
    ssg_path.write_bytes(_build_ssg_v5_bytes(V5_ENTRIES, chunk_size=32))

    with pytest.raises(CreateFailed) as excinfo:
        SsgFS(str(ssg_path))
    assert "compressed" in str(excinfo.value)


def test_hexn_fs_surfaces_skipped_archives(tmp_path):
    """A .ssg that can't be mounted is skipped so the other ~2000 still
    are - but it has to say so, or its files just silently aren't there.
    """
    (tmp_path / "weapon.ssg").write_bytes(_build_ssg_v5_bytes(V5_ENTRIES))
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "cutscene.ssg").write_bytes(_build_ssg_v5_bytes(V5_MOCAP_ENTRIES))

    game_fs = HexnFS(str(tmp_path))
    assert game_fs.readbytes("/weapons/models/gun.edgemodel") == V5_ENTRIES[0][1]

    skipped = game_fs.skipped_archives()
    assert len(skipped) == 1
    source, reason = skipped[0]
    assert source == "sub/cutscene.ssg"
    assert "MCPH" in reason


def test_hexn_fs_v5_archive_does_not_shadow_current_content(tmp_path):
    """The id_magic 5 archives on a real install hold a superseded revision
    of paths the current archives also carry (their .edgemodel is format
    version 15 against the shipped 17/18), so one must never win a shared
    path - while a path only it has still has to resolve.
    """
    (tmp_path / "aaa_weapon.ssg").write_bytes(_build_ssg_v5_bytes(
        [("weapons/models/gun.edgemodel", b"FM6S" + b"O" * 33, b"MODL"),
         ("weapons/models/only_here.edgemodel", b"FM6S" + b"U" * 21, b"MODL")]))
    (tmp_path / "zzz_current.ssg").write_bytes(
        _build_ssg_bytes([("weapons/models/gun.edgemodel", b"FM6S-CURRENT")]))

    game_fs = HexnFS(str(tmp_path))
    assert not game_fs.failed_ssgs
    assert game_fs.readbytes("/weapons/models/gun.edgemodel") == b"FM6S-CURRENT"
    assert game_fs.origin_of("/weapons/models/gun.edgemodel") == "zzz_current.ssg"
    assert game_fs.readbytes("/weapons/models/only_here.edgemodel") == b"FM6S" + b"U" * 21
