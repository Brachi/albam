"""
Writing RE4UHD texture packs - albam.engines.cie.archive._rebuild_pack, and
update_lfs dispatching to it.

A pack is the archive a model's textures actually live in: a .tpl entry names
a pack id and an index into it, and the pack is a separate .lfs under
ImagePack / ImagePackHD (see albam/engines/cie/textures.py). Replacing a
texture therefore rebuilds that pack and nothing else - the .tpl keeps
pointing at the same pack id and the same index.

The first half of this file builds packs by hand and needs no game data. The
second half rebuilds real ones, which needs --game-dir.
"""
import json
import os
import struct

import pytest

from albam.engines.cie.archive import (PACK_DATA_ALIGNMENT, PACK_ENTRY_HEADER_SIZE,
                                       PACK_HEADER_SIZE, _rebuild_pack)
from tests.cie.lfs_paths import resolve_archive_hashes

# The .pack archives of the shared parsing dataset - already verified against
# the committed catalog by tests/cie/test_lfs_fs.py, which is where that
# dataset and its guard live. One is a plain "*.pack.lfs" and one a
# "*.pack.yz2.lfs", whose payload is a plain pack too (see
# albam.engines.cie.fs).
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
with open(os.path.join(DATASETS_DIR, "lfs_parsing_hashes.json")) as f:
    PACK_DATASET = [d for d in json.load(f) if d["payload_extension"] == ".pack"]

# Payloads albam would never have to decode: the writer copies a replacement's
# bytes through without reading them.
FAKE_DDS = b"DDS " + b"\x7f" * 220
FAKE_TGA = b"\x00\x00\x02\x00" + b"\x11" * 180


