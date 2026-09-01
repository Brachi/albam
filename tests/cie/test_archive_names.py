"""
CI-safe unit tests for albam.engines.cie.fs.split_archive_name - the rule
deciding how an .lfs's decompressed bytes get read (and, via the catalog
generator, what a dataset entry is tagged with). No game data needed.
"""
import pytest

from albam.engines.cie.fs import split_archive_name


@pytest.mark.parametrize("file_name,expected", [
    ("r20d.udas.lfs", ("r20d", ".udas")),
    ("icon_u.tpl.lfs", ("icon_u", ".tpl")),
    ("SizeTbl.dat.lfs", ("SizeTbl", ".dat")),
    # The extra ".yz2" is bookkeeping the game adds; the payload is a pack.
    ("0d104000.pack.yz2.lfs", ("0d104000", ".pack")),
    # The stem is everything up to the first dot, so a dotted stem would be
    # read as extensions. No real archive has one (every name in an install
    # is "<stem>.<payload>.lfs" or "<stem>.pack.yz2.lfs"), so this pins the
    # rule down rather than describing game data.
    ("a.b.c.pack.lfs", ("a", ".b")),
])
def test_split_archive_name(file_name, expected):
    assert split_archive_name(file_name) == expected


@pytest.mark.parametrize("file_name", ["nameless.lfs", "noextension", ""])
def test_split_archive_name_rejects_unidentifiable(file_name):
    with pytest.raises(ValueError):
        split_archive_name(file_name)
