"""The two things that differ between an .arc's versions: how an entry's
payload is compressed, and which table names its file type - and, since
version 17 can now be written as well as read, that packing one produces
entries in its own codec.

Most of this needs no game data: the streams those tests decode are built by
hand out of one uncompressed LZX block, which exercises the frame header,
the block header and the bit reader's alignment, but not the Huffman path.
The dataset-driven half at the bottom is what puts real Devil May Cry 4
entries - megabytes of them, spanning many frames - through the encoder, and
what checks albam's own decoder against one that is not albam's.

Two parts of the DMC4 story are deliberately not covered here, because
neither can be executed rather than because nobody got to them:

* Whether the game itself loads an archive albam repacked. Nothing automated
  can answer that, which is why the encoder is checked against a second,
  independent LZX decoder instead (see tests/xcompress_cab.py) - strong
  evidence that the stream is real LZX, and not the same thing as the game
  accepting it.
* Editing a DMC4 model in Blender and writing it back. That story stops
  before the packer: exporting any DMC4 .mod fails in mod_153 serialization
  (`ConsistencyError: index_buffer`), on 5 of 5 models tried and identically
  on the commit this branch started from, so it is a defect of the mesh
  exporter and not of packing. What reaches the writer in these tests is a
  payload taken back out of an archive.
"""
import json
import os
import struct
import zlib

import pytest

from albam.engines.mtfw import (
    EXTENSION_TO_FILE_ID,
    FILE_ID_TO_EXTENSION,
    FILE_ID_TO_EXTENSION_DMC4,
)
from albam.engines.mtfw.archive import update_arc
from albam.engines.mtfw.arc_fs import (
    ARC_VERSION_DMC4,
    AmbiguousExtension,
    decompress_entry,
    file_type_extensions,
)
from albam.engines.mtfw.structs.arc import Arc
from albam.lib import xcompress_encode
from albam.lib.xcompress import _BitReader, xmem_decompress
from albam.lib.xcompress_encode import (
    FRAME_SIZE,
    FrameTooLarge,
    _lz77_tokens,
    _operations,
    _split_blocks,
    compress_frames,
    frame_stream,
    xmem_compress,
)
from tests.mtfw.scripts.catalog_paths import resolve_hashes
from tests.xcompress_cab import independent_decompress, sevenzip
from tests.xcompress_frames import frames_of

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


class FakeVFile:
    """The four things update_arc asks a vfile for."""

    def __init__(self, relative_path, data, app_id="dmc4"):
        self.relative_path = relative_path
        self.extension = relative_path.rsplit(".", 1)[-1]
        self.app_id = app_id
        self._data = data

    def get_bytes(self):
        return self._data


def build_arc(version, entries):
    """An .arc holding `entries` as (path, file type id, payload, flags),
    each payload given uncompressed and encoded here in the archive's codec.

    Written out by hand rather than through _serialize_arc, so that a test of
    the writer is not reading back the writer's own idea of the layout: a
    header, one 80 byte record per entry, padding out to where the first
    payload starts, and then the payloads back to back. Encoding here is what
    keeps `size` the decompressed length and `zsize` the encoded one, so an
    entry of the fixture reads back the way a real archive's does.
    """
    table = bytearray()
    body = bytearray()
    padding = 32760 - (len(entries) * 80) % 32768
    offset = 8 + len(entries) * 80 + padding
    for path, file_type, payload, flags in entries:
        if version == ARC_VERSION_DMC4:
            chunk = stored_frame(payload)
        else:
            chunk = zlib.compress(payload)
        table += path.encode("ascii").ljust(64, b"\x00")
        table += struct.pack("<iIII", file_type, len(chunk),
                             len(payload) | (flags << 29), offset)
        body += chunk
        offset += len(chunk)
    header = struct.pack("<4shh", b"ARC\x00", version, len(entries))
    return header + bytes(table) + b"\x00" * padding + bytes(body)


def parse_arc(data):
    parsed = Arc.from_bytes(data)
    parsed._read()
    return parsed


DMC4_TEX = 0x3CAD8076  # rTexture, as a version 17 archive numbers it
DMC4_LMT = 0x139EE51D  # rMotionList


