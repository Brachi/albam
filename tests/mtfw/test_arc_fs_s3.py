"""
MTFW_FS.from_s3() against a mocked S3 (moto) - no real bucket/credentials
needed to validate the mechanism. Real Cloudflare R2 usage differs only in
which endpoint_url/credentials get passed to from_s3() (see its docstring).
Everything else - listing, opening, ranged reads, decompression - is
identical, since R2 speaks the S3 API.

Fixture arcs are built synthetically (see _build_arc_bytes) rather than read
from local files: tests/data/ is deliberately gitignored (never commit real
game asset bytes, even small ones), and this file is meant to stay fully
self-contained/network-free anyway, which downloading real fixture content
(from R2 or anywhere else) would defeat the point of.
"""
import os
import zlib

import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("moto")
pytest.importorskip("smart_open")

from moto import mock_aws  # noqa: E402

from albam.engines.mtfw import EXTENSION_TO_FILE_ID  # noqa: E402
from albam.engines.mtfw.arc_fs import MTFW_FS  # noqa: E402
from albam.engines.mtfw.structs.arc import Arc  # noqa: E402
from kaitaistruct import BytesIO, KaitaiStream  # noqa: E402

BUCKET = "re5-assets"
# GAME_ROOT_PREFIX mirrors the real bucket layout (see tests/mtfw/r2_config.py/
# .env.example): one shared bucket, each app_id's game root under its own
# prefix (here "re5", matching the app_id) - NOT the folder arcs happen to
# live in. `prefix` has to be the common root covering *both* where arcs live
# (searched recursively beneath it, like local find_arc_files()/os.walk) and
# where loose files' exposed paths are rooted - narrowing it to ARC_DIR would
# silently break loose resolution and the arc-itself-via-loose-layer parity
# below.
ARC_DIR = "nativePC_MT/Image/Archive/"
GAME_ROOT_PREFIX = "re5"
SAMPLE_PATH = "pawn/pl/pl00/model/pl0000.mod"
SAMPLE_RAW_PATH = "pawn\\pl\\pl00\\model\\pl0000"  # arc's own internal (backslash) form
# Random, and deliberately larger than _s3_opener's 1MiB range_chunk_size:
# a single bounded range read against a *smaller* file gets clipped to EOF,
# so its ContentLength ends up covering ~the whole file regardless of how
# little was actually consumed - the construction-doesn't-download-the-
# payload assertions below would be comparing against a false "downloaded
# everything" reading in that case, not a real one. 12MiB keeps any single
# 1MiB-bounded read a small fraction of the total, same as a real (tens-of-
# MiB) arc would.
SAMPLE_CONTENT = b"MOD\x00FAKE-CONTENT-FOR-MOCKED-S3-TESTS" + os.urandom(12 * 1024 * 1024)

# from_s3() builds its own client internally now (no client= param), so
# tests just need *some* credentials moto will accept - these never talk to
# anything real.
DUMMY_CREDS = dict(
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
    region_name="us-east-1",
)


def _build_arc_bytes(entries):
    """Build valid .arc bytes (see structs/arc.ksy) using the generated
    Arc/FileEntry read-write struct classes themselves, rather than
    hand-rolling the binary layout (bit-packed size/flags fields especially
    aren't worth re-deriving by hand). entries is a list of
    (raw_path, file_type, content) tuples - raw_path uses backslashes,
    matching the real format's own internal convention; content is the raw
    (uncompressed) bytes for that entry.
    """
    arc = Arc()
    arc.header = Arc.ArcHeader(_parent=arc, _root=arc)
    arc.header.ident = b"ARC\x00"
    arc.header.version = 1
    arc.header.num_files = len(entries)

    table_size = 8 + len(entries) * 80
    padding_size = 32760 - (len(entries) * 80) % 32768
    offset = table_size + padding_size

    arc.file_entries = []
    for raw_path, file_type, content in entries:
        compressed = zlib.compress(content)
        fe = Arc.FileEntry(_parent=arc, _root=arc)
        fe.file_path = raw_path
        fe.file_type = file_type
        fe.zsize = len(compressed)
        fe.size = len(content)
        fe.flags = 0
        fe.offset = offset
        fe.raw_data = compressed
        arc.file_entries.append(fe)
        offset += len(compressed)

    arc.padding = b"\x00" * padding_size

    # KaitaiStream's write mode needs the underlying stream pre-sized to its
    # final length upfront (it snapshots size() once at construction) -
    # `offset` is exactly the total length by now (table + padding + every
    # compressed blob appended in order).
    io_out = KaitaiStream(BytesIO(b"\x00" * offset))
    arc._write(io_out)
    io_out._io.seek(0)
    return io_out._io.read()


