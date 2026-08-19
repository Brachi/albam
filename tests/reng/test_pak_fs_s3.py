"""
PakFS.from_s3() and ReenFS.from_s3() against a mocked S3 (moto) - no real
bucket/credentials or real .pak needed to validate the mechanism. Real
Cloudflare R2 usage differs only in which endpoint_url/credentials get
passed to from_s3() (see its docstring, and albam.lib.s3 which it shares
with MTFW_FS.from_s3).

Fixture pak bytes are built synthetically (see _build_pak_bytes) rather than
read from a local file: tests/data/ is deliberately gitignored (never
commit real game asset bytes, even small ones), a real .pak is tens of GB
anyway, and this file is meant to stay fully self-contained/network-free -
same rationale as tests/mtfw/test_arc_fs_s3.py, which this mirrors.

Pak.FileEntry (structs/pak.py) has no generated _write() (unlike Arc), so
the bytes are packed by hand via struct - the layout (see pak_fs.py's
HEADER_SIZE/FILE_ENTRY_SIZE) is simple enough that isn't a real burden.
"""
import os
import struct
import zlib

import pytest

boto3 = pytest.importorskip("boto3")
pytest.importorskip("moto")
pytest.importorskip("smart_open")

from moto import mock_aws  # noqa: E402

from albam.engines.reng.pak_fs import PakFS, ReenFS, HASH_SEED  # noqa: E402

import pymmh3 as mmh3  # noqa: E402

BUCKET = "re3-assets"
KEY = "re3/re_chunk_000.pak"
SAMPLE_PATH = "natives/stm/escape/character/player/pl0000/mesh/pl0000.mesh.2109108288"
OTHER_PATH = "natives/stm/escape/character/enemy/em0000/mesh/em0000.mesh.2109108288"
NOT_IN_PAK_PATH = "natives/stm/escape/character/player/pl0005/mesh/pl0005.mesh.2109108288"
# Deliberately larger than s3_opener's 1MiB range_chunk_size, same reasoning
# as test_arc_fs_s3.py's SAMPLE_CONTENT: a bounded range read against a
# *smaller* file gets clipped to EOF, which would make the
# construction-doesn't-download-the-payload assertion pass for the wrong
# reason.
SAMPLE_CONTENT = b"MESH-FAKE-CONTENT-FOR-MOCKED-S3-TESTS" + os.urandom(12 * 1024 * 1024)
OTHER_CONTENT = b"MESH-OTHER-FAKE-CONTENT"

DUMMY_CREDS = dict(
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
    region_name="us-east-1",
)


def _hash_path(path):
    return mmh3.hash(path.encode("utf-16")[2:], HASH_SEED) & HASH_SEED


def _build_pak_bytes(entries):
    """entries: list of (virtual_path, content) tuples. Every entry is
    stored zlib-compressed (flags=1), matching PakFS.openbin's zlib branch.
    """
    header_size = 16
    entry_size = 48
    table_size = header_size + entry_size * len(entries)

    packed_entries = b""
    blobs = b""
    offset = table_size
    for path, content in entries:
        # PakFS.openbin() decompresses with zlib.decompress(raw, -15) - raw
        # deflate, no zlib header/trailer (matches the pre-existing
        # PakWrapper.get_file() this replaced) - so the fixture must
        # compress the same way, not plain zlib.compress().
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        compressed = compressor.compress(content) + compressor.flush()
        packed_entries += struct.pack(
            "<IIQQQQQ",
            _hash_path(path),
            0,  # file_path_hash_case_sensitive - unused by PakFS
            offset,
            len(compressed),
            len(content),
            1,  # flags: zlib
            0,  # unk_01
        )
        blobs += compressed
        offset += len(compressed)

    header = struct.pack("<4sIII", b"KPKA", 1, len(entries), 0)
    return header + packed_entries + blobs


FIXTURE_ENTRIES = [
    (SAMPLE_PATH, SAMPLE_CONTENT),
    (OTHER_PATH, OTHER_CONTENT),
]
FIXTURE_PAK_BYTES = _build_pak_bytes(FIXTURE_ENTRIES)


@pytest.fixture
def path_list_file(tmp_path):
    # NOT_IN_PAK_PATH is included to confirm PakFS filters candidates down
    # to what's actually present in this pak (see pak_fs.py's module
    # docstring) - it must never show up as a match.
    list_path = tmp_path / "path_list.txt"
    list_path.write_text("\n".join([SAMPLE_PATH, OTHER_PATH, NOT_IN_PAK_PATH]) + "\n")
    return str(list_path)


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        client.put_object(Bucket=BUCKET, Key=KEY, Body=FIXTURE_PAK_BYTES)
        yield client


