import os

import pytest


def _generate_tests_arc_file_path(metafunc):
    arc_dirs = metafunc.config.getoption("arcdir")

    if not arc_dirs:
        pytest.skip("No arc directory or app_id supplied")
        return

    total_arc_files = []
    total_test_ids = []

    for app_id_and_arc_dir in arc_dirs:
        # TODO: error handling
        app_id, arc_dir = app_id_and_arc_dir.split("::")
        assert type(arc_dir) is str
        ARC_FILES = [
            {"filepath": os.path.join(root, f), "app_id": app_id}
            for root, _, files in os.walk(arc_dir)
            for f in files
            if f.endswith(".arc")
        ]
        total_arc_files.extend(ARC_FILES)
        test_ids = [f"{af['app_id']}::{os.path.basename(af['filepath'])}" for af in ARC_FILES]
        assert len(ARC_FILES) == len(test_ids)
        total_test_ids.extend(test_ids)

    metafunc.parametrize("arc_file", total_arc_files, ids=total_test_ids)


def _generate_tests_from_arcs(file_extension, metafunc):
    """
    Generate one parsed object for file_extension, based on provided arcs.
    Defer decompression and parsing to test-run time, not
    collection time.
    It requires a fixture named after the extension
    """
    arc_dirs = metafunc.config.getoption("arcdir")
    if not arc_dirs:
        pytest.skip("No arc directory supplied")
        return

    total_parsed_files = []
    total_test_ids = []

    for arc_dir in arc_dirs:
        app_id, arc_dir = arc_dir.split("::")
        ARC_FILES = [
            os.path.join(root, f)
            for root, _, files in os.walk(arc_dir)
            for f in files
            if f.endswith(".arc")
        ]

        if not ARC_FILES:
            raise ValueError(f"No files ending in .arc found in {arc_dir}")

        parsed_files, ids = files_per_arc(file_extension, ARC_FILES, app_id)
        total_parsed_files.extend(parsed_files)
        total_test_ids.extend(ids)
    # mrl fixture in tests/mtfw/conftest.py
    metafunc.parametrize(file_extension, total_parsed_files, indirect=True, ids=total_test_ids)


def files_per_arc(file_extension, arc_paths, app_id):
    # importing here to avoid errors in test collection.
    # Since collection happens before calling register() in `pytest_sessionstart`
    # sys.path is not modified to include albam_vendor, so the vendored dep kaitaistruct
    # is not found when needed.
    from albam.engines.mtfw.archive import ArcWrapper
    final = []
    ids = []
    for arc_path in arc_paths:
        arc_name = os.path.basename(arc_path)
        try:
            arc = ArcWrapper(arc_path)
        except Exception:  # TODO: skip/xfail
            continue
        file_entries = arc.get_file_entries_by_extension(file_extension)
        if not file_entries:
            del arc
            continue
        for fe in file_entries:
            final.append((arc, fe, app_id))
            ids.append("::".join((arc_name, f"{fe.file_path}.{file_extension}")))
    return final, ids
