"""Turns a missing bundled dependency into an actionable message (#370).

Blender's extension packaging bundles albam's third-party dependencies as
wheels inside the release zip (see scripts/build_extension.py). A user who
instead uses GitHub's "Code -> Download ZIP" button gets the source only,
with none of those wheels, and the first `import fs` or `import bc7enc`
albam does raises a bare ModuleNotFoundError with no indication of why - at
least 3 separate #support reports, one costing a user "hours" before they
worked it out.

Imported first thing in albam/__init__.py, before anything that might
actually be missing, so this module itself has to stay free of third-party
imports.
"""

# pyproject.toml's [project.dependencies], minus bpy (Blender provides its
# own) and setuptools (already present in Blender's bundled Python). Each
# entry is the name Python imports, not necessarily the PyPI distribution
# name - bc7enc-py imports as "bc7enc". Deliberately excludes the `reen`/`s3`
# extras: those aren't bundled in a normal release build either (opt-in,
# gated behind ALBAM_ENABLE_REEN / the s3 cache), so a user missing one of
# them hasn't made the source-zip mistake this module is about.
BUNDLED_DEPENDENCIES = frozenset({"fs", "kaitaistruct", "pymorton", "bc7enc"})

RELEASES_URL = "https://github.com/Brachi/albam/releases"


def reraise_as_source_zip_hint(ex):
    """Re-raise a ModuleNotFoundError with a clear cause, or pass it through.

    `ex.name` is the top-level package the failed import was trying to
    reach - e.g. "fs" even for `from fs.path import dirname` - so comparing
    just the first dotted component against BUNDLED_DEPENDENCIES still
    matches. Anything else is a real bug in albam's own code, not a
    packaging problem, and is re-raised unchanged so it isn't masked.

    Call from inside an `except ModuleNotFoundError:` block.
    """
    root_name = (ex.name or "").split(".")[0]
    if root_name not in BUNDLED_DEPENDENCIES:
        raise ex

    message = (
        f"Albam failed to load: the Python package '{root_name}' is missing.\n"
        "\n"
        "This happens when Albam is installed from GitHub's 'Code' -> 'Download ZIP' "
        "button, which only has the source code, not Albam's bundled dependencies.\n"
        "\n"
        f"Download the add-on from the Releases page instead:\n{RELEASES_URL}\n"
        "and install that zip (Preferences > Get Extensions, or Add-ons > install "
        "from disk) rather than the GitHub source archive."
    )
    # Blender's own addon-enable failure handling only guarantees the
    # traceback reaches the console, not that the exception's message is
    # shown anywhere else a user might see it - so print it too, loudly.
    banner = "=" * 70
    print(f"\n{banner}\n{message}\n{banner}\n")
    raise ImportError(message) from ex
