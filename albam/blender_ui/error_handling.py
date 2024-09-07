from platform import platform
import traceback
from pathlib import Path
import sys

import bpy

from albam.exceptions import AlbamCheckFailure
from albam.registry import blender_registry
from albam.__version__ import __version__ as albam_version

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


@blender_registry.register_blender_type
class ALBAM_OT_ErrorHandler(bpy.types.Operator):
    bl_label = "Something went wrong"
    bl_idname = "albam.error_handler_popup"
    ISSUES_URL = "https://github.com/Brachi/albam/issues"
    DISCORD_INVITE_URL = "https://discord.gg/QC2FhGhxCh"
    ERROR_UNEXPECTED_HEADER = "An unexpected error happened"
    ERROR_UNEXPECTED_SOLUTION_MSG = "Please provide the error shown in the console for help"
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
        else:
            self.error_header = self.ERROR_UNEXPECTED_HEADER
            self.error_message = ""
            self.error_details = ""
            self.error_solution = self.ERROR_UNEXPECTED_SOLUTION_MSG
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
        type_err, err, tb = sys.exc_info()
        stack_summary = traceback.extract_tb(tb)
        traceback_str = "".join(stack_summary.format())
        traceback_str_home_redacted = traceback_str.replace(str(Path.home()), "******")
        error = ERROR_TEMPLATE.format(
            blender_version=".".join(map(str, bpy.app.version)),
            albam_version=albam_version,
            operating_system=platform(),
            error=f"{type_err.__name__}: {str(err)}",
            traceback_str=traceback_str_home_redacted,
        )

        return error

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
