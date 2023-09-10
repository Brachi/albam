import os

import pytest


def _generate_tests_arc_file_path(metafunc):
    arc_dir = metafunc.config.getoption("arcdir")
    if not arc_dir:
        pytest.skip("No arc directory supplied")
        return

    ARC_FILES = [
        os.path.join(root, f)
        for root, _, files in os.walk(arc_dir)
        for f in files
        if f.endswith(".arc")
    ]
    arc_names = [os.path.basename(f) for f in ARC_FILES]
    metafunc.parametrize("arc_filepath", ARC_FILES, ids=arc_names)


def _generate_tests_from_arcs(file_extension, metafunc):
    """
    Generate one parsed object for file_extension, based on provided arcs.
    Defer decompression and parsing to test-run time, not
    collection time.
    It requires a fixture named after the extension
    """
    arc_dir = metafunc.config.getoption("arcdir")
    if not arc_dir:
        pytest.skip("No arc directory supplied")
        return

    ARC_FILES = [
        os.path.join(root, f)
        for root, _, files in os.walk(arc_dir)
        for f in files
        if f.endswith(".arc")
    ]

    if not ARC_FILES:
        raise ValueError(f"No files ending in .arc found in {arc_dir}")

    parsed_files, ids = files_per_arc(file_extension, ARC_FILES)
    # mrl fixture in tests/mtfw/conftest.py
    metafunc.parametrize(file_extension, parsed_files, indirect=True, ids=ids)


def files_per_arc(file_extension, arc_paths):
    # importing here to avoid errors in test collection.
    # Since collection happens before calling register() in `pytest_sessionstart`
    # sys.path is not modified to include albam_vendor, so the vendored dep kaitaistruct
    # is not found when needed.
    from albam.engines.mtfw.archive import ArcWrapper
    final = []
    ids = []
    for arc_path in arc_paths:
        arc_name = os.path.basename(arc_path)
        arc = ArcWrapper(None, arc_path)
        file_entries = arc.get_file_entries_by_extension(file_extension)
        if not file_entries:
            del arc
            continue
        for fe in file_entries:
            final.append((arc, fe))
            ids.append("::".join((arc_name, f"{fe.file_path}.{file_extension}")))
    return final, ids
