import os

import pytest

from albam.mtframework import Arc, KNOWN_ARC_FAILS
from tests.conftest import SAMPLES_DIR


@pytest.fixture(scope='session')
def arc_re5_samples(config=None):
    samples_dir = pytest.config.getoption('--dirarc') or os.path.join(SAMPLES_DIR, 're5/arc')
    CORRUPTED_ARCS = {'uOmf303.arc', 's101.arc', 'uOmS103ScrAdj.arc'}
    return [os.path.join(root, f)
            for root, _, files in os.walk(samples_dir)
            for f in files if f.endswith('.arc') and f.startswith('s') and f not in CORRUPTED_ARCS]


@pytest.mark.parametrize("arc_file", arc_re5_samples())
def test_arc_unpack_re5(tmpdir, arc_file):
    if arc_file.endswith(KNOWN_ARC_FAILS):
        pytest.xfail()
    arc = Arc(file_path=arc_file)
    out = os.path.join(str(tmpdir), 'extracted_arc')

    arc.unpack(out)

    files = {os.path.join(root, f) for root, _, files in os.walk(out)
             for f in files}
    expected_sizes = sorted([f.size for f in arc.file_entries if f.size])
    files_sizes = sorted([os.path.getsize(f) for f in files])

    assert os.path.isdir(out)
    assert arc.files_count == len(files)
    assert expected_sizes == files_sizes


@pytest.mark.parametrize('arc_file', arc_re5_samples())
def test_arc_from_dir_re5(tmpdir, arc_file):
    """get an arc file (ideally from the game), unpack it, repackit, unpack it again
    compare the 2 arc files and the 2 output folders"""

    if arc_file.endswith(KNOWN_ARC_FAILS):
        pytest.xfail()
    arc_original = Arc(file_path=arc_file)
    arc_original_out = os.path.join(str(tmpdir), os.path.basename(arc_file).replace('.arc', ''))
    arc_original.unpack(arc_original_out)

    arc_from_dir = Arc.from_dir(arc_original_out)
    arc_from_dir_out = os.path.join(str(tmpdir), 'arc-from-dir.arc')
    with open(arc_from_dir_out, 'wb') as w:
        w.write(arc_from_dir)

    arc_from_arc_from_dir = Arc(file_path=arc_from_dir_out)
    arc_from_arc_from_dir_out = os.path.join(str(tmpdir), 'arc-from-arc-from-dir')
    arc_from_arc_from_dir.unpack(arc_from_arc_from_dir_out)

    files_extracted_1 = [f for _, _, files in os.walk(arc_original_out) for f in files]
    files_extracted_2 = [f for _, _, files in os.walk(arc_from_arc_from_dir_out) for f in files]

    # Assumming zlib default compression used in all original arc files.
    assert os.path.getsize(arc_file) == os.path.getsize(arc_from_dir_out)
    # The hashes would be different due to the file_paths ordering
    assert arc_original.files_count == arc_from_arc_from_dir.files_count
    assert sorted(files_extracted_1) == sorted(files_extracted_2)
    assert arc_from_arc_from_dir.file_entries[0].offset == 32768
