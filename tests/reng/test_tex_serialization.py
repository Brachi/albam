import io
import json
import os

import pytest
from kaitaistruct import KaitaiStream

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# round-trip (see test_dataset_hashes_are_in_catalog below), same pattern as
# tests/reng/test_mesh_parsing.py - extend this directly to add more.
TEX_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "tex_serialization_hashes.json"
)
with open(TEX_SERIALIZATION_DATASET_PATH) as f:
    TEX_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_tex_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_tex_path_hash")
        argvalues = [(d["app_id"], d["tex_path_hash"]) for d in TEX_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['tex_path_hash']}" for d in TEX_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by TEX_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no real .pak needed.
    """
    for entry in TEX_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["tex_path_hash"] in catalog_hashes, (
            f"{entry['tex_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def tex_src_bytes(pak_fs_root, local_tex_path_hash):
    path = resolve_hashes(pak_fs_root, {local_tex_path_hash})[local_tex_path_hash]
    return pak_fs_root.readbytes(path)


def test_tex_roundtrip(tex_src_bytes):
    """Byte-exact round trip: read the real file with the current, unmodified
    tex.ksy, then write it back out into a pre-sized buffer (the same
    Kaitai read-write idiom albam/engines/mtfw/mesh.py's real .mod export
    uses, ~line 910) and compare against the original bytes. Deliberately
    strict - if tex.ksy fails to model every byte of the real file (e.g. an
    unread/padding gap), this will fail even though plain _read() parsing
    succeeds. That's the point: a structural completeness check independent
    of manually reading the format.
    """
    from albam.engines.reng.structs.reengine_tex import ReengineTex

    src_bytes = tex_src_bytes

    parsed = ReengineTex(KaitaiStream(io.BytesIO(src_bytes)))
    parsed._read()

    # dds_data is a Kaitai "instance" (a lazily-computed pos/size substream,
    # not a regular seq field), so plain _read() never touches it. _write()
    # reassigns parsed._io to the new destination stream before
    # _fetch_instances() gets a chance to lazily populate it from the
    # source - by then it's too late, and it crashes with an AttributeError
    # instead of comparing bytes. Force it to read (and cache) from the
    # still-attached source stream now, for every mipmap, so the write path
    # below has something to write back.
    for mipmap in parsed.mipmaps:
        _ = mipmap.dds_data

    out_stream = KaitaiStream(io.BytesIO(bytearray(len(src_bytes))))
    parsed._check()
    parsed._write(out_stream)

    out_bytes = out_stream.to_byte_array()
    assert out_bytes == src_bytes
