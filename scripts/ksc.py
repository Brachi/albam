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
import re
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
DOWNLOAD_TIMEOUT_SECONDS = 60
# What a generated parser carrying a hand edit says next to it (see "Regenerating
# the Kaitai Struct parsers" in the README). Regenerating one drops the edit.
HAND_EDIT_MARKER = "deliberate hand edit"
PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


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
        with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response, \
                open(archive, "wb") as f:
            shutil.copyfileobj(response, f)
        verify_sha256(archive, sha256)
        unpacked = Path(tmp, "unpacked")
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(unpacked)
        (top,) = unpacked.iterdir()
        try:
            top.rename(version_dir)
        except OSError:
            # Another run installed it first, which is as good as this one.
            if not version_dir.is_dir():
                raise


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


def check_runtime_pin(pyproject=PYPROJECT):
    """Refuse to run when pyproject.toml pins a different kaitaistruct runtime:
    generated parsers target the runtime of the compiler that wrote them."""
    if not pyproject.is_file():
        return
    match = re.search(r'"kaitaistruct==([^"]+)"', pyproject.read_text(encoding="utf-8"))
    if match and match.group(1) != KSC_VERSION:
        raise SystemExit(
            f"pyproject.toml pins kaitaistruct=={match.group(1)} but this script runs compiler "
            f"{KSC_VERSION}. Move KSC_VERSION and KSC_SHA256 together with the pin."
        )


def output_dir(argv):
    """The --outdir/-d the compiler will write to, as it would read it."""
    for i, arg in enumerate(argv):
        if arg in ("--outdir", "-d") and i + 1 < len(argv):
            return Path(argv[i + 1])
        if arg.startswith("--outdir="):
            return Path(arg.split("=", 1)[1])
    return Path(".")


def hand_edited_parsers(directory):
    """The generated parsers under `directory` that carry HAND_EDIT_MARKER."""
    found = set()
    for path in directory.rglob("*.py"):
        try:
            if HAND_EDIT_MARKER in path.read_text(encoding="utf-8", errors="ignore"):
                found.add(path)
        except OSError:
            continue
    return found


def main(argv):
    check_runtime_pin()
    java = java_command()
    version_dir = cache_dir() / KSC_VERSION
    if not version_dir.is_dir():
        install(version_dir)

    outdir = output_dir(argv)
    hand_edited = hand_edited_parsers(outdir) if outdir.is_dir() else set()
    cmd = [java, "-cp", classpath(version_dir), KSC_MAIN_CLASS, *argv]
    status = subprocess.call(cmd)

    dropped = sorted(path for path in hand_edited if path not in hand_edited_parsers(outdir))
    for path in dropped:
        print(f"WARNING: regenerated {path}, which carried a hand edit the compiler does not "
              f"produce. Reapply it from the previous version (git diff {path}).", file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
