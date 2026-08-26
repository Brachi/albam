"""
Tests for albam/__init__.py's register()/unregister() - the addon's Blender-
facing enable/disable entry points. Real Blender calls these whenever the
user (or Blender itself, e.g. on an addon update) disables and re-enables
the addon within a single session, so unregister() must undo everything
register() did to shared, session-lived state - not just the bpy classes -
or repeated enable/disable cycles leak state that keeps growing.

These tests drive register()/unregister() from a subprocess rather than the
live pytest process. This session's own register() already ran once (see
tests/conftest.py's pytest_sessionstart), and a second in-process
register()/unregister()/register() cycle collides with a separate,
pre-existing bug: AlbamCustomPropertiesFactory (albam/blender_ui/
custom_properties.py) appends freshly-generated dynamic Panel classes to
blender_registry.types on every register() call without ever clearing the
previous cycle's entries, so a later unregister() call trips over stale,
already-invalidated bl_rna and raises RuntimeError - unrelated to the
load_post handler bug these tests target, but real, and out of scope here.
Running each scenario in its own fresh subprocess (a single unregister()
call per process, so that latent bug never gets a chance to fire) sidesteps
it entirely while still exercising the real register()/unregister()
functions end to end, and can't corrupt this session's shared bpy state.
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