FIXTURE_ARC_BYTES = {
    "uPl00ChrisNormal.arc": _build_arc_bytes(
        [(SAMPLE_RAW_PATH, EXTENSION_TO_FILE_ID["mod"], SAMPLE_CONTENT)]
    ),
    # content doesn't matter here - only used as a second, distinct arc for
    # count-based assertions (test_from_s3_loads_arcs and friends).
    "s400.arc": _build_arc_bytes(
        [("stage\\s400\\placeholder", EXTENSION_TO_FILE_ID["mod"], b"MOD\x00PLACEHOLDER")]
    ),
}
FIXTURE_ARCS = tuple(FIXTURE_ARC_BYTES)


def _from_s3(**kwargs):
    kwargs = {**DUMMY_CREDS, **kwargs}
    return MTFW_FS.from_s3(bucket=BUCKET, prefix=GAME_ROOT_PREFIX, **kwargs)


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        for name, data in FIXTURE_ARC_BYTES.items():
            client.put_object(Bucket=BUCKET, Key=f"{GAME_ROOT_PREFIX}/{ARC_DIR}{name}", Body=data)
        yield client


@pytest.fixture
def get_object_calls(s3_client, monkeypatch):
    """Record (Range, ContentLength) for every get_object call made by any
    S3 client built while this fixture is active. Needed because from_s3()
    builds its client internally now - tests have no direct handle on it to
    spy on, so instead this wraps boto3.client() itself for the duration of
    the test, spying on whatever client(s) get constructed through it
    (both the setup client above and from_s3()'s own).
    """
    calls = []
    real_client_factory = boto3.client

    def spying_client_factory(*args, **kwargs):
        client = real_client_factory(*args, **kwargs)
        original_get_object = client.get_object

        def spy(**gkwargs):
            result = original_get_object(**gkwargs)
            calls.append((gkwargs.get("Range"), result["ContentLength"]))
            return result

        client.get_object = spy
        return client

    monkeypatch.setattr(boto3, "client", spying_client_factory)
    return calls


def test_from_s3_loads_arcs(s3_client):
    game_fs = _from_s3(include_loose=False)
    assert game_fs.failed_arcs == []
    assert len(list(game_fs.iterate_fs())) == len(FIXTURE_ARCS)


def test_from_s3_includes_loose_layer_by_default(s3_client):
    game_fs = _from_s3()
    assert len(list(game_fs.iterate_fs())) == len(FIXTURE_ARCS) + 1


def test_from_s3_include_loose_false_disables_loose_layer(s3_client):
    loose_override = b"MOD\x00LOOSE-OVERRIDE-CONTENT"
    s3_client.put_object(Bucket=BUCKET, Key=f"{GAME_ROOT_PREFIX}/{SAMPLE_PATH}", Body=loose_override)

    game_fs = _from_s3(include_loose=False)
    # with no loose layer, the packed copy is all there is - loose_override
    # sitting in the bucket at that key is simply invisible
    assert game_fs.readbytes(SAMPLE_PATH) != loose_override
    assert game_fs.readbytes(SAMPLE_PATH) == SAMPLE_CONTENT


