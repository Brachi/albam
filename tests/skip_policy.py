"""What a skip means in this suite: an input the test needs isn't here.

That input is game data (no --game-dir for the app, R2 not configured, a
file the install doesn't have), a package (pytest.importorskip) or an
external tool (a skipif on its absence). With those as the only causes, a
skip in CI always means data is missing, and locally it says which games
aren't pointed at. tests/conftest.py fails any other skip.

A test that doesn't apply is never a skip:
- to a dataset entry: it gets no case for it (@applies_to, see
  tests/dataset_cases.py);
- to the running Blender: @requires_blender deselects it at collection, so
  it counts as deselected, not skipped. test_skip_policy.py checks every
  such test still runs on a Blender version CI tests.
"""
import pytest

# The empty parameter set pytest marks a test with when @applies_to leaves
# it no dataset entry at all: no data to run it on.
EMPTY_PARAMETER_SET_PREFIX = "got empty parameter set"
IMPORTORSKIP_PREFIX = "could not import"


class MissingInput(pytest.skip.Exception):
    """Raised by skip_missing(); the one runtime skip the policy allows."""


def skip_missing(reason):
    """Skip because an input the test needs isn't here (see the module doc)."""
    raise MissingInput(reason)


def requires_blender(*version):
    """Run only on Blender `version` (major, minor) or later; deselected on
    earlier ones."""
    return pytest.mark.requires_blender(*version)


def is_missing_input(item, skipped):
    """Whether `skipped`, the Skipped exception that ended `item`, is a skip
    the policy allows."""
    if isinstance(skipped, MissingInput):
        return True
    reason = str(skipped.msg or "")
    if reason.startswith((IMPORTORSKIP_PREFIX, EMPTY_PARAMETER_SET_PREFIX)):
        return True
    # A skipif declares the input it's missing (a tool, credentials).
    return any(marker.kwargs.get("reason") == reason for marker in item.iter_markers("skipif"))
