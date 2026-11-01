"""The error popup's "copy report" button (see #371).

Synthetic: no game data needed. The popup itself (ALBAM_OT_ErrorHandler) is
a Blender modal dialog and awkward to drive directly in a test, so this
exercises the two pure pieces that actually matter: format_error_report(),
which assembles the text the button copies, and the copy operator's
execute(), which is plain enough to call directly through bpy.ops.
"""
import sys
from pathlib import Path

import bpy

from albam.blender_ui.error_handling import format_error_report


def _report_for(exc):
    try:
        raise exc
    except type(exc):
        return format_error_report(*sys.exc_info())


def test_format_error_report_includes_message_and_traceback():
    report = _report_for(ValueError("something broke"))

    assert "ValueError: something broke" in report
    assert "_report_for" in report
    assert "raise exc" in report


def test_format_error_report_redacts_home_directory():
    # The traceback includes this file's own absolute path, under the
    # user's home directory - that's the one piece of the report that
    # could leak something personal onto a public #support thread.
    report = _report_for(ValueError("boom"))

    assert str(Path.home()) not in report
    assert "******" in report


def test_copy_error_report_operator_copies_text_and_reports_info():
    # execute() is the whole of this operator's behavior - it is only ever
    # reached through the "Copy report to clipboard" button, which sets
    # report_text from the popup's own error_report_text before calling it.
    result = bpy.ops.albam.copy_error_report(report_text="Albam error report\nsome traceback")

    assert result == {"FINISHED"}
