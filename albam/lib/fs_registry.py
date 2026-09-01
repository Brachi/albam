"""
Session-lifetime registry of live PyFilesystem2 `FS` instances.

`bpy.types.PropertyGroup` can only hold `bpy.props.*` fields - it can't hold a
live Python object such as an `MTFW_FS`/`ArcFS`/`MemoryFS` instance. This is
the plain-Python side-table that VFS roots point at (via a string key stored
on the root `VirtualFile`) instead of smuggling state into Blender types.
"""

import uuid

_REGISTRY = {}


def register(fs_instance):
    """Store `fs_instance` under a fresh key and return that key."""
    key = uuid.uuid4().hex
    _REGISTRY[key] = fs_instance
    return key


def reconnect(key, fs_instance):
    """Store `fs_instance` under an existing `key` (one a `VirtualFile.fs_key`
    already carries, restored from a .blend file), instead of minting a new
    one. Used to rebuild this process-lifetime registry after it comes up
    empty in a fresh Blender session - see albam/vfs.py's load_post handler.
    """
    _REGISTRY[key] = fs_instance


def get(key):
    return _REGISTRY[key]


def unregister(key):
    """Remove and close the FS instance stored under `key`, if any."""
    fs_instance = _REGISTRY.pop(key, None)
    if fs_instance is not None:
        fs_instance.close()


def clear():
    """Close and remove every registered FS instance."""
    for key in list(_REGISTRY):
        unregister(key)
