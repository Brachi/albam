import os
import json
import pytest

from albam.engines.mtfw.structs.xfs import Xfs
from albam.engines.mtfw.config_assets import from_xfs
from albam.engines.mtfw.xfs.layout import _lot_records
from albam.lib.stage_placer.re5_item_ids import ITEM_ID_RE5
from tests.mtfw.scripts.catalog_paths import resolve_hashes


XFS_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "xfs_parsing_hashes.json"
)
with open(XFS_PARSING_DATASET_PATH) as f:
    XFS_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and "local_xfs_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_xfs_path_hash")
        argvalues = [(d["app_id"], d["xfs_path_hash"]) for d in XFS_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['xfs_path_hash']}" for d in XFS_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by TEX_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in XFS_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["xfs_path_hash"] in catalog_hashes, (
            f"{entry['xfs_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_xfs(game_fs_root, local_app_id, local_xfs_path_hash):
    path = resolve_hashes(game_fs_root, {local_xfs_path_hash})[local_xfs_path_hash]
    xfs_bytes = game_fs_root.readbytes(path)

    parsed = Xfs.from_bytes(xfs_bytes)
    parsed._read()
    return {"parsed": parsed, "path": path, "app_id": local_app_id}


def test_parsed_xfs_version(parsed_xfs):
    assert parsed_xfs["parsed"].header.version_major == 6


def test_dataset_item_classes_are_in_item_id_re5(parsed_xfs, local_xfs_path_hash):
    """Find ItemId entries with a known LOT class but an empty mapped class."""
    extension = os.path.splitext(parsed_xfs["path"])[1].lower().lstrip(".")
    if extension != "lot":
        return

    xfs = parsed_xfs["parsed"]
    has_item_id_property = any(
        (prop.name or "").casefold() == "itemid"
        for class_def in xfs.class_defs
        for prop in class_def.properties
    )
    if not has_item_id_property:
        return

    xml_root = from_xfs(xfs, extension, parsed_xfs["app_id"]).getroot()
    missing_classes = {}
    for (
        _item_path,
        (
            _item_record,
            xml_unit_class,
            _info,
            _info_path,
            _unit_class_path,
            item_id,
            _item_id_path,
        ),
    ) in _lot_records(xml_root).items():
        if item_id is None or not xml_unit_class.strip():
            continue
        mapping = ITEM_ID_RE5.get(item_id)
        if mapping is not None and not mapping[0]:
            missing_classes.setdefault(item_id, set()).add(xml_unit_class)

    missing_classes = {
        item_id: sorted(unit_classes)
        for item_id, unit_classes in sorted(missing_classes.items())
    }
    assert not missing_classes, (
        f"XFS dataset entry {local_xfs_path_hash!r} contains ItemId entries "
        f"with empty ITEM_ID_RE5 class mappings: {missing_classes}"
    )