def _build_pack(pack_id, files):
    """A pack payload holding `files`, a list of (bytes, DDS flag).

    Written here rather than with the writer under test, and laid out the way
    every shipped pack lays out its first file and 604 of the 644 uncompressed
    packs of an install lay out all of them: each file's raw bytes start on a
    PACK_DATA_ALIGNMENT boundary. The header words the writer carries over are
    given the values every shipped entry has - 0xFFFFFFFF, and the pack's own
    id split over two u2 fields.
    """
    def data_offset(end_of_previous):
        unaligned = end_of_previous + PACK_ENTRY_HEADER_SIZE
        aligned = -(-unaligned // PACK_DATA_ALIGNMENT) * PACK_DATA_ALIGNMENT
        return aligned - PACK_ENTRY_HEADER_SIZE

    offsets = []
    bodies = bytearray()
    body_start = data_offset(PACK_HEADER_SIZE + 4 * len(files))
    for index, (data, is_dds) in enumerate(files):
        offset = body_start + len(bodies)
        offsets.append(offset)
        bodies += struct.pack("<IIHHI", len(data), 0xFFFFFFFF,
                              pack_id & 0xFFFF, pack_id >> 16, is_dds) + data
        if index < len(files) - 1:
            end = offset + PACK_ENTRY_HEADER_SIZE + len(data)
            bodies += b"\x00" * (data_offset(end) - end)

    header = bytearray(struct.pack("<II", pack_id, len(files)))
    for offset in offsets:
        header += struct.pack("<I", offset)
    header += b"\x00" * (body_start - len(header))
    return bytes(header) + bytes(bodies)


def _entries(payload):
    """[(name, bytes)] for a pack payload, named the way the VFS names its
    entries - which is what a replacement is matched against."""
    from albam.engines.cie.fs import pack_entry_extension
    from albam.engines.cie.structs.pack import Pack

    pack = Pack.from_bytes(payload)
    pack._read()
    return [(f"{pack.pack_name:08x}_{i:03d}.{pack_entry_extension(entry)}",
             bytes(entry.data.raw_data))
            for i, entry in enumerate(pack.file_entries)]


@pytest.fixture
def pack():
    """A three-file pack: a DDS flagged as one, a DDS left unflagged (which is
    how 6650 of the 9882 DDS entries of an install ship), and a TGA."""
    return _build_pack(0x0D104000, [(FAKE_DDS, 1), (FAKE_DDS + b"\x01" * 64, 0),
                                    (FAKE_TGA, 0)])


def test_a_handbuilt_pack_reads_back(pack):
    """The fixture is only worth testing the writer against if the reader
    agrees it is a pack, since the reader is what a mod is judged by."""
    assert [name for name, _data in _entries(pack)] == [
        "0d104000_000.dds", "0d104000_001.tga", "0d104000_002.tga"]


def test_rebuilding_unchanged_is_byte_for_byte_identical(pack):
    """Handing one entry back unchanged gives the pack that went in.

    Nothing may drift when a mod replaces one texture of the four hundred a
    pack can hold, so the identity case is exact rather than merely
    equivalent.
    """
    name, data = _entries(pack)[1]
    assert _rebuild_pack(pack, {name: data}) == pack


def test_a_same_size_replacement_moves_nothing_else(pack):
    """A replacement that fits where the entry already sat leaves every other
    byte of the pack alone - offset table included."""
    before = _entries(pack)
    name, data = before[1]
    replacement = bytes(len(data))
    rebuilt = _rebuild_pack(pack, {name: replacement})

    assert len(rebuilt) == len(pack)
    assert struct.unpack_from("<3I", rebuilt, PACK_HEADER_SIZE) == \
        struct.unpack_from("<3I", pack, PACK_HEADER_SIZE)
    assert [d for _n, d in _entries(rebuilt)] == [before[0][1], replacement, before[2][1]]


def test_a_shorter_replacement_moves_nothing_else(pack):
    before = _entries(pack)
    name, data = before[1]
    replacement = data[:32]
    rebuilt = _rebuild_pack(pack, {name: replacement})

    assert struct.unpack_from("<3I", rebuilt, PACK_HEADER_SIZE) == \
        struct.unpack_from("<3I", pack, PACK_HEADER_SIZE)
    assert [d for _n, d in _entries(rebuilt)] == [before[0][1], replacement, before[2][1]]


def test_a_longer_replacement_shifts_only_what_follows_it(pack):
    """An entry that outgrew its range is laid out afresh and the entries after
    it move; the ones before it do not."""
    before = _entries(pack)
    name, data = before[1]
    replacement = data + b"\xab" * 4000
    rebuilt = _rebuild_pack(pack, {name: replacement})

    offsets_before = struct.unpack_from("<3I", pack, PACK_HEADER_SIZE)
    offsets_after = struct.unpack_from("<3I", rebuilt, PACK_HEADER_SIZE)
    assert offsets_after[0] == offsets_before[0]
    assert offsets_after[1] == offsets_before[1]
    assert offsets_after[2] > offsets_before[2]
    assert [d for _n, d in _entries(rebuilt)] == [before[0][1], replacement, before[2][1]]


def test_every_rebuilt_entry_starts_its_data_on_the_alignment(pack):
    """What 604 of the 644 uncompressed packs of an install do for every entry,
    and all 644 do for the first: a file's raw bytes begin on a
    PACK_DATA_ALIGNMENT boundary."""
    name, data = _entries(pack)[0]
    rebuilt = _rebuild_pack(pack, {name: data + b"\x00" * 5000})

    count = struct.unpack_from("<I", rebuilt, 4)[0]
    offsets = struct.unpack_from(f"<{count}I", rebuilt, PACK_HEADER_SIZE)
    assert [(o + PACK_ENTRY_HEADER_SIZE) % PACK_DATA_ALIGNMENT for o in offsets] == [0] * count


def test_the_last_entry_growing_leaves_no_trailing_bytes(pack):
    """No shipped pack has bytes after its final file, so a rebuilt one
    doesn't either."""
    entries = _entries(pack)
    name, data = entries[-1]
    for replacement in (data + b"\x22" * 3000, data[:16]):
        rebuilt = _rebuild_pack(pack, {name: replacement})
        count = struct.unpack_from("<I", rebuilt, 4)[0]
        last = struct.unpack_from(f"<{count}I", rebuilt, PACK_HEADER_SIZE)[-1]
        assert len(rebuilt) == last + PACK_ENTRY_HEADER_SIZE + len(replacement)


def test_the_dds_flag_is_always_carried_through_unchanged(pack):
    """The flag is the entry's own, whatever the replacement's bytes are: a
    shipped pack leaves it clear over DDS bytes just as often as it sets it, so
    the replacement never gets a say in it.

    Read back through the entry names, which is what the flag decides.
    """
    flagged, unflagged, tga = _entries(pack)
    names = [flagged[0], unflagged[0], tga[0]]

    for name, replacement in ((flagged[0], FAKE_DDS + b"\x03" * 8),
                              (unflagged[0], FAKE_DDS),
                              (flagged[0], FAKE_TGA)):
        rebuilt = _rebuild_pack(pack, {name: replacement})
        assert [n for n, _d in _entries(rebuilt)] == names


def test_a_replacement_is_matched_by_its_number_not_its_archive_name(pack):
    """A pack's entries carry no names, only positions, so the number albam
    exposed the entry under is the whole of the match - the stem in front of it
    is whichever archive it was read from, which a mod's own file need not
    repeat."""
    replacement = FAKE_TGA[:24]
    for name in ("0d104000_002.tga", "whatever_002.TGA"):
        assert _entries(_rebuild_pack(pack, {name: replacement}))[2][1] == replacement


def test_a_replacement_matching_nothing_is_an_error(pack):
    with pytest.raises(ValueError, match="matched an entry"):
        _rebuild_pack(pack, {"0d104000_009.dds": b""})
    # The right number, the extension the other flag would have given it.
    with pytest.raises(ValueError, match="matched an entry"):
        _rebuild_pack(pack, {"0d104000_000.tga": b""})


def test_a_payload_that_is_not_a_pack_is_refused():
    """An .lfs named for a container does not always hold one (see
    albam.engines.cie.fs.LfsFS._split), and the writer is handed the payload
    rather than the mounted files - so it says so rather than emitting a
    container built over whatever the bytes read as."""
    # A count of two whose first "offset" points inside the offset table.
    payload = struct.pack("<IIII", 0, 2, 8, 500) + bytes(500)
    with pytest.raises(ValueError, match="not a pack"):
        _rebuild_pack(payload, {"x_000.dds": b""})


def test_an_absurd_file_count_is_refused_without_being_parsed():
    """The generated reader reads one offset per file the count claims, so a
    count nothing could hold has to be caught before it is handed over."""
    payload = struct.pack("<II", 0, 0xFFFFFFFF) + bytes(4096)
    with pytest.raises(ValueError, match="claims 4294967295 files"):
        _rebuild_pack(payload, {"x_000.dds": b""})


def test_aliased_entry_offsets_are_refused():
    """Two entries at one offset would leave the first with no bytes between
    its own offset and the next, which is how an entry is carried over. No
    pack of an install does it; a payload that is not a pack can."""
    header = struct.pack("<IIIII", 0, 3, 256, 256, 400)
    payload = header + bytes(1024 - len(header))
    with pytest.raises(ValueError, match="ascending and distinct"):
        _rebuild_pack(payload, {"x_000.dds": b""})


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in PACK_DATASET]
        ids = [f"{d['app_id']}-pack-{d['archive_path_hash']}" for d in PACK_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


@pytest.fixture(scope="session")
def shipped_pack(game_root, local_archive_path_hash):
    """A real pack archive's path, and the files it mounts."""
    from albam.engines.cie.fs import LfsFS

    path = resolve_archive_hashes(game_root, {local_archive_path_hash})[local_archive_path_hash]
    fs = LfsFS(path)
    try:
        files = {p: fs.readbytes(p) for p in fs.walk.files()}
    finally:
        fs.close()
    assert files
    return path, files


class _ExportedVFile:
    """What update_lfs takes of an exported file: a name and its bytes."""

    def __init__(self, display_name, data_bytes):
        self.display_name = display_name
        self._data_bytes = data_bytes

    def get_bytes(self):
        return self._data_bytes


def test_rebuilding_a_shipped_pack_unchanged_is_byte_for_byte_identical(shipped_pack):
    """A real pack, one entry handed back unchanged, comes out as the payload
    that went in - which is what says the writer reproduces a shipped layout
    rather than merely producing a readable one.

    True of all 644 uncompressed packs of an install, and of the payload of
    every compressed one sampled, including the "*.pack.yz2.lfs" ones.
    """
    from albam.engines.cie.archive import _read_payload

    path, files = shipped_pack
    payload, extension = _read_payload(path)
    assert extension == ".pack"

    name = sorted(files)[0]
    assert _rebuild_pack(payload, {name.lstrip("/"): files[name]}) == payload


def test_writing_a_shipped_pack_unchanged_remounts_the_same_files(shipped_pack, tmp_path):
    """The whole writer - decompress, rebuild, compress - and the archive
    mounted back off disk, which is the file a mod would ship."""
    from albam.engines.cie.archive import update_lfs
    from albam.engines.cie.fs import LfsFS

    path, files = shipped_pack
    name = sorted(files)[0]
    archive = update_lfs(path, [_ExportedVFile(name.lstrip("/"), files[name])])

    repacked_path = tmp_path / os.path.basename(path)
    repacked_path.write_bytes(archive)
    repacked = LfsFS(str(repacked_path))
    try:
        assert {p: repacked.readbytes(p) for p in repacked.walk.files()} == files
    finally:
        repacked.close()


def test_replacing_a_texture_in_a_shipped_pack(shipped_pack, tmp_path):
    """The point of the writer: a supplied DDS in place of a shipped texture,
    read back out of the archive the writer produced.

    The DDS is not decoded by anything here - import keeps the original bytes
    on the Blender image and this path hands bytes straight through - so a
    stand-in with the right magic is what a replacement looks like to the
    writer. Deliberately longer than what it replaces, which is the case that
    moves every entry after it.
    """
    from albam.engines.cie.archive import update_lfs
    from albam.engines.cie.fs import LfsFS

    path, files = shipped_pack
    name = sorted(files)[0]
    replacement = FAKE_DDS + b"\x5a" * (len(files[name]) + 3000)
    archive = update_lfs(path, [_ExportedVFile(name.lstrip("/"), replacement)])

    repacked_path = tmp_path / os.path.basename(path)
    repacked_path.write_bytes(archive)
    repacked = LfsFS(str(repacked_path))
    try:
        after = {p: repacked.readbytes(p) for p in repacked.walk.files()}
    finally:
        repacked.close()

    expected = dict(files)
    expected[name] = replacement
    assert after == expected
