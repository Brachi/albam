#!/usr/bin/env python3
"""
Install a built extension zip into a throwaway Blender and enable it:

    python scripts/smoke_test_extension.py dist/albam-0.5.0.zip

What this catches that building the zip doesn't: the zip installing fine but
the add-on failing to register because something it imports isn't there. A
dependency added to pyproject.toml without regenerating pylock.toml shipped
exactly that way, and nothing failed until a user installed it.

So it has to run in an interpreter where albam's dependencies are NOT already
installed - otherwise the add-on imports them from the environment and a zip
missing every wheel still passes. A bare `bpy` install is the right
environment; a venv that has had `pip install .` run in it is not.

Blender's user resources (extensions, preferences) are redirected to a temp
directory, so this never touches a real Blender configuration.
"""
import os
import sys
import tempfile
import traceback
from pathlib import Path

PACKAGE_ID = "albam"
REPO_MODULE = "user_default"
MODULE_NAME = f"bl_ext.{REPO_MODULE}.{PACKAGE_ID}"


def smoke_test(zip_path):
    import bpy

    # Enabling the extensions add-on is what provides bpy.ops.extensions.
    bpy.ops.preferences.addon_enable(module="bl_pkg")
    bpy.ops.extensions.package_install_files(
        filepath=str(zip_path), repo=REPO_MODULE, enable_on_install=False
    )
    # Separate from the install so a failure to register is reported as
    # itself, rather than as the install operator failing.
    bpy.ops.preferences.addon_enable(module=MODULE_NAME)

    import addon_utils

    if not addon_utils.check(MODULE_NAME)[1]:
        raise SystemExit(f"{MODULE_NAME} installed but is not enabled")
    # Nothing here is reachable unless registration ran: the operators come
    # from albam's registry and the property group from its register().
    if not hasattr(bpy.ops.albam, "import_vfile"):
        raise SystemExit("albam is enabled but registered no import operator")
    if not hasattr(bpy.context.scene, "albam"):
        raise SystemExit("albam is enabled but registered no scene properties")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} <path to albam-<version>.zip>")
    zip_path = Path(sys.argv[1]).resolve()
    if not zip_path.is_file():
        raise SystemExit(f"{zip_path} not found")

    with tempfile.TemporaryDirectory(prefix="albam-smoke-test-") as tmp:
        # Read by Blender when it initializes, so it has to be set before bpy
        # is imported - hence the import inside smoke_test() below.
        os.environ["BLENDER_USER_RESOURCES"] = tmp
        print(f"Installing {zip_path.name} into a throwaway Blender at {tmp} ...")
        smoke_test(zip_path)

    print(f"OK: {zip_path.name} installs, enables and registers.")


if __name__ == "__main__":
    status = 0
    try:
        main()
    except SystemExit as ex:
        print(ex, file=sys.stderr)
        status = 1
    except BaseException:
        traceback.print_exc()
        status = 1
    # Blender 4.2 segfaults during interpreter finalization, so a run that
    # passed still exits 139. Skip finalization instead of teaching every
    # caller to second-guess the exit code.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(status)