@pytest.fixture
def get_object_calls(s3_client, monkeypatch):
    """Record (Range, ContentLength) for every get_object call made by any
    S3 client built while this fixture is active - same technique as
    tests/mtfw/test_arc_fs_s3.py's fixture of the same name, since
    PakFS.from_s3() also builds its client internally.
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


def _from_s3(path_list_file, **kwargs):
    kwargs = {**DUMMY_CREDS, **kwargs}
    return PakFS.from_s3(bucket=BUCKET, key=KEY, path_list_path=path_list_file, **kwargs)


def test_from_s3_matches_only_paths_present_in_this_pak(s3_client, path_list_file):
    pak_fs = _from_s3(path_list_file)
    matched = set(pak_fs.walk.files())
    assert matched == {"/" + SAMPLE_PATH, "/" + OTHER_PATH}
    assert ("/" + NOT_IN_PAK_PATH) not in matched


def test_from_s3_construction_does_not_download_whole_pak(get_object_calls, path_list_file):
    _from_s3(path_list_file)

    # Construction only ever needs the header + fixed-size file-entry table
    # (~2 small bounded chunks here) - bounded by that, never by how big any
    # entry's actual content is. Comparing against SAMPLE_CONTENT's size
    # (not the whole fixture) is the real invariant: a real multi-GB pak's
    # header+table stays this small regardless of the pak's total size, so
    # a percentage-of-fixture-size comparison would be the wrong thing to
    # assert here (and flakes on a fixture this small either way).
    total_fetched = sum(content_length for _range, content_length in get_object_calls)
    assert total_fetched < len(SAMPLE_CONTENT)
    # every request must be a bounded range, never open-ended to EOF
    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)


def test_from_s3_read_matches_local_reference(get_object_calls, path_list_file):
    pak_fs = _from_s3(path_list_file)

    get_object_calls.clear()  # isolate the read below from construction's calls
    data = pak_fs.readbytes("/" + SAMPLE_PATH)
    assert data == SAMPLE_CONTENT

    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)
    fetched = sum(cl for _r, cl in get_object_calls)
    assert fetched < len(FIXTURE_PAK_BYTES)


# --- ReenFS.from_s3() -------------------------------------------------

REEN_PREFIX = "re3"
REEN_BASE_KEY = f"{REEN_PREFIX}/re_chunk_000.pak"
REEN_PATCH_KEY = f"{REEN_PREFIX}/re_chunk_000.pak.patch_001.pak"
REEN_LOOSE_KEY = f"{REEN_PREFIX}/re3_config.ini"

OVERLAP_PATH = SAMPLE_PATH  # present in both base and patch, different content
# BASE_ONLY_CONTENT reuses SAMPLE_CONTENT (deliberately >1MiB, see its own
# comment above) so the construction-doesn't-download-bulk-data test below
# has a meaningful size to compare against - a tiny placeholder here would
# make that assertion pass for the wrong reason, same lesson as PakFS's own
# from-s3 test.
BASE_ONLY_CONTENT = SAMPLE_CONTENT
PATCH_OVERLAP_CONTENT = b"MESH-PATCHED-VERSION"
LOOSE_CONTENT = b"[Render]\nMainMenu=False\n"

REEN_BASE_PAK_BYTES = _build_pak_bytes([(OVERLAP_PATH, BASE_ONLY_CONTENT), (OTHER_PATH, OTHER_CONTENT)])
REEN_PATCH_PAK_BYTES = _build_pak_bytes([(OVERLAP_PATH, PATCH_OVERLAP_CONTENT)])


@pytest.fixture
def reen_s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        client.put_object(Bucket=BUCKET, Key=REEN_BASE_KEY, Body=REEN_BASE_PAK_BYTES)
        client.put_object(Bucket=BUCKET, Key=REEN_PATCH_KEY, Body=REEN_PATCH_PAK_BYTES)
        client.put_object(Bucket=BUCKET, Key=REEN_LOOSE_KEY, Body=LOOSE_CONTENT)
        yield client


def _reen_from_s3(path_list_file, **kwargs):
    kwargs = {**DUMMY_CREDS, **kwargs}
    return ReenFS.from_s3(bucket=BUCKET, prefix=REEN_PREFIX, path_list_path=path_list_file, **kwargs)


def test_reen_from_s3_patch_wins_over_base(reen_s3_client, path_list_file):
    reen_fs = _reen_from_s3(path_list_file)
    assert reen_fs.readbytes("/" + OVERLAP_PATH) == PATCH_OVERLAP_CONTENT
    name, _owner = reen_fs.which("/" + OVERLAP_PATH)
    assert name == REEN_PATCH_KEY


def test_reen_from_s3_falls_through_to_base_for_base_only_path(reen_s3_client, path_list_file):
    reen_fs = _reen_from_s3(path_list_file)
    assert reen_fs.readbytes("/" + OTHER_PATH) == OTHER_CONTENT
    name, _owner = reen_fs.which("/" + OTHER_PATH)
    assert name == REEN_BASE_KEY


def test_reen_from_s3_includes_loose_layer_by_default(reen_s3_client, path_list_file):
    reen_fs = _reen_from_s3(path_list_file)
    assert reen_fs.readbytes("/re3_config.ini") == LOOSE_CONTENT


def test_reen_from_s3_include_loose_false_disables_loose_layer(reen_s3_client, path_list_file):
    reen_fs = _reen_from_s3(path_list_file, include_loose=False)
    assert not reen_fs.exists("/re3_config.ini")


def test_reen_from_s3_construction_does_not_download_whole_paks(
    get_object_calls, path_list_file, reen_s3_client
):
    _reen_from_s3(path_list_file)

    # bounded by header+table size across both pak layers, never by content -
    # comparing against BASE_ONLY_CONTENT's size (not the whole fixture),
    # same reasoning as PakFS's own equivalent test.
    total_fetched = sum(content_length for _range, content_length in get_object_calls)
    assert total_fetched < len(BASE_ONLY_CONTENT)
    assert all(_range and not _range.endswith("-") for _range, _ in get_object_calls)
