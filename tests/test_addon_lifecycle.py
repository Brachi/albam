"""
Tests for albam/__init__.py's register()/unregister() - the addon's Blender-
facing enable/disable entry points. Real Blender calls these whenever the
user (or Blender itself, e.g. on an addon update) disables and re-enables
the addon within a single session, so unregister() must undo everything
register() did - both the bpy classes it registered and the shared,
session-lived state it touched - or repeated enable/disable cycles crash
outright or leak state that keeps growing.

These tests drive register()/unregister() from a subprocess rather than the
live pytest process: this session already called register() once of its own
(see tests/conftest.py's pytest_sessionstart), so cycling it again in-process
would corrupt that shared session instead of just failing cleanly. Each
scenario gets its own fresh subprocess.
"""
import ast
import subprocess
import sys
import textwrap


# bpy segfaults during interpreter finalization once register() has run
# (reproducible under 4.2 with a single register() and no unregister() at
# all), so each script ends with os._exit() to skip finalization altogether -
# otherwise the subprocess exit status says nothing about what it tested.
# .github/workflows/tests.yml works around the same segfault for pytest itself.
EXIT_WITHOUT_FINALIZING = """
sys.stdout.flush()
os._exit(0)
"""


def _run(script):
    # bpy itself writes startup noise (e.g. a color management config line)
    # to stdout ahead of anything the script prints, so only the last line
    # is the script's own output.
    script = "import os\nimport sys\n" + textwrap.dedent(script) + EXIT_WITHOUT_FINALIZING
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"subprocess failed (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    return result.stdout.strip().splitlines()[-1]


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
    output = _run(
        """
        import bpy
        from albam import register, unregister

        register()
        unregister()
        register()
        unregister()
        print("cycles ok")
        """
    )
    assert output == "cycles ok"


def test_unregister_removes_load_post_handlers_it_added():
    # register() appends its own handler functions to
    # bpy.app.handlers.load_post - a plain list Blender calls in full on
    # every .blend load. unregister() must remove exactly what register()
    # added, so a register()/unregister()/register() cycle (an addon
    # disable followed by a re-enable) doesn't leave duplicates behind
    # that fire twice on every future load.
    output = _run(
        """
        import bpy
        from albam import LOAD_POST_HANDLERS, register, unregister

        def counts():
            return [bpy.app.handlers.load_post.count(h) for h in LOAD_POST_HANDLERS]

        register()  # simulates the addon already being enabled
        before = counts()

        unregister()  # disable
        after_unregister = counts()

        register()  # re-enable
        after_reregister = counts()

        print((len(LOAD_POST_HANDLERS), before, after_unregister, after_reregister))
        """
    )
    num_handlers, before, after_unregister, after_reregister = ast.literal_eval(output)
    assert num_handlers, "register() no longer tracks any load_post handler"
    assert before == [1] * num_handlers
    assert after_unregister == [0] * num_handlers, "unregister() left a load_post handler registered"
    assert after_reregister == [1] * num_handlers, "re-registering produced duplicate handlers"


def test_unregister_tolerates_an_already_removed_load_post_handler():
    # A handler register() added could already be gone from load_post by
    # the time unregister() runs (e.g. some other teardown path removed it
    # first) - unregister() must not raise ValueError out of list.remove()
    # in that case.
    output = _run(
        """
        import bpy
        from albam import LOAD_POST_HANDLERS, register, unregister

        register()
        bpy.app.handlers.load_post.remove(LOAD_POST_HANDLERS[0])

        unregister()  # must not raise
        print("ok")
        """
    )
    assert output == "ok"
