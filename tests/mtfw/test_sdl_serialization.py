import json
import os

import bpy
import pytest

from tests.mtfw.conftest import import_export
from tests.mtfw.scripts.catalog_paths import resolve_hashes


# Committed, fixed dataset - not selectable via --mtfw-dataset like the rest
# of tests/mtfw/*.py. This is the single source of truth for what this file
# tests locally; extend it directly rather than pointing at some other file.
# Every hash here must be a subset of that app_id's committed
# tests/mtfw/datasets/<app_id>_catalog.json - see test_dataset_hashes_are_in_catalog
# below, which enforces it.
SDL_SERIALIZATION_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "sdl_serialization_hashes.json"
)
with open(SDL_SERIALIZATION_DATASET_PATH) as f:
    SDL_SERIALIZATION_DATASET = json.load(f)


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_sdl_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_sdl_path_hash")
        argvalues = [(d["app_id"], d["sdl_path_hash"]) for d in SDL_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['sdl_path_hash']}" for d in SDL_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - every hash referenced
    by SBC_SERIALIZATION_DATASET must be a subset of that app_id's committed
    catalog, so this file only ever exercises real, unmodified, hash-verified
    game files. CI-safe: reads two committed JSON files, no --game-dir needed.
    """
    for entry in SDL_SERIALIZATION_DATASET:
        catalog_path = os.path.join(os.path.dirname(__file__), "datasets", f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog_hashes = {e["path_hash"] for e in json.load(f)}
        assert entry["sdl_path_hash"] in catalog_hashes, (
            f"{entry['sdl_path_hash']!r} ({entry['app_id']}) is not in {catalog_path!r}"
        )


@pytest.fixture(scope="session")
def sdl_export_local(game_fs_root, local_app_id, local_sdl_path_hash):
    from albam.engines.mtfw.structs.sdl_156 import Sdl156

    bpy.context.scene.albam.apps.app_selected = local_app_id

    local_sbc_path = resolve_hashes(game_fs_root, {local_sdl_path_hash})[local_sdl_path_hash].lstrip("/")
    print(f"[SDL serialization] file={local_sbc_path!r} app_id={local_app_id!r}", flush=True)
    vfile_sdl = import_export(local_app_id, local_sbc_path)
    vfile_sdl_exported = bpy.context.scene.albam.exported.select_vfile(local_app_id, local_sbc_path)
    assert vfile_sdl_exported

    Sdl = Sdl156
    src_sdl = Sdl.from_bytes(vfile_sdl.get_bytes())
    dst_sdl = Sdl.from_bytes(vfile_sdl_exported.get_bytes())
    src_sdl._read()
    dst_sdl._read()
    return src_sdl, dst_sdl


@pytest.fixture(scope="session")
def sdl_imported_local(sdl_export_local):
    return sdl_export_local[0]


@pytest.fixture(scope="session")
def sdl_exported_local(sdl_export_local):
    return sdl_export_local[1]


def test_sdl_header(sdl_imported_local, sdl_exported_local):
    src = sdl_imported_local
    dst = sdl_exported_local

    assert src.header.version == dst.header.version
    assert src.header.frame_max == dst.header.frame_max
    assert src.header.floor_frame == dst.header.floor_frame
    assert src.header.ofs_names == dst.header.ofs_names
    assert len(src.tracks) == len(dst.tracks)


def test_sdl_tracks(sdl_imported_local, sdl_exported_local):
    src = sdl_imported_local
    dst = sdl_exported_local
    for track_index, (src_track, dst_track) in enumerate(zip(src.tracks, dst.tracks)):
        assert src_track.track_type == dst_track.track_type
        assert src_track.prop_type == dst_track.prop_type
        assert src_track.parent == dst_track.parent
        assert src_track.num_frames == dst_track.num_frames
        assert src_track.name == dst_track.name
        if getattr(src_track, "timing_frames", None) is not None:
            for src_timing, dst_timing in zip(src_track.timing_frames, dst_track.timing_frames):
                assert src_timing.frame == dst_timing.frame
                assert dst_timing.type == dst_timing.type


def test_sdl_data_blocks(sdl_imported_local, sdl_exported_local):
    src = sdl_imported_local
    dst = sdl_exported_local
    for track_index, (src_track, dst_track) in enumerate(zip(src.tracks, dst.tracks)):
        if src_track.num_frames > 0:
            assert len(src_track.data) == len(dst_track.data)
            for src_data, dst_data in zip(src_track.data, dst_track.data):
                if src_track.prop_type in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
                    assert src_data.val == dst_data.val
                elif src_track.prop_type == 14:
                    assert src_data.ref_path == dst_data.ref_path
                elif src_track.prop_type == 15:
                    assert src_data.r == dst_data.r
                    assert src_data.g == dst_data.g
                    assert src_data.b == dst_data.b
                    assert src_data.a == dst_data.a
                elif src_track.prop_type in (20, 36):
                    assert src_data.x == dst_data.x
                    assert src_data.y == dst_data.y
                    assert src_data.z == dst_data.z
                elif src_track.prop_type in (21, 22, 36):
                    assert src_data.x == dst_data.x
                    assert src_data.y == dst_data.y
                    assert src_data.z == dst_data.z
                    assert src_data.w == dst_data.w
                elif src_track.prop_type == 40:
                    assert src_data.p1 == dst_data.p1
                    assert src_data.p2 == dst_data.p2
                elif src_track.prop_type == 55:
                    assert src_data.s == dst_data.s
                    assert src_data.r == dst_data.r
                elif src_track.prop_type == 57:
                    assert src_data.x == dst_data.x
                    assert src_data.y == dst_data.y


def test_sdl_offsets(sdl_imported_local, sdl_exported_local):
    src = sdl_imported_local
    dst = sdl_exported_local
    for track_index, (src_track, dst_track) in enumerate(zip(src.tracks, dst.tracks)):
        # Original files have junk string data like s512.arc>stage/s512/light/LightLnk/a00/s512_a00.sdl
        # has track 105 mColor name only because offset set in the middle of mBloomColor. string
        # it's impossible to keep this check
        # assert src_track.ofs_name == dst_track.ofs_name, (
        #    f"track {track_index}: name mismatch "
        #    f"{src_track.name!r} != {dst_track.name!r}; "
        #    f"ofs_name {src_track.ofs_name} -> {dst_track.ofs_name}"
        # )
        assert src_track.dti_ref == dst_track.dti_ref
        assert src_track.ofs_timing == dst_track.ofs_timing
        assert src_track.ofs_data == dst_track.ofs_data
