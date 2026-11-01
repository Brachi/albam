"""Tests for albam/_missing_dependency.py (#370).

A user who installs Albam from GitHub's "Code -> Download ZIP" button gets
none of the bundled wheels (fs, bc7enc, kaitaistruct, pymorton), and used to
see a bare ModuleNotFoundError with no indication of why. These tests cover
the helper that turns that into an actionable message, both in isolation
(no bpy needed - pure logic) and wired into `import albam` itself.
"""
import ast
import subprocess
import sys
import textwrap

import pytest

from albam._missing_dependency import BUNDLED_DEPENDENCIES, reraise_as_source_zip_hint


@pytest.mark.parametrize("name", sorted(BUNDLED_DEPENDENCIES))
def test_reraise_as_source_zip_hint_rewrites_known_dependencies(name):
    original = ModuleNotFoundError(f"No module named {name!r}")
    original.name = name

    with pytest.raises(ImportError) as exc_info:
        reraise_as_source_zip_hint(original)

    message = str(exc_info.value)
    assert name in message
    assert "Download ZIP" in message
    assert "releases" in message
    assert exc_info.value.__cause__ is original


def test_reraise_as_source_zip_hint_matches_on_the_top_level_package():
    # `from fs.path import dirname` reports ex.name as "fs", not "fs.path" -
    # confirmed separately - but a dotted name should still match if it ever
    # shows up, since only the top-level package is ever actually bundled.
    original = ModuleNotFoundError("No module named 'fs.path'")
    original.name = "fs.path"

    with pytest.raises(ImportError):
        reraise_as_source_zip_hint(original)


def test_reraise_as_source_zip_hint_passes_through_unrelated_errors():
    # A missing module that isn't one of albam's bundled dependencies is a
    # real bug (e.g. a typo'd internal import), not a packaging problem -
    # it must come back unchanged, not get relabeled as a source-zip issue.
    original = ModuleNotFoundError("No module named 'not_a_real_dependency'")
    original.name = "not_a_real_dependency"

    with pytest.raises(ModuleNotFoundError) as exc_info:
        reraise_as_source_zip_hint(original)

    assert exc_info.value is original


def _run(script):
    # Fresh subprocess, not the live pytest process: this session's `import
    # albam` already succeeded (tests/conftest.py's pytest_sessionstart
    # calls register()), and sys.modules poisoning to simulate a missing
    # dependency would corrupt that shared state for every other test.
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
    )
    return result


def test_import_albam_surfaces_a_clear_message_when_a_bundled_dependency_is_missing():
    # sys.modules[name] = None makes the import system report that module as
    # not found without actually uninstalling it - the simplest way to
    # reproduce a source-zip install's missing `fs` from a normal dev venv
    # that has it. A marker line separates the result from bpy's own
    # startup noise on stdout (e.g. a color management config line).
    script = """
        import sys
        sys.modules["fs"] = None
        try:
            import albam
        except ImportError as ex:
            print("RESULT", type(ex).__name__, repr(str(ex)))
        else:
            print("RESULT", "NO ERROR RAISED")
    """
    result = _run(script)
    assert result.returncode == 0, result.stderr
    (result_line,) = [line for line in result.stdout.splitlines() if line.startswith("RESULT ")]
    _, exc_type, message_repr = result_line.split(" ", 2)
    assert exc_type == "ImportError"
    message = ast.literal_eval(message_repr)
    assert "Download ZIP" in message
    assert "releases" in message
    assert "ModuleNotFoundError" not in message  # the rewritten message, not the raw one
