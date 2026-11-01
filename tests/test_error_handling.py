"""The error popup's "copy report" button (see #371).

Synthetic: no game data needed. The popup itself (ALBAM_OT_ErrorHandler) is
a Blender modal dialog and awkward to drive directly in a test, so this
exercises the two pure pieces that actually matter: format_error_report(),
which assembles the text the button copies, and the copy operator's
execute(), called directly with a stub context.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

from albam.blender_ui.error_handling import ALBAM_OT_CopyErrorReport, format_error_report
from albam.exceptions import AlbamCheckFailure


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


def test_format_error_report_redacts_home_directory(monkeypatch):
    # Both the traceback (this file's own path) and the error message can
    # carry a home path, and the report is pasted onto public threads.
    fake_home = Path(__file__).resolve().parent
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    report = _report_for(FileNotFoundError(f"No such file: '{fake_home / 'secret.arc'}'"))

    assert str(fake_home) not in report
    assert "No such file: '******" in report
    assert "******" in report.split("Traceback:")[1]


def test_format_error_report_includes_check_failure_details_and_solution():
    report = _report_for(AlbamCheckFailure("Too many bones", "Mesh: body_01", "Split the mesh"))

    assert "AlbamCheckFailure: Too many bones" in report
    assert "Details: Mesh: body_01" in report
    assert "Solution: Split the mesh" in report


def test_copy_error_report_operator_copies_text_and_reports_info():
    # execute() is the whole of this operator's behavior. It is called
    # unbound with a stub self and context, so the copied text and the
    # report can be read back without a window manager clipboard.
    reports = []
    stub_self = SimpleNamespace(
        report_text="Albam error report\nsome traceback",
        report=lambda kind, msg: reports.append((kind, msg)),
    )
    context = SimpleNamespace(window_manager=SimpleNamespace(clipboard=""))

    result = ALBAM_OT_CopyErrorReport.execute(stub_self, context)

    assert result == {"FINISHED"}
    assert context.window_manager.clipboard == "Albam error report\nsome traceback"
    assert reports == [({"INFO"}, "Error report copied to clipboard")]
