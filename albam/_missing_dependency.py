"""Explains a missing third-party dependency when albam fails to load (#370).

Blender's extension packaging bundles albam's third-party dependencies as
wheels inside the release zip, and scripts/build_extension.py lists them in
the zip's blender_manifest.toml. The manifest in the source tree has
`wheels = []`, so an install from GitHub's "Code > Download ZIP" archive
can be told apart from a release build whose wheels Blender failed to
install.

Imported first thing in albam/__init__.py, before anything that might be
missing, so this module only uses the standard library.
"""
from pathlib import Path
import tomllib

MANIFEST_PATH = Path(__file__).with_name("blender_manifest.toml")
RELEASES_URL = "https://github.com/Brachi/albam/releases"


def missing_dependency_hint(ex, manifest_path=MANIFEST_PATH):
    """Return an ImportError explaining `ex`, or None to keep `ex` as is.

    `ex` is a caught ModuleNotFoundError. A module under albam's own package
    is never a packaging problem (it ships in every zip), so that case and
    an unreadable manifest return None and the caller re-raises the
    original error.
    """
    if not ex.name or ex.name == __package__ or ex.name.startswith(f"{__package__}."):
        return None
    try:
        with open(manifest_path, "rb") as f:
            manifest = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None

    root_name = ex.name.split(".")[0]
    if manifest.get("wheels"):
        platforms = ", ".join(manifest.get("platforms", [])) or "unknown"
        message = (
            f"Albam failed to load: the Python package '{root_name}' is missing.\n"
            "\n"
            "This Albam zip bundles its dependencies as wheels, but Blender did not "
            "install them. Check that:\n"
            f"- your platform is supported by this build ({platforms})\n"
            "- the zip was installed through Blender's extension installer "
            "(Preferences > Get Extensions > Install from Disk), not extracted or "
            "copied into the add-ons folder\n"
            "- your Blender version is supported by this Albam release\n"
            "\n"
            f"Releases: {RELEASES_URL}"
        )
    else:
        message = (
            f"Albam failed to load: the Python package '{root_name}' is missing.\n"
            "\n"
            "This copy of Albam is the source code, without the bundled dependencies. "
            "That happens when it is installed from GitHub's 'Code' > 'Download ZIP' "
            "button.\n"
            "\n"
            f"Download the add-on zip from the Releases page instead:\n{RELEASES_URL}\n"
            "and install it from Preferences > Get Extensions > Install from Disk.\n"
            "\n"
            "Running from a development checkout? See README.md for installing the "
            "dependencies."
        )
    return ImportError(message, name=ex.name)
