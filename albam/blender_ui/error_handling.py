import os
from platform import platform
import traceback
from pathlib import Path
import sys

import bpy

from ..exceptions import AlbamCheckFailure
from ..registry import blender_registry
from ..__version__ import __version__ as albam_version

RERAISE_ERRORS_ENV_VAR = "ALBAM_RERAISE_ERRORS"

ERROR_TEMPLATE = """
==================
Albam error report
==================

Blender version: {blender_version}
Albam version: {albam_version}
Operating System: {operating_system}
Error: {error}
Traceback:
{traceback_str}
=================
"""


HOME_REDACTED = "******"


def _redact_home(text):
    home = Path.home()
    for home_str in {str(home), home.as_posix()}:
        text = text.replace(home_str, HOME_REDACTED)
    return text


def format_error_report(type_err, err, tb):
    """The full report - versions, OS, error, traceback - as a string, with
    the user's home directory redacted everywhere in it.

    The redaction covers the whole report, not just the traceback: the error
    message itself often carries a path (e.g. a FileNotFoundError), and the
    report is meant to be pasted into public #support and GitHub threads.

    For an AlbamCheckFailure the error line is followed by its details and
    solution, which name the offending objects or materials.

    Module level, and taking the exception explicitly, so callers outside a
    popup can use it: the operator error handlers print it from their own
    `except` blocks, which is the only way it reaches a console when Blender
    runs in background mode (`INVOKE_DEFAULT` falls back to `execute()`
    there, so the popup's `invoke()` never runs).
    """
    stack_summary = traceback.extract_tb(tb)
    traceback_str = "".join(stack_summary.format())
    error = f"{type_err.__name__}: {str(err)}"
    if isinstance(err, AlbamCheckFailure):
        error += f"\nDetails: {err.details}\nSolution: {err.solution}"
    report = ERROR_TEMPLATE.format(
        blender_version=".".join(map(str, bpy.app.version)),
        albam_version=albam_version,
        operating_system=platform(),
        error=error,
        traceback_str=traceback_str,
    )
    return _redact_home(report)


def handle_operator_exception(operator, message):
    """Shared tail for every operator `except` block: print the report, then
    surface it to the user.

    Call from inside the `except`, which is where sys.exc_info() is live.
    This is the only place the report is printed, so the traceback reaches
    the console in headless Blender and CI too, where the popup never opens.

    With ALBAM_RERAISE_ERRORS set the exception is re-raised instead of being
    turned into an operator report. Blender converts an {'ERROR'} report into
    a bare RuntimeError carrying only `message`, which loses the traceback
    and the exception type - fine for a user staring at a dialog, useless for
    a test asserting on a failure. The test suite sets it (tests/conftest.py).
    """
    type_err, err, tb = sys.exc_info()
    print(format_error_report(type_err, err, tb))
    if os.environ.get(RERAISE_ERRORS_ENV_VAR):
        raise err
    operator.report({"ERROR"}, f"{message}: {type_err.__name__}: {err}")
    bpy.ops.albam.error_handler_popup("INVOKE_DEFAULT")


@blender_registry.register_blender_type
class ALBAM_OT_ErrorHandler(bpy.types.Operator):
    bl_label = "Something went wrong"
    bl_idname = "albam.error_handler_popup"
    ISSUES_URL = "https://github.com/Brachi/albam/issues"
    DISCORD_INVITE_URL = "https://discord.gg/QC2FhGhxCh"
    ERROR_UNEXPECTED_HEADER = "An unexpected error happened"
    ERROR_UNEXPECTED_SOLUTION_MSG = "Copy the report below and include it when asking for help"
    ERROR_CHECK_FAILURE_HEADER = "A check failed"
    MIN_POPUP_WIDTH = 300
    PIXELS_PER_CHAR = 7  # should be dynamic based on resolution/dpi

    error_header = bpy.props.StringProperty(default="")
    error_message = bpy.props.StringProperty(default="")
    error_details = bpy.props.StringProperty(default="")
    error_solution = bpy.props.StringProperty(default="")
    # The plain-assignment properties above are not registered as RNA
    # properties (Blender only registers annotations); they work as ordinary
    # Python attributes because invoke() and draw() run on the same instance.
    # This one is an annotation like ALBAM_OT_CopyErrorReport.report_text,
    # with StringProperty's default maxlen=0, which means unbounded, so a
    # long traceback is not truncated.
    error_report_text: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        type_err, err, tb = sys.exc_info()
        # Computed for every error, not just unexpected ones: this is what
        # the "copy report" button puts on the clipboard, and a check
        # failure's traceback is just as useful to a #support helper as an
        # unexpected error's. Printing is left to handle_operator_exception().
        self.error_report_text = self._generate_error_report(type_err, err, tb)
        if issubclass(type(err), AlbamCheckFailure):
            self.error_header = self.ERROR_CHECK_FAILURE_HEADER
            self.error_message = err.message
            self.error_details = err.details
            self.error_solution = err.solution
        else:
            self.error_header = self.ERROR_UNEXPECTED_HEADER
            self.error_message = ""
            self.error_details = ""
            self.error_solution = self.ERROR_UNEXPECTED_SOLUTION_MSG
        return context.window_manager.invoke_props_dialog(self, width=self._calculate_popup_width())

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.error_header, icon="ERROR")
        layout.separator()
        layout.label(text=self.error_message)
        layout.label(text=self.error_details)
        layout.label(text=self.error_solution)

        layout.separator()
        layout.separator()

        copy_op = layout.operator(
            ALBAM_OT_CopyErrorReport.bl_idname, text="Copy report to clipboard", icon="COPYDOWN"
        )
        copy_op.report_text = self.error_report_text
        issues_op = layout.operator("wm.url_open", text="Report an issue on Github", icon="URL")
        issues_op.url = self.ISSUES_URL
        discord_op = layout.operator("wm.url_open", text="Ask on Discord #support", icon="URL")
        discord_op.url = self.DISCORD_INVITE_URL
        layout.separator()
        layout.separator()

    @staticmethod
    def _generate_error_report(type_err, err, tb):
        return format_error_report(type_err, err, tb)

    def _calculate_popup_width(self):
        using_space = (
            self.error_header,
            self.error_message,
            self.error_details,
            self.error_solution,
        )
        needed = max(len(label) for label in using_space)
        width = max(needed * self.PIXELS_PER_CHAR, self.MIN_POPUP_WIDTH)
        return width


@blender_registry.register_blender_type
class ALBAM_OT_CopyErrorReport(bpy.types.Operator):
    """Copy the full error report (message and traceback) to the clipboard.

    Exists so a #support user can paste the actual error directly, instead
    of being asked to open the system console (which most users don't know
    exists) and copy it from there by hand.
    """

    bl_label = "Copy report to clipboard"
    bl_idname = "albam.copy_error_report"
    bl_description = "Copy the full error report, including the traceback, to the clipboard"
    # Only reachable through the popup's button, which sets report_text.
    # Hidden from F3 search, where running it would copy an empty string.
    bl_options = {"INTERNAL"}

    # Annotation syntax, so it is a registered RNA property: it is set on
    # the button's operator instance (layout.operator() in the popup's
    # draw()) and read back on the instance Blender creates when the button
    # is clicked, and only RNA properties survive that trip.
    report_text: bpy.props.StringProperty(default="")

    def execute(self, context):
        context.window_manager.clipboard = self.report_text
        self.report({"INFO"}, "Error report copied to clipboard")
        return {"FINISHED"}
