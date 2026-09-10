import os

import bpy
import pytest

from albam import register, unregister
from albam.blender_ui.error_handling import RERAISE_ERRORS_ENV_VAR
from albam.lib import fs_registry


# Written by pytest_sessionfinish so CI can recover the real exit status when
# the interpreter segfaults on the way out - see the comment there.
EXIT_STATUS_FILE_ENV_VAR = "ALBAM_PYTEST_EXIT_STATUS_FILE"


def pytest_sessionstart():
    # Operator error handlers turn any exception into an {'ERROR'} report,
    # which Blender re-raises as a bare RuntimeError carrying only the
    # handler's own message - no traceback, no exception type. Useless for a
    # test: a broken export reported as "RuntimeError: Export failed"
    # pointing at conftest says nothing about what actually broke. With this
    # set, the handlers re-raise instead, so failures land on the line that
    # caused them (see albam/blender_ui/error_handling.py).
    os.environ[RERAISE_ERRORS_ENV_VAR] = "1"
    register()


def pytest_sessionfinish(exitstatus):
    _record_exit_status(exitstatus)
    unregister()

    # bpy (the pip package, not the full Blender application) segfaults
    # during CPython interpreter finalization whenever any registered
    # bpy.types.PropertyGroup subclass defines a plain Python method -
    # unrelated to anything this addon's own teardown can prevent. Harmless:
    # normal interpreter shutdown already flushes all of pytest's output
    # before the crash, which is the very last thing that happens. Don't
    # add an os._exit(int(exitstatus)) shortcut here to dodge the scary
    # traceback - it skips that flush, and on at least one real run (a
    # dataset missing an optional key, aborting collection) that silently
    # discarded pytest's entire output instead of just the exit code. CI's
    # existing handling (discounting exit code 139 - see
    # .github/workflows/tests.yml) is the right place to deal with the exit
    # code, not here.


def _record_exit_status(exitstatus):
    """Write pytest's own exit status to $ALBAM_PYTEST_EXIT_STATUS_FILE, if
    set, before anything else in teardown runs.

    bpy segfaults during interpreter finalization (see pytest_sessionfinish
    above), so the shell that ran pytest sees 139 whether the run passed or
    failed, and CI cannot tell the two apart from the exit code alone.
    Discounting 139 outright - which is what the workflow used to do - turns
    every real failure on an affected bpy version into a green build; it hid
    8 errors on one half of the matrix. Recording the status here, while the
    interpreter is still alive and pytest has already decided the outcome,
    gives CI something trustworthy to fall back on.
    """
    path = os.environ.get(EXIT_STATUS_FILE_ENV_VAR)
    if not path:
        return
    try:
        with open(path, "w") as f:
            f.write(str(int(exitstatus)))
    except OSError as err:  # never let bookkeeping fail the run
        print(f"Could not write {path!r}: {err}")


def pytest_addoption(parser):
    parser.addoption(
        "--game-dir",
        action="append",
        help="Format: <app-id>::<value>[::<path-list>]: <value> is either a local game "
        "install root (recursively scanned for .arc files via MTFW_FS), or an explicit "
        "'r2://<bucket>/<prefix>' to source that app-id from R2 instead, e.g. "
        "'r2://albam/re5' (bare 'r2://' with no bucket/prefix is not allowed - always name "
        "both). Credentials always come from env vars (see .env.example), never from this "
        "flag; CI supplies the bucket the same way, by interpolating a secret directly "
        "into the --game-dir value (e.g. r2://${{ secrets.R2_BUCKET_NAME }}/re5) rather "
        "than this reading a bucket name from env itself. The optional third segment is "
        "reng-only (a .pak's file entries carry only hashes, "
        "not paths, so an external candidate-path list is required - see "
        "albam/engines/reng/pak_fs.py's module docstring): a local path, or 'r2://<key>' "
        "to fetch it from the game root's own R2 bucket/prefix instead, where <key> is "
        "the key it was uploaded under. MTFW apps ignore a third segment if given. Used "
        "by tests/mtfw/*.py and tests/reng/*.py's "
        "hash-driven, catalog-verified local round-trip tests. Can be passed multiple "
        "times.",
    )


def pytest_configure(config):
    # Validate eagerly, once, at startup - not from within a fixture, where a
    # malformed value would otherwise only surface once each parametrized
    # test actually runs it, as one raw traceback per test instead of a
    # single clear message before anything even starts.
    from tests.mtfw.r2_config import R2_PROTOCOL_PREFIX

    for app_id_and_dir in config.getoption("game_dir") or []:
        parts = app_id_and_dir.split("::")
        if len(parts) not in (2, 3) or not all(parts):
            raise pytest.UsageError(
                f"--game-dir={app_id_and_dir!r} is malformed: expected a non-empty "
                f"app-id and a non-empty value, joined by '::', with an optional third "
                f"'::'-joined non-empty segment (reng's path-list - see --help), e.g. "
                f"--game-dir=re5::/path/to/game or --game-dir=re3::/path/to/re3::"
                f"/path/to/list.txt (a single ':' is not the separator)"
            )
        # Bare "r2://" (nothing after it) is a flag-writing mistake, not an
        # environment issue (unlike e.g. an empty bucket interpolated from
        # an unconfigured CI secret, which stays a clean skip elsewhere) -
        # worth failing loudly here rather than a same-look skip.
        for part in parts[1:]:
            if part == R2_PROTOCOL_PREFIX:
                raise pytest.UsageError(
                    f"--game-dir={app_id_and_dir!r} uses bare {R2_PROTOCOL_PREFIX!r} - r2:// "
                    f"must always be explicit: 'r2://<bucket>/<prefix>' (game root, e.g. "
                    f"r2://albam/re5) or 'r2://<key>' (reng's path-list segment)"
                )


def close_new_fs_roots(before):
    """Close the FS roots registered since `before` was taken.

    Not fs_registry.clear(): that closes every filesystem in the process.
    Session-scoped parametrization interleaves every engine's tests in the
    same session - cie's with mtfw's and hexn's, whose game_fs_root is one
    session-scoped FS shared by every test in it - so clearing here closed
    it mid-run and every later test using it failed with FilesystemClosed.
    """
    for key in fs_registry.keys():
        if key not in before:
            fs_registry.unregister(key)


def vfs_root_names():
    """Names of every root vfile currently in the main VFS - a snapshot to
    diff against after a test, so only the roots it added get removed (see
    remove_new_vfs_roots)."""
    return {vf.name for vf in bpy.context.scene.albam.vfs.file_list if vf.is_root}


def remove_new_vfs_roots(before):
    """Remove only the VFS roots added since `before` was taken (see
    vfs_root_names()), each via the real "Remove imported files" operator so
    a root's whole subtree goes with it - not
    scene.albam.vfs.file_list.clear().

    vfs.file_list is one collection shared by every engine's tests in the
    same session, same reasoning as close_new_fs_roots() above: mtfw's and
    hexn's own game_fs_root fixtures mount their whole-game root once per
    session and expect it to still be there on every later test. Clearing
    the whole list here emptied it out from under them - the later test's
    own session-scoped fixture, having already run once, never re-mounts,
    so every VFS lookup after that silently found nothing.
    """
    vfs = bpy.context.scene.albam.vfs
    for name in [vf.name for vf in vfs.file_list if vf.is_root]:
        if name in before:
            continue
        index = vfs.file_list.find(name)
        if index == -1:
            continue  # already removed as part of an earlier root's own cleanup
        vfs.file_list_selected_index = index
        bpy.ops.albam.remove_imported()
