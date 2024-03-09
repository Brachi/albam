from platform import platform
import traceback
import sys

import bpy

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
    bl_label = ""
    bl_idname = "albam.error_handler_popup"
    ISSUES_URL = "https://github.com/Brachi/albam/issues"
    DISCORD_INVITE_URL = "https://discord.gg/QC2FhGhxCh"

    def invoke(self, context, event):
        error = self._generate_error_report()
        print(error)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Something went wrong", icon="ERROR")
        layout.label(text="An unexpected error happened.")
        layout.label(text="Please Provide the error shown in the console for help")

        issues_op = layout.operator("wm.url_open", text="Report an issue on Github", icon="URL")
        issues_op.url = self.ISSUES_URL
        discord_op = layout.operator("wm.url_open", text="Ask on Discord #support", icon="URL")
        discord_op.url = self.DISCORD_INVITE_URL
        layout.row()

    @staticmethod
    def _generate_error_report():
        type_err, err, tb = sys.exc_info()
        stack_summary = traceback.extract_tb(tb)
        traceback_str = "".join(stack_summary.format())
        error = ERROR_TEMPLATE.format(
            blender_version=".".join(map(str, bpy.app.version)),
            albam_version=albam_version,
            operating_system=platform(),
            error=f"{type_err.__name__}: {str(err)}",
            traceback_str=traceback_str,
        )

        return error
