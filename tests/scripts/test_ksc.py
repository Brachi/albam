"""Covers scripts/ksc.py's install layer - checksum, unpack, cache location -
against a small zip built on the fly.

CI-safe: nothing here downloads the real compiler or needs Java. install()
fetches through urllib, which reads file:// URLs just as well.
"""
import hashlib
import importlib.util
import os
import zipfile
from pathlib import Path

import pytest

KSC_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ksc.py"
_spec = importlib.util.spec_from_file_location("ksc", KSC_PATH)
ksc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ksc)


@pytest.fixture
def fake_release(tmp_path):
    """A zip shaped like the real release: one top-level dir with lib/*.jar."""
    archive = tmp_path / "release.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("kaitai-struct-compiler-0.11/lib/b.jar", b"b")
        zf.writestr("kaitai-struct-compiler-0.11/lib/a.jar", b"a")
        zf.writestr("kaitai-struct-compiler-0.11/bin/kaitai-struct-compiler", b"#!/bin/sh\n")
    sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive.as_uri(), sha256


def test_install_unpacks_the_release_into_the_version_dir(tmp_path, fake_release):
    url, sha256 = fake_release
    version_dir = tmp_path / "cache" / "0.11"
    ksc.install(version_dir, url=url, sha256=sha256)
    assert (version_dir / "lib" / "a.jar").read_bytes() == b"a"
    assert (version_dir / "bin" / "kaitai-struct-compiler").is_file()


def test_install_refuses_a_checksum_mismatch_and_leaves_nothing_behind(tmp_path, fake_release):
    """A bad download must not end up looking installed: main() only checks
    that the version dir exists before running from it.
    """
    url, _ = fake_release
    cache = tmp_path / "cache"
    with pytest.raises(SystemExit, match="Checksum mismatch"):
        ksc.install(cache / "0.11", url=url, sha256="0" * 64)
    assert list(cache.iterdir()) == []


def test_classpath_lists_every_jar_in_order(tmp_path, fake_release):
    url, sha256 = fake_release
    version_dir = tmp_path / "0.11"
    ksc.install(version_dir, url=url, sha256=sha256)
    lib = version_dir / "lib"
    assert ksc.classpath(version_dir) == os.pathsep.join([str(lib / "a.jar"), str(lib / "b.jar")])


def test_classpath_rejects_a_version_dir_without_jars(tmp_path):
    (tmp_path / "lib").mkdir()
    with pytest.raises(SystemExit, match="No .jar files"):
        ksc.classpath(tmp_path)


def test_cache_dir_honors_the_override(monkeypatch, tmp_path):
    monkeypatch.setenv("ALBAM_KSC_DIR", str(tmp_path))
    assert ksc.cache_dir() == tmp_path


def test_cache_dir_defaults_to_the_platform_cache(monkeypatch):
    monkeypatch.delenv("ALBAM_KSC_DIR", raising=False)
    assert ksc.cache_dir() == ksc.default_cache_dir()
    assert ksc.cache_dir().parts[-1] == "ksc"
