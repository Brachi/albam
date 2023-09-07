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


def _generate_tests_mrl(metafunc):
    """
    Generate one parsed mrl object per test, based on provided arcs.
    Defer decompression and parsing to test-run time, not
    collection time
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

    mrls, ids = mrls_per_arc(ARC_FILES)
    # mrl fixture in tests/mtfw/conftest.py
    metafunc.parametrize("mrl", mrls, indirect=True, ids=ids)


def mrls_per_arc(arc_paths):
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found
    from albam.engines.mtfw.archive import ArcWrapper
    final = []
    ids = []
    for arc_path in arc_paths:
        arc_name = os.path.basename(arc_path)
        arc = ArcWrapper(None, arc_path)
        mrls_fe = arc.get_file_entries_by_extension("mrl")
        if not mrls_fe:
            continue
        for mrl in mrls_fe:
            final.append((arc, mrl))
            ids.append("::".join((arc_name, mrl.file_path + ".mrl")))
    return final, ids
