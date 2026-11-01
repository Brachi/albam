"""
The .udas variants an install holds beyond the little-endian container
albam reads.

Three kinds of payload arrive under that extension. Almost all of them are
the little-endian container structs/udas.ksy models. A couple write their
block table big-endian and hold their DAT block as a YZ2 compressed stream
(see albam/engines/cie/yz2.py), which albam decodes and lists. One holds no
block table at all, so it is not a UDAS whatever its name says, and mounts as
a single file with an error saying why.

Only the little-endian variant can be written back: this file also pins down
that the writer refuses the other two rather than emitting a little-endian
container over what was never one.
"""
import json
import os

import pytest

from tests.cie.lfs_paths import resolve_archive_hashes
from tests.dataset_cases import applies_to, entries_for

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
UDAS_VARIANT_DATASET_PATH = os.path.join(DATASETS_DIR, "udas_variant_hashes.json")
with open(UDAS_VARIANT_DATASET_PATH) as f:
    UDAS_VARIANT_DATASET = json.load(f)

# What each dataset entry's "variant" means, as a byte order for the block
# table (see albam.engines.cie.fs.udas_byte_order): None for a payload that
# holds no block table in either order.
VARIANT_BYTE_ORDERS = {
    "little_endian": "<",
    "big_endian_yz2": ">",
    "no_block_table": None,
}
# SHA-1 of each big-endian archive's DAT block once out of YZ2: what the
# original C++ yz2 decoder (as JADERLINK's RE4_DASYZ2_TOOL ships it, built
# with 32-bit words) produces for the same blocks.
DECODED_DAT_SHA1 = {
    "16751b2ceafb2bb9": "46c93da3015665023f81212f4787489cda84e51a",
    "76e7d1b4720d91d4": "0aaa908fd75d27fbd3e657beb0acc8191adb46bf",
}
# Where a block table starts and where every archive seen puts its DAT block.
BLOCK_TABLE_END = 0x20 + 32
DATA_BLOCK_OFFSET = 0x400


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        entries = entries_for(metafunc, UDAS_VARIANT_DATASET)
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in entries]
        ids = [f"{d['app_id']}-{d['variant']}-{d['archive_path_hash']}"
               for d in entries]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by UDAS_VARIANT_DATASET must be in that app_id's committed catalog.
    CI-safe: reads two committed JSON files, no real install needed.
    """
    for entry in UDAS_VARIANT_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        catalogued = catalog.get(entry["archive_path_hash"])
        assert catalogued is not None, (
            f"{entry['archive_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )
        assert catalogued["payload_extension"] == entry["payload_extension"], (
            f"{entry['archive_path_hash']!r} is a {catalogued['payload_extension']!r} archive, "
            f"not {entry['payload_extension']!r}"
        )


def test_dataset_variants_are_known():
    """CI-safe: the dataset only names variants this file knows how to check."""
    for entry in UDAS_VARIANT_DATASET:
        assert entry["variant"] in VARIANT_BYTE_ORDERS


@pytest.fixture(scope="session")
def local_variant(local_archive_path_hash):
    return next(d["variant"] for d in UDAS_VARIANT_DATASET
                if d["archive_path_hash"] == local_archive_path_hash)


@pytest.fixture(scope="session")
def archive_path(game_root, local_archive_path_hash):
    return resolve_archive_hashes(game_root, {local_archive_path_hash})[local_archive_path_hash]


@pytest.fixture(scope="session")
def payload(archive_path):
    """The archive decompressed, which is where every variant only starts to
    differ: decompression itself works for all of them."""
    from albam.engines.cie.archive import _read_payload

    payload, extension = _read_payload(archive_path)
    assert extension == ".udas"
    return payload


def test_byte_order_is_read_from_the_block_table(payload, local_variant):
    """The block table is what says which variant an archive is.

    Not the eight signature words in front of it: both of the values those
    take occur in archives whose block table is little-endian, so reading
    them as a byte-order mark misclassifies a good part of an install.
    """
    from albam.engines.cie.fs import read_udas_block_table, udas_byte_order

    expected = VARIANT_BYTE_ORDERS[local_variant]
    assert udas_byte_order(payload) == expected

    if expected is None:
        return
    blocks = read_udas_block_table(payload, expected)
    block_type, size, offset = blocks[0]
    assert block_type == 0, "the first block of every archive seen is the DAT block"
    assert offset == DATA_BLOCK_OFFSET
    assert BLOCK_TABLE_END <= offset <= len(payload)
    assert offset + size <= len(payload)


@applies_to(variant="big_endian_yz2")
def test_big_endian_data_block_is_a_yz2_stream(payload, local_archive_path_hash):
    """The big-endian variant's DAT block is not a file table but a YZ2
    compressed stream, so its entries can only be listed once it is decoded:
    the block opens with its own compressed and decompressed lengths in
    ASCII hex, and the compressed one accounts for the rest of the block.

    What it decodes to is pinned by hash, since a decoder bug can keep the
    length right and still garble the bytes (yz2's matches are looked up by
    content, so a wrong byte early on derails later copies, not the coder).
    """
    import hashlib

    from albam.engines.cie.fs import (YZ2_HEADER_SIZE, is_yz2_block, read_udas_block_table,
                                      split_big_endian_dat, udas_byte_order)
    from albam.engines.cie.yz2 import decompress

    _block_type, size, offset = read_udas_block_table(payload, udas_byte_order(payload))[0]
    assert is_yz2_block(payload, offset)

    header = payload[offset:offset + YZ2_HEADER_SIZE].split(b"\n")[0]
    compressed, decompressed = (int(value, 16) for value in header.split(b"\t"))
    assert YZ2_HEADER_SIZE + compressed <= size
    assert decompressed > compressed, "a block stored compressed should shrink"

    block = decompress(payload[offset:offset + size])
    assert len(block) == decompressed
    assert hashlib.sha1(block).hexdigest() == DECODED_DAT_SHA1[local_archive_path_hash]
    extensions = [extension for _index, extension, _data in split_big_endian_dat(block)]
    assert {"LIT", "SMD", "SMX", "SHD", "TEX"} <= set(extensions)


def test_variants_list_their_entries_or_say_why_not(archive_path, payload, local_variant):
    """Both UDAS variants list their entries. An archive albam cannot list
    still mounts, holding its whole payload under the archive's own name -
    and carries an error saying why, rather than the parse failure of reading
    it as the wrong container.
    """
    from albam.engines.cie.fs import LfsFS

    fs = LfsFS(archive_path)
    try:
        paths = list(fs.walk.files())
        error = fs.container_error
        stem = os.path.basename(archive_path).split(".")[0]
        if local_variant in ("little_endian", "big_endian_yz2"):
            assert error is None
            assert len(paths) > 1
            assert all(path.startswith(f"/{stem}_") for path in paths)
            return

        assert paths == [f"/{stem}.udas"]
        assert fs.readbytes(paths[0]) == payload
        assert isinstance(error, ValueError)
        assert "block table" in str(error)
    finally:
        fs.close()


def test_the_writer_refuses_what_it_cannot_read(payload, local_variant):
    """Rebuilding a variant through the little-endian writer would emit a
    container the game cannot load, and would do it silently, so the writer
    turns it down instead."""
    from albam.engines.cie.archive import _rebuild_udas

    if local_variant == "little_endian":
        # Reached the entry-matching stage, i.e. not turned away as a variant.
        with pytest.raises(ValueError, match="matched an entry"):
            _rebuild_udas(payload, {"not_an_entry_of_this_archive.bin": b""})
        return

    with pytest.raises(NotImplementedError, match="little-endian variant"):
        _rebuild_udas(payload, {"not_an_entry_of_this_archive.bin": b""})
