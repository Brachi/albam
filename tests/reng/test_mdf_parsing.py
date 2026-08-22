import io
import json
import os

import pytest
from kaitaistruct import KaitaiStream

from tests.mtfw.scripts.catalog_paths import resolve_hashes

# Committed, fixed dataset - explicit, hash-only, catalog-verified files to
# parse (see test_dataset_hashes_are_in_catalog below), same pattern as
# test_mesh_parsing.py - extend this directly to add more. Picked for
# category variety (characters, buildings, props, weapons, VFX), same
# categories as the mesh-parsing/import datasets, and each is the real
# sibling .mdf2 of one of that dataset's .mesh files.
MDF_PARSING_DATASET_PATH = os.path.join(os.path.dirname(__file__), "datasets", "mdf_parsing_hashes.json")
with open(MDF_PARSING_DATASET_PATH) as f:
    MDF_PARSING_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_mdf_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_mdf_path_hash")
        argvalues = [(d["app_id"], d["mdf_path_hash"]) for d in MDF_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['mdf_path_hash']}" for d in MDF_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by MDF_PARSING_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no real .pak needed.
    """
    for entry in MDF_PARSING_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["mdf_path_hash"] in catalog_hashes, (
            f"{entry['mdf_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def parsed_mdf(pak_fs_root, local_mdf_path_hash):
    from albam.engines.reng.structs.reengine_mdf import ReengineMdf

    path = resolve_hashes(pak_fs_root, {local_mdf_path_hash})[local_mdf_path_hash]
    src_bytes = pak_fs_root.readbytes(path)

    # Same technique albam.engines.reng.material.build_blender_materials
    # uses - mdf_version isn't stored in the file itself, only in its own
    # extension (".mdf2.<version>").
    mdf_version = int(path.rpartition(".")[2])

    parsed = ReengineMdf(mdf_version, KaitaiStream(io.BytesIO(src_bytes)))
    parsed._read()
    return parsed


def test_mdf(parsed_mdf):
    mdf = parsed_mdf

    assert mdf.id_magic == b"MDF\x00"
    assert mdf.num_materials > 0
    assert len(mdf.materials) == mdf.num_materials

    for material in mdf.materials:
        assert material.name
        assert len(material.textures) == material.num_textures
        assert len(material.properties_headers) == material.num_properties_headers

        for texture in material.textures:
            assert texture.texture_type
            assert texture.texture_path

        for prop in material.properties_headers:
            assert prop.name
            assert len(prop.params) == prop.num_params
