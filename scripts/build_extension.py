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

Wheels are downloaded once per (platform, Python version) target, so a
dependency shipping platform-specific wheels (bc7enc-py) ends up in the zip
for every platform blender_manifest.toml declares, not just the machine that
built it. Blender picks the matching wheel at install time.
"""
import argparse
import hashlib
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
# blender_manifest.toml's platform ids mapped to the wheel platform tags pip
# accepts for each. Blender installs a bundled wheel by matching these tags,
# so every declared platform needs its own wheel for any dependency that
# isn't pure Python.
PLATFORM_TAGS = {
    "linux-x64": (
        "manylinux2014_x86_64",
        "manylinux_2_17_x86_64",
        "manylinux_2_28_x86_64",
        "linux_x86_64",
    ),
    "windows-x64": ("win_amd64",),
    "macos-x64": ("macosx_10_9_x86_64", "macosx_11_0_x86_64"),
    "macos-arm64": ("macosx_11_0_arm64",),
}
# The Python versions Blender bundles across the releases this addon supports
# (4.2 ships 3.11, 5.2 ships 3.13), mirroring pyproject.toml's bpy pins. A
# dependency with cp-tagged wheels resolves to a different file for each.
TARGET_PYTHON_VERSIONS = ("3.11", "3.13")


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


def _locked_packages(lock_path):
    with open(lock_path, "rb") as f:
        lock = tomllib.load(f)
    return lock.get("packages", [])


def _locked_wheel_hashes(lock_path):
    return {
        wheel["name"]: wheel.get("hashes", {}).get("sha256")
        for package in _locked_packages(lock_path)
        for wheel in package.get("wheels", [])
    }


def _manifest_platforms():
    with open(MANIFEST_PATH, "rb") as f:
        platforms = tomllib.load(f)["platforms"]
    unknown = [p for p in platforms if p not in PLATFORM_TAGS]
    if unknown:
        raise SystemExit(
            f"{MANIFEST_PATH} declares platform(s) {', '.join(sorted(unknown))} with no wheel tags "
            f"in PLATFORM_TAGS - add them there so their wheels get bundled"
        )
    return platforms


def _normalize(name):
    return re.sub(r"[-_.]+", "_", name).lower()


def _wheel_platform_tags(wheel_filename):
    # name-version(-build)?-python-abi-platform.whl, where each of the last
    # three is a dot-separated tag set ("py2.py3-none-any").
    return set(wheel_filename[: -len(".whl")].split("-")[-1].split("."))


def _download_wheels(lock_path, wheels_dir, platforms):
    # The lock is the full resolved closure, so each package is downloaded by
    # pinned version with --no-deps: no resolution happens per target, only
    # wheel selection. pip picks wheels for this machine unless told
    # otherwise, hence one pass per (platform, Python version).
    requirements = [f"{p['name']}=={p['version']}" for p in _locked_packages(lock_path)]
    for platform in platforms:
        for python_version in TARGET_PYTHON_VERSIONS:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "download",
                "--dest",
                str(wheels_dir),
                "--only-binary=:all:",
                "--no-deps",
                "--python-version",
                python_version,
            ]
            for tag in PLATFORM_TAGS[platform]:
                cmd += ["--platform", tag]
            subprocess.run(cmd + requirements, check=True, cwd=REPO_ROOT)


def _verify_wheel_hashes(wheels_dir, lock_path):
    # pip checks hashes itself when installing from a lock file; downloading
    # by pinned version doesn't, so check here. The lock only records the
    # environment it was generated in, so the other platforms' wheels have no
    # hash to check against.
    locked_hashes = _locked_wheel_hashes(lock_path)
    for wheel_path in sorted(wheels_dir.glob("*.whl")):
        expected = locked_hashes.get(wheel_path.name)
        if expected is None:
            continue
        digest = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
        if digest != expected:
            raise SystemExit(
                f"Hash mismatch for {wheel_path.name}: {lock_path.name} has {expected}, "
                f"downloaded file is {digest}"
            )


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


def _check_wheel_coverage(wheel_filenames, lock_path, platforms):
    # A package missing a wheel for one platform would produce a zip that
    # installs fine on the machine that built it and fails on import
    # everywhere else - which is how bc7enc-py went missing entirely.
    missing = []
    for package in _locked_packages(lock_path):
        name = _normalize(package["name"])
        candidates = [w for w in wheel_filenames if _normalize(w.split("-")[0]) == name]
        for platform in platforms:
            accepted = {"any", *PLATFORM_TAGS[platform]}
            if not any(_wheel_platform_tags(w) & accepted for w in candidates):
                missing.append(f"{package['name']} ({platform})")
    if missing:
        raise SystemExit(
            "No wheel for: " + ", ".join(missing) + "\n"
            "Every dependency needs a wheel for every platform blender_manifest.toml declares. "
            "If one genuinely has none, drop that platform from the manifest or the dependency "
            "from pyproject.toml."
        )


def generate_lock():
    pyproject = _load_pyproject()
    requirement_strings = _filter_out_bpy(_requirement_strings(pyproject, extras=[]))
    print(f"Locking {len(requirement_strings)} top-level requirement(s) into {LOCK_PATH} ...")
    for r in requirement_strings:
        print(f"  - {r}")
    _generate_lock_file(requirement_strings, LOCK_PATH)
    # Downloaded and thrown away here purely to fail now, rather than at the
    # next build, if the new resolution has nothing to offer some platform.
    platforms = _manifest_platforms()
    with tempfile.TemporaryDirectory(prefix="albam-lock-check-") as tmp:
        tmp = Path(tmp)
        print(f"Checking every locked package has a wheel for {', '.join(platforms)} ...")
        _download_wheels(LOCK_PATH, tmp, platforms)
        _check_wheel_coverage([w.name for w in tmp.glob("*.whl")], LOCK_PATH, platforms)
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

        platforms = _manifest_platforms()
        print(f"Downloading wheels from {lock_path} for {', '.join(platforms)} ...")
        wheels_dir.mkdir(exist_ok=True)
        _download_wheels(lock_path, wheels_dir, platforms)

        wheel_filenames = [p.name for p in wheels_dir.glob("*.whl")]
        if not wheel_filenames:
            raise SystemExit(f"pip download produced no wheels from {lock_path} - aborting")
        _verify_wheel_hashes(wheels_dir, lock_path)
        _check_wheel_coverage(wheel_filenames, lock_path, platforms)
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
