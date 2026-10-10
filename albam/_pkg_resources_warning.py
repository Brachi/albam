"""Silences the deprecation warning pyfilesystem2 triggers on import.

Imported for its side effect, first thing in albam/__init__.py, so the
filter is in place before anything reaches `fs`. Any albam import runs that
first, so this covers Blender's console, the test suite and every script.

fs 2.4.16 is the latest release and still declares two pkg_resources
namespace packages plus one entry-point lookup. Recent setuptools warns on
each, so three lines of someone else's deprecation notice preceded every
command's own output. The pin in pyproject.toml keeps `fs` working, but
does not go back far enough to predate the warning.

Filtering rather than patching the dependency: the warning is about a
dependency's dependency, says nothing about albam, and the fix has to
survive a reinstall of `fs`. Scoped to that one message from `fs` itself,
so an equivalent warning from anywhere else in a Blender session still
shows.
"""
import warnings

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API",
    category=UserWarning,
    module=r"fs(\.|$)",
)
