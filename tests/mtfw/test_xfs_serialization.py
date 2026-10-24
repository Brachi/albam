import json
import os
import xml.etree.ElementTree as ET

import pytest

from albam.engines.mtfw.config_assets import from_xfs, to_xfs
from albam.engines.mtfw.structs.xfs import Xfs
from tests.mtfw.scripts.catalog_paths import resolve_hashes


# Add real, catalog-verified XFS assets here in a separate dataset update.
# Each entry uses: {"app_id", "xfs_path_hash"}.
XFS_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "xfs_serialization_hashes.json"
)
with open(XFS_SERIALIZATION_DATASET_PATH) as f:
    XFS_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if (
        "local_app_id" in metafunc.fixturenames
        and "local_xfs_path_hash" in metafunc.fixturenames
    ):
        argnames = ("local_app_id", "local_xfs_path_hash")
        argvalues = [
            (entry["app_id"], entry["xfs_path_hash"])
            for entry in XFS_SERIALIZATION_DATASET
        ]
        ids = [
            f"{entry['app_id']}-{entry['xfs_path_hash']}"
            for entry in XFS_SERIALIZATION_DATASET
        ]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """Every XFS fixture must refer to a hash in its app's committed catalog."""
    for entry in XFS_SERIALIZATION_DATASET:
        catalog_path = os.path.join(
            os.path.dirname(__file__),
            "datasets",
            f"{entry['app_id']}_catalog.json",
        )
        with open(catalog_path) as f:
            catalog_hashes = {item["path_hash"] for item in json.load(f)}
        assert entry["xfs_path_hash"] in catalog_hashes, (
            f"{entry['xfs_path_hash']!r} ({entry['app_id']}) is not in "
            f"{catalog_path!r}"
        )


@pytest.fixture(scope="session")
def xfs_xml_roundtrip(
    game_fs_root,
    local_xfs_path_hash,
):
    path = resolve_hashes(game_fs_root, {local_xfs_path_hash})[
        local_xfs_path_hash
    ]
    extension = os.path.splitext(path)[1].lstrip(".").lower()
    source = Xfs.from_bytes(game_fs_root.readbytes(path))
    source._read()

    source_xml = from_xfs(source, extension)
    exported_bytes = to_xfs(source_xml)
    exported = Xfs.from_bytes(exported_bytes)
    exported._read()
    exported_xml = from_xfs(exported, extension)
    return source_xml, exported_xml, source, exported


def test_xfs_serialization_round_trips_xml(xfs_xml_roundtrip):
    source_xml, exported_xml, source, exported = xfs_xml_roundtrip

    assert ET.tostring(source_xml.getroot()) == ET.tostring(exported_xml.getroot())
    assert source.header.version_major == exported.header.version_major
    assert source.header.version_minor == exported.header.version_minor
    assert len(source.class_defs) == len(exported.class_defs)
    assert source.data.num_roots == exported.data.num_roots
