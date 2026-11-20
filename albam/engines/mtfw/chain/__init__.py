"""RE5 chain collision and simulation support."""

import bpy

# Importing these modules runs their registry decorators. Import the file
# handlers first to preserve the property registration order they depend on.
from .chain_import import load_ccl, load_chn  # noqa: F401
from .chain_export import export_ccl, export_chn  # noqa: F401
from . import ui as _ui  # noqa: F401


def register_handlers():
    handler = _ui.preview_highlight_handler
    handlers = bpy.app.handlers.depsgraph_update_post
    if handler not in handlers:
        handlers.append(handler)
    load_handler = _ui.chain_file_load_post
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)
    _ui.chain_file_load_post(None)


def unregister_handlers():
    _ui.reset_preview_highlight_state()
    handlers = bpy.app.handlers.depsgraph_update_post
    handler = _ui.preview_highlight_handler
    if handler in handlers:
        handlers.remove(handler)
    load_handler = _ui.chain_file_load_post
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
