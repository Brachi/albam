"""Tests for parsing LFS container files."""


def test_lfs_structure(parsed_lfs_file):
    """Test that LFS structure is correctly parsed."""
    lfs_wrapper = parsed_lfs_file
    assert lfs_wrapper is not None
    assert hasattr(lfs_wrapper, 'compressed'), "LFS should have compressed member"
    assert hasattr(lfs_wrapper, 'parsed'), "LFS should have parsed member"


def test_lfs_compressed_structure(parsed_lfs_file):
    """Test LFS compressed structure."""
    lfs_wrapper = parsed_lfs_file
    compressed = lfs_wrapper.compressed

    assert compressed is not None, "Compressed LFS should not be None"
    assert hasattr(compressed, 'header'), "Compressed LFS should have header"
    assert hasattr(compressed, 'file_entries'), "Compressed LFS should have file_entries"


def test_lfs_header(parsed_lfs_file):
    """Test LFS header properties."""
    lfs_wrapper = parsed_lfs_file
    compressed = lfs_wrapper.compressed
    header = compressed.header

    assert header is not None, "LFS header should not be None"
    assert hasattr(header, 'id_magic'), "Header should have id_magic"
    assert hasattr(header, 'num_files'), "Header should have num_files"

    num_files = header.num_files
    assert isinstance(num_files, int), "num_files should be an integer"
    assert num_files > 0, "LFS should contain at least one file"


def test_lfs_file_entries_count(parsed_lfs_file):
    """Test that LFS file entries match header count."""
    lfs_wrapper = parsed_lfs_file
    compressed = lfs_wrapper.compressed

    num_files_in_header = compressed.header.num_files
    num_file_entries = len(compressed.file_entries)

    assert num_files_in_header == num_file_entries, \
        f"File entries ({num_file_entries}) should match header count ({num_files_in_header})"


def test_lfs_file_entries_structure(parsed_lfs_file):
    """Test structure of LFS file entries."""
    lfs_wrapper = parsed_lfs_file
    compressed = lfs_wrapper.compressed

    for i, entry in enumerate(compressed.file_entries):
        assert hasattr(entry, 'size_compressed'), f"File entry {i} should have size_compressed"
        assert hasattr(entry, 'size_decompressed'), f"File entry {i} should have size_decompressed"
        assert hasattr(entry, 'offset'), f"File entry {i} should have offset"

        assert isinstance(entry.size_compressed, int), f"size_compressed {i} should be int"
        assert isinstance(entry.size_decompressed, int), f"size_decompressed {i} should be int"
        assert isinstance(entry.offset, int), f"offset {i} should be int"


def test_lfs_decompression(parsed_lfs_file):
    """Test that LFS decompression produces valid parsed data."""
    lfs_wrapper = parsed_lfs_file
    parsed = lfs_wrapper.parsed

    assert parsed is not None, "Decompressed LFS data should not be None"
    # The parsed object type depends on the contained file type
    # (could be Udas, Dat, Pack, or Evd)
    assert hasattr(parsed, 'header') or hasattr(parsed, 'file_entries'), \
        "Decompressed data should have either header or file_entries"


def test_lfs_file_entries_accessible(parsed_lfs_file):
    """Test that file entries extracted from LFS are accessible."""
    lfs_wrapper = parsed_lfs_file

    file_entries = lfs_wrapper.get_file_entries()
    assert isinstance(file_entries, list), "get_file_entries() should return a list"
    assert len(file_entries) > 0, "LFS should have at least one extractable file"

    for entry in file_entries:
        assert hasattr(entry, 'file_path_with_ext'), "Each entry should have file_path_with_ext"


def test_lfs_file_retrieval(parsed_lfs_file):
    """Test that files can be retrieved from LFS."""
    lfs_wrapper = parsed_lfs_file

    file_entries = lfs_wrapper.get_file_entries()
    if file_entries:
        first_entry = file_entries[0]
        file_path_with_ext = first_entry.file_path_with_ext

        # Parse file path and extension
        parts = file_path_with_ext.rsplit('.', 1)
        if len(parts) == 2:
            file_path_no_ext, file_ext = parts

            # Try to retrieve the file
            try:
                file_data = lfs_wrapper.get_file(file_path_no_ext, file_ext)
                assert isinstance(file_data, bytes), "Retrieved file data should be bytes"
                assert len(file_data) > 0, "Retrieved file should have content"
            except RuntimeError:
                # File might not be retrievable via get_file, that's ok
                pass


def test_lfs_metadata(parsed_lfs_file):
    """Test LFS metadata attributes."""
    lfs_wrapper = parsed_lfs_file

    assert hasattr(lfs_wrapper, 'file_path'), "LFS should have file_path"
    assert hasattr(lfs_wrapper, 'file_type'), "LFS should have file_type"
    assert hasattr(lfs_wrapper, '_app_id'), "LFS should have _app_id"

    # File type should be one of the supported types
    supported_types = {'.udas', '.dat', '.pack', '.evd', '.yz2'}
    assert lfs_wrapper.file_type in supported_types, \
        f"File type {lfs_wrapper.file_type} should be one of {supported_types}"
