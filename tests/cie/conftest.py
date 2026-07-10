import os
import pytest

LFS_DIRS = None


def pytest_generate_tests(metafunc):
    if "parsed_udas_from_lfs" in metafunc.fixturenames:
        _generate_tests_from_lfs("udas", metafunc, "parsed_udas_from_lfs")
    elif "parsed_lfs_file" in metafunc.fixturenames:
        _generate_tests_from_lfs("lfs", metafunc, "parsed_lfs_file")


@pytest.fixture
def parsed_udas_from_lfs(request):
    """
    Parse UDAS file extracted from LFS container.

    request.param is a tuple of (lfs_wrapper, file_index)
    """
    # test collection before calling register() in pytest_session_start
    # doesn't have sys.path modified for albam_vendor, so kaitaistruct
    # not found

    lfs_wrapper, file_index = request.param

    # For UDAS files, the file_type is determined from the LFS header
    if lfs_wrapper.file_type == ".udas":
        udas = lfs_wrapper.parsed
        udas._arc_name = os.path.basename(lfs_wrapper.file_path)
        udas._lfs_path = lfs_wrapper.file_path
        udas._num_bytes = sum(fe.size_compressed for fe in lfs_wrapper.compressed.file_entries)
        return udas
    else:
        pytest.skip(f"Not a UDAS file: {lfs_wrapper.file_type}")


@pytest.fixture
def parsed_lfs_file(request):
    """
    Parse LFS container file.

    request.param is a tuple of (lfs_path, app_id)
    """
    from albam.engines.cie.archive import LfsWrapper

    lfs_path, app_id = request.param

    lfs_wrapper = LfsWrapper(lfs_path)
    lfs_wrapper._app_id = app_id

    return lfs_wrapper


LFS_FILES_CACHE = {}


def _generate_tests_from_lfs(file_type, metafunc, fixturename):
    """
    Generate one parsed object for file_type, based on provided lfs files.
    Defer decompression and parsing to test-run time, not collection time.
    It requires a fixture named after file_type
    """
    global LFS_DIRS, LFS_FILES_CACHE

    lfs_dirs = metafunc.config.getoption("lfsdir")
    if not lfs_dirs:
        pytest.skip("No lfs directory supplied")
        return

    if lfs_dirs and not LFS_DIRS:
        # if loading multiple times will generate multiple
        # tests even with scope=session. We want only one
        # per item in the dataset
        LFS_DIRS = lfs_dirs

    total_parsed_files = []
    total_test_ids = []

    for lfs_dir in LFS_DIRS:
        app_id, lfs_dir_path = lfs_dir.split("::")
        LFS_FILES = [
            os.path.join(root, f)
            for root, _, files in os.walk(lfs_dir_path)
            for f in files
            if f.endswith(".lfs")
        ]

        if not LFS_FILES:
            raise ValueError(f"No files ending in .lfs found in {lfs_dir_path}")

        parsed_files, ids = _files_per_lfs(file_type, LFS_FILES, app_id)
        total_parsed_files.extend(parsed_files)
        total_test_ids.extend(ids)

    metafunc.parametrize(fixturename, total_parsed_files, indirect=True, ids=total_test_ids)


def _files_per_lfs(file_type, lfs_paths, app_id):
    """
    Extract and parse files from LFS containers.

    For file_type == "udas": returns (lfs_wrapper, file_index) tuples
    For file_type == "lfs": returns (lfs_path, app_id) tuples
    """
    # importing here to avoid errors in test collection.
    # Since collection happens before calling register() in `pytest_sessionstart`
    # sys.path is not modified to include albam_vendor, so the vendored dep kaitaistruct
    # is not found when needed.
    from albam.engines.cie.archive import LfsWrapper

    final = []
    ids = []
    failed_lfs = []

    for lfs_path in lfs_paths:
        lfs_name = os.path.basename(lfs_path)
        try:
            lfs_wrapper = LfsWrapper(lfs_path)
        except OSError as err:
            if err.errno == 24:
                raise RuntimeError("Exceeded open file limits. Try running `ulimit -S -n 4096`")
        except Exception as e:
            failed_lfs.append((lfs_path, str(e)))
            continue

        if file_type == "udas":
            if lfs_wrapper.file_type == ".udas":
                # For UDAS, we return the whole wrapper
                # (since UDAS contains multiple files within one container)
                final.append((lfs_wrapper, 0))
                ids.append(f"{lfs_name}::udas")
            # If it's not a UDAS file, skip it
        elif file_type == "lfs":
            # For LFS, just return the file path and app_id
            final.append((lfs_path, app_id))
            ids.append(lfs_name)

    if failed_lfs:
        print(f"failed to load the following lfs files: {failed_lfs}")

    return final, ids
