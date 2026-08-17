import os

import pytest

from tests.mtfw.scripts.catalog_paths import (
    HASH_LENGTH,
    hash_identity,
    hash_relative_path,
    hash_virtual_path,
    normalize_virtual_path,
    to_portable_relative_path,
)


def test_to_portable_relative_path_strips_game_root():
    result = to_portable_relative_path(
        "/home/seba/games/RE5/nativePC_MT/Image/Archive/uPl00ChrisNormal.arc",
        "/home/seba/games/RE5",
    )
    assert result == "nativepc_mt/image/archive/upl00chrisnormal.arc"


def test_to_portable_relative_path_is_independent_of_install_location():
    # Two different "users" with the same game at different absolute paths
    # must produce the identical relative identity.
    a = to_portable_relative_path(
        "/home/seba/games/RE5/nativePC_MT/Image/Archive/uPl00ChrisNormal.arc",
        "/home/seba/games/RE5",
    )
    b = to_portable_relative_path(
        "/mnt/d/SteamLibrary/steamapps/common/Resident Evil 5/nativePC_MT/Image/Archive/uPl00ChrisNormal.arc",
        "/mnt/d/SteamLibrary/steamapps/common/Resident Evil 5",
    )
    assert a == b


def test_to_portable_relative_path_normalizes_current_os_separator():
    # absolute_path/game_root always come from THIS process's own os.walk(),
    # so they're always in this platform's own separator style already -
    # there's no real scenario where Windows-style paths reach this
    # function while running on Linux or vice versa. What has to hold is:
    # whatever os.sep this platform uses, it gets normalized to "/" so the
    # resulting hash matches what any other platform would produce for the
    # same relative structure.
    result = to_portable_relative_path(
        os.sep.join(["", "game", "Image", "Archive", "File.arc"]),
        os.sep.join(["", "game"]),
    )
    assert result == "image/archive/file.arc"


def test_to_portable_relative_path_normalizes_case():
    a = to_portable_relative_path("/game/Image/Archive/File.arc", "/game")
    b = to_portable_relative_path("/game/image/archive/file.arc", "/game")
    assert a == b == "image/archive/file.arc"


def test_to_portable_relative_path_rejects_paths_outside_game_root():
    with pytest.raises(ValueError):
        to_portable_relative_path("/etc/passwd", "/home/seba/games/RE5")


def test_hash_identity_is_deterministic_and_truncated():
    h1 = hash_identity("nativepc_mt/image/archive/upl00chrisnormal.arc")
    h2 = hash_identity("nativepc_mt/image/archive/upl00chrisnormal.arc")
    assert h1 == h2
    assert len(h1) == HASH_LENGTH
    assert all(c in "0123456789abcdef" for c in h1)


def test_hash_identity_differs_for_different_input():
    assert hash_identity("a.arc") != hash_identity("b.arc")


def test_normalize_virtual_path_strips_leading_slash_and_lowercases():
    assert normalize_virtual_path("/Pawn/Pl/pl00/Model/Pl0000.mod") == "pawn/pl/pl00/model/pl0000.mod"


def test_hash_virtual_path_matches_regardless_of_case():
    assert hash_virtual_path("/Pawn/Pl00.mod") == hash_virtual_path("/pawn/pl00.mod")


def test_hash_relative_path_matches_across_install_locations():
    # The end-to-end property that actually matters: two different "users"
    # owning the same game, at different absolute install paths, must
    # arrive at the same committed-catalog hash for the same real asset.
    h1 = hash_relative_path(
        "/home/seba/games/RE5/nativePC_MT/Image/Archive/uPl00ChrisNormal.arc",
        "/home/seba/games/RE5",
    )
    h2 = hash_relative_path(
        "/mnt/d/SteamLibrary/steamapps/common/Resident Evil 5/nativePC_MT/Image/Archive/uPl00ChrisNormal.arc",
        "/mnt/d/SteamLibrary/steamapps/common/Resident Evil 5",
    )
    assert h1 == h2
