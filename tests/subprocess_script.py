"""Runs a test script in a fresh Python subprocess.

For tests that would corrupt the live pytest process: this session already
called register() once (see tests/conftest.py's pytest_sessionstart), so
cycling it again or poisoning sys.modules in-process would break every
other test.
"""
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


def run_script(script):
    """Run `script` with os and sys imported and return its last stdout line."""
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
