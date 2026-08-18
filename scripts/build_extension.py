#!/usr/bin/env python3
"""
Build the Albam Blender extension zip.

Dependency versions are pinned in pylock.toml (PEP 751), the committed source
of truth for pyproject.toml's [project.dependencies] (bpy excluded - Blender
always provides its own). A normal build just downloads wheels from that lock
file and doesn't touch pyproject.toml at all:

    python scripts/build_extension.py [--output-dir dist]

When pyproject.toml's core dependencies change, regenerate the lock (writes
pylock.toml at the repo root, resolving the full transitive closure fresh
from PyPI) and commit the result:

    python scripts/build_extension.py --generate-lock

[project.optional-dependencies].<extra> groups (e.g. s3) aren't part of the
committed lock - passing --extra resolves+locks them fresh into a scratch
lock file for that build only:

    python scripts/build_extension.py --extra s3

Either way, the resulting wheels + a blender_manifest.toml with `wheels =
[...]` filled in get zipped into dist/albam-<version>.zip. Aborts if
pyproject.toml's version and albam/__version__.py disagree.

Assumes every resolved dependency ships a universal ("py3-none-any") wheel -
true for everything under [project.dependencies] today. If a future
dependency needs platform-specific wheels, this script's single
`pip download`/`pip lock` pass (no --platform/--python-version pins) would
need to become one pass per target platform instead.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

from packaging.requirements import Requirement

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
ADDON_DIR = REPO_ROOT / "albam"
MANIFEST_PATH = ADDON_DIR / "blender_manifest.toml"
VERSION_PATH = ADDON_DIR / "__version__.py"
VERSION_FILE_RE = re.compile(r'^__version__\s*=\s*"([^"]*)"', re.MULTILINE)
# Mirrors RE_MANIFEST_SEMVER in Blender's own
# scripts/addons_core/bl_pkg/cli/blender_ext.py - blender_manifest.toml's
# `version` field is validated as real SemVer 2.0.0 (build metadata like
# "+12.main" included), not the simpler digits-only pattern used for
# blender_version_min/max.
MANIFEST_SEMVER_RE = re.compile(
    r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)?"
    r"(?:\+[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)?$"
)
MANIFEST_VERSION_LINE_RE = re.compile(r'^version\s*=\s*"[^"]*"', re.MULTILINE)
# pip only recognizes PEP 751 lock files by this exact filename pattern
# ("pylock.toml" or "pylock.<name>.toml") - content sniffing isn't enough,
# confirmed by pip silently mis-parsing a differently-named file as a plain
# requirements.txt instead of erroring.
LOCK_PATH = REPO_ROOT / "pylock.toml"


def _load_pyproject():
    with open(PYPROJECT_PATH, "rb") as f:
        return tomllib.load(f)


def _check_version_files_match(pyproject_version):
    # Not parsed via import: albam/__init__.py needs bpy, which this script
    # can't assume is installed.
    match = VERSION_FILE_RE.search(VERSION_PATH.read_text())
    if not match:
        raise SystemExit(f"Couldn't find __version__ = \"...\" in {VERSION_PATH}")
    file_version = match.group(1)
    if file_version != pyproject_version:
        raise SystemExit(
            f"Version mismatch: pyproject.toml has {pyproject_version!r}, "
            f"{VERSION_PATH} has {file_version!r} - keep them in sync"
        )


def _requirement_strings(pyproject, extras):
    project = pyproject["project"]
    reqs = list(project.get("dependencies", []))
    optional = project.get("optional-dependencies", {})
    for extra in extras:
        try:
            reqs.extend(optional[extra])
        except KeyError:
            raise SystemExit(f"--extra {extra!r} is not defined under [project.optional-dependencies]")
    return reqs


def _filter_out_bpy(requirement_strings):
    # bpy is Blender itself - never bundle it, and it wouldn't resolve via
    # pip download anyway (it's not on PyPI as a real package for every
    # version pinned here).
    return [r for r in requirement_strings if Requirement(r).name.lower() != "bpy"]


def _generate_lock_file(requirement_strings, lock_path):
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "lock",
        "--only-binary=:all:",
        "-o",
        str(lock_path),
    ] + requirement_strings
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def _wheel_names_from_lock(lock_path):
    with open(lock_path, "rb") as f:
        lock = tomllib.load(f)
    return [wheel["name"] for package in lock.get("packages", []) for wheel in package.get("wheels", [])]


def _download_wheels_from_lock(lock_path, wheels_dir):
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--dest",
        str(wheels_dir),
        "--only-binary=:all:",
        "-r",
        str(lock_path),
    ]
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def _write_manifest(wheel_filenames, dest_path, version_override=None):
    manifest_text = MANIFEST_PATH.read_text()
    wheel_lines = "\n".join(f'  "./wheels/{name}",' for name in sorted(wheel_filenames))
    new_wheels_block = f"wheels = [\n{wheel_lines}\n]\n" if wheel_filenames else "wheels = [\n]\n"

    start = manifest_text.index("wheels = [")
    end = manifest_text.index("]", start) + 1
    # skip the trailing newline after the closing bracket, if present
    if end < len(manifest_text) and manifest_text[end] == "\n":
        end += 1
    manifest_text = manifest_text[:start] + new_wheels_block + manifest_text[end:]

    if version_override:
        new_version_line = f'version = "{version_override}"'
        manifest_text = MANIFEST_VERSION_LINE_RE.sub(new_version_line, manifest_text, count=1)

    dest_path.write_text(manifest_text)


def _stage_addon(staging_root):
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
    shutil.copytree(ADDON_DIR, staging_root, ignore=ignore)


def _check_universal_wheels(wheel_filenames):
    # blender_manifest.toml declares both windows-x64 and linux-x64, and
    # Blender itself spans multiple bundled Python versions (3.11 for
    # bpy==4.2.0, 3.13 for bpy==5.2.0) - a single `pip download` pass (no
    # --platform/--abi/--python-version pins) only ever fetches wheels
    # compatible with *this* machine. That's fine as long as every resolved
    # wheel is universal ("none-any"); a platform/abi-specific wheel slipping
    # through would silently work here and silently break everywhere else.
    universal_suffixes = ("-py3-none-any.whl", "-py2.py3-none-any.whl")
    non_universal = [name for name in wheel_filenames if not name.endswith(universal_suffixes)]
    if non_universal:
        names = ", ".join(sorted(non_universal))
        raise SystemExit(
            f"Refusing to bundle non-universal wheel(s): {names}\n"
            "These were built for this machine's platform/Python only and would silently "
            "break on other declared platforms (windows-x64/linux-x64) or Blender's other "
            "bundled Python version. This script needs a --platform/--abi/--python-version "
            "pinned `pip download` pass per target instead of the current single pass."
        )


def generate_lock():
    pyproject = _load_pyproject()
    requirement_strings = _filter_out_bpy(_requirement_strings(pyproject, extras=[]))
    print(f"Locking {len(requirement_strings)} top-level requirement(s) into {LOCK_PATH} ...")
    for r in requirement_strings:
        print(f"  - {r}")
    _generate_lock_file(requirement_strings, LOCK_PATH)
    _check_universal_wheels(_wheel_names_from_lock(LOCK_PATH))
    print(f"Wrote {LOCK_PATH} - review and commit it.")


def build(extras, output_dir, version_override=None):
    pyproject = _load_pyproject()
    version = version_override or pyproject["project"]["version"]
    _check_version_files_match(pyproject["project"]["version"])
    if version_override and not MANIFEST_SEMVER_RE.match(version_override):
        raise SystemExit(
            f"--version {version_override!r} is not valid SemVer 2.0.0 - Blender's own "
            "blender_manifest.toml validator would reject it too"
        )

    with tempfile.TemporaryDirectory(prefix="albam-extension-build-") as tmp:
        tmp = Path(tmp)
        staging_root = tmp / "albam"
        wheels_dir = staging_root / "wheels"

        print(f"Staging addon files from {ADDON_DIR} ...")
        _stage_addon(staging_root)

        if extras:
            # Extras aren't part of the committed core lock - resolve+lock
            # them fresh into a scratch pylock.toml for this build only,
            # rather than mixing them into the committed one.
            requirement_strings = _filter_out_bpy(_requirement_strings(pyproject, extras))
            lock_path = tmp / "pylock.toml"
            print(f"Locking core + extra(s) {extras} for this build only (not committed) ...")
            _generate_lock_file(requirement_strings, lock_path)
        else:
            if not LOCK_PATH.exists():
                raise SystemExit(f"{LOCK_PATH} not found - run with --generate-lock first")
            lock_path = LOCK_PATH

        print(f"Downloading wheels from {lock_path} ...")
        wheels_dir.mkdir(exist_ok=True)
        _download_wheels_from_lock(lock_path, wheels_dir)

        wheel_filenames = [p.name for p in wheels_dir.glob("*.whl")]
        if not wheel_filenames:
            raise SystemExit(f"pip download produced no wheels from {lock_path} - aborting")
        _check_universal_wheels(wheel_filenames)
        print(f"Bundled {len(wheel_filenames)} wheel(s):")
        for name in sorted(wheel_filenames):
            print(f"  - {name}")

        manifest_dest = staging_root / "blender_manifest.toml"
        _write_manifest(wheel_filenames, manifest_dest, version_override=version_override)

        output_dir.mkdir(parents=True, exist_ok=True)
        zip_path = output_dir / f"albam-{version}.zip"
        if zip_path.exists():
            zip_path.unlink()

        print(f"Writing {zip_path} ...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(staging_root.rglob("*")):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(staging_root))

    print(f"Done: {zip_path}")
    return zip_path


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--generate-lock",
        action="store_true",
        help=f"Regenerate {LOCK_PATH.name} from pyproject.toml's core dependencies and exit, "
        "without building the zip.",
    )
    parser.add_argument(
        "--extra",
        action="append",
        default=[],
        dest="extras",
        help="Additional [project.optional-dependencies] group to bundle (e.g. s3). Repeatable. "
        "Locked fresh for this build only, not added to the committed lock file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "dist",
        help="Directory to write the resulting zip into (default: ./dist)",
    )
    parser.add_argument(
        "--version",
        dest="version_override",
        default=None,
        help="Override both the packaged manifest's `version` field and the zip filename's version "
        "(default: pyproject.toml's project.version, left untouched). Must be valid SemVer 2.0.0 - "
        "e.g. '0.5.0+12.main' - since that's what Blender's own manifest validator requires.",
    )
    args = parser.parse_args()
    if args.generate_lock:
        if args.extras:
            raise SystemExit("--generate-lock and --extra can't be combined - the lock covers core deps only")
        generate_lock()
    else:
        build(args.extras, args.output_dir, version_override=args.version_override)


if __name__ == "__main__":
    main()