def test_packing_a_version_17_archive_writes_xmemcompress_entries(tmp_path):
    """The point of the encoder existing: a DMC4 archive packs like any
    other, and what lands in it is a stream the archive's own codec reads.

    Before there was an encoder this had to be refused outright, because the
    alternative was writing zlib into an archive the game reads as LZX.
    """
    replaced = b"the payload that gets replaced\n" * 500
    untouched = b"the payload nothing happens to\n" * 500
    path = tmp_path / "test.arc"
    path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, replaced, 1),
        ("chr\\pl000\\pl001", DMC4_TEX, untouched, 2),
    ]))

    new_payload = b"albam wrote this one\n" * 2000
    rebuilt = parse_arc(update_arc(str(path), [
        FakeVFile("chr\\pl000\\pl000.tex", new_payload)]))

    assert rebuilt.header.version == ARC_VERSION_DMC4
    entries = {e.file_path: e for e in rebuilt.file_entries}
    assert len(entries) == 2

    written = entries["chr\\pl000\\pl000"]
    assert written.size == len(new_payload)
    assert written.zsize == len(written.raw_data)
    assert decompress_entry(ARC_VERSION_DMC4, written.raw_data, written.size) == new_payload
    with pytest.raises(zlib.error):
        zlib.decompress(written.raw_data)

    kept = entries["chr\\pl000\\pl001"]
    assert kept.raw_data == stored_frame(untouched)
    assert decompress_entry(ARC_VERSION_DMC4, kept.raw_data, kept.size) == untouched


def test_packing_leaves_an_entry_s_flags_alone(tmp_path):
    """Every entry of every version 7 archive carries flags 2, but a DMC4
    archive uses 0 and 1 as well - only ever on a tex, so the value says
    something about the texture, and rewriting it would be inventing an
    answer."""
    payload = b"a texture, supposedly\n" * 200
    path = tmp_path / "test.arc"
    path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        (f"chr\\tex{flags}", DMC4_TEX, payload, flags)
        for flags in (0, 1, 2)
    ]))

    rebuilt = parse_arc(update_arc(str(path), [
        FakeVFile("chr\\tex0.tex", b"replaced\n" * 100)]))

    assert [e.flags for e in rebuilt.file_entries] == [0, 1, 2]


def test_packing_gives_a_new_entry_its_own_version_s_file_type_id(tmp_path):
    """The two versions number the same resource classes from different
    hashes, so an entry albam adds has to be labelled with the id the archive
    it is going into uses - the shared table's id would name nothing there."""
    path = tmp_path / "test.arc"
    path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"x" * 100, 2)]))

    rebuilt = parse_arc(update_arc(str(path), [
        FakeVFile("chr\\pl000\\motion.lmt", b"a motion list\n" * 100)]))

    added = {e.file_path: e for e in rebuilt.file_entries}["chr\\pl000\\motion"]
    assert added.file_type == DMC4_LMT
    assert FILE_ID_TO_EXTENSION.get(DMC4_LMT) is None


def test_a_new_entry_s_payload_reads_back_through_both_decoders(tmp_path):
    """Adding a file a DMC4 archive does not already hold: the payload has to
    survive, not just get the right label.

    The label is what test_packing_gives_a_new_entry_its_own_version_s_file_type_id
    covers. This is the other half - that what lands in the archive is a
    stream the archive's own codec reads, all the way back out through the
    ordinary reading path.
    """
    from albam.engines.mtfw.arc_fs import ArcFS

    arc_path = tmp_path / "test.arc"
    arc_path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"the entry already there\n" * 200, 2)]))

    payload = b"a texture albam added\n" * 900
    rebuilt_bytes = update_arc(str(arc_path), [
        FakeVFile("chr\\albam\\newly_added.tex", payload)])
    rebuilt = parse_arc(rebuilt_bytes)

    assert len(rebuilt.file_entries) == 2
    added = next(e for e in rebuilt.file_entries
                 if e.file_path == "chr\\albam\\newly_added")
    assert added.file_type == DMC4_TEX
    assert added.size == len(payload)
    assert decompress_entry(ARC_VERSION_DMC4, added.raw_data, added.size) == payload

    out = tmp_path / "rebuilt.arc"
    out.write_bytes(rebuilt_bytes)
    assert ArcFS(str(out)).readbytes("/chr/albam/newly_added.tex") == payload


