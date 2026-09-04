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


def format_error_report(type_err, err, tb):
    """The full report - versions, OS, redacted traceback - as a string.

    Module level, and taking the exception explicitly, so callers outside a
    popup can use it: the operator error handlers print it from their own
    `except` blocks, which is the only way it reaches a console when Blender
    runs in background mode (`INVOKE_DEFAULT` falls back to `execute()`
    there, so the popup's `invoke()` never runs and its print never happens).
    """
    stack_summary = traceback.extract_tb(tb)
    traceback_str = "".join(stack_summary.format())
    traceback_str_home_redacted = traceback_str.replace(str(Path.home()), "******")
    return ERROR_TEMPLATE.format(
        blender_version=".".join(map(str, bpy.app.version)),
        albam_version=albam_version,
        operating_system=platform(),
        error=f"{type_err.__name__}: {str(err)}",
        traceback_str=traceback_str_home_redacted,
    )


def handle_operator_exception(operator, message):
    """Shared tail for every operator `except` block: print the report, then
    surface it to the user.

    Call from inside the `except`, which is where sys.exc_info() is live.
    Printing here rather than from the popup means the traceback survives
    headless Blender and CI, where the popup never opens - the popup itself
    tells users to "provide the error shown in the console", which until now
    was empty for exactly those users.

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
    ERROR_UNEXPECTED_SOLUTION_MSG = "Please provide the error shown in the console for help"
    ERROR_UNEXPECTED_SOLUTION_MSG_2 = "Go to Window -> Toggle System Console"
    ERROR_CHECK_FAILURE_HEADER = "A check failed"
    MIN_POPUP_WIDTH = 300
    PIXELS_PER_CHAR = 7  # should be dynamic based on resolution/dpi

    error_header = bpy.props.StringProperty(default="")
    error_message = bpy.props.StringProperty(default="")
    error_details = bpy.props.StringProperty(default="")
    error_solution = bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        type_err, err, tb = sys.exc_info()
        if issubclass(type(err), AlbamCheckFailure):
            self.error_header = self.ERROR_CHECK_FAILURE_HEADER
            self.error_message = err.message
            self.error_details = err.details
            self.error_solution = err.solution
            self.error_solution_2 = ""
        else:
            self.error_header = self.ERROR_UNEXPECTED_HEADER
            self.error_message = ""
            self.error_details = ""
            self.error_solution = self.ERROR_UNEXPECTED_SOLUTION_MSG
            self.error_solution_2 = self.ERROR_UNEXPECTED_SOLUTION_MSG_2
            error = self._generate_error_report(type_err, err, tb)
            print(error)
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
        if self.error_solution_2:
            layout.label(text=self.error_solution_2)

        layout.separator()
        layout.separator()

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
