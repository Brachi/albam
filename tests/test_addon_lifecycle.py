"""
register()/unregister() are the addon's Blender-facing enable/disable entry
points, and Blender (or the user) can cycle them more than once per session -
e.g. disabling and re-enabling the addon, or Blender doing so itself on an
update. These tests drive that from a subprocess rather than in-process:
conftest.py's pytest_sessionstart already calls register() once for the
whole pytest session, so a second register()/unregister() cycle run here
directly would corrupt that shared session instead of just failing cleanly.
"""
import subprocess
import sys


# bpy segfaults during interpreter finalization once register() has run
# (reproducible under 4.2 with a single register() and no unregister() at
# all), so the subprocess ends with os._exit() to skip finalization
# altogether - otherwise its exit status says nothing about the cycles.
# .github/workflows/tests.yml works around the same thing for pytest itself.
REGISTER_TWICE = """
import os
import sys

import bpy
from albam import register, unregister

register()
unregister()
register()
unregister()
print("cycles ok")
sys.stdout.flush()
os._exit(0)
"""


def test_register_unregister_survives_a_second_cycle():
    """
    AlbamCustomPropertiesFactory() (albam/blender_ui/custom_properties.py)
    rebuilds its dynamic PropertyGroup/Panel classes from scratch on every
    register() call, unlike the classes collected via the
    @blender_registry.register_blender_prop/register_blender_type decorators,
    which only run once per process (at module import time). A second
    register() therefore used to leave stale, already-unregistered class
    objects with reused bl_idnames sitting in blender_registry.types, and the
    following unregister() crashed on the first one it hit with:

        RuntimeError: unregister_class(...):, missing bl_rna attribute from
        '_RNAMeta' instance (may not be registered)
    """
    result = subprocess.run(
        [sys.executable, "-c", REGISTER_TWICE],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "cycles ok" in result.stdout, result.stdout + result.stderr
