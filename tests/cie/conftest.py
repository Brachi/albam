import os

import pytest

from albam.lib import fs_registry

from tests.mtfw.r2_config import R2_PROTOCOL_PREFIX, resolve_r2_source

# app_id -> the directory its archives were fetched into this session.
_DOWNLOADED = {}


def _cie_game_dirs(pytestconfig):
    # Reuses the shared --game-dir option (see tests/conftest.py).
    parsed = {}
    for entry in pytestconfig.getoption("game_dir") or []:
        parts = entry.split("::")
        parsed[parts[0]] = parts[1]
    return parsed


def _fetch_from_r2(value, destination):
    """Download every archive under an "r2://<bucket>/<prefix>" into
    `destination`, and return it - or None if R2 is not configured.

    Downloaded rather than read in place, which the other engines do not
    need to do. Their filesystems read an archive's header over a range
    request and only fetch what a test touches; an .lfs has to be
    decompressed whole before anything in it can be listed, so streaming it
    would fetch the whole object anyway. The curated set is small, and this
    keeps every test working against a plain directory.
    """
    from albam.lib.s3 import build_s3_client

    r2 = resolve_r2_source(value)
    if r2 is None:
        return None

    client = build_s3_client(
        endpoint_url=r2["endpoint_url"],
        aws_access_key_id=r2["aws_access_key_id"],
        aws_secret_access_key=r2["aws_secret_access_key"],
    )
    prefix = r2["prefix"].strip("/")
    paginator = client.get_paginator("list_objects_v2")
    count = 0
    # Everything under the prefix, not just the .lfs archives the datasets
    # name: a model's texture pack is found by scanning the directory beside
    # it, and ships either compressed or as a plain file.
    for page in paginator.paginate(Bucket=r2["bucket"], Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            relative = key[len(prefix):].lstrip("/") if prefix else key
            path = os.path.join(destination, relative.replace("/", os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path) or os.path.getsize(path) != obj["Size"]:
                client.download_file(r2["bucket"], key, path)
            count += 1
    return destination if count else None


@pytest.fixture(scope="session")
def game_root(pytestconfig, local_app_id, tmp_path_factory):
    """
    A directory holding this app's archives, from
    --game-dir=<app-id>::<game-root>, where the value is either a real
    install root or "r2://<bucket>/<prefix>" (fetched once per session, see
    _fetch_from_r2).

    Unlike the other engines' equivalents this is a plain directory, not a
    mounted whole-game filesystem: there is no CieFS to mount (see
    albam/engines/cie/fs.py for why), so tests mount the individual archives
    their dataset names instead.

    Skips cleanly when no --game-dir was given for this app_id.
    """
    game_dirs = _cie_game_dirs(pytestconfig)
    if local_app_id not in game_dirs:
        pytest.skip(f"No --game-dir supplied for app_id={local_app_id!r}")

    root = game_dirs[local_app_id]
    if root.startswith(R2_PROTOCOL_PREFIX):
        if local_app_id not in _DOWNLOADED:
            destination = str(tmp_path_factory.mktemp(f"{local_app_id}-r2"))
            _DOWNLOADED[local_app_id] = _fetch_from_r2(root, destination)
        root = _DOWNLOADED[local_app_id]
        if root is None:
            pytest.skip(
                f"--game-dir={local_app_id}::{game_dirs[local_app_id]} requested but R2 "
                f"isn't configured (empty bucket, missing s3 extras, or missing "
                f"credentials - see .env.example), or the prefix holds no archives")
        return root

    if not os.path.isdir(root):
        pytest.skip(f"--game-dir={local_app_id}::{root} does not exist")
    return root


def close_new_fs_roots(before):
    """Close the FS roots registered since `before` was taken.

    Not fs_registry.clear(): that closes every filesystem in the process.
    Session-scoped parametrization interleaves this suite's tests with
    tests/mtfw's, whose game_fs_root is one session-scoped MTFW_FS shared by
    every test in it - so clearing here closed it mid-run and every mtfw test
    after this point failed with FilesystemClosed.
    """
    for key in fs_registry.keys():
        if key not in before:
            fs_registry.unregister(key)
