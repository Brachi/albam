"""Tests for parsing UDAS files from LFS containers."""


def test_udas_structure(parsed_udas_from_lfs):
    """Test that UDAS structure is correctly parsed."""
    udas = parsed_udas_from_lfs
    assert udas is not None
    assert hasattr(udas, 'header'), "UDAS should have header"


def test_udas_header(parsed_udas_from_lfs):
    """Test UDAS header properties."""
    udas = parsed_udas_from_lfs
    header = udas.header

    assert header is not None, "UDAS header should not be None"
    assert hasattr(header, 'id_magic'), "Header should have id_magic"
    assert hasattr(header, 'file_size'), "Header should have file_size"


def test_udas_data_blocks(parsed_udas_from_lfs):
    """Test UDAS data blocks structure."""
    udas = parsed_udas_from_lfs
    header = udas.header

    assert hasattr(header, 'data_blocks'), "Header should have data_blocks"
    data_blocks = header.data_blocks

    assert hasattr(data_blocks, 'file_entries'), "Data blocks should have file_entries"
    assert hasattr(data_blocks, 'file_extension'), "Data blocks should have file_extension"

    # Check that file_entries and extensions match in count
    num_files = len(data_blocks.file_entries)
    num_exts = len(data_blocks.file_extension)
    assert num_files == num_exts, f"File entries ({num_files}) should match extensions ({num_exts})"


def test_udas_file_entries(parsed_udas_from_lfs):
    """Test UDAS file entries are accessible."""
    udas = parsed_udas_from_lfs
    file_entries = udas.header.data_blocks.file_entries

    assert len(file_entries) > 0, "UDAS should contain at least one file entry"

    for i, entry in enumerate(file_entries):
        assert hasattr(entry, 'raw_data'), f"File entry {i} should have raw_data"
        assert isinstance(entry.raw_data, bytes), f"File entry {i} raw_data should be bytes"


def test_udas_file_extensions(parsed_udas_from_lfs):
    """Test UDAS file extensions are accessible."""
    udas = parsed_udas_from_lfs
    extensions = udas.header.data_blocks.file_extension

    assert len(extensions) > 0, "UDAS should contain at least one extension entry"

    for i, ext_entry in enumerate(extensions):
        assert hasattr(ext_entry, 'ext'), f"Extension entry {i} should have ext field"
        # ext field is a string (null-terminated)
        assert isinstance(ext_entry.ext, str), f"Extension {i} should be a string"


def test_udas_metadata(parsed_udas_from_lfs):
    """Test UDAS metadata attributes added during parsing."""
    udas = parsed_udas_from_lfs

    # These are set by the fixture
    assert hasattr(udas, '_arc_name'), "UDAS should have _arc_name attribute"
    assert hasattr(udas, '_lfs_path'), "UDAS should have _lfs_path attribute"
    assert hasattr(udas, '_num_bytes'), "UDAS should have _num_bytes attribute"

    assert isinstance(udas._num_bytes, int), "Number of bytes should be an integer"
    assert udas._num_bytes > 0, "UDAS should have non-zero size"