@pytest.mark.skipif(sevenzip() is None,
                    reason="p7zip is not installed (see tests/xcompress_cab.py)")
def test_a_new_entry_s_payload_reads_back_through_an_independent_decoder(tmp_path):
    """The same entry, read by a decoder albam did not write.

    albam agreeing with itself says the encoder and the decoder match; it
    does not say the stream is LZX. This is what says that much, short of
    the game itself.
    """
    arc_path = tmp_path / "test.arc"
    arc_path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"the entry already there\n" * 200, 2)]))

    payload = b"a texture albam added\n" * 900
    rebuilt = parse_arc(update_arc(str(arc_path), [
        FakeVFile("chr\\albam\\newly_added.tex", payload)]))

    added = next(e for e in rebuilt.file_entries
                 if e.file_path == "chr\\albam\\newly_added")
    assert independent_decompress(added.raw_data, added.size) == payload


def test_an_entry_spanning_many_frames_survives_the_write_path(tmp_path):
    """A payload of several frames packed through the archive writer, not
    through the encoder on its own.

    An .lfs chunk is two frames holding one block, so nothing on that side
    ever asked the encoder for a stream that runs frame after frame. The
    dataset tests put real multi-megabyte entries through `xmem_compress`
    directly; this puts one through `update_arc`, which is what a user
    actually reaches, and checks the stream it wrote has the frame shape the
    game's own entries have.
    """
    arc_path = tmp_path / "test.arc"
    arc_path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"small\n" * 10, 2)]))

    payload = (b"a line that repeats itself, mostly\n" * 30000)[:5 * FRAME_SIZE + 4321]
    rebuilt = parse_arc(update_arc(str(arc_path), [
        FakeVFile("chr\\pl000\\pl000.tex", payload)]))

    written = rebuilt.file_entries[0]
    assert written.size == len(payload)
    frames, trailing = frames_of(written.raw_data)
    assert len(frames) == 6
    assert [f[0] for f in frames] == [2] * 5 + [5]
    assert sum(f[1] for f in frames) == len(payload)
    assert trailing == b""
    assert decompress_entry(ARC_VERSION_DMC4, written.raw_data, written.size) == payload


@pytest.mark.skipif(sevenzip() is None,
                    reason="p7zip is not installed (see tests/xcompress_cab.py)")
def test_a_many_frame_entry_reads_back_through_an_independent_decoder(tmp_path):
    arc_path = tmp_path / "test.arc"
    arc_path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"small\n" * 10, 2)]))

    payload = (b"a line that repeats itself, mostly\n" * 30000)[:5 * FRAME_SIZE + 4321]
    rebuilt = parse_arc(update_arc(str(arc_path), [
        FakeVFile("chr\\pl000\\pl000.tex", payload)]))

    written = rebuilt.file_entries[0]
    assert independent_decompress(written.raw_data, written.size) == payload


DMC4_CHR_TBL = 0x19DDF06A  # rCharTbl, one of the two types called "bin"
DMC4_PL_PARAM_TBL = 0x7A5DCF86  # rPlParamTbl, the other


def test_adding_an_entry_whose_extension_names_two_types_is_refused(tmp_path):
    """A DMC4 ".bin" is either an rCharTbl or an rPlParamTbl, and an
    extension is all albam is told about a file a user hands it. Labelling
    the entry with whichever of the two the reverse table happened to keep
    would hand the engine a resource class the file is not, silently, so the
    pack stops and names both candidates instead."""
    path = tmp_path / "test.arc"
    path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"x" * 100, 2)]))

    with pytest.raises(AmbiguousExtension) as excinfo:
        update_arc(str(path), [
            FakeVFile("chr\\pl000\\param.bin", b"a table\n" * 100)])

    message = str(excinfo.value)
    assert ".bin" in message
    assert "0x19DDF06A" in message
    assert "0x7A5DCF86" in message