def test_from_s3_construction_does_not_download_whole_arcs(get_object_calls):
    _from_s3()

    total_fetched = sum(content_length for _range, content_length in get_object_calls)
    total_arc_bytes = sum(len(data) for data in FIXTURE_ARC_BYTES.values())
    # constructing only needs each archive's header+file-table, never the
    # compressed content - true even with the default loose layer, since
    # S3LooseFS.__init__ makes no calls at all
    assert total_fetched < total_arc_bytes / 10
    # and every request must be a bounded range, never open-ended to EOF
    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)


def test_from_s3_read_matches_local_reference(get_object_calls):
    game_fs = _from_s3()

    get_object_calls.clear()  # isolate the read below from construction's calls
    data = game_fs.readbytes(SAMPLE_PATH)
    assert data == SAMPLE_CONTENT

    # bounded, and nowhere near the size of the archive it came from
    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)
    fetched = sum(cl for _r, cl in get_object_calls)
    assert fetched < len(FIXTURE_ARC_BYTES["uPl00ChrisNormal.arc"])

    reference_arc = Arc.from_bytes(FIXTURE_ARC_BYTES["uPl00ChrisNormal.arc"])
    reference_arc._read()
    file_entry = next(fe for fe in reference_arc.file_entries if fe.file_path == SAMPLE_RAW_PATH)
    expected = zlib.decompress(file_entry.raw_data)
    reference_arc._io.close()

    assert data == expected


def test_from_s3_origin_of(s3_client):
    game_fs = _from_s3()
    # relative to prefix (GAME_ROOT_PREFIX="re5" here), not the bucket key
    # verbatim - see MTFW_FS.origin_of()'s docstring.
    assert game_fs.origin_of(SAMPLE_PATH) == ARC_DIR + "uPl00ChrisNormal.arc"
    assert game_fs.origin_absolute_path(SAMPLE_PATH) == f"{GAME_ROOT_PREFIX}/{ARC_DIR}uPl00ChrisNormal.arc"


def test_from_s3_origin_of_strips_a_deeper_prefix(s3_client):
    # reuses the same uploaded keys, rooted one level deeper than the app_id
    # convention above - proves origin_of() genuinely strips whatever
    # `prefix` it was given, not just the app_id-length case.
    prefix = f"{GAME_ROOT_PREFIX}/nativePC_MT"
    game_fs = MTFW_FS.from_s3(bucket=BUCKET, prefix=prefix, include_loose=False, **DUMMY_CREDS)

    origin = game_fs.origin_of(SAMPLE_PATH)

    assert origin == "Image/Archive/uPl00ChrisNormal.arc"
    assert (game_fs.origin_absolute_path(SAMPLE_PATH) ==
            f"{GAME_ROOT_PREFIX}/{ARC_DIR}uPl00ChrisNormal.arc")


def test_from_s3_loose_file_overrides_packed_content(s3_client):
    # a loose override lives at the path itself, not under the arcs' prefix -
    # same convention as a local unpacked/modded file under game_root.
    loose_override = b"MOD\x00LOOSE-OVERRIDE-CONTENT"
    s3_client.put_object(Bucket=BUCKET, Key=f"{GAME_ROOT_PREFIX}/{SAMPLE_PATH}", Body=loose_override)

    game_fs = _from_s3()

    assert game_fs.readbytes(SAMPLE_PATH) == loose_override
    # not from an arc, so origin_of should say so
    assert game_fs.origin_of(SAMPLE_PATH) is None


def test_from_s3_arc_file_itself_reachable_via_loose_layer(s3_client):
    """Parity with local MTFW_FS: an .arc is not excluded from the loose
    layer, so it remains readable as a raw whole blob at its own key,
    independent of its unpacked content exposed at different paths."""
    arc_key = ARC_DIR + "uPl00ChrisNormal.arc"
    game_fs = _from_s3()

    assert game_fs.exists(arc_key)
    name, owner_fs = game_fs.which(arc_key)
    assert name == "<loose>"

    raw = game_fs.readbytes(arc_key)
    assert raw == FIXTURE_ARC_BYTES["uPl00ChrisNormal.arc"]
    # resolved via the loose layer, not the arc layer, so origin_of is None
    assert game_fs.origin_of(arc_key) is None
