#!/usr/bin/env python3
"""
Run the Kaitai Struct compiler at the version albam's parsers are generated
with, downloading it on first use.

    python scripts/ksc.py --target python -w --outdir . <file>.ksy

Every argument is passed straight through to kaitai-struct-compiler, so this
is a drop-in for it (see "Regenerating the Kaitai Struct parsers" in the
README). The compiler version is pinned here next to its checksum and has to
move together with pyproject.toml's `kaitaistruct` runtime pin: generated
parsers target the runtime of the compiler that wrote them.

The release zip is the same on every platform - the compiler is a JVM
program, seven .jar files - so Java is the only prerequisite. It's started
directly rather than through the zip's own bin/ launchers, which differ per
platform (a .bat on Windows, where passing arguments through cmd.exe has its
own quoting rules).

The unpacked compiler is cached per version under the platform's cache
directory, next to albam's S3 cache (see albam.lib.s3.default_cache_dir);
deleting it is always safe. ALBAM_KSC_DIR overrides the location.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

KSC_VERSION = "0.11"
KSC_URL = (
    "https://github.com/kaitai-io/kaitai_struct_compiler/releases/download/"
    f"{KSC_VERSION}/kaitai-struct-compiler-{KSC_VERSION}.zip"
)
KSC_SHA256 = "ff89389d9dc9e770d78a24af328763cb1f8e7b31ce7766c9edf10669a060f2a2"
KSC_MAIN_CLASS = "io.kaitai.struct.JavaMain"


def default_cache_dir():
    """Same platform conventions as albam.lib.s3.default_cache_dir, which
    can't be imported from here without pulling in albam (and bpy with it).
    """
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
        return Path(base, "albam", "cache", "ksc")
    if sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Caches/albam/ksc"))
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return Path(base, "albam", "ksc")


def cache_dir():
    override = os.environ.get("ALBAM_KSC_DIR")
    return Path(override) if override else default_cache_dir()


def verify_sha256(path, expected):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise SystemExit(
            f"Checksum mismatch for {path}: expected {expected}, got {digest.hexdigest()}. "
            "Not using it."
        )


def install(version_dir, url=KSC_URL, sha256=KSC_SHA256):
    """Download, verify and unpack into version_dir. Unpacks into a sibling
    temp dir and renames it into place, so an interrupted run never leaves a
    half-extracted compiler that looks installed.
    """
    version_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=version_dir.parent) as tmp:
        archive = Path(tmp, "ksc.zip")
        print(f"Downloading kaitai-struct-compiler {KSC_VERSION}...", file=sys.stderr)
        with urllib.request.urlopen(url) as response, open(archive, "wb") as f:
            shutil.copyfileobj(response, f)
        verify_sha256(archive, sha256)
        unpacked = Path(tmp, "unpacked")
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(unpacked)
        (top,) = unpacked.iterdir()
        top.rename(version_dir)


def classpath(version_dir):
    jars = sorted((version_dir / "lib").glob("*.jar"))
    if not jars:
        raise SystemExit(f"No .jar files under {version_dir / 'lib'} - delete {version_dir} and rerun.")
    return os.pathsep.join(str(jar) for jar in jars)


def java_command():
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = Path(java_home, "bin", "java.exe" if sys.platform == "win32" else "java")
        if candidate.is_file():
            return str(candidate)
    java = shutil.which("java")
    if java is None:
        raise SystemExit(
            "kaitai-struct-compiler needs Java, and none was found on PATH or in JAVA_HOME. "
            "Any JRE/JDK 8+ works, e.g. Eclipse Temurin (https://adoptium.net)."
        )
    return java


def main(argv):
    version_dir = cache_dir() / KSC_VERSION
    if not version_dir.is_dir():
        install(version_dir)
    cmd = [java_command(), "-cp", classpath(version_dir), KSC_MAIN_CLASS, *argv]
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