def test_replacing_an_entry_whose_extension_names_two_types_keeps_its_own(tmp_path):
    """The other side of that refusal: an entry the archive already holds
    has an answer rather than a guess - the type it was parsed with - so
    replacing an rCharTbl "bin" packs, and stays an rCharTbl."""
    path = tmp_path / "test.arc"
    path.write_bytes(build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\param", DMC4_CHR_TBL, b"a table\n" * 100, 2)]))

    payload = b"a replacement table\n" * 100
    rebuilt = parse_arc(update_arc(str(path), [
        FakeVFile("chr\\pl000\\param.bin", payload)]))

    entry = rebuilt.file_entries[0]
    assert entry.file_type == DMC4_CHR_TBL
    assert decompress_entry(ARC_VERSION_DMC4, entry.raw_data, entry.size) == payload


def test_adding_an_entry_to_a_version_7_archive_resolves_its_extension(tmp_path):
    """The shared table doubles up on one extension too - two ids are "shp" -
    but version 7 archives have been written with the last of the two since
    long before version 17 could be written at all, so that keeps resolving
    rather than becoming a refusal."""
    path = tmp_path / "test.arc"
    path.write_bytes(build_arc(ARC_VERSION_ZLIB, [
        ("chr\\pl000\\pl000", EXTENSION_TO_FILE_ID["tex"], b"x" * 100, 2)]))

    rebuilt = parse_arc(update_arc(str(path), [
        FakeVFile("chr\\pl000\\shape.shp", b"a shape\n" * 100, app_id="re5")]))

    added = {e.file_path: e for e in rebuilt.file_entries}["chr\\pl000\\shape"]
    assert added.file_type == 0x5204D557


def test_packing_a_version_7_archive_still_writes_zlib(tmp_path):
    """The other side of the same switch: nothing changes for the archives
    albam already wrote."""
    path = tmp_path / "test.arc"
    zlib_tex = EXTENSION_TO_FILE_ID["tex"]
    path.write_bytes(build_arc(ARC_VERSION_ZLIB, [
        ("chr\\pl000\\pl000", zlib_tex, b"old\n" * 100, 2)]))

    payload = b"albam wrote this one\n" * 200
    rebuilt = parse_arc(update_arc(str(path), [
        FakeVFile("chr\\pl000\\pl000.tex", payload, app_id="re5")]))

    entry = rebuilt.file_entries[0]
    assert zlib.decompress(entry.raw_data) == payload


def test_an_entry_the_encoder_cannot_write_is_refused_by_name(tmp_path, monkeypatch):
    """A payload the encoder cannot frame stops the pack and says which
    entry it was, rather than half-writing an archive or leaving the user
    with a bare internal traceback.

    No real payload gets a frame past what its header can count, so the
    encoder is made to produce one; everything from there on is the real
    write path.
    """
    arc_path = tmp_path / "test.arc"
    original = build_arc(ARC_VERSION_DMC4, [
        ("chr\\pl000\\pl000", DMC4_TEX, b"old\n" * 100, 2)])
    arc_path.write_bytes(original)

    def oversized_frames(payload, **kwargs):
        return [(b"\x00" * 0x10000, len(payload))]

    monkeypatch.setattr(xcompress_encode, "compress_frames", oversized_frames)

    payload = b"albam wrote this one\n" * 20
    with pytest.raises(FrameTooLarge) as excinfo:
        update_arc(str(arc_path), [FakeVFile("chr\\pl000\\pl000.tex", payload)])

    message = str(excinfo.value)
    assert "chr\\pl000\\pl000.tex" in message
    assert str(len(payload)) in message
    assert "65535" in message
    assert arc_path.read_bytes() == original


def _bits_msb_first(data):
    """The bit sequence _BitReader walks: 16-bit little-endian words, each
    read most significant bit first."""
    bits = ""
    for i in range(0, len(data) - 1, 2):
        word = data[i] | (data[i + 1] << 8)
        bits += format(word, "016b")
    return bits


@pytest.mark.parametrize("skip", range(16))
def test_bit_reader_matches_the_bit_sequence(skip):
    """A 24-bit read entered with a nearly empty buffer needs 39 bits held
    at once; a reader that keeps only 32 returns a truncated value. That is
    the block-length field, so the block ends in the wrong place and the
    rest of the stream decodes as noise.
    """
    data = bytes((i * 37 + 11) & 0xFF for i in range(32))
    bits = _bits_msb_first(data)

    reader = _BitReader(data, 0, len(data))
    if skip:
        assert reader.read(skip) == int(bits[:skip], 2)
    assert reader.read(24) == int(bits[skip:skip + 24], 2)
    assert reader.read(16) == int(bits[skip + 24:skip + 40], 2)


# Committed, fixed dataset - explicit, hash-only, catalog-verified entries to
# put through the encoder (see test_dataset_hashes_are_in_catalog below).
# Chosen to span the sizes an .arc holds, from a stream that is one short
# frame to one of several megabytes and eighty of them.
ARC_COMPRESSION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "arc_compression_hashes.json")
with open(ARC_COMPRESSION_DATASET_PATH) as f:
    ARC_COMPRESSION_DATASET = json.load(f)

