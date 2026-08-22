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
import subprocess
import sys
import textwrap


def _run(script):
    # bpy itself writes startup noise (e.g. a color management config line)
    # to stdout ahead of anything the script prints, so only the last line
    # is the script's own output.
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"subprocess failed (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    return result.stdout.strip().splitlines()[-1]


def test_unregister_removes_load_post_handlers_it_added():
    # register() appends its own handler function(s) to
    # bpy.app.handlers.load_post - a plain list Blender calls in full on
    # every .blend load. unregister() must remove exactly what register()
    # added, so a register()/unregister()/register() cycle (an addon
    # disable followed by a re-enable) doesn't leave a duplicate behind
    # that fires twice on every future load.
    output = _run(
        """
        import bpy
        from albam import register, unregister
        from albam.data_loading import populate_albam_data

        register()  # simulates the addon already being enabled
        before = bpy.app.handlers.load_post.count(populate_albam_data)

        unregister()  # disable
        after_unregister = bpy.app.handlers.load_post.count(populate_albam_data)

        register()  # re-enable
        after_reregister = bpy.app.handlers.load_post.count(populate_albam_data)

        print(before, after_unregister, after_reregister)
        """
    )
    before, after_unregister, after_reregister = (int(x) for x in output.split())
    assert before == 1
    assert after_unregister == 0, "unregister() left its load_post handler registered"
    assert after_reregister == 1, "re-registering after unregister() produced a duplicate handler"


def test_unregister_tolerates_an_already_removed_load_post_handler():
    # A handler register() added could already be gone from load_post by
    # the time unregister() runs (e.g. some other teardown path removed it
    # first) - unregister() must not raise ValueError out of list.remove()
    # in that case.
    output = _run(
        """
        import bpy
        from albam import register, unregister
        from albam.data_loading import populate_albam_data

        register()
        bpy.app.handlers.load_post.remove(populate_albam_data)

        unregister()  # must not raise
        print("ok")
        """
    )
    assert output == "ok"
