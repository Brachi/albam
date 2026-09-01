"""
Room geometry: parsing a real scenario .smd, and importing one.

A scenario is the room itself - a placement table plus the models it places,
each of them a mesh .bin embedded in the file (see
albam/engines/cie/structs/re4-uhd-smd.ksy). The parsing tests check the file
against what the format says about itself, above all that the two offset
tables really do cover every index the entries use, since nothing in the
file states their length - only a zero past the last offset ends them. The
import test drives the registered import function the way the VFS panel
does, and checks a room comes out assembled rather than piled at the origin.

The dataset is two archives of one split room: the archive holding the
models its parts share, and one of those parts, which places models out of
both.
"""
import json
import os

import bpy
import pytest

from albam.lib import fs_registry
from tests.cie.lfs_paths import resolve_archive_hashes

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "scenario_parsing_hashes.json")
with open(DATASET_PATH) as f:
    SCENARIO_DATASET = json.load(f)

MESH_HEADER_SIZES = (0x40, 0x50, 0x60)
MESH_FLAG_OFFSET = 0x20
MESH_FLAG = 0x80000000


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in SCENARIO_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in SCENARIO_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - see
    tests/cie/test_lfs_fs.py, same check. CI-safe."""
    for entry in SCENARIO_DATASET:
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


@pytest.fixture(scope="session")
def archive_path(game_root, local_archive_path_hash):
    return resolve_archive_hashes(game_root, {local_archive_path_hash})[local_archive_path_hash]


@pytest.fixture(scope="session")
def scenarios(archive_path):
    """{entry name: bytes} for every .smd the archive holds."""
    from albam.engines.cie.fs import LfsFS

    fs = LfsFS(archive_path)
    try:
        found = {path: fs.readbytes(path) for path in fs.walk.files()
                 if path.lower().endswith(".smd")}
    finally:
        fs.close()
    assert found, "a room archive in this dataset should hold at least one scenario"
    return found


@pytest.fixture
def _clean_scene():
    # bpy.data and the VFS are session-scoped state: register() runs once per
    # pytest session, so a test leaving objects or roots behind changes what
    # the next one sees.
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    bpy.context.scene.albam.vfs.file_list.clear()
    bpy.context.scene.albam.exported.file_list.clear()
    fs_registry.clear()


def _parse(data):
    from albam.engines.cie.structs.re4_uhd_smd import Re4UhdSmd

    smd = Re4UhdSmd.from_bytes(data)
    smd._read()
    return smd


def test_scenario_header(scenarios):
    from albam.engines.cie.scenario import SCENARIO_MAGICS

    for name, data in scenarios.items():
        smd = _parse(data)
        assert smd.header.magic in SCENARIO_MAGICS, f"{name}: unknown magic"
        assert smd.header.offset_model_table < len(data), f"{name}: model table past the end"
        assert smd.header.offset_tpl_table < len(data), f"{name}: tpl table past the end"
        # The entries have to fit before the model table starts, or the
        # entry size this reads them at is wrong.
        assert len(smd.entries) == smd.header.num_entries
        assert smd.header.offset_model_table >= 16 + 72 * smd.header.num_entries, (
            f"{name}: the model table overlaps the entries"
        )


def test_offset_tables_are_terminated_past_what_the_entries_use(scenarios):
    """Neither table states its length, and the reader takes the zero past
    the last offset as the end. What has to hold for that to be safe is that
    every index the entries use lands before the terminator - a table may
    hold one more model than any entry places, but never one fewer."""
    for name, data in scenarios.items():
        smd = _parse(data)
        placed = [e for e in smd.entries if e.is_placed]
        assert placed, f"{name}: a scenario should place at least one model"

        num_models = len(smd.offsets_models) - 1  # the terminator is not one
        num_tpls = len(smd.offsets_tpls) - 1
        own = [e for e in placed if not e.is_shared]
        if own:
            assert max(e.model_id for e in own) <= num_models - 1, (
                f"{name}: an entry addresses a model the table doesn't hold"
            )
        assert max(e.tpl_id for e in placed) <= num_tpls - 1, (
            f"{name}: an entry addresses a .tpl the table doesn't hold"
        )
        assert smd.offsets_models[-1] == 0 and smd.offsets_tpls[-1] == 0


def test_embedded_models_are_mesh_bins(scenarios):
    """Every model an entry places is a mesh .bin, and the vertex count its
    header states is the one its face strips describe.

    Only the models the entries reach: a table can carry a spare offset past
    them that points at nothing readable, and nothing ever follows it.

    The second half matters because a scenario is where a model can outgrow
    the u2 count in its own header, which the mesh importer reads - so a room
    that hit it would import short.
    """
    for name, data in scenarios.items():
        smd = _parse(data)
        used = {e.model_id for e in smd.entries if e.is_placed and not e.is_shared}
        for index in sorted(used):
            offset = smd.header.offset_model_table + smd.offsets_models[index]
            assert offset + 0x60 <= len(data), f"{name}: model {index} starts past the end"
            model = _parse_embedded_model(data, offset)
            assert model.header.offset_bones in MESH_HEADER_SIZES, (
                f"{name}: model {index} has no mesh .bin header"
            )
            flags = int.from_bytes(
                data[offset + MESH_FLAG_OFFSET:offset + MESH_FLAG_OFFSET + 4], "little")
            assert flags & MESH_FLAG, f"{name}: model {index} is not flagged as a mesh"

            corners = sum(strip.fcount
                          for material in model.materials
                          for strip in material.face_index.strips)
            assert corners == model.header.num_vertices, (
                f"{name}: model {index} states {model.header.num_vertices} vertices "
                f"but its strips describe {corners}"
            )


def test_embedded_tpls_parse(scenarios):
    from albam.engines.cie.structs.tpl import Tpl

    for name, data in scenarios.items():
        smd = _parse(data)
        for index in range(len(smd.offsets_tpls) - 1):
            offset = smd.header.offset_tpl_table + smd.offsets_tpls[index]
            tpl = Tpl.from_bytes(data[offset:])
            tpl._read()
            assert tpl.num_tpl > 0, f"{name}: .tpl {index} holds no textures"
            assert len(tpl.tpl_entries) == tpl.num_tpl


def _parse_embedded_model(data, offset):
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    model = Re4UhdBin.from_bytes(data[offset:])
    model._read()
    return model


def test_scenario_imports_assembled(archive_path, local_app_id, _clean_scene):
    """The registered import function builds the room, placed.

    Every model of a scenario sits at the origin in its own file, so a room
    imported without its placements is a heap of overlapping pieces - which
    is exactly what a matrix silently dropped somewhere would leave. Distinct
    object matrices spread over a real extent is what says otherwise.
    """
    from albam.registry import blender_registry

    bpy.context.scene.albam.apps.app_selected = local_app_id
    vfs = bpy.context.scene.albam.vfs
    root = vfs.add_real_file(local_app_id, archive_path)
    scenarios = [vf for vf in vfs.file_list
                 if vf.tree_node.root_id == root.name and not vf.is_root and
                 vf.display_name.lower().endswith(".smd")]
    assert scenarios, "a room archive in this dataset should hold at least one scenario"

    # The smallest one: they all go through the same code, and a room can
    # carry a hundred models.
    vfile = min(scenarios, key=lambda vf: len(vf.get_bytes()))
    import_function = blender_registry.import_registry[(vfile.app_id, vfile.extension)]
    bl_scenario = import_function(vfile, bpy.context)

    placed = list(bl_scenario.children)
    assert placed, "the scenario placed nothing"
    # A placement is one mesh object, or an empty carrying the position and
    # scale with the model rotated under it (see scenario._place).
    meshes = [o for o in bl_scenario.children_recursive if o.type == "MESH"]
    assert len(meshes) == len(placed), "a placement brought in no model"
    assert all(len(mesh.data.polygons) for mesh in meshes), "a placed model has no faces"

    bpy.context.view_layer.update()  # object matrices are only as fresh as this
    if len(placed) > 1:
        translations = {tuple(round(v, 3) for v in child.matrix_world.translation)
                        for child in placed}
        assert len(translations) > 1, "every model was placed at the same point"