# Below this an entry is one frame and one block, and forcing a second block
# out of it says nothing.
SEVERAL_BLOCKS_CAP = 100000


# The archive the repack test rewrites is whichever one holds this entry.
REPACK_ENTRY_HASH = "829d4caf886bc448"


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_entry_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_entry_path_hash")
        argvalues = [(d["app_id"], d["entry_path_hash"]) for d in ARC_COMPRESSION_DATASET]
        ids = [f"{d['app_id']}-{d['entry_path_hash']}" for d in ARC_COMPRESSION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")
    elif "local_app_id" in metafunc.fixturenames:
        # game_fs_root is session scoped, so what it is parametrized on has
        # to be too.
        metafunc.parametrize("local_app_id", ["dmc4"], scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by ARC_COMPRESSION_DATASET must be in that app_id's committed catalog, so
    this file only ever exercises real, unmodified, hash-verified game files.
    CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in ARC_COMPRESSION_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["entry_path_hash"] in catalog_hashes, (
            f"{entry['entry_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def entry_payload(game_fs_root, local_entry_path_hash):
    """One real archived entry, decoded - what the encoder has to write back."""
    path = resolve_hashes(game_fs_root, {local_entry_path_hash})[local_entry_path_hash]
    return game_fs_root.readbytes(path)


@pytest.fixture(scope="session")
def shipped_stream(game_fs_root, local_entry_path_hash):
    """The same entry as its archive stores it: the stream the game reads."""
    from albam.engines.mtfw.arc_fs import ArcFS, _entry_path

    path = resolve_hashes(game_fs_root, {local_entry_path_hash})[local_entry_path_hash]
    arc_path = game_fs_root.origin_absolute_path(path)
    if arc_path is None:
        # A loose file on disk shadows the archived one of the same path, so
        # there is no shipped stream behind it in this install.
        pytest.skip(f"{local_entry_path_hash} resolves to a loose file here")
    arc = ArcFS(arc_path)
    extensions = file_type_extensions(arc.version)
    parsed = Arc.from_file(arc_path)
    parsed._read()
    for file_entry in parsed.file_entries:
        if _entry_path(file_entry, extensions) == path:
            return file_entry.raw_data
    raise AssertionError(f"{path!r} is not an entry of {arc_path!r}")


@pytest.mark.skipif(sevenzip() is None,
                    reason="p7zip is not installed (see tests/xcompress_cab.py)")
def test_a_shipped_stream_decodes_the_same_through_an_independent_decoder(
        shipped_stream, entry_payload):
    """What makes the independent decoder worth anything: it reads the
    game's own streams, and reads them the way the game's archives say they
    decode.

    Without this the transplant into a CAB folder would be an assumption,
    and a test built on it would only be comparing albam against a second
    guess. With it, the two decoders agreeing on what albam writes means
    something.
    """
    assert independent_decompress(shipped_stream, len(entry_payload)) == entry_payload


def test_a_real_entry_round_trips_through_the_encoder(entry_payload):
    """A real entry, compressed by albam and decoded back byte for byte.

    Real payloads are what put real entropy through the trees, and real
    entries are what put a stream across many frames - which is the one thing
    an .lfs chunk, two frames holding one block, never asks of the encoder.
    """
    stream = xmem_compress(entry_payload)
    assert xmem_decompress(stream, len(entry_payload)) == entry_payload
    if len(entry_payload) > 4 * FRAME_SIZE:
        assert len(stream) < len(entry_payload)


@pytest.mark.skipif(sevenzip() is None,
                    reason="p7zip is not installed (see tests/xcompress_cab.py)")
def test_a_real_entry_round_trips_through_an_independent_decoder(entry_payload):
    """The same thing, read by a decoder albam did not write. Round-tripping
    through albam's own proves the encoder and the decoder agree; this is the
    closest a test gets to asking whether the stream is really LZX."""
    stream = xmem_compress(entry_payload)
    assert independent_decompress(stream, len(entry_payload)) == entry_payload


def test_a_real_entry_frames_the_way_the_game_s_own_streams_do(entry_payload):
    """Frame for frame the shape every shipped entry has: full frames under
    the short header, a last frame under the long one, nothing behind it."""
    stream = xmem_compress(entry_payload)
    frames, trailing = frames_of(stream)
    assert [f[0] for f in frames] == [2] * (len(frames) - 1) + [5]
    assert [f[1] for f in frames[:-1]] == [FRAME_SIZE] * (len(frames) - 1)
    assert sum(f[1] for f in frames) == len(entry_payload)
    assert trailing == b""


def test_a_real_entry_round_trips_when_forced_into_several_blocks(entry_payload):
    """The case only a 16MB entry reaches on its own: a block header landing
    in the middle of a frame, at whatever bit offset the symbols before it
    ended on.

    That is where the decoder's block-length field is read - 24 bits, out of
    a buffer that can be nearly empty - and reading it wrong puts the block's
    end in the wrong place and turns everything after it into noise. It went
    unnoticed until entries were decoded whole (see xcompress._BitReader.read),
    so it gets a test that reaches it with a real payload rather than a
    16MB one.
    """
    blocks = _split_blocks(_operations(entry_payload, _lz77_tokens(entry_payload)),
                           SEVERAL_BLOCKS_CAP)
    if len(entry_payload) > SEVERAL_BLOCKS_CAP:
        assert len(blocks) > 1

    stream = frame_stream(compress_frames(entry_payload, max_block_size=SEVERAL_BLOCKS_CAP))
    assert xmem_decompress(stream, len(entry_payload)) == entry_payload


def test_packing_a_real_archive_rewrites_one_entry_and_nothing_else(
        game_fs_root, local_app_id, tmp_path):
    """A whole shipped archive through the writer, not a two entry stand-in.

    What the synthetic tests cannot say is whether an archive of sixty real
    entries comes back out intact: the entries albam did not touch have to
    arrive byte for byte, in the same order, with their sizes, type ids and
    flags as they were, and the one it did has to be readable through the
    ordinary reading path.
    """
    from albam.engines.mtfw.arc_fs import ArcFS, _entry_path

    path = resolve_hashes(game_fs_root, {REPACK_ENTRY_HASH})[REPACK_ENTRY_HASH]
    arc_path = game_fs_root.origin_absolute_path(path)
    if arc_path is None:
        pytest.skip(f"{REPACK_ENTRY_HASH} resolves to a loose file here")

    original = Arc.from_file(arc_path)
    original._read()
    extensions = file_type_extensions(original.header.version)
    target = next(e for e in original.file_entries if _entry_path(e, extensions) == path)

    payload = b"albam wrote this one\n" * 500
    rebuilt_bytes = update_arc(arc_path, [FakeVFile(
        target.file_path + "." + extensions[target.file_type], payload)])
    rebuilt = parse_arc(rebuilt_bytes)

    assert rebuilt.header.version == original.header.version == ARC_VERSION_DMC4
    assert len(rebuilt.file_entries) == len(original.file_entries)
    for before, after in zip(original.file_entries, rebuilt.file_entries):
        assert after.file_path == before.file_path
        assert after.file_type == before.file_type
        assert after.flags == before.flags
        if before is target:
            continue
        assert after.size == before.size
        assert after.raw_data == before.raw_data

    written = next(e for e in rebuilt.file_entries if e.file_path == target.file_path)
    assert written.size == len(payload)
    assert decompress_entry(ARC_VERSION_DMC4, written.raw_data, written.size) == payload

    out = tmp_path / "rebuilt.arc"
    out.write_bytes(rebuilt_bytes)
    assert ArcFS(str(out)).readbytes(path) == payload
